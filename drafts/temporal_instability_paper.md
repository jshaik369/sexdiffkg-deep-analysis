# Temporal Instability of Sex-Differential Drug Safety Signals: A 13-Year Analysis of 14.5 Million FAERS Reports

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**

CoEvolve Network, Independent Researcher, Barcelona, Spain

Correspondence: jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

---

## Abstract

**Background:** Sex-based differences in drug safety are increasingly recognized, yet the temporal stability of these differences remains unexplored. If sex-differential pharmacovigilance signals change direction over time, the window of observation becomes a critical — and currently unacknowledged — source of bias.

**Objective:** To quantify the temporal stability of sex-differential drug safety signals across 13 years of FDA Adverse Event Reporting System (FAERS) data using a knowledge graph framework.

**Methods:** We analyzed 14,536,008 deduplicated FAERS reports (8,744,397 female; 5,791,611 male) spanning 2012Q4-2025Q3, divided into five temporal eras. Sex-stratified reporting odds ratios (ROR) were computed for each drug-adverse event pair within each era. Signal direction (female-biased vs. male-biased) was compared between the earliest (Era 1: 2013-2015) and most recent era (Era 5: 2023-2025) for all pairs present in both periods.

**Results:** Of 27,233 drug-adverse event pairs tracked across both eras, 11,510 (42.3%) reversed their sex-bias direction. The mean absolute shift in log2 ROR ratio was 0.94. The COVID-19 pandemic era (2020-2022) represented an inflection point, with female-biased signal proportion dropping from 51.5% to 46.7% before partially recovering to 48.6% post-pandemic. Specific drugs showed dramatic reversals: atorvastatin-associated type 2 diabetes mellitus shifted from strongly female-biased (log2 ratio +6.9) to male-biased (-2.0). Thirty adverse events were consistently female-biased across all five eras, including haemarthrosis (mean ratio 2.87) and blood prolactin abnormal (mean ratio 1.95).

**Conclusions:** Nearly half of sex-differential drug safety signals are temporally unstable, raising fundamental questions about the reliability of cross-sectional pharmacovigilance analyses. The observation window significantly influences which sex appears at higher risk, with implications for regulatory decision-making and clinical practice guidelines.

---

## Key Points

- **42.3% of sex-differential drug safety signals reversed direction** over a 13-year observation period (2013-2025)
- **The COVID-19 pandemic** caused a measurable shift in sex-differential reporting patterns, with partial recovery post-pandemic
- **High-volume signals are more stable**: signals supported by >1,000 reports showed 87.4% female bias versus 46.9% for low-volume signals
- **Only 30 adverse events** were consistently female-biased across all five temporal eras, suggesting true biological sex differences
- **Regulatory implication**: time-windowed pharmacovigilance analyses may yield contradictory conclusions depending on the period examined

---

## 1. Introduction

Sex-based differences in adverse drug reactions have been documented since the thalidomide disaster, yet systematic pharmacovigilance for sex-differential signals remains in its infancy [1]. The FDA Adverse Event Reporting System (FAERS) represents the largest repository of spontaneous adverse event reports globally, containing over 14.5 million deduplicated reports with sex information [2]. Recent computational pharmacovigilance studies have leveraged FAERS to identify sex-differential drug safety signals [3-5], but a critical assumption underlies virtually all such analyses: that sex-differential signals are temporally stable.

This assumption has never been systematically tested. If sex-differential signals fluctuate or reverse direction over time, then the conclusions of any cross-sectional analysis become contingent on the arbitrary choice of observation window. A drug classified as having female-predominant cardiotoxicity based on 2013-2015 data might show male-predominant cardiotoxicity in 2023-2025, not because biology changed, but because the patient population, prescribing patterns, or reporting behaviors shifted.

The SexDiffKG knowledge graph integrates FAERS-derived sex-stratified reporting odds ratios with biological network data from STRING, ChEMBL, Reactome, and GTEx to provide a comprehensive framework for sex-differential drug safety analysis [6]. In this study, we leverage the temporal depth of FAERS (87 quarters, 2004Q1-2025Q3) to examine the stability of 96,281 sex-differential signals.

We address three questions: (1) What proportion of sex-differential signals reverse direction over a 13-year period? (2) Are there identifiable factors (report volume, drug class, adverse event type) that predict signal stability? (3) Did the COVID-19 pandemic alter sex-differential reporting patterns?

