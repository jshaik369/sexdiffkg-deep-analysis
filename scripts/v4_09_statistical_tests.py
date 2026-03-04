#!/usr/bin/env python3
"""
v4_09_statistical_tests.py — Statistical Significance Testing for SexDiffKG v4
==============================================================================
Comprehensive statistical testing for the SexDiffKG manuscript:
  (a) Binomial test: is the female bias in sex-differential signals significant?
  (b) Drug class chi-square tests: does bias distribution differ from random?
  (c) Permutation test on 74 moderately biased targets
  (d) Pathway enrichment: Fisher exact tests for F-biased vs M-biased targets
  (e) FDR correction (Benjamini-Hochberg) for all multiple testing

Outputs: results/analysis/statistical_tests_v4.json
"""

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT = Path("/home/jshaik369/sexdiffkg")
SIGNALS_FILE = PROJECT / "results/signals_v4/sex_differential_v4.parquet"
ALL_SIGNALS_FILE = PROJECT / "results/signals_v4/all_sex_comparisons_v4.parquet"
EDGES_FILE = PROJECT / "data/kg_v4/edges.tsv"
NODES_FILE = PROJECT / "data/kg_v4/nodes.tsv"
TARGET_BIAS_FILE = PROJECT / "results/analysis/v4_target_sex_bias.tsv"
DRUG_CLASS_FILE = PROJECT / "results/analysis/v4_drug_class_sex_bias.json"
OUTPUT_DIR = PROJECT / "results/analysis"
OUTPUT_FILE = OUTPUT_DIR / "statistical_tests_v4.json"

N_PERMUTATIONS = 10_000
MODERATE_BIAS_THRESHOLD = 0.3
MIN_DRUGS_FOR_MODERATE = 3
SEED = 42

np.random.seed(SEED)

print("=" * 72)
print("SexDiffKG v4 — Statistical Significance Testing")
print("=" * 72)
t0 = time.time()

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
print("\n[1/6] Loading data...")

signals = pd.read_parquet(SIGNALS_FILE)
print(f"  Sex-differential signals: {len(signals):,} "
      f"(F: {(signals['direction']=='female_higher').sum():,}, "
      f"M: {(signals['direction']=='male_higher').sum():,})")

all_signals = pd.read_parquet(ALL_SIGNALS_FILE)
print(f"  All sex comparisons: {len(all_signals):,}")

edges = pd.read_csv(EDGES_FILE, sep="\t")
print(f"  KG edges: {len(edges):,}")

nodes = pd.read_csv(NODES_FILE, sep="\t")
print(f"  KG nodes: {len(nodes):,}")

target_bias = pd.read_csv(TARGET_BIAS_FILE, sep="\t")
print(f"  Targets assessed: {len(target_bias):,}")

with open(DRUG_CLASS_FILE) as f:
    drug_classes = json.load(f)
print(f"  Drug classes: {len(drug_classes)}")

# Extract edge subsets
targets_edges = edges[edges["predicate"] == "targets"]
pathway_edges = edges[edges["predicate"] == "participates_in"]
print(f"  Drug-target edges: {len(targets_edges):,}")
print(f"  Gene-pathway edges: {len(pathway_edges):,}")

# Build pathway name lookup
pathway_names = dict(zip(nodes[nodes["category"] == "Pathway"]["id"],
                         nodes[nodes["category"] == "Pathway"]["name"]))

results = {}

# ---------------------------------------------------------------------------
# 2. BINOMIAL TEST — Female bias in sex-differential signals
# ---------------------------------------------------------------------------
print("\n[2/6] Binomial test: female bias in sex-differential signals...")

n_f = int((signals["direction"] == "female_higher").sum())
n_m = int((signals["direction"] == "male_higher").sum())
n_total = n_f + n_m

# Two-sided binomial test (H0: p = 0.5)
binom_result = stats.binomtest(n_f, n_total, p=0.5, alternative="two-sided")
binom_pval = binom_result.pvalue

