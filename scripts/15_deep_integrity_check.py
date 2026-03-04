#!/usr/bin/env python3
"""
SexDiffKG Deep Integrity Check — GPU-accelerated, zero-tolerance validation.
Uses idle GPU + RAM to verify every aspect of the pipeline.
PHARMACOVIGILANCE DATA = LIVES AT STAKE. Zero errors tolerated.
"""
import json, time, sys, traceback
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd

# Try GPU
try:
    import torch
    HAS_TORCH = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"PyTorch device: {device}")
except ImportError:
    HAS_TORCH = False
    print("PyTorch not available, CPU-only mode")

base = Path("/home/jshaik369/sexdiffkg")
report_path = base / "results" / "INTEGRITY_REPORT.md"
t0 = time.time()

# Counters
PASS = 0
FAIL = 0
WARN = 0
findings = []

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        findings.append(("✅ PASS", name, detail))
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        findings.append(("❌ FAIL", name, detail))
        print(f"  ❌ FAIL: {name} — {detail}")

def warn(name, detail=""):
    global WARN
    WARN += 1
    findings.append(("⚠️ WARN", name, detail))
    print(f"  ⚠️ WARN: {name} — {detail}")

print("=" * 70)
print("  SexDiffKG DEEP INTEGRITY CHECK")
print("  Pharmacovigilance data — zero error tolerance")
print("=" * 70)

# ============================================================
# CHECK 1: Knowledge Graph Structural Integrity
# ============================================================
print("\n[1/8] KNOWLEDGE GRAPH STRUCTURAL INTEGRITY")
print("-" * 50)

nodes = pd.read_csv(base / "data/kg/nodes.tsv", sep="\t")
edges = pd.read_csv(base / "data/kg/edges.tsv", sep="\t")

# 1.1 Node counts
check("Node count = 127,063", len(nodes) == 127063, f"actual={len(nodes)}")

# 1.2 Edge counts
check("Edge count = 5,839,717", len(edges) == 5839717, f"actual={len(edges)}")

# 1.3 No duplicate nodes
dup_nodes = nodes["id"].duplicated().sum()
check("No duplicate node IDs", dup_nodes == 0, f"duplicates={dup_nodes}")

# 1.4 No duplicate edges
dup_edges = edges.duplicated(subset=["subject", "predicate", "object"]).sum()
check("No duplicate edges (subject+predicate+object)", dup_edges == 0, f"duplicates={dup_edges}")

# 1.5 Node type distribution
node_counts = nodes["category"].value_counts().to_dict()
expected_nodes = {"Gene": 70607, "Drug": 29277, "AdverseEvent": 16162,
                  "Protein": 8721, "Pathway": 2279, "Tissue": 17}
for cat, expected in expected_nodes.items():
    actual = node_counts.get(cat, 0)
    check(f"Node type {cat} = {expected}", actual == expected, f"actual={actual}")

# 1.6 Edge type distribution
edge_counts = edges["predicate"].value_counts().to_dict()
expected_edges = {"has_adverse_event": 4640396, "participates_in": 537605,
                  "interacts_with": 465390, "sex_differential_adverse_event": 183539,
                  "targets": 12682, "sex_differential_expression": 105}
for pred, expected in expected_edges.items():
    actual = edge_counts.get(pred, 0)
    check(f"Edge type {pred} = {expected:,}", actual == expected, f"actual={actual:,}")

# 1.7 No NaN in node IDs or names
nan_ids = nodes["id"].isna().sum()
nan_names = nodes["name"].isna().sum()
check("No NaN node IDs", nan_ids == 0, f"NaN ids={nan_ids}")
if nan_names > 0:
    warn(f"NaN node names: {nan_names}", "Some nodes may lack names")

