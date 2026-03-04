# Mechanism of Action (MOA) Clustering Analysis
**Date:** 2026-03-04
**Status:** COMPLETE

## Summary
846 drugs have BOTH ChEMBL protein targets AND sex-differential signals.
130 MOA clusters identified (proteins targeted by ≥3 drugs).

## Top MOA Clusters by Signal Volume

| Target | N Drugs | Signals | %Female |
|--------|---------|---------|---------|
| Glucocorticoid receptor | 30 | 3,786 | 66.4% |
| TNF | 4 | 2,382 | 45.0% |
| 5-HT receptor (1A) | 23 | 2,251 | 66.9% |
| COX | 21 | 1,867 | 54.6% |
| GABA-A receptor | 31 | 1,824 | 61.8% |
| D2 dopamine receptor | 18 | 1,610 | 70.2% |
| Mu-opioid receptor | 14 | 1,311 | 67.6% |
| Dihydrofolate reductase | 4 | 1,215 | 45.8% |
| 5-HT receptor (2A) | 12 | 1,178 | 73.3% |
| Sodium channel alpha | 16 | 1,174 | 43.5% |

## Most Female-Biased MOAs (≥20 signals)
1. **PPARα (peroxisome proliferator)**: 93.9% F, 3 drugs
2. **Histamine H2 receptor**: 85.5% F, 4 drugs
3. **IL-2 receptor**: 83.8% F, 3 drugs
4. **CD19**: 83.0% F, 6 drugs
5. **PD-L1**: 82.8% F, 3 drugs

## Most Male-Biased MOAs (≥20 signals)
1. **Progesterone receptor**: 3.1% F (96.9% M), 5 drugs
2. **CGRP receptor**: 4.7% F (95.3% M), 3 drugs
3. **Estrogen receptor**: 7.4% F (92.6% M), 3 drugs
4. **NTRK**: 10.7% F (89.3% M), 3 drugs
5. **PTH receptor**: 14.6% F (85.4% M), 3 drugs

## Most Heterogeneous MOAs (same target, opposite drug effects)
1. **Peptidyl-prolyl cis-trans isomerase**: 95.8pp spread across 5 drugs
2. **Glucocorticoid receptor**: 91.2pp spread across 17 drugs
3. **GABA-A receptor**: 87.5pp spread across 17 drugs
4. **Muscarinic AChR**: 85.7pp spread across 5 drugs
5. **Mu-opioid receptor**: 85.0pp spread across 12 drugs

## Key Insights
- **Hormone receptors show PARADOXICAL patterns**: Progesterone/estrogen receptor drugs = male-biased AEs
- **Immune checkpoint targets (PD-L1, CD19, IL-2R)**: Consistently female-biased (82-84%)
- **Glucocorticoid receptor**: Highest heterogeneity — MOA alone insufficient to predict sex bias
- **Same target ≠ same sex pattern**: Drug formulation, indication, and patient population matter
