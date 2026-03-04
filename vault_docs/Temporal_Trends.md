# Temporal Trend Analysis (2026-03-04)

## Data
- 14,536,008 FAERS reports, 52 quarters (2012Q4-2025Q3), 5 eras
- Results: results/analysis/temporal_trend_analysis.json

## KEY FINDING: 42.3% of Signals Reversed Direction Over Time

Of 27,233 drug-AE pairs with sufficient data in both Era 1 (2013-2015) and Era 5 (2023-2025):
- 11,510 (42.3%) REVERSED their sex-differential direction
- Mean absolute shift: 0.94 log2 units

This is a critical finding: nearly half of sex-differential safety signals are NOT temporally stable.

## Female Reporting Ratio Declining
| Period | F/M Ratio | %F |
|--------|-----------|-----|
| Early (2012-2014) | 1.678 | 62.6% |
| Late (2024-2025) | 1.474 | 59.5% |
| Change | -0.204 | -3.1pp |

## COVID-Era Inflection (2020-2022)
- Female % dropped from 61.9% to 55.3% during 2020Q3-2021Q3
- Massive COVID vaccine report influx skewed male
- Only 46.7% of drug-AE pairs female-biased in Era 4 (vs 51.3% in Era 1)
- Partially recovered post-2022 but not to pre-2020 levels

## Temporally Stable Signals (Most Robust)
- 418 AEs consistently female-biased across ALL 5 eras
- 609 AEs consistently male-biased across ALL 5 eras
- These represent the most reliable biological sex differences

## Largest Temporal Shifts
### Toward Female:
- Infliximab + Injury: +8.5 log2
- Minoxidil + Intentional misuse: +8.1 (women using off-label)
- Olaparib: +4.86 overall (expanded to female cancers)

### Toward Male:
- Atorvastatin + Type 2 DM: -8.9 log2
- Simvastatin + Cholesterol increased: -5.6

## Publication Target
- Clinical Pharmacology & Therapeutics (IF 6.3) or Pharmacoepidemiology & Drug Safety (IF 3.2)
- Paper: Temporal Instability of Sex-Differential Drug Safety Signals: A 13-Year FAERS Analysis
- UNIQUE: No published work has examined temporal stability of sex-diff PV signals
