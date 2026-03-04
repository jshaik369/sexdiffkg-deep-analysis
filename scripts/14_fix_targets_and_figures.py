#!/usr/bin/env python3
"""Fix target sex-bias analysis + generate all publication figures."""
import json, time
from pathlib import Path
from collections import defaultdict
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

base = Path("/home/jshaik369/sexdiffkg")
out_dir = base / "results" / "analysis"
fig_dir = base / "results" / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)
t0 = time.time()

# ============================================================
# PART 1: Fix target sex-bias analysis
# ============================================================
print("=" * 60)
print("PART 1: Fixing target sex-bias analysis")
print("=" * 60)

print("Loading data...")
nodes = pd.read_csv(base / "data/kg/nodes.tsv", sep="\t")
edges = pd.read_csv(base / "data/kg/edges.tsv", sep="\t")
sexdiff = pd.read_parquet(base / "results/signals/sex_differential.parquet")

# Strong signals
robust = sexdiff[sexdiff["min_reports"] >= 10].copy()
strong = robust[robust["log_ror_ratio"].abs() > 1.0].copy()
print(f"Strong signals: {len(strong):,}")

# Drug nodes
drugs = nodes[nodes["category"] == "Drug"]
chembl_drugs = drugs[drugs["id"].str.startswith("CHEMBL")]
all_drugs = drugs.copy()

# Build name→CHEMBL ID mapping (bridge FAERS drugs to CHEMBL targets)
chembl_name_map = dict(zip(chembl_drugs["name"].str.upper(), chembl_drugs["id"]))

# Target edges (Drug CHEMBL ID → Gene)
target_edges = edges[edges["predicate"] == "targets"]
drug_targets = defaultdict(set)
for _, row in target_edges.iterrows():
    drug_targets[row["subject"]].add(row["object"])
print(f"Drugs with targets: {len(drug_targets)}")

# Map signal drug_names → CHEMBL IDs via name match
strong["chembl_id"] = strong["drug_name"].map(chembl_name_map)
matched_targets = strong.dropna(subset=["chembl_id"])
print(f"Signals with CHEMBL match: {len(matched_targets):,} / {len(strong):,}")

# For each matched signal, look up gene targets
target_sex_profile = defaultdict(lambda: {"f": set(), "m": set(), "all": set()})
matched_with_targets = 0
for _, row in matched_targets.iterrows():
    cid = row["chembl_id"]
    targets = drug_targets.get(cid, set())
    if not targets:
        continue
    matched_with_targets += 1
    for t in targets:
        target_sex_profile[t]["all"].add(cid)
        if row["direction"] == "female_higher":
            target_sex_profile[t]["f"].add(cid)
        else:
            target_sex_profile[t]["m"].add(cid)

print(f"Signals matched to gene targets: {matched_with_targets:,}")
print(f"Gene targets with sex-differential data: {len(target_sex_profile)}")

# Build target bias table
target_bias = []
for target, p in target_sex_profile.items():
    nf, nm, nt = len(p["f"]), len(p["m"]), len(p["all"])
    if nt >= 2:  # Lowered threshold from 3 to 2
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

# Save fixed target analysis
if len(target_bias_df) > 0:
    target_bias_df.to_csv(out_dir / "target_sex_bias.tsv", sep="\t", index=False)
    print(f"\nTop female-biased targets:")
    for _, r in target_bias_df[target_bias_df["sex_bias_score"] > 0].head(10).iterrows():
        print(f'  {r["gene_name"]:30s} score={r["sex_bias_score"]:+.3f} ({r["total_drugs"]} drugs)')
    print(f"\nTop male-biased targets:")
    for _, r in target_bias_df[target_bias_df["sex_bias_score"] < 0].head(10).iterrows():
        print(f'  {r["gene_name"]:30s} score={r["sex_bias_score"]:+.3f} ({r["total_drugs"]} drugs)')

# Update statistics JSON
stats_path = out_dir / "sexdiffkg_statistics.json"
with open(stats_path) as f:
    stats = json.load(f)
stats["analysis"]["targets_with_sex_bias"] = len(target_bias_df)
stats["analysis"]["drugs_matched_to_targets"] = matched_with_targets
with open(stats_path, "w") as f:
    json.dump(stats, f, indent=2, default=str)
