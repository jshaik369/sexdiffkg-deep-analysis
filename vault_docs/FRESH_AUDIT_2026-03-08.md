# SexDiffKG Fresh Adversarial Audit — March 8, 2026

**Auditor**: Claude (independent audit)
**Scope**: Complete repo — 83 Python scripts, 344 JSON files, 6 parquet files, 37 TSV files, 32 papers/drafts, 1 complete manuscript, all vault docs
**Method**: 4 parallel deep-audit agents + direct manuscript cross-referencing

---

## SECTION 1: CRITICAL — Manuscript vs Code Contradictions

These are claims in the **published manuscript** (`Publication/manuscript_scidata_COMPLETE.md`) that directly contradict the actual code.

### F-01: Train/Test Split — Manuscript Says 80/20, All Code Uses 90/10
- **Manuscript line 97**: "All models used an 80/20 train/test split with random_state=42"
- **Manuscript line 468 (Table 7 caption)**: "All models used an 80/20 train/test split"
- **Every single training script**: `full_factory.split(ratios=[0.9, 0.1], random_state=42)`
  - `v4_05b_train_rotatE_fixed.py:59`
  - `v4_05_train_rotatE.py:101`
  - `v4_07d_train_rotatE_cpu_fixed.py:25`
  - `v4_04_train_distmult.py` (same pattern)
- **Impact**: CRITICAL. The manuscript misrepresents the experimental methodology. A 90/10 split gives more training data, meaning reported metrics may be inflated compared to what an 80/20 split would produce. Peer reviewers or replicators using 80/20 will get different (likely worse) results.
- **Verdict**: The manuscript is WRONG. Code uses 90/10. Must fix manuscript or code.

### F-02: RotatE Embedding Dimension — Manuscript Says 256, Code Uses 200
- **Manuscript line 95**: "RotatE used 256-dimensional embeddings"
- **Manuscript line 127**: "RotatE used 256-dimensional embeddings trained for 200 epochs"
- **Manuscript line 466 (Table 7)**: "256 complex"
- **Every RotatE script**: `EMBEDDING_DIM = 200`
  - `v4_05b_train_rotatE_fixed.py:111`
  - `v4_05_train_rotatE.py:55`
  - `v4_07d_train_rotatE_cpu_fixed.py:35` (model init shows dim=200)
- **Impact**: CRITICAL. The manuscript reports a model architecture that doesn't match the actual trained model. 256 vs 200 complex dimensions = 512 vs 400 real parameters per entity.

### F-03: RotatE Metrics Published Before Training Completes
- **Manuscript line 95**: "RotatE v4.1 achieved MRR 0.2018, Hits@1 11.28%, Hits@10 36.77%, AMRI 0.9922"
- **User's status report**: RotatE v5.2 training is STILL RUNNING (epoch 5 of 200, evaluation in progress)
- **Question**: Where did MRR 0.2018 come from? No results file exists in the repo for RotatE. Either:
  - (a) These are fabricated numbers inserted as placeholders, or
  - (b) They come from a previous training run not in this repo
- **Impact**: CRITICAL if fabricated. The manuscript presents specific 4-decimal metrics for a model that may not have finished training.

### F-04: ComplEx Entity Count Mismatch
- **Manuscript line 263 (Table)**: ComplEx has "113,012" entities
- **Manuscript line 264 (Table)**: DistMult has "113,155" entities
- **Manuscript everywhere else**: KG has 109,867 nodes
- **What happened**: TriplesFactory creates its own entity index from unique values in triples, which may differ from the node file count (if some nodes have no edges, or if triples contain entities not in nodes.tsv). The mismatch is 113,012 vs 109,867 = 3,145 extra entities in the triple file.
- **Impact**: MODERATE. This reveals that 3,145 entity IDs appear in triples but not in nodes.tsv (orphan entities in triples), or that 3,145 nodes have zero edges. Either way, the KG is inconsistent.

### F-05: AMRI Uses Wrong Denominator in "Fixed" Script
- **File**: `v4_05b_train_rotatE_fixed.py:88-89`
```python
n_ent = testing_factory.num_entities
metrics["amri"] = round(1.0 - (2.0 * metrics["arithmetic_mean_rank"]) / (n_ent + 1), 4)
```
- **Problem**: Uses `testing_factory.num_entities` instead of `full_factory.num_entities`. The testing factory may have fewer entities.
- **Contrast**: `v4_05_train_rotatE.py:204` correctly uses `full_factory.num_entities`
- **Impact**: The "fixed" version introduced a NEW bug while fixing the epoch counter bug. Reported AMRI 0.9922 may be inflated.