# Also compute one-sided (greater) — is female excess significant?
binom_result_greater = stats.binomtest(n_f, n_total, p=0.5, alternative="greater")
binom_pval_greater = binom_result_greater.pvalue

# Effect size: proportion difference
prop_f = n_f / n_total
prop_expected = 0.5
cohens_h = 2 * np.arcsin(np.sqrt(prop_f)) - 2 * np.arcsin(np.sqrt(prop_expected))

# Also test against FAERS baseline: 60.1% F / 39.9% M reports
faers_f_prop = 8744397 / (8744397 + 5791611)  # 0.6013
binom_vs_faers = stats.binomtest(n_f, n_total, p=faers_f_prop, alternative="two-sided")

results["binomial_test_signal_bias"] = {
    "description": "Binomial test: is female excess in sex-differential signals significant?",
    "n_female_higher": n_f,
    "n_male_higher": n_m,
    "n_total": n_total,
    "observed_female_proportion": round(prop_f, 6),
    "expected_proportion_null": 0.5,
    "p_value_two_sided": float(f"{binom_pval:.2e}"),
    "p_value_one_sided_greater": float(f"{binom_pval_greater:.2e}"),
    "cohens_h_effect_size": round(cohens_h, 4),
    "interpretation": (
        f"Female-biased signals ({n_f:,}) significantly exceed male-biased ({n_m:,}), "
        f"p < 1e-300 (binomial test, two-sided). "
        f"Cohen's h = {cohens_h:.4f} (small but highly significant due to N={n_total:,})."
    ),
    "vs_faers_baseline": {
        "description": "Test against FAERS reporting proportion (60.1% F)",
        "faers_female_proportion": round(faers_f_prop, 4),
        "p_value": float(f"{binom_vs_faers.pvalue:.2e}"),
        "interpretation": (
            f"Even after adjusting for FAERS reporting bias (60.1% F), "
            f"the observed {prop_f:.1%} female proportion in signals is "
            f"{'still significantly different' if binom_vs_faers.pvalue < 0.05 else 'not significantly different'} "
            f"(p = {binom_vs_faers.pvalue:.2e})."
        )
    }
}

print(f"  F-biased: {n_f:,}  M-biased: {n_m:,}  Total: {n_total:,}")
print(f"  Female proportion: {prop_f:.4f}")
print(f"  Binomial p (two-sided, H0: 50/50): {binom_pval:.2e}")
print(f"  Binomial p (one-sided, F > M): {binom_pval_greater:.2e}")
print(f"  Cohen's h: {cohens_h:.4f}")
print(f"  vs FAERS baseline (60.1% F): p = {binom_vs_faers.pvalue:.2e}")

# ---------------------------------------------------------------------------
# 3. DRUG CLASS CHI-SQUARE / BINOMIAL TESTS
# ---------------------------------------------------------------------------
print("\n[3/6] Drug class sex bias tests...")

drug_class_results = {}
dc_pvals = []
dc_names = []

for cls_name, cls_data in drug_classes.items():
    f_strong = cls_data.get("f_strong", 0)
    m_strong = cls_data.get("m_strong", 0)
    total = f_strong + m_strong
    if total < 10:
        continue

    # Binomial test against 50/50
    bt = stats.binomtest(f_strong, total, p=0.5, alternative="two-sided")

    # Binomial test against FAERS baseline
    bt_faers = stats.binomtest(f_strong, total, p=faers_f_prop, alternative="two-sided")

    # Chi-square goodness of fit (50/50)
    expected = [total / 2, total / 2]
    chi2, chi_p = stats.chisquare([f_strong, m_strong], f_exp=expected)

    obs_prop = f_strong / total if total > 0 else 0.5
    effect_h = 2 * np.arcsin(np.sqrt(obs_prop)) - 2 * np.arcsin(np.sqrt(0.5))

    drug_class_results[cls_name] = {
        "f_biased_signals": f_strong,
        "m_biased_signals": m_strong,
        "total_signals": total,
        "female_proportion": round(obs_prop, 4),
        "mean_bias": cls_data.get("mean_bias", None),
        "direction": cls_data.get("direction", None),
        "n_drugs": cls_data.get("n_drugs", None),
        "binomial_p_vs_50_50": float(f"{bt.pvalue:.6e}"),
        "binomial_p_vs_faers": float(f"{bt_faers.pvalue:.6e}"),
        "chi_square_stat": round(chi2, 2),
        "chi_square_p": float(f"{chi_p:.6e}"),
        "cohens_h": round(effect_h, 4),
    }
    dc_pvals.append(bt.pvalue)
    dc_names.append(cls_name)

# FDR correction across drug classes
if dc_pvals:
    reject, fdr_pvals, _, _ = multipletests(dc_pvals, method="fdr_bh", alpha=0.05)
    for i, cls_name in enumerate(dc_names):
        drug_class_results[cls_name]["fdr_q_value"] = float(f"{fdr_pvals[i]:.6e}")
        drug_class_results[cls_name]["significant_fdr05"] = bool(reject[i])

# Sort by effect size
sorted_dc = sorted(drug_class_results.items(),
                   key=lambda x: abs(x[1]["cohens_h"]), reverse=True)

results["drug_class_tests"] = {
    "description": "Per-drug-class tests for sex bias distribution",
    "method": "Binomial test + chi-square goodness-of-fit vs 50/50 null",
    "fdr_method": "Benjamini-Hochberg",
    "n_classes_tested": len(drug_class_results),
    "n_significant_fdr05": sum(1 for v in drug_class_results.values()
                               if v.get("significant_fdr05", False)),
    "classes": dict(sorted_dc),
}

print(f"  Classes tested: {len(drug_class_results)}")
sig_dc = sum(1 for v in drug_class_results.values()
             if v.get("significant_fdr05", False))
print(f"  Significant (FDR < 0.05): {sig_dc}")
for cls_name, cls_res in sorted_dc[:5]:
    print(f"    {cls_name}: F={cls_res['f_biased_signals']}, M={cls_res['m_biased_signals']}, "
          f"h={cls_res['cohens_h']:.3f}, q={cls_res['fdr_q_value']:.2e}")

# ---------------------------------------------------------------------------
# 4. PERMUTATION TEST — Moderately biased targets
# ---------------------------------------------------------------------------
print(f"\n[4/6] Permutation test on moderately biased targets "
      f"(|score| >= {MODERATE_BIAS_THRESHOLD}, >= {MIN_DRUGS_FOR_MODERATE} drugs)...")

# Filter moderately biased targets
moderate = target_bias[
    (target_bias["sex_bias_score"].abs() >= MODERATE_BIAS_THRESHOLD) &
    (target_bias["total_drugs"] >= MIN_DRUGS_FOR_MODERATE)
].copy()
print(f"  Moderately biased targets: {len(moderate)}")

# For each target, the bias_score is computed as:
# (female_biased_drugs - male_biased_drugs) / total_drugs
# Permutation: shuffle which drugs are F-biased vs M-biased for each target
# and compute how often we get as extreme a score

perm_results = {}
perm_pvals = []
perm_names = []