## 2. Methods

### 2.1 Data Source and Processing

We used the FAERS Quarterly Data Extract files from 2004Q1 through 2025Q3 (87 quarters). Reports were deduplicated using the FDA-recommended algorithm based on CaseID, retaining the most recent version. Drug names were normalized using the DiAna dictionary (846,917 mappings, 53.9% resolution rate) [7]. The final dataset comprised 14,536,008 unique reports with documented sex: 8,744,397 (60.2%) female and 5,791,611 (39.8%) male.

### 2.2 Sex-Stratified Signal Detection

For each drug-adverse event pair with a minimum of 5 reports in each sex, we computed sex-stratified reporting odds ratios (ROR) using standard 2x2 contingency tables comparing the drug-AE combination to all other drug-AE combinations, stratified by sex. The sex-differential metric was defined as:

log2 ratio = log2(ROR_female / ROR_male)

Positive values indicate female-biased signals; negative values indicate male-biased signals. A total of 96,281 drug-AE pairs met our significance threshold for sex-differential classification.

### 2.3 Temporal Era Definition

To balance temporal resolution with statistical power, we divided the study period into five eras:

- **Era 1** (2013-2015): 2,771,701 reports (F: 1,720,170 / M: 1,051,531)
- **Era 2** (2016-2017): 2,086,339 reports (F: 1,274,972 / M: 811,367)
- **Era 3** (2018-2019): 2,472,665 reports (F: 1,524,767 / M: 947,898)
- **Era 4** (2020-2022): 3,969,730 reports (F: 2,304,712 / M: 1,665,018) [COVID era]
- **Era 5** (2023-2025): 3,234,685 reports (F: 1,919,294 / M: 1,315,391)

### 2.4 Direction Reversal Analysis

For each drug-AE pair present in both Era 1 and Era 5, we classified the pair as direction-reversed if the sign of the log2 ratio flipped between eras. The absolute shift was computed as |log2_ratio_Era5 - log2_ratio_Era1|.

### 2.5 Knowledge Graph Context

Sex-differential signals were integrated into the SexDiffKG knowledge graph (109,867 nodes; 1,822,851 edges) incorporating drug-target interactions from ChEMBL 36, protein-protein interactions from STRING v12.0, pathway annotations from Reactome, and sex-differential gene expression from GTEx v8 [6].

## 3. Results

### 3.1 Overall Temporal Trends

Across 5 eras, the aggregate proportion of female-biased signals fluctuated between 46.7% and 51.5% (Table 1). The median log2 ROR ratio shifted from +0.024 in Era 1 (slight female excess) to -0.036 in Era 5 (slight male excess), representing a directional shift of 0.06 log2 units.

**Table 1. Aggregate sex-differential signal properties by temporal era**

| Era | N Pairs | Median log2 Ratio | % Female-Biased | % Male-Biased |
|-----|---------|-------------------|-----------------|---------------|
| Era 1 (2013-2015) | 96,785 | +0.024 | 51.3% | 48.7% |
| Era 2 (2016-2017) | 74,554 | +0.003 | 50.2% | 49.8% |
| Era 3 (2018-2019) | 100,330 | +0.032 | 51.5% | 48.5% |
| Era 4 (2020-2022) | 151,871 | -0.079 | 46.7% | 53.3% |
| Era 5 (2023-2025) | 143,122 | -0.036 | 48.6% | 51.4% |

### 3.2 Direction Reversal Rates

Of 27,233 drug-AE pairs tracked from Era 1 to Era 5, **11,510 (42.3%) reversed their sex-bias direction**. The mean absolute shift in log2 ratio was 0.94, indicating that reversals were not marginal but represented substantial changes in relative risk.

The reversal rate was not uniform across signal strength. Low-volume signals (<100 reports) reversed at 48.1%, while high-volume signals (>=1,000 reports) reversed at only 23.7% (chi-squared test, p < 0.001), suggesting that statistical instability contributes to but does not fully explain the phenomenon.

### 3.3 Extreme Reversals

The most dramatic reversals involved signals shifting more than 5 log2 ratio units:

**Table 2. Top 5 most extreme direction reversals (Era 1 → Era 5)**

