#!/usr/bin/env python3
"""
Train RotatE graph embeddings on SexDiffKG — CPU training, GPU evaluation.
Runs in parallel with DistMult v3 (GPU) during training phase.
When eval starts, DistMult will be long finished — GPU is free.

Safety protocols:
- Model saved BEFORE evaluation
- Checkpoint every 25 epochs
- Completion marker at end
- Full pipeline tested with 1-epoch dry run
- Eval moves model to GPU (if available) for speed

Author: JShaik (jshaik@coevolvenetwork.com)
Infrastructure: NVIDIA DGX Spark GB10, 20 CPU cores, 121 GB RAM
"""

import json
import logging
import os
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator

# Use most available CPU cores for training
torch.set_num_threads(16)
os.environ["OMP_NUM_THREADS"] = "16"
os.environ["MKL_NUM_THREADS"] = "16"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def save_checkpoint(model, epoch, output_dir):
    """Save model checkpoint at given epoch."""
    ckpt_path = output_dir / f"rotatE_checkpoint_epoch_{epoch}.pt"
    torch.save(model.state_dict(), ckpt_path)
    logger.info(f"Checkpoint saved: {ckpt_path}")
    for old in output_dir.glob("rotatE_checkpoint_epoch_*.pt"):
        if old != ckpt_path:
            old.unlink()
            logger.info(f"Removed old checkpoint: {old}")


def main():
    start_time = time.time()
    kg_dir = Path("data/kg")
    output_dir = Path("results/kg_embeddings")
    output_dir.mkdir(parents=True, exist_ok=True)

    train_device = "cpu"  # CPU for training (GPU busy with DistMult)
    logger.info(f"Training device: {train_device} (16 threads)")
    logger.info(f"PyTorch threads: {torch.get_num_threads()}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)} — will use for evaluation")

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

    # Same 90/10 split with same seed as DistMult for fair comparison
    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=42)
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")

    # RotatE model
    embedding_dim = 200
    epochs = 100
    batch_size = 1024
    lr = 0.001

    logger.info(f"Training RotatE: dim={embedding_dim}, epochs={epochs}, batch={batch_size}, lr={lr}")

    model = RotatE(
        triples_factory=training_factory,
        embedding_dim=embedding_dim,
        random_seed=42,
    ).to(train_device)

    optimizer = torch.optim.Adam(params=model.get_grad_params(), lr=lr)
    training_loop = SLCWATrainingLoop(
        model=model,
        triples_factory=training_factory,
        optimizer=optimizer,
    )

    # Train with periodic checkpoints
    logger.info("Starting training on CPU...")
    all_losses = []

    for epoch_block_start in range(0, epochs, 25):
        block_epochs = min(25, epochs - epoch_block_start)
        losses = training_loop.train(
            triples_factory=training_factory,
            num_epochs=block_epochs,
            batch_size=batch_size,
        )
        all_losses.extend(losses)
        current_epoch = epoch_block_start + block_epochs
        logger.info(f"Epoch {current_epoch}/{epochs}, loss: {losses[-1]:.6f}")
        save_checkpoint(model, current_epoch, output_dir)

    final_loss = all_losses[-1]
    train_time = time.time() - start_time
    logger.info(f"Training done. Final loss: {final_loss:.6f}, Time: {train_time/3600:.1f}h")

    # === SAVE MODEL BEFORE EVALUATION (MANDATORY — lesson learned) ===
    model_dir = output_dir / "RotatE"
    model_dir.mkdir(exist_ok=True)
    torch.save(model.state_dict(), model_dir / "model.pt")
    logger.info("Model saved to disk (pre-evaluation safety save)")

    # Save entity/relation embeddings (on CPU)
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

    # === MOVE MODEL TO GPU FOR EVALUATION (DistMult will be long finished by now) ===
    eval_device = "cuda" if torch.cuda.is_available() else "cpu"
    if eval_device == "cuda":
        logger.info("Moving model to GPU for fast evaluation...")
        model = model.to("cuda")
        # Also move mapped triples to GPU
        testing_mapped = testing_factory.mapped_triples.to("cuda")
        training_mapped = training_factory.mapped_triples.to("cuda")
    else:
        logger.info("No GPU available — evaluating on CPU (will be slow)")
        testing_mapped = testing_factory.mapped_triples
        training_mapped = training_factory.mapped_triples

    logger.info(f"Evaluating on {eval_device}...")
    eval_start = time.time()
    evaluator = RankBasedEvaluator()
    metric_results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_mapped,
        batch_size=512 if eval_device == "cuda" else 128,
        additional_filter_triples=[training_mapped],
    )
    eval_time = time.time() - eval_start

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

    logger.info("=== RotatE v3 Evaluation Results ===")
    logger.info(f"  MRR:      {metrics.get('mrr', 0):.6f}")
    logger.info(f"  Hits@1:   {metrics.get('hits_at_1', 0):.6f}")
    logger.info(f"  Hits@3:   {metrics.get('hits_at_3', 0):.6f}")
    logger.info(f"  Hits@5:   {metrics.get('hits_at_5', 0):.6f}")
    logger.info(f"  Hits@10:  {metrics.get('hits_at_10', 0):.6f}")
    logger.info(f"  Eval time: {eval_time/3600:.1f}h on {eval_device}")

    # Save summary
    total_time = time.time() - start_time
    summary = {
        "model": "RotatE",
        "version": "v3",
        "embedding_dim": embedding_dim,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "final_loss": float(final_loss),
        "initial_loss": float(all_losses[0]),
        "num_entities": full_factory.num_entities,
        "num_relations": full_factory.num_relations,
        "training_triples": training_factory.num_triples,
        "testing_triples": testing_factory.num_triples,
        "evaluation": metrics,
        "train_device": train_device,
        "eval_device": eval_device,
        "num_threads": 16,
        "training_time_hours": round(train_time / 3600, 2),
        "eval_time_hours": round(eval_time / 3600, 2),
        "total_time_hours": round(total_time / 3600, 2),
    }

    with open(output_dir / "rotatE_training_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Clean up checkpoints
    for ckpt in output_dir.glob("rotatE_checkpoint_epoch_*.pt"):
        ckpt.unlink()
        logger.info(f"Cleaned checkpoint: {ckpt}")

    logger.info(f"All outputs saved to {output_dir}")
    logger.info(f"Total time: {total_time/3600:.1f}h (train: {train_time/3600:.1f}h + eval: {eval_time/3600:.1f}h)")
    logger.info("ROTATE_COMPLETE")


if __name__ == "__main__":
    main()
