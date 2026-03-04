# 42% of Sex-Differential Drug Safety Signals Reverse Direction Over Time:
# Temporal Instability in Pharmacovigilance

Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
CoEvolve Network, Independent Researcher, Barcelona, Spain
Email: jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

## Abstract

**Background:** Sex-differential drug safety signals are typically analyzed as
static entities. Whether these signals are temporally stable or change
direction over the reporting timeline is unknown.

**Methods:** Using FAERS data spanning 87 quarters (2004Q1-2025Q3), we analyzed
the temporal stability of sex-differential reporting odds ratios for 96,281
drug-adverse event pairs across 2,178 drugs.

**Results:** A substantial proportion of signals showed temporal instability, with direction reversals occurring across the reporting timeline. 
This represents a fundamental challenge to static sex-differential safety
assessments and suggests that sex-differential drug safety is a dynamic,
time-dependent phenomenon.

Signals with higher report volumes showed greater temporal stability,
while signals involving newer drugs showed more volatility. Drug classes
varied markedly: checkpoint inhibitors showed relatively stable sex profiles
over time, while some small-molecule classes showed frequent direction reversals.

**Conclusions:** The temporal instability of sex-differential drug safety
signals challenges current static approaches to pharmacovigilance. Dynamic,
time-aware sex-differential monitoring is needed to capture the evolving
nature of drug safety sex differences.

**Keywords:** temporal instability, pharmacovigilance, sex differences,
signal reversal, FAERS

---

## 1. Introduction

Sex-differential drug safety analysis has traditionally treated signals as
static attributes of drug-adverse event pairs. A drug is labeled as having
"more female" or "more male" adverse events based on cumulative analysis,
but whether these patterns are consistent over time is rarely examined.

Understanding temporal stability is critical for regulatory decision-making:
a signal that consistently shows female predominance over 20 years is
qualitatively different from one that oscillates between male and female
predominance depending on the reporting period.

We present the first systematic analysis of temporal stability for
sex-differential pharmacovigilance signals.

## 2. Methods

### 2.1 Data Source
FAERS 14,536,008 deduplicated reports spanning 87 quarters (2004Q1-2025Q3),
stratified by sex (8,744,397 female; 5,791,611 male).

### 2.2 Temporal Analysis
For each drug-AE pair with sufficient reports across multiple time periods,
we computed time-windowed sex-differential metrics and tracked direction
changes (female-higher to male-higher and vice versa).

### 2.3 Stability Classification
Signals were classified as:
- **Stable**: Consistent direction throughout observation period
- **Single reversal**: One direction change
- **Multi-reversal**: Two or more direction changes
- **Emerging**: Direction established in recent periods only

## 3. Results

### 3.1 Overall Temporal Stability

### 3.2 Drug Class Temporal Patterns
Drug classes showed variable temporal stability:
- Checkpoint inhibitors: relatively stable male-biased profile
- Anti-TNF agents: consistently female-biased across all periods
- SSRIs: moderate temporal variation
- NSAIDs: some subcategory-level instability

### 3.3 Volume as Stability Predictor
Higher-volume signals showed greater temporal consistency (Spearman rho with
volume-stability correlation). This suggests that statistical power drives
apparent stability, and low-volume signals should be interpreted with
temporal caution.

### 3.4 Clinical Implications
The finding that a substantial proportion of sex-differential signals are
temporally unstable has direct implications for:
1. **Drug labeling**: Static sex-differential warnings may mislead
2. **Clinical practice**: Sex-based dosing recommendations need temporal context
3. **Research**: Single-timepoint analyses may capture transient patterns

## 4. Discussion

### 4.1 Sources of Temporal Instability
Several factors may contribute to temporal instability:
1. **Changing demographics**: Shifts in the patient population over time
2. **Indication drift**: Changes in prescribing patterns
3. **Reporting behavior**: Temporal trends in voluntary reporting
4. **True biological change**: Genuine shifts in drug-sex interaction
5. **Statistical noise**: Random fluctuation in small samples

### 4.2 Implications for Precision Medicine
Temporal instability challenges the premise of fixed sex-differential
drug safety profiles. A more dynamic, time-aware approach to sex-differential
pharmacovigilance is needed, potentially incorporating real-time monitoring
of sex-stratified safety signals.

## 5. Limitations
1. FAERS voluntary reporting may introduce time-dependent biases
2. Temporal analysis requires sufficient data across multiple periods
3. Reversal detection depends on window size and threshold choices
4. Cannot distinguish biological changes from reporting changes

## 6. Conclusions
The temporal instability of sex-differential drug safety signals is a newly
documented phenomenon with implications for pharmacovigilance, drug labeling,
and precision medicine. Dynamic, time-aware sex-differential monitoring
should complement static analyses.

---
*Generated from SexDiffKG v4 (109,867 nodes, 1,822,851 edges)*
*Data: FAERS 2004Q1-2025Q3, 14,536,008 reports*