---

## SECTION 2: CRITICAL — Entity Mapping Corruption

### F-06: Wrong Entity-to-Index Mapping Corrupts ALL Embedding Analyses
- **File**: `scripts/13_sexdiff_analysis.py:58-59`
```python
all_entities = sorted(set(triples["h"].unique()) | set(triples["t"].unique()))
entity2idx = {e: i for i, e in enumerate(all_entities)}
```
- **Same bug**: `scripts/16_molecular_audit.py:402-403`
```python
all_ents = sorted(set(triples["h"].astype(str)) | set(triples["t"].astype(str)))
ent2idx = {e: i for i, e in enumerate(all_ents)}
```
- **Why this is wrong**: PyKEEN's `TriplesFactory` builds its own internal `entity_to_id` mapping, which is NOT alphabetically sorted. The embeddings are stored in PyKEEN's index order. Looking up entity "DRUG:aspirin" by alphabetical index gives a DIFFERENT embedding than what PyKEEN trained.
- **Impact**: CRITICAL. Every downstream analysis using embeddings is wrong:
  - Drug clustering results → random
  - Drug similarity computations → random
  - Sex-bias scores from embeddings → random
  - All 89 "deterministic checks" in molecular audit → checking wrong embeddings
  - PCA visualizations → meaningless

### F-07: 13_sexdiff_analysis.py Uses v1 KG, Not v4
- **Line 39**: `nodes = pd.read_csv(base / "data/kg/nodes.tsv", sep="\t")` — this is the v1 KG path
- **Line 44**: `sexdiff = pd.read_parquet(base / "results/signals/sex_differential.parquet")` — v1 signals
- **Line 50**: `entity_emb = np.load(base / "results/kg_embeddings/DistMult/embeddings/entity_embeddings.npz")` — v1 embeddings
- **Impact**: The main analysis script operates on completely stale data. All results from this script are for the wrong KG version.

---

## SECTION 3: CRITICAL — Fabricated/Fake Data

### F-08: Fabricated Gene Expression Data (05c_gtex_sex_de.py)
- The script hardcodes a list of "sex-differentially expressed genes" with made-up Ensembl IDs, fold changes, and p-values rather than computing them from actual GTEx data
- These fabricated values propagate into the KG as `sex_de_gene` edges
- **Note**: Manuscript acknowledges this is "literature-curated" (line 83), which is different from "computed from raw data" but the script's approach of hardcoding fake Ensembl IDs with fake statistics is still problematic

### F-09: Figure 2 Script Uses Random Data
- `scripts/09_generate_figures.py` generates Figure 2 using `np.random.exponential` rather than loading actual signal data
- The manuscript describes Figure 2 as showing "the 96,281 sex-differential drug-adverse event signals" — but the script that generates it uses random numbers

---

## SECTION 4: CRITICAL — Statistical Methodology Bugs

### F-10: BH FDR Correction Implemented Incorrectly
- **File**: `scripts/04_compute_signals.py:434-471`
- Manual BH implementation applies correction factors in wrong order
- **Fix**: Use `statsmodels.stats.multitest.multipletests(pvals, method='fdr_bh')`

### F-11: Integrity Check Uses Wrong Log Base
- **File**: `scripts/15_deep_integrity_check.py`
- Uses `np.log2()` to re-derive `log_ror_ratio`, but pipeline uses `np.log()` (natural log)
- Every single signal is flagged as having a ratio discrepancy → integrity check is useless
- Manuscript line 123 even discusses the "log base clarification" but the script was never fixed

### F-12: Temporal Trend Analysis Uses Wrong Log Base
- **File**: `scripts/temporal_trend_analysis.py:242`
- Same log2 vs ln issue — temporal trend ratios are on a different scale than main analysis

---

## SECTION 5: CRITICAL — Training Script Bugs

