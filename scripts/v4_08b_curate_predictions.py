#!/usr/bin/env python3
"""
SexDiffKG v4 — Step 8b: Curate Link Predictions for Clinically Relevant Drugs
==============================================================================
Filters ComplEx predictions to well-established drugs (>=50 existing AE edges)
and generates interpretable results for the manuscript.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path.home() / "sexdiffkg"
KG_DIR = BASE / "data/kg_v4"
PRED_DIR = BASE / "results/link_predictions"

# Load triples
print("Loading triples...")
df = pd.read_csv(KG_DIR / "triples.tsv", sep="\t", header=None, names=["h", "r", "t"])
df = df.dropna()

# Count existing edges per drug
hae = df[df["r"] == "has_adverse_event"]
sdae = df[df["r"] == "sex_differential_adverse_event"]

drug_hae_counts = hae["h"].value_counts()
drug_sdae_counts = sdae["h"].value_counts()

# Load predictions
preds = pd.read_csv(PRED_DIR / "complex_v4_sdae_predictions.tsv", sep="\t")
print(f"Loaded {len(preds)} predictions")

# Add drug edge counts
preds["drug_hae_edges"] = preds["drug"].map(drug_hae_counts).fillna(0).astype(int)
preds["drug_sdae_edges"] = preds["drug"].map(drug_sdae_counts).fillna(0).astype(int)
preds["drug_total_edges"] = preds["drug_hae_edges"] + preds["drug_sdae_edges"]

# Filter 1: Well-established drugs (>=50 total AE edges)
well_established = preds[preds["drug_total_edges"] >= 50].copy()
print(f"\nWell-established drugs (>=50 AE edges): {len(well_established)} predictions")

# Filter 2: From those, get predictions WITH existing hae edge (drug-AE association known, but sex-diff not yet characterized)
known_assoc = well_established[well_established["has_adverse_event_edge"] == True].copy()
print(f"Known drug-AE associations (hae exists, sdae novel): {len(known_assoc)} predictions")

# Filter 3: Truly novel (no known association at all)  
truly_novel = well_established[well_established["has_adverse_event_edge"] == False].copy()
print(f"Truly novel drug-AE pairs: {len(truly_novel)} predictions")

# Print top 30 known associations (most clinically interpretable)
print(f"\n{'='*100}")
print(f"TOP 30 — Known Drug-AE Association, Predicted Novel Sex-Differential Signal")
print(f"(Drug-AE pair has 'has_adverse_event' edge but NO 'sex_differential_adverse_event' edge)")
print(f"{'='*100}")
print(f"{'Rank':>4} {'Score':>8} {'#AE':>5} {'Drug':<35} {'Adverse Event':<35}")
print("-" * 100)
for i, (_, r) in enumerate(known_assoc.head(30).iterrows()):
    print(f"{i+1:>4} {r['score']:>8.3f} {r['drug_total_edges']:>5} {r['drug_name_clean']:<35} {r['ae_name_clean']:<35}")

# Print top 30 truly novel
print(f"\n{'='*100}")
print(f"TOP 30 — Truly Novel Drug-AE Predictions (no existing edge)")
print(f"{'='*100}")
print(f"{'Rank':>4} {'Score':>8} {'#AE':>5} {'Drug':<35} {'Adverse Event':<35}")
print("-" * 100)
for i, (_, r) in enumerate(truly_novel.head(30).iterrows()):
    print(f"{i+1:>4} {r['score']:>8.3f} {r['drug_total_edges']:>5} {r['drug_name_clean']:<35} {r['ae_name_clean']:<35}")

# Drug class analysis for top predictions
print(f"\n{'='*100}")
print(f"DRUG FREQUENCY IN TOP 500 PREDICTIONS (well-established only)")
print(f"{'='*100}")
drug_freq = well_established["drug_name_clean"].value_counts().head(20)
for drug, count in drug_freq.items():
    total = well_established[well_established["drug_name_clean"] == drug]["drug_total_edges"].iloc[0]
    print(f"  {drug:<35} {count:>3} predictions ({total} existing AE edges)")

# Save curated results
known_assoc.to_csv(PRED_DIR / "curated_known_assoc_predictions.tsv", sep="\t", index=False)
truly_novel.to_csv(PRED_DIR / "curated_novel_predictions.tsv", sep="\t", index=False)

# Summary
summary = {
    "total_raw_predictions": len(preds),
    "well_established_predictions": len(well_established),
    "known_association_novel_sexdiff": len(known_assoc),
    "truly_novel_pairs": len(truly_novel),
    "unique_drugs_in_curated": well_established["drug_name_clean"].nunique(),
    "min_drug_ae_edges": 50,
}
with open(PRED_DIR / "curated_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nCurated results saved to: {PRED_DIR}/")
print(json.dumps(summary, indent=2))
