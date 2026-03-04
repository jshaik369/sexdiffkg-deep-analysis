# Sex-Specific Drug Safety Warnings Are Needed for 187 Medications: Evidence from 14.5 Million FDA Adverse Event Reports

## Authors
Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)¹

¹CoEvolve Network, Independent Researcher, Barcelona, Spain

Correspondence: jshaik@coevolvenetwork.com
ORCID: 0009-0002-1748-7516

## Abstract

### Importance
Drug labels rarely include sex-specific safety information despite known biological differences in drug metabolism, distribution, and adverse event profiles between women and men.

### Objective
To systematically identify medications with significant sex-differential adverse event profiles warranting sex-specific safety warnings using a comprehensive knowledge graph approach.

### Design, Setting, and Participants
Cross-sectional analysis of the FDA Adverse Event Reporting System (FAERS), encompassing 14,536,008 deduplicated reports (8,744,397 female; 5,791,611 male) spanning 87 quarters from 2004 Q1 through 2025 Q3. Sex-stratified reporting odds ratios (ROR) were computed for all drug-adverse event pairs meeting minimum reporting thresholds. A knowledge graph integrating FAERS signals with protein targets (ChEMBL 36), protein-protein interactions (STRING v12.0), biological pathways (Reactome), and tissue-specific gene expression (GTEx v8) was constructed to provide mechanistic context.

### Main Outcomes and Measures
Drugs were classified as requiring sex-specific warnings based on stringent criteria: (1) ≥80% of sex-differential signals biased toward one sex, (2) ≥10 qualifying adverse event signals, (3) mean absolute log-ratio ≥0.5 (corresponding to ≥1.6-fold ROR difference), and (4) signals spanning ≥3 MedDRA System Organ Classes.

### Results
Among 2,178 drugs with sex-differential signals, 187 (8.6%) met all four criteria for sex-specific warnings: 113 requiring enhanced female monitoring and 74 requiring enhanced male monitoring. These 187 drugs collectively account for 23,847 sex-differential signals (24.8% of the total 96,281 signals identified). Key findings include:

**Female-warning drugs (n=113):** Predominantly cardiovascular agents (amlodipine, atorvastatin, metoprolol), neuropsychiatric medications (gabapentin, pregabalin, duloxetine), and immunomodulators (adalimumab, etanercept). Sudden cardiac death signals were 94.6% female-biased across 17 cardiovascular drugs. All checkpoint inhibitor immune-related adverse events (irAEs) showed 100% female bias.

**Male-warning drugs (n=74):** Concentrated in anti-infective agents (fluoroquinolones, azithromycin), oncology drugs (docetaxel, carboplatin), and hormonal therapies. Hepatotoxicity signals were 78% female-biased but renal toxicity was 67% male-biased.

The anti-regression pattern — where sex-differential effect sizes increase rather than attenuate with larger sample sizes (Spearman ρ=+0.258, P<10⁻¹⁵) — validates that these signals reflect genuine biological differences rather than statistical noise.

### Conclusions and Relevance
Nearly one in eleven drugs with pharmacovigilance data shows a pattern of sex-differential adverse events meeting stringent criteria for sex-specific safety warnings. Current drug labels largely fail to communicate these differences. Regulatory agencies should mandate sex-stratified safety analyses and consider updating labels for the 187 identified medications. The knowledge graph approach enables mechanistic prioritization by linking observed sex differences to biological pathways and molecular targets.

**Keywords:** sex differences, drug safety, pharmacovigilance, adverse events, FAERS, knowledge graph, regulatory science, sex-specific medicine

---

## Introduction

The biological basis for sex differences in drug response is well established. Women have higher body fat percentage, lower hepatic CYP3A4 activity relative to body weight, slower gastric emptying, and distinct immune profiles compared to men.¹⁻³ These pharmacokinetic and pharmacodynamic differences translate to clinically meaningful variations in adverse event profiles. Yet drug labels remain largely sex-agnostic, and the 2014 FDA mandate for sex-stratified clinical trial reporting has produced limited downstream changes to prescribing information.⁴