### F-13: Block Training Resets PyKEEN Internal State
- **Files**: `v4_05_train_rotatE.py:130-143` and 5 other scripts
```python
for block_start in range(0, EPOCHS, CKPT_EVERY):
    losses = training_loop.train(num_epochs=n_ep, ...)
```
- PyKEEN's `train()` resets internal epoch counter on each call
- Learning rate scheduler restarts, internal state resets
- The "fixed" scripts (`v4_05b`, `v4_07d`) correctly use single `train()` call
- **Impact**: Models trained with block training may have suboptimal performance

### F-14: v4_07d Uses model.parameters() Instead of get_grad_params()
- **File**: `v4_07d_train_rotatE_cpu_fixed.py:39`
```python
optimizer = torch.optim.Adam(model.parameters(), lr=0.00005)
```
- Should use `model.get_grad_params()` for PyKEEN models
- May include non-trainable parameters in the optimization

---

## SECTION 6: MODERATE — Cross-Version Contamination

### F-15: Multiple Scripts Reference Wrong KG Version
| Script | References | Should reference |
|--------|-----------|-----------------|
| `13_sexdiff_analysis.py` | `data/kg/` (v1) | `data/kg_v4/` |
| `16_molecular_audit.py` | `data/kg/` (v1) | `data/kg_v4/` |
| `audit_data_lineage.py:30` | `data/kg/` (v1) | `data/kg_v4/` |
| `verify_numbers.py:36-51` | v3 expected ranges | v4 ranges |
| `audit_reproducibility.py:56-60` | v3 expected ranges | v4 ranges |
| `v4_15_sider_cross_reference.py:29` | v2 signals | v4 signals |
| `v4_13_canada_vigilance_signals.py:129` | v2 signals | v4 signals |
| `temporal_trend_analysis.py:28-31` | Uses log2 | Should use ln |

### F-16: v3 Scripts Can Overwrite v4 Publication Data
- `generate_all_submissions.py` contains v3 numbers (127K nodes, 5.8M edges, KEGG, 63.3% precision)
- `master_rebuild_v3.py` references KEGG, v2 signal paths, and calls fabricated gene data script
- Running either script would corrupt v4 outputs

### F-17: Benchmark 24 Is Duplicate of Benchmark 6
- **File**: `scripts/validate_40_benchmarks.py:37`
- ASPIRIN + GI haemorrhage appears as both benchmark 6 and benchmark 24
- Code comment says "dup of #6 w/ different source"
- Inflates benchmark count from 39 unique to 40 claimed
- 40 benchmarks → really 39 unique. Precision and coverage numbers change.

---

## SECTION 7: MODERATE — Hardcoded Values and Paths

### F-18: Hardcoded User Path in 17+ Scripts
All of these use `/home/jshaik369/sexdiffkg` which will fail on any other machine:
- `v4_model_comparison.py`, `v4_eval_distmult_v41.py`, `v4_06_retrain_distmult_v41.py`
- `v4_07_train_rotatE_gpu.py`, `v4_07b_train_rotatE_gpu_fixed.py`, `v4_07c_train_rotatE_cpu.py`
- `v4_07d_train_rotatE_cpu_fixed.py`, `v4_09_statistical_tests.py`, `v4_drug_clustering.py`
- `15_target_analysis_v4.py`, `16_molecular_audit.py`, `psychotropic_analysis.py`
- `oncology_sex_diff.py`, `temporal_trend_analysis.py`, `generate_figures.py`
- `generate_figures_5_6_7.py`, `update_docs_v4.py`, `audit_v4_complete.py`

### F-19: Hardcoded Entity Count Assertion
- `v4_embedding_prediction_analysis.py:188`: `assert factory.num_entities == 113012`
- Current v4 KG has 109,867 nodes → this assertion would fail
- Script crashes on any KG rebuild

### F-20: Hardcoded Embedding Metrics in Analysis Script
- `13_sexdiff_analysis.py:282-284`:
```python
"mrr": 0.04762,
"hits_at_10": 0.08852,
"amri": 0.9807,
```
- These are v3 metrics hardcoded directly into the output JSON, not read from any results file

---

## SECTION 8: MODERATE — Silent Failures

### F-21: v4_04_unify_ids Gene Lookup Key Mismatch
- **File**: `v4_04_unify_ids.py:259-260`
- Checks `if raw in gene_nodes_chembl` but accesses `gene_nodes_chembl[eid]` where `eid` has `GENE:` prefix
- Keys never match → gene-to-ChEMBL unification silently fails for ALL entries

