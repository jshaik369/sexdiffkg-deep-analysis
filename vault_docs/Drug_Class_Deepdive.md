# Drug Class Sex-Differential Deep-Dive

**Generated:** 2026-03-04 08:09
**Source:** 96,281 pharmacovigilance signals from 2,178 drugs
**Classes analyzed:** 10 ATC Level 2 classes covering 526 drugs and 36,690 signals

## Executive Summary

- **Most female-biased class:** Analgesics (65.3% female-higher signals)
- **Most male-biased class:** Lipid Modifying Agents (Statins) (57.5% male-higher signals)
- **Most heterogeneous class:** Anti-inflammatory / NSAIDs (CV = 0.83)
- **Total paradoxical drugs:** 99 (drugs bucking their class trend)

## Class Summary Table

| ATC | Class | Drugs | Signals | %Female | %Male | Trend | Mean LR | Within-Class | Paradoxical |
|-----|-------|------:|--------:|--------:|------:|-------|--------:|--------------|------------:|
| C10 | Lipid Modifying Agents (Statins) | 23 | 1,493 | 42.5% | 57.5% | male_higher | -0.1153 | High heterogeneity | 1 |
| M01 | Anti-inflammatory / NSAIDs | 25 | 1,825 | 54.4% | 45.6% | female_higher | +0.2146 | High heterogeneity | 9 |
| J01 | Antibacterials (Antibiotics) | 73 | 3,738 | 49.5% | 50.5% | male_higher | -0.0133 | High heterogeneity | 19 |
| C09 | Renin-Angiotensin Agents (ACEi/ARBs) | 17 | 1,651 | 61.5% | 38.5% | female_higher | +0.3271 | Moderate heterogeneity | 2 |
| A10 | Antidiabetics | 30 | 1,821 | 52.8% | 47.2% | female_higher | +0.0666 | High heterogeneity | 6 |
| B01 | Antithrombotic Agents (Anticoagulants) | 34 | 2,705 | 65.1% | 34.9% | female_higher | +0.2491 | Moderate heterogeneity | 6 |
| N06 | Psychoanaleptics (Antidepressants) | 53 | 3,485 | 46.6% | 53.4% | male_higher | -0.0508 | High heterogeneity | 8 |
| L01 | Antineoplastic Agents | 218 | 14,016 | 65.1% | 34.9% | female_higher | +0.2857 | Moderate heterogeneity | 28 |
| N02 | Analgesics | 41 | 4,953 | 65.3% | 34.7% | female_higher | +0.4243 | High heterogeneity | 17 |
| C07 | Beta Blocking Agents | 12 | 1,003 | 52.7% | 47.3% | female_higher | +0.0516 | High heterogeneity | 3 |

---
## C10: Lipid Modifying Agents (Statins)

