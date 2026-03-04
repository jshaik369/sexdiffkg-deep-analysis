# SexDiffKG v4 Geographic Variation Analysis
**Date:** 2026-03-04 03:29 CET
**Script:** scripts/v4_12_geographic_variation.py
**Output:** results/analysis/geographic_variation_v4.json

## Country-Level Sex-Differential Signals

| Country | Reports | F Reporters | Strong Signals | % F-Biased | Mean log_ratio |
|---------|---------|-------------|----------------|------------|----------------|
| **JP** | 412,316 | **47.0%** (less F) | 2,586 | **57.4%** | **+0.041** |
| ES | 117,420 | 52.1% | 1,011 | 52.4% | +0.016 |
| CN | 160,623 | 49.6% | 1,229 | 51.0% | +0.001 |
| IN | 62,500 | 45.6% | 276 | 51.1% | +0.015 |
| **US** | 9,934,811 | 62.5% (most F) | 31,688 | **50.8%** | +0.002 |
| FR | 416,996 | 52.8% | 6,328 | 49.1% | -0.009 |
| AU | 104,498 | 50.4% | 1,139 | 48.5% | -0.019 |
| DE | 292,428 | 55.4% | 4,971 | 47.1% | -0.030 |
| IT | 201,710 | 54.2% | 2,175 | 47.1% | -0.019 |
| NL | 96,869 | 50.4% | 688 | 39.1% | -0.090 |
| GB | 491,181 | 56.1% | 6,974 | 39.2% | -0.112 |
| CO | 58,100 | 57.0% | 301 | 35.5% | -0.101 |
| **CA** | 573,932 | **60.3%** | 23,344 | **34.2%** | **-0.354** |
| **BR** | 117,585 | **64.9%** (most F) | 627 | **30.0%** | **-0.120** |

## KEY FINDING: Reporting Sex Ratio Does NOT Predict Signal Sex Bias

Japan: 47% female reporters but **57.4% female-biased signals** (highest F-bias)
Brazil: 65% female reporters but **30.0% female-biased signals** (lowest F-bias)
Canada: 60% female reporters but **34.2% female-biased signals**

This demonstrates that sex-differential ADR signals are NOT an artifact of female over-reporting. Countries with more female reporters do NOT automatically produce more female-biased signals.

## Cross-Country Correlations (vs US)

| Comparison | Pearson r | n (shared pairs) |
|-----------|-----------|-----------------|
| US vs CO | 0.347 | 924 |
| US vs (unspecified) | 0.391 | 6,645 |
| US vs BR | 0.332 | 2,180 |
| US vs IN | 0.285 | 724 |
| US vs AU | 0.259 | 2,310 |
| US vs JP | **0.204** | 7,056 |
| US vs NL | 0.191 | 1,633 |
| US vs FR | 0.166 | 9,595 |
| US vs GB | 0.163 | 11,833 |
| US vs CN | 0.150 | 2,762 |
| US vs DE | 0.145 | 8,944 |
| US vs CA | **0.143** | 20,644 |
| US vs ES | 0.129 | 2,322 |
| US vs IT | 0.119 | 4,594 |

**Weak cross-country correlations** (r = 0.12-0.39) suggest substantial geographic variation in sex-differential signal patterns. This may reflect:
1. Different prescribing practices by country
2. Different healthcare access patterns by sex
3. Different ADR reporting cultures
4. Different drug market compositions
5. Genuine population-level pharmacogenomic variation

## Manuscript Implications

1. **Reporting bias control:** Japan result directly counters the criticism that female bias in FAERS signals is simply an artifact of female over-reporting
2. **Cross-country validation:** Low correlations mean country-specific analyses needed for local pharmacovigilance
3. **Limitation:** FAERS is predominantly US-reported (68% of reports) — signals may not generalize to all populations
4. **Potential Figure:** World map colored by % F-biased, or scatter plot of F reporter % vs F signal %