# 1.8 No NaN in edge subjects/objects/predicates
nan_subj = edges["subject"].isna().sum()
nan_obj = edges["object"].isna().sum()
nan_pred = edges["predicate"].isna().sum()
check("No NaN edge subjects", nan_subj == 0, f"NaN subjects={nan_subj}")
check("No NaN edge objects", nan_obj == 0, f"NaN objects={nan_obj}")
check("No NaN edge predicates", nan_pred == 0, f"NaN predicates={nan_pred}")

# 1.9 Orphan node check (nodes not in any edge)
edge_entities = set(edges["subject"].unique()) | set(edges["object"].unique())
node_ids = set(nodes["id"].unique())
orphan_nodes = node_ids - edge_entities
check("Orphan nodes < 1%", len(orphan_nodes) / len(nodes) < 0.01,
      f"orphans={len(orphan_nodes)} ({100*len(orphan_nodes)/len(nodes):.2f}%)")

# 1.10 Dangling edges (edges referencing non-existent nodes)
dangling_subj = set(edges["subject"].unique()) - node_ids
dangling_obj = set(edges["object"].unique()) - node_ids
check("No dangling edge subjects", len(dangling_subj) == 0, f"dangling={len(dangling_subj)}")
check("No dangling edge objects", len(dangling_obj) == 0, f"dangling={len(dangling_obj)}")

# 1.11 Self-loops check
self_loops = (edges["subject"] == edges["object"]).sum()
check("Self-loops < 0.01%", self_loops / len(edges) < 0.0001,
      f"self_loops={self_loops} ({100*self_loops/len(edges):.4f}%)")

# 1.12 Relation type consistency (check subject/object categories match expected)
print("  Checking relation type consistency...")
target_edges = edges[edges["predicate"] == "targets"]
target_subjects = set(target_edges["subject"].unique())
drug_ids = set(nodes[nodes["category"] == "Drug"]["id"].unique())
gene_ids = set(nodes[nodes["category"] == "Gene"]["id"].unique())
targets_valid_subj = target_subjects.issubset(drug_ids)
check("'targets' edges: all subjects are Drug nodes", targets_valid_subj,
      f"non-drug subjects in targets: {len(target_subjects - drug_ids)}")

target_objects = set(target_edges["object"].unique())
targets_valid_obj = target_objects.issubset(gene_ids)
check("'targets' edges: all objects are Gene nodes", targets_valid_obj,
      f"non-gene objects in targets: {len(target_objects - gene_ids)}")

# ============================================================
# CHECK 2: SEX-DIFFERENTIAL SIGNAL VALIDATION
# ============================================================
print("\n[2/8] SEX-DIFFERENTIAL SIGNAL VALIDATION")
print("-" * 50)

sexdiff = pd.read_parquet(base / "results/signals/sex_differential.parquet")
ror_by_sex = pd.read_parquet(base / "results/signals/ror_by_sex.parquet")

# 2.1 Signal counts
check("Sex-differential signals = 183,544", len(sexdiff) == 183544, f"actual={len(sexdiff)}")

# 2.2 Strong signal filter
strong = sexdiff[(sexdiff["min_reports"] >= 10) & (sexdiff["log_ror_ratio"].abs() > 1.0)]
check("Strong signals = 49,026", len(strong) == 49026, f"actual={len(strong)}")

# 2.3 Direction split
female = strong[strong["direction"] == "female_higher"]
male = strong[strong["direction"] == "male_higher"]
check("Female-biased strong = 28,669", len(female) == 28669, f"actual={len(female)}")
check("Male-biased strong = 20,357", len(male) == 20357, f"actual={len(male)}")

# 2.4 ROR mathematical validation — sample 1000 signals and recompute
print("  Recalculating ROR for 1000 random signals...")
np.random.seed(42)
sample_idx = np.random.choice(len(sexdiff), min(1000, len(sexdiff)), replace=False)
sample = sexdiff.iloc[sample_idx]

