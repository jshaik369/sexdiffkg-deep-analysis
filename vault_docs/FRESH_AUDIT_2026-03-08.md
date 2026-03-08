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

## SECTION 10: Data File Integrity

### F-29: v4.2 JSON Has Wrong Signal Counts (4,000 Discrepancy)
- **File**: `sexdiffkg_statistics_v42.json` reports female_biased=55,771 and male_biased=40,510
- **Every other source**: 51,771 female / 44,510 male (verified in all TSV files, manuscript, JSON results)
- **Impact**: CRITICAL. A 4,000-count discrepancy in the v4.2 statistics file. If anyone uses the v4.2 stats, they get wrong numbers.

### F-30: Supplementary Table Numbering Conflicts
- `analysis/` and `supplementary/` directories both use table_S* naming but with DIFFERENT content:
  - S4 = model_comparison (analysis/) vs bidirectional_aes (supplementary/)
  - S5 = data_sources (analysis/) vs model_comparison (supplementary/)
  - S6 = pathway_enrichment (analysis/) vs death_signals (supplementary/)
- **Impact**: MODERATE. "Table S5" means completely different data depending on which directory.

### F-31: 535 Duplicate Rows in ATC WHO Hierarchy
- `data_processed/atc_who_hierarchy.csv`: 535 duplicate rows (8.9% of 6,030)
- `data_processed/kg_drug_atc_mapping.csv`: 50 duplicate rows (1.9% of 2,665) plus 253 missing chembl_id (9.5%)

### F-32: Molecular Parquet Files Have 45-91% Null Rates
- `gene_pathways.parquet`: uniprot_id 54.5% null, string_id 91.5% null
- `id_mappings.parquet`: ensembl_gene_id 50.4% null, string_id 88.5% null
- `ppi_network.parquet`: protein_ensembl 51.2% null, protein_symbol 44.6% null
- **Impact**: MODERATE. Any joins on these columns silently drop 45-91% of rows.

### F-33: sex_de_genes_v4.parquet Is Exact Duplicate
- `sex_de_genes.parquet` and `sex_de_genes_v4.parquet` are byte-for-byte identical
- Redundant file adds confusion about which is canonical

### F-34: 69% of Data Files Are Orphans
- 34 of 49 data files (all supplementary TSVs, all CSVs, several analysis TSVs) are not referenced by any Python script
- Generated by interactive sessions, not reproducible scripts

---

## SECTION 10b: JSON Data Integrity (344 Files Audited)

### F-35: FABRICATION SIGNAL — v4.2 F/M Shift Is Exactly +4,000/-4,000
- v4.1: female_higher=51,771, male_higher=44,510 (sum=96,281)
- v4.2: female_biased=55,771, male_biased=40,510 (sum=96,281)
- The shift is **exactly +4,000 female and -4,000 male**
- A real data cleaning operation would not produce a perfectly round redistribution
- **Impact**: CRITICAL. This is a strong indicator that the v4.2 numbers were manually edited, not computed

### F-36: Five Mutually Contradictory KG Sizes
| Source | Version | Nodes | Edges |
|--------|---------|-------|-------|
| `sexdiffkg_statistics.json` | v4.1 | 109,867 | 1,822,851 |
| `sexdiffkg_statistics_v42.json` | v4.2 | 126,575 | 5,489,928 |
| `v4_network_topology.json` | v4 | 127,063 | 5,839,717 |
| `kg_v52_build_summary.json` | v5 | 246,056 | 3,182,843 |
| v52 wave files | v5.2 | 217,993 | 3,194,017 |
- None agree. The v4.2 numbers (126,575 nodes, 5.49M edges) look like v3 data mislabeled as v4.2.

### F-37: 13 JSON Files Have Constant Placeholder Values (Fabrication Pattern)
- `wave117_drug_safety_sex_index.json`: all 50 entries have `pct_female = 0.5`
- `wave118_ae_sex_stability.json`: all 50 entries have `pct_female = 0.5`
- `v52_wave59_sex_bias_entropy.json`: all 20 entries have `pct_female = 50.0`
- `v52_wave62_ae_specificity_index.json`: all 20 entries have `pct_female = 50.0`
- `v52_wave9_ae_organ_network.json`: all 50 drugs have `n_organs = 18`
- `polypharmacy_sex_bias.json`: all 30 drugs have `n_socs = 13`
- `soc_sex_bias_analysis.json`: all 50 entries have `max_f_pct = 100.0` AND `spread = 100.0`
- `v4_target_analysis.json`: all 20 top_male_biased entries have `sex_bias_score = -1.0`
- 5 more files with similar constant-value patterns
- **Impact**: CRITICAL. Arrays that should contain computed data have identical values across all entries — a hallmark of placeholder/template data that was never replaced with real computations

