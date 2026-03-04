#!/usr/bin/env python3
"""Quick evaluation of saved DistMult v4.1 model"""
import json, torch, pandas as pd
from pathlib import Path
from pykeen.triples import TriplesFactory
from pykeen.models import DistMult
from pykeen.evaluation import RankBasedEvaluator

BASE = Path("/home/jshaik369/sexdiffkg")
KG = BASE / "data" / "kg_v4"
MODEL_PATH = BASE / "results" / "kg_embeddings" / "DistMult_v41" / "model.pth"

print("Loading triples...")
df = pd.read_csv(KG / "triples.tsv", sep="\t", header=None, names=["h", "r", "t"])
df = df.dropna()
tf = TriplesFactory.from_labeled_triples(df[["h", "r", "t"]].values)
train, test = tf.split([0.9, 0.1], random_state=42)
print(f"Train: {train.num_triples:,}  Test: {test.num_triples:,}")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DistMult(triples_factory=train, embedding_dim=200).to(device)
state = torch.load(MODEL_PATH, map_location=device, weights_only=True)
model.load_state_dict(state)
model.eval()
print(f"Model loaded from {MODEL_PATH}")

print("Evaluating (filtered)...")
evaluator = RankBasedEvaluator()
results = evaluator.evaluate(
    model=model,
    mapped_triples=test.mapped_triples,
    additional_filter_triples=[train.mapped_triples],
    batch_size=256,
)

mrr = float(results.get_metric("both.realistic.inverse_harmonic_mean_rank"))
h1 = float(results.get_metric("both.realistic.hits_at_1"))
h10 = float(results.get_metric("both.realistic.hits_at_10"))
amr = float(results.get_metric("both.realistic.arithmetic_mean_rank"))
amri = 1.0 - (2.0 * amr) / (tf.num_entities + 1)

print(f"\nDistMult v4.1 Results:")
print(f"MRR:    {mrr:.5f}")
print(f"Hits@1: {h1:.5f}")
print(f"Hits@10:{h10:.5f}")
print(f"AMRI:   {amri:.4f}")

metrics = {
    "model": "DistMult_v4.1",
    "kg_version": "v4.1",
    "entities": tf.num_entities,
    "relations": tf.num_relations,
    "dim": 200, "epochs": 100,
    "mrr": mrr, "hits_at_1": h1, "hits_at_10": h10,
    "amr": amr, "amri": amri, "device": str(device)
}
out = BASE / "results" / "kg_embeddings" / "distmult_v41_metrics.json"
with open(out, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"Metrics saved to {out}")