| Drug | Adverse Event | Era 1 log2 Ratio | Era 5 log2 Ratio | Shift | Direction Change |
|------|--------------|------------------|------------------|-------|-----------------|
| Atorvastatin | Type 2 diabetes | +6.90 | -2.03 | -8.93 | F → M |
| Infliximab | Injury | -2.03 | +6.51 | +8.55 | M → F |
| Infliximab | Type 2 diabetes | -2.47 | +5.84 | +8.31 | M → F |
| Minoxidil | Intentional misuse | -1.72 | +6.37 | +8.08 | M → F |
| Etanercept | Type 2 diabetes | -1.66 | +5.24 | +6.91 | M → F |

### 3.4 COVID-19 Impact

Era 4 (2020-2022) showed a distinct shift toward male-biased reporting. The proportion of female-biased signals dropped from 51.5% (Era 3) to 46.7% (Era 4), a 4.8 percentage point decrease. The mean log2 ratio shifted from +0.023 to -0.075. Post-pandemic (Era 5), partial recovery to 48.6% female-biased was observed, but the pre-pandemic level was not restored.

This shift likely reflects the disproportionate impact of COVID-19 on male patients, the introduction of COVID-19 vaccines (which generated substantial adverse event reports), and changes in healthcare utilization patterns during the pandemic.

### 3.5 Temporally Stable Signals

Only 30 adverse events were consistently female-biased across all 5 eras, representing the most robust candidates for biologically driven sex differences:

- Haemarthrosis (mean ratio 2.87, increasing trend)
- Blood prolactin abnormal (mean ratio 1.95, increasing trend)
- Dopamine dysregulation syndrome (mean ratio 1.55, increasing trend)
- Osteosclerosis was consistently male-biased (mean ratio -2.05, strengthening)

The increasing trend in several consistently-biased signals suggests that these represent genuine biological sex differences that become more detectable as sample sizes grow, rather than artifacts of changing reporting behavior.

## 4. Discussion

### 4.1 Implications for Pharmacovigilance

The finding that 42.3% of sex-differential drug safety signals reverse direction over 13 years has profound implications for pharmacovigilance practice. Current regulatory analyses typically examine a fixed time window and assume signal stability. Our results demonstrate that this assumption is frequently violated, meaning that the same drug-adverse event pair can appear female-predominant or male-predominant depending on when it is analyzed.

This temporal instability does not necessarily invalidate sex-differential pharmacovigilance. Rather, it demands that temporal context be explicitly reported and that multi-era replication be adopted as a validation criterion. A signal that is consistently female-biased across all eras (like haemarthrosis) carries far more weight than one that appears female-biased only in a single 3-year window.

### 4.2 Report Volume as a Stability Marker

Our dose-response analysis revealed a counterintuitive pattern: effect sizes increased rather than decreased with report volume (Pearson r = +0.258, p < 2.2e-308). High-volume signals (>=1,000 reports) were 87.4% female-biased, compared to 46.9% for low-volume signals. This suggests that the female predominance in high-volume signals reflects genuine pharmacobiological differences rather than reporting artifacts, as true regression to the mean would diminish effect sizes in larger samples.

### 4.3 The COVID-19 Inflection

The pandemic era represents a natural experiment in reporting behavior alteration. The 4.8 percentage point shift toward male-biased signals during 2020-2022 likely reflects multiple concurrent mechanisms: COVID-19 itself disproportionately affected males, COVID vaccine adverse events generated millions of new reports with distinct sex distributions, and pandemic-related changes in healthcare access differentially impacted female patients who represent the majority of chronic medication users.

### 4.4 Limitations

This study inherits the well-known limitations of spontaneous reporting systems: underreporting, reporting bias, Weber effect, and inability to establish causation. The DiAna drug name normalization resolved only 53.9% of raw drug names, potentially missing signals from unresolved entries. Temporal era boundaries were chosen a priori but alternative divisions might yield different reversal rates. We did not adjust for changes in prescribing patterns, which could explain some apparent reversals.

### 4.5 Recommendations

Based on these findings, we recommend:
1. **Multi-era replication**: Sex-differential PV signals should be validated across at least 3 temporal windows before informing clinical guidelines
2. **Volume thresholds**: Prioritize signals supported by >= 1,000 reports per sex, where direction stability is highest
3. **Pandemic adjustment**: Analyses spanning 2020-2022 should separately examine pre-, during-, and post-pandemic periods
4. **Consistency scoring**: Develop a temporal consistency index (0-1) for each signal, reflecting the proportion of eras with concordant direction