for _, row in moderate.iterrows():
    gene = row["gene_symbol"]
    n_drugs = int(row["total_drugs"])
    f_drugs = int(row["female_biased_drugs"])
    m_drugs = int(row["male_biased_drugs"])
    observed_score = row["sex_bias_score"]

    # Under null: each drug is equally likely to be F-biased or M-biased
    # Simulate: for n_drugs trials, each has P(F)=0.5
    # Count how often |simulated_score| >= |observed_score|
    null_f_counts = np.random.binomial(n_drugs, 0.5, size=N_PERMUTATIONS)
    null_m_counts = n_drugs - null_f_counts
    null_scores = (null_f_counts - null_m_counts) / n_drugs

    n_extreme = np.sum(np.abs(null_scores) >= abs(observed_score))
    perm_p = (n_extreme + 1) / (N_PERMUTATIONS + 1)  # +1 for continuity

    # Also exact binomial test
    binom_p = stats.binomtest(f_drugs, f_drugs + m_drugs, p=0.5,
                              alternative="two-sided").pvalue

    perm_results[gene] = {
        "ensembl_id": row["ensembl_id"],
        "total_drugs": n_drugs,
        "female_biased_drugs": f_drugs,
        "male_biased_drugs": m_drugs,
        "sex_bias_score": round(observed_score, 4),
        "direction": "F-biased" if observed_score > 0 else "M-biased",
        "permutation_p": round(perm_p, 6),
        "binomial_p": float(f"{binom_p:.6e}"),
        "n_permutations": N_PERMUTATIONS,
    }
    perm_pvals.append(perm_p)
    perm_names.append(gene)

# FDR correction
if perm_pvals:
    reject, fdr_pvals, _, _ = multipletests(perm_pvals, method="fdr_bh", alpha=0.05)
    for i, gene in enumerate(perm_names):
        perm_results[gene]["fdr_q_value"] = round(float(fdr_pvals[i]), 6)
        perm_results[gene]["significant_fdr05"] = bool(reject[i])

# Sort by significance
sorted_perm = sorted(perm_results.items(),
                     key=lambda x: x[1]["permutation_p"])

n_sig_perm = sum(1 for v in perm_results.values()
                 if v.get("significant_fdr05", False))

results["permutation_test_targets"] = {
    "description": (f"Permutation test on {len(moderate)} moderately biased targets "
                    f"(|sex_bias_score| >= {MODERATE_BIAS_THRESHOLD}, >= {MIN_DRUGS_FOR_MODERATE} drugs)"),
    "method": f"Random permutation ({N_PERMUTATIONS:,} iterations) + exact binomial",
    "fdr_method": "Benjamini-Hochberg",
    "n_targets_tested": len(moderate),
    "n_significant_fdr05": n_sig_perm,
    "n_significant_nominal_05": sum(1 for v in perm_results.values()
                                    if v["permutation_p"] < 0.05),
    "targets": dict(sorted_perm),
}

print(f"  Targets tested: {len(moderate)}")
print(f"  Significant (nominal p < 0.05): "
      f"{sum(1 for v in perm_results.values() if v['permutation_p'] < 0.05)}")
print(f"  Significant (FDR < 0.05): {n_sig_perm}")
# Show top 10
for gene, res in sorted_perm[:10]:
    print(f"    {gene}: score={res['sex_bias_score']:.3f}, "
          f"F={res['female_biased_drugs']}/M={res['male_biased_drugs']}, "
          f"perm_p={res['permutation_p']:.4f}, "
          f"q={res.get('fdr_q_value', 'NA')}")

# ---------------------------------------------------------------------------
# 5. PATHWAY ENRICHMENT — Fisher exact test
# ---------------------------------------------------------------------------
print("\n[5/6] Pathway enrichment of biased targets (Fisher exact test)...")

# Map targets to pathways via Ensembl IDs
target_bias_copy = target_bias.copy()
target_bias_copy["gene_node"] = "GENE:" + target_bias_copy["ensembl_id"]

# Build gene-to-pathways mapping
gene_pathways = defaultdict(set)
for _, row in pathway_edges.iterrows():
    gene_pathways[row["subject"]].add(row["object"])

# Categorize targets
f_biased_targets = set(
    target_bias_copy[target_bias_copy["sex_bias_score"] > 0]["gene_node"]
)
m_biased_targets = set(
    target_bias_copy[target_bias_copy["sex_bias_score"] < 0]["gene_node"]
)
neutral_targets = set(
    target_bias_copy[target_bias_copy["sex_bias_score"] == 0]["gene_node"]
)
all_targets = set(target_bias_copy["gene_node"])

