# SexDiffKG Comprehensive Audit — 2026-03-08
## Ultra-Deep Analysis: Integrity, Methodology, Contribution, and Publication Readiness

---

## EXECUTIVE SUMMARY

SexDiffKG is a **genuinely novel and significant contribution** to computational pharmacovigilance. The core innovation — treating sex as a first-class structural dimension in a knowledge graph rather than an aggregated attribute — fills a real gap that PrimeKG, Hetionet, DRKG, and PharmKG all leave open. The scale (14.5M FAERS reports, 96,281 sex-differential signals) is unprecedented. However, several integrity issues must be resolved before publication to ensure the work withstands peer review.

**Verdict**: The work will be **appreciated and recognized** by the computational biology and pharmacovigilance communities, but specific issues below could lead to **justified critique** if not addressed.

---

## SECTION 1: CRITICAL ISSUES (Must Fix Before Publication)

### 1.1 Canada Vigilance Cross-Reference FAILED

**Location**: `scripts/v4_13_canada_vigilance_signals.py:128-133`
**Evidence**: `analysis/canada_vigilance_signals_v4.json` line 24

The FAERS cross-reference in the Canada Vigilance analysis **threw a SQL error**:
```
Binder Error: Referenced column "adverse_event" not found in FROM clause!
```

**Root cause**: Line 128 reads from `signals_v2/sex_differential.parquet` which uses the column name `pt` (from `04_compute_signals.py:534`), but the SQL at line 133 references `f.adverse_event` — a column that doesn't exist.

**Impact**: The "91% Canada Vigilance concordance" claim in `grand_audit_report.md:88` is **not verified by the v4 pipeline**. The Canada Vigilance signals themselves were computed correctly (7,655 strong signals from 592,089 reports), but the cross-reference against FAERS was never successfully executed.

**Fix**: Change `adverse_event` to `pt` in the SQL query, or use the v4 signal file path (`signals_v4/`) instead of `signals_v2/`.

**Manuscript impact**: The complete manuscript (`Publication/manuscript_scidata_COMPLETE.md`) does NOT cite the 91% figure — it is only in `grand_audit_report.md` and `vault_docs/`. So the manuscript is safe, but the audit report is misleading.

---

### 1.2 Death Statistics Inconsistency (THREE Different Numbers)

**Location**: `grand_audit_report.md:56-63`, `vault_docs/MASTER_FINDINGS_SYNTHESIS.md:60-64`

Three different "% female" values for death-related signals exist across the codebase:

| Source | %F | N | Definition |
|--------|-----|-----|-----------|
| `outcome_severity_sex.json` death_detail | 46.2% | 450 | Death-specific AE terms only |
| `outcome_severity_sex.json` Fatal category | **50.1%** | 738 | Fatal outcome severity category |
| `death_deepdive_analysis.json` | 68.9% | 856 | All death-associated signals |
| `master_statistics.json` death field | 74.5% | 337 | MedDRA PT "Death" only |
| `MASTER_FINDINGS_SYNTHESIS.md` Finding #7 | **"74%"** | — | Uncited |

**Impact**: The MASTER_FINDINGS_SYNTHESIS still claims "DEATH IS 74% FEMALE" — this is the narrowest definition (only signals where the AE term is literally "Death"), not the standardized Fatal severity category (50.1%) that the audit recommended.

**Resolution**: The grand audit correctly identified 50.1%F (Fatal severity, n=738) as canonical. The ISMB abstract uses this correctly in the severity-sex gradient. Finding #7 in the master synthesis must be corrected.

---

### 1.3 Zero Automated Test Coverage

**Location**: Entire codebase (84 scripts, 0 test files)

There are no pytest/unittest files, no CI/CD pipeline, and no test configuration. Critical mathematical functions (`compute_ror`, `compute_prr`, `statsmodels_fdr`) have no unit tests. A bug in these functions would silently corrupt all 96,281 signals and every downstream claim.

**Impact**: Reviewers at Scientific Data or ISMB may flag the lack of automated testing as a reproducibility concern. The existing audit scripts (`audit_reproducibility.py`, `validate_40_benchmarks_v4.py`) validate outputs but not the correctness of the code itself.

**Recommendation**: At minimum, add unit tests for the core statistical functions (ROR, PRR, FDR) with known-answer test cases from pharmacovigilance textbooks. See `TEST_COVERAGE_ANALYSIS.md` for the full plan.

---

## SECTION 2: STATISTICAL METHODOLOGY AUDIT

### 2.1 ROR Computation — CORRECT with Minor Concern

**Location**: `scripts/04_compute_signals.py:308-345`

