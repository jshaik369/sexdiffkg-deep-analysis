import json, logging, torch, numpy as np, pandas as pd
from pathlib import Path
from pykeen.triples import TriplesFactory
from pykeen.models import DistMult
from pykeen.training import SLCWATrainingLoop
from pykeen.evaluation import RankBasedEvaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Device: {device}")

# Load triples from v1 KG (same as original training)
kg_dir = Path("data/kg")
df = pd.read_csv(kg_dir / "triples.tsv", sep="\t", header=None, names=["h","r","t"])
df = df.dropna().reset_index(drop=True)
df["h"] = df["h"].astype(str); df["r"] = df["r"].astype(str); df["t"] = df["t"].astype(str)
logger.info(f"Loaded {len(df):,} triples")

triples_array = df[["h","r","t"]].values
full_factory = TriplesFactory.from_labeled_triples(triples=triples_array, create_inverse_triples=False)
training_factory, testing_factory = full_factory.split(ratios=[0.9, 0.1], random_state=42)
logger.info(f"Train: {training_factory.num_triples:,}, Test: {testing_factory.num_triples:,}")

# Quick 5-epoch train to get eval working, then full 100ep
model = DistMult(triples_factory=training_factory, embedding_dim=200, random_seed=42).to(device)
optimizer = torch.optim.Adam(params=model.get_grad_params(), lr=0.001)
training_loop = SLCWATrainingLoop(model=model, triples_factory=training_factory, optimizer=optimizer)

# Train 100 epochs (this time with working eval)
logger.info("Training DistMult 100 epochs...")
losses = training_loop.train(triples_factory=training_factory, num_epochs=100, batch_size=512)
logger.info(f"Training done. Final loss: {losses[-1]:.6f}")

# Evaluate (no ks param - use defaults)
logger.info("Evaluating with rank-based metrics...")
evaluator = RankBasedEvaluator()
metric_results = evaluator.evaluate(
    model=model,
    mapped_triples=testing_factory.mapped_triples,
    batch_size=512,
    additional_filter_triples=[training_factory.mapped_triples],
)

metrics = {}
try:
    metrics["mrr"] = float(metric_results.get_metric("both.realistic.inverse_harmonic_mean_rank"))
except Exception as e:
    logger.warning(f"MRR error: {e}")

for k in [1, 3, 5, 10]:
    try:
        metrics[f"hits_at_{k}"] = float(metric_results.get_metric(f"both.realistic.hits_at_{k}"))
    except Exception as e:
        logger.warning(f"Hits@{k} error: {e}")

logger.info("=== DistMult Evaluation Results ===")
for k, v in metrics.items():
    logger.info(f"  {k}: {v:.6f}")

# Save model and embeddings
output_dir = Path("results/kg_embeddings")
output_dir.mkdir(parents=True, exist_ok=True)
model_dir = output_dir / "DistMult"
model_dir.mkdir(exist_ok=True)
torch.save(model.state_dict(), model_dir / "model.pt")

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

# Save summary
summary = {
    "model": "DistMult", "embedding_dim": 200, "epochs": 100,
    "batch_size": 512, "learning_rate": 0.001,
    "final_loss": float(losses[-1]), "initial_loss": float(losses[0]),
    "num_entities": full_factory.num_entities, "num_relations": full_factory.num_relations,
    "training_triples": training_factory.num_triples, "testing_triples": testing_factory.num_triples,
    "evaluation": metrics, "device": device,
}
with open(output_dir / "distmult_training_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

logger.info(f"All saved to {output_dir}")
logger.info("DISTMULT_COMPLETE")
