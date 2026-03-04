#!/usr/bin/env python3
"""
Retrain DistMult on KG v4.1 (with real GTEx sex-DE data).

KG v4.1: 109,867 nodes, 1,822,851 edges (289 real GTEx edges vs 105 fake in v4.0)
Previous DistMult v4: MRR 0.09316, Hits@10 18.42%, AMRI 0.9906
"""
import json
import time
import torch
import pandas as pd
from pathlib import Path
from pykeen.triples import TriplesFactory
from pykeen.models import DistMult
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator
from pykeen.losses import MarginRankingLoss

BASE = Path("/home/jshaik369/sexdiffkg")
KG = BASE / "data" / "kg_v4"
OUT = BASE / "results" / "kg_embeddings"

print("=" * 60)
print("DistMult v4.1 Training (KG with real GTEx data)")
print("=" * 60)

# Load triples
df = pd.read_csv(KG / "triples.tsv", sep="\t", header=None, names=["h", "r", "t"])
df = df[~df["h"].isin(["nan", ""]) & ~df["t"].isin(["nan", ""])]
df = df.dropna()
print(f"Triples: {len(df):,} (after NaN filter)")

tf = TriplesFactory.from_labeled_triples(df[["h", "r", "t"]].values)
train, test = tf.split([0.9, 0.1], random_state=42)
print(f"Train: {train.num_triples:,}  Test: {test.num_triples:,}")
print(f"Entities: {tf.num_entities:,}  Relations: {tf.num_relations}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

model = DistMult(
    triples_factory=train,
    embedding_dim=200,
    loss=MarginRankingLoss(margin=1.0),
).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
training_loop = SLCWATrainingLoop(model=model, triples_factory=train, optimizer=optimizer)

print(f"\nTraining 100 epochs...")
t0 = time.time()
losses = training_loop.train(triples_factory=train, num_epochs=100, batch_size=512, use_tqdm=True, use_tqdm_batch=True)
train_time = time.time() - t0
print(f"Training: {train_time/60:.1f} min")

# Save model
model_dir = OUT / "DistMult_v41"
model_dir.mkdir(parents=True, exist_ok=True)
torch.save(model.state_dict(), model_dir / "model.pth")
print(f"Model saved to {model_dir}")

# Evaluate
print("\nEvaluating...")
evaluator = RankBasedEvaluator()
results = evaluator.evaluate(model, test, batch_size=256)

mrr = float(results.get_metric("both.realistic.inverse_harmonic_mean_rank"))
h10 = float(results.get_metric("both.realistic.hits_at_10"))
amr = float(results.get_metric("both.realistic.arithmetic_mean_rank"))
amri = 1.0 - (2.0 * amr) / (tf.num_entities + 1)

print(f"\n{'='*60}")
print(f"DistMult v4.1 Results")
print(f"{'='*60}")
print(f"MRR:      {mrr:.5f}")
print(f"Hits@10:  {h10:.5f}")
print(f"AMR:      {amr:.1f}")
print(f"AMRI:     {amri:.4f}")
print(f"Top %:    {(1-amri)*100:.2f}%")
print(f"Train:    {train_time/60:.1f} min")

# Compare with v4.0
v4_mrr = 0.09316
v4_amri = 0.9906
print(f"\nDelta from v4.0:")
print(f"  MRR:  {mrr:.5f} vs {v4_mrr:.5f} ({(mrr-v4_mrr)/v4_mrr*100:+.1f}%)")
print(f"  AMRI: {amri:.4f} vs {v4_amri:.4f}")

metrics = {
    "model": "DistMult_v4.1",
    "kg_version": "v4.1_gtex_real",
    "entities": tf.num_entities,
    "relations": tf.num_relations,
    "train_triples": train.num_triples,
    "test_triples": test.num_triples,
    "dim": 200,
    "epochs": 100,
    "batch_size": 512,
    "lr": 0.001,
    "mrr": mrr,
    "hits_at_10": h10,
    "amr": amr,
    "amri": amri,
    "training_time_min": round(train_time/60, 1),
    "device": str(device),
    "comparison": {"v4_mrr": v4_mrr, "v4_amri": v4_amri}
}
with open(OUT / "distmult_v41_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(f"\nMetrics saved to {OUT}/distmult_v41_metrics.json")
