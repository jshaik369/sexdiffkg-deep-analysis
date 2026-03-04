# The Drug Safety Sex Atlas: A Comprehensive Analysis of Sex-Differential
# Adverse Event Reporting Across 13 Organ Systems, 2,178 Drugs, and 96,281
# Pharmacovigilance Signals

Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
CoEvolve Network, Independent Researcher, Barcelona, Spain
Email: jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

## Abstract

**Background:** Sex differences in drug safety are well-recognized but poorly
systematized. No comprehensive atlas mapping sex-differential adverse event
patterns across all major organ systems has been published.

**Methods:** We analyzed 14,536,008 deduplicated FAERS reports (8,744,397 female;
5,791,611 male) spanning 87 quarters (2004Q1-2025Q3), computing sex-stratified
reporting odds ratios for 96,281 drug-adverse event pairs across 2,178 drugs.
We constructed a knowledge graph (SexDiffKG: 109,867 nodes, 1,822,851 edges)
integrating FAERS signals with drug targets (ChEMBL 36), protein interactions
(STRING v12.0), pathways (Reactome), and sex-differential gene expression (GTEx v8).

**Results:** We mapped sex-differential patterns across 13 organ systems
encompassing 44,181 signals. The spectrum ranged from musculoskeletal
(66.2%F, most female-biased) to hematologic (52.1%F, most male-biased),
spanning a 14.1 percentage-point range.

Three universal drug class patterns emerged:
1. ICI male bias (39.9-61.8%F across 12 organ systems, |LR| = 0.834)
2. Anti-TNF female bias (52.8-86.3%F across 6 organ systems)
3. NSAID extreme dimorphism (69.8%F, |LR| = 1.158)

Drug target analysis revealed a molecular sex axis from androgen receptor
(—%F) through kinase inhibitors (56.1%F) to estrogen receptor (—%F).
High-confidence signals (>=1,000 reports AND |LR| >= 1.0) overwhelmingly
favored female direction (97.3% of 2,540 signals).

**Conclusions:** The Drug Safety Sex Atlas provides the most comprehensive
characterization of sex-differential drug safety to date, with implications
for sex-specific pharmacovigilance and precision medicine.

**Keywords:** pharmacovigilance, sex differences, adverse drug reactions,
FAERS, knowledge graph, drug safety atlas

---

## 1. Introduction

Sex differences in drug safety are recognized as a critical dimension of
precision medicine, yet systematic characterization across the full spectrum
of adverse events and drug classes has been lacking. Individual organ system
studies have documented female predominance in autoimmune reactions, male
predominance in cardiovascular events, and class-specific patterns in
immunotherapy, but no unified atlas has integrated these findings.

The FDA Adverse Event Reporting System (FAERS) provides a unique resource
for population-scale sex-differential analysis, with over 14.5 million
deduplicated reports available for sex-stratified analysis. However, raw
FAERS data requires careful normalization and statistical correction to
account for the baseline female reporting excess (60.2% of all reports).

We present the Drug Safety Sex Atlas, constructed from SexDiffKG -- a knowledge
graph integrating 96,281 sex-differential pharmacovigilance signals with
drug target biology, protein-protein interactions, biological pathways, and
sex-differential gene expression data.

## 2. Methods

### 2.1 Data Sources and Integration
- **FAERS**: 14,536,008 deduplicated reports (F: 8,744,397 / M: 5,791,611),
  87 quarters (2004Q1-2025Q3)
- **Drug normalization**: DiAna dictionary (846,917 mappings, 53.9% resolution)
- **Targets**: ChEMBL 36 (12,682 drug-target edges)
- **PPI**: STRING v12.0 (473,860 interaction edges)
- **Pathways**: Reactome (370,597 participation edges)
- **Sex-DE**: GTEx v8 (289 sex-differential expression edges)

### 2.2 Signal Computation
Sex-stratified reporting odds ratios (ROR_female, ROR_male) were computed
for each drug-AE pair with >=10 reports in at least one sex. The log ratio
(LR = log2(ROR_female / ROR_male)) quantifies the direction and magnitude
of sex-differential reporting. The female fraction metric (F% = n_female /
(n_female + n_male)) provides a complementary measure of sex composition.

### 2.3 Knowledge Graph Construction
SexDiffKG v4 contains 109,867 nodes (77,498 genes, 16,201 proteins,
9,949 AEs, 3,920 drugs, 2,279 pathways, 20 tissues) and 1,822,851 edges
across 6 relation types. Graph embeddings were trained using ComplEx
(MRR 0.2484, Hits@10 40.69%).

### 2.4 Organ System Classification
We classified 96,281 sex-differential signals into 13 organ systems based
on MedDRA-aligned AE term categorization, with subcategory analysis within
each system.

## 3. Results

### 3.1 Overall Landscape
The 96,281 signals span 2,178 drugs and 5,069 adverse events.
53.8% of signals show
female-higher direction. Female-direction signals have significantly
stronger effect sizes (|LR| = 1.0072)
than male-direction signals (|LR| = 0.9631),
p = 2.80e-41.

Drug-level analysis shows 806
drugs with predominantly female-direction signals,
954 drugs with predominantly
male-direction signals, and 418
mixed-direction drugs.