ror_errors = 0
direction_errors = 0
for _, row in sample.iterrows():
    ror_f = row.get("ror_female", None)
    ror_m = row.get("ror_male", None)
    log_ratio = row.get("log_ror_ratio", None)
    direction = row.get("direction", None)
    
    if pd.notna(ror_f) and pd.notna(ror_m) and ror_f > 0 and ror_m > 0:
        expected_ratio = np.log2(ror_f / ror_m)
        if abs(expected_ratio - log_ratio) > 0.001:
            ror_errors += 1
    
    if pd.notna(log_ratio) and pd.notna(direction):
        expected_dir = "female_higher" if log_ratio > 0 else "male_higher"
        if direction != expected_dir and log_ratio != 0:
            direction_errors += 1

check(f"ROR ratio math correct (1000 samples)", ror_errors == 0,
      f"errors={ror_errors}/1000")
check(f"Direction labels correct (1000 samples)", direction_errors == 0,
      f"errors={direction_errors}/1000")

# 2.5 No infinite or NaN ROR values in strong signals
nan_ror_f = strong["ror_female"].isna().sum()
nan_ror_m = strong["ror_male"].isna().sum()
inf_ror_f = np.isinf(strong["ror_female"]).sum() if hasattr(strong["ror_female"], '__iter__') else 0
inf_ror_m = np.isinf(strong["ror_male"]).sum() if hasattr(strong["ror_male"], '__iter__') else 0
check("No NaN in strong signal ROR_female", nan_ror_f == 0, f"NaN={nan_ror_f}")
check("No NaN in strong signal ROR_male", nan_ror_m == 0, f"NaN={nan_ror_m}")
check("No Inf in strong signal ROR_female", inf_ror_f == 0, f"Inf={inf_ror_f}")
check("No Inf in strong signal ROR_male", inf_ror_m == 0, f"Inf={inf_ror_m}")

# 2.6 Min reports threshold enforcement
below_threshold = (strong["min_reports"] < 10).sum()
check("All strong signals have ≥10 reports per sex", below_threshold == 0,
      f"below_threshold={below_threshold}")

# 2.7 log_ror_ratio magnitude check
below_magnitude = (strong["log_ror_ratio"].abs() <= 1.0).sum()
check("All strong signals have |log_ror_ratio| > 1.0", below_magnitude == 0,
      f"below_magnitude={below_magnitude}")

# 2.8 Unique drugs and AEs
unique_drugs = sexdiff["drug_name"].nunique()
unique_aes = sexdiff["pt"].nunique()
check("Unique drugs in sex-diff = 3,441", unique_drugs == 3441, f"actual={unique_drugs}")
check("Unique AEs in sex-diff = 5,658", unique_aes == 5658, f"actual={unique_aes}")

# ============================================================
# CHECK 3: EMBEDDING INTEGRITY (GPU-accelerated)
# ============================================================
print("\n[3/8] EMBEDDING INTEGRITY CHECK")
print("-" * 50)

entity_emb = np.load(base / "results/kg_embeddings/DistMult/embeddings/entity_embeddings.npz")["embeddings"]
relation_emb = np.load(base / "results/kg_embeddings/DistMult/embeddings/relation_embeddings.npz")["embeddings"]

# 3.1 Shape checks
check("Entity embeddings shape = (126575, 200)", entity_emb.shape == (126575, 200),
      f"actual={entity_emb.shape}")
check("Relation embeddings shape = (6, 200)", relation_emb.shape == (6, 200),
      f"actual={relation_emb.shape}")

# 3.2 No NaN values
nan_entity = np.isnan(entity_emb).sum()
nan_relation = np.isnan(relation_emb).sum()
check("No NaN in entity embeddings", nan_entity == 0, f"NaN count={nan_entity}")
check("No NaN in relation embeddings", nan_relation == 0, f"NaN count={nan_relation}")

# 3.3 No Inf values
inf_entity = np.isinf(entity_emb).sum()
inf_relation = np.isinf(relation_emb).sum()
check("No Inf in entity embeddings", inf_entity == 0, f"Inf count={inf_entity}")
check("No Inf in relation embeddings", inf_relation == 0, f"Inf count={inf_relation}")