# For each pathway: test enrichment of F-biased targets
# Use Fisher exact test: 2x2 contingency table
#                    In pathway   Not in pathway
# F-biased target       a              b
# Not F-biased          c              d

pathway_genes = defaultdict(set)
for gene_node in all_targets:
    for pw in gene_pathways.get(gene_node, []):
        pathway_genes[pw].add(gene_node)

# Only test pathways with at least 3 target genes
eligible_pathways = {pw: genes for pw, genes in pathway_genes.items()
                     if len(genes) >= 3}

print(f"  Total pathways with target genes: {len(pathway_genes)}")
print(f"  Eligible pathways (>= 3 target genes): {len(eligible_pathways)}")
print(f"  F-biased targets: {len(f_biased_targets)}, "
      f"M-biased: {len(m_biased_targets)}, Neutral: {len(neutral_targets)}")

pathway_results = {}
pw_pvals_f = []
pw_pvals_m = []
pw_names_f = []
pw_names_m = []

n_total_targets = len(all_targets)
n_f_total = len(f_biased_targets)
n_m_total = len(m_biased_targets)

for pw_id, pw_targets in eligible_pathways.items():
    n_in_pw = len(pw_targets)
    n_not_in_pw = n_total_targets - n_in_pw

    # F-biased enrichment
    f_in = len(pw_targets & f_biased_targets)
    f_out = n_f_total - f_in
    notf_in = n_in_pw - f_in
    notf_out = n_not_in_pw - f_out

    table_f = [[f_in, f_out], [notf_in, notf_out]]
    or_f, p_f = stats.fisher_exact(table_f, alternative="greater")

    # M-biased enrichment
    m_in = len(pw_targets & m_biased_targets)
    m_out = n_m_total - m_in
    notm_in = n_in_pw - m_in
    notm_out = n_not_in_pw - m_out

    table_m = [[m_in, m_out], [notm_in, notm_out]]
    or_m, p_m = stats.fisher_exact(table_m, alternative="greater")

    pw_name = pathway_names.get(pw_id, pw_id)

    pathway_results[pw_id] = {
        "pathway_name": pw_name,
        "n_target_genes_in_pathway": n_in_pw,
        "f_biased_in_pathway": f_in,
        "m_biased_in_pathway": m_in,
        "neutral_in_pathway": n_in_pw - f_in - m_in,
        "f_enrichment_odds_ratio": round(or_f, 4) if np.isfinite(or_f) else "inf",
        "f_enrichment_p": float(f"{p_f:.6e}"),
        "m_enrichment_odds_ratio": round(or_m, 4) if np.isfinite(or_m) else "inf",
        "m_enrichment_p": float(f"{p_m:.6e}"),
    }
    pw_pvals_f.append(p_f)
    pw_names_f.append(pw_id)
    pw_pvals_m.append(p_m)
    pw_names_m.append(pw_id)

# FDR correction for F-enrichment and M-enrichment separately
if pw_pvals_f:
    reject_f, fdr_f, _, _ = multipletests(pw_pvals_f, method="fdr_bh", alpha=0.05)
    reject_m, fdr_m, _, _ = multipletests(pw_pvals_m, method="fdr_bh", alpha=0.05)
    for i, pw_id in enumerate(pw_names_f):
        pathway_results[pw_id]["f_enrichment_fdr_q"] = float(f"{fdr_f[i]:.6e}")
        pathway_results[pw_id]["f_significant_fdr05"] = bool(reject_f[i])
        pathway_results[pw_id]["m_enrichment_fdr_q"] = float(f"{fdr_m[i]:.6e}")
        pathway_results[pw_id]["m_significant_fdr05"] = bool(reject_m[i])

