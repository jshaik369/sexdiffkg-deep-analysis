#!/usr/bin/env python3
"""
SexDiffKG v4 — Step 4b: Train RotatE with FIXED Hyperparameters
=================================================================
FIXES from v3 (which had MRR 0.0001 = completely broken):
1. NSSALoss (self-adversarial negative sampling) — the correct loss for RotatE
2. Learning rate 0.00005 (v3 used 0.001 — way too high for RotatE)
3. Margin 9.0 (RotatE paper default)
4. Adversarial temperature 1.0
5. Negative samples 256 per positive
6. Checkpoints every 25 epochs
7. Training on CPU (GB10 NVRTC doesn't support RotatE complex ops on GPU)
8. Evaluation on GPU (DistMult-compatible operations)

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-03
Reference: Sun et al., "RotatE: Knowledge Graph Embedding by Relational Rotation" (ICLR 2019)
"""

import json, logging, time, gc, os
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE
from pykeen.training import SLCWATrainingLoop
from pykeen.losses import NSSALoss
from pykeen.sampling import BasicNegativeSampler
from pykeen.evaluation import RankBasedEvaluator

# CPU threading for training
torch.set_num_threads(16)
os.environ["OMP_NUM_THREADS"] = "16"
os.environ["MKL_NUM_THREADS"] = "16"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/v4_05_train_rotatE.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / "sexdiffkg"
KG_DIR = BASE / "data/kg_v4"
OUT_DIR = BASE / "results/kg_embeddings_v4/RotatE"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CKPT_DIR = OUT_DIR / "checkpoints"
CKPT_DIR.mkdir(exist_ok=True)