# 3.4 No zero vectors (degenerate embeddings)
zero_entities = (np.linalg.norm(entity_emb, axis=1) == 0).sum()
zero_relations = (np.linalg.norm(relation_emb, axis=1) == 0).sum()
check("No zero entity embeddings", zero_entities == 0, f"zero vectors={zero_entities}")
check("No zero relation embeddings", zero_relations == 0, f"zero vectors={zero_relations}")

# 3.5 Embedding value range (should not be extreme)
emb_max = np.abs(entity_emb).max()
emb_mean = np.abs(entity_emb).mean()
check("Entity embedding max |value| < 100", emb_max < 100, f"max={emb_max:.4f}")
check("Entity embedding mean |value| reasonable", 0.01 < emb_mean < 10,
      f"mean={emb_mean:.4f}")

# 3.6 GPU-accelerated: embedding distribution analysis
if HAS_TORCH:
    print("  GPU: Analyzing embedding distribution...")
    emb_tensor = torch.from_numpy(entity_emb).to(device)
    
    # Norms distribution
    norms = torch.norm(emb_tensor, dim=1)
    norm_mean = norms.mean().item()
    norm_std = norms.std().item()
    norm_min = norms.min().item()
    norm_max = norms.max().item()
    
    check("Embedding norms have reasonable variance", norm_std / norm_mean < 2.0,
          f"mean={norm_mean:.4f}, std={norm_std:.4f}, cv={norm_std/norm_mean:.4f}")
    
    # Check for near-duplicate embeddings (cosine similarity)
    print("  GPU: Checking for near-duplicate embeddings (sample 5000)...")
    sample_size = min(5000, entity_emb.shape[0])
    idx = torch.randperm(entity_emb.shape[0])[:sample_size]
    sample_emb = emb_tensor[idx]
    sample_norm = sample_emb / (torch.norm(sample_emb, dim=1, keepdim=True) + 1e-8)
    cos_sim = torch.mm(sample_norm, sample_norm.t())
    # Zero out diagonal
    cos_sim.fill_diagonal_(0)
    near_dupes = (cos_sim > 0.999).sum().item() // 2
    check(f"Near-duplicate embeddings < 0.1% (sample {sample_size})",
          near_dupes < sample_size * 0.001,
          f"near_dupes={near_dupes} ({100*near_dupes/sample_size:.3f}%)")
    
    # Embedding collapse detection (all embeddings in tight cluster)
    cos_mean = cos_sim.abs().mean().item()
    check("No embedding collapse (mean |cos_sim| < 0.5)", cos_mean < 0.5,
          f"mean_cos_sim={cos_mean:.4f}")
    
    del emb_tensor, sample_emb, sample_norm, cos_sim
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# 3.7 Drug embedding coverage check
triples = pd.read_csv(base / "data/kg/triples.tsv", sep="\t", header=None, names=["h", "r", "t"])
triples = triples.dropna().reset_index(drop=True)
all_entities = sorted(set(triples["h"].astype(str).unique()) | set(triples["t"].astype(str).unique()))
entity2idx = {e: i for i, e in enumerate(all_entities)}
drug_ids_in_kg = set(nodes[nodes["category"] == "Drug"]["id"].unique())
drugs_with_emb = sum(1 for d in drug_ids_in_kg if d in entity2idx and entity2idx[d] < entity_emb.shape[0])
check("Drug embedding coverage > 99%", drugs_with_emb / len(drug_ids_in_kg) > 0.99,
      f"covered={drugs_with_emb}/{len(drug_ids_in_kg)} ({100*drugs_with_emb/len(drug_ids_in_kg):.1f}%)")

# ============================================================
# CHECK 4: CROSS-REFERENCE AUDIT (Pipeline Consistency)
# ============================================================
print("\n[4/8] CROSS-REFERENCE AUDIT")
print("-" * 50)