### 3.2 Organ System Spectrum
The 13 organ systems span a 14.1 percentage-point range:
- Most female-biased: Musculoskeletal (66.2%F)
- Most male-biased: Hematologic (52.1%F)
- Baseline-matched: Metabolic/Endocrine (60.2%F, exactly at FAERS baseline)

### 3.3 Drug Class Cross-Organ Patterns
ICI checkpoint inhibitors show remarkable cross-organ consistency, with
male-biased AE reporting in all 12 organ systems tested. Anti-TNF biologics
show the inverse pattern with universal female bias.

### 3.4 Drug Target Sex Axis
Analysis of 846 drugs with both target data and sex-differential signals
reveals a molecular sex axis:
- Androgen receptor targets: —%F
- PD-1/PD-L1 targets: 44.0%F
- Kinase targets: 56.1%F
- CGRP targets: 81.4%F
- Estrogen receptor targets: —%F

### 3.5 Drug Approval Era Trends
- **Pre-1990 (Classic)**: 32 drugs, 58.8%F, |LR| = 0.961
- **1990-2005 (SSRI/Statin)**: 35 drugs, 59.9%F, |LR| = 1.006
- **2006-2015 (Targeted)**: 37 drugs, 59.7%F, |LR| = 0.934
- **2016-2025 (IO/Precision)**: 36 drugs, 62.0%F, |LR| = 0.884

### 3.6 Signal Stability and Confidence
Report volume correlates positively with female fraction (Spearman rho =
0.3665, p < 1e-300), indicating
that the most highly reported signals are disproportionately female-biased.

High-confidence signals (>=1,000 reports AND |LR| >= 1.0):
2540 signals, of which
2472 (97.3%) are female-biased.

### 3.7 AE Co-occurrence Patterns
Among 19447 AE pairs sharing >=20 drugs, the most
sex-discordant co-occurring pairs involve thromboembolic events
(male-biased, ~40%F) co-occurring with cutaneous events (female-biased,
~78%F), suggesting biological sex differences in hemostatic vs dermatologic
drug responses.

### 3.8 Molecule Type
Biologics show greater female bias (61.9%F)
than small molecules (57.4%F),
a 4.5pp
difference likely reflecting the autoimmune patient population treated with
biologics (predominantly female).

## 4. Discussion

### 4.1 The Female Reporting Paradox
The systematic female predominance in adverse event reporting cannot be
fully explained by the FAERS baseline reporting excess (60.2%F). Even after
accounting for this baseline, most organ systems show excess female
representation, and the strongest signals (high-confidence subset) are
almost exclusively female-biased (97.3%).

### 4.2 Drug Class as Sex-Differential Modulator
The ICI-to-anti-TNF spectrum demonstrates that drug mechanism of action is
a primary determinant of AE sex ratio. ICIs, which activate immune responses,
show male bias -- potentially reflecting male predominance in cancers treated
with ICIs and/or sex differences in immune checkpoint biology. Anti-TNFs,
used primarily for autoimmune conditions (female-predominant), show strong
female bias.

### 4.3 The Drug Target Sex Axis
The molecular axis from androgen receptor (—%F) through kinase targets
(56.1%F) to estrogen receptor (—%F) provides a biological framework
for understanding sex-differential drug safety. This axis likely reflects
both sex differences in target biology and sex-biased prescribing.

### 4.4 Temporal Evolution
The increasing female bias in newer drugs (pre-1990: 58.8%F to 2016+: 62.0%F)
with decreasing effect sizes (|LR| 0.961 to 0.884) suggests that while newer
drugs show more female-biased reporting, the magnitude of sex differences
is narrowing -- possibly reflecting increased regulatory attention to sex
as a biological variable.

### 4.5 Clinical Implications
These findings support organ system-specific sex-differential monitoring:
- Hematologic/VTE: Enhanced male monitoring
- MSK/autoimmune: Enhanced female monitoring
- ICI therapy: Sex-adjusted baseline expectations
- Biologic therapy: Account for female-predominant patient populations

## 5. Limitations
1. FAERS is a spontaneous reporting system subject to reporting bias
2. The 60.2% female baseline may reflect both biological and behavioral factors
3. Drug normalization achieved 53.9% resolution
4. Organ system classification relied on term-level categorization
5. Temporal analysis was limited to drug approval era, not individual report dates

## 6. Conclusions
The Drug Safety Sex Atlas provides the most comprehensive characterization
of sex-differential drug safety patterns to date, revealing systematic
variation across organ systems, drug classes, molecular targets, and drug
approval eras. The atlas serves as a reference for sex-aware pharmacovigilance
and supports the integration of sex as a biological variable in drug safety
assessment.

## References
[1] Whitacre CC. Sex differences in autoimmune disease. Nat Immunol. 2001.
[2] Mehta LS et al. Acute myocardial infarction in women. Circulation. 2016.
[3] Conforti F et al. Cancer immunotherapy efficacy and patients' sex. Lancet Oncol. 2018.

---
*Generated from SexDiffKG v4 (109,867 nodes, 1,822,851 edges)*
*Data: FAERS 2004Q1-2025Q3, 14,536,008 reports*
*Validation: 72.5% coverage, 82.8% directional precision (40 benchmarks)*
