#!/usr/bin/env python3
"""
Train DistMult graph embeddings on SexDiffKG (v3 fixed).
Fixed: RankBasedEvaluator API for PyKEEN 1.11.x (no 'ks' param).

Author: JShaik (jshaik@coevolvenetwork.com)
"""

import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.models import DistMult
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    kg_dir = Path("data/kg")
    output_dir = Path("results/kg_embeddings")
    output_dir.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # Load triples
    logger.info("Loading triples...")
    df = pd.read_csv(kg_dir / "triples.tsv", sep="\t", header=None, names=["h", "r", "t"])
    before = len(df)
    df = df.dropna(subset=["h", "r", "t"]).reset_index(drop=True)
    df["h"] = df["h"].astype(str)
    df["r"] = df["r"].astype(str)
    df["t"] = df["t"].astype(str)
    logger.info(f"Loaded {len(df):,} triples (dropped {before - len(df):,} NaN)")

    triples_array = df[["h", "r", "t"]].values
    full_factory = TriplesFactory.from_labeled_triples(
        triples=triples_array, create_inverse_triples=False
    )
    logger.info(f"Entities: {full_factory.num_entities:,}, Relations: {full_factory.num_relations:,}")

    # Split 90/10
    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=42)
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")

    # DistMult model
    embedding_dim = 200
    epochs = 100
    batch_size = 512
    lr = 0.001

    logger.info(f"Training DistMult: dim={embedding_dim}, epochs={epochs}, batch={batch_size}, lr={lr}")

    model = DistMult(
        triples_factory=training_factory,
        embedding_dim=embedding_dim,
        random_seed=42,
    ).to(device)

    optimizer = torch.optim.Adam(params=model.get_grad_params(), lr=lr)
    training_loop = SLCWATrainingLoop(
        model=model,
        triples_factory=training_factory,
        optimizer=optimizer,
    )

    losses = training_loop.train(
        triples_factory=training_factory,
        num_epochs=epochs,
        batch_size=batch_size,
    )
    logger.info(f"Training done. Final loss: {losses[-1]:.6f}")

    # Save model IMMEDIATELY after training (before eval, to avoid losing weights)
    model_dir = output_dir / "DistMult"
    model_dir.mkdir(exist_ok=True)
    torch.save(model.state_dict(), model_dir / "model.pt")
    logger.info("Model checkpoint saved (pre-evaluation safety save)")

    # Save entity/relation embeddings
    emb_dir = model_dir / "embeddings"
    emb_dir.mkdir(exist_ok=True)

    entity_emb = model.entity_representations[0](indices=None).cpu().detach().numpy()
    id_to_entity = {v: k for k, v in full_factory.entity_to_id.items()}
    entity_ids = [id_to_entity[i] for i in range(len(id_to_entity))]
    np.savez(emb_dir / "entity_embeddings.npz", embeddings=entity_emb, ids=entity_ids)

    relation_emb = model.relation_representations[0](indices=None).cpu().detach().numpy()
    id_to_relation = {v: k for k, v in full_factory.relation_to_id.items()}
    relation_ids = [id_to_relation[i] for i in range(len(id_to_relation))]
    np.savez(emb_dir / "relation_embeddings.npz", embeddings=relation_emb, ids=relation_ids)
    logger.info("Embeddings saved")

    # Evaluate — PyKEEN 1.11.x: no 'ks' param, defaults include HitsAtK(1,3,5,10)
    logger.info("Evaluating with rank-based metrics...")
    evaluator = RankBasedEvaluator()
    metric_results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_factory.mapped_triples,
        batch_size=batch_size,
        additional_filter_triples=[training_factory.mapped_triples],
    )

    metrics = {}
    try:
        metrics["mrr"] = float(metric_results.get_metric("both.realistic.inverse_harmonic_mean_rank"))
    except Exception:
        metrics["mrr"] = 0.0

    for k in [1, 3, 5, 10]:
        try:
            metrics[f"hits_at_{k}"] = float(metric_results.get_metric(f"both.realistic.hits_at_{k}"))
        except Exception:
            metrics[f"hits_at_{k}"] = 0.0

    logger.info("=== DistMult v3 Evaluation Results ===")
    logger.info(f"  MRR:      {metrics.get('mrr', 0):.6f}")
    logger.info(f"  Hits@1:   {metrics.get('hits_at_1', 0):.6f}")
    logger.info(f"  Hits@3:   {metrics.get('hits_at_3', 0):.6f}")
    logger.info(f"  Hits@5:   {metrics.get('hits_at_5', 0):.6f}")
    logger.info(f"  Hits@10:  {metrics.get('hits_at_10', 0):.6f}")

    # Save summary
    summary = {
        "model": "DistMult",
        "version": "v3",
        "embedding_dim": embedding_dim,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "final_loss": float(losses[-1]),
        "initial_loss": float(losses[0]),
        "num_entities": full_factory.num_entities,
        "num_relations": full_factory.num_relations,
        "training_triples": training_factory.num_triples,
        "testing_triples": testing_factory.num_triples,
        "evaluation": metrics,
        "device": device,
    }

    with open(output_dir / "distmult_training_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"All outputs saved to {output_dir}")
    logger.info("DISTMULT_COMPLETE")


if __name__ == "__main__":
    main()