**23 drugs | 1,493 signals | Class trend: male_higher**
- Female-higher: 635 (42.5%)
- Male-higher: 858 (57.5%)
- Mean log-ratio: -0.1153 | Median: -0.5463 | SD: 1.0073
- Within-class variation: High heterogeneity (CV=0.742, range 0.0%--62.5%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| ROSUVASTATIN | Creatinine renal clearance decreased | +3.499 | 137.61 | 4.16 | 368 | 11 |
| ATORVASTATIN | Gynaecomastia | +3.323 | 23.35 | 0.84 | 11 | 136 |
| ATORVASTATIN | Type 2 diabetes mellitus | +3.318 | 193.41 | 7.00 | 6,693 | 198 |
| ATORVASTATIN | Macular degeneration | +3.181 | 21.66 | 0.90 | 563 | 10 |
| ROSUVASTATIN | Orthostatic hypotension | +3.089 | 38.46 | 1.75 | 436 | 31 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| ROSUVASTATIN | Micturition urgency | -3.089 | 0.89 | 19.51 | 10 | 173 |
| ROSUVASTATIN | Sensation of foreign body | -3.055 | 1.14 | 24.29 | 11 | 91 |
| SIMVASTATIN | Ascites | -2.974 | 0.62 | 12.04 | 10 | 257 |
| ROSUVASTATIN | Systemic lupus erythematosus | -2.887 | 0.80 | 14.36 | 43 | 86 |
| COLESEVELAM | Dyspnoea | -2.798 | 0.26 | 4.30 | 14 | 92 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Hepatic enzyme increased | 6 | 100% | male_higher | -0.7798 |
| Discomfort | 5 | 100% | male_higher | -1.0514 |
| Tendon rupture | 5 | 100% | male_higher | -1.0025 |
| Chest discomfort | 5 | 100% | male_higher | -0.9394 |
| Paraesthesia | 5 | 100% | male_higher | -0.6493 |
| Wheezing | 4 | 100% | male_higher | -1.7258 |
| Muscle injury | 4 | 100% | male_higher | -1.2817 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| ATORVASTATIN | 388 | 46.4% | +0.0268 | HMG CoA reductase inhibitors |
| ROSUVASTATIN | 337 | 49.0% | -0.0486 | HMG CoA reductase inhibitors |
| SIMVASTATIN | 261 | 52.5% | +0.0447 | HMG CoA reductase inhibitors |
| EVOLOCUMAB | 131 | 19.1% | -0.4877 | Other lipid modifying agents |
| EZETIMIBE | 94 | 40.4% | -0.1707 | Other lipid modifying agents |
| PRAVASTATIN | 67 | 37.3% | -0.2267 | HMG CoA reductase inhibitors |
| FENOFIBRATE | 57 | 40.4% | -0.1420 | Fibrates |
| ALIROCUMAB | 53 | 17.0% | -0.5852 | Other lipid modifying agents |
| INCLISIRAN | 26 | 34.6% | -0.2612 | Other lipid modifying agents |
| FLUVASTATIN | 21 | 42.9% | -0.2003 | HMG CoA reductase inhibitors |
| LOMITAPIDE | 13 | 15.4% | -0.6707 | Other lipid modifying agents |
| COLESTYRAMINE | 11 | 36.4% | -0.3963 | Bile acid sequestrants |
| LOVASTATIN | 8 | 62.5% | +0.1650 | HMG CoA reductase inhibitors |
| COLESEVELAM | 6 | 16.7% | -1.3714 | Bile acid sequestrants |
| GEMFIBROZIL | 4 | 0.0% | -0.9302 | Fibrates |
| BEMPEDOIC ACID | 3 | 33.3% | -0.2041 | Other lipid modifying agents |
| PITAVASTATIN | 3 | 33.3% | -0.2729 | HMG CoA reductase inhibitors |
| COLESTIPOL | 3 | 0.0% | -1.3586 | Bile acid sequestrants |
| CHOLESTYRAMINE | 2 | 50.0% | -0.0225 | Bile acid sequestrants |
| COLESTIPOL HYDROCHLORIDE | 2 | 0.0% | -0.7363 | Bile acid sequestrants |
| *...and 3 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| LOVASTATIN | 8 | 62.5% | +0.1650 | HMG CoA reductase inhibitors | 62.5% female-biased vs class 42.5% |

---
## M01: Anti-inflammatory / NSAIDs

**25 drugs | 1,825 signals | Class trend: female_higher**
- Female-higher: 992 (54.4%)
- Male-higher: 833 (45.6%)
- Mean log-ratio: +0.2146 | Median: +0.5636 | SD: 1.3547
- Within-class variation: High heterogeneity (CV=0.83, range 0.0%--100.0%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| DICLOFENAC | Injury | +4.234 | 20.83 | 0.30 | 2,243 | 14 |
| DICLOFENAC | Delirium | +4.156 | 18.10 | 0.28 | 829 | 11 |
| DICLOFENAC | Wound | +3.987 | 92.66 | 1.72 | 4,390 | 34 |
| DICLOFENAC | Irritable bowel syndrome | +3.942 | 67.46 | 1.31 | 2,731 | 12 |
| DICLOFENAC | Type 2 diabetes mellitus | +3.930 | 44.22 | 0.87 | 2,593 | 15 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| SODIUM AUROTHIOMALATE | Pulmonary thrombosis | -4.136 | 10.85 | 678.61 | 20 | 151 |
| SODIUM AUROTHIOMALATE | Apparent death | -4.092 | 34.96 | 2093.37 | 20 | 150 |
| SODIUM AUROTHIOMALATE | Pulmonary embolism | -4.051 | 1.67 | 95.80 | 21 | 156 |
| SODIUM AUROTHIOMALATE | Red blood cell sedimentation rate abnormal | -3.899 | 50.53 | 2494.93 | 30 | 63 |
| CELECOXIB | Nightmare | -3.794 | 0.50 | 22.22 | 19 | 265 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Hypertension | 9 | 100% | female_higher | +1.3707 |
| Fatigue | 8 | 100% | female_higher | +1.3306 |
| Gastrointestinal disorder | 7 | 100% | female_higher | +1.2564 |
| Diarrhoea | 7 | 100% | female_higher | +1.0896 |
| Ankylosing spondylitis | 7 | 100% | male_higher | -0.8469 |
| Headache | 6 | 100% | female_higher | +1.1121 |
| Delirium | 5 | 100% | female_higher | +2.5263 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| DICLOFENAC | 401 | 50.6% | +0.3193 | Acetic acid derivatives and related substances |
| IBUPROFEN | 372 | 59.4% | +0.1692 | Other cardiac preparations |
| NAPROXEN | 331 | 54.1% | +0.3764 | Antiinflammatory products for vaginal administration |
| CELECOXIB | 274 | 63.1% | +0.5047 | Other antineoplastic agents |
| MELOXICAM | 87 | 59.8% | +0.2444 | Oxicams |
| SODIUM AUROTHIOMALATE | 68 | 30.9% | -1.0521 | Gold preparations |
| KETOROLAC | 60 | 20.0% | -0.7922 | Antiinflammatory agents, non-steroids |
| KETOPROFEN | 59 | 66.1% | +0.5920 | Propionic acid derivatives |
| INDOMETACIN | 55 | 83.6% | +0.8858 | Antiinflammatory agents, non-steroids |
| PIROXICAM | 21 | 81.0% | +0.6258 | Oxicams |
| ETORICOXIB | 20 | 25.0% | -0.4444 | Coxibs |
| LOXOPROFEN | 14 | 64.3% | +0.2531 | Propionic acid derivatives |
| ROFECOXIB | 14 | 21.4% | -1.3039 | Coxibs |
| INDOMETHACIN | 12 | 50.0% | -0.0893 | Acetic acid derivatives and related substances |
| MEFENAMIC ACID | 8 | 12.5% | -0.7475 | Fenamates |
| GLUCOSAMINE | 8 | 0.0% | -2.0862 | Other antiinflammatory and antirheumatic agents, non-steroids |
| NIMESULIDE | 7 | 14.3% | -0.7322 | Other antiinflammatory and antirheumatic agents, non-steroids |
| ETODOLAC | 3 | 33.3% | -0.2225 | Acetic acid derivatives and related substances |
| NABUMETONE | 3 | 0.0% | -0.9430 | Other antiinflammatory and antirheumatic agents, non-steroids |
| PENICILLAMINE | 2 | 100.0% | +0.7015 | Penicillamine and similar agents |
| *...and 5 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| ETODOLAC | 3 | 33.3% | -0.2225 | Acetic acid derivatives and related substances | Only 33.3% female-biased vs class 54.4% |
| ETORICOXIB | 20 | 25.0% | -0.4444 | Coxibs | Only 25.0% female-biased vs class 54.4% |
| GLUCOSAMINE | 8 | 0.0% | -2.0862 | Other antiinflammatory and antirheumatic agents, non-steroids | Only 0.0% female-biased vs class 54.4% |
| KETOROLAC | 60 | 20.0% | -0.7922 | Antiinflammatory agents, non-steroids | Only 20.0% female-biased vs class 54.4% |
| MEFENAMIC ACID | 8 | 12.5% | -0.7475 | Fenamates | Only 12.5% female-biased vs class 54.4% |
| NABUMETONE | 3 | 0.0% | -0.9430 | Other antiinflammatory and antirheumatic agents, non-steroids | Only 0.0% female-biased vs class 54.4% |
| NIMESULIDE | 7 | 14.3% | -0.7322 | Other antiinflammatory and antirheumatic agents, non-steroids | Only 14.3% female-biased vs class 54.4% |
| ROFECOXIB | 14 | 21.4% | -1.3039 | Coxibs | Only 21.4% female-biased vs class 54.4% |
| SODIUM AUROTHIOMALATE | 68 | 30.9% | -1.0521 | Gold preparations | Only 30.9% female-biased vs class 54.4% |

---
## J01: Antibacterials (Antibiotics)

**73 drugs | 3,738 signals | Class trend: male_higher**
- Female-higher: 1,852 (49.5%)
- Male-higher: 1,886 (50.5%)
- Mean log-ratio: -0.0133 | Median: -0.5032 | SD: 1.1177
- Within-class variation: High heterogeneity (CV=0.648, range 0.0%--100.0%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| LEVOFLOXACIN | Orthostatic hypotension | +3.935 | 43.92 | 0.86 | 492 | 13 |
| SULFAMETHOXAZOLE | Pruritus | +3.754 | 52.39 | 1.23 | 1,628 | 10 |
| SULFAMETHOXAZOLE | Stomatitis | +3.611 | 325.40 | 8.80 | 1,619 | 11 |
| SULFAMETHOXAZOLE | Pyrexia | +3.599 | 75.23 | 2.06 | 1,685 | 19 |
| SULFAMETHOXAZOLE | Arthralgia | +3.413 | 39.43 | 1.30 | 1,546 | 11 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| CEFTRIAXONE | Stress | -3.894 | 0.23 | 11.14 | 10 | 232 |
| MOXIFLOXACIN | Nodule | -3.887 | 1.75 | 85.32 | 12 | 201 |
| CEFALEXIN | Asthma | -3.603 | 0.74 | 27.27 | 21 | 151 |
| SULFAMETHOXAZOLE | Lymphoproliferative disorder | -3.395 | 25.32 | 755.39 | 11 | 43 |
| MOXIFLOXACIN | Thrombosis | -3.352 | 0.33 | 9.42 | 10 | 196 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Adverse drug reaction | 11 | 100% | female_higher | +1.1024 |
| Cardiac arrest | 10 | 100% | female_higher | +0.6440 |
| Nodule | 9 | 100% | male_higher | -1.6464 |
| Loss of personal independence in daily activities | 9 | 100% | male_higher | -1.5776 |
| Pulmonary embolism | 8 | 100% | male_higher | -1.9246 |
| Tendonitis | 8 | 100% | male_higher | -1.0931 |
| Visual acuity reduced | 8 | 100% | male_higher | -1.2930 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| CIPROFLOXACIN | 342 | 41.2% | -0.1243 | Antiinfectives |
| LEVOFLOXACIN | 254 | 46.5% | -0.1366 | Fluoroquinolones |
| DOXYCYCLINE | 223 | 58.7% | +0.4624 | Antiinfectives and antiseptics for local oral treatment |
| AMOXICILLIN | 212 | 42.9% | -0.1256 | Penicillins with extended spectrum |
| METRONIDAZOLE | 209 | 23.9% | -0.6263 | Other chemotherapeutics |
| VANCOMYCIN | 191 | 76.4% | +0.4887 | Antibiotics |
| AZITHROMYCIN | 189 | 40.7% | -0.0849 | Macrolides |
| MOXIFLOXACIN | 175 | 58.9% | +0.2484 | Fluoroquinolones |
| CLARITHROMYCIN | 175 | 37.1% | -0.2410 | Macrolides |
| CEFTRIAXONE | 167 | 64.1% | +0.1346 | Third-generation cephalosporins |
| LINEZOLID | 124 | 80.6% | +0.5416 | Other antibacterials |
| MEROPENEM | 119 | 86.6% | +0.6479 | Carbapenems |
| MINOCYCLINE | 100 | 55.0% | +0.2838 | Antiinfectives for treatment of acne |
| CLINDAMYCIN | 98 | 42.9% | -0.1454 | Antibiotics |
| CEFUROXIME | 87 | 33.3% | -0.5240 | Antibiotics |
| SULFAMETHOXAZOLE | 75 | 57.3% | +0.3433 | Intermediate-acting sulfonamides |
| AMIKACIN | 73 | 57.5% | +0.0962 | Antibiotics |
| TOBRAMYCIN | 59 | 33.9% | -0.2906 | Other aminoglycosides |
| DAPTOMYCIN | 56 | 78.6% | +0.6107 | Other antibacterials |
| ERYTHROMYCIN | 55 | 21.8% | -0.7797 | Antiinfectives for treatment of acne |
| *...and 53 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| CEFEPIME | 41 | 80.5% | +0.5131 | Fourth-generation cephalosporins | 80.5% female-biased vs class 49.5% |
| CEFIDEROCOL | 3 | 100.0% | +1.0193 | Other cephalosporins and penems | 100.0% female-biased vs class 49.5% |
| CEFOTAXIME | 23 | 78.3% | +0.6948 | Third-generation cephalosporins | 78.3% female-biased vs class 49.5% |
| CEFTAZIDIME | 41 | 75.6% | +0.4052 | Third-generation cephalosporins | 75.6% female-biased vs class 49.5% |
| CEFTRIAXONE | 167 | 64.1% | +0.1346 | Third-generation cephalosporins | 64.1% female-biased vs class 49.5% |
| CLOXACILLIN | 6 | 83.3% | +0.4613 | Beta-lactamase resistant penicillins | 83.3% female-biased vs class 49.5% |
| COLISTIN | 15 | 86.7% | +0.6697 | Polymyxins | 86.7% female-biased vs class 49.5% |
| DAPTOMYCIN | 56 | 78.6% | +0.6107 | Other antibacterials | 78.6% female-biased vs class 49.5% |
| DORIPENEM | 3 | 100.0% | +0.6819 | Carbapenems | 100.0% female-biased vs class 49.5% |
| FUSIDIC ACID | 3 | 100.0% | +0.8626 | Medicated dressings with antiinfectives | 100.0% female-biased vs class 49.5% |
| GENTAMICIN | 45 | 62.2% | +0.2278 | Other aminoglycosides | 62.2% female-biased vs class 49.5% |
| LINEZOLID | 124 | 80.6% | +0.5416 | Other antibacterials | 80.6% female-biased vs class 49.5% |
| MEROPENEM | 119 | 86.6% | +0.6479 | Carbapenems | 86.6% female-biased vs class 49.5% |
| PIPERACILLIN | 3 | 66.7% | +0.1667 | Penicillins with extended spectrum | 66.7% female-biased vs class 49.5% |
| STREPTOMYCIN | 5 | 80.0% | +0.5175 | Streptomycins | 80.0% female-biased vs class 49.5% |
| TAZOBACTAM | 8 | 75.0% | +0.4478 | Beta-lactamase inhibitors | 75.0% female-biased vs class 49.5% |
| TEICOPLANIN | 18 | 83.3% | +0.5458 | Glycopeptide antibacterials | 83.3% female-biased vs class 49.5% |
| TIGECYCLINE | 26 | 84.6% | +0.5964 | Tetracyclines | 84.6% female-biased vs class 49.5% |
| VANCOMYCIN | 191 | 76.4% | +0.4887 | Antibiotics | 76.4% female-biased vs class 49.5% |

---
## C09: Renin-Angiotensin Agents (ACEi/ARBs)

**17 drugs | 1,651 signals | Class trend: female_higher**
- Female-higher: 1,016 (61.5%)
- Male-higher: 635 (38.5%)
- Mean log-ratio: +0.3271 | Median: +0.6238 | SD: 1.1239
- Within-class variation: Moderate heterogeneity (CV=0.334, range 20.0%--87.5%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| RAMIPRIL | Liver injury | +3.702 | 48.03 | 1.18 | 755 | 18 |
| RAMIPRIL | Road traffic accident | +3.510 | 13.05 | 0.39 | 371 | 12 |
| RAMIPRIL | Treatment failure | +3.505 | 9.38 | 0.28 | 628 | 16 |
| RAMIPRIL | Hepatic cirrhosis | +3.379 | 20.88 | 0.71 | 245 | 11 |
| RAMIPRIL | Blister | +3.370 | 16.41 | 0.56 | 764 | 19 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| CANDESARTAN | Nodule | -2.821 | 2.17 | 36.40 | 14 | 79 |
| RAMIPRIL | Breath sounds abnormal | -2.821 | 2.61 | 43.81 | 10 | 155 |
| CANDESARTAN | Full blood count abnormal | -2.579 | 4.29 | 56.59 | 20 | 128 |
| RAMIPRIL | Micturition urgency | -2.492 | 1.36 | 16.41 | 12 | 125 |
| CANDESARTAN | Hypothyroidism | -2.489 | 1.94 | 23.37 | 26 | 128 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Confusional state | 8 | 100% | female_higher | +1.2212 |
| Product use issue | 7 | 100% | female_higher | +1.3312 |
| Pneumonia | 7 | 100% | female_higher | +1.4858 |
| Drug abuse | 7 | 100% | female_higher | +0.7727 |
| Hyperkalaemia | 7 | 100% | female_higher | +0.6464 |
| Anxiety | 6 | 100% | female_higher | +1.6006 |
| Cerebrovascular accident | 6 | 100% | female_higher | +1.3410 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| RAMIPRIL | 368 | 71.2% | +0.6755 | ACE inhibitors, plain |
| LISINOPRIL | 252 | 84.5% | +0.7209 | ACE inhibitors, plain |
| VALSARTAN | 219 | 49.3% | -0.0085 | Angiotensin II receptor blockers (ARBs), plain |
| CANDESARTAN | 198 | 52.5% | +0.1886 | Angiotensin II receptor blockers (ARBs), plain |
| LOSARTAN | 130 | 49.2% | +0.0019 | Angiotensin II receptor blockers (ARBs), plain |
| PERINDOPRIL | 123 | 68.3% | +0.4052 | ACE inhibitors, plain |
| IRBESARTAN | 97 | 43.3% | -0.0699 | Angiotensin II receptor blockers (ARBs), plain |
| TELMISARTAN | 73 | 50.7% | +0.0121 | Angiotensin II receptor blockers (ARBs), plain |
| ENALAPRIL | 72 | 66.7% | +0.3884 | ACE inhibitors, plain |
| ALISKIREN | 38 | 50.0% | +0.3933 | Renin-inhibitors |
| CAPTOPRIL | 20 | 20.0% | -0.6939 | ACE inhibitors, plain |
| QUINAPRIL | 15 | 26.7% | -0.3068 | ACE inhibitors, plain |
| SPARSENTAN | 13 | 46.2% | -0.0964 | Other agents acting on the renin-angiotensin system |
| OLMESARTAN MEDOXOMIL | 12 | 41.7% | -0.2716 | Angiotensin II receptor blockers (ARBs), plain |
| BENAZEPRIL | 9 | 66.7% | +0.2269 | ACE inhibitors, plain |
| TRANDOLAPRIL | 8 | 87.5% | +0.8053 | ACE inhibitors, plain |
| FOSINOPRIL | 4 | 75.0% | +0.4227 | ACE inhibitors, plain |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| CAPTOPRIL | 20 | 20.0% | -0.6939 | ACE inhibitors, plain | Only 20.0% female-biased vs class 61.5% |
| QUINAPRIL | 15 | 26.7% | -0.3068 | ACE inhibitors, plain | Only 26.7% female-biased vs class 61.5% |

---
## A10: Antidiabetics

**30 drugs | 1,821 signals | Class trend: female_higher**
- Female-higher: 962 (52.8%)
- Male-higher: 859 (47.2%)
- Mean log-ratio: +0.0666 | Median: +0.5194 | SD: 0.9248
- Within-class variation: High heterogeneity (CV=0.563, range 0.0%--100.0%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| SITAGLIPTIN | Gangrene | +3.247 | 54.99 | 2.14 | 117 | 10 |
| GLICLAZIDE | Rhinorrhoea | +2.438 | 16.95 | 1.48 | 172 | 11 |
| METFORMIN | Sinus disorder | +2.423 | 4.86 | 0.43 | 244 | 11 |
| GLICLAZIDE | Coma | +2.389 | 21.82 | 2.00 | 116 | 12 |
| METFORMIN | Therapeutic product effect decreased | +2.320 | 1.81 | 0.18 | 193 | 11 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| METFORMIN | Abortion spontaneous | -3.581 | 1.52 | 54.74 | 190 | 14 |
| METFORMIN | Neurological symptom | -2.946 | 1.28 | 24.30 | 12 | 181 |
| METFORMIN | Vasculitis | -2.804 | 0.64 | 10.63 | 13 | 159 |
| LIRAGLUTIDE | Lung disorder | -2.691 | 0.33 | 4.85 | 14 | 106 |
| LIRAGLUTIDE | Nodule | -2.627 | 1.24 | 17.17 | 18 | 75 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Rhabdomyolysis | 8 | 100% | female_higher | +0.9907 |
| Lactic acidosis | 7 | 100% | female_higher | +0.8501 |
| Renal failure acute | 7 | 100% | female_higher | +0.7111 |
| Fall | 6 | 100% | female_higher | +0.8350 |
| Skin ulcer | 6 | 100% | male_higher | -0.8083 |
| Abdominal pain lower | 6 | 100% | male_higher | -0.9155 |
| Angioedema | 6 | 100% | female_higher | +0.7612 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| METFORMIN | 399 | 62.4% | +0.2421 | Biguanides |
| SITAGLIPTIN | 154 | 55.2% | +0.1929 | Dipeptidyl peptidase 4 (DPP-4) inhibitors |
| DAPAGLIFLOZIN | 154 | 59.1% | +0.0912 | Sodium-glucose co-transporter 2 (SGLT2) inhibitors |
| SEMAGLUTIDE | 152 | 31.6% | -0.2785 | Glucagon-like peptide-1 (GLP-1) analogues |
| LIRAGLUTIDE | 101 | 13.9% | -0.7929 | Glucagon-like peptide-1 (GLP-1) analogues |
| EMPAGLIFLOZIN | 96 | 60.4% | +0.1522 | Sodium-glucose co-transporter 2 (SGLT2) inhibitors |
| TIRZEPATIDE | 95 | 8.4% | -0.5797 | Other blood glucose lowering drugs, excl. insulins |
| EXENATIDE | 92 | 39.1% | -0.1988 | Glucagon-like peptide-1 (GLP-1) analogues |
| GLICLAZIDE | 91 | 76.9% | +0.6859 | Sulfonylureas |
| DULAGLUTIDE | 77 | 27.3% | -0.3414 | Glucagon-like peptide-1 (GLP-1) analogues |
| CANAGLIFLOZIN | 69 | 60.9% | +0.1489 | Sodium-glucose co-transporter 2 (SGLT2) inhibitors |
| PIOGLITAZONE | 61 | 90.2% | +0.7549 | Thiazolidinediones |
| ROSIGLITAZONE | 47 | 93.6% | +0.5987 | Thiazolidinediones |
| LINAGLIPTIN | 42 | 52.4% | -0.0050 | Dipeptidyl peptidase 4 (DPP-4) inhibitors |
| GLIMEPIRIDE | 38 | 81.6% | +0.5365 | Sulfonylureas |
| VILDAGLIPTIN | 25 | 68.0% | +0.2808 | Dipeptidyl peptidase 4 (DPP-4) inhibitors |
| GLIBENCLAMIDE | 25 | 56.0% | +0.1189 | Sulfonylureas |
| REPAGLINIDE | 22 | 68.2% | +0.2904 | Other blood glucose lowering drugs, excl. insulins |
| SAXAGLIPTIN | 18 | 66.7% | +0.2710 | Dipeptidyl peptidase 4 (DPP-4) inhibitors |
| GLIPIZIDE | 17 | 47.1% | -0.0431 | Sulfonylureas |
| *...and 10 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| ALBIGLUTIDE | 14 | 21.4% | -0.3770 | Glucagon-like peptide-1 (GLP-1) analogues | Only 21.4% female-biased vs class 52.8% |
| DULAGLUTIDE | 77 | 27.3% | -0.3414 | Glucagon-like peptide-1 (GLP-1) analogues | Only 27.3% female-biased vs class 52.8% |
| EXENATIDE | 92 | 39.1% | -0.1988 | Glucagon-like peptide-1 (GLP-1) analogues | Only 39.1% female-biased vs class 52.8% |
| LIRAGLUTIDE | 101 | 13.9% | -0.7929 | Glucagon-like peptide-1 (GLP-1) analogues | Only 13.9% female-biased vs class 52.8% |
| SEMAGLUTIDE | 152 | 31.6% | -0.2785 | Glucagon-like peptide-1 (GLP-1) analogues | Only 31.6% female-biased vs class 52.8% |
| TIRZEPATIDE | 95 | 8.4% | -0.5797 | Other blood glucose lowering drugs, excl. insulins | Only 8.4% female-biased vs class 52.8% |

---
## B01: Antithrombotic Agents (Anticoagulants)

**34 drugs | 2,705 signals | Class trend: female_higher**
- Female-higher: 1,762 (65.1%)
- Male-higher: 943 (34.9%)
- Mean log-ratio: +0.2491 | Median: +0.5991 | SD: 0.9445
- Within-class variation: Moderate heterogeneity (CV=0.344, range 25.0%--100.0%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| DIPYRIDAMOLE | Cognitive disorder | +3.397 | 439.35 | 14.70 | 461 | 12 |
| APIXABAN | Blood test abnormal | +3.158 | 4.78 | 0.20 | 292 | 10 |
| DIPYRIDAMOLE | Hypotension | +2.842 | 105.98 | 6.18 | 441 | 22 |
| CLOPIDOGREL | Neutrophilia | +2.840 | 16.57 | 0.97 | 64 | 10 |
| ACETYLSALICYLIC ACID | Muscle spasticity | +2.801 | 11.25 | 0.68 | 234 | 14 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| APIXABAN | Mite allergy | -3.210 | 8.62 | 213.57 | 14 | 236 |
| DALTEPARIN | Abdominal distension | -3.169 | 1.72 | 40.91 | 17 | 210 |
| DALTEPARIN | Dry mouth | -3.162 | 1.27 | 29.94 | 10 | 115 |
| APIXABAN | Nodule | -3.125 | 0.33 | 7.46 | 21 | 242 |
| DALTEPARIN | Blood cholesterol increased | -3.042 | 2.38 | 49.75 | 10 | 99 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Cerebral haemorrhage | 11 | 100% | female_higher | +0.6988 |
| Muscle haemorrhage | 10 | 100% | female_higher | +1.4200 |
| Gastrointestinal haemorrhage | 10 | 100% | female_higher | +0.7129 |
| Myocardial infarction | 8 | 100% | female_higher | +0.9697 |
| Drug ineffective | 8 | 100% | male_higher | -0.9374 |
| Decreased appetite | 8 | 100% | female_higher | +0.7697 |
| Subdural haematoma | 8 | 100% | female_higher | +0.8528 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| ACETYLSALICYLIC ACID | 433 | 73.0% | +0.4798 | Salicylic acid and derivatives |
| CLOPIDOGREL | 300 | 82.3% | +0.6232 | Platelet aggregation inhibitors excl. heparin |
| APIXABAN | 275 | 58.5% | +0.0749 | Direct factor Xa inhibitors |
| RIVAROXABAN | 243 | 68.7% | +0.2723 | Direct factor Xa inhibitors |
| WARFARIN | 220 | 56.8% | +0.0324 | Vitamin K antagonists |
| TREPROSTINIL | 165 | 32.1% | -0.3164 | Platelet aggregation inhibitors excl. heparin |
| HEPARIN | 144 | 63.9% | +0.1189 | Other ophthalmologicals |
| ASPIRIN | 137 | 82.5% | +0.5828 | Salicylic acid and derivatives |
| TICAGRELOR | 136 | 79.4% | +0.4725 | Platelet aggregation inhibitors excl. heparin |
| ENOXAPARIN | 105 | 52.4% | +0.1013 | Heparin group |
| SELEXIPAG | 68 | 25.0% | -0.4078 | Platelet aggregation inhibitors excl. heparin |
| EPOPROSTENOL | 64 | 28.1% | -0.4232 | Platelet aggregation inhibitors excl. heparin |
| ALTEPLASE | 62 | 72.6% | +0.3884 | Enzymes |
| DALTEPARIN | 58 | 25.9% | -0.8999 | Heparin group |
| PRASUGREL | 50 | 96.0% | +0.7561 | Platelet aggregation inhibitors excl. heparin |
| EDOXABAN | 50 | 74.0% | +0.5002 | Direct factor Xa inhibitors |
| FLUINDIONE | 24 | 95.8% | +0.8285 | Vitamin K antagonists |
| FONDAPARINUX | 24 | 58.3% | +0.1867 | Other antithrombotic agents |
| PHENPROCOUMON | 23 | 78.3% | +0.5528 | Vitamin K antagonists |
| ILOPROST | 23 | 78.3% | +0.3499 | Platelet aggregation inhibitors excl. heparin |
| *...and 14 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| DALTEPARIN | 58 | 25.9% | -0.8999 | Heparin group | Only 25.9% female-biased vs class 65.1% |
| EPOPROSTENOL | 64 | 28.1% | -0.4232 | Platelet aggregation inhibitors excl. heparin | Only 28.1% female-biased vs class 65.1% |
| NADROPARIN | 7 | 28.6% | -0.2094 | Heparin group | Only 28.6% female-biased vs class 65.1% |
| SELEXIPAG | 68 | 25.0% | -0.4078 | Platelet aggregation inhibitors excl. heparin | Only 25.0% female-biased vs class 65.1% |
| TINZAPARIN | 9 | 33.3% | -0.2952 | Heparin group | Only 33.3% female-biased vs class 65.1% |
| TREPROSTINIL | 165 | 32.1% | -0.3164 | Platelet aggregation inhibitors excl. heparin | Only 32.1% female-biased vs class 65.1% |

---
## N06: Psychoanaleptics (Antidepressants)

**53 drugs | 3,485 signals | Class trend: male_higher**
- Female-higher: 1,625 (46.6%)
- Male-higher: 1,860 (53.4%)
- Mean log-ratio: -0.0508 | Median: -0.5312 | SD: 1.0468
- Within-class variation: High heterogeneity (CV=0.626, range 0.0%--100.0%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| ATOMOXETINE | Obesity | +3.959 | 155.15 | 2.96 | 339 | 12 |
| ATOMOXETINE | Epilepsy | +3.926 | 117.94 | 2.33 | 523 | 16 |
| ATOMOXETINE | Product use in unapproved indication | +3.657 | 11.37 | 0.29 | 485 | 16 |
| TRAZODONE | Wheezing | +3.234 | 17.44 | 0.69 | 580 | 11 |
| ATOMOXETINE | Muscular weakness | +3.230 | 11.86 | 0.47 | 260 | 10 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| DESVENLAFAXINE | Maternal exposure during pregnancy | -3.809 | 0.30 | 13.68 | 18 | 11 |
| ESCITALOPRAM | Sleep disorder due to a general medical condition | -3.624 | 0.74 | 27.61 | 12 | 208 |
| NORTRIPTYLINE | Nightmare | -3.581 | 3.36 | 120.74 | 17 | 268 |
| ESCITALOPRAM | Systemic lupus erythematosus | -3.509 | 0.68 | 22.61 | 32 | 77 |
| SERTRALINE | Maternal exposure during pregnancy | -3.342 | 2.86 | 81.00 | 781 | 448 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Cardiac arrest | 14 | 100% | female_higher | +0.7634 |
| Pulmonary oedema | 11 | 100% | male_higher | -1.2584 |
| Bipolar disorder | 11 | 100% | male_higher | -0.7919 |
| Hypotension | 10 | 100% | female_higher | +1.0305 |
| Fear | 10 | 100% | male_higher | -0.8110 |
| Maternal exposure during pregnancy | 9 | 100% | male_higher | -1.9963 |
| Renal impairment | 9 | 100% | female_higher | +1.0206 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| SERTRALINE | 302 | 42.1% | -0.1765 | Selective serotonin reuptake inhibitors |
| VENLAFAXINE | 287 | 40.8% | -0.2002 | Other antidepressants |
| CITALOPRAM | 237 | 56.5% | +0.0840 | Selective serotonin reuptake inhibitors |
| ESCITALOPRAM | 217 | 28.1% | -0.5181 | Selective serotonin reuptake inhibitors |
| FLUOXETINE | 204 | 36.3% | -0.2914 | Selective serotonin reuptake inhibitors |
| MIRTAZAPINE | 193 | 57.0% | +0.1207 | Other antidepressants |
| AMITRIPTYLINE | 189 | 54.0% | +0.0875 | Non-selective monoamine reuptake inhibitors |
| DULOXETINE | 189 | 45.0% | -0.1575 | Other antidepressants |
| PAROXETINE | 186 | 48.4% | -0.0285 | Selective serotonin reuptake inhibitors |
| BUPROPION | 174 | 54.0% | +0.0816 | Other antidepressants |
| TRAZODONE | 151 | 65.6% | +0.4611 | Other antidepressants |
| METHYLPHENIDATE | 147 | 77.6% | +0.4738 | Centrally acting sympathomimetics |
| ATOMOXETINE | 105 | 68.6% | +1.0213 | Centrally acting sympathomimetics |
| LISDEXAMFETAMINE | 97 | 26.8% | -0.5384 | Centrally acting sympathomimetics |
| RIVASTIGMINE | 74 | 37.8% | -0.2174 | Anticholinesterases |
| NORTRIPTYLINE | 64 | 48.4% | +0.0422 | Non-selective monoamine reuptake inhibitors |
| DONEPEZIL | 62 | 46.8% | -0.0206 | Anticholinesterases |
| VORTIOXETINE | 61 | 31.1% | -0.3067 | Other antidepressants |
| DESVENLAFAXINE | 46 | 10.9% | -0.6694 | Other antidepressants |
| CLOMIPRAMINE | 43 | 41.9% | -0.2560 | Non-selective monoamine reuptake inhibitors |
| *...and 33 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| AMFETAMINE | 36 | 63.9% | +0.1697 | Centrally acting sympathomimetics | 63.9% female-biased vs class 46.6% |
| ATOMOXETINE | 105 | 68.6% | +1.0213 | Centrally acting sympathomimetics | 68.6% female-biased vs class 46.6% |
| CAFFEINE | 35 | 80.0% | +1.0135 | Other dermatologicals | 80.0% female-biased vs class 46.6% |
| DEXMETHYLPHENIDATE | 17 | 76.5% | +0.5537 | Centrally acting sympathomimetics | 76.5% female-biased vs class 46.6% |
| DEXTROAMPHETAMINE | 3 | 66.7% | +0.3132 | Centrally acting sympathomimetics | 66.7% female-biased vs class 46.6% |
| METAMFETAMINE | 35 | 80.0% | +0.6069 | Centrally acting sympathomimetics | 80.0% female-biased vs class 46.6% |
| METHYLPHENIDATE | 147 | 77.6% | +0.4738 | Centrally acting sympathomimetics | 77.6% female-biased vs class 46.6% |
| TRAZODONE | 151 | 65.6% | +0.4611 | Other antidepressants | 65.6% female-biased vs class 46.6% |

---
## L01: Antineoplastic Agents

**218 drugs | 14,016 signals | Class trend: female_higher**
- Female-higher: 9,121 (65.1%)
- Male-higher: 4,895 (34.9%)
- Mean log-ratio: +0.2857 | Median: +0.6113 | SD: 0.9343
- Within-class variation: Moderate heterogeneity (CV=0.409, range 0.0%--100.0%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| METHOTREXATE | Glossodynia | +4.745 | 60.67 | 0.53 | 6,104 | 14 |
| RITUXIMAB | Prescribed overdose | +4.559 | 19.12 | 0.20 | 1,278 | 12 |
| SIROLIMUS | Transplant dysfunction | +4.505 | 2536.59 | 28.05 | 452 | 17 |
| METHOTREXATE | Pemphigus | +4.371 | 258.34 | 3.27 | 6,680 | 22 |
| RITUXIMAB | Obesity | +4.335 | 27.36 | 0.36 | 1,172 | 20 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| PERTUZUMAB | Carbohydrate antigen 15-3 increased | -7.391 | 8.59 | 13927.37 | 11 | 10 |
| TRASTUZUMAB | Carbohydrate antigen 15-3 increased | -5.865 | 6.90 | 2431.30 | 19 | 10 |
| PERTUZUMAB | Oligohydramnios | -5.445 | 4.50 | 1042.91 | 18 | 11 |
| DOCETAXEL | Carbohydrate antigen 15-3 increased | -4.786 | 5.37 | 642.74 | 16 | 10 |
| PERTUZUMAB | SARS-CoV-2 test positive | -4.395 | 1.34 | 108.37 | 21 | 46 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Fungal infection | 32 | 100% | male_higher | -1.0374 |
| Neurotoxicity | 31 | 100% | female_higher | +0.9098 |
| Drug interaction | 29 | 100% | female_higher | +0.7138 |
| Cardiac failure congestive | 25 | 100% | female_higher | +0.8531 |
| Graft versus host disease | 24 | 100% | female_higher | +0.9380 |
| Polyneuropathy | 23 | 100% | female_higher | +0.8135 |
| Abdominal pain lower | 21 | 100% | male_higher | -1.0601 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| METHOTREXATE | 892 | 48.5% | +0.0815 | Folic acid analogues |
| RITUXIMAB | 755 | 66.6% | +0.5724 | CD20 (Clusters of Differentiation 20) inhibitors |
| CYCLOPHOSPHAMIDE | 498 | 64.7% | +0.2688 | Nitrogen mustard analogues |
| DOXORUBICIN | 325 | 71.4% | +0.4281 | Anthracyclines and related substances |
| CARBOPLATIN | 310 | 63.5% | +0.2470 | Platinum compounds |
| PEMBROLIZUMAB | 309 | 73.1% | +0.4206 | PD-1/PD-L1 (Programmed cell death protein 1/death ligand 1) inhibitors |
| DOCETAXEL | 304 | 11.2% | -0.7539 | Taxanes |
| BEVACIZUMAB | 294 | 55.4% | +0.1184 | VEGF/VEGFR (Vascular Endothelial Growth Factor) inhibitors |
| VINCRISTINE | 290 | 76.2% | +0.4992 | Vinca alkaloids and analogues |
| CYTARABINE | 274 | 79.6% | +0.5558 | Pyrimidine analogues |
| CELECOXIB | 274 | 63.1% | +0.5047 | Other antineoplastic agents |
| ETOPOSIDE | 273 | 79.1% | +0.5395 | Podophyllotoxin derivatives |
| CAPECITABINE | 270 | 57.4% | +0.1077 | Pyrimidine analogues |
| PACLITAXEL | 259 | 62.5% | +0.1893 | Taxanes |
| OXALIPLATIN | 239 | 69.0% | +0.3565 | Platinum compounds |
| FLUOROURACIL | 239 | 60.3% | +0.1585 | Pyrimidine analogues |
| EVEROLIMUS | 239 | 50.6% | +0.0010 | Mammalian target of rapamycin (mTOR) kinase inhibitors |
| NIVOLUMAB | 238 | 66.8% | +0.2990 | PD-1/PD-L1 (Programmed cell death protein 1/death ligand 1) inhibitors |
| CISPLATIN | 219 | 76.3% | +0.4889 | Platinum compounds |
| BORTEZOMIB | 209 | 75.1% | +0.5021 | Proteasome inhibitors |
| *...and 198 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| ABEMACICLIB | 12 | 8.3% | -1.0965 | Cyclin-dependent kinase (CDK) inhibitors | Only 8.3% female-biased vs class 65.1% |
| AMINOLEVULINIC ACID | 4 | 0.0% | -0.7520 | Sensitizers used in photodynamic/radiation therapy | Only 0.0% female-biased vs class 65.1% |
| AMIVANTAMAB | 8 | 25.0% | -0.4359 | Other monoclonal antibodies and antibody drug conjugates | Only 25.0% female-biased vs class 65.1% |
| AVAPRITINIB | 52 | 11.5% | -0.4895 | Other protein kinase inhibitors | Only 11.5% female-biased vs class 65.1% |
| CAPMATINIB | 15 | 13.3% | -0.5726 | Other protein kinase inhibitors | Only 13.3% female-biased vs class 65.1% |
| CHLORMETHINE | 22 | 13.6% | -0.5016 | Nitrogen mustard analogues | Only 13.6% female-biased vs class 65.1% |
| CLADRIBINE | 54 | 20.4% | -0.5610 | Selective immunosuppressants | Only 20.4% female-biased vs class 65.1% |
| DOCETAXEL | 304 | 11.2% | -0.7539 | Taxanes | Only 11.2% female-biased vs class 65.1% |
| EPIRUBICIN | 72 | 33.3% | -0.3684 | Anthracyclines and related substances | Only 33.3% female-biased vs class 65.1% |
| ERIBULIN | 6 | 16.7% | -0.6408 | Other antineoplastic agents | Only 16.7% female-biased vs class 65.1% |
| FRUQUINTINIB | 16 | 37.5% | -0.1586 | Vascular endothelial growth factor receptor (VEGFR) tyrosine kinase inhibitors | Only 37.5% female-biased vs class 65.1% |
| LAPATINIB | 7 | 28.6% | -0.6939 | Human epidermal growth factor receptor 2 (HER2) tyrosine kinase inhibitors | Only 28.6% female-biased vs class 65.1% |
| LAROTRECTINIB | 4 | 25.0% | -0.3779 | Other protein kinase inhibitors | Only 25.0% female-biased vs class 65.1% |
| LORLATINIB | 22 | 36.4% | -0.1404 | Anaplastic lymphoma kinase (ALK) inhibitors | Only 36.4% female-biased vs class 65.1% |
| MITOTANE | 6 | 0.0% | -0.8553 | Other antineoplastic agents | Only 0.0% female-biased vs class 65.1% |
| NIROGACESTAT | 3 | 33.3% | -0.4159 | Other antineoplastic agents | Only 33.3% female-biased vs class 65.1% |
| OFATUMUMAB | 67 | 11.9% | -0.6881 | CD20 (Clusters of Differentiation 20) inhibitors | Only 11.9% female-biased vs class 65.1% |
| PERTUZUMAB | 53 | 7.5% | -2.0129 | HER2 (Human Epidermal Growth Factor Receptor 2) inhibitors | Only 7.5% female-biased vs class 65.1% |
| RIPRETINIB | 19 | 31.6% | -0.3614 | Other protein kinase inhibitors | Only 31.6% female-biased vs class 65.1% |
| RUCAPARIB | 13 | 38.5% | -0.3405 | Poly (ADP-ribose) polymerase (PARP) inhibitors | Only 38.5% female-biased vs class 65.1% |
| SACITUZUMAB GOVITECAN | 11 | 27.3% | -0.3666 | Other monoclonal antibodies and antibody drug conjugates | Only 27.3% female-biased vs class 65.1% |
| SELUMETINIB | 4 | 25.0% | -0.4744 | Mitogen-activated protein kinase (MEK) inhibitors | Only 25.0% female-biased vs class 65.1% |
| SONIDEGIB | 7 | 28.6% | -0.4151 | Hedgehog pathway inhibitors | Only 28.6% female-biased vs class 65.1% |
| TALIMOGENE LAHERPAREPVEC | 4 | 25.0% | -0.2654 | Antineoplastic cell and gene therapy | Only 25.0% female-biased vs class 65.1% |
| TRABECTEDIN | 16 | 31.2% | -0.2788 | Other plant alkaloids and natural products | Only 31.2% female-biased vs class 65.1% |
| TRASTUZUMAB | 101 | 30.7% | -0.8069 | HER2 (Human Epidermal Growth Factor Receptor 2) inhibitors | Only 30.7% female-biased vs class 65.1% |
| TRASTUZUMAB DERUXTECAN | 20 | 25.0% | -0.6075 | HER2 (Human Epidermal Growth Factor Receptor 2) inhibitors | Only 25.0% female-biased vs class 65.1% |
| TRASTUZUMAB EMTANSINE | 17 | 0.0% | -1.6939 | HER2 (Human Epidermal Growth Factor Receptor 2) inhibitors | Only 0.0% female-biased vs class 65.1% |

---
## N02: Analgesics

**41 drugs | 4,953 signals | Class trend: female_higher**
- Female-higher: 3,234 (65.3%)
- Male-higher: 1,719 (34.7%)
- Mean log-ratio: +0.4243 | Median: +0.6624 | SD: 1.1830
- Within-class variation: High heterogeneity (CV=0.714, range 0.0%--100.0%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| OXYCODONE | Infusion related reaction | +5.496 | 11.61 | 0.05 | 2,523 | 10 |
| OXYCODONE | Pericarditis | +5.396 | 51.53 | 0.23 | 2,508 | 11 |
| OXYCODONE | Blister | +5.056 | 14.54 | 0.09 | 2,917 | 19 |
| OXYCODONE | Impaired healing | +4.808 | 27.42 | 0.22 | 2,933 | 22 |
| OXYCODONE | Wheezing | +4.462 | 6.83 | 0.08 | 1,532 | 18 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| RIZATRIPTAN | Hyperhidrosis | -4.675 | 1.17 | 125.57 | 13 | 255 |
| ALMOTRIPTAN | Hyperhidrosis | -3.997 | 12.44 | 677.33 | 24 | 240 |
| GABAPENTIN | Hand deformity | -3.813 | 0.27 | 12.05 | 13 | 38 |
| ALMOTRIPTAN | Product use in unapproved indication | -3.812 | 2.47 | 111.56 | 10 | 176 |
| FENTANYL | Pelvic pain | -3.665 | 0.21 | 8.37 | 10 | 52 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Hypersensitivity | 15 | 100% | female_higher | +1.4629 |
| Weight decreased | 14 | 100% | female_higher | +0.8610 |
| Infection | 13 | 100% | female_higher | +1.6960 |
| Drug intolerance | 13 | 100% | female_higher | +1.3154 |
| Pneumonia | 12 | 100% | female_higher | +1.5430 |
| Decreased appetite | 12 | 100% | female_higher | +1.0213 |
| Peripheral swelling | 11 | 100% | female_higher | +1.8973 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| OXYCODONE | 492 | 85.0% | +1.0913 | Natural opium alkaloids |
| PARACETAMOL | 487 | 56.9% | +0.3364 | Anilides |
| MORPHINE | 441 | 83.4% | +0.8473 | Natural opium alkaloids |
| ACETYLSALICYLIC ACID | 433 | 73.0% | +0.4798 | Salicylic acid and derivatives |
| PREGABALIN | 406 | 53.9% | +0.1730 | Gabapentinoids |
| TRAMADOL | 360 | 75.3% | +0.7217 | Other opioids |
| GABAPENTIN | 333 | 34.8% | -0.4093 | Gabapentinoids |
| HYDROMORPHONE | 311 | 76.5% | +0.6543 | Natural opium alkaloids |
| FENTANYL | 291 | 74.6% | +0.4738 | Opioid anesthetics |
| BUPRENORPHINE | 261 | 54.0% | +0.2293 | Drugs used in opioid dependence |
| CODEINE | 190 | 75.8% | +0.8320 | Natural opium alkaloids |
| ASPIRIN | 137 | 82.5% | +0.5828 | Salicylic acid and derivatives |
| CLONIDINE | 111 | 60.4% | +0.3295 | Imidazoline receptor agonists |
| METHADONE | 107 | 73.8% | +0.4249 | Diphenylpropylamine derivatives |
| ACETAMINOPHEN | 89 | 65.2% | +0.5140 | Anilides |
| ERENUMAB | 68 | 79.4% | +0.7509 | Calcitonin gene-related peptide (CGRP) antagonists |
| SUMATRIPTAN | 57 | 21.1% | -0.5148 | Selective serotonin (5HT1) agonists |
| OXYMORPHONE | 50 | 68.0% | +0.2795 | Natural opium alkaloids |
| PETHIDINE | 48 | 27.1% | -0.4504 | Phenylpiperidine derivatives |
| TAPENTADOL | 39 | 43.6% | -0.1629 | Other opioids |
| *...and 21 more* | | | | |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| ALMOTRIPTAN | 5 | 0.0% | -3.4489 | Selective serotonin (5HT1) agonists | Only 0.0% female-biased vs class 65.3% |
| ATOGEPANT | 8 | 0.0% | -0.8608 | Calcitonin gene-related peptide (CGRP) antagonists | Only 0.0% female-biased vs class 65.3% |
| DIHYDROERGOTAMINE | 6 | 33.3% | -1.1865 | Ergot alkaloids | Only 33.3% female-biased vs class 65.3% |
| ELETRIPTAN | 9 | 0.0% | -1.3542 | Selective serotonin (5HT1) agonists | Only 0.0% female-biased vs class 65.3% |
| EPTINEZUMAB | 27 | 0.0% | -1.1895 | Calcitonin gene-related peptide (CGRP) antagonists | Only 0.0% female-biased vs class 65.3% |
| FREMANEZUMAB | 23 | 8.7% | -0.7574 | Calcitonin gene-related peptide (CGRP) antagonists | Only 8.7% female-biased vs class 65.3% |
| GABAPENTIN | 333 | 34.8% | -0.4093 | Gabapentinoids | Only 34.8% female-biased vs class 65.3% |
| GALCANEZUMAB | 36 | 5.6% | -0.7518 | Calcitonin gene-related peptide (CGRP) antagonists | Only 5.6% female-biased vs class 65.3% |
| LASMIDITAN | 3 | 0.0% | -0.7577 | Selective serotonin (5HT1) agonists | Only 0.0% female-biased vs class 65.3% |
| NALBUPHINE | 3 | 33.3% | -0.0852 | Morphinan derivatives | Only 33.3% female-biased vs class 65.3% |
| PETHIDINE | 48 | 27.1% | -0.4504 | Phenylpiperidine derivatives | Only 27.1% female-biased vs class 65.3% |
| RIMEGEPANT | 12 | 0.0% | -0.9635 | Calcitonin gene-related peptide (CGRP) antagonists | Only 0.0% female-biased vs class 65.3% |
| RIZATRIPTAN | 15 | 13.3% | -1.2305 | Selective serotonin (5HT1) agonists | Only 13.3% female-biased vs class 65.3% |
| SUMATRIPTAN | 57 | 21.1% | -0.5148 | Selective serotonin (5HT1) agonists | Only 21.1% female-biased vs class 65.3% |
| UBROGEPANT | 3 | 0.0% | -1.0867 | Calcitonin gene-related peptide (CGRP) antagonists | Only 0.0% female-biased vs class 65.3% |
| ZICONOTIDE | 8 | 37.5% | -0.1868 | Other analgesics and antipyretics | Only 37.5% female-biased vs class 65.3% |
| ZOLMITRIPTAN | 7 | 14.3% | -1.3226 | Selective serotonin (5HT1) agonists | Only 14.3% female-biased vs class 65.3% |

---
## C07: Beta Blocking Agents

**12 drugs | 1,003 signals | Class trend: female_higher**
- Female-higher: 529 (52.7%)
- Male-higher: 474 (47.3%)
- Mean log-ratio: +0.0516 | Median: +0.5194 | SD: 1.0210
- Within-class variation: High heterogeneity (CV=0.514, range 0.0%--83.3%)

### Top 5 Female-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| BISOPROLOL | Haemarthrosis | +3.350 | 28.20 | 0.99 | 42 | 12 |
| ACEBUTOLOL | Toxicity to various agents | +2.934 | 79.37 | 4.22 | 317 | 12 |
| BISOPROLOL | Arterial occlusive disease | +2.917 | 40.64 | 2.20 | 129 | 13 |
| ATENOLOL | Haemoglobin decreased | +2.903 | 6.75 | 0.37 | 216 | 10 |
| BISOPROLOL | Vital capacity decreased | +2.803 | 756.22 | 45.86 | 94 | 14 |

### Top 5 Male-Biased Signals

| Drug | Adverse Event | Log Ratio | ROR_F | ROR_M | N_F | N_M |
|------|--------------|----------:|------:|------:|----:|----:|
| LABETALOL | Abortion spontaneous | -5.679 | 7.91 | 2315.89 | 48 | 15 |
| LABETALOL | Polyhydramnios | -3.113 | 75.20 | 1690.75 | 10 | 11 |
| PROPRANOLOL | Sedation | -2.773 | 2.65 | 42.34 | 32 | 288 |
| BETAXOLOL | Hypersensitivity | -2.751 | 4.56 | 71.44 | 18 | 64 |
| PROPRANOLOL | Multiple sclerosis | -2.204 | 0.35 | 3.20 | 12 | 28 |

### Most Consistent AE Patterns (across drugs)

| Adverse Event | # Drugs | Consistency | Direction | Mean LR |
|--------------|--------:|------------:|-----------|--------:|
| Angioedema | 5 | 100% | female_higher | +1.0152 |
| Adverse drug reaction | 4 | 100% | female_higher | +0.8882 |
| Medication error | 4 | 100% | female_higher | +0.8464 |
| Drug ineffective | 3 | 100% | female_higher | +1.2192 |
| Blood thyroid stimulating hormone increased | 3 | 100% | male_higher | -1.5830 |
| Drug abuse | 3 | 100% | female_higher | +1.1932 |
| Lactic acidosis | 3 | 100% | male_higher | -1.2776 |

### Drug Profiles

| Drug | Signals | %Female | Mean LR | Subclass |
|------|--------:|--------:|--------:|----------|
| BISOPROLOL | 270 | 60.4% | +0.2237 | Beta blocking agents, selective |
| METOPROLOL | 244 | 53.7% | +0.0868 | Beta blocking agents, selective |
| ATENOLOL | 136 | 66.2% | +0.3517 | Beta blocking agents, selective |
| PROPRANOLOL | 123 | 27.6% | -0.4733 | Beta blocking agents, non-selective |
| CARVEDILOL | 112 | 52.7% | +0.0204 | Alpha and beta blocking agents |
| NEBIVOLOL | 38 | 50.0% | +0.0244 | Beta blocking agents, selective |
| SOTALOL | 24 | 58.3% | +0.1928 | Beta blocking agents, non-selective |
| LABETALOL | 22 | 18.2% | -1.0996 | Alpha and beta blocking agents |
| TIMOLOL | 15 | 46.7% | -0.1328 | Beta blocking agents, non-selective |
| NADOLOL | 12 | 25.0% | -0.5520 | Beta blocking agents, non-selective |
| ACEBUTOLOL | 6 | 83.3% | +1.3865 | Beta blocking agents, selective |
| BETAXOLOL | 1 | 0.0% | -2.7507 | Beta blocking agents |

### Paradoxical Drugs (Against Class Trend)

| Drug | Signals | %Female | Mean LR | Subclass | Note |
|------|--------:|--------:|--------:|----------|------|
| LABETALOL | 22 | 18.2% | -1.0996 | Alpha and beta blocking agents | Only 18.2% female-biased vs class 52.7% |
| NADOLOL | 12 | 25.0% | -0.5520 | Beta blocking agents, non-selective | Only 25.0% female-biased vs class 52.7% |
| PROPRANOLOL | 123 | 27.6% | -0.4733 | Beta blocking agents, non-selective | Only 27.6% female-biased vs class 52.7% |

---
## Key Findings & Interpretation

### Sex-Differential Patterns by Therapeutic Area

1. **Cardiovascular drugs** (C07, C09, C10): Examine whether blood pressure and lipid
   management show consistent female vs male safety profiles
2. **Analgesics/Anti-inflammatories** (M01, N02): Pain management drugs may show
   sex differences due to pharmacokinetic factors (body weight, fat distribution)
3. **Psychoanaleptics** (N06): Known sex differences in depression/anxiety prevalence
   may confound pharmacovigilance signals
4. **Antineoplastics** (L01): The largest class -- cancer drug toxicity profiles
   vary substantially by sex, mechanism, and tumor type

### Methodological Notes

- **Log ratio**: log2(ROR_female / ROR_male). Positive = female-biased, negative = male-biased
- **Paradoxical drugs**: Drugs whose sex-differential pattern opposes the class majority
  (requires 3+ signals and <40% or >60% alignment with class trend)
- **Consistency**: Fraction of drugs showing the same direction for a given AE
- **Within-class CV**: Coefficient of variation of per-drug %female-higher scores

---
*Analysis performed on 2026-03-04 using SexDiffKG v4 signals*