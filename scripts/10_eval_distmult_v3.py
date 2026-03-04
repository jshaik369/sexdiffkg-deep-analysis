#!/usr/bin/env python3
"""
Evaluate saved DistMult v3 model — load checkpoint, run RankBasedEvaluator.
No retraining. Produces distmult_training_summary.json with MRR/Hits@K.

Author: JShaik (jshaik@coevolvenetwork.com)
"""
import json, logging, time
from pathlib import Path
import numpy as np, pandas as pd, torch
from pykeen.triples import TriplesFactory
from pykeen.models import DistMult
from pykeen.evaluation import RankBasedEvaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    kg_dir   = Path("data/kg")
    out_dir  = Path("results/kg_embeddings")
    model_path = out_dir / "DistMult" / "model.pt"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")

    # ── Load triples (same pipeline as training) ──
    logger.info("Loading triples...")
    df = pd.read_csv(kg_dir / "triples.tsv", sep="\t", header=None, names=["h","r","t"])
    before = len(df)
    df = df.dropna(subset=["h","r","t"]).reset_index(drop=True)
    df["h"] = df["h"].astype(str); df["r"] = df["r"].astype(str); df["t"] = df["t"].astype(str)
    logger.info(f"Loaded {len(df):,} triples (dropped {before - len(df):,} NaN)")

    full_factory = TriplesFactory.from_labeled_triples(
        triples=df[["h","r","t"]].values, create_inverse_triples=False
    )
    logger.info(f"Entities: {full_factory.num_entities:,}, Relations: {full_factory.num_relations:,}")

    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=42)
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")

    # ── Rebuild model architecture & load weights ──
    logger.info(f"Loading saved model from {model_path} ...")
    model = DistMult(
        triples_factory=training_factory,
        embedding_dim=200,
        random_seed=42,
    ).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    logger.info("Model loaded successfully.")

    # ── Evaluate ──
    logger.info("Running rank-based evaluation on test set...")
    t0 = time.time()
    evaluator = RankBasedEvaluator()   # No 'ks' param — PyKEEN 1.11.x
    results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_factory.mapped_triples.to(device),
        additional_filter_triples=[training_factory.mapped_triples.to(device)],
        batch_size=256,
    )
    eval_time = time.time() - t0
    logger.info(f"Evaluation completed in {eval_time/60:.1f} minutes")

    # ── Extract metrics ──
    rm = results.to_dict()
    # PyKEEN stores metrics under different key structures; handle gracefully
    def get_metric(name):
        """Try multiple key paths for a metric."""
        for side in ["both", "head", "tail"]:
            for typ in ["realistic", "optimistic", "pessimistic"]:
                key = f"{side}.{typ}.{name}"
                if key in rm:
                    return float(rm[key])
        # fallback: search flat
        for k, v in rm.items():
            if name in k and "both" in k and "realistic" in k:
                return float(v)
        return None

    mrr       = get_metric("inverse_harmonic_mean_rank")
    hits_at_1 = get_metric("hits_at_1")
    hits_at_3 = get_metric("hits_at_3")
    hits_at_5 = get_metric("hits_at_5")
    hits_at_10= get_metric("hits_at_10")

    logger.info(f"MRR: {mrr}")
    logger.info(f"Hits@1: {hits_at_1}  Hits@3: {hits_at_3}  Hits@5: {hits_at_5}  Hits@10: {hits_at_10}")

    # ── Save summary ──
    summary = {
        "model": "DistMult",
        "version": "v3",
        "kg": "v3_nan_filtered",
        "embedding_dim": 200,
        "epochs": 100,
        "batch_size": 512,
        "learning_rate": 0.001,
        "loss_function": "SLCWA",
        "final_loss": 0.236710,
        "seed": 42,
        "entities": int(full_factory.num_entities),
        "relations": int(full_factory.num_relations),
        "train_triples": int(training_factory.num_triples),
        "test_triples": int(testing_factory.num_triples),
        "metrics": {
            "mrr": mrr,
            "hits_at_1": hits_at_1,
            "hits_at_3": hits_at_3,
            "hits_at_5": hits_at_5,
            "hits_at_10": hits_at_10,
        },
        "eval_time_minutes": round(eval_time / 60, 2),
        "eval_device": device,
        "all_metrics": {k: float(v) if isinstance(v, (int, float)) else str(v) for k, v in rm.items()},
    }

    summary_path = out_dir / "distmult_v3_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {summary_path}")

    # Also dump full metric dict for audit
    full_path = out_dir / "distmult_v3_full_metrics.json"
    with open(full_path, "w") as f:
        json.dump({k: float(v) if isinstance(v, (int, float)) else str(v) for k, v in rm.items()}, f, indent=2)
    logger.info(f"Full metrics saved to {full_path}")

    logger.info("=== DistMult v3 EVALUATION COMPLETE ===")

if __name__ == "__main__":
    main()