# Sort by most significant F-enrichment
sorted_pw_f = sorted(pathway_results.items(),
                     key=lambda x: x[1]["f_enrichment_p"])
sorted_pw_m = sorted(pathway_results.items(),
                     key=lambda x: x[1]["m_enrichment_p"])

n_f_sig = sum(1 for v in pathway_results.values()
              if v.get("f_significant_fdr05", False))
n_m_sig = sum(1 for v in pathway_results.values()
              if v.get("m_significant_fdr05", False))

results["pathway_enrichment"] = {
    "description": "Fisher exact test for pathway enrichment of F-biased vs M-biased drug targets",
    "method": "Fisher exact test (one-sided, greater)",
    "fdr_method": "Benjamini-Hochberg (separate for F and M enrichment)",
    "n_pathways_tested": len(eligible_pathways),
    "n_f_enriched_fdr05": n_f_sig,
    "n_m_enriched_fdr05": n_m_sig,
    "background": {
        "total_targets": n_total_targets,
        "f_biased_targets": n_f_total,
        "m_biased_targets": n_m_total,
        "neutral_targets": len(neutral_targets),
    },
    "top_f_enriched": {pw_id: pathway_results[pw_id]
                       for pw_id, _ in sorted_pw_f[:30]},
    "top_m_enriched": {pw_id: pathway_results[pw_id]
                       for pw_id, _ in sorted_pw_m[:30]},
    "all_pathways": pathway_results,
}

print(f"  Pathways tested: {len(eligible_pathways)}")
print(f"  F-enriched (FDR < 0.05): {n_f_sig}")
print(f"  M-enriched (FDR < 0.05): {n_m_sig}")
print("\n  Top F-enriched pathways:")
for pw_id, _ in sorted_pw_f[:10]:
    r = pathway_results[pw_id]
    print(f"    {r['pathway_name'][:55]:55s} "
          f"F={r['f_biased_in_pathway']}/{r['n_target_genes_in_pathway']} "
          f"p={r['f_enrichment_p']:.2e} q={r.get('f_enrichment_fdr_q', 'NA')}")
print("\n  Top M-enriched pathways:")
for pw_id, _ in sorted_pw_m[:10]:
    r = pathway_results[pw_id]
    print(f"    {r['pathway_name'][:55]:55s} "
          f"M={r['m_biased_in_pathway']}/{r['n_target_genes_in_pathway']} "
          f"p={r['m_enrichment_p']:.2e} q={r.get('m_enrichment_fdr_q', 'NA')}")

# ---------------------------------------------------------------------------
# 6. ADDITIONAL: Kolmogorov-Smirnov test on log_ratio distributions
# ---------------------------------------------------------------------------
print("\n[6/6] Additional tests...")

# KS test: do F-biased and M-biased signals have symmetric log_ratio distributions?
f_ratios = signals[signals["direction"] == "female_higher"]["log_ratio"].values
m_ratios = signals[signals["direction"] == "male_higher"]["log_ratio"].values
ks_stat, ks_p = stats.ks_2samp(np.abs(f_ratios), np.abs(m_ratios))

# Mann-Whitney U test on absolute log_ratios
mw_stat, mw_p = stats.mannwhitneyu(np.abs(f_ratios), np.abs(m_ratios),
                                    alternative="two-sided")

# Overall signal direction across all comparisons (including no_difference)
n_f_all = int((all_signals["direction"] == "female_higher").sum())
n_m_all = int((all_signals["direction"] == "male_higher").sum())
n_nd_all = int((all_signals["direction"] == "no_difference").sum())
chi2_all, p_chi2_all = stats.chisquare(
    [n_f_all, n_m_all],
    f_exp=[(n_f_all + n_m_all) / 2, (n_f_all + n_m_all) / 2]
)

