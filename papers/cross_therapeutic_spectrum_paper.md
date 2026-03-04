# The Sex-Differential Drug Safety Spectrum: A Pan-Therapeutic Analysis of 96,281 Pharmacovigilance Signals Across 19 Drug Classes

## Authors
Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
CoEvolve Network, Independent Researcher, Barcelona, Spain
ORCID: 0009-0002-1748-7516

## Abstract

**Background:** Sex differences in adverse drug reactions are well-documented for individual drugs but rarely quantified across therapeutic areas simultaneously. We present the first comprehensive pan-therapeutic mapping of sex-differential drug safety signals.

**Methods:** Using 14.5 million FAERS reports (2004Q1–2025Q3), we computed sex-stratified reporting odds ratios for 2,178 drugs across 5,069 adverse events, yielding 96,281 sex-differential signals. We analyzed sex bias patterns across 19 major drug classes encompassing cardiovascular, psychiatric, pain, endocrine, anti-infective, autoimmune, dermatological, and ophthalmological therapeutics.

**Results:** The pan-therapeutic sex spectrum spans from 83% female (CGRP migraine agents) to 15% female (S1P modulators), a 68-percentage-point range. Key findings:

1. **Pain therapeutics** show a female-biased gradient: CGRP agents (83%F) > NSAIDs (67%F) > opioids (62%F) > cannabinoids (44%F, male-leaning). Within strong opioids, morphine (67%F) differs from oxymorphone (45%F) by 22pp despite identical receptor targets.

2. **Cardiovascular drugs** span 29pp: ERA/prostacyclin PAH drugs (71%F) reflect female-predominant disease, while ARNI (42%F) and antiarrhythmics (47%F) lean male. DOACs are remarkably uniform (53-56%F, 3pp spread). Beta-blockers show carvedilol (46%F) vs atenolol (66%F) — 20pp within the same mechanism class.

3. **Endocrine drugs** reveal that GLP-1 agonists are female-biased (58%F) with tirzepatide highest (65%F); SGLT2 inhibitors are near-balanced (48%F); osteoporosis drugs are heavily female (72-92%F) dominated by prescribing bias in an F-predominant disease.

4. **Anti-infectives** show tetracyclines (68%F) as most female-biased antibiotic class, while carbapenems (51%F) are balanced. HIV antiretrovirals are male-biased (42%F) reflecting patient demographics. Anti-infective allergy signals are 71%F while nephrotoxicity is 45%F.

5. **Psychiatric drugs** reveal the most extreme within-class spreads: atypical antipsychotics span 90pp (risperidone 93%F → cariprazine 3%F), and ADHD stimulants span 51pp (methylphenidate 78%F → dexamfetamine 15%F).

6. **Autoimmune drugs** show anti-CD20 spanning 60pp (ofatumumab 12%F → obinutuzumab 72%F) and JAK inhibitors spanning 46pp, despite shared mechanisms.

**Conclusions:** Sex-differential safety profiles vary more within drug classes than between them — within-class spreads (up to 90pp) often exceed between-class differences. This challenges the assumption that mechanism of action determines sex-differential safety. The 68pp pan-therapeutic spectrum, from CGRP migraine agents to S1P modulators, demonstrates that sex-specific pharmacovigilance should be mandatory across all therapeutic areas.

**Keywords:** sex differences, pharmacovigilance, FAERS, drug safety, adverse drug reactions, pan-therapeutic

## 1. Introduction

Sex differences in adverse drug reactions represent one of the most significant yet underaddressed challenges in pharmacotherapy. While individual drug-AE pairs have been studied, the broader landscape — how sex-differential safety varies across and within therapeutic areas — remains uncharacterized.

We present SexDiffKG, a knowledge graph integrating 14,536,008 FAERS reports with molecular target, pathway, and tissue expression data. Our analysis of 96,281 sex-differential signals across 2,178 drugs enables the first comprehensive mapping of the pan-therapeutic sex spectrum.

## 2. Methods

### 2.1 Data Sources
- **FAERS:** 14,536,008 deduplicated reports (F:8,744,397, M:5,791,611), 87 quarters (2004Q1–2025Q3)
- **Drug normalization:** DiAna dictionary (846,917 mappings, 53.9% resolution)
- **Molecular targets:** ChEMBL 36 (12,682 drug-target edges)
- **Protein interactions:** STRING v12.0 (473,860 PPI edges)
- **Pathways:** Reactome (370,597 participates_in edges)
- **Tissue expression:** GTEx v8 (289 sex-differential expression edges)

### 2.2 Sex-Differential Signal Detection
Sex-stratified reporting odds ratios (ROR) were computed independently for male and female FAERS populations. A drug-AE pair was classified as sex-differential if the log(ROR_female/ROR_male) was statistically significant (p < 0.05 with Bonferroni correction) and had at least 5 reports per sex.