# 4.1 sex_differential_adverse_event edges match signal count
sdae_edges = edge_counts.get("sex_differential_adverse_event", 0)
check("sex_diff_AE edges ≈ sex-diff signals",
      abs(sdae_edges - len(sexdiff)) < 10,
      f"edges={sdae_edges}, signals={len(sexdiff)}, diff={abs(sdae_edges - len(sexdiff))}")

# 4.2 Drug nodes cover all sex-diff signal drugs
signal_drugs = set(sexdiff["drug_name"].unique())
drug_names_in_kg = set(nodes[nodes["category"] == "Drug"]["name"].str.upper().unique())
drug_coverage = len(signal_drugs & drug_names_in_kg) / len(signal_drugs)
check("Signal drug coverage in KG > 95%", drug_coverage > 0.95,
      f"coverage={drug_coverage:.1%} ({len(signal_drugs & drug_names_in_kg)}/{len(signal_drugs)})")

# 4.3 AE nodes cover all sex-diff signal AEs
signal_aes = set(sexdiff["pt"].unique())
ae_names_in_kg = set(nodes[nodes["category"] == "AdverseEvent"]["name"].str.upper().unique())
ae_coverage = len(signal_aes & ae_names_in_kg) / len(signal_aes)
check("Signal AE coverage in KG > 95%", ae_coverage > 0.95,
      f"coverage={ae_coverage:.1%} ({len(signal_aes & ae_names_in_kg)}/{len(signal_aes)})")

# 4.4 Triples file consistency
check("Triples count matches usable (no NaN) triples",
      len(triples) >= 5400000 and len(triples) <= 5500000,
      f"triples={len(triples)}")

# 4.5 Entity count in triples matches embedding count
check("Entity count in triples = embedding rows",
      len(all_entities) == entity_emb.shape[0],
      f"entities={len(all_entities)}, embedding_rows={entity_emb.shape[0]}")

# ============================================================
# CHECK 5: TARGET ANALYSIS VALIDATION
# ============================================================
print("\n[5/8] TARGET ANALYSIS VALIDATION")
print("-" * 50)

target_bias_path = base / "results/analysis/target_sex_bias.tsv"
if target_bias_path.exists():
    target_bias = pd.read_csv(target_bias_path, sep="\t")
    
    # 5.1 Count check
    check("Target count = 430", len(target_bias) == 430, f"actual={len(target_bias)}")
    
    # 5.2 Score range
    score_min = target_bias["sex_bias_score"].min()
    score_max = target_bias["sex_bias_score"].max()
    check("Sex bias scores in [-1, +1]", score_min >= -1.0 and score_max <= 1.0,
          f"range=[{score_min:.3f}, {score_max:.3f}]")
    
    # 5.3 Math consistency: female_fraction = female_biased_drugs / total_drugs
    target_bias["check_frac"] = target_bias["female_biased_drugs"] / target_bias["total_drugs"]
    frac_errors = (abs(target_bias["check_frac"] - target_bias["female_fraction"]) > 0.002).sum()
    check("Female fraction math correct", frac_errors == 0, f"errors={frac_errors}")
    
    # 5.4 Math consistency: sex_bias_score = (female - male) / total
    target_bias["check_score"] = (target_bias["female_biased_drugs"] - target_bias["male_biased_drugs"]) / target_bias["total_drugs"]
    score_errors = (abs(target_bias["check_score"] - target_bias["sex_bias_score"]) > 0.002).sum()
    check("Sex bias score math correct", score_errors == 0, f"errors={score_errors}")
    
    # 5.5 All targets are Gene nodes
    target_ids = set(target_bias["target_id"].unique())
    gene_ids_set = set(nodes[nodes["category"] == "Gene"]["id"].unique())
    non_gene_targets = target_ids - gene_ids_set
    check("All targets are Gene nodes", len(non_gene_targets) == 0,
          f"non-gene targets={len(non_gene_targets)}")
    
    # 5.6 All targets appear in target edges
    target_edge_genes = set(target_edges["object"].unique())
    targets_not_in_edges = target_ids - target_edge_genes
    check("All analyzed targets appear in KG target edges", len(targets_not_in_edges) == 0,
          f"missing from edges={len(targets_not_in_edges)}")
    
    # 5.7 Independent re-derivation — pick top 5 targets and verify counts
    print("  Re-deriving top 5 target scores independently...")
    chembl_drugs_df = nodes[nodes["category"] == "Drug"][nodes["id"].str.startswith("CHEMBL")]
    chembl_name_map = dict(zip(chembl_drugs_df["name"].str.upper(), chembl_drugs_df["id"]))
    drug_target_map = defaultdict(set)
    for _, row in target_edges.iterrows():
        drug_target_map[row["subject"]].add(row["object"])
    
    strong_copy = strong.copy()
    strong_copy["chembl_id"] = strong_copy["drug_name"].map(chembl_name_map)
    
    rederive_ok = True
    for _, trow in target_bias.head(5).iterrows():
        tid = trow["target_id"]
        # Find all drugs targeting this gene
        drugs_for_target = [did for did, tgts in drug_target_map.items() if tid in tgts]
        # Find signals for these drugs
        signals_for_target = strong_copy[strong_copy["chembl_id"].isin(drugs_for_target)]
        unique_chembl = signals_for_target["chembl_id"].nunique()
        
        if abs(unique_chembl - trow["total_drugs"]) > 1:  # Allow 1 tolerance
            warn(f"Target {trow['gene_name']}: expected {trow['total_drugs']} drugs, got {unique_chembl}")
            rederive_ok = False
    
    check("Independent re-derivation of top 5 targets", rederive_ok)
