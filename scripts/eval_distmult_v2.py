#!/usr/bin/env python3
"""Train + evaluate DistMult on KG v2 (normalized drugs). 10 epochs (loss plateaus by epoch 6)."""
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

# Use KG v2 (normalized drugs)
df = pd.read_csv("data/kg_v2/triples.tsv", sep="\t", header=None, names=["h","r","t"])
df = df.dropna().reset_index(drop=True)
df["h"]=df["h"].astype(str); df["r"]=df["r"].astype(str); df["t"]=df["t"].astype(str)
logger.info(f"Loaded {len(df):,} triples")

ta = df[["h","r","t"]].values
ff = TriplesFactory.from_labeled_triples(triples=ta, create_inverse_triples=False)
tr, te = ff.split(ratios=[0.9, 0.1], random_state=42)
logger.info(f"Entities: {ff.num_entities:,}, Relations: {ff.num_relations:,}")
logger.info(f"Train: {tr.num_triples:,}, Test: {te.num_triples:,}")

m = DistMult(triples_factory=tr, embedding_dim=200, random_seed=42).to(device)
o = torch.optim.Adam(params=m.get_grad_params(), lr=0.001)
tl = SLCWATrainingLoop(model=m, triples_factory=tr, optimizer=o)

logger.info("Training DistMult 10 epochs (loss plateaus by epoch 6)...")
losses = tl.train(triples_factory=tr, num_epochs=10, batch_size=512)
logger.info(f"Final loss: {losses[-1]:.6f}")

logger.info("Evaluating (filtered, rank-based)...")
ev = RankBasedEvaluator()
mr = ev.evaluate(model=m, mapped_triples=te.mapped_triples, batch_size=512,
                 additional_filter_triples=[tr.mapped_triples])

metrics = {}
try: metrics["mrr"] = float(mr.get_metric("both.realistic.inverse_harmonic_mean_rank"))
except Exception as e: logger.warning(f"MRR: {e}")
for k in [1, 3, 5, 10]:
    try: metrics[f"hits_at_{k}"] = float(mr.get_metric(f"both.realistic.hits_at_{k}"))
    except Exception as e: logger.warning(f"Hits@{k}: {e}")

logger.info("=== DistMult v2 Results ===")
for k, v in metrics.items():
    logger.info(f"  {k}: {v:.6f}")

# Save
out = Path("results/kg_embeddings"); out.mkdir(parents=True, exist_ok=True)
md = out / "DistMult_v2"; md.mkdir(exist_ok=True)
torch.save(m.state_dict(), md / "model.pt")

# Save embeddings
ed = md / "embeddings"; ed.mkdir(exist_ok=True)
ee = m.entity_representations[0](indices=None).cpu().detach().numpy()
i2e = {v:k for k,v in ff.entity_to_id.items()}
eids = [i2e[i] for i in range(len(i2e))]
np.savez(ed / "entity_embeddings.npz", embeddings=ee, ids=eids)

re = m.relation_representations[0](indices=None).cpu().detach().numpy()
i2r = {v:k for k,v in ff.relation_to_id.items()}
rids = [i2r[i] for i in range(len(i2r))]
np.savez(ed / "relation_embeddings.npz", embeddings=re, ids=rids)

summary = {
    "model": "DistMult", "kg": "v2_normalized", "dim": 200, "epochs": 10,
    "batch_size": 512, "lr": 0.001,
    "initial_loss": float(losses[0]), "final_loss": float(losses[-1]),
    "entities": ff.num_entities, "relations": ff.num_relations,
    "train_triples": tr.num_triples, "test_triples": te.num_triples,
    "metrics": metrics, "device": device,
}
with open(out / "distmult_v2_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

logger.info(f"Saved to {out}")
logger.info("DISTMULT_V2_COMPLETE")
