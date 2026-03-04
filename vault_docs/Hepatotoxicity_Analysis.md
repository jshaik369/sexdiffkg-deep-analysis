# Hepatotoxicity Sex-Differential Analysis (2026-03-04)

## Data
- Source: `results/signals_v4/sex_differential_v4.parquet` (96,281 signals)
- Results: `results/analysis/hepatotoxicity_sex_diff.json`
- 2,792 hepatic signals, 106 AEs, 586 drugs

## Key Finding: 2:1 Female Predominance in Drug Hepatotoxicity

Overall: 66.7% female-higher (1,861 F / 931 M)

### Hepatic AE Sex Patterns
| AE | Signals | %F | Note |
|----|---------|-----|------|
| Hepatic cirrhosis | 64 | 88% | Strongest F bias |
| Hepatic function abnormal | 132 | 80% | |
| DILI | 135 | 78% | Critical safety |
| Hepatitis | 107 | 77% | |
| Cholestasis | 106 | 77% | |
| Hepatocellular injury | 104 | 76% | |
| Hepatic failure | 93 | 74% | Fatal outcome |
| Liver disorder | 137 | 67% | |
| Hepatic enzyme increased | 181 | 61% | |
| Hepatic steatosis | 70 | 43% | M-biased (fatty liver) |
| Hepatic fibrosis | 15 | 13% | Strongly M-biased |
| Autoimmune hepatitis | 18 | 28% | Paradoxically M-biased |

### DILI Focus
- 135 signals, 77.8% female-higher
- Strongest: OXYCODONE (logR=3.717), RANITIDINE (logR=2.765), RAMIPRIL (logR=2.575)

### Most Female-Biased Hepatotoxic Drugs
- Risperidone: 100% F (17 signals)
- Mycophenolate mofetil: 100% F (16)
- Tenofovir: 100% F (15)
- Nivolumab: 100% F (14)
- Quetiapine: 93% F (15)
- Ranitidine: 93% F (14)

### Most Male-Biased Hepatotoxic Drugs
- Levothyroxine: 94% M (17 signals)
- Metronidazole: 100% M (11)
- Ondansetron: 100% M (5)
- Amoxicillin/clavulanate: 100% M (6)

### Paradoxes
1. **Hepatic fibrosis** (13% F) and **autoimmune hepatitis** (28% F) are male-biased despite liver disease epidemiology
2. **Hepatic steatosis** male-biased — consistent with NAFLD epidemiology
3. Most severe endpoints (cirrhosis, failure, DILI) are strongly female-biased

## Publication Target
- Hepatology (IF 17.3) or J Hepatology (IF 25.7)
- Paper: Sex-Differential Drug-Induced Liver Injury: 586 Drugs from 14.5M FAERS Reports