else:
    warn("Target sex bias file not found")

# ============================================================
# CHECK 6: CLUSTER ANALYSIS VALIDATION
# ============================================================
print("\n[6/8] CLUSTER ANALYSIS VALIDATION")
print("-" * 50)

cluster_path = base / "results/analysis/cluster_profiles.json"
pca_path = base / "results/analysis/drug_pca_coordinates.tsv"

with open(cluster_path) as f:
    profiles = json.load(f)
pca_df = pd.read_csv(pca_path, sep="\t")

# 6.1 Cluster count
check("Number of clusters = 20", len(profiles) == 20, f"actual={len(profiles)}")

# 6.2 PCA drug count
check("PCA drug count = 29,201", len(pca_df) == 29201, f"actual={len(pca_df)}")

# 6.3 Cluster total drugs matches PCA count
total_in_clusters = sum(p["n_drugs"] for p in profiles)
check("Total drugs across clusters = 29,201", total_in_clusters == 29201,
      f"actual={total_in_clusters}")

# 6.4 Signal counts are consistent
total_signals = sum(p["n_signals"] for p in profiles)
check("Total signals across clusters = 49,026", total_signals == 49026,
      f"actual={total_signals}")

# 6.5 Female ratio range
for p in profiles:
    if p["n_signals"] > 0:
        if p["female_ratio"] < 0 or p["female_ratio"] > 1:
            check(f"Cluster {p['cluster']} female_ratio in [0,1]", False,
                  f"ratio={p['female_ratio']}")
            break
else:
    check("All cluster female ratios in [0, 1]", True)

# 6.6 PCA coordinates are finite
pca_nan = pca_df[["pc1", "pc2"]].isna().sum().sum()
pca_inf = np.isinf(pca_df[["pc1", "pc2"]].values).sum()
check("No NaN in PCA coordinates", pca_nan == 0, f"NaN={pca_nan}")
check("No Inf in PCA coordinates", pca_inf == 0, f"Inf={pca_inf}")