Previous pharmacovigilance studies have identified sex differences for individual drug classes — fluoroquinolones,⁵ statins,⁶ opioids,⁷ and immune checkpoint inhibitors⁸ — but no systematic, data-driven assessment has quantified how many drugs across all therapeutic classes warrant sex-specific safety warnings.

We constructed SexDiffKG, a sex-differential drug safety knowledge graph integrating 14.5 million FAERS reports with molecular target data, protein interaction networks, biological pathway annotations, and tissue-specific gene expression. Using this resource, we identify 187 medications meeting stringent criteria for sex-specific safety warnings and characterize the biological mechanisms underlying these sex differences.

## Methods

### Data Sources and Knowledge Graph Construction

SexDiffKG v4 comprises 109,867 nodes and 1,822,851 edges integrating six data sources:

1. **FAERS** (2004 Q1–2025 Q3): 14,536,008 deduplicated reports after case-level deduplication by FDA case ID, with demographic extraction and indication mapping. Drug names were normalized using the DiAna dictionary (846,917 mappings, 53.9% resolution to standardized names).

2. **ChEMBL 36**: 12,682 drug–protein target interactions with binding affinity data.

3. **STRING v12.0**: 473,860 protein–protein interaction edges (combined score ≥700).

4. **Reactome**: 370,597 gene/protein–pathway participation edges across 2,279 biological pathways.

5. **GTEx v8**: 289 sex-differential gene expression edges derived from tissue-specific differential expression analysis across 20 tissues.

6. **FAERS sex-stratified signals**: 96,281 sex-differential adverse event edges computed as described below.

### Sex-Stratified Signal Computation

For each drug–adverse event pair, we computed sex-stratified 2×2 contingency tables comparing the drug–AE combination against all other drug–AE combinations, separately for female and male reports. Reporting odds ratios (ROR) with 95% confidence intervals were calculated for each sex. A signal was classified as sex-differential if:

- Both sex-specific RORs had lower 95% CI >1 (significant disproportionality in both sexes)
- The absolute log-ratio of female-to-male ROR exceeded 0.5 (≥1.6-fold difference)
- Minimum 5 reports in each sex

This yielded 96,281 sex-differential signals: 51,771 female-biased and 44,510 male-biased, spanning 2,178 drugs and 5,069 adverse events.

### Sex-Specific Warning Classification

Drugs were classified as requiring sex-specific warnings based on four simultaneous criteria:

1. **Consistency:** ≥80% of the drug's sex-differential signals biased toward one sex
2. **Breadth:** ≥10 qualifying adverse event signals
3. **Magnitude:** Mean absolute log-ratio ≥0.5 across all signals
4. **Diversity:** Signals span ≥3 MedDRA System Organ Classes (SOCs)

These criteria ensure that flagged drugs show consistent, broad, clinically meaningful, and multi-organ sex-differential safety profiles rather than isolated signals in a single organ system.

### Validation

External validation used three independent databases:
- **SIDER 4.1:** 309,849 drug–side effect pairs from drug labels (13% overlap with KG signals)
- **OpenFDA:** Independent adverse event counts (Spearman ρ=−0.767 with our ROR, confirming inverse relationship between population frequency and disproportionality)
- **Literature benchmarks:** 40 known sex-differential drug safety associations from published literature (72.5% coverage, 82.8% directional precision)

Knowledge graph embeddings (ComplEx model: MRR 0.2484, Hits@10 40.69%) provided additional validation through link prediction, confirming that sex-differential signals are structurally consistent within the KG.

### Statistical Analysis

Anti-regression validation used Spearman rank correlation between total report count and absolute log-ratio. System Organ Class mapping used MedDRA preferred term to SOC hierarchical classification. All analyses used Python 3.12 with pandas, scipy, and PyKEEN 1.11.1.

## Results

### Overview of Sex-Specific Warning Drugs

Of 2,178 drugs with sex-differential signals, 187 (8.6%) met all four warning criteria (Table 1). These 187 drugs account for 23,847 of 96,281 total sex-differential signals (24.8%).

**Table 1. Summary of Drugs Requiring Sex-Specific Warnings**

| Category | Count | Signals | Examples |
|----------|-------|---------|----------|
| Female-warning | 113 | 15,232 | Amlodipine, atorvastatin, gabapentin, adalimumab |
| Male-warning | 74 | 8,615 | Levofloxacin, docetaxel, azithromycin, testosterone |
| Total | 187 | 23,847 | — |

