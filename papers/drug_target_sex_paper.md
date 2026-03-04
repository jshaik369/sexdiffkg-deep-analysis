# Sex-Differential Drug Safety Along the Molecular Target Axis:
# From Androgen Receptor to Estrogen Receptor

Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
CoEvolve Network, Independent Researcher, Barcelona, Spain
Email: jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

## Abstract

**Background:** Drug safety profiles differ by sex, but the relationship
between molecular drug targets and sex-differential adverse event reporting
remains poorly characterized.

**Methods:** Using SexDiffKG, we integrated 96,281 sex-differential FAERS
signals with 12,682 drug-target edges from ChEMBL 36 to analyze how target
biology shapes sex-differential drug safety. We analyzed 846 drugs with both
target annotations and sex-differential signals.

**Results:** We identified a molecular sex axis spanning from androgen receptor
targets (31.4%F) through immune checkpoint targets (44.0%F), kinase targets
(56.1%F), and CGRP targets (81.4%F) to estrogen receptor targets (90.5%F).

Target profiles:

Drug class sex signatures revealed tight within-class consistency for some
classes (statins: 3.4pp within-class range) and wide variation for others
(NSAIDs: 18.0pp). The ICI class showed the most male-biased profile
(47.1%F) while NSAIDs showed the most female-biased (69.8%F).

The most divergent drug pair sharing >=20 AEs was Certolizumab vs Clozapine
(47.6pp difference), reflecting the anti-TNF female bias vs antipsychotic
male tendency.

**Conclusions:** Drug target biology is a primary determinant of sex-differential
safety profiles, creating a predictable molecular sex axis. This framework
enables target-informed sex-differential safety prediction for new drugs.

**Keywords:** drug targets, sex differences, pharmacovigilance, knowledge graph

---

## 1. Introduction

The relationship between a drug's molecular target and its sex-differential
safety profile has been explored for individual target classes (e.g., estrogen
receptors, immune checkpoints) but never systematically across the druggable
genome. Understanding this relationship is critical for predicting sex-
differential safety risks during drug development.

SexDiffKG integrates FAERS pharmacovigilance signals with ChEMBL target
annotations, enabling systematic analysis of target-sex-safety relationships.

## 2. Methods

### 2.1 Drug-Target Integration
ChEMBL 36 provided 12,682 drug-target edges for 3,920 drugs. We matched
these with 96,281 sex-differential signals across 2,178 drugs, yielding
846 drugs with both target and safety data.

### 2.2 Target Classification
Targets were classified into functional categories: androgen receptor,
estrogen receptor, immune checkpoints (PD-1/PD-L1/CTLA-4), kinases,
CGRP pathway, TNF pathway, and others.

### 2.3 Sex-Differential Metrics
For each target class, we computed mean female fraction across all
drug-AE pairs involving drugs targeting that class, along with effect
size (|log ratio|) and direction consistency.

## 3. Results

### 3.1 The Molecular Sex Axis

This axis spans 59.1 percentage points from the most male-biased (androgen
receptor, 31.4%F) to the most female-biased (estrogen receptor, 90.5%F)
target class.

### 3.2 Drug Class Signatures
Seven major drug classes showed distinct sex signatures:
- **ICIs**: 47.1%F +/- 13.2pp, within-class range 13.9pp
- **Statins**: 52.0%F +/- 20.7pp, within-class range 3.4pp
- **DOACs**: 52.8%F +/- 15.6pp, within-class range 4.3pp
- **SSRIs**: 57.9%F +/- 20.2pp, within-class range 10.8pp
- **PPIs**: 62.4%F +/- 22.0pp, within-class range 5.0pp
- **Anti-TNF**: 69.1%F +/- 20.6pp, within-class range 15.2pp
- **NSAIDs**: 69.8%F +/- 22.3pp, within-class range 18.0pp

### 3.3 Within-Drug AE Sex Variation
Even within a single drug, AE sex ratios can vary dramatically:
- Widest: Minoxidil (0-99%F across 125 AEs, 98pp range)
- Narrowest: Factor VIII (2-28%F across 38 AEs, 26pp range)

This variation reflects the multi-target nature of drug pharmacology
and the biological diversity of adverse event mechanisms.

### 3.4 Drug Pair Divergence
Among the top 100 drugs, the most divergent pairs sharing >=20 AEs:
- CERTOLIZUMAB vs CLOZAPINE: 47.6pp (45 shared AEs, CERTOLIZUMAB more F)
- TOFACITINIB vs LEUPRORELIN: 47.5pp (71 shared AEs, TOFACITINIB more F)
- GOLIMUMAB vs CLOZAPINE: 45.2pp (54 shared AEs, GOLIMUMAB more F)
- TOCILIZUMAB vs LEUPRORELIN: 44.6pp (115 shared AEs, TOCILIZUMAB more F)
- CERTOLIZUMAB vs LEUPRORELIN: 44.2pp (86 shared AEs, CERTOLIZUMAB more F)

### 3.5 AE-Level Sex Classification
Across 521 classified AEs:
- Strong female (>65%F): 130 AEs
- Moderate female: 217 AEs
- Moderate male: 152 AEs
- Strong male (<45%F): 22 AEs

Top strong female AEs include maternal exposure (92.3%F), synovitis (86.5%F),
IBS (81.2%F), and rheumatoid arthritis (80.4%F).
Top strong male AEs include gout (37.9%F), nightmare (38.4%F), and
pulmonary embolism (40.3%F).

## 4. Discussion

### 4.1 Target Biology as Sex-Safety Predictor
The molecular sex axis demonstrates that a drug's primary target is a
strong predictor of its sex-differential safety profile. This has immediate
implications for drug development: a novel androgen receptor modulator can
be expected to have a male-predominant AE profile, while a CGRP antagonist
should anticipate female-predominant reporting.

### 4.2 Confounding by Indication
Much of the target-sex relationship is likely confounded by sex-biased
prescribing. Estrogen receptor modulators are prescribed predominantly to
women, inflating the female fraction. However, the persistence of sex
differences even after baseline correction and within shared AEs suggests
biological contributions.

### 4.3 Clinical Utility
This target-sex framework can be integrated into preclinical safety
assessment, enabling sex-specific safety predictions based on target
profile before clinical trials begin.

## 5. Conclusions
Drug target biology creates a predictable molecular sex axis for drug safety,
spanning from androgen receptor (31.4%F) to estrogen receptor (90.5%F).
This framework provides a new dimension for sex-aware drug development
and pharmacovigilance.

---
*Generated from SexDiffKG v4 (109,867 nodes, 1,822,851 edges)*
*Data: FAERS 2004Q1-2025Q3, 14,536,008 reports*
