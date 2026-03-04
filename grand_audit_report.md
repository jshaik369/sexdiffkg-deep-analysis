# SexDiffKG Grand Audit Report — All 100 Waves
**Date:** 2026-03-04
**Author:** J.Shaik (Autonomous Analysis Pipeline)

## Phase I: Integrity Sweep — PASS (100%)

### JSON Audit
- **204/204** analysis JSONs valid and parseable
- **0 corrupt, 0 missing**
- Total data: 3.0 MB

### Figure Audit
- **279/279** figures with PNG+PDF pairs
- Range: figS1 through fig264 (with gaps in numbering — expected)
- All at 300 DPI, publication quality

### Paper Audit
- **35/35** paper drafts valid
- 3 flagged as thin (< 2KB): hepatotoxicity_sex_paper.md (1,323B), severe_ae_sex_paper.md (1,636B), glp1ra_diabetes_paper.md (1,803B)
- Recommendation: flesh out or merge into domain papers

---

## Phase II: Deep Consistency Study

### Tier 1 — Strongest & Most Novel Findings (HIGH priority)

| # | Finding | Key Stat | Novelty |
|---|---------|----------|---------|
| 1 | **Severity-Sex Gradient** | Fatal 50.1%F → Moderate 63.5%F (rho=0.93, p=0.003) | **Entirely novel** — no prior systematic quantification |
| 2 | **Anti-Regression Monotonicity** | D1→D10 rho=1.0 (p=6.6e-64), bootstrap CI [0.988, 1.0] | **Counter-intuitive** — more data strengthens signal |
| 3 | **Extreme Female Asymmetry** | 7,457 F-extreme vs 519 M-extreme (14.4x), 221 vs 3 hubs (73.6x) | Scale never previously quantified |
| 4 | **20-Class Therapeutic Spectrum** | CDK4/6i 93.7%F → ICIs 46.9%F | First systematic 20-class ranking |

### Tier 2 — Strong Findings, Moderate Novelty

| # | Finding | Key Stat |
|---|---------|----------|
| 5 | Biologics Gap | 63.9%F vs 57.6%F small molecules (p=9.56e-117) |
| 6 | Reporter-Signal Decorrelation | r=-0.007 (p=0.74) — rules out reporter bias |
| 7 | Sex Prediction Model | R²=0.77, rho=0.90, 52.3% improvement |
| 8 | Volume-Sex Gradient | D1 50.4%F → D10 80.3%F (monotonic) |

### Tier 3 — Supporting & Confirmatory

| # | Finding | Key Stat |
|---|---------|----------|
| 9 | Cross-Validation Composite | 82.9% mean (Lit 92%, Meta 76.9%, Withdrawal 80%, Benchmark 82.8%) |
| 10 | Emerging Drug Classes | CGRP 83.0%F, PARPi 78.3%F, JAKi 66.9%F, ICIs 46.9%F |

---

## Identified Inconsistencies

### CRITICAL: Death/Fatal Statistics — Three Values

| Source | %F | N | Definition |
|--------|-----|-----|-----------|
| outcome_severity_sex.json death_detail | 46.2% | 450 | Death-specific AE terms only |
| outcome_severity_sex.json Fatal category | 50.1% | 738 | Fatal outcome severity category |
| death_deepdive_analysis.json | 68.9% | 856 | All death-associated signals |

**Resolution:** Standardize on Fatal severity category (50.1%F, n=738) as most defensible. Run sensitivity analyses with alternatives. Document in methods.

### MODERATE: Autoimmune F Fraction — 50.7% vs 69.2%

Signal-level (50.7%) vs drug-level mean (69.2%) aggregation difference. Document aggregation method explicitly.

### MINOR: Volume Gradient Binning

Three files report different ranges. **Canonical:** dose_response_sex.json decile values (50.4-80.3%F).

### MINOR: Cardiotoxicity Anti-Regression Exception

Cardiotoxicity rho=0.2 vs overall rho=1.0. Report honestly as domain-specific exception (possible sex-balanced cardiac risk factors, QT prolongation).

### MINOR: OpenFDA Concordance

66.7% with negative correlation, only 24 drugs. Underpowered — exclude from composite or flag explicitly.

---

## Validation Summary (All Sources)

| Source | Concordance | N |
|--------|-------------|---|
| Literature cross-validation | 92.0% | 11/12 |
| Canada Vigilance | 91.0% | 1,212 signals, r=0.785 |
| 40 Literature benchmarks | 82.8% | 24/29 correct direction |
| Drug withdrawal | 80.0% | 4/5 |
| Meta-analysis | 76.9% | 10/13 |
| **Composite** | **82.9%** | 4 sources |
| Internal split-half | r=0.755 | — |
| Sex prediction model | R²=0.77, rho=0.90 | — |

---

## Models

| Model | MRR | Hits@1 | Hits@10 | AMRI |
|-------|-----|--------|---------|------|
| ComplEx v4 | **0.2484** | 0.1678 | 0.4069 | 0.9902 |
| RotatE v4.1 | 0.2018 | — | — | — |
| DistMult v4.1 | 0.1013 | 0.0481 | 0.1961 | 0.9909 |

---

## Cumulative Totals (100 Waves, 10 Sessions)

- **204** analysis JSONs
- **279** publication figures (PNG+PDF)
- **35** paper drafts (Papers 1-41, some merged)
- **3.0 MB** analysis data
- **4** GitHub commits for Session 10
- **KG:** 109,867 nodes / 1,822,851 edges
- **FAERS:** 14,536,008 deduplicated reports
- **Signals:** 96,281 sex-differential (49,026 strong)

---

## Pre-Publication Action Items

1. Resolve death statistics inconsistency — pick one definition, sensitivity analyses
2. Document cardiotoxicity anti-regression exception
3. Remove/flag OpenFDA from composite validation
4. Standardize volume gradient to dose_response_sex decile values
5. Clarify autoimmune aggregation method
6. Flesh out 3 thin papers or merge into domain papers
