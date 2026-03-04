#!/usr/bin/env python3
"""Comprehensive v4 audit — checks all v4 data files for completeness and consistency."""
import json
import os
import pandas as pd
from pathlib import Path

BASE = Path("/home/jshaik369/sexdiffkg")
results = {"checks": [], "passed": 0, "failed": 0, "warnings": 0}

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results["checks"].append({"name": name, "status": status, "detail": detail})
    if condition:
        results["passed"] += 1
        print(f"  [PASS] {name}")
    else:
        results["failed"] += 1
        print(f"  [FAIL] {name}: {detail}")

def warn(name, detail):
    results["warnings"] += 1
    results["checks"].append({"name": name, "status": "WARN", "detail": detail})
    print(f"  [WARN] {name}: {detail}")

print("=" * 60)
print("SexDiffKG v4 COMPREHENSIVE AUDIT")
print("=" * 60)

# 1. FAERS data exists
print("\n[1/8] FAERS data...")
faers_dir = BASE / "data" / "processed" / "faers_clean"
demo_files = list(faers_dir.glob("demo_*.parquet"))
check("FAERS demo files exist", len(demo_files) > 0, f"Found {len(demo_files)}")

# 2. Drug normalization
print("\n[2/8] Drug normalization...")
norm_file = faers_dir / "drug_normalized_v4.parquet"
check("drug_normalized_v4.parquet exists", norm_file.exists())
if norm_file.exists():
    df = pd.read_parquet(norm_file)
    check("Drug norm has rows", len(df) > 500000, f"{len(df)} rows")

# 3. Signals
print("\n[3/8] Sex-differential signals...")
sig_file = BASE / "results" / "signals_v4" / "sex_differential_v4.parquet"
check("sex_differential_v4.parquet exists", sig_file.exists())
if sig_file.exists():
    sig = pd.read_parquet(sig_file)
    check("Signal count = 96,281", len(sig) == 96281, f"got {len(sig)}")
    f_count = len(sig[sig.direction == "female_higher"])
    m_count = len(sig[sig.direction == "male_higher"])
    check("F-higher = 51,771", f_count == 51771, f"got {f_count}")
    check("M-higher = 44,510", m_count == 44510, f"got {m_count}")
    check("No NaN in drug_name", sig.drug_name.isna().sum() == 0)
    check("No NaN in adverse_event", sig.adverse_event.isna().sum() == 0)

# 4. Knowledge Graph
print("\n[4/8] Knowledge Graph v4.1...")
kg_dir = BASE / "data" / "kg_v4"
for f in ["nodes.tsv", "edges.tsv", "triples.tsv"]:
    check(f"{f} exists", (kg_dir / f).exists())

nodes = pd.read_csv(kg_dir / "nodes.tsv", sep="\t")
edges = pd.read_csv(kg_dir / "edges.tsv", sep="\t")
triples = pd.read_csv(kg_dir / "triples.tsv", sep="\t", header=None)
check("Nodes = 109,867", len(nodes) == 109867, f"got {len(nodes)}")
check("Edges = 1,822,851", len(edges) == 1822851, f"got {len(edges)}")
check("Triples = edges", len(triples) == len(edges), f"triples={len(triples)} edges={len(edges)}")

# Check for NaN in triples
t_nan = triples.isna().any(axis=1).sum()
check("Zero NaN in triples", t_nan == 0, f"found {t_nan} NaN rows")

# Check nan strings
t_str_nan = ((triples[0] == "nan") | (triples[2] == "nan")).sum()
check("Zero 'nan' strings in triples", t_str_nan == 0, f"found {t_str_nan}")

# 5. Embeddings
print("\n[5/8] Embeddings...")
cx_file = BASE / "results" / "kg_embeddings" / "complex_v4_metrics.json"
check("ComplEx v4 metrics exist", cx_file.exists())
if cx_file.exists():
    cx = json.load(open(cx_file))
    check("ComplEx MRR > 0.2", cx["mrr"] > 0.2, f"MRR={cx['mrr']}")
    check("ComplEx Hits@10 > 0.3", cx["hits_at_10"] > 0.3, f"H@10={cx['hits_at_10']}")

# 6. Validation
print("\n[6/8] Validation...")
val_file = BASE / "results" / "validation_40_benchmarks_v4.json"
check("Validation results exist", val_file.exists())
if val_file.exists():
    val = json.load(open(val_file))
    check("40 benchmarks tested", val["total_benchmarks"] == 40)
    check("Precision > 80%", val["precision_pct"] > 80, f"got {val['precision_pct']}%")

# 7. Target analysis
print("\n[7/8] Target analysis...")
ta_file = BASE / "results" / "analysis" / "v4_target_analysis.json"
check("Target analysis exists", ta_file.exists())
ta_tsv = BASE / "results" / "analysis" / "v4_target_sex_bias.tsv"
check("Target TSV exists", ta_tsv.exists())

# 8. Statistics JSON consistency
print("\n[8/8] Statistics JSON...")
stats_file = BASE / "results" / "analysis" / "sexdiffkg_statistics.json"
check("Statistics JSON exists", stats_file.exists())
if stats_file.exists():
    st = json.load(open(stats_file))
    check("Stats version = v4", st.get("version") == "v4", f"got {st.get('version')}")
    check("Stats signals match file", st["pipeline"]["sex_differential_signals"] == 96281)
    check("Stats nodes match file", st["knowledge_graph"]["nodes"] == 109867)
    check("Stats edges match file", st["knowledge_graph"]["edges"] == 1822851)

# 9. Publication docs
print("\n[9/9] Publication documents...")
pub_dir = BASE / "Publication"
for f in ["ISMB2026_short_abstract.txt", "ASHG2026_abstract.txt", "NeurIPS2026_abstract.txt"]:
    fp = pub_dir / f
    if fp.exists():
        content = fp.read_text()
        has_v3_kegg = "KEGG" in content
        has_v3_nodes = "127,063" in content
        if has_v3_kegg or has_v3_nodes:
            warn(f"{f} has stale v3 text", "KEGG" if has_v3_kegg else "127,063")
        else:
            check(f"{f} has v4 numbers", True)

readme = (BASE / "README.md").read_text()
check("README has v4 nodes", "109,867" in readme, "Looking for 109,867")
check("README has Reactome", "Reactome" in readme)
check("README no KEGG reference", "KEGG" not in readme)

print("\n" + "=" * 60)
print(f"AUDIT COMPLETE: {results['passed']} passed, {results['failed']} failed, {results['warnings']} warnings")
print("=" * 60)

# Save results
with open(BASE / "results" / "audits" / "v4_comprehensive_audit.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to results/audits/v4_comprehensive_audit.json")
