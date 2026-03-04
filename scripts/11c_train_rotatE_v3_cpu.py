#!/usr/bin/env python3
"""
Train RotatE v3 on CPU — 100 epochs, GPU eval.
GB10 NVRTC doesn't support RotatE's complex ops on GPU for training.
CPU training with 16 threads + GPU evaluation (DistMult-style ops work on GPU).

Checkpoints every 25 epochs. Saves model BEFORE eval.
Author: JShaik (jshaik@coevolvenetwork.com)
"""
import json, logging, time, gc, os
from pathlib import Path
import numpy as np, pandas as pd, torch
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator

# CPU threading
torch.set_num_threads(16)
os.environ["OMP_NUM_THREADS"] = "16"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    kg_dir   = Path("data/kg")
    out_dir  = Path("results/kg_embeddings/RotatE")
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = out_dir / "checkpoints"
    ckpt_dir.mkdir(exist_ok=True)

    device = "cpu"  # Force CPU for training (GB10 NVRTC incompatible with RotatE complex ops)
    logger.info(f"Training device: {device} (16 threads)")
    logger.info(f"GPU available for eval: {torch.cuda.is_available()}")

    # ── Load triples ──
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
    del df; gc.collect()

    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=42)
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")

    # ── RotatE model on CPU ──
    embedding_dim = 200
    total_epochs  = 100
    batch_size    = 1024
    lr            = 0.001
    ckpt_every    = 25

    logger.info(f"Training RotatE: dim={embedding_dim}, epochs={total_epochs}, batch={batch_size}, lr={lr}")

    model = RotatE(
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

    # ── Train in blocks ──
    total_loss = None
    for block_start in range(0, total_epochs, ckpt_every):
        block_end = min(block_start + ckpt_every, total_epochs)
        n_ep = block_end - block_start
        logger.info(f"Training epochs {block_start+1}-{block_end} ...")
        t_block = time.time()
        losses = training_loop.train(
            triples_factory=training_factory,
            num_epochs=n_ep,
            batch_size=batch_size,
        )
        block_time = time.time() - t_block
        total_loss = losses[-1] if losses else total_loss
        logger.info(f"Epoch {block_end}/{total_epochs} done — loss: {total_loss:.6f} ({block_time/60:.1f} min)")

        # Checkpoint
        ckpt_path = ckpt_dir / f"checkpoint_epoch{block_end}.pt"
        torch.save(model.state_dict(), ckpt_path)
        logger.info(f"Checkpoint saved: {ckpt_path}")

    logger.info(f"Training done. Final loss: {total_loss:.6f}")

    # ── SAFETY: Save model + embeddings BEFORE evaluation ──
    model_path = out_dir / "model.pt"
    torch.save(model.state_dict(), model_path)
    logger.info(f"Model saved to {model_path} ({model_path.stat().st_size / 1e6:.1f} MB)")

    emb_dir = out_dir / "embeddings"
    emb_dir.mkdir(exist_ok=True)
    entity_emb = model.entity_representations[0](indices=None).detach().cpu().numpy()
    relation_emb = model.relation_representations[0](indices=None).detach().cpu().numpy()
    np.savez(emb_dir / "entity_embeddings.npz", embeddings=entity_emb)
    np.savez(emb_dir / "relation_embeddings.npz", embeddings=relation_emb)
    logger.info(f"Embeddings saved: entities {entity_emb.shape}, relations {relation_emb.shape}")
    del entity_emb, relation_emb; gc.collect()

    # ── Evaluate — try GPU first, fall back to CPU ──
    logger.info("Running rank-based evaluation...")
    model.eval()

    eval_device = device
    if torch.cuda.is_available():
        try:
            logger.info("Attempting GPU evaluation...")
            model_gpu = model.to("cuda")
            test_triples = testing_factory.mapped_triples.to("cuda")
            train_triples = training_factory.mapped_triples.to("cuda")
            eval_device = "cuda"
            logger.info("GPU eval setup OK")
        except Exception as e:
            logger.warning(f"GPU eval failed ({e}), using CPU")
            model_gpu = model.to("cpu")
            test_triples = testing_factory.mapped_triples
            train_triples = training_factory.mapped_triples
            eval_device = "cpu"
    else:
        model_gpu = model
        test_triples = testing_factory.mapped_triples
        train_triples = training_factory.mapped_triples

    t0 = time.time()
    evaluator = RankBasedEvaluator()
    results = evaluator.evaluate(
        model=model_gpu,
        mapped_triples=test_triples,
        additional_filter_triples=[train_triples],
        batch_size=128,
    )
    eval_time = time.time() - t0
    logger.info(f"Evaluation completed in {eval_time/60:.1f} minutes on {eval_device}")

    rm = results.to_dict()

    # Parse metrics
    def extract_metrics(rm_dict):
        metrics = {}
        try:
            if isinstance(rm_dict.get("both"), str):
                import ast
                both = ast.literal_eval(rm_dict["both"])
                r = both.get("realistic", {})
            elif isinstance(rm_dict.get("both"), dict):
                r = rm_dict["both"].get("realistic", {})
            else:
                r = {}
            metrics["mrr"] = r.get("inverse_harmonic_mean_rank")
            metrics["hits_at_1"] = r.get("hits_at_1")
            metrics["hits_at_3"] = r.get("hits_at_3")
            metrics["hits_at_5"] = r.get("hits_at_5")
            metrics["hits_at_10"] = r.get("hits_at_10")
            metrics["amr"] = r.get("arithmetic_mean_rank")
            metrics["gmr"] = r.get("geometric_mean_rank")
        except Exception as e:
            logger.warning(f"Could not parse metrics: {e}")
        return metrics

    metrics = extract_metrics(rm)
    logger.info(f"MRR: {metrics.get('mrr')}")
    logger.info(f"Hits@1: {metrics.get('hits_at_1')}  Hits@3: {metrics.get('hits_at_3')}  Hits@5: {metrics.get('hits_at_5')}  Hits@10: {metrics.get('hits_at_10')}")

    summary = {
        "model": "RotatE",
        "version": "v3",
        "kg": "v3_nan_filtered",
        "embedding_dim": embedding_dim,
        "complex_dim": embedding_dim * 2,
        "epochs": total_epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "loss_function": "SLCWA",
        "final_loss": round(float(total_loss), 6),
        "seed": 42,
        "entities": int(full_factory.num_entities),
        "relations": int(full_factory.num_relations),
        "train_triples": int(training_factory.num_triples),
        "test_triples": int(testing_factory.num_triples),
        "metrics": {k: round(v, 5) if v else None for k, v in metrics.items()},
        "eval_time_minutes": round(eval_time / 60, 2),
        "train_device": "cpu",
        "eval_device": eval_device,
    }

    summary_path = out_dir / "rotatE_v3_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {summary_path}")

    full_path = out_dir / "rotatE_v3_full_metrics.json"
    with open(full_path, "w") as f:
        json.dump({k: str(v) for k, v in rm.items()}, f, indent=2)
    logger.info(f"Full metrics saved to {full_path}")

    logger.info("=== RotatE v3 TRAINING + EVALUATION COMPLETE ===")

if __name__ == "__main__":
    main()