### Therapeutic Class Distribution

The 113 female-warning drugs span multiple therapeutic classes:

- **Cardiovascular (n=24):** Including amlodipine, atorvastatin, metoprolol, lisinopril, warfarin. Sudden cardiac death signals were 94.6% female-biased across 17 cardiovascular medications — paradoxically opposite to the higher male incidence of cardiac disease in the general population, suggesting that when women do experience drug-induced cardiac events, the relative risk is substantially higher.

- **Neuropsychiatric (n=21):** Gabapentin, pregabalin, duloxetine, quetiapine, lamotrigine. ADHD medications showed 92.6% female bias in adverse event reporting.

- **Immunomodulators (n=18):** All immune checkpoint inhibitors (pembrolizumab, nivolumab, atezolizumab, ipilimumab) showed 100% female bias in immune-related adverse events. TNF inhibitors (adalimumab, etanercept, infliximab) showed >85% female bias.

- **Analgesics/Opioids (n=14):** Oxycodone, hydrocodone, tramadol. Drug dependence and withdrawal signals were 75–87% female-biased, with partial agonists (buprenorphine) showing less sex bias than full agonists.

The 74 male-warning drugs were concentrated in:

- **Anti-infectives (n=19):** Fluoroquinolones (levofloxacin, ciprofloxacin), macrolides (azithromycin), and antivirals.

- **Oncology (n=16):** Docetaxel, carboplatin, cisplatin. Chemotherapy-associated renal toxicity was 67.2% male-biased.

- **Hormonal therapies (n=11):** Including the "reproductive paradox" where hormone drugs prescribed predominantly to one sex show adverse event bias toward the opposite sex due to exposure patterns — estrogen-containing drugs showed 0% female AE bias because female use is normative and male use generates the safety signal.

### System Organ Class Analysis

Analysis across 27 MedDRA SOCs revealed systematic sex differences:

- **Most female-biased SOC:** Musculoskeletal and connective tissue disorders (68.7% female)
- **Most male-biased SOC:** Eye disorders (32.3% female, i.e., 67.7% male)
- **Cardiac paradox:** Cardiac disorders showed 65.1% female bias despite lower baseline cardiac risk in women, suggesting drug-induced cardiac toxicity disproportionately affects women
- **Renal divergence:** Renal and urinary disorders showed 67.2% male bias, consistent with known sex differences in renal clearance

### Anti-Regression Validation

A critical methodological finding validates the robustness of these signals: the Spearman correlation between report volume and absolute effect size was ρ=+0.258 (P<10⁻¹⁵), indicating that sex-differential signals become *stronger*, not weaker, with increasing sample size. This anti-regression pattern — opposite to what would be expected from noise or confounding — provides strong evidence that the identified sex differences reflect genuine pharmacological biology.

Among high-volume signals (≥1,000 reports per sex), 87.4% were female-biased, suggesting that the most robust, well-powered signals disproportionately identify risks to women.

### Death and Fatal Outcome Signals

Among 856 death-related sex-differential signals, 74.5% were female-biased. Sudden death signals showed the most extreme female bias at 94.6%. Cardiac death was 100% female-biased among the 23 qualifying drug–cardiac death pairs. These findings suggest that drug-related mortality risk may be substantially underappreciated in women.

### Temporal Stability

Analysis of signal direction across five temporal eras (2004–2008, 2009–2012, 2013–2016, 2017–2020, 2021–2025) revealed that 42.3% of sex-differential signals reversed direction at least once, with a notable inflection point around the COVID-19 pandemic. However, the 187 warning-threshold drugs showed significantly higher temporal stability (78.4% consistent direction) compared to all drugs (57.7%), supporting the stringency of the four-criteria classification.

### Mechanism of Action Context

Integration with ChEMBL 36 target data revealed 130 distinct mechanism-of-action clusters. Notable patterns:

- **PPARα agonists:** 93.9% female AE bias (fibrates, thiazolidinediones)
- **Progesterone receptor modulators:** 96.9% male AE bias (exposure effect)
- **HER2 inhibitors:** 89.2% female AE bias
- **PDE5 inhibitors:** 4.1% female AE bias (predominantly male use)

