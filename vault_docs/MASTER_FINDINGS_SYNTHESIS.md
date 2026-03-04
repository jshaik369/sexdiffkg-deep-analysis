# SexDiffKG Master Findings Synthesis
## Complete Analysis Summary — 2026-03-04

### Project Overview
- **SexDiffKG v4**: 109,867 nodes / 1,822,851 edges
- **FAERS**: 14,536,008 reports (F:8,744,397 / M:5,791,611), 87 quarters
- **Sex-differential signals**: 96,281 (51,771 female_higher / 44,510 male_higher)
- **Drugs**: 2,178 with signals / 3,920 in KG
- **Adverse Events**: 5,069 with signals / 9,949 in KG
- **Best Model**: ComplEx v4 (MRR 0.2484, Hits@10 40.69%)

---

## TEN MAJOR FINDINGS

### 1. THE CARDIAC REVERSAL PHENOMENON
Drug-induced cardiac AEs are **67% female-biased** despite CVD being epidemiologically male-predominant.
- Sudden cardiac death: 100% F | Cardiac arrest: 85% F | MI: 82% F
- Palpitations: sole male-biased cardiac AE (82% M)
- 2,187 signals, 760 drugs
- **Impact**: Challenges the assumption that cardiac safety is primarily a male concern

### 2. SYSTEMATIC OPIOID FEMALE VULNERABILITY
75% of opioid AE signals are female-higher across 17 drugs.
- Full mu-agonists (oxycodone 85%, morphine 83%) >> partial agonists (buprenorphine 54%)
- Drug hypersensitivity consistently female across 11 opioids
- **Mechanism**: Receptor-level sex difference — partial agonism reduces female vulnerability
- **Impact**: Supports sex-specific opioid dosing guidelines

### 3. CHECKPOINT INHIBITOR irAE FEMALE BIAS
ALL immune-related AEs are 100% female-higher across all 8 checkpoint inhibitors.
- Myocarditis, hypophysitis, thyroiditis — all exclusively female-biased
- Overall CPI signals: 74.6% female
- Oncology cardiotoxicity: 84.6% female across all drug classes
- **Impact**: First large-scale evidence of systematic female irAE vulnerability

### 4. ANTI-CD20 PARADOX (Same Mechanism, Opposite Bias)
Anti-CD20 antibodies show OPPOSITE sex bias depending on disease treated:
- Rituximab (RA/lymphoma): 66.6% female
- Ocrelizumab (MS): 28.7% female
- Ofatumumab (MS): 11.9% female
- **Mechanism**: Indication (disease population) drives sex bias more than drug mechanism
- **Impact**: Demonstrates confounding by indication in pharmacovigilance sex analyses

### 5. HEPATOTOXICITY: 2:1 FEMALE PREDOMINANCE
Drug-induced liver injury shows systematic female vulnerability (66.7% overall).
- DILI: 78% F | Cirrhosis: 88% F | Hepatic failure: 74% F
- Paradox: Hepatic steatosis (43% F) and fibrosis (13% F) are male-biased
- Risperidone hepatotoxicity: 100% F (17 signals)
- **Impact**: Female-specific DILI monitoring protocols needed

### 6. PSYCHOTROPIC MECHANISM-DEPENDENT SEX BIAS
Different receptor mechanisms produce different sex bias patterns:
- D2 antagonists (antipsychotics): 64.8% F — risperidone 92.9% F
- GABA modulators (benzos): 65.3% F — diazepam 76.4% F
- 5-HT modulators (SSRIs): 42.2% F — slightly male-biased
- **Mechanism**: Receptor type determines sex-differential AE vulnerability
- Antipsychotic paradoxes: NMS 100% F, metabolic syndrome 100% F, BUT weight gain 0% F

### 7. DEATH IS 74% FEMALE
Drug-related mortality reporting shows 3:1 female predominance.
- 251 female-higher death signals vs 86 male-higher
- Persists across drug classes
- **Impact**: Most alarming finding — female drug safety deserves urgent attention

### 8. TEMPORAL INSTABILITY: 42.3% OF SIGNALS REVERSED
Over 13 years (2013-2025), nearly half of sex-differential signals reversed direction.
- COVID era (2020-2022) caused major inflection: female% dropped from 62% to 55%
- 418 AEs consistently female across ALL 5 eras (most robust signals)
- 609 AEs consistently male across ALL 5 eras
- **Impact**: Static sex-differential analyses may be misleading; temporal stratification essential

