#!/usr/bin/env python3
"""
Train graph embeddings using PyKEEN on the SexDiffKG knowledge graph.

Uses TriplesFactory.from_labeled_triples() for efficient loading
and PyKEEN pipeline for training RotatE and TransE models.

Usage:
    python 07_train_embeddings.py --kg-dir data/kg/ --output-dir results/kg_embeddings/
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE, TransE
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator
from pykeen.losses import MarginRankingLoss

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class KGEmbeddingTrainer:
    """Train and evaluate KG embedding models."""

    def __init__(
        self,
        kg_dir: Path,
        output_dir: Path,
        embedding_dim: int = 200,
        batch_size: int = 512,
        learning_rate: float = 0.001,
        epochs: int = 100,
        device: str = "cuda",
    ):
        self.kg_dir = Path(kg_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_dim = embedding_dim
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.device = device if torch.cuda.is_available() else "cpu"
        self.results = {}

        # Will be set by load_dataset
        self.training_factory = None
        self.testing_factory = None
        self.entity_to_id = None
        self.relation_to_id = None

        logger.info(f"CUDA available: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No'}")

    def load_dataset(self) -> None:
        """Load triples from TSV file into PyKEEN TriplesFactory."""
        logger.info("Loading KG triples dataset")
        triples_file = self.kg_dir / "triples.tsv"

        if not triples_file.exists():
            raise FileNotFoundError(f"Triples file not found: {triples_file}")

        # Read triples
        df = pd.read_csv(triples_file, sep="\t", header=None, names=["h", "r", "t"])
        logger.info(f"Loaded {len(df):,} triples")

        # Drop rows with NaN entity IDs
        before = len(df)
        df = df.dropna(subset=["h", "r", "t"]).reset_index(drop=True)
        df["h"] = df["h"].astype(str)
        df["r"] = df["r"].astype(str)
        df["t"] = df["t"].astype(str)
        dropped = before - len(df)
        if dropped > 0:
            logger.info(f"Dropped {dropped:,} triples with NaN values ({len(df):,} remaining)")

        # Convert to numpy array for PyKEEN
        triples_array = df[["h", "r", "t"]].values
        logger.info(f"Creating TriplesFactory from {len(triples_array):,} triples...")

        # Create TriplesFactory — PyKEEN handles all the ID mapping internally
        full_factory = TriplesFactory.from_labeled_triples(
            triples=triples_array,
            create_inverse_triples=False,
        )

        logger.info(f"Entities: {full_factory.num_entities:,}")
        logger.info(f"Relations: {full_factory.num_relations:,}")

        # Split: 90% training, 10% testing
        self.training_factory, self.testing_factory = full_factory.split(
            ratios=[0.9, 0.1],
            random_state=42,
        )

        self.entity_to_id = full_factory.entity_to_id
        self.relation_to_id = full_factory.relation_to_id

        logger.info(f"Training triples: {self.training_factory.num_triples:,}")
        logger.info(f"Testing triples: {self.testing_factory.num_triples:,}")
        logger.info("Dataset loaded successfully")

    def train_model(self, model_class, model_name: str) -> Dict:
        """
        Train an embedding model.

        Args:
            model_class: PyKEEN model class (RotatE, TransE, etc.)
            model_name: Name of model for logging/saving

        Returns:
            Dictionary with training results and metrics
        """
        logger.info(f"Training {model_name} model")
        logger.info(f"Config: embedding_dim={self.embedding_dim}, "
                    f"batch_size={self.batch_size}, epochs={self.epochs}, "
                    f"lr={self.learning_rate}")

        # Initialize model
        model = model_class(
            triples_factory=self.training_factory,
            embedding_dim=self.embedding_dim,
            random_seed=42,
        ).to(self.device)

        # Setup training
        optimizer = torch.optim.Adam(
            params=model.get_grad_params(),
            lr=self.learning_rate,
        )

        training_loop = SLCWATrainingLoop(
            model=model,
            triples_factory=self.training_factory,
            optimizer=optimizer,
        )

        # Train model
        logger.info("Starting training loop")
        losses = training_loop.train(
            triples_factory=self.training_factory,
            num_epochs=self.epochs,
            batch_size=self.batch_size,
        )

        logger.info(f"Training completed. Final loss: {losses[-1]:.6f}")

        # Evaluate model
        logger.info("Evaluating model with rank-based metrics")
        evaluator = RankBasedEvaluator(ks=[1, 3, 5, 10, 100])
        metric_results = evaluator.evaluate(
            model=model,
            mapped_triples=self.testing_factory.mapped_triples,
            batch_size=self.batch_size,
            additional_filter_triples=[self.training_factory.mapped_triples],
        )

        # Extract metrics
        metrics = {}
        try:
            metrics["mrr"] = float(metric_results.get_metric("both.realistic.inverse_harmonic_mean_rank"))
        except Exception:
            try:
                metrics["mrr"] = float(metric_results.get_metric("mean_reciprocal_rank"))
            except Exception:
                metrics["mrr"] = 0.0

        for k in [1, 10, 100]:
            try:
                metrics[f"hits_at_{k}"] = float(metric_results.get_metric(f"both.realistic.hits_at_{k}"))
            except Exception:
                try:
                    metrics[f"hits_at_{k}"] = float(metric_results.get_metric(f"hits_at_{k}"))
                except Exception:
                    metrics[f"hits_at_{k}"] = 0.0

        logger.info(f"Evaluation metrics:")
        logger.info(f"  MRR: {metrics.get('mrr', 0):.4f}")
        logger.info(f"  Hits@1: {metrics.get('hits_at_1', 0):.4f}")
        logger.info(f"  Hits@10: {metrics.get('hits_at_10', 0):.4f}")
        logger.info(f"  Hits@100: {metrics.get('hits_at_100', 0):.4f}")

        # Save model
        model_dir = self.output_dir / model_name
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / "model.pt"
        torch.save(model.state_dict(), model_path)
        logger.info(f"Saved model to {model_path}")

        # Save embeddings
        embeddings_dir = model_dir / "embeddings"
        embeddings_dir.mkdir(exist_ok=True)

        # Entity embeddings
        entity_rep = model.entity_representations[0]
        entity_embeddings = entity_rep(indices=None).cpu().detach().numpy()
        id_to_entity = {v: k for k, v in self.entity_to_id.items()}
        entity_ids = [id_to_entity[i] for i in range(len(id_to_entity))]
        df_entity_emb = pd.DataFrame(
            entity_embeddings,
            index=entity_ids,
        )
        entity_emb_path = embeddings_dir / "entity_embeddings.parquet"
        df_entity_emb.to_parquet(entity_emb_path)
        logger.info(f"Saved entity embeddings to {entity_emb_path}")

        # Relation embeddings
        relation_rep = model.relation_representations[0]
        relation_embeddings = relation_rep(indices=None).cpu().detach().numpy()
        id_to_relation = {v: k for k, v in self.relation_to_id.items()}
        relation_ids = [id_to_relation[i] for i in range(len(id_to_relation))]
        df_relation_emb = pd.DataFrame(
            relation_embeddings,
            index=relation_ids,
        )
        relation_emb_path = embeddings_dir / "relation_embeddings.parquet"
        df_relation_emb.to_parquet(relation_emb_path)
        logger.info(f"Saved relation embeddings to {relation_emb_path}")

        # Save results
        results = {
            "model": model_name,
            "config": {
                "embedding_dim": self.embedding_dim,
                "batch_size": self.batch_size,
                "learning_rate": self.learning_rate,
                "epochs": self.epochs,
            },
            "training": {
                "final_loss": float(losses[-1]),
                "loss_history": [float(l) for l in losses],
            },
            "evaluation": metrics,
        }

        results_path = model_dir / "results.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved results to {results_path}")

        return results

    def train_all_models(self) -> None:
        """Train all embedding models."""
        logger.info("=" * 80)
        logger.info("SexDiffKG Embedding Training Pipeline")
        logger.info("=" * 80)

        # Load dataset once
        self.load_dataset()

        # Train models
        models_to_train = [
            (RotatE, "RotatE"),
            (TransE, "TransE"),
        ]

        for model_class, model_name in models_to_train:
            logger.info("")
            logger.info(f"{'=' * 80}")
            logger.info(f"Training {model_name}")
            logger.info(f"{'=' * 80}")

            try:
                result = self.train_model(model_class, model_name)
                self.results[model_name] = result
            except Exception as e:
                logger.error(f"Failed to train {model_name}: {e}", exc_info=True)

        # Save summary
        self.save_summary()

    def save_summary(self) -> None:
        """Save training summary."""
        summary_path = self.output_dir / "training_summary.json"
        with open(summary_path, "w") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Saved training summary to {summary_path}")

        # Print comparison
        if self.results:
            logger.info("")
            logger.info("=" * 80)
            logger.info("Model Comparison")
            logger.info("=" * 80)
            comparison_df = pd.DataFrame([
                {
                    "Model": name,
                    "MRR": result["evaluation"].get("mrr", 0),
                    "Hits@1": result["evaluation"].get("hits_at_1", 0),
                    "Hits@10": result["evaluation"].get("hits_at_10", 0),
                    "Hits@100": result["evaluation"].get("hits_at_100", 0),
                }
                for name, result in self.results.items()
            ])
            logger.info("\n" + comparison_df.to_string(index=False))

            comparison_path = self.output_dir / "model_comparison.csv"
            comparison_df.to_csv(comparison_path, index=False)
            logger.info(f"Saved comparison to {comparison_path}")


def main(args: argparse.Namespace) -> None:
    kg_dir = Path(args.kg_dir)
    output_dir = Path(args.output_dir)

    if not kg_dir.exists():
        raise FileNotFoundError(f"KG directory not found: {kg_dir}")

    logger.info(f"KG directory: {kg_dir}")
    logger.info(f"Output directory: {output_dir}")

    trainer = KGEmbeddingTrainer(
        kg_dir=kg_dir,
        output_dir=output_dir,
        embedding_dim=args.embedding_dim,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        epochs=args.epochs,
        device=args.device,
    )

    trainer.train_all_models()

    logger.info("")
    logger.info("=" * 80)
    logger.info("Embedding training pipeline completed successfully")
    logger.info("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train KG embeddings using PyKEEN"
    )
    parser.add_argument("--kg-dir", type=str, default="data/kg/")
    parser.add_argument("--output-dir", type=str, default="results/kg_embeddings/")
    parser.add_argument("--embedding-dim", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"])
    parser.add_argument("--log-level", type=str, default="INFO")

    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)

    try:
        main(args)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise SystemExit(1)