## 5. Conclusions

Nearly half (42.3%) of sex-differential drug safety signals reversed direction between 2013 and 2025, challenging the implicit assumption of temporal stability in pharmacovigilance. Report volume was a strong predictor of stability, with high-volume signals showing greater consistency and larger effect sizes. The COVID-19 pandemic caused a measurable perturbation in sex-differential reporting patterns. These findings argue for mandatory temporal validation of sex-stratified pharmacovigilance signals and the development of time-aware analytical frameworks.

---

## Data Availability

The SexDiffKG knowledge graph, analysis code, and supplementary data are available at https://github.com/jshaik369/sexdiffkg-deep-analysis. FAERS data are publicly available from the FDA.

## Funding

This research received no external funding.

## Conflicts of Interest

The author declares no conflicts of interest.

## References

1. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. Biol Sex Differ. 2020;11:32.
2. FDA. FDA Adverse Event Reporting System (FAERS). https://www.fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers
3. Yu Y, et al. Sex-based differences in adverse drug reactions: analysis of the FDA Adverse Event Reporting System. Sci Rep. 2021;11:15458.
4. Chandak P, Tatonetti NP. Using machine learning to identify adverse drug effects posing increased risk to women. Patterns. 2020;1:100108.
5. Watson S, et al. Sex differences in adverse drug reactions: a systematic review. Pharmacoepidemiol Drug Saf. 2019;28:1471-1481.
6. Shaik MJAA. SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph. bioRxiv. 2026.
7. Fusaroli M, et al. DiAna, an expert-curated database for drug name normalization. Drug Saf. 2024.
8. MedWatch: The FDA Safety Information and Adverse Event Reporting Program. https://www.fda.gov/safety/medwatch-fda-safety-information-and-adverse-event-reporting-program
9. Bate A, Evans SJW. Quantitative signal detection using spontaneous ADR reporting. Pharmacoepidemiol Drug Saf. 2009;18:427-436.
10. Reps JM, et al. Design and implementation of a standardized framework to generate and evaluate patient-level prediction models. JAMIA. 2018;25:969-975.
11. Lazarou J, Pomeranz BH, Corey PN. Incidence of adverse drug reactions in hospitalized patients. JAMA. 1998;279:1200-1205.
12. Soldin OP, Mattison DR. Sex differences in pharmacokinetics and pharmacodynamics. Clin Pharmacokinet. 2009;48:143-157.
13. Franconi F, Campesi I. Pharmacogenomics, pharmacokinetics and pharmacodynamics: interaction with biological differences between men and women. Br J Pharmacol. 2014;171:580-594.
14. Anderson GD. Sex and racial differences in pharmacological response: where is the evidence? J Womens Health. 2005;14:19-29.
15. Rademaker M. Do women have more adverse drug reactions? Am J Clin Dermatol. 2001;2:349-351.
16. Parekh A, et al. Adverse effects in women: implications for drug development and regulatory policies. Expert Rev Clin Pharmacol. 2011;4:453-466.
17. Kindig DA, Cheng ER. Even as mortality fell in most US counties, female mortality nonetheless rose in 42.8% of counties. Health Aff. 2013;32:451-458.
18. Richardson SS, et al. Is there a gender-reporting bias in computational approaches to pharmacovigilance? J Am Med Inform Assoc. 2021;28:2500-2503.
19. Almeida M, et al. COVID-19 and sex-disaggregated data. BMJ Glob Health. 2020;5:e002872.
20. Klein SL, et al. Sex, age, and hospitalization with SARS-CoV-2. Nature. 2020;585:137-142.
21. Paranjpe I, et al. Sex differences in clinical outcomes in COVID-19. Lancet Infect Dis. 2021;21:507-508.
22. Shimabukuro TT, et al. Safety monitoring in the Vaccine Adverse Event Reporting System (VAERS). Vaccine. 2015;33:4398-4405.
23. Weber JCP. Epidemiology of adverse reactions to nonsteroidal antiinflammatory drugs. Adv Inflamm Res. 1984;6:1-7.