# RotatE paper hyperparameters (adapted for our graph size)
EMBEDDING_DIM = 200
EPOCHS = 200
BATCH_SIZE = 512
LR = 0.00005          # CRITICAL FIX: v3 used 0.001 (20x too high)
MARGIN = 9.0          # RotatE paper default
ADV_TEMP = 1.0        # Self-adversarial temperature
NUM_NEG = 256         # Negative samples per positive
CKPT_EVERY = 25
SEED = 42


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("SexDiffKG v4 — RotatE Training (FIXED hyperparameters)")
    logger.info("=" * 70)
    logger.info(f"Key fixes from v3:")
    logger.info(f"  Loss: NSSALoss (was default MarginRankingLoss)")
    logger.info(f"  LR: {LR} (was 0.001)")
    logger.info(f"  Margin: {MARGIN}")
    logger.info(f"  Adversarial temp: {ADV_TEMP}")
    logger.info(f"  Negative samples: {NUM_NEG}")
    logger.info(f"  Epochs: {EPOCHS}")
    
    train_device = "cpu"  # GB10 NVRTC can't compile RotatE complex ops
    logger.info(f"Training device: {train_device} (16 threads)")
    logger.info(f"GPU available for eval: {torch.cuda.is_available()}")
    
    # Load triples
    triples_file = KG_DIR / "triples.tsv"
    logger.info(f"Loading triples from {triples_file}")
    df = pd.read_csv(triples_file, sep="\t", header=None, names=["h", "r", "t"])
    before = len(df)
    df = df.dropna().reset_index(drop=True)
    df["h"] = df["h"].astype(str)
    df["r"] = df["r"].astype(str)
    df["t"] = df["t"].astype(str)
    df = df[(df["h"] != "nan") & (df["r"] != "nan") & (df["t"] != "nan")]
    logger.info(f"Loaded {len(df):,} triples (dropped {before - len(df):,})")
    
    full_factory = TriplesFactory.from_labeled_triples(
        triples=df[["h", "r", "t"]].values, create_inverse_triples=False
    )
    logger.info(f"Entities: {full_factory.num_entities:,}, Relations: {full_factory.num_relations:,}")
    del df; gc.collect()
    
    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=SEED)
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")
    
    # RotatE model with NSSALoss
    logger.info("Initializing RotatE with NSSALoss...")
    model = RotatE(
        triples_factory=training_factory,
        embedding_dim=EMBEDDING_DIM,
        random_seed=SEED,
    ).to(train_device)
    
    loss = NSSALoss(margin=MARGIN, adversarial_temperature=ADV_TEMP)
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
    # Override the loss
    model.loss = loss
    
    # Train in blocks with checkpoints
    all_losses = []
    for block_start in range(0, EPOCHS, CKPT_EVERY):
        block_end = min(block_start + CKPT_EVERY, EPOCHS)
        n_ep = block_end - block_start
        logger.info(f"Training epochs {block_start+1}-{block_end}...")
        t_block = time.time()
        
        losses = training_loop.train(
            triples_factory=training_factory,
            num_epochs=n_ep,
            batch_size=BATCH_SIZE,
        )
        
        block_time = time.time() - t_block
        all_losses.extend(losses)
        logger.info(f"  Epoch {block_end}/{EPOCHS}: loss={losses[-1]:.6f} ({block_time/60:.1f} min)")
        
        # Checkpoint
        ckpt_path = CKPT_DIR / f"checkpoint_epoch{block_end}.pt"
        torch.save(model.state_dict(), ckpt_path)
        logger.info(f"  Checkpoint saved: {ckpt_path}")
    
    train_time = time.time() - start
    logger.info(f"Training done in {train_time/3600:.2f}h. Final loss: {all_losses[-1]:.6f}")
    
    # Save model BEFORE evaluation
    model_path = OUT_DIR / "model.pt"
    torch.save(model.state_dict(), model_path)
    logger.info(f"Model saved: {model_path} ({model_path.stat().st_size/1e6:.1f} MB)")
    
    # Save embeddings
    emb_dir = OUT_DIR / "embeddings"
    emb_dir.mkdir(exist_ok=True)
    entity_emb = model.entity_representations[0](indices=None).detach().cpu().numpy()
    relation_emb = model.relation_representations[0](indices=None).detach().cpu().numpy()
    np.savez(emb_dir / "entity_embeddings.npz", embeddings=entity_emb)
    np.savez(emb_dir / "relation_embeddings.npz", embeddings=relation_emb)
    logger.info(f"Embeddings saved: entities {entity_emb.shape}, relations {relation_emb.shape}")
    del entity_emb, relation_emb; gc.collect()
    
    # Evaluate — try GPU
    logger.info("Running evaluation...")
    model.eval()
    eval_start = time.time()
    
    eval_device = train_device
    if torch.cuda.is_available():
        try:
            logger.info("Attempting GPU evaluation...")
            model = model.to("cuda")
            eval_device = "cuda"
            logger.info("GPU eval setup OK")
        except Exception as e:
            logger.warning(f"GPU eval failed ({e}), staying on CPU")
            model = model.to("cpu")
    
    evaluator = RankBasedEvaluator()
    results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_factory.mapped_triples.to(eval_device),
        additional_filter_triples=[training_factory.mapped_triples.to(eval_device)],
        batch_size=128,
    )
    eval_time = time.time() - eval_start
    logger.info(f"Evaluation done in {eval_time/60:.1f} min on {eval_device}")
    
    metrics = {}
    for key in ["inverse_harmonic_mean_rank", "hits_at_1", "hits_at_3", "hits_at_5", "hits_at_10",
                "arithmetic_mean_rank", "geometric_mean_rank"]:
        try:
            metrics[key] = float(results.get_metric(f"both.realistic.{key}"))
        except:
            metrics[key] = None
    
    if metrics.get("arithmetic_mean_rank"):
        metrics["amri"] = round(1.0 - (2.0 * metrics["arithmetic_mean_rank"]) / (full_factory.num_entities + 1), 4)
    
    logger.info("=== RotatE v4 Results ===")
    logger.info(f"  MRR:      {metrics.get('inverse_harmonic_mean_rank', 0):.6f}")
    logger.info(f"  Hits@1:   {metrics.get('hits_at_1', 0):.6f}")
    logger.info(f"  Hits@3:   {metrics.get('hits_at_3', 0):.6f}")
    logger.info(f"  Hits@5:   {metrics.get('hits_at_5', 0):.6f}")
    logger.info(f"  Hits@10:  {metrics.get('hits_at_10', 0):.6f}")
    logger.info(f"  AMRI:     {metrics.get('amri', 'N/A')}")
    
    # Compare with v3
    v3_mrr = 0.0001
    v4_mrr = metrics.get("inverse_harmonic_mean_rank", 0) or 0
    if v4_mrr > 0 and v3_mrr > 0:
        improvement = ((v4_mrr - v3_mrr) / v3_mrr) * 100
        logger.info(f"  v3→v4 MRR improvement: {improvement:+.1f}%")
    
    total_time = time.time() - start
    summary = {
        "model": "RotatE", "version": "v4", "kg_version": "v4_diana_reactome",
        "hyperparameters": {
            "embedding_dim": EMBEDDING_DIM, "epochs": EPOCHS,
            "batch_size": BATCH_SIZE, "learning_rate": LR,
            "loss": "NSSALoss", "margin": MARGIN,
            "adversarial_temperature": ADV_TEMP,
            "num_negative_samples": NUM_NEG,
        },
        "final_loss": round(float(all_losses[-1]), 6),
        "initial_loss": round(float(all_losses[0]), 6),
        "entities": full_factory.num_entities, "relations": full_factory.num_relations,
        "train_triples": training_factory.num_triples,
        "test_triples": testing_factory.num_triples,
        "metrics": {k: round(v, 6) if v else None for k, v in metrics.items()},
        "v3_comparison": {"v3_mrr": v3_mrr, "v4_mrr": round(v4_mrr, 6)},
        "training_time_hours": round(train_time / 3600, 2),
        "eval_time_minutes": round(eval_time / 60, 2),
        "total_time_hours": round(total_time / 3600, 2),
        "train_device": train_device, "eval_device": eval_device,
    }
    
    with open(OUT_DIR / "rotatE_v4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    with open(OUT_DIR / "rotatE_v4_full_metrics.json", "w") as f:
        json.dump({k: str(v) for k, v in results.to_dict().items()}, f, indent=2)
    
    logger.info(f"Total time: {total_time/3600:.2f}h")
    logger.info("ROTATE_V4_COMPLETE")


if __name__ == "__main__":
    main()
