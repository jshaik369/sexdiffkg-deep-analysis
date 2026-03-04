#!/usr/bin/env python3
"""SexDiffKG analysis — optimized for speed."""
import json, time
from pathlib import Path
from collections import defaultdict
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

base = Path("/home/jshaik369/sexdiffkg")
out_dir = base / "results" / "analysis"
out_dir.mkdir(parents=True, exist_ok=True)

t0 = time.time()
print("Loading nodes...")
nodes = pd.read_csv(base / "data/kg/nodes.tsv", sep="\t")

print("Loading edges (targets only)...")
# Only load target edges for target analysis - skip full 5.8M edge load
edges_chunks = pd.read_csv(base / "data/kg/edges.tsv", sep="\t", chunksize=500000)
target_edges = []
edge_stats = {}
total_edges = 0
for chunk in edges_chunks:
    total_edges += len(chunk)
    for pred, cnt in chunk["predicate"].value_counts().items():
        edge_stats[pred] = edge_stats.get(pred, 0) + int(cnt)
    targets = chunk[chunk["predicate"] == "targets"]
    if len(targets) > 0:
        target_edges.append(targets)
target_edges = pd.concat(target_edges) if target_edges else pd.DataFrame()
print(f"  Total edges: {total_edges:,}, target edges: {len(target_edges):,}")

print("Loading signals...")
sexdiff = pd.read_parquet(base / "results/signals/sex_differential.parquet")
ror_by_sex = pd.read_parquet(base / "results/signals/ror_by_sex.parquet")

print("Loading embeddings...")
entity_emb = np.load(base / "results/kg_embeddings/DistMult/embeddings/entity_embeddings.npz")["embeddings"]
relation_emb = np.load(base / "results/kg_embeddings/DistMult/embeddings/relation_embeddings.npz")["embeddings"]

# Entity mapping
triples = pd.read_csv(base / "data/kg/triples.tsv", sep="\t", header=None, names=["h","r","t"])
triples = triples.dropna().reset_index(drop=True)
triples["h"] = triples["h"].astype(str); triples["r"] = triples["r"].astype(str); triples["t"] = triples["t"].astype(str)
all_entities = sorted(set(triples["h"].unique()) | set(triples["t"].unique()))
entity2idx = {e: i for i, e in enumerate(all_entities)}
del triples  # Free memory

# KG stats
node_stats = nodes["category"].value_counts().to_dict()

# Sex-diff analysis
robust = sexdiff[sexdiff["min_reports"] >= 10].copy()
strong = robust[robust["log_ror_ratio"].abs() > 1.0].copy()
strong_female = strong[strong["direction"] == "female_higher"]
strong_male = strong[strong["direction"] == "male_higher"]
print(f"Strong signals: {len(strong):,} (F:{len(strong_female):,}, M:{len(strong_male):,})")

# Drug embeddings + clustering
drug_nodes = nodes[nodes["category"] == "Drug"]
name_to_id = dict(zip(drug_nodes["name"].str.upper(), drug_nodes["id"]))
drug_with_emb = [d for d in drug_nodes["id"].tolist() if d in entity2idx and entity2idx[d] < entity_emb.shape[0]]
drug_indices = [entity2idx[d] for d in drug_with_emb]
drug_emb_matrix = entity_emb[drug_indices]
norms = np.linalg.norm(drug_emb_matrix, axis=1, keepdims=True)
norms[norms == 0] = 1
drug_emb_norm = drug_emb_matrix / norms

print(f"Clustering {len(drug_with_emb):,} drugs...")
n_clusters = 20
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
drug_clusters = kmeans.fit_predict(drug_emb_norm)
drug_to_cluster = {drug_with_emb[i]: int(drug_clusters[i]) for i in range(len(drug_with_emb))}
pca = PCA(n_components=2, random_state=42)
drug_pca = pca.fit_transform(drug_emb_norm)
print(f"PCA variance: {pca.explained_variance_ratio_.sum():.3f}")

# Match signals to clusters
strong_c = strong.copy()
strong_c["drug_id"] = strong_c["drug_name"].map(name_to_id)
strong_c["cluster"] = strong_c["drug_id"].map(drug_to_cluster)
matched = strong_c.dropna(subset=["cluster"])
print(f"Matched: {len(matched):,} / {len(strong):,}")

# Cluster profiles
cluster_profiles = []
for c in range(n_clusters):
    cs = matched[matched["cluster"] == c]
    nd = sum(1 for v in drug_to_cluster.values() if v == c)
    cluster_profiles.append({
        "cluster": c, "n_drugs": nd, "n_signals": len(cs),
        "female_biased": int((cs["direction"] == "female_higher").sum()),
        "male_biased": int((cs["direction"] == "male_higher").sum()),
        "female_ratio": round((cs["direction"] == "female_higher").mean(), 3) if len(cs) > 0 else 0.5,
        "top_aes": cs["pt"].value_counts().head(5).to_dict(),
        "top_drugs": cs["drug_name"].value_counts().head(5).to_dict(),
    })

# Target analysis
print("Target analysis...")
drug_targets = defaultdict(set)
for _, row in target_edges.iterrows():
    drug_targets[row["subject"]].add(row["object"])

target_sex_profile = defaultdict(lambda: {"f": set(), "m": set(), "all": set()})
for _, row in matched.iterrows():
    did = row["drug_id"]
    if pd.isna(did): continue
    for t in drug_targets.get(did, set()):
        target_sex_profile[t]["all"].add(did)
        if row["direction"] == "female_higher":
            target_sex_profile[t]["f"].add(did)
        else:
            target_sex_profile[t]["m"].add(did)

