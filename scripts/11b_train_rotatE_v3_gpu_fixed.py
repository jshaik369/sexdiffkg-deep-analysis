#!/usr/bin/env python3
"""
Train RotatE v3 on GPU — 100 epochs, smaller batch size for GB10 memory.
Fixed: batch_size=256 to avoid OOM on unified memory GPU.
Checkpoints every 25 epochs. Saves model BEFORE eval.

Author: JShaik (jshaik@coevolvenetwork.com)
"""
import json, logging, time, gc
from pathlib import Path
import numpy as np, pandas as pd, torch
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    kg_dir   = Path("data/kg")
    out_dir  = Path("results/kg_embeddings/RotatE")
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = out_dir / "checkpoints"
    ckpt_dir.mkdir(exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

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

    # Free dataframe memory
    del df
    gc.collect()

    training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=42)
    logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")

    # ── RotatE model — smaller batch for GB10 unified memory ──
    embedding_dim = 200  # complex dim = 400
    total_epochs  = 100
    batch_size    = 256   # Reduced from 1024 to avoid OOM
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

    # ── Dry run: 1 epoch to verify memory fits ──
    logger.info("Dry run: 1 epoch to verify memory...")
    try:
        dry_losses = training_loop.train(
            triples_factory=training_factory,
            num_epochs=1,
            batch_size=batch_size,
        )
        logger.info(f"Dry run OK — loss: {dry_losses[-1]:.6f}")
    except RuntimeError as e:
        if "memory" in str(e).lower() or "sub_batch" in str(e).lower():
            logger.error(f"OOM even at batch_size={batch_size}. Trying batch_size=128...")
            batch_size = 128
            # Reset model
            model = RotatE(
                triples_factory=training_factory,
                embedding_dim=embedding_dim,
                random_seed=42,
            ).to(device)
            optimizer = torch.optim.Adam(params=model.get_grad_params(), lr=lr)
            training_loop = SLCWATrainingLoop(
                model=model, triples_factory=training_factory, optimizer=optimizer,
            )
            dry_losses = training_loop.train(
                triples_factory=training_factory, num_epochs=1, batch_size=batch_size,
            )
            logger.info(f"Dry run OK at batch_size={batch_size} — loss: {dry_losses[-1]:.6f}")
        else:
            raise

    # ── Train remaining epochs in blocks with checkpoints ──
    # Already did 1 epoch in dry run, so 99 more
    remaining = total_epochs - 1
    total_loss = dry_losses[-1] if dry_losses else None
    epochs_done = 1

    while epochs_done < total_epochs:
        # Next checkpoint boundary
        next_ckpt = min(((epochs_done // ckpt_every) + 1) * ckpt_every, total_epochs)
        n_ep = next_ckpt - epochs_done
        if n_ep <= 0:
            break

        logger.info(f"Training epochs {epochs_done+1}-{next_ckpt} ({n_ep} epochs) ...")
        losses = training_loop.train(
            triples_factory=training_factory,
            num_epochs=n_ep,
            batch_size=batch_size,
        )
        total_loss = losses[-1] if losses else total_loss
        epochs_done = next_ckpt
        logger.info(f"Epoch {epochs_done}/{total_epochs} done — loss: {total_loss:.6f}")

        # Checkpoint
        ckpt_path = ckpt_dir / f"checkpoint_epoch{epochs_done}.pt"
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

    # Free embedding arrays
    del entity_emb, relation_emb
    gc.collect()

    # ── Evaluate ──
    logger.info("Running rank-based evaluation...")
    model.eval()
    t0 = time.time()
    evaluator = RankBasedEvaluator()  # No 'ks' — PyKEEN 1.11.x
    results = evaluator.evaluate(
        model=model,
        mapped_triples=testing_factory.mapped_triples.to(device),
        additional_filter_triples=[training_factory.mapped_triples.to(device)],
        batch_size=128,  # Smaller eval batch for safety
    )
    eval_time = time.time() - t0
    logger.info(f"Evaluation completed in {eval_time/60:.1f} minutes")

    rm = results.to_dict()

    # Parse metrics from the nested dict structure
    def extract_metrics(rm_dict):
        """Extract from PyKEEN's to_dict() which returns nested dicts as strings."""
        metrics = {}
        try:
            # Try both.realistic first
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
        "device": device,
    }

    summary_path = out_dir / "rotatE_v3_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {summary_path}")

    # Full metrics dump
    full_path = out_dir / "rotatE_v3_full_metrics.json"
    with open(full_path, "w") as f:
        json.dump({k: str(v) for k, v in rm.items()}, f, indent=2)
    logger.info(f"Full metrics saved to {full_path}")

    logger.info("=== RotatE v3 TRAINING + EVALUATION COMPLETE ===")

if __name__ == "__main__":
    main()
