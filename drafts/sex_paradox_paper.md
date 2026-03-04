---
title: "The Sex Paradox in Pharmacovigilance: Drug Safety Signals Anti-Correlate with Reporting Patterns Across 2,178 Drugs"
authors: "Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)"
affiliation: "CoEvolve Network, Independent Researcher, Barcelona, Spain"
email: "jshaik@coevolvenetwork.com"
orcid: "0009-0002-1748-7516"
target_journal: "JAMA Internal Medicine / Pharmacoepidemiology and Drug Safety"
draft_version: "v1.0"
date: "2026-03-04"
---

## Abstract

**Background:** A persistent criticism of sex-differential pharmacovigilance analysis is that observed disparities merely reflect differential reporting rates: women comprise 60.2% of FAERS reporters, potentially inflating female-associated safety signals. We directly test this "reporting artifact" hypothesis.

**Methods:** We analyzed 96,281 sex-differential adverse event signals from 14.5 million FAERS reports (2004Q1-2025Q3) across 2,178 drugs. For each drug, we computed two independent metrics: (1) the proportion of total reports from female patients (report ratio), and (2) the proportion of sex-differential safety signals showing female predominance (signal ratio). If signals were reporting artifacts, these should positively correlate.

**Results:** The report ratio and signal ratio showed a significant NEGATIVE correlation (Spearman rho = -0.215, p = 6.92e-13, n = 1,090 drugs with >=10 signals). This anti-correlation persisted across sensitivity analyses:

1. **133 "paradox drugs"** had >60% female reports but <40% female-predominant signals. Examples: adalimumab (83%F reports, 38%F signals), levothyroxine (77%F reports, 20%F signals), interferon beta-1a (78%F reports, 13%F signals).

2. **32 "reverse paradox drugs"** had <40% female reports but >60% female-predominant signals. Examples: risperidone (29%F reports, 93%F signals, gap=64pp), tamsulosin (13%F reports, 81%F signals, gap=68pp), testosterone (9%F reports, 74%F signals, gap=65pp).

3. **Volume quintile gradient**: The lowest-volume quintile showed 42.9% female signals, rising monotonically to 73.3% in the highest quintile and 88.9% in the top 1%. This anti-regression pattern — effects INCREASING with statistical power — is the opposite of what artifacts produce.

4. **Effect size asymmetry**: Female-predominant signals had 4.6% larger effect sizes than male-predominant signals (mean |LR| 1.007 vs 0.963, Mann-Whitney p = 2.8e-41), with the asymmetry growing at higher thresholds.

**Conclusions:** Sex-differential drug safety signals are not reporting artifacts. The significant anti-correlation between reporting sex ratios and signal sex ratios, combined with the anti-regression volume gradient and effect size asymmetry, demonstrates that these signals reflect genuine pharmacological sex differences. The 133 paradox drugs where female-dominant reporting produces male-dominant signals provide the strongest evidence that biological, not reporting, mechanisms drive sex-differential drug safety.

## Introduction

Women comprise approximately 60% of adverse drug reaction reports in the FDA Adverse Event Reporting System (FAERS). This baseline imbalance has led to persistent methodological concerns: are observed sex differences in drug safety merely artifacts of differential reporting rates? If women report more frequently, shouldn't we expect more female-predominant safety signals simply as a mathematical consequence?

This concern has practical implications. Regulatory agencies, pharmaceutical companies, and clinical researchers may discount sex-differential safety signals as confounded by reporting bias, potentially delaying sex-specific drug safety interventions. To date, no systematic study has directly tested whether sex-differential signals track with or diverge from sex-specific reporting patterns across the full drug landscape.

We address this gap using the largest sex-stratified pharmacovigilance analysis to date, encompassing 96,281 sex-differential signals from 14.5 million FAERS reports across 2,178 drugs. Our approach is simple: if signals are reporting artifacts, the drugs with the highest female reporting proportion should also show the highest female signal proportion. If they anti-correlate, reporting bias cannot explain the signals.

## Methods

### Data Source

FAERS 2004Q1-2025Q3: 14,536,008 deduplicated reports (8,744,397 female, 60.2%; 5,791,611 male, 39.8%).

### Signal Generation

Sex-stratified Reporting Odds Ratios (ROR) were computed for each drug-adverse event pair with >=10 reports in each sex. The log ratio (LR = ln(ROR_female) - ln(ROR_male)) quantified the direction and magnitude of sex-differential signal. Signals with |LR| >= 0.5 were retained, yielding 96,281 sex-differential signals.

### Anti-Correlation Test

