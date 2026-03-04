# SexDiffKG v4 Statistical Significance Testing
**Date:** 2026-03-04 03:20 CET
**Script:** scripts/v4_09_statistical_tests.py
**Output:** results/analysis/statistical_tests_v4.json (354 KB)

## 1. Binomial Test: Female Bias in Signals
- 96,281 sex-differential signals: 51,771 F-biased (53.77%) vs 44,510 M-biased (46.23%)
- Binomial p = **3.51e-121** (two-sided, H0: 50/50)
- Cohen's h = 0.0755 (small effect size)
- CRITICAL INSIGHT: After correcting for 60.1% female FAERS reporting rate, the 53.8% F-biased proportion is LOWER than expected — signals under-represent female bias relative to reporting rates

## 2. Drug Class Tests: ALL 18/18 Significant (FDR < 0.05)
| Drug Class | F-biased | M-biased | Cohen's h | FDR q |
|-----------|----------|----------|-----------|-------|
| Opioids | 4,923 | 1,632 | 0.526 | 0.0 |
| Checkpoint Inhibitors | 732 | 280 | 0.463 | 8.73e-47 |
| Antipsychotics | 2,337 | 955 | 0.433 | 3.32e-131 |
| ACE Inhibitors | 1,607 | 691 | 0.410 | 8.41e-83 |
| Corticosteroids | 3,555 | 1,555 | 0.402 | 9.56e-176 |
| SSRIs (M-biased) | 854 | 1,183 | -0.165 | — |
| Anticonvulsants (M-biased) | 1,260 | 1,389 | -0.049 | — |
| Insulins (M-biased) | 529 | 602 | -0.065 | — |

## 3. Target Permutation Test: 0/74 Significant (Underpowered)
- None of 74 moderately biased targets reach significance individually
- Reason: too few drugs per target (3-14) for permutation test power
- Implication: Target-level bias is exploratory/hypothesis-generating
- The AGGREGATE pathway analysis reveals strong structure despite individual target weakness

## 4. Pathway Enrichment: 32 F-enriched + 47 M-enriched (FDR < 0.05)
**F-enriched (top 5):**
| Pathway | F/Total | FDR q |
|---------|---------|-------|
| Collagen biosynthesis & modifying enzymes | 25/25 | 4.42e-15 |
| Collagen chain trimerization | 25/25 | 4.42e-15 |
| Assembly of collagen fibrils | 27/29 | 2.34e-14 |
| Non-integrin membrane-ECM interactions | 27/29 | 2.34e-14 |
| ECM proteoglycans | 29/34 | 2.66e-13 |

**M-enriched (top 5):**
| Pathway | M/Total | FDR q |
|---------|---------|-------|
| Voltage gated K+ channels | 40/40 | 7.34e-21 |
| Assembly of NMDA receptors | 20/21 | 3.13e-08 |
| GLUT4 translocation | 16/16 | 2.48e-07 |
| HSP90 steroid hormone receptors | 17/18 | 5.45e-07 |
| NuMA recruitment to centrosomes | 15/15 | 5.45e-07 |

**Biological interpretation:**
- F-biased targets cluster in ECM/collagen pathways (connective tissue biology — known sex differences in collagen metabolism)
- M-biased targets cluster in ion channel/neurotransmitter pathways (voltage-gated K+ channels, NMDA receptors)

## 5. Distribution Tests
- KS test (F vs M |log_ratio|): D=0.0387, p=1.42e-31
- Mann-Whitney U: p=2.80e-41
- Chi-square across all 254,114 comparisons: chi2=547.59, p=4.22e-121
- Mean F |log_ratio| = 0.8976, mean M |log_ratio| = 0.8696 (small but significant difference)

## Manuscript Key Messages
1. Female predominance among signals is highly significant but with small effect size
2. All 18 drug classes tested show significant sex bias after FDR correction
3. Individual target significance is limited (underpowered) but pathway patterns are robust
4. 79 pathways show significant sex-biased enrichment (32 F + 47 M)
5. ECM/collagen pathways are uniquely F-biased; ion channels are uniquely M-biased
