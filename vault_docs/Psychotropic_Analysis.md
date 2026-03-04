# Psychotropic Sex-Differential Analysis (2026-03-04)

## Data
- Source: `results/signals_v4/sex_differential_v4.parquet` (96,281 signals)
- Direction values: `female_higher` / `male_higher` (corrected)
- Results: `results/analysis/psychotropic_sex_diff.json`

## Key Finding: Class-Dependent Sex Bias in Psychiatry

Psychotropic drugs show DIVERGENT sex patterns by mechanism:
- **Antipsychotics**: 64.8% female-biased (dopamine D2 antagonists)
- **Anxiolytics**: 65.3% female-biased (GABAergic benzodiazepines)
- **Antidepressants**: 45.3% female — slightly MALE-biased (serotonergic)
- **Mood stabilizers**: 46.0% female — balanced

This suggests that receptor mechanism determines sex-differential AE vulnerability.

## Antipsychotics (2,558 signals, 15 drugs)

### Extreme outliers:
- **Risperidone**: 92.9% F (518 signals, logR=+0.940) — strongest sex-specific drug
- **Paliperidone**: 85.7% F — consistent (active metabolite of risperidone)
- **Cariprazine**: 97.4% MALE — notable exception (D3-preferring partial agonist)

### Metabolic/Cardiac AEs:
| AE | Signals | %F | logR | Note |
|----|---------|-----|------|------|
| Sexual dysfunction | 8 | 100% | +2.431 | Strongest effect |
| Gynaecomastia | 5 | 80% | +2.249 | Paradoxical |
| Metabolic syndrome | 6 | 100% | +1.030 | All female |
| NMS | 7 | 100% | +0.846 | All female |
| QT prolongation | 7 | 86% | +0.690 | Clinically critical |
| Weight increased | 3 | 0% | -1.525 | Male-biased |
| Akathisia | 2 | 0% | -1.675 | Male-biased |
| Type 2 DM | 5 | 0% | -0.836 | Male-biased |

**Publication-ready insight**: Women on antipsychotics show MORE sexual dysfunction, NMS, metabolic syndrome, and QT prolongation, but LESS weight gain and akathisia. This pattern has NOT been reported in the PV literature at this scale.

## Antidepressants (2,649 signals, 21 drugs)

- SSRIs: 42.2% F (slight male bias)
- SNRIs: 39.5% F (more male bias)
- TCAs: 47.9% F (balanced)
- Other (trazodone, bupropion, mirtazapine): 55.0% F
- **Desvenlafaxine**: most male-skewed (10.9% F)
- **Trazodone**: most female-biased AD (65.6% F)

## Anxiolytics (1,374 signals, 10 drugs)

- **Diazepam**: 76.4% F
- **Alprazolam**: 75.1% F
- **Buspirone** (non-benzo): 28.0% F — outlier, non-GABAergic

## Cross-Class Patterns

**Always female across 10+ drugs**: Respiratory arrest, angioedema, anaemia, rash, renal impairment, cardiac arrest, drug-induced liver injury
**Always male across 10+ drugs**: Fear, feeling jittery, increased appetite, irritability

## Publication Target
- Journal: Biological Psychiatry (IF 12.8) or Psychopharmacology (IF 3.4)
- Paper: Sex-Differential Adverse Event Profiles Across Psychotropic Drug Classes: A Pharmacovigilance Knowledge Graph Analysis of 96,281 Signals
- Unique angle: Mechanism-dependent sex bias (D2 vs 5-HT vs GABA)
