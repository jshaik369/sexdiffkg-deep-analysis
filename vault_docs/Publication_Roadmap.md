# SexDiffKG — Complete Publication Roadmap
## Generated: 2026-03-04 | Based on vault audit + literature review + signal analysis

## EXECUTIVE SUMMARY

SexDiffKG has **at least 10 distinct publishable papers** based on existing completed analyses.
The project is uniquely positioned: **no existing work combines sex-stratified pharmacovigilance, multi-relational KG, and KG embeddings**. The closest competitor (AwareDX, 2020) identified 5x fewer signals without any KG structure.

---

## PUBLICATION 1: Data Descriptor (PRIMARY — Submit First)

**Title:** "SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph Integrating 14.5 Million FAERS Reports with Multi-Omics Molecular Data"
**Target:** Scientific Data (IF 6.9)
**Status:** MANUSCRIPT COMPLETE (672 lines), cover letter ready, ISMB abstract submitted
**What's needed to submit:**
1. Upload v4 data to Zenodo (currently only v3)
2. Generate PDF figures (currently PNG only)
3. Register on FAIRsharing.org
4. Final proofread with v4 numbers verified
**Timeline:** 2-3 days of work → submit

---

## PUBLICATION 2: Pharmacovigilance Methods Paper

**Title:** "Sex-Stratified Disproportionality Analysis of 14.5 Million FAERS Reports: 96,281 Sex-Differential Drug Safety Signals"
**Target:** Drug Safety (IF 3.65) — published DiAna, READUS-PV
**Novel contributions:**
- Largest sex-stratified FAERS analysis ever (96,281 signals vs AwareDX's 20,817)
- DiAna-normalized (most studies skip rigorous drug name normalization)
- READUS-PV compliant methodology
- v4.2 quality controls: Haldane correction, Woolf 95% CI, BH FDR, chi-squared
**Existing materials:** Statistical tests (results/analysis/statistical_tests_v4.json), signal parquets, validation benchmarks
**What's needed:** Write focused methods paper emphasizing pharmacovigilance methodology
**Timeline:** 1-2 weeks writing

---

## PUBLICATION 3: Clinical Findings — Drug-Induced Cardiac Sex Differences

**Title:** "Sex Differences in Drug-Induced Cardiac Events: The Reversal Phenomenon from 14.5 Million FAERS Reports"
**Target:** Clinical Pharmacology & Therapeutics (IF 5.5) or JAMA Internal Medicine
**THE KEY FINDING:**
- Drug-induced MI: 82.4% female-biased across 182 drugs (general pop is male-predominant)
- Cardiac arrest: 84.8% female, Sudden cardiac death: 100% female
- This is the "reversal phenomenon" — pharmacological perturbation exposes female cardiac vulnerability
- Counter-intuitive, clinically impactful, and novel
**Existing materials:** Signal data in sex_differential_v4.parquet
**What's needed:** Deep-dive analysis + clinical interpretation manuscript
**Timeline:** 2-3 weeks

---

## PUBLICATION 4: Opioid Sex Differences

**Title:** "Systematic Female Vulnerability to Opioid Adverse Effects: Evidence from a 21-Year Pharmacovigilance Analysis"
**Target:** Anesthesiology (IF 9.1) or Pain (IF 5.6)
**Key findings:**
- Every major opioid shows female-biased signal profile (69-81% female)
- Oxycodone: 598 signals, 81.1% female, strongest effect
- Age-dependent: female bias drops from 88% (18-44) to 40% (65+) — age-sex interaction data already exists
- Male-biased: "Psychological trauma" consistently male across all opioids
**Existing materials:** Signal analysis + age_sex_interaction_v4.json + per_country analysis
**Timeline:** 2 weeks

---

## PUBLICATION 5: Antipsychotic Sex Differences (Risperidone Focus)

**Title:** "Risperidone Shows Extreme Sex-Differential Safety Profile Among Antipsychotic Drugs: A Pharmacovigilance Knowledge Graph Analysis"
**Target:** Schizophrenia Bulletin (IF 7.3) or World Psychiatry (IF 73.3 — if strong enough)
**Key finding:** Risperidone 93% female-biased (518 signals) vs other antipsychotics 47-69%
- Extends beyond prolactin-related AEs to cardiac, metabolic, emotional
- ClinicalTrials.gov gap analysis shows 0 trials examining sex-differential antipsychotic ADRs
**Existing materials:** Signal data + MentalHealth-KG feasibility + clinical trials cross-ref
**Timeline:** 2-3 weeks

---

## PUBLICATION 6: Age-Sex Interaction Paper

**Title:** "Age-Dependent Reversal of Sex-Differential Drug Safety Signals: Evidence from FAERS"
**Target:** Biology of Sex Differences (IF 5.1)
**NOVEL FINDING:**
- Female ADR bias drops from 63.2% (18-44) to 49.3% (65+)
- Opioids flip from 88% F to 40% F with age
- Antipsychotics show similar reversal
- Mechanism likely: hormonal changes, altered PK, prescribing patterns
**Existing materials:** COMPLETE (age_sex_interaction_v4.json in results/)
**Timeline:** 1-2 weeks writing

---

## PUBLICATION 7: 62-Country Geographic Variation

**Title:** "Geographic Variation in Sex-Differential Drug Safety Signals Across 62 Countries"
**Target:** Drug Safety (IF 3.65) or Pharmacoepidemiology and Drug Safety
**NOVEL FINDING:**
- 3.2x variation in female-bias across countries
- Japan paradox: 47% female reporters but 55% female-biased signals → reporting bias doesn't explain the pattern
- Checkpoint inhibitors: universal female bias (51-92% across 40+ countries)
- SSRIs: universal male bias despite female prescribing dominance
**Existing materials:** COMPLETE (per_country_deep_analysis_v4.json, 62 countries, 9 drug classes)
**Timeline:** 1-2 weeks writing

---

## PUBLICATION 8: KG Embedding + Link Prediction

**Title:** "Knowledge Graph Embeddings Predict Novel Sex-Differential Drug Safety Signals via Drug-Target-Pathway Integration"
**Target:** Briefings in Bioinformatics (IF 7.7), cover letter already written
**Key findings:**
- ComplEx MRR 0.2484, 3 models compared
- 71.6M triples scored, 500 top predictions curated
- 84 truly novel predictions, 143 known-association predictions
- Enriched for oncology drugs and substance-related conditions
**Existing materials:** COMPLETE (link prediction results, model comparison, drug clustering)
**Timeline:** 2-3 weeks writing

---

## PUBLICATION 9: Corticosteroid Sex Differences

**Title:** "Sex-Differential Corticosteroid Safety Profiles: Implications for Dose-Optimization"
**Target:** Annals of Internal Medicine or Clinical Pharmacology & Therapeutics
**Key findings:**
- ALL corticosteroids show 70-82% female-biased signals
- Prednisone: 926 signals (most of any drug), 70.2% female
- Prednisolone: 82.5% female, Dexamethasone: 80.3% female
- Given how widely prescribed they are, sex-differential dosing could have massive clinical impact
**Existing materials:** Signal data ready
**Timeline:** 2 weeks

---

## PUBLICATION 10: Biologic DMARD Mechanism-Specific Sex Patterns

**Title:** "Immune Mechanism of Action Determines Sex-Differential Safety of Biologic DMARDs"
**Target:** Annals of the Rheumatic Diseases (IF 20.3) or Arthritis & Rheumatology (IF 11.4)
**Key finding:**
- Anti-CD20 (rituximab): 66.6% female
- Anti-TNF (adalimumab): 61.8% MALE
- JAK inhibitors: 75% MALE
- Mechanism-specific, not class-wide → B-cell vs JAK-STAT sex differences
**Existing materials:** Signal data + drug class analysis + target analysis
**Timeline:** 2-3 weeks

---

## PRIORITY ORDER (by impact × feasibility)

| Priority | Paper | Target Journal | IF | Effort | Impact |
|:---:|---|---|:---:|---|---|
| 1 | Data Descriptor | Scientific Data | 6.9 | LOW (manuscript done) | HIGH (establishes resource) |
| 2 | Cardiac Reversal | CPT / JAMA Int Med | 5.5-39 | MEDIUM | VERY HIGH (counter-intuitive) |
| 3 | Opioid Sex Diff | Anesthesiology | 9.1 | MEDIUM | HIGH (opioid crisis timely) |
| 4 | 62-Country Geographic | Drug Safety | 3.65 | LOW (data ready) | HIGH (refutes reporting bias) |
| 5 | Age-Sex Interaction | Biol Sex Diff | 5.1 | LOW (data ready) | HIGH (novel reversal) |
| 6 | PV Methods | Drug Safety | 3.65 | MEDIUM | MEDIUM (methodology) |
| 7 | Risperidone/Antipsychotic | Schizophr Bull | 7.3 | MEDIUM | HIGH (clinical) |
| 8 | KG Embeddings | Brief Bioinform | 7.7 | MEDIUM | MEDIUM (computational) |
| 9 | Corticosteroid | Ann Int Med | 39.2 | MEDIUM | HIGH (if accepted) |
| 10 | Biologic DMARDs | Ann Rheum Dis | 20.3 | MEDIUM | HIGH (if accepted) |

---

## IMMEDIATE ACTIONS (This Session)

1. ✅ Vault audit complete
2. ✅ Literature landscape complete
3. ✅ Signal analysis complete
4. ⏳ ATC classification download (enriches drug class analysis)
5. ⏳ KG structure analysis (enriches data descriptor)
6. ⏳ bioRxiv competitor scan (citation opportunities)
7. → Upload v4 to Zenodo
8. → Generate v4 PDF figures
9. → Start cardiac reversal paper (highest impact new finding)

---

## SUPPLEMENTARY DATASETS TO ACQUIRE

| Dataset | Purpose | Status |
|---|---|---|
| ATC drug classification | Drug class enrichment | Extracting from ChEMBL |
| Drug indications (ChEMBL) | Indication-stratified analysis | Extracting from ChEMBL |
| MedDRA hierarchy | AE grouping by SOC/HLT | Needs subscription or FAERS mapping |
| JADER (Japan) | Cross-country validation | Needs manual download (CAPTCHA) |
| FDA drug labels | Sex-specific warnings as ground truth | Available via DailyMed API |
| DrugBank ATC codes | Additional drug classification | Academic license (free) |