### F-38: v4.2 "Cleaning" Produced 3x MORE Data (Impossible)
- v4.2 claims it removed 349,789 NaN edges and 1,584,555 duplicates
- Yet v4.2 has 5,489,928 edges vs v4.1's 1,822,851 (3x MORE)
- `has_adverse_event` went from 869K to 4.64M (5.3x increase)
- `interacts_with` dropped from 474K to 116K (75% loss)
- **Impact**: CRITICAL. Cleaning should REDUCE data, not triple it. The v4.2 stats file is internally contradictory.

### F-39: RotatE MRR Differs by Factor of 2,000x Between Files
- `grand_synthesis_session3.json`: RotatE_v4 MRR = 0.000106
- `all_models_comparison.json`: RotatE_v4.1 MRR = 0.2018
- A 1,900x difference for ostensibly the same model family

### F-40: 24.19M vs 14.54M Total Reports
- `grand_summary_session3.json`, `severity_sex_analysis.json`: total_reports = 24,194,276
- All canonical FAERS sources: 14,536,008
- The 24.19M number is 1.66x larger and never explained

### F-41: 190 NaN/Inf/Null Values Across JSON Files
- 73 float NaN values (e.g., `confidence_tiers.json`, `effect_size_deep.json`)
- 93 string "inf" odds ratios in `statistical_tests_v4.json` pathway enrichment
- 3 float Inf values in `v52_wave98_signal_enrichment.json`
- 21 null values across 5 files
- `v52_wave104_ppi_sex_propagation.json`: all 20 top_hubs have `direct_pctf = NaN`

### F-42: ChEMBL Version Regression
- v4.1 claims ChEMBL **36** (newer)
- v4.2 claims ChEMBL **35** (older)
- A version "upgrade" should not downgrade its data source

### F-43: FAERS F+M = Total Exactly (No Unspecified Sex)
- 8,744,397 + 5,791,611 = 14,536,008 with zero remainder
- Real FAERS data always has reports with unspecified sex
- Indicates pre-filtering that is undocumented in the manuscript

---

## SECTION 11: Cross-Paper Contradictions

### F-25: Death Signal Direction Contradicted Across Papers (28pp gap)
- **MASTER_FINDINGS_SYNTHESIS.md** and **bidirectional_ae_paper.md**: Death signals are 74-74.5% female-biased
- **Four other papers** (extreme_signals, organ_system, network_topology, seriousness_sex_gradient): Death signals are 46-46.2% female-biased
- **Impact**: CRITICAL. A 28 percentage-point contradiction on the SAME metric across papers in the same project. One set of papers says deaths are overwhelmingly female-biased; the other says they're nearly balanced.
- **Root cause**: Likely conflation of two different metrics — "mean female fraction of reports" vs "proportion of signals classified as female-direction by log ratio"

### F-26: Severity Gradient Reversed Between Papers
- **severity_sex_gradient_paper.md**: Life-threatening events = 75% female → severity INCREASES female bias
- **age_sex_interaction_paper.md**: Fatal events = 50.1% female → severity DECREASES female bias
- **Impact**: CRITICAL. These papers present OPPOSITE conclusions about the relationship between severity and sex bias

### F-27: "49,026 Strong Signals" Used With Incompatible Threshold Definitions
- One paper defines strong signals as |log_ratio| >= 0.5
- Another paper defines strong signals as |log_ratio| >= 1.0 AND >= 50 reports
- Both cite "49,026 strong signals" using these incompatible thresholds
- **Impact**: CRITICAL. The same count can't apply to two different filter criteria

### F-28: Systematic Metric Conflation Across All Papers
- **Root cause**: The project uses two different measures of "female bias" interchangeably:
  - (a) Mean female fraction of reports (demographic-based)
  - (b) Proportion of signals classified as female-direction by log ratio (signal-based)
- These measure FUNDAMENTALLY different things and produce dramatically different numbers
- Until every paper explicitly labels which metric is being used, cross-document contradictions will persist

---

## SECTION 11: Summary

### Severity Breakdown

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 28 | Manuscript contradicts code, entity mapping corruption, fabricated/placeholder data, cross-paper contradictions, impossible data transformations |
| MODERATE | 15 | Version mismatches, silent failures, hardcoded values |
| MINOR | ~10 | Bare excepts, deprecated APIs, duplicates, orphan files |
| **Total** | **~53** | |

### The 5 Most Dangerous Issues

1. **80/20 vs 90/10 split (F-01)**: Manuscript lies about experimental methodology
2. **RotatE dim 256 vs 200 (F-02)**: Manuscript lies about model architecture
3. **Entity mapping corruption (F-06)**: ALL embedding-based analyses use wrong embeddings
4. **RotatE metrics possibly fabricated (F-03)**: Specific numbers for a model that may not have finished training
5. **v1 KG used in main analysis (F-07)**: Core analysis script operates on completely stale data

6. **Death signal direction 74% vs 46% (F-25)**: Papers within the same project contradict each other by 28pp on whether death-associated signals are female-biased
7. **Severity gradient reversed (F-26)**: One paper says severity increases female bias; another says it decreases it
8. **Metric conflation (F-28)**: "Female bias" means different things in different papers — some use report demographics, others use signal direction

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
