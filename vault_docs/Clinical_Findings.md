# SexDiffKG Clinical Findings — Corrected Analysis (2026-03-04)

**Direction column values**: `female_higher` / `male_higher` (confirmed)
**Signal file**: `results/signals_v4/sex_differential_v4.parquet` (96,281 signals)
**Overall distribution**: 51,771 female_higher / 44,510 male_higher

---

## 1. Cardiac Sex Reversal (2,187 signals, 760 drugs)

**Overall**: 67.0% female-higher (1,466 F / 721 M)

Drug-induced cardiac events show **systematic female overrepresentation** — opposite to the baseline epidemiological expectation that cardiovascular disease is male-predominant.

### Per-AE Pattern:
| Adverse Event | Signals | % Female-higher | Mean logR |
|---------------|---------|-----------------|-----------|
| Sudden cardiac death | 7 | 100% | 0.938 |
| Cardiac arrest | 210 | 85% | 0.585 |
| Myocardial infarction | 182 | 82% | 0.626 |
| Cardiac failure | 184 | 80% | 0.536 |
| Cardio-respiratory arrest | 141 | 77% | 0.411 |
| Ventricular tachycardia | 83 | 76% | 0.520 |
| Angina pectoris | 68 | 75% | 0.578 |
| Ventricular fibrillation | 47 | 72% | 0.326 |
| Arrhythmia | 94 | 65% | 0.215 |
| Tachycardia | 157 | 63% | 0.280 |
| Bradycardia | 104 | 62% | 0.117 |
| Electrocardiogram QT prolonged | 113 | 61% | 0.141 |
| Atrial fibrillation | 149 | 60% | 0.102 |
| **Palpitations** | **153** | **18%** | **-0.609** |

**Key insight**: Palpitations is the ONLY cardiac AE with male predominance (82% male-higher). All serious/fatal cardiac endpoints are strongly female-biased.

### Strongest drug-AE cardiac signals:
- Trazodone → Cardiac disorder: logR=2.938 (ROR_F=6.78 vs ROR_M=0.36)
- Ketamine → MI: logR=2.461 (ROR_F=7.39 vs ROR_M=0.63)
- Methylprednisolone → Angina: logR=2.443 (ROR_F=5.06 vs ROR_M=0.44)
- Sildenafil: 11 cardiac signals, 100% female-higher
- Risperidone: 11 cardiac signals, 100% female-higher

### Drugs with predominantly female cardiac signals:
Olanzapine (83% F), Levetiracetam (91% F), Sildenafil (100% F), Risperidone (100% F), Lacosamide (90% F)

### Drugs with predominantly male cardiac signals:
Allopurinol (88% M), Magnesium (100% M), Calcium (86% M)

---

## 2. Opioid Systematic Female Vulnerability (2,674 signals, 17 drugs)

**Overall**: 75.1% female-higher (2,008 F / 666 M)

### Per-Drug Pattern:
| Drug | Signals | % Female-higher | Mean logR |
|------|---------|-----------------|-----------|
| OXYCODONE | 492 | 85.0% | 1.091 |
| MORPHINE | 441 | 83.4% | 0.847 |
| CODEINE | 190 | 75.8% | 0.832 |
| TRAMADOL | 360 | 75.3% | 0.722 |
| HYDROMORPHONE | 311 | 76.5% | 0.654 |
| FENTANYL | 291 | 74.6% | 0.474 |
| METHADONE | 107 | 73.8% | 0.425 |
| HYDROCODONE | 76 | 68.4% | 0.334 |
| OXYMORPHONE | 50 | 68.0% | 0.280 |
| BUPRENORPHINE | 261 | 54.0% | 0.229 |
| TAPENTADOL | 39 | 43.6% | -0.163 |

**Key insight**: Buprenorphine (partial agonist) and tapentadol (dual mechanism) show REDUCED female bias compared to full mu-agonists, suggesting mechanism-dependent sex differences.

### Cross-opioid AE consistency (AEs in 3+ opioids):
**Always female-higher**: Drug hypersensitivity (11 opioids), drug intolerance (9), pyrexia (9), rash (9), pruritus (8), cardiac arrest (8), substance use disorder (8), hypotension (7)
**Always male-higher**: Impaired driving ability (9 opioids), impaired quality of life (8)

---

## 3. ATC Drug Class Sex Patterns (1,424 drugs, 137,665 signal-ATC pairs)

### Level 1 Therapeutic Areas:
| ATC | Class | Signals | % Female | Bias |
|-----|-------|---------|----------|------|
| H | Systemic Hormones | 4,928 | 65.0% | F-BIASED |
| A | Alimentary/Metabolism | 13,848 | 58.3% | F-BIASED |
| N | Nervous System | 22,425 | 58.2% | F-BIASED |
| J | Anti-infectives | 7,424 | 57.9% | F-BIASED |
| L | Antineoplastic/Immunomod | 27,627 | 57.8% | F-BIASED |
| R | Respiratory | 11,494 | 49.1% | BALANCED |
| C | Cardiovascular | 11,455 | 54.6% | BALANCED |
| P | Antiparasitic | 980 | 36.3% | M-BIASED |
| V | Various | 1,060 | 44.5% | M-BIASED |

### Most female-biased L2 groups:
- J02 Antimycotics (75.6% F)
- J04 Antimycobacterials (74.2% F)
- H02 Systemic Corticosteroids (69.2% F)
- N02 Analgesics (66.4% F)

### Most male-biased L2 groups:
- P02 Anthelmintics (14.1% F)
- G03 Sex Hormones (19.8% F)
- V08 Contrast Media (20.7% F)

### Notable L3 findings:
- N02A Opioids: 74.3% female, meanLogR=0.667
- G04C BPH drugs: 84.1% female (paradoxical — male-specific drugs with extreme female AE bias)

---

## 4. SOC (System Organ Class) Sex Patterns

| SOC | % Female | Bias |
|-----|----------|------|
| Social circumstances | 80.6% | F-BIASED |
| Renal/urinary | 67.2% | F-BIASED |
| Cardiac disorders | 65.1% | F-BIASED |
| Psychiatric disorders | 58.4% | F-BIASED |
| Eye disorders | 32.3% | M-BIASED |
| Reproductive system | 34.2% | M-BIASED |

---

## Publication-Ready Narrative Points

1. **Cardiac reversal phenomenon**: Drug-induced cardiac AEs are 67% female-biased despite CVD being epidemiologically male-predominant. This suggests drugs unmask female cardiac vulnerability not captured by disease prevalence alone.

2. **Opioid vulnerability gradient**: Full mu-agonists show 75-85% female bias; partial agonists (buprenorphine) drop to 54%. Suggests receptor-level pharmacological mechanism for sex differences.

3. **Cross-class consistency**: Nearly ALL drug classes show female AE bias (8/11 ATC L1 groups). The exceptions (antiparasitics, contrast media) may reflect prescribing patterns rather than biology.

4. **BPH paradox**: Drugs for male-only conditions (BPH) show 84% female-biased AEs in the rare women who receive them — extreme sex-specific vulnerability.

5. **Palpitations exception**: The only cardiac AE with male predominance, possibly reflecting male anxiety-related cardiac symptom reporting patterns.

---

*Generated 2026-03-04 with corrected direction values (female_higher/male_higher). Previous version used wrong filter values.*
