#!/usr/bin/env python3
"""
SexDiffKG v4 — RotatE Training FIXED (epoch counting bug)
============================================================
BUG FIX: PyKEEN's train() uses range(self._epoch, num_epochs).
Must pass CUMULATIVE epoch count, not block size.

Also trying ComplEx as alternative since RotatE may not suit this graph.

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-03
"""

import json, logging, time, gc, os
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE, ComplEx
from pykeen.training import SLCWATrainingLoop
from pykeen.losses import NSSALoss
from pykeen.sampling import BasicNegativeSampler
from pykeen.evaluation import RankBasedEvaluator

torch.set_num_threads(16)
os.environ["OMP_NUM_THREADS"] = "16"
os.environ["MKL_NUM_THREADS"] = "16"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/v4_05b_train_rotatE_fixed.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / "sexdiffkg"
KG_DIR = BASE / "data/kg_v4"
SEED = 42


def load_data():
    triples_file = KG_DIR / "triples.tsv"
    logger.info(f"Loading triples from {triples_file}")
    df = pd.read_csv(triples_file, sep="\t", header=None, names=["h", "r", "t"])
    df = df.dropna().reset_index(drop=True)
    df["h"] = df["h"].astype(str)
    df["r"] = df["r"].astype(str)
    df["t"] = df["t"].astype(str)
    df = df[(df["h"] != "nan") & (df["r"] != "nan") & (df["t"] != "nan")]
    logger.info(f"Loaded {len(df):,} triples")
    
    full_factory = TriplesFactory.from_labeled_triples(
        triples=df[["h", "r", "t"]].values, create_inverse_triples=False
    )
    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=SEED)
    logger.info(f"Entities: {full_factory.num_entities:,}, Relations: {full_factory.num_relations:,}")
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")
    return full_factory, training_factory, testing_factory


def evaluate_model(model, testing_factory, training_factory, device):
    logger.info(f"Evaluating on {device}...")
    model.eval()
    model = model.to(device)
    evaluator = RankBasedEvaluator()
    t0 = time.time()
    results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_factory.mapped_triples.to(device),
        additional_filter_triples=[training_factory.mapped_triples.to(device)],
        batch_size=128,
    )
    eval_time = time.time() - t0
    
    metrics = {}
    for key in ["inverse_harmonic_mean_rank", "hits_at_1", "hits_at_3", "hits_at_5", "hits_at_10",
                "arithmetic_mean_rank", "geometric_mean_rank"]:
        try:
            metrics[key] = float(results.get_metric(f"both.realistic.{key}"))
        except:
            metrics[key] = None
    
    if metrics.get("arithmetic_mean_rank"):
        n_ent = testing_factory.num_entities
        metrics["amri"] = round(1.0 - (2.0 * metrics["arithmetic_mean_rank"]) / (n_ent + 1), 4)
    
    logger.info(f"  MRR:      {metrics.get('inverse_harmonic_mean_rank', 0):.6f}")
    logger.info(f"  Hits@1:   {metrics.get('hits_at_1', 0):.6f}")
    logger.info(f"  Hits@10:  {metrics.get('hits_at_10', 0):.6f}")
    logger.info(f"  AMRI:     {metrics.get('amri', 'N/A')}")
    logger.info(f"  Eval time: {eval_time/60:.1f} min")
    
    return metrics, eval_time, results


