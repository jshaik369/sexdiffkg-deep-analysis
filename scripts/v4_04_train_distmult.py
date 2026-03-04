#!/usr/bin/env python3
"""
SexDiffKG v4 — Step 4a: Train DistMult on KG v4
=================================================
200d, 100 epochs, proper evaluation on NaN-free KG v4.

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-03
"""

import json, logging, time, gc
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
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/v4_04_train_distmult.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / "sexdiffkg"
KG_DIR = BASE / "data/kg_v4"
OUT_DIR = BASE / "results/kg_embeddings_v4/DistMult"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_DIM = 200
EPOCHS = 100
BATCH_SIZE = 512
LR = 0.001
SEED = 42


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("SexDiffKG v4 — DistMult Training (200d, 100 epochs)")
    logger.info("=" * 70)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Load triples (already NaN-free from v4 build)
    triples_file = KG_DIR / "triples.tsv"
    logger.info(f"Loading triples from {triples_file}")
    df = pd.read_csv(triples_file, sep="\t", header=None, names=["h", "r", "t"])
    before = len(df)
    df = df.dropna().reset_index(drop=True)
    df["h"] = df["h"].astype(str)
    df["r"] = df["r"].astype(str)
    df["t"] = df["t"].astype(str)
    # Extra safety: remove literal "nan" strings
    df = df[(df["h"] != "nan") & (df["r"] != "nan") & (df["t"] != "nan")]
    logger.info(f"Loaded {len(df):,} triples (dropped {before - len(df):,})")
    
    full_factory = TriplesFactory.from_labeled_triples(
        triples=df[["h", "r", "t"]].values, create_inverse_triples=False
    )
    logger.info(f"Entities: {full_factory.num_entities:,}, Relations: {full_factory.num_relations:,}")
    
    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=SEED)
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")
    
    # Train
    logger.info(f"Training DistMult: dim={EMBEDDING_DIM}, epochs={EPOCHS}, batch={BATCH_SIZE}, lr={LR}")
    model = DistMult(
        triples_factory=training_factory,
        embedding_dim=EMBEDDING_DIM,
        random_seed=SEED,
    ).to(device)
    
    optimizer = torch.optim.Adam(params=model.get_grad_params(), lr=LR)
    training_loop = SLCWATrainingLoop(
        model=model, triples_factory=training_factory, optimizer=optimizer,
    )
    
    losses = training_loop.train(
        triples_factory=training_factory, num_epochs=EPOCHS, batch_size=BATCH_SIZE,
    )
    train_time = time.time() - start
    logger.info(f"Training done in {train_time/3600:.2f}h. Final loss: {losses[-1]:.6f}")
    
    # Save model BEFORE eval
    torch.save(model.state_dict(), OUT_DIR / "model.pt")
    
    # Save embeddings
    emb_dir = OUT_DIR / "embeddings"
    emb_dir.mkdir(exist_ok=True)
    entity_emb = model.entity_representations[0](indices=None).cpu().detach().numpy()
    relation_emb = model.relation_representations[0](indices=None).cpu().detach().numpy()
    id_to_entity = {v: k for k, v in full_factory.entity_to_id.items()}
    entity_ids = [id_to_entity[i] for i in range(len(id_to_entity))]
    np.savez(emb_dir / "entity_embeddings.npz", embeddings=entity_emb, ids=entity_ids)
    np.savez(emb_dir / "relation_embeddings.npz", embeddings=relation_emb)
    logger.info("Embeddings saved")
    
    # Evaluate
    logger.info("Evaluating...")
    eval_start = time.time()
    evaluator = RankBasedEvaluator()
    results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_factory.mapped_triples,
        batch_size=BATCH_SIZE,
        additional_filter_triples=[training_factory.mapped_triples],
    )
    eval_time = time.time() - eval_start
    
    metrics = {}
    for key in ["inverse_harmonic_mean_rank", "hits_at_1", "hits_at_3", "hits_at_5", "hits_at_10",
                "arithmetic_mean_rank", "geometric_mean_rank"]:
        try:
            metrics[key] = float(results.get_metric(f"both.realistic.{key}"))
        except:
            metrics[key] = None
    
    # AMRI
    if metrics.get("arithmetic_mean_rank"):
        amri = 1.0 - (2.0 * metrics["arithmetic_mean_rank"]) / (full_factory.num_entities + 1)
        metrics["amri"] = round(amri, 4)
    
    logger.info("=== DistMult v4 Results ===")
    logger.info(f"  MRR:      {metrics.get('inverse_harmonic_mean_rank', 0):.6f}")
    logger.info(f"  Hits@1:   {metrics.get('hits_at_1', 0):.6f}")
    logger.info(f"  Hits@3:   {metrics.get('hits_at_3', 0):.6f}")
    logger.info(f"  Hits@5:   {metrics.get('hits_at_5', 0):.6f}")
    logger.info(f"  Hits@10:  {metrics.get('hits_at_10', 0):.6f}")
    logger.info(f"  AMRI:     {metrics.get('amri', 'N/A')}")
    
    total_time = time.time() - start
    summary = {
        "model": "DistMult", "version": "v4", "kg_version": "v4_diana_reactome",
        "embedding_dim": EMBEDDING_DIM, "epochs": EPOCHS, "batch_size": BATCH_SIZE,
        "learning_rate": LR, "final_loss": round(float(losses[-1]), 6),
        "initial_loss": round(float(losses[0]), 6),
        "entities": full_factory.num_entities, "relations": full_factory.num_relations,
        "train_triples": training_factory.num_triples,
        "test_triples": testing_factory.num_triples,
        "metrics": {k: round(v, 6) if v else None for k, v in metrics.items()},
        "training_time_hours": round(train_time / 3600, 2),
        "eval_time_minutes": round(eval_time / 60, 2),
        "total_time_hours": round(total_time / 3600, 2),
        "device": device,
    }
    
    with open(OUT_DIR / "distmult_v4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Also save full metrics JSON
    with open(OUT_DIR / "distmult_v4_full_metrics.json", "w") as f:
        json.dump({k: str(v) for k, v in results.to_dict().items()}, f, indent=2)
    
    logger.info(f"Total time: {total_time/3600:.2f}h")
    logger.info("DISTMULT_V4_COMPLETE")


if __name__ == "__main__":
    main()