The ROR formula is standard: `ROR = (a*d) / (b*c)` with 95% CI via `exp(ln(ROR) ± 1.96 * sqrt(1/a + 1/b + 1/c + 1/d))`. This matches the Rothman-Greenland formulation used in standard pharmacovigilance (van Puijenbroek 2002, Bate 2009).

**Minor concern**: The pseudocount approach (line 326-329) uses 0.5 for b,c when zero, and 1 for a,d. This is the Haldane correction, which is standard but may inflate ROR for zero-cell contingency tables. Consider noting this in the methods section.

### 2.2 PRR Computation — CORRECT

**Location**: `scripts/04_compute_signals.py:348-384`

Standard PRR formula with Yates-uncorrected chi-squared. The formula matches Evans et al. (2001).

### 2.3 Benjamini-Hochberg FDR — CORRECT but Custom

**Location**: `scripts/04_compute_signals.py:434-471`

A custom BH FDR implementation rather than using `statsmodels.stats.multitest.multipletests`. The implementation appears correct (sorted p-values, BH threshold, corrected p-values via minimum accumulation), but the per-sex stratification in `apply_fdr_correction` (line 387-431) means FDR is computed within each sex stratum separately. This is methodologically defensible (different total numbers of comparisons per sex), and is documented.

**Recommendation**: Add a unit test comparing the custom implementation against `statsmodels.stats.multitest.multipletests` to verify equivalence.

### 2.4 Sex-Differential Signal — CORRECT

**Location**: `scripts/04_compute_signals.py:474-546`

`log_ror_ratio = ln(ROR_female) - ln(ROR_male) = ln(ROR_F / ROR_M)`. Uses natural log (documented in the manuscript). The threshold |ln ratio| >= 0.5 corresponds to ~1.65-fold difference, which is explicitly noted.

### 2.5 Temporal Validation — METHODOLOGICALLY SOUND

**Location**: `scripts/v4_10_temporal_validation.py`

Train/test split on `fda_dt` (2004-2020 / 2021-2025) is standard in temporal pharmacovigilance validation. The 84% directional precision for strong signals replicated across periods is strong evidence of temporal stability.

**Concern**: Only 51.4% of reports (7.47M of 14.5M) had valid event dates. The manuscript correctly notes this but should clarify whether the 48.6% missing-date reports could have systematically different sex distributions.

### 2.6 Statistical Tests Module — CORRECT

**Location**: `scripts/v4_09_statistical_tests.py`

Uses scipy.stats for binomial tests, chi-square goodness-of-fit, and statsmodels for FDR correction. The Cohen's h effect size (0.0755) is correctly described as "small but highly significant" — this is honest reporting.

**Important**: The binomial test against the null of 50% gives p < 1e-121, but against the FAERS reporting proportion (60.1% female), the observed 53.8% is actually *below* what reporting bias alone would predict. This is a strong methodological point that undermines the "reporting bias" criticism.

---

## SECTION 3: MOLECULAR DATA INTEGRITY

### 3.1 Data Sources — Current and Appropriate

| Source | Version | Status |
|--------|---------|--------|
| FAERS | 2004Q1-2025Q3 | Current (latest available) |
| STRING | v12.0 | Current as of 2024 |
| ChEMBL | 36 | Current (released Jan 2024) |
| Reactome | 2026-02 | Current |
| GTEx | v8 (Oliva 2020) | Current reference dataset |
| DiAna | 2025 | Current |

### 3.2 ID Mapping — Verified

The VEDA integrity audit (`analysis/veda_integrity_audit.json`) passed all 41 checks:
- 0 NaN node IDs, 0 duplicate node IDs
- 0 orphan edge endpoints
- 0 self-loops
- All Ensembl IDs valid format (12,577/12,577 ENSG*)
- Gene symbols 100% standard format

### 3.3 KG Structure — Sound

- 109,867 nodes across 6 categories (Gene: 77,498 | Protein: 16,201 | AE: 9,949 | Drug: 3,920 | Pathway: 2,279 | Tissue: 20)
- 1,822,851 edges across 6 predicates
- Zero orphan entities in triple file
- All edge subjects and objects present in node file
- MD5 checksums verified for all output files

### 3.4 GTEx Integration — Minimal but Correct

Only 289 sex-differential expression edges in the KG. This is correct — Oliva et al. (2020) reported relatively few genes passing strict significance thresholds for sex-differential expression. The manuscript correctly notes that adding these 289 edges modestly improved DistMult performance (MRR 0.0932 → 0.1013).

### 3.5 Drug-Target Coverage

12,682 drug-target edges from ChEMBL. Drug name coverage: 100%. Target name: 100%. Gene symbol: 99.4%. UniProt: 100%.

---

## SECTION 4: CONTRIBUTION TO HUMAN KNOWLEDGE