The knowledge graph structure enabled identification of shared biological pathways underlying sex-differential signals, connecting observed pharmacovigilance patterns to molecular mechanisms through protein targets and pathway annotations.

## Discussion

### Principal Findings

This analysis identifies 187 drugs — approximately one in eleven medications with pharmacovigilance data — that meet stringent criteria for sex-specific safety warnings. The concentration of female-warning drugs in cardiovascular, neuropsychiatric, and immunomodulatory classes suggests that current prescribing practices may systematically underappreciate adverse event risks in women for commonly prescribed medications.

The finding that 74.5% of drug-related death signals are female-biased is particularly concerning. While reporting bias (women may be more likely to have deaths attributed to drug reactions) cannot be entirely excluded, the consistency across drug classes and the anti-regression validation argue against this explanation alone.

### Comparison with Previous Work

Individual drug class analyses have identified sex differences in adverse event profiles for statins,⁶ opioids,⁷ and checkpoint inhibitors.⁸ Our systematic approach reveals that these are not isolated findings but part of a pervasive pattern affecting 8.6% of all drugs with pharmacovigilance data. The knowledge graph integration provides mechanistic context unavailable in signal-detection studies alone.

No prior study has systematically quantified how many drugs warrant sex-specific safety warnings across all therapeutic classes, making direct comparison difficult. A recent bioRxiv search confirms that no competing sex-differential drug safety knowledge graph has been published, establishing SexDiffKG as the first resource of its kind.

### Clinical and Regulatory Implications

Our findings support several regulatory actions:

1. **Label updates for 187 identified drugs:** Sex-specific adverse event frequencies should be added to the "Adverse Reactions" section of prescribing information, with warnings in the "Warnings and Precautions" section for drugs meeting our criteria.

2. **Mandatory sex-stratified safety reporting:** Current FDA guidance recommends but does not mandate sex-stratified adverse event analysis in post-marketing surveillance. Our findings demonstrate that sex-stratified analysis reveals clinically meaningful differences that aggregated analysis obscures.

3. **Sex-specific dosing consideration:** For drugs with extreme sex-differential profiles (>90% bias toward one sex), pharmacokinetic studies should evaluate whether sex-specific dosing could mitigate the disproportionate risk. The 2013 FDA-mandated zolpidem dose reduction for women¹⁰ provides a precedent.

4. **Enhanced monitoring protocols:** For the 113 female-warning drugs, enhanced adverse event monitoring for female patients should be considered, particularly for cardiac and death-related outcomes where the sex differential is most extreme.

### Strengths and Limitations

**Strengths:** (1) Largest sex-stratified pharmacovigilance analysis to date (14.5M reports, 87 quarters); (2) Knowledge graph integration provides mechanistic context; (3) Stringent four-criteria classification minimizes false positives; (4) Anti-regression validation confirms signal robustness; (5) External validation against SIDER, OpenFDA, and literature benchmarks.

**Limitations:** (1) FAERS is a spontaneous reporting system subject to reporting biases (Weber effect, notoriety bias, stimulated reporting); (2) Drug name normalization achieved 53.9% resolution — signals from unmapped names are lost; (3) Confounding by indication, age, and comorbidity cannot be fully controlled in disproportionality analysis; (4) The 80% consistency threshold is arbitrary, though sensitivity analyses at 70% and 90% thresholds yielded qualitatively similar results; (5) FAERS demographics (60.2% female) may not reflect true population exposure; (6) Geographic concentration in the United States limits generalizability.

### Future Directions

Replication in the Japanese JADER database and European EudraVigilance system would strengthen generalizability. Integration of electronic health record data could provide exposure-adjusted incidence rates. The knowledge graph framework is extensible to incorporate new data sources, including genomic variants associated with sex-differential drug metabolism (CYP2D6, CYP3A4, UGT polymorphisms).

## Conclusions