### 9. PAN-THERAPEUTIC FEMALE VULNERABILITY
8/11 ATC Level 1 drug classes show female-biased AE reporting.
- Systemic hormones most F-biased: 65.0%
- Antiparasitics most M-biased: 36.3%
- Overall distribution: 53.8% female-higher signals
- **Impact**: Female AE vulnerability is NOT limited to specific drug classes

### 10. KG EMBEDDINGS PREDICT NOVEL SEX-DIFFERENTIAL SIGNALS
ComplEx model scored 26.6M novel drug-AE pairs for sex-differential potential.
- Top 100 predictions include clinically plausible candidates
- 46/100 have existing has_adverse_event edges (known association predicted to be sex-differential)
- AE nodes occupy highest-norm embedding positions (most distinctive)
- **Impact**: KG structure can generate testable hypotheses for sex-differential safety

---

## PUBLICATION PIPELINE (Priority Order)

| # | Paper | Target Journal | IF | Status |
|---|-------|---------------|-----|--------|
| 1 | Data Descriptor (KG + methods) | Scientific Data | 5.8 | Manuscript ~90% done |
| 2 | ISMB 2026 Abstract | ISMB/ECCB | -- | Submitted |
| 3 | Cardiac Reversal | CPT / Circulation | 6.3/37.8 | Analysis complete |
| 4 | Opioid Female Vulnerability | Anesthesiology | 8.8 | Analysis complete |
| 5 | CPI irAE Female Bias | JCO / Ann Oncol | 45.3/32.0 | Analysis complete |
| 6 | Temporal Instability | Pharmacoepidemiol Drug Saf | 3.2 | Analysis complete |
| 7 | Hepatotoxicity Sex Diff | Hepatology | 17.3 | Analysis complete |
| 8 | Psychotropic Mechanism-Dependent | Biol Psychiatry | 12.8 | Analysis complete |
| 9 | Anti-CD20 Paradox | Drug Safety | 4.0 | Analysis complete |
| 10 | KG Embedding Predictions | Brief Bioinform | 9.5 | Analysis complete |
| 11 | Autoimmune Indication Effect | Arthritis Rheumatol | 13.3 | Analysis complete |

---

## ANALYSIS INVENTORY

### JSON Results (results/analysis/)
1. cardiac_reversal_analysis.json
2. opioid_sex_diff_analysis.json
3. atc_soc_analysis.json
4. psychotropic_sex_diff.json
5. global_signal_rankings.json
6. autoimmune_sex_diff.json
7. hepatotoxicity_sex_diff.json
8. oncology_sex_diff.json
9. high_confidence_signals.json
10. embedding_predictions.json + embedding_predictions_top100.tsv
11. temporal_trend_analysis.json
12. network_centrality.json

### Supplementary Data (data/processed/)
- atc_drug_classification.csv (4,569)
- atc_who_full.csv (7,345)
- atc_who_hierarchy.csv (6,030)
- drug_indications.csv (59,954)
- kg_drug_atc_mapping.csv (2,665)
- ae_soc_mapping.csv (9,949)

### Vault Documents (16 total)
- MASTER_FINDINGS_SYNTHESIS.md (this file)
- Clinical_Findings.md (corrected)
- ATC_SOC_Analysis.md
- Psychotropic_Analysis.md
- Global_Signal_Rankings.md
- Autoimmune_Analysis.md
- Hepatotoxicity_Analysis.md
- Embedding_Predictions.md
- Oncology_Analysis.md
- High_Confidence_Signals.md
- Temporal_Trends.md
- Network_Centrality.md
- Publication_Strategy.md
- Publication_Roadmap.md
- bioRxiv_Competitor_Scan.md
- Full_Project_Inventory.md

---

## COMPETITIVE ADVANTAGE

No published work combines ALL of:
1. Sex-stratified pharmacovigilance (96,281 signals from 14.5M reports)
2. Multi-relational knowledge graph (6 entity types, 6 edge types)
3. KG embedding-based predictions (ComplEx MRR 0.2484)
4. Temporal trend analysis (13 years, 5 eras)
5. ATC/SOC cross-classification
6. Network centrality analysis

Closest competitor AwareDX (Chandak 2020): 20,817 signals, no KG, no embeddings, no temporal analysis. SexDiffKG has 4.6x more signals and adds 4 analytical dimensions.

---

*Generated 2026-03-04. Direction values: female_higher/male_higher (corrected).*
*Author: Mohammed Javeed Akhtar Abbas Shaik (J.Shaik), CoEvolve Network*
