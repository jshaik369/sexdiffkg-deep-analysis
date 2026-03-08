# Test Coverage Analysis: SexDiffKG Deep Analysis

## Current State

**The codebase has zero automated tests.** There are no `test_*.py` files, no `conftest.py`, no `pytest.ini`, and no CI/CD pipeline. The project contains 84 Python scripts with no unit, integration, or regression test suite.

The project does include validation/audit scripts (`audit_reproducibility.py`, `validate_40_benchmarks_v4.py`, `15_deep_integrity_check.py`) that verify pipeline outputs against expected values, but these are data-validation scripts — not automated software tests. They require the full FAERS dataset to run and cannot be executed in isolation.

---

## Priority Areas for Test Coverage

### Priority 1 (Critical) — Core Statistical Functions

These are pure mathematical functions that directly affect every downstream result. Bugs here silently corrupt all signals, KG edges, and manuscript claims.

**`scripts/04_compute_signals.py`**

| Function | Why it needs tests |
|---|---|
| `compute_ror(a, b, c, d)` | ROR formula, CI computation, pseudocount handling for zero cells. A sign error or off-by-one in the CI width would invalidate all 96,281 signals. |
| `compute_prr(a, b, c, d)` | PRR and chi-squared statistic. Division-by-zero edge cases with empty contingency cells. |
| `statsmodels_fdr(p_values, alpha)` | Custom BH FDR implementation. Incorrect rank handling or accumulation direction would change which signals pass the threshold. |
| `apply_fdr_correction(signal_df)` | Orchestrates per-sex FDR. Must correctly partition by sex and map results back to original indices. |
| `compute_sex_differential_signals(signal_df)` | log(ROR_F/ROR_M) calculation. Must handle NaN, zero, and negative ROR values. |

**Suggested tests:**
- Known-answer tests: verify ROR/PRR against hand-calculated 2x2 tables from textbooks
- Edge cases: `a=0`, `b=0`, `c=0`, `d=0`, all zeros, very large values
- FDR: verify against `statsmodels.stats.multitest.multipletests` on synthetic p-value vectors
- Regression: snapshot top-10 signals from a small synthetic dataset

---

### Priority 2 (High) — Drug Name Normalization

Drug normalization is the single largest source of entity resolution in the pipeline. The 4-tier cascade in `v4_01_normalize_diana.py` determines whether drugs are mapped correctly — errors propagate into the KG and all analyses.

**`scripts/v4_01_normalize_diana.py`**

| Function | Why it needs tests |
|---|---|
| `clean_name(name)` | Salt/formulation stripping. Must not over-strip (e.g., "SODIUM CHLORIDE" should not become "SODIUM" or empty string). Parenthetical removal may break names like "INTERFERON BETA-1A (AVONEX)". |
| `load_diana_dict()` | CSV parsing with semicolons, uppercase normalization. Edge cases: missing columns, NaN substances, duplicate keys. |
| Tier cascade logic (in `main`) | DiAna > prod_ai > ChEMBL > cleaned fallback. A drug matching in Tier 1 must not also be counted in Tier 2. Priority ordering must be respected. |

**Suggested tests:**
- `clean_name`: test salt stripping ("METOPROLOL TARTRATE" → "METOPROLOL"), no-op for clean names, non-string input returns ""
- Tier priority: mock all 4 dictionaries, verify that Tier 1 match prevents Tier 2 lookup
- Edge cases: empty strings, None values, names that are pure salt suffixes

---

### Priority 3 (High) — Knowledge Graph Construction

The `SexDiffKGBuilder` class in `06_build_kg.py` is well-structured and highly testable without any data dependencies.

**`scripts/06_build_kg.py`**

| Function | Why it needs tests |
|---|---|
| `add_node()` | Deduplication by ID, category assignment. Verify that adding the same node twice does not create duplicates. |
| `add_edge()` | Must reject edges with missing nodes. Verify edge properties are preserved. |
| `save_triples_tsv()` | Output format must match PyKEEN's expected `h\tr\tt` without headers. |
| `get_statistics()` | Category/predicate counting must be consistent with actual graph state. |
| `load_adverse_events()` | ID construction (`DRUG:NAME` format) must handle spaces, special chars, empty strings. |

**Suggested tests:**
- Build a small graph in memory (5 nodes, 8 edges), verify statistics
- Add edge with missing subject → verify it is skipped with warning
- Add duplicate node → verify idempotency
- Save triples and re-read → verify round-trip fidelity

---

### Priority 4 (Medium) — Deduplication Logic