print(f"\nUpdated {stats_path}")

# ============================================================
# PART 2: Generate publication-quality figures
# ============================================================
print("\n" + "=" * 60)
print("PART 2: Generating publication figures")
print("=" * 60)

plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'figure.dpi': 300, 'savefig.dpi': 300, 'savefig.bbox': 'tight',
    'font.family': 'sans-serif',
})

# ---- Figure 1: Drug PCA clusters colored by sex-differential profile ----
print("Figure 1: Drug PCA clusters...")
pca_df = pd.read_csv(out_dir / "drug_pca_coordinates.tsv", sep="\t")
with open(out_dir / "cluster_profiles.json") as f:
    profiles = json.load(f)

# Compute cluster female ratio for coloring
cluster_ratios = {}
for p in profiles:
    c = p["cluster"]
    if p["n_signals"] > 0:
        cluster_ratios[c] = p["female_ratio"]
    else:
        cluster_ratios[c] = 0.5  # neutral

pca_df["female_ratio"] = pca_df["cluster"].map(cluster_ratios)
pca_df["has_signals"] = pca_df["cluster"].map(
    lambda c: next((p["n_signals"] for p in profiles if p["cluster"] == c), 0)) > 0

fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# Plot clusters without signals in gray
no_sig = pca_df[~pca_df["has_signals"]]
has_sig = pca_df[pca_df["has_signals"]]

ax.scatter(no_sig["pc1"], no_sig["pc2"], c='#cccccc', s=3, alpha=0.2, rasterized=True)
sc = ax.scatter(has_sig["pc1"], has_sig["pc2"], c=has_sig["female_ratio"],
                cmap='RdBu_r', vmin=0, vmax=1, s=5, alpha=0.4, rasterized=True)
