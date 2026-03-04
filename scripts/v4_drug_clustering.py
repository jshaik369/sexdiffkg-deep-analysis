#!/usr/bin/env python3
"""Drug clustering analysis using ComplEx v4 embeddings."""
import json
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

BASE = Path("/home/jshaik369/sexdiffkg")

print("=" * 60)
print("Drug Clustering Analysis (ComplEx v4 Embeddings)")
print("=" * 60)

# Load triples to get entity mapping
triples = pd.read_csv(BASE / "data" / "kg_v4" / "triples.tsv", sep="\t", header=None, names=["h", "r", "t"])
triples = triples[~triples["h"].isin(["nan", ""]) & ~triples["t"].isin(["nan", ""])]
triples = triples.dropna()

from pykeen.triples import TriplesFactory
tf = TriplesFactory.from_labeled_triples(triples[["h", "r", "t"]].values)
entity_to_id = tf.entity_to_id
id_to_entity = {v: k for k, v in entity_to_id.items()}

# Load ComplEx model
print("Loading ComplEx model...")
model_data = torch.load(BASE / "results" / "kg_embeddings_v4" / "ComplEx" / "model.pt", map_location="cpu", weights_only=False)

# Extract entity embeddings
# ComplEx stores real and imaginary parts
try:
    real = model_data["entity_representations.0._embeddings.weight"].numpy()
    imag = model_data["entity_representations.1._embeddings.weight"].numpy()
    # Concatenate real and imaginary parts for clustering
    embeddings = np.concatenate([real, imag], axis=1)
    print(f"Embedding shape: {embeddings.shape} (real + imag)")
except KeyError:
    # Try alternative key structure
    keys = [k for k in model_data.keys() if "entity" in k.lower()]
    print(f"Available keys: {keys[:5]}")
    emb_key = [k for k in keys if "weight" in k][0]
    embeddings = model_data[emb_key].numpy()
    print(f"Embedding shape: {embeddings.shape}")

# Get drug entities
nodes = pd.read_csv(BASE / "data" / "kg_v4" / "nodes.tsv", sep="\t")
drug_nodes = nodes[nodes.iloc[:, 1] == "Drug"] if len(nodes.columns) > 1 else nodes[nodes["type"] == "Drug"]
drug_names = set(drug_nodes.iloc[:, 0].values)
print(f"Drug nodes in KG: {len(drug_names)}")

# Filter to drugs that are in the embedding
drug_ids = {}
for name in drug_names:
    if name in entity_to_id:
        drug_ids[name] = entity_to_id[name]
print(f"Drugs with embeddings: {len(drug_ids)}")

if len(drug_ids) < 20:
    print("Too few drugs for clustering, exiting")
    exit(1)

# Extract drug embeddings
drug_names_list = list(drug_ids.keys())
drug_indices = [drug_ids[n] for n in drug_names_list]
drug_embeddings = embeddings[drug_indices]
print(f"Drug embedding matrix: {drug_embeddings.shape}")

# PCA for visualization
print("\nRunning PCA...")
pca = PCA(n_components=min(50, drug_embeddings.shape[0]-1))
drug_pca = pca.fit_transform(drug_embeddings)
var_explained = pca.explained_variance_ratio_.cumsum()
print(f"Variance explained by 10 PCs: {var_explained[min(9, len(var_explained)-1)]:.1%}")
print(f"Variance explained by 50 PCs: {var_explained[-1]:.1%}")

# K-Means clustering
K = 20
print(f"\nRunning K-Means (K={K})...")
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
clusters = kmeans.fit_predict(drug_pca[:, :min(50, drug_pca.shape[1])])

# Load signals for sex-bias analysis per cluster
signals = pd.read_parquet(BASE / "results" / "signals_v4" / "sex_differential_v4.parquet")

cluster_stats = []
for k in range(K):
    drugs_in_cluster = [drug_names_list[i] for i in range(len(clusters)) if clusters[i] == k]
    cluster_signals = signals[signals.drug_name.isin(drugs_in_cluster)]
    n_signals = len(cluster_signals)
    if n_signals > 0:
        f_ratio = len(cluster_signals[cluster_signals.direction == "female_higher"]) / n_signals
        mean_log = cluster_signals.log_ratio.mean()
    else:
        f_ratio = 0.5
        mean_log = 0.0
    
    bias = "female-biased" if f_ratio > 0.55 else ("male-biased" if f_ratio < 0.45 else "balanced")
    
    cluster_stats.append({
        "cluster": k,
        "n_drugs": len(drugs_in_cluster),
        "n_signals": n_signals,
        "female_ratio": round(f_ratio, 3),
        "mean_log_ratio": round(mean_log, 4),
        "bias_direction": bias,
        "top_drugs": drugs_in_cluster[:5]
    })

# Print results
print(f"\n{'='*70}")
print(f"{'Cluster':>8} {'Drugs':>6} {'Signals':>8} {'F%':>6} {'MeanLR':>8} {'Bias'}")
print(f"{'='*70}")
for s in sorted(cluster_stats, key=lambda x: -x["n_signals"]):
    print(f"  {s['cluster']:>5}   {s['n_drugs']:>5}   {s['n_signals']:>7}  {s['female_ratio']:.3f}  {s['mean_log_ratio']:>+.4f}  {s['bias_direction']}")

# Summary
f_biased = sum(1 for s in cluster_stats if s["bias_direction"] == "female-biased")
m_biased = sum(1 for s in cluster_stats if s["bias_direction"] == "male-biased")
balanced = sum(1 for s in cluster_stats if s["bias_direction"] == "balanced")
print(f"\nCluster bias summary: {f_biased} female-biased, {m_biased} male-biased, {balanced} balanced")

# Save results
output = {
    "model": "ComplEx_v4",
    "n_drugs": len(drug_ids),
    "k_clusters": K,
    "pca_variance_50pc": round(float(var_explained[-1]), 4),
    "cluster_summary": {
        "female_biased": f_biased,
        "male_biased": m_biased,
        "balanced": balanced
    },
    "clusters": cluster_stats
}

out_path = BASE / "results" / "analysis" / "v4_drug_clustering.json"
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to {out_path}")

# Save PCA coordinates for visualization
pca_df = pd.DataFrame({
    "drug": drug_names_list,
    "cluster": clusters,
    "pca1": drug_pca[:, 0],
    "pca2": drug_pca[:, 1],
})
pca_path = BASE / "results" / "analysis" / "v4_drug_pca_coordinates.tsv"
pca_df.to_csv(pca_path, sep="\t", index=False)
print(f"PCA coordinates saved to {pca_path}")