target_bias = []
for target, p in target_sex_profile.items():
    nf, nm, nt = len(p["f"]), len(p["m"]), len(p["all"])
    if nt >= 3:
        ti = nodes[nodes["id"] == target]
        gn = ti["name"].iloc[0] if len(ti) > 0 else target
        target_bias.append({
            "target_id": target, "gene_name": gn, "total_drugs": nt,
            "female_biased_drugs": nf, "male_biased_drugs": nm,
            "female_fraction": round(nf / max(nt, 1), 3),
            "sex_bias_score": round((nf - nm) / max(nt, 1), 3),
        })

target_bias_df = pd.DataFrame(target_bias)
if len(target_bias_df) > 0:
    target_bias_df = target_bias_df.sort_values("sex_bias_score", key=abs, ascending=False)
print(f"Targets with sex bias: {len(target_bias_df)}")

# Drug signal counts
drug_signal_counts = strong.groupby("drug_name").agg(
    total_strong=("log_ror_ratio", "count"),
    female_biased=("direction", lambda x: (x == "female_higher").sum()),
    male_biased=("direction", lambda x: (x == "male_higher").sum()),
    max_ratio=("log_ror_ratio", lambda x: x.abs().max()),
).sort_values("total_strong", ascending=False)

ae_signal_counts = strong.groupby("pt").agg(
    total_strong=("log_ror_ratio", "count"),
    female_biased=("direction", lambda x: (x == "female_higher").sum()),
    male_biased=("direction", lambda x: (x == "male_higher").sum()),
    max_ratio=("log_ror_ratio", lambda x: x.abs().max()),
).sort_values("total_strong", ascending=False)

# Save
print("Saving results...")
ror_signal_count = int(ror_by_sex[ror_by_sex["signal"]].shape[0])
overall = {
    "pipeline": {
        "faers_reports_total": 14536008, "faers_female": 8744397, "faers_male": 5791611,
        "ror_signals_total": ror_signal_count,
        "sex_differential_signals": int(len(sexdiff)), "robust_signals": int(len(robust)),
        "strong_sex_diff_signals": int(len(strong)),
        "female_biased_strong": int(len(strong_female)), "male_biased_strong": int(len(strong_male)),
    },
    "knowledge_graph": {
        "nodes": int(len(nodes)), "edges": total_edges,
        "node_types": node_stats, "edge_types": edge_stats,
    },
    "embeddings": {
        "model": "DistMult", "version": "v3", "dim": 200, "epochs": 100,
        "entities": int(entity_emb.shape[0]), "relations": int(relation_emb.shape[0]),
        "mrr": 0.04762, "hits_at_10": 0.08852, "amri": 0.9807,
    },
    "analysis": {
        "drugs_clustered": len(drug_with_emb), "n_clusters": n_clusters,
        "pca_var_explained": round(float(pca.explained_variance_ratio_.sum()), 3),
        "targets_with_sex_bias": len(target_bias_df),
        "signals_matched": int(len(matched)),
    },
    "unique_drugs_sex_diff": int(sexdiff["drug_name"].nunique()),
    "unique_aes_sex_diff": int(sexdiff["pt"].nunique()),
}

with open(out_dir / "sexdiffkg_statistics.json", "w") as f:
    json.dump(overall, f, indent=2, default=str)
drug_signal_counts.head(100).to_csv(out_dir / "top_drugs_by_sex_diff.tsv", sep="\t")
ae_signal_counts.head(100).to_csv(out_dir / "top_aes_by_sex_diff.tsv", sep="\t")
strong_female.nlargest(200, "log_ror_ratio")[
    ["drug_name", "pt", "ror_female", "ror_male", "log_ror_ratio", "a_female", "a_male"]
].to_csv(out_dir / "top_female_biased_signals.tsv", sep="\t", index=False)
strong_male.nsmallest(200, "log_ror_ratio")[
    ["drug_name", "pt", "ror_female", "ror_male", "log_ror_ratio", "a_female", "a_male"]
].to_csv(out_dir / "top_male_biased_signals.tsv", sep="\t", index=False)
with open(out_dir / "cluster_profiles.json", "w") as f:
    json.dump(cluster_profiles, f, indent=2, default=str)
if len(target_bias_df) > 0:
    target_bias_df.to_csv(out_dir / "target_sex_bias.tsv", sep="\t", index=False)
pd.DataFrame({
    "drug_id": drug_with_emb, "cluster": drug_clusters,
    "pc1": drug_pca[:, 0], "pc2": drug_pca[:, 1],
}).to_csv(out_dir / "drug_pca_coordinates.tsv", sep="\t", index=False)

elapsed = time.time() - t0
print(f"\nDone in {elapsed/60:.1f} minutes")
print(f"\n{'='*60}")
print(f"  SexDiffKG Analysis COMPLETE")
print(f"{'='*60}")
print(f"  Signals: {len(sexdiff):,} total, {len(strong):,} strong")
print(f"  Female-biased: {len(strong_female):,}, Male-biased: {len(strong_male):,}")
print(f"  Drugs clustered: {len(drug_with_emb):,}")
print(f"  Targets with sex bias: {len(target_bias_df)}")
if len(target_bias_df) > 0:
    print(f"\n  Top female-biased targets:")
    for _, r in target_bias_df[target_bias_df["sex_bias_score"] > 0].head(5).iterrows():
        print(f'    {r["gene_name"]:30s} score={r["sex_bias_score"]:+.3f} ({r["total_drugs"]} drugs)')
    print(f"  Top male-biased targets:")
    for _, r in target_bias_df[target_bias_df["sex_bias_score"] < 0].head(5).iterrows():
        print(f'    {r["gene_name"]:30s} score={r["sex_bias_score"]:+.3f} ({r["total_drugs"]} drugs)')
print(f"\n  Files: {out_dir}")
print(f"{'='*60}")