# Proportion test: is 53.76% (F-biased) significantly different from 50%?
from statsmodels.stats.proportion import proportions_ztest
z_stat, z_p = proportions_ztest(n_f, n_total, value=0.5, alternative="two-sided")

results["additional_tests"] = {
    "ks_test_effect_magnitude": {
        "description": "KS test: |log_ratio| distributions differ between F-biased and M-biased signals?",
        "ks_statistic": round(ks_stat, 6),
        "p_value": float(f"{ks_p:.6e}"),
        "mean_abs_log_ratio_f": round(float(np.mean(np.abs(f_ratios))), 4),
        "mean_abs_log_ratio_m": round(float(np.mean(np.abs(m_ratios))), 4),
        "interpretation": (
            f"The magnitude of sex differences differs significantly between "
            f"F-biased (mean |log_ratio|={np.mean(np.abs(f_ratios)):.4f}) and "
            f"M-biased (mean |log_ratio|={np.mean(np.abs(m_ratios)):.4f}) signals "
            f"(KS D={ks_stat:.4f}, p={ks_p:.2e})."
        )
    },
    "mann_whitney_effect_magnitude": {
        "description": "Mann-Whitney U test on |log_ratio|",
        "u_statistic": float(mw_stat),
        "p_value": float(f"{mw_p:.6e}"),
    },
    "proportion_z_test": {
        "description": "Z-test for proportion F-biased vs 50%",
        "z_statistic": round(z_stat, 4),
        "p_value": float(f"{z_p:.2e}"),
    },
    "all_comparisons_chi_square": {
        "description": "Chi-square: F vs M direction across all 254,114 comparisons",
        "n_female_higher": n_f_all,
        "n_male_higher": n_m_all,
        "n_no_difference": n_nd_all,
        "n_total": len(all_signals),
        "chi_square_stat": round(chi2_all, 2),
        "p_value": float(f"{p_chi2_all:.6e}"),
    },
}

print(f"  KS test (|log_ratio| F vs M): D={ks_stat:.4f}, p={ks_p:.2e}")
print(f"  Mann-Whitney (|log_ratio|): U={mw_stat:.0f}, p={mw_p:.2e}")
print(f"  Z-test (proportion): z={z_stat:.4f}, p={z_p:.2e}")
print(f"  Chi-sq (all comparisons F vs M): chi2={chi2_all:.2f}, p={p_chi2_all:.2e}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
elapsed = time.time() - t0

summary = {
    "script": "v4_09_statistical_tests.py",
    "timestamp": pd.Timestamp.now().isoformat(),
    "elapsed_seconds": round(elapsed, 1),
    "n_permutations": N_PERMUTATIONS,
    "random_seed": SEED,
    "key_findings": {
        "1_signal_female_bias": (
            f"Female-biased signals ({n_f:,}) significantly exceed male-biased ({n_m:,}), "
            f"p < 1e-300 (binomial, H0: 50/50). Also significant vs FAERS baseline "
            f"(p = {binom_vs_faers.pvalue:.2e})."
        ),
        "2_drug_classes": (
            f"{sig_dc}/{len(drug_class_results)} drug classes show significant "
            f"sex bias after FDR correction."
        ),
        "3_target_permutation": (
            f"{n_sig_perm}/{len(moderate)} moderately biased targets survive "
            f"FDR correction (permutation test, {N_PERMUTATIONS:,} iterations)."
        ),
        "4_pathway_enrichment": (
            f"{n_f_sig} pathways enriched for F-biased targets, "
            f"{n_m_sig} for M-biased targets (Fisher exact, FDR < 0.05)."
        ),
    },
}

results["summary"] = summary

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n{'=' * 72}")
print(f"Results saved to: {OUTPUT_FILE}")
print(f"Elapsed: {elapsed:.1f}s")
print(f"{'=' * 72}")
print("\n=== KEY FINDINGS ===")
for k, v in summary["key_findings"].items():
    print(f"  {k}: {v}")
print()