### F-22: Drug Clustering Wrong Column Name
- **File**: `v4_drug_clustering.py:49`
- Uses `nodes.iloc[:, 1] == "Drug"` but v4 nodes.tsv has `category` as column 3 (index 2)
- Fallback `nodes["type"]` also wrong → zero Drug nodes selected → empty clustering

### F-23: Bare `except` Clauses Hiding Errors
- `v4_04_train_distmult.py:125`: `except:` swallows all errors
- `v4_14_per_country_deep_analysis.py:114`: `except: pass`
- `v4_05b_train_rotatE_fixed.py:84`: `except:` catches all metric lookup failures
- These hide real bugs during execution

### F-24: SQL Injection in Geographic Analysis
- `v4_12_geographic_variation.py:52`: `AND reporter_country = '{country_code}'`
- Country codes interpolated directly via f-strings into SQL

---

## SECTION 9: POLICING THE LIVE TRAINING

### Status Report Claims vs Reality

| Claim | Reality |
|-------|---------|
| "Nothing is broken. Nothing was messed up" | FALSE. 8+ critical bugs identified, entity mapping corruption invalidates all embedding analyses |
| "All numbers verified against source parquet files on DGX" | Verified WHAT version? 13_sexdiff_analysis.py reads v1 KG, not v4 |
| "GROUND_TRUTH.json was already correct" | GROUND_TRUTH.json does not exist in this repo. Referenced in manuscript but not deposited |
| "RotatE v5.2 training" | No v5.2 training script exists. The repo has v4_05b_train_rotatE_fixed.py which trains on v4 KG |
| "Post-completion script prepared" | Not in this repo |
| "Paper number audit — All 29 papers audited" | Good, but manuscript still says 80/20 split (actually 90/10) and RotatE dim 256 (actually 200) |
| "5,658→5,069 AEs in 24 files" | Manuscript Table 3 line 405 now says 5,069 ✓ |
| "Signal split 51,771/44,510" | Manuscript line 69 matches ✓ |

### RotatE v5.2 Training: What's Actually Running?

Based on `results/kg_v52_build_summary.json`:
- KG v5.2 = merger of v4 (109,867 nodes) + VEDA-KG → 217,993 nodes, 3,194,017 edges
- This is a DIFFERENT KG than what the manuscript describes (109,867 nodes / 1,822,851 edges)
- If the v5.2 RotatE training uses this merged KG, the metrics will NOT be comparable to those reported for v4 in the manuscript
- The manuscript currently reports RotatE metrics as if they were trained on v4

---

## SECTION 10: Summary

### Severity Breakdown

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 14 | Manuscript contradicts code, entity mapping corruption, fabricated data |
| MODERATE | 10 | Version mismatches, silent failures, hardcoded values |
| MINOR | ~10 | Bare excepts, deprecated APIs, style issues |
| **Total** | **~34** | |

### The 5 Most Dangerous Issues

1. **80/20 vs 90/10 split (F-01)**: Manuscript lies about experimental methodology
2. **RotatE dim 256 vs 200 (F-02)**: Manuscript lies about model architecture
3. **Entity mapping corruption (F-06)**: ALL embedding-based analyses use wrong embeddings
4. **RotatE metrics possibly fabricated (F-03)**: Specific numbers for a model that may not have finished training
5. **v1 KG used in main analysis (F-07)**: Core analysis script operates on completely stale data

### What Needs to Happen Before Publication

1. Fix manuscript: 90/10 split, RotatE dim=200, verify RotatE metrics are real
2. Fix entity mapping in 13_sexdiff_analysis.py and 16_molecular_audit.py → use factory.entity_to_id
3. Regenerate all embedding-based analyses with correct entity indices
4. Fix AMRI denominator in v4_05b to use full_factory
5. Update all scripts to reference v4 KG paths
6. Delete or mark v3/v1 scripts as deprecated
7. Fix integrity check log base (log2 → ln)
8. Deposit GROUND_TRUTH.json (referenced in manuscript but missing)
9. Remove benchmark 24 duplicate → update count to 39

---

*Fresh audit completed March 8, 2026. 4 parallel agents + direct manuscript review.*
*Background agents still running — additional findings will be appended.*
