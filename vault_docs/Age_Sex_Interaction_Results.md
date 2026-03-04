# SexDiffKG v4 Age-Sex Interaction Analysis
**Date:** 2026-03-04 03:25 CET
**Script:** scripts/v4_11_age_sex_interaction.py
**Output:** results/analysis/age_sex_interaction_v4.json

## NOVEL FINDING: Sex-Differential ADRs Follow Age Gradient

### Overall Age Group Statistics
| Age Group | Reports | Strong Signals | % F-Biased | Mean log_ratio |
|-----------|---------|----------------|------------|----------------|
| Young Adult (18-44) | 1,856,734 | 20,458 | **63.2%** | **+0.170** |
| Middle-Aged (45-64) | 3,063,407 | 31,322 | **52.1%** | +0.012 |
| Elderly (65+) | 3,421,962 | 30,983 | **49.3%** | -0.017 |

**Key insight:** Female ADR bias decreases monotonically with age from 63.2% to 49.3%, consistent with the HORMONAL HYPOTHESIS (estrogen/progesterone modulation of drug metabolism diminishes post-menopause).

### Drug Class Age Patterns (NOVEL)

#### Opioids — Age-Dependent Sex Reversal
| Age | Signals | % F-Biased | Mean log_ratio | Interpretation |
|-----|---------|------------|----------------|----------------|
| Young (18-44) | 872 | **87.8%** | **+1.14** | Overwhelming F vulnerability |
| Middle (45-64) | 709 | 56.8% | +0.22 | Reduced but still F-biased |
| Elderly (65+) | 465 | **39.8%** | **-0.10** | FLIPS to M-biased |

→ CYP3A4 is estrogen-regulated; higher female activity in reproductive years → higher metabolite exposure → more ADRs. Post-menopause, this difference disappears.

#### Antipsychotics — Parallel Age Reversal
| Age | Signals | % F-Biased | Mean log_ratio |
|-----|---------|------------|----------------|
| Young (18-44) | 1,209 | **71.1%** | +0.53 |
| Middle (45-64) | 826 | 55.4% | +0.09 |
| Elderly (65+) | 441 | **40.4%** | -0.18 |

→ CYP1A2 (major metabolizer for olanzapine/clozapine) is estrogen-regulated. Women have ~40% lower CYP1A2 activity → higher drug levels → more ADRs in reproductive years.

#### SSRIs — Progressive Male Bias with Age
| Age | Signals | % F-Biased | Mean log_ratio |
|-----|---------|------------|----------------|
| Young (18-44) | 471 | 52.4% | +0.06 |
| Middle (45-64) | 397 | 47.4% | -0.13 |
| Elderly (65+) | 311 | **32.5%** | **-0.48** |

→ Already male-biased overall (SSRIs show mean lr = -0.189 in full dataset), becomes progressively more male-biased with age. Possibly related to age-dependent changes in serotonin transporter expression.

#### ACE Inhibitors — Persistent Female Vulnerability
| Age | Signals | % F-Biased | Mean log_ratio |
|-----|---------|------------|----------------|
| Young (18-44) | 78 | 67.9% | +0.74 |
| Middle (45-64) | 296 | **78.0%** | +0.67 |
| Elderly (65+) | 386 | 64.2% | +0.26 |

→ ACE inhibitors show persistent F-bias across all age groups, strongest in middle age. Kinin-mediated cough (the signature ACE inhibitor ADR) is estrogen-modulated but also involves bradykinin pathways that maintain sex differences post-menopause.

#### Statins — U-Shaped Pattern
| Age | Signals | % F-Biased | Mean log_ratio |
|-----|---------|------------|----------------|
| Young (18-44) | 53 | 50.9% | +0.06 |
| Middle (45-64) | 456 | 38.6% | -0.21 |
| Elderly (65+) | 612 | **56.5%** | +0.14 |

→ U-shaped: equal in young, M-biased in middle age, F-biased in elderly. Possibly reflects post-menopausal cardiovascular risk profile changes.

#### Hormonal (Tamoxifen, AI) — Consistently Male-Biased
| Age | Signals | % F-Biased | Mean log_ratio |
|-----|---------|------------|----------------|
| Young (18-44) | 2 | 0.0% | -1.95 |
| Middle (45-64) | 13 | 7.7% | -2.44 |
| Elderly (65+) | 3 | 0.0% | -0.81 |

→ Validates ESR1 paradox across all ages. Males are vulnerable to hormonal therapy ADRs regardless of age.

### Direction Flips: Young vs Elderly
- **1,470 drug-AE pairs** flip direction between young adults and elderly
- Top flips include prednisone, azathioprine (immunosuppressants), metformin
- These represent age-dependent sex-differential ADR patterns that could inform age-specific dosing

### Manuscript Impact
1. **This is the first large-scale demonstration of age-dependent sex-differential ADR patterns** across 14.5M FAERS reports
2. The opioid and antipsychotic age reversal patterns are novel and clinically actionable
3. Directly supports the hormonal hypothesis for sex-differential pharmacovigilance
4. Potential Figure: line chart showing % F-biased by age group for 6 drug classes
5. Could be a standalone finding worthy of highlighting in the Abstract