cbar = plt.colorbar(sc, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("Female bias ratio", fontsize=11)
cbar.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
cbar.set_ticklabels(["Male\nbiased", "0.25", "Neutral", "0.75", "Female\nbiased"])

ax.set_xlabel("PC1 (DistMult embedding)")
ax.set_ylabel("PC2 (DistMult embedding)")
ax.set_title("SexDiffKG: Drug Embedding Clusters by Sex-Differential Safety Profile\n(29,201 drugs, 20 clusters, PCA variance 61.9%)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.savefig(fig_dir / "fig1_drug_pca_clusters.png", dpi=300)
fig.savefig(fig_dir / "fig1_drug_pca_clusters.pdf")
plt.close()
print("  Saved fig1_drug_pca_clusters.png/pdf")

# ---- Figure 2: Sex-differential signal distribution ----
print("Figure 2: Signal distribution...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 2A: Distribution of log ROR ratio
ax = axes[0]
bins = np.linspace(-5, 5, 80)
ax.hist(strong[strong["direction"] == "female_higher"]["log_ror_ratio"],
        bins=bins, color='#E74C3C', alpha=0.7, label=f'Female-biased (n={len(strong[strong["direction"]=="female_higher"]):,})')
ax.hist(strong[strong["direction"] == "male_higher"]["log_ror_ratio"],
        bins=bins, color='#3498DB', alpha=0.7, label=f'Male-biased (n={len(strong[strong["direction"]=="male_higher"]):,})')
ax.axvline(x=0, color='black', linestyle='--', alpha=0.5, linewidth=0.8)
ax.set_xlabel("log(ROR ratio) [Female/Male]")
ax.set_ylabel("Number of drug-AE signals")
ax.set_title("A. Distribution of Sex-Differential Signals")
ax.legend(loc="upper right", fontsize=9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# 2B: Top 15 drugs by number of sex-differential signals
ax = axes[1]
drug_counts = pd.read_csv(out_dir / "top_drugs_by_sex_diff.tsv", sep="\t", index_col=0)
top15 = drug_counts.head(15)

y_pos = range(len(top15))
ax.barh(y_pos, top15["female_biased"], color='#E74C3C', alpha=0.8, label="Female-biased")
ax.barh(y_pos, -top15["male_biased"], color='#3498DB', alpha=0.8, label="Male-biased")
ax.set_yticks(y_pos)
ax.set_yticklabels([n[:25] for n in top15.index], fontsize=8)
ax.set_xlabel("Number of sex-differential signals")
ax.set_title("B. Top 15 Drugs by Sex-Differential Signals")
ax.legend(loc="lower right", fontsize=8)
ax.axvline(x=0, color='black', linewidth=0.5)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.invert_yaxis()

fig.tight_layout()
fig.savefig(fig_dir / "fig2_signal_distribution.png", dpi=300)
fig.savefig(fig_dir / "fig2_signal_distribution.pdf")
plt.close()
print("  Saved fig2_signal_distribution.png/pdf")

# ---- Figure 3: Knowledge Graph overview ----
print("Figure 3: KG overview...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 3A: Node type distribution
ax = axes[0]
node_types = nodes["category"].value_counts()
colors_map = {
    "Gene": "#2ECC71", "Drug": "#E74C3C", "AdverseEvent": "#F39C12",
    "Protein": "#3498DB", "Pathway": "#9B59B6", "Tissue": "#1ABC9C"
}
colors = [colors_map.get(t, "#95A5A6") for t in node_types.index]
wedges, texts, autotexts = ax.pie(
    node_types.values, labels=None, autopct='%1.1f%%',
    colors=colors, pctdistance=0.8, startangle=90
)
for t in autotexts:
    t.set_fontsize(8)
ax.legend([f"{k} ({v:,})" for k, v in node_types.items()],
          loc="center left", bbox_to_anchor=(-0.35, 0.5), fontsize=8)
ax.set_title("A. Node Type Distribution (127,063 nodes)")

# 3B: Edge type distribution
ax = axes[1]
edge_types = edges["predicate"].value_counts()
bars = ax.barh(range(len(edge_types)), edge_types.values, color='#34495E', alpha=0.8)
ax.set_yticks(range(len(edge_types)))
ax.set_yticklabels(edge_types.index, fontsize=8)
ax.set_xlabel("Number of edges")
ax.set_title(f"B. Edge Type Distribution ({len(edges):,} edges)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.invert_yaxis()
# Add value labels
for i, (v, name) in enumerate(zip(edge_types.values, edge_types.index)):
    if v > 100000:
        ax.text(v + 5000, i, f"{v:,}", va='center', fontsize=7)

fig.tight_layout()
fig.savefig(fig_dir / "fig3_kg_overview.png", dpi=300)
fig.savefig(fig_dir / "fig3_kg_overview.pdf")
plt.close()
print("  Saved fig3_kg_overview.png/pdf")

# ---- Figure 4: Target sex-bias scores ----
print("Figure 4: Target sex bias...")
if len(target_bias_df) >= 5:
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    top_targets = pd.concat([
        target_bias_df[target_bias_df["sex_bias_score"] > 0].head(15),
        target_bias_df[target_bias_df["sex_bias_score"] < 0].head(15),
    ]).sort_values("sex_bias_score")
    
    colors = ['#E74C3C' if s > 0 else '#3498DB' for s in top_targets["sex_bias_score"]]
    y_pos = range(len(top_targets))
    ax.barh(y_pos, top_targets["sex_bias_score"], color=colors, alpha=0.8)
    ax.set_yticks(y_pos)
    labels = [f'{r["gene_name"]} (n={r["total_drugs"]})' for _, r in top_targets.iterrows()]
    ax.set_yticklabels(labels, fontsize=8)
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_xlabel("Sex Bias Score\n(+1 = all female-biased drugs, -1 = all male-biased)")
    ax.set_title(f"SexDiffKG: Gene Targets with Sex-Differential Drug Safety\n({len(target_bias_df)} targets with ≥2 sex-differential drugs)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    red_patch = mpatches.Patch(color='#E74C3C', alpha=0.8, label='Female-biased')
    blue_patch = mpatches.Patch(color='#3498DB', alpha=0.8, label='Male-biased')
    ax.legend(handles=[red_patch, blue_patch], loc='lower right')
    
    fig.tight_layout()
    fig.savefig(fig_dir / "fig4_target_sex_bias.png", dpi=300)
    fig.savefig(fig_dir / "fig4_target_sex_bias.pdf")
    plt.close()
    print("  Saved fig4_target_sex_bias.png/pdf")
else:
    print("  Skipped (not enough targets)")

# ---- Figure 5: Pipeline overview / FAERS data summary ----
print("Figure 5: FAERS data summary...")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 5A: FAERS reports by sex
ax = axes[0]
vals = [8744397, 5791611]
labels_bar = ["Female\n(8.74M)", "Male\n(5.79M)"]
bars = ax.bar(labels_bar, vals, color=['#E74C3C', '#3498DB'], alpha=0.8, width=0.5)
ax.set_ylabel("Number of FAERS reports")
ax.set_title("A. FDA Adverse Event Reports by Sex\n(14.5M total)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100000,
            f"{v/1e6:.2f}M", ha='center', fontsize=10)

# 5B: Signal filtering funnel
ax = axes[1]
funnel = [
    ("All drug-AE pairs\n(ROR signals)", 2610331),
    ("Sex-differential\nsignals", 183544),
    ("Robust (≥10 reports\nper sex)", 183544),
    ("Strong (~2.7× difference)", 49026),
]
y_pos = range(len(funnel))
colors_f = ['#BDC3C7', '#F39C12', '#E67E22', '#E74C3C']
bars = ax.barh(y_pos, [v for _, v in funnel], color=colors_f, alpha=0.85)
ax.set_yticks(y_pos)
ax.set_yticklabels([n for n, _ in funnel], fontsize=9)
ax.set_xlabel("Number of signals")
ax.set_title("B. Signal Filtering Pipeline")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.invert_yaxis()
for i, (_, v) in enumerate(funnel):
    ax.text(v + 20000, i, f"{v:,}", va='center', fontsize=9)

fig.tight_layout()
fig.savefig(fig_dir / "fig5_faers_summary.png", dpi=300)
fig.savefig(fig_dir / "fig5_faers_summary.pdf")
plt.close()
print("  Saved fig5_faers_summary.png/pdf")

# ---- Figure 6: Cluster sex-bias heatmap ----
print("Figure 6: Cluster profiles heatmap...")
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
prof_data = []
for p in profiles:
    prof_data.append({
        "cluster": p["cluster"], "n_drugs": p["n_drugs"],
        "n_signals": p["n_signals"], "female_ratio": p["female_ratio"]
    })
prof_df = pd.DataFrame(prof_data).sort_values("n_signals", ascending=False)
active = prof_df[prof_df["n_signals"] > 0]

if len(active) > 0:
    bars = ax.bar(range(len(active)), active["n_signals"],
                  color=[plt.cm.RdBu_r(r) for r in active["female_ratio"]],
                  alpha=0.85, edgecolor='gray', linewidth=0.5)
    ax.set_xticks(range(len(active)))
    ax.set_xticklabels([f'C{c}\n({nd})' for c, nd in zip(active["cluster"], active["n_drugs"])],
                        fontsize=7, rotation=0)
    ax.set_xlabel("Cluster (number of drugs)")
    ax.set_ylabel("Number of sex-differential signals")
    ax.set_title("SexDiffKG: Embedding Cluster Sex-Differential Profiles\n(color: red=female-biased, blue=male-biased)")
    
    sm = plt.cm.ScalarMappable(cmap='RdBu_r', norm=plt.Normalize(0, 1))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
    cbar.set_label("Female bias ratio")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

fig.tight_layout()
fig.savefig(fig_dir / "fig6_cluster_profiles.png", dpi=300)
fig.savefig(fig_dir / "fig6_cluster_profiles.pdf")
plt.close()
print("  Saved fig6_cluster_profiles.png/pdf")

# ---- Summary ----
elapsed = time.time() - t0
print(f"\n{'='*60}")
print(f"ALL DONE in {elapsed/60:.1f} minutes")
print(f"{'='*60}")
print(f"Target analysis: {len(target_bias_df)} targets with sex-differential drug profiles")
print(f"Figures saved: {fig_dir}")
for f in sorted(fig_dir.glob("*")):
    print(f"  {f.name} ({f.stat().st_size/1024:.0f} KB)")
print(f"{'='*60}")