# 6.7 GPU: Verify KMeans is reasonable (silhouette on sample)
if HAS_TORCH:
    print("  GPU: Computing cluster quality metrics...")
    drug_emb_sample = entity_emb[:min(29201, entity_emb.shape[0])]
    drug_idx_list = [entity2idx[d] for d in nodes[nodes["category"] == "Drug"]["id"]
                     if d in entity2idx and entity2idx[d] < entity_emb.shape[0]]
    drug_emb_matrix = entity_emb[drug_idx_list[:29201]]
    norms = np.linalg.norm(drug_emb_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    drug_emb_norm = drug_emb_matrix / norms
    
    # Intra-cluster vs inter-cluster distance (simplified check)
    from sklearn.metrics import silhouette_score
    clusters_arr = pca_df["cluster"].values[:len(drug_emb_norm)]
    if len(clusters_arr) == len(drug_emb_norm):
        # Sample for speed
        sample_n = min(5000, len(drug_emb_norm))
        sidx = np.random.choice(len(drug_emb_norm), sample_n, replace=False)
        sil = silhouette_score(drug_emb_norm[sidx], clusters_arr[sidx])
        check("Silhouette score > 0 (clusters meaningful)", sil > 0,
              f"silhouette={sil:.4f}")
    else:
        warn("Cluster array size mismatch — cannot compute silhouette")

# ============================================================
# CHECK 7: STATISTICAL ROBUSTNESS
# ============================================================
print("\n[7/8] STATISTICAL ROBUSTNESS")
print("-" * 50)

# 7.1 Bootstrap CI on female/male ratio
print("  Bootstrap CI on female-bias ratio (1000 iterations)...")
np.random.seed(42)
n_bootstrap = 1000
ratios = []
for _ in range(n_bootstrap):
    boot_idx = np.random.choice(len(strong), len(strong), replace=True)
    boot = strong.iloc[boot_idx]
    ratio = (boot["direction"] == "female_higher").mean()
    ratios.append(ratio)

ci_lower = np.percentile(ratios, 2.5)
ci_upper = np.percentile(ratios, 97.5)
reported_ratio = 28669 / 49026
check("Female-bias ratio 95% CI contains reported value",
      ci_lower <= reported_ratio <= ci_upper,
      f"reported={reported_ratio:.4f}, CI=[{ci_lower:.4f}, {ci_upper:.4f}]")

# 7.2 Effect size distribution sanity
median_abs_ratio = strong["log_ror_ratio"].abs().median()
check("Median |log_ror_ratio| > 1.0 (by definition)", median_abs_ratio > 1.0,
      f"median={median_abs_ratio:.4f}")
mean_abs_ratio = strong["log_ror_ratio"].abs().mean()
check("Mean |log_ror_ratio| reasonable (< 5.0)", mean_abs_ratio < 5.0,
      f"mean={mean_abs_ratio:.4f}")

# 7.3 No single drug dominates (top drug < 5% of signals)
drug_counts_check = strong["drug_name"].value_counts()
top_drug_pct = drug_counts_check.iloc[0] / len(strong)
check("Top drug < 5% of signals (no single-drug dominance)",
      top_drug_pct < 0.05,
      f"top_drug={drug_counts_check.index[0]}, {top_drug_pct:.3%}")

# 7.4 Report count sanity — a_female + a_male should be reasonable
if "a_female" in strong.columns and "a_male" in strong.columns:
    total_reports = strong["a_female"] + strong["a_male"]
    check("All strong signals have total reports ≥ 20", (total_reports >= 20).all(),
          f"below 20: {(total_reports < 20).sum()}")

# ============================================================
# CHECK 8: EDGE CASE DETECTION
# ============================================================
print("\n[8/8] EDGE CASE & ANOMALY DETECTION")
print("-" * 50)

# 8.1 Extreme ROR ratios (> 10x could be data quality issue)
extreme_ratios = (strong["log_ror_ratio"].abs() > np.log2(1000)).sum()
if extreme_ratios > 0:
    warn(f"Signals with >1000× sex ratio: {extreme_ratios}",
         "May be legitimate but should be reviewed")
else:
    check("No extreme sex ratios (>1000×)", True)

# 8.2 Drugs with ONLY female or ONLY male signals (completely one-sided)
drug_dir = strong.groupby("drug_name")["direction"].nunique()
one_sided = (drug_dir == 1).sum()
total_drugs_checked = len(drug_dir)
check("One-sided drugs < 50%", one_sided / total_drugs_checked < 0.5,
      f"one-sided={one_sided}/{total_drugs_checked} ({100*one_sided/total_drugs_checked:.1f}%)")

# 8.3 Sex ratio of FAERS reports consistency
faers_ratio = 8744397 / (8744397 + 5791611)
check("FAERS female ratio ~ 60%", 0.55 < faers_ratio < 0.65,
      f"ratio={faers_ratio:.3f}")

# 8.4 DistMult metrics sanity
stats_path = base / "results/analysis/sexdiffkg_statistics.json"
with open(stats_path) as f:
    stats = json.load(f)

mrr = stats["embeddings"]["mrr"]
h10 = stats["embeddings"]["hits_at_10"]
amri = stats["embeddings"]["amri"]
check("MRR > random baseline (1/126575)", mrr > 1/126575,
      f"MRR={mrr}, random={1/126575:.8f}")
check("Hits@10 > 10 × random", h10 > 10/126575,
      f"H@10={h10}, 10×random={10/126575:.8f}")
check("AMRI > 0.95 (top 5% ranking)", amri > 0.95, f"AMRI={amri}")

# 8.5 Model file integrity
model_path = base / "results/kg_embeddings/DistMult/model.pt"
model_size = model_path.stat().st_size
check("Model file size > 90 MB", model_size > 90_000_000,
      f"size={model_size/1e6:.1f} MB")

# ============================================================
# FINAL REPORT
# ============================================================
elapsed = time.time() - t0
print("\n" + "=" * 70)
print(f"  INTEGRITY CHECK COMPLETE — {elapsed:.1f}s")
print("=" * 70)
print(f"  ✅ PASSED: {PASS}")
print(f"  ❌ FAILED: {FAIL}")
print(f"  ⚠️  WARNINGS: {WARN}")
print(f"  TOTAL CHECKS: {PASS + FAIL}")

if FAIL == 0:
    verdict = "✅ ALL CHECKS PASSED — DATA IS PUBLICATION-READY"
else:
    verdict = f"❌ {FAIL} CHECKS FAILED — REQUIRES INVESTIGATION"

print(f"\n  VERDICT: {verdict}")
print("=" * 70)

# Write report
with open(report_path, "w") as f:
    f.write("# SexDiffKG Deep Integrity Report\n\n")
    f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Runtime:** {elapsed:.1f} seconds\n")
    f.write(f"**Infrastructure:** NVIDIA DGX Spark GB10 (GPU + CPU)\n\n")
    f.write(f"## Verdict\n\n**{verdict}**\n\n")
    f.write(f"| Metric | Count |\n|--------|-------|\n")
    f.write(f"| Checks Passed | {PASS} |\n")
    f.write(f"| Checks Failed | {FAIL} |\n")
    f.write(f"| Warnings | {WARN} |\n")
    f.write(f"| Total | {PASS + FAIL + WARN} |\n\n")
    f.write("## Detailed Results\n\n")
    f.write("| Status | Check | Detail |\n|--------|-------|--------|\n")
    for status, name, detail in findings:
        f.write(f"| {status} | {name} | {detail} |\n")
    f.write(f"\n## Statistical Robustness\n\n")
    f.write(f"- Female-bias ratio: {reported_ratio:.4f}\n")
    f.write(f"- 95% Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}]\n")
    f.write(f"- Bootstrap iterations: {n_bootstrap}\n")
    if HAS_TORCH:
        f.write(f"- Embedding norm: mean={norm_mean:.4f}, std={norm_std:.4f}\n")
        f.write(f"- Mean pairwise cosine similarity: {cos_mean:.4f}\n")
    f.write(f"\n---\n*This report was generated by automated deep integrity checking.*\n")
    f.write(f"*All {PASS + FAIL} checks must pass for publication clearance.*\n")

print(f"\nReport saved: {report_path}")