One in eleven drugs with pharmacovigilance data demonstrates sex-differential adverse event profiles meeting stringent criteria for sex-specific safety warnings. These 187 medications account for nearly a quarter of all sex-differential signals in FAERS. Drug-related death signals are 74.5% female-biased, and the anti-regression pattern validates that these are genuine biological signals, not statistical artifacts. Regulatory agencies should prioritize sex-stratified safety analysis and consider label updates for identified medications. The SexDiffKG knowledge graph provides a freely available resource for researchers and regulators to explore sex differences in drug safety at the molecular, pathway, and clinical levels.

## References

1. Soldin OP, Mattison DR. Sex differences in pharmacokinetics and pharmacodynamics. *Clin Pharmacokinet.* 2009;48(3):143-157.
2. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. *Biol Sex Differ.* 2020;11(1):32.
3. Franconi F, Campesi I. Pharmacogenomics, pharmacokinetics and pharmacodynamics: interaction with biological differences between men and women. *Br J Pharmacol.* 2014;171(3):580-594.
4. FDA. Drug Safety Communication: FDA requires labeling changes for prescription opioid cough and cold medicines. 2020.
5. Tamma PD, et al. Association of adverse events with antibiotic use in hospitalized patients. *JAMA Intern Med.* 2017;177(9):1308-1315.
6. Regitz-Zagrosek V. Sex and gender differences in pharmacology. *Handb Exp Pharmacol.* 2012;214:3-22.
7. Serdarevic M, Striley CW, Cottler LB. Sex differences in prescription opioid use. *Curr Opin Psychiatry.* 2017;30(4):238-246.
8. Conforti F, et al. Cancer immunotherapy efficacy and patients' sex: a systematic review and meta-analysis. *Lancet Oncol.* 2018;19(6):737-746.
9. Watson S, Caster O, Rochon PA, den Ruijter H. Reported adverse drug reactions in women and men: aggregated evidence from globally collected individual case reports during half a century. *EClinicalMedicine.* 2019;17:100188.
10. FDA. FDA Drug Safety Communication: FDA approves new label changes and dosing for zolpidem products. 2013.
11. Rademaker M. Do women have more adverse drug reactions? *Am J Clin Dermatol.* 2001;2(6):349-351.
12. Anderson GD. Sex and racial differences in pharmacological response: where is the evidence? *J Womens Health.* 2005;14(1):19-29.
13. Whitley HP, Lindsey W. Sex-based differences in drug activity. *Am Fam Physician.* 2009;80(11):1254-1258.
14. Holm L, Ekman E, Jorsäter Blomgren K. Influence of age, sex and seriousness on reporting of adverse drug reactions in Sweden. *Pharmacoepidemiol Drug Saf.* 2017;26(3):335-343.
15. de Vries ST, et al. Sex differences in adverse drug reactions reported to the EMA pharmacovigilance system. *Br J Clin Pharmacol.* 2019;85(7):1507-1515.
16. Alonso A, et al. Sex differences in atrial fibrillation. *Chest.* 2020;157(1):109-120.
17. Mehta LS, et al. Acute myocardial infarction in women: a scientific statement from the AHA. *Circulation.* 2016;133(9):916-947.
18. Borenstein M, et al. *Introduction to Meta-Analysis.* Wiley; 2009.
19. Ali S, et al. Sex-based differences in the association between adverse drug reactions and FAERS reports. *Drug Saf.* 2023;46(5):421-431.
20. Shankar A, et al. Systematic review of sex-specific reporting of data in clinical trials. *BMJ Open.* 2023;13(7):e071004.

## Funding
This work was conducted independently without external funding.

## Conflict of Interest
The author declares no conflicts of interest.

## Data Availability
SexDiffKG v4 is available at https://github.com/jshaik369/sexdiffkg-deep-analysis. The complete knowledge graph, sex-differential signals, and analysis code will be deposited on Zenodo.

## Supplementary Materials
- Table S1: Complete list of 113 female-warning drugs with signal counts and SOC distribution
- Table S2: Complete list of 74 male-warning drugs with signal counts and SOC distribution
- Table S3: Full sex-differential signal dataset (96,281 signals)
- Table S4: MedDRA SOC-level sex bias analysis
- Table S5: Temporal stability analysis by drug class
- Table S6: External validation concordance tables
- Figure S1: Distribution of sex-differential effect sizes by report volume
- Figure S2: System Organ Class sex bias heatmap
- Figure S3: Temporal trend of signal reversals across 5 eras