**`scripts/03_deduplicate.py`**

| Function | Why it needs tests |
|---|---|
| `deduplicate_demo(demo_df)` | Core dedup: keep latest `fda_dt` per `caseid`, break ties by largest `primaryid`. Must filter to sex in (M, F). |
| `filter_related_tables()` | Drug/reac rows must be filtered to only surviving primaryids. |
| `create_checkpoint()` | JSON checkpoint must contain correct counts and removal rates. |

**Suggested tests:**
- Synthetic DataFrame with known duplicates (same caseid, different fda_dt) → verify correct row survives
- Tie-breaking: same caseid + same fda_dt → verify largest primaryid wins
- Sex filter: rows with sex='UNK' must be removed
- Related table filtering: drug/reac rows with removed primaryids must be dropped

---

### Priority 5 (Medium) — Temporal Validation

**`scripts/v4_10_temporal_validation.py`**

| Area | Why it needs tests |
|---|---|
| `compute_signals_for_period()` | SQL string interpolation with `filter_clause` — verify that train/test split correctly partitions by `fda_dt` relative to `TRAIN_CUTOFF = '20201231'` |
| Signal concordance | Verify that the concordance metric (signals found in train that replicate in test) is computed correctly |

**Suggested tests:**
- Synthetic data spanning 2019-2022, verify split produces correct train/test counts
- Edge case: drug-AE pair only in train period → not in test concordance
- Edge case: drug-AE pair only in test period → not counted as replication

---

### Priority 6 (Lower) — Statistical Tests Module

**`scripts/v4_09_statistical_tests.py`**

While this script uses well-tested scipy/statsmodels functions, the *orchestration* logic (which signals are fed to which test, how results are aggregated) should be tested.

| Area | Why it needs tests |
|---|---|
| Binomial test setup | Verify `n_f` and `n_m` counts are correctly extracted from the signals DataFrame |
| Permutation test | Verify the null distribution is generated correctly and the p-value is computed as the fraction of permuted stats >= observed |
| FDR across multiple tests | Verify that correction is applied to the correct set of p-values |

---

## Recommended Implementation Plan

### Phase 1: Set up test infrastructure
```
pip install pytest pytest-cov
```
Create `tests/conftest.py` with shared fixtures (small synthetic DataFrames for demo, drug, reac tables).

### Phase 2: Test core math (Priority 1)
Create `tests/test_compute_signals.py`:
- `test_ror_known_values` — textbook 2x2 tables
- `test_ror_zero_cell_handling` — pseudocount behavior
- `test_prr_known_values`
- `test_prr_zero_denominator`
- `test_fdr_matches_statsmodels` — compare custom BH vs statsmodels
- `test_fdr_all_significant` / `test_fdr_none_significant`
- `test_sex_differential_direction`

### Phase 3: Test normalization (Priority 2)
Create `tests/test_drug_normalization.py`:
- `test_clean_name_salts`
- `test_clean_name_formulations`
- `test_clean_name_edge_cases`
- `test_tier_cascade_priority`

### Phase 4: Test KG builder (Priority 3)
Create `tests/test_kg_builder.py`:
- `test_add_node_idempotent`
- `test_add_edge_missing_node`
- `test_statistics_accuracy`
- `test_triples_format`
- `test_drug_ae_id_construction`

### Phase 5: Test dedup (Priority 4)
Create `tests/test_deduplicate.py`:
- `test_dedup_keeps_latest`
- `test_dedup_tiebreak_primaryid`
- `test_dedup_filters_sex`
- `test_related_table_filtering`

### Phase 6: CI/CD
Add `.github/workflows/test.yml` to run `pytest --cov` on every push.

---

## Estimated Effort

| Phase | Files | Est. tests | Complexity |
|---|---|---|---|
| Phase 1: Infrastructure | 1 | 0 | Low |
| Phase 2: Core math | 1 | ~15 | Medium |
| Phase 3: Normalization | 1 | ~10 | Low |
| Phase 4: KG builder | 1 | ~10 | Low |
| Phase 5: Deduplication | 1 | ~8 | Medium |
| Phase 6: CI/CD | 1 | 0 | Low |
| **Total** | **6** | **~43** | |

## Key Observation

The most impactful tests are in **Phase 2** (core statistical functions). These functions are pure (no I/O), deterministic, and have well-defined mathematical specifications. A bug in `compute_ror` or `statsmodels_fdr` would silently corrupt every signal in the dataset and every claim in the manuscript. These tests should be written first.