def train_rotate():
    """Train RotatE with FIXED epoch counting — all 200 epochs in one call."""
    logger.info("=" * 70)
    logger.info("=== RotatE v4.1 (FIXED: single train() call for all 200 epochs) ===")
    logger.info("=" * 70)
    
    full_factory, training_factory, testing_factory = load_data()
    
    OUT_DIR = BASE / "results/kg_embeddings_v4/RotatE_v4.1"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    EMBEDDING_DIM = 200
    EPOCHS = 200
    BATCH_SIZE = 512
    LR = 0.00005
    MARGIN = 9.0
    ADV_TEMP = 1.0
    NUM_NEG = 256
    
    model = RotatE(
        triples_factory=training_factory,
        embedding_dim=EMBEDDING_DIM,
        random_seed=SEED,
    ).to("cpu")
    
    loss = NSSALoss(margin=MARGIN, adversarial_temperature=ADV_TEMP)
    model.loss = loss
    
    optimizer = torch.optim.Adam(params=model.get_grad_params(), lr=LR)
    negative_sampler = BasicNegativeSampler(
        mapped_triples=training_factory.mapped_triples,
        num_negs_per_pos=NUM_NEG,
    )
    
    training_loop = SLCWATrainingLoop(
        model=model,
        triples_factory=training_factory,
        optimizer=optimizer,
        negative_sampler=negative_sampler,
    )
    
    # FIXED: Train ALL epochs in ONE call
    logger.info(f"Training RotatE: dim={EMBEDDING_DIM}, epochs={EPOCHS}, batch={BATCH_SIZE}, lr={LR}")
    logger.info(f"Loss: NSSALoss(margin={MARGIN}, adv_temp={ADV_TEMP}), neg_samples={NUM_NEG}")
    
    t0 = time.time()
    losses = training_loop.train(
        triples_factory=training_factory,
        num_epochs=EPOCHS,
        batch_size=BATCH_SIZE,
    )
    train_time = time.time() - t0
    logger.info(f"Training done in {train_time/3600:.2f}h. Final loss: {losses[-1]:.6f}")
    logger.info(f"Loss trajectory: {losses[0]:.4f} → {losses[24]:.4f} → {losses[49]:.4f} → {losses[-1]:.4f}")
    
    # Save model
    torch.save(model.state_dict(), OUT_DIR / "model.pt")
    
    # Save embeddings
    emb_dir = OUT_DIR / "embeddings"
    emb_dir.mkdir(exist_ok=True)
    entity_emb = model.entity_representations[0](indices=None).detach().cpu().numpy()
    relation_emb = model.relation_representations[0](indices=None).detach().cpu().numpy()
    np.savez(emb_dir / "entity_embeddings.npz", embeddings=entity_emb)
    np.savez(emb_dir / "relation_embeddings.npz", embeddings=relation_emb)
    
    # Evaluate
    eval_device = "cuda" if torch.cuda.is_available() else "cpu"
    metrics, eval_time, results = evaluate_model(model, testing_factory, training_factory, eval_device)
    
    summary = {
        "model": "RotatE", "version": "v4.1_fixed",
        "bug_fix": "All 200 epochs in single train() call — v4.0 only trained 25 due to epoch counter bug",
        "hyperparameters": {
            "embedding_dim": EMBEDDING_DIM, "epochs": EPOCHS,
            "batch_size": BATCH_SIZE, "learning_rate": LR,
            "loss": "NSSALoss", "margin": MARGIN,
            "adversarial_temperature": ADV_TEMP, "num_negative_samples": NUM_NEG,
        },
        "final_loss": round(float(losses[-1]), 6),
        "loss_at_25": round(float(losses[24]), 6),
        "loss_at_50": round(float(losses[49]), 6),
        "entities": full_factory.num_entities, "relations": full_factory.num_relations,
        "train_triples": training_factory.num_triples, "test_triples": testing_factory.num_triples,
        "metrics": {k: round(v, 6) if v else None for k, v in metrics.items()},
        "training_time_hours": round(train_time / 3600, 2),
        "eval_time_minutes": round(eval_time / 60, 2),
    }
    with open(OUT_DIR / "rotatE_v4.1_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    del model, entity_emb, relation_emb; gc.collect()
    return metrics


def train_complex():
    """Train ComplEx as alternative — handles asymmetric relations via complex space."""
    logger.info("=" * 70)
    logger.info("=== ComplEx v4 (alternative to RotatE) ===")
    logger.info("=" * 70)
    
    full_factory, training_factory, testing_factory = load_data()
    
    OUT_DIR = BASE / "results/kg_embeddings_v4/ComplEx"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    EMBEDDING_DIM = 200
    EPOCHS = 100
    BATCH_SIZE = 512
    LR = 0.001
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Training ComplEx on {device}: dim={EMBEDDING_DIM}, epochs={EPOCHS}")
    
    model = ComplEx(
        triples_factory=training_factory,
        embedding_dim=EMBEDDING_DIM,
        random_seed=SEED,
    ).to(device)
    
    optimizer = torch.optim.Adam(params=model.get_grad_params(), lr=LR)
    training_loop = SLCWATrainingLoop(
        model=model, triples_factory=training_factory, optimizer=optimizer,
    )
    
    t0 = time.time()
    losses = training_loop.train(
        triples_factory=training_factory, num_epochs=EPOCHS, batch_size=BATCH_SIZE,
    )
    train_time = time.time() - t0
    logger.info(f"ComplEx training done in {train_time/3600:.2f}h. Final loss: {losses[-1]:.6f}")
    
    # Save model
    torch.save(model.state_dict(), OUT_DIR / "model.pt")
    
    # Save embeddings
    emb_dir = OUT_DIR / "embeddings"
    emb_dir.mkdir(exist_ok=True)
    entity_emb = model.entity_representations[0](indices=None).detach().cpu().numpy()
    relation_emb = model.relation_representations[0](indices=None).detach().cpu().numpy()
    np.savez(emb_dir / "entity_embeddings.npz", embeddings=entity_emb)
    np.savez(emb_dir / "relation_embeddings.npz", embeddings=relation_emb)
    
    # Evaluate
    metrics, eval_time, results = evaluate_model(model, testing_factory, training_factory, device)
    
    summary = {
        "model": "ComplEx", "version": "v4",
        "embedding_dim": EMBEDDING_DIM, "epochs": EPOCHS,
        "batch_size": BATCH_SIZE, "learning_rate": LR,
        "final_loss": round(float(losses[-1]), 6),
        "entities": full_factory.num_entities, "relations": full_factory.num_relations,
        "train_triples": training_factory.num_triples, "test_triples": testing_factory.num_triples,
        "metrics": {k: round(v, 6) if v else None for k, v in metrics.items()},
        "training_time_hours": round(train_time / 3600, 2),
        "eval_time_minutes": round(eval_time / 60, 2),
    }
    with open(OUT_DIR / "complex_v4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    return metrics


def main():
    start = time.time()
    
    # 1. Train ComplEx on GPU first (faster, good comparison point)
    complex_metrics = train_complex()
    
    # 2. Train RotatE FIXED on CPU (slower but now actually trains all 200 epochs)
    rotate_metrics = train_rotate()
    
    # 3. Compare all models
    logger.info("\n" + "=" * 70)
    logger.info("=== MODEL COMPARISON ===")
    logger.info("=" * 70)
    
    # Load DistMult v4 for comparison
    dm_path = BASE / "results/kg_embeddings_v4/DistMult/distmult_v4_summary.json"
    if dm_path.exists():
        with open(dm_path) as f:
            dm = json.load(f)
        dm_metrics = dm["metrics"]
        logger.info(f"DistMult v4:  MRR={dm_metrics.get('inverse_harmonic_mean_rank', 0):.6f}  Hits@10={dm_metrics.get('hits_at_10', 0):.6f}")
    
    logger.info(f"ComplEx v4:   MRR={complex_metrics.get('inverse_harmonic_mean_rank', 0):.6f}  Hits@10={complex_metrics.get('hits_at_10', 0):.6f}")
    logger.info(f"RotatE v4.1:  MRR={rotate_metrics.get('inverse_harmonic_mean_rank', 0):.6f}  Hits@10={rotate_metrics.get('hits_at_10', 0):.6f}")
    
    total = time.time() - start
    logger.info(f"\nTotal time: {total/3600:.2f}h")
    logger.info("ALL_MODELS_COMPLETE")


if __name__ == "__main__":
    main()