### 2.3 Drug Classification
Drugs were classified into 19 major therapeutic classes and 80+ subclasses based on ATC codes and mechanism of action. Within-class sex bias spread was computed as max(%F) - min(%F) across drugs with ≥5 signals.

## 3. Results

### 3.1 Pan-Therapeutic Sex Spectrum
The global mean across 96,281 signals is 53.8% female, but this masks enormous variation:
- **Most female-biased:** CGRP migraine agents (83%F), antihistamines (73%F), osteoporosis drugs (73%F)
- **Near balanced:** Statins (52%F), SGLT2 inhibitors (48%F), carbapenems (51%F)
- **Male-biased:** HIV antiretrovirals (42%F), cannabinoids (44%F), S1P modulators (15%F)

### 3.2 Pain & Migraine
Among migraine drugs, CGRP agents (83%F) show 16pp more female bias than triptans (67%F) despite treating the same condition. Erenumab (92%F) is the most female-biased migraine drug.

Cannabinoids (44%F) are the only male-leaning pain class, contrasting sharply with conventional pain drugs (65%F) — a 20pp gap.

### 3.3 Cardiovascular
PAH drugs reflect disease epidemiology: ERAs (71%F) and prostacyclins (70%F) vs PDE5 inhibitors (55%F). Among beta-blockers, carvedilol (46%F, alpha+beta) differs from atenolol (66%F, beta-1 selective) by 20pp, suggesting receptor selectivity influences sex-differential safety.

DOACs show the tightest within-class agreement (3pp) of any analyzed drug class.

### 3.4 Endocrine & Metabolic
GLP-1 agonists range from tirzepatide (65%F) to liraglutide (50%F). Corticosteroid metabolic AEs (76%F) and psychiatric AEs (74%F) are strongly female-biased while infection AEs (53%F) are balanced.

### 3.5 Anti-Infectives
Tetracyclines (68%F) are the most female-biased antibiotic class. Anti-infective allergy (71%F) is strongly female while nephrotoxicity (45%F) and tendon damage (41%F) are male-biased.

### 3.6 Within-Class Variation
The most striking finding is that within-class sex bias variation often exceeds between-class variation:
| Drug Class | Spread (pp) | Min Drug | Max Drug |
|-----------|-------------|----------|----------|
| Atypical antipsychotics | 90 | Cariprazine (3%F) | Risperidone (93%F) |
| Triptans | 65 | Almotriptan (12%F) | Sumatriptan (77%F) |
| Anti-CD20 | 60 | Ofatumumab (12%F) | Obinutuzumab (72%F) |
| ADHD stimulants | 51 | Dexamfetamine (15%F) | Methylphenidate (78%F) |
| JAK inhibitors | 46 | Upadacitinib (24%F) | Ruxolitinib (70%F) |
| CCBs | 43 | Nimodipine (28%F) | Diltiazem (70%F) |
| Muscle relaxants | 39 | Dantrolene (40%F) | Cyclobenzaprine (79%F) |
| Corticosteroids | 37 | Fludrocortisone (37%F) | Triamcinolone (75%F) |
| Retinoids | 34 | Acitretin (43%F) | Adapalene (77%F) |
| NSAIDs | 32 | Flurbiprofen (48%F) | Piroxicam (80%F) |

## 4. Discussion

The 68pp pan-therapeutic spectrum (CGRP agents 83%F to S1P modulators 15%F) demonstrates that sex-differential drug safety is not random — it follows systematic patterns driven by disease demographics, molecular targets, and pharmacokinetic sex differences.

The finding that within-class spreads (up to 90pp) exceed between-class differences challenges mechanism-centric models of sex-differential safety. Drugs sharing primary targets (e.g., all atypical antipsychotics target D2/5-HT2A) can show completely opposite sex-bias profiles. This suggests secondary pharmacology, pharmacokinetics, and indication-specific factors drive sex-differential safety more than primary mechanism.

### 4.1 Limitations
- FAERS is a spontaneous reporting system subject to reporting biases
- Reporter demographics may not perfectly reflect patient demographics
- Sex-differential signals reflect disproportionality, not causal risk

### 4.2 Clinical Implications
- DOACs are the safest cardiovascular class for sex-balanced prescribing (3pp spread)
- Within-class switching may alter sex-differential safety profiles dramatically
- Regulatory agencies should require sex-stratified safety analyses for all drug classes

## 5. Conclusion

We present the first comprehensive pan-therapeutic mapping of sex-differential drug safety across 19 drug classes and 96,281 signals. The extraordinary within-class variation (up to 90pp) demonstrates that sex-differential safety cannot be predicted from mechanism of action alone and must be individually characterized for every approved drug.

## Data Availability
SexDiffKG v4: https://github.com/jshaik369/sexdiffkg-deep-analysis
