# High-Confidence Sex-Differential Signals (2026-03-04)

## Data
- Source: results/signals_v4/sex_differential_v4.parquet (96,281 signals)
- Results: results/analysis/high_confidence_signals.json

## Report Count Distribution
| Metric | Value |
|--------|-------|
| Mean reports/signal | 251 |
| Median reports/signal | 72 |
| Maximum | 55,041 |
| >1,000 reports | 4,470 signals |
| >10,000 reports | 89 signals |

## High-Confidence Signals (>1000 reports AND |logR|>0.5): 4,470

## Top Composite Score Signals (Volume x Effect)
1. Minoxidil -> Adverse drug reaction: composite=25.33 (8,460 reports, logR=-6.448, male baldness)
2. Oxycodone -> Infusion related reaction: composite=18.71 (2,533 reports, logR=5.496, female)
3. Adalimumab -> Pemphigus: composite=18.17 (6,782 reports, female autoimmune)
4. Methotrexate -> Glossodynia: composite=17.97 (6,118 reports, female burning mouth)

## Highest-Volume Drug-AE Pairs
- Oxycodone -> Pain: 55,041 reports (male-higher, paradoxical pain)
- Ranitidine -> Prostate cancer: 54,130 reports (denominator artifact)
- Adapalene -> Drug ineffective: 43,316 reports (male acne treatment failure)

## Top Drugs by Total Reports
1. Methotrexate: 686K reports, neutral bias
2. Rituximab: 684K reports, 67% F
3. Prednisone: 629K reports, 70% F
4. Oxycodone: 366K reports, 85% F

## Key Insight: Denominator Effects
Several top signals are artifacts of sex-skewed disease populations (breast cancer, prostate conditions, male-pattern baldness). True pharmacological sex differences are best identified by the composite score which balances volume and effect size.