### 4.1 What is Genuinely Novel

1. **First sex-stratified pharmacovigilance KG**: Existing biomedical KGs (PrimeKG, Hetionet, DRKG, PharmKG) aggregate safety data without sex stratification. SexDiffKG is the first to encode sex as a structural property of drug-AE edges.

2. **Scale**: 14.5M reports, 96,281 sex-differential signals across 2,178 drugs and 5,069 AEs. No prior study has systematically characterized sex differences at this scale.

3. **Severity-sex gradient**: The finding that fatal AEs are sex-balanced (50.1%F) while mild AEs are 63.5% female (rho=0.93) has not been previously reported.

4. **Anti-regression effect**: Female signal bias intensifying with statistical power (rho=1.0) is counter-intuitive and novel.

5. **20-class therapeutic spectrum**: First systematic ranking from CDK4/6 inhibitors (93.7%F) to ICIs (46.9%F).

### 4.2 What Reviewers Will Appreciate

- The transparency of including all 244 analysis JSONs and 84 scripts
- The honest reporting of effect sizes (Cohen's h = 0.076, "small")
- The temporal validation demonstrating signal stability
- The explicit acknowledgment of limitations (FAERS reporting biases, confounding by indication)
- The 40-benchmark validation with directional precision
- The comprehensive KG documentation in Biolink-compliant format

### 4.3 What Reviewers Will Critique

1. **Confounding by indication**: The anti-CD20 paradox (Finding #4) shows that indication drives sex bias as much as pharmacology. Reviewers will ask whether the entire signal set is confounded by differential prescribing patterns rather than true pharmacological sex differences. **Mitigation**: The manuscript acknowledges this explicitly and the reporter-signal decorrelation (r=-0.007) partially addresses it.

2. **FAERS reporting bias**: 60.1% of FAERS reports are from women. Reviewers will argue that female-predominant signals simply reflect reporting proportions. **Mitigation**: The binomial test against the FAERS baseline (53.8% observed vs 60.1% expected) actually shows *fewer* female signals than reporting alone would predict. This is a strong defense.

3. **No confounding adjustment**: Unlike OHDSI/OMOP studies, there is no adjustment for age, comorbidity, concomitant medications, or dose. The ROR/PRR approach is signal detection, not causal inference. **Mitigation**: This is a data descriptor, not a causal claim paper. The manuscript correctly frames results as signals, not causal relationships.

4. **Lack of clinical validation**: The 40 benchmarks are from published literature, not from prospective clinical data. **Mitigation**: This is standard for computational pharmacovigilance. FAERS-based signal detection is by definition retrospective.

5. **MRR of 0.2484 is modest**: Compared to PrimeKG (which achieves higher MRR on specific tasks), the embedding performance is moderate. **Mitigation**: The KG has 6 relation types (vs PrimeKG's 30+), and AMRI > 0.99 shows triples rank in the top 0.5% of candidates.

### 4.4 Will Humans Recognize and Appreciate This Work?

**YES, with qualifications.** The work fills a genuine gap in the pharmacovigilance landscape. The ISMB 2026 venue is appropriate — ISMB accepts KG/computational biology work of this type. Scientific Data is the right journal for a data descriptor of this nature.

The work will be **especially appreciated by**:
- Pharmacovigilance researchers who need sex-stratified signals
- KG/ML researchers who want a domain-specific benchmark with sex as a novel dimension
- Regulatory scientists interested in sex-specific drug safety patterns

The work will be **critiqued by**:
- Clinical pharmacologists who want confounding-adjusted estimates (this is not the goal)
- Causal inference advocates who see signal detection as insufficient
- Those who expect prospective validation (impossible for a data descriptor)

---

## SECTION 5: MANUSCRIPT ACCURACY AUDIT

### 5.1 Key Numbers — All Verified

| Claim | Manuscript Value | Source Value | Status |
|-------|-----------------|--------------|--------|
| FAERS reports | 14,536,008 | `sexdiffkg_statistics_v4.json` | MATCH |
| Sex-differential signals | 96,281 | `sexdiffkg_statistics_v4.json` | MATCH |
| Female-higher | 51,771 | `sexdiffkg_statistics_v4.json` | MATCH |
| Male-higher | 44,510 | `sexdiffkg_statistics_v4.json` | MATCH |
| Female proportion | 53.8% | 51771/96281 = 53.77% | MATCH |
| DiAna mappings | 846,917 | `sexdiffkg_statistics_v4.json` | MATCH |
| Resolution rate | 53.9% | `sexdiffkg_statistics_v4.json` | MATCH |
| KG nodes | 109,867 | `sexdiffkg_statistics_v4.json` | MATCH |
| KG edges | 1,822,851 | `sexdiffkg_statistics_v4.json` | MATCH |
| ComplEx MRR | 0.2484 | `sexdiffkg_statistics_v4.json` | MATCH |
| Hits@10 | 40.69% | `sexdiffkg_statistics_v4.json` | MATCH |
| AMRI | 0.9902 | `sexdiffkg_statistics_v4.json` | MATCH |
| Benchmark precision | 82.8% | `cross_database_concordance.json` | MATCH |
| Temporal directional precision | 84.0% | `temporal_validation_v4.json` | MATCH |
| Binomial p-value | 3.5e-121 | `statistical_tests_v4.json` | MATCH |
| Cohen's h | 0.076 | `statistical_tests_v4.json` (0.0755) | MATCH (rounded) |

### 5.2 Manuscript Does NOT Include Unverified Claims

The complete manuscript avoids the problematic claims:
- Does NOT cite "91% Canada Vigilance concordance" (good)
- Does NOT claim "DEATH IS 74% FEMALE" (good)
- Does NOT claim "82.9% composite concordance" (that's in the audit, not manuscript)
- Correctly uses the temporal validation numbers (84.0% strong, 72.6% relaxed)

### 5.3 Methodological Completeness

The Technical Validation section is thorough:
- 5 validation strategies documented
- Internal consistency audits with specific pass/fail counts
- MD5 checksums for output files
- Honest acknowledgment of limitations
- Embedding evaluation with multiple metrics

---

## SECTION 6: PRE-PUBLICATION ACTION ITEMS

### Critical (Must Fix)
1. Fix Canada Vigilance cross-reference bug (`adverse_event` → `pt`)
2. Update `MASTER_FINDINGS_SYNTHESIS.md` Finding #7 death statistic to 50.1%F
3. Add basic unit tests for core statistical functions (ROR, PRR, FDR)

### Important (Should Fix)
4. Add note in methods about the Haldane pseudocount correction for zero cells
5. Clarify in temporal validation that 48.6% of reports lacked valid dates
6. Standardize death statistics across all vault docs and drafts
7. Remove/flag OpenFDA concordance from validation composite (negative correlation)
8. Document the natural logarithm base consistently in all materials

### Nice to Have
9. Add CI/CD pipeline with pytest
10. Flesh out the 3 thin paper drafts (<2KB) or remove them
11. Add conftest.py with synthetic data fixtures for future testing
12. Consider adding the Canada Vigilance results to the manuscript once the bug is fixed

---

## SECTION 7: COMPETITIVE LANDSCAPE POSITIONING

### Direct Competitors
- **PrimeKG** (Chandak et al., 2023): 29 edge types, 100K+ nodes. No sex stratification. SexDiffKG fills this gap.
- **Hetionet** (Himmelstein et al., 2017): 47K nodes, 24 edge types. No sex-specific safety data.
- **DRKG** (Ioannidis et al., 2020): Drug repurposing KG. No sex dimension.
- **PharmKG** (Zheng et al., 2021): No sex-stratified signals.

### Why SexDiffKG is Novel
None of the above KGs encode sex as a structural dimension on drug-AE edges. The `sex_differential_adverse_event` edge type with `log_ror_ratio` as a quantitative property is unique to SexDiffKG.

### Key Differentiator
SexDiffKG converts sex from a metadata attribute into a first-class graph structural element, enabling embedding-based inference of sex-differential signals that is impossible with sex-aggregated KGs.

---

## SECTION 8: METHODS ASSESSMENT (Does it Follow Standards?)

### Pharmacovigilance Standards
| Standard | Status |
|----------|--------|
| ROR computation (van Puijenbroek 2002) | Compliant |
| PRR computation (Evans 2001) | Compliant |
| BH FDR correction (Benjamini-Hochberg 1995) | Compliant |
| Signal threshold (ROR_lower > 1, a >= 5) | Standard |
| Sex-differential threshold (|ln ratio| > 0.5) | Novel but justified |

### KG Standards
| Standard | Status |
|----------|--------|
| Biolink Model node categories | Compliant |
| KGX format (nodes/edges TSV) | Compliant |
| PyKEEN triple format | Compliant |

### FAIR Principles
| Principle | Status |
|-----------|--------|
| Findable (persistent identifiers) | Planned (Zenodo DOI) |
| Accessible (open access) | Yes (GitHub + Zenodo) |
| Interoperable (standard formats) | Yes (Biolink, KGX) |
| Reusable (license, provenance) | Yes (CC-BY-SA) |

---

*Generated: 2026-03-08 by comprehensive automated audit*
*Total analysis files reviewed: 244 JSONs, 84 scripts, 40 vault docs*