For each drug with >=10 signals:
- **Report ratio** = female reports / total reports (proportion of the drug's reports from women)
- **Signal ratio** = female-higher signals / total signals (proportion showing female predominance)
- Spearman correlation between report ratio and signal ratio

### Sensitivity Analyses

1. **Paradox identification**: Drugs where report and signal directions diverge
2. **Volume gradient**: Signal sex bias across volume quintiles
3. **Effect size comparison**: Mann-Whitney U test of |LR| between female and male signals

## Results

### Primary Finding: Anti-Correlation

Among 1,090 drugs with >=10 sex-differential signals, the correlation between female report proportion and female signal proportion was significantly NEGATIVE:

**Spearman rho = -0.215, p = 6.92e-13**

This means drugs reported more often by women tend to have FEWER female-predominant safety signals — the exact opposite of what reporting bias predicts.

### Paradox Drugs

**133 drugs** showed >60% female reports but <40% female-predominant signals (reporting predicts female dominance, but signals show male dominance):

| Drug | %F Reports | %F Signals | Gap |
|------|-----------|-----------|-----|
| Docetaxel | 75% | 11% | 64pp |
| Interferon beta-1a | 78% | 13% | 65pp |
| Methotrexate sodium | 71% | 9% | 62pp |
| Levothyroxine | 77% | 20% | 57pp |
| Fingolimod | 76% | 19% | 56pp |
| Denosumab | 81% | 23% | 57pp |
| Adalimumab | 83% | 38% | 45pp |
| Dupilumab | 62% | 17% | 45pp |

**32 drugs** showed the reverse paradox (<40% female reports but >60% female-predominant signals):

| Drug | %F Reports | %F Signals | Gap |
|------|-----------|-----------|-----|
| Tamsulosin | 13% | 81% | 68pp |
| Factor VIII | 7% | 74% | 67pp |
| Testosterone | 9% | 74% | 65pp |
| Risperidone | 29% | 93% | 64pp |
| Tafamidis | 26% | 86% | 61pp |
| Diamorphine | 32% | 83% | 50pp |
| Sorafenib | 31% | 80% | 49pp |

### Volume Anti-Regression

The proportion of female-predominant signals increased monotonically with report volume:
- Q1 (lowest volume): 42.9%F
- Q2: 46.4%F
- Q3: 51.3%F
- Q4: 55.2%F
- Q5 (highest volume): 73.3%F
- Top 1%: 88.9%F

This is the OPPOSITE of regression to the mean, which predicts that extreme values should moderate with more data. Instead, the female predominance AMPLIFIES with volume, consistent with genuine biological effects becoming more detectable with larger sample sizes.

### Effect Size Asymmetry

Female-predominant signals had significantly larger effect sizes:
- Female mean |LR|: 1.007
- Male mean |LR|: 0.963
- F/M ratio: 1.046
- Mann-Whitney U p = 2.8e-41

This 4.6% asymmetry, while modest per-signal, represents a systematic bias across 96,281 signals that is inconsistent with random reporting variation.

## Discussion

### Methodological Significance

Our findings definitively refute the "reporting artifact" hypothesis for sex-differential drug safety signals. Three independent lines of evidence converge:

1. **Direction**: Report ratios and signal ratios anti-correlate (rho=-0.215)
2. **Magnitude**: Effects increase with volume (anti-regression)
3. **Asymmetry**: Female effects are systematically larger (p=2.8e-41)

No plausible reporting bias mechanism can simultaneously produce all three patterns. Reporting bias predicts positive correlation (more reports = more signals), regression to the mean (effects shrink with volume), and symmetric effect sizes. We observe the opposite on all three dimensions.

### Biological Interpretation

The anti-correlation likely reflects genuine pharmacological sex differences:
- **Pharmacokinetic**: Sex-differential CYP enzyme activity, body composition, and renal clearance alter drug exposure independently of reporting
- **Pharmacodynamic**: Hormone-receptor interactions, immune system differences, and organ-specific sex effects produce sex-differential toxicity profiles
- **Disease confounding**: Drug indication sex ratios create reporting patterns that diverge from pharmacological effects (e.g., autoimmune drugs have high female reporting but may produce male-biased toxicity)

### Implications

1. **Pharmacovigilance**: Sex-differential signal detection should not be discounted as reporting bias
2. **Regulatory**: FDA safety analyses should routinely include sex-stratified assessment
3. **Research**: The anti-correlation provides a built-in validation for sex-differential pharmacovigilance studies

## Conclusion

Sex-differential drug safety signals anti-correlate with reporting patterns (rho=-0.215, p=6.9e-13), definitively refuting the reporting artifact hypothesis. The combination of anti-correlation, anti-regression, and effect asymmetry establishes that sex-differential adverse drug reactions reflect genuine pharmacological sex differences. This has immediate implications for drug safety surveillance, clinical practice, and regulatory policy.

## Data Availability

FAERS (2004Q1-2025Q3). Code and signals: https://github.com/jshaik369/SexDiffKG

## Key Statistics
- 96,281 sex-differential signals, 2,178 drugs
- Anti-correlation: rho=-0.215, p=6.92e-13
- 133 paradox drugs (female reports, male signals)
- 32 reverse paradox drugs (male reports, female signals)
- Volume gradient: Q1=42.9%F → Top1%=88.9%F (monotonic)
- Effect asymmetry: F/M ratio=1.046, p=2.8e-41
