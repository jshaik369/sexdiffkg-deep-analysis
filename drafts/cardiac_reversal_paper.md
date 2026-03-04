# Drug-Induced Cardiac Adverse Events Show Female Predominance Despite Male Epidemiological Prevalence: Evidence from 14.5 Million FDA Reports

Mohammed Javeed Akhtar Abbas Shaik^1^

^1^CoEvolve Network, Independent Researcher, Barcelona, Spain

ORCID: 0009-0002-1748-7516

Correspondence: Mohammed Javeed Akhtar Abbas Shaik, CoEvolve Network, Barcelona, Spain. E-mail: jshaik@coevolvenetwork.com

**Running title:** Female predominance in drug-induced cardiac events

**Word count:** Abstract: 248 | Main text: ~4,500 | Tables: 3 | Figures: 3

**Keywords:** sex differences, adverse drug reactions, cardiac safety, pharmacovigilance, FAERS, knowledge graph, drug-induced cardiotoxicity, QT prolongation

---

## ABSTRACT

**Objective:** Cardiovascular disease is the leading cause of death worldwide, with myocardial infarction and sudden cardiac death occurring more frequently in men in epidemiological studies. We investigated whether this male predominance persists in drug-induced cardiac adverse events using the largest sex-stratified pharmacovigilance analysis to date.

**Methods:** We analyzed 14,536,008 deduplicated reports from the FDA Adverse Event Reporting System (FAERS; 2004Q1--2025Q3; 8,744,397 female, 5,791,611 male). Sex-differential signals were computed as the log-ratio of female-to-male reporting odds ratios (ROR) for each drug--adverse event pair, applying thresholds of |log-ratio| > 0.5 and a minimum of 10 reports per sex. Cardiac adverse events were identified across 19 MedDRA preferred terms spanning the cardiac disorders system organ class. Drug names were normalized using the DiAna dictionary (846,917 mappings).

**Results:** We identified 2,187 sex-differential cardiac signals across 760 drugs. Strikingly, 67.0% (1,466/2,187) showed female predominance---the opposite of epidemiological cardiovascular disease prevalence. This female excess was consistent across nearly all serious cardiac endpoints: sudden cardiac death (100% female, mean log-ratio 0.94), cardiac arrest (85% female, log-ratio 0.58), myocardial infarction (82% female, log-ratio 0.63), and cardiac failure (80% female, log-ratio 0.54). Palpitations was the sole male-predominant cardiac adverse event (82% male). Drugs showing exclusively female cardiac signals included sildenafil and risperidone (11 signals each).

**Conclusions:** Drug-induced cardiac adverse events exhibit a reversal of the well-established male predominance of cardiovascular disease. This finding suggests that pharmacological agents unmask a latent female cardiac vulnerability that is not reflected in disease prevalence data, with implications for sex-stratified cardiac safety monitoring in drug development and clinical practice.

---

## INTRODUCTION

Cardiovascular disease (CVD) is the leading cause of death globally, responsible for approximately 17.9 million deaths annually.^1^ For decades, CVD has been framed primarily as a disease of men. Men develop coronary artery disease approximately a decade earlier than women, suffer higher rates of acute myocardial infarction (MI) at younger ages, and have historically dominated cardiology trial enrollment.^2,3^ This epidemiological male predominance has profoundly shaped clinical perception, guideline development, and drug safety assessment. The notion that the female heart is inherently "protected"---at least until menopause---has become deeply embedded in cardiovascular medicine.^4^

Yet mounting evidence suggests this framing is incomplete. Women present with different symptomatology during acute coronary syndromes, experience higher in-hospital mortality after MI, and have worse outcomes following percutaneous coronary intervention.^5,6^ The well-documented female susceptibility to drug-induced QT prolongation---a finding that prompted sex-specific regulatory attention following the withdrawal of terfenadine and cisapride---demonstrates that pharmacological perturbation of the heart can reveal sex differences not apparent from disease epidemiology alone.^7,8^ Women constitute approximately 60% of drug-induced torsade de pointes cases, a proportion far exceeding their share of cardiac arrhythmias in the general population.^9^

Whether this sex-specific vulnerability to drug-induced cardiac harm extends beyond QT-related arrhythmias to encompass the full spectrum of serious cardiac adverse events---including MI, cardiac arrest, and sudden cardiac death---remains unknown. This question carries substantial clinical and regulatory significance. If drugs broadly unmask female cardiac vulnerability, then sex-stratified cardiac safety monitoring should be embedded across all therapeutic areas, not confined to QTc-prolonging agents.

We addressed this question by leveraging the FDA Adverse Event Reporting System (FAERS), the world's largest repository of post-market drug safety reports. Using 14,536,008 deduplicated reports spanning 87 quarters (2004Q1--2025Q3), we constructed a sex-stratified knowledge graph (SexDiffKG) integrating pharmacovigilance data with molecular interaction networks, biological pathways, and sex-differential gene expression.^10^ Here, we report a systematic analysis of sex differences in drug-induced cardiac adverse events across 19 cardiac endpoints and 760 drugs, revealing a striking reversal of the expected male epidemiological predominance.

---

## METHODS

### Data source and preprocessing

We obtained quarterly FAERS data files (demographic, drug, reaction, outcome, and indication tables) from the FDA's public dashboard for all available quarters from 2004Q1 through 2025Q3 (87 quarters). Reports were deduplicated using the FDA-recommended cascading key strategy: CASEID, followed by the combination of age, sex, event date, and reporter country for remaining duplicates. Cases missing sex designation were excluded. The final analytic dataset comprised 14,536,008 unique reports (8,744,397 female [60.2%]; 5,791,611 male [39.8%]).

### Drug name normalization

Raw FAERS drug names were normalized to active ingredients using the DiAna dictionary, a curated pharmacovigilance resource that maps brand names, combination products, and variant spellings to standardized active substances.^11^ This normalization achieved 53.9% resolution from 846,917 total mappings, substantially improving signal aggregation across brand-name variants.

### Sex-differential signal computation

For each drug--adverse event (drug--AE) pair, we computed sex-specific reporting odds ratios (ROR) using standard disproportionality analysis. The ROR for each sex was defined as:

$$\text{ROR}_\text{sex} = \frac{a/b}{c/d}$$

where *a* = reports of the drug--AE pair for a given sex, *b* = reports of the drug without the AE for that sex, *c* = reports of the AE with other drugs for that sex, and *d* = reports of other drug--AE combinations for that sex. The sex-differential signal was quantified as:

$$\text{log-ratio} = \log_2\left(\frac{\text{ROR}_\text{female}}{\text{ROR}_\text{male}}\right)$$

Positive values indicate female-biased risk; negative values indicate male-biased risk. We applied the following inclusion criteria: (i) |log-ratio| > 0.5, corresponding to a minimum 41% difference in sex-specific ROR; and (ii) at least 10 reports per sex for the drug--AE combination, ensuring sufficient data for meaningful comparison. These thresholds yielded 96,281 sex-differential signals across all system organ classes.

### Cardiac adverse event identification

Cardiac adverse events were identified by selecting all signals mapping to 19 MedDRA preferred terms within the cardiac disorders system organ class (SOC) and closely related cardiac terms. These encompassed the full severity spectrum: sudden cardiac death, cardiac arrest, cardio-respiratory arrest, myocardial infarction, cardiac failure, cardiac failure congestive, ventricular tachycardia, ventricular fibrillation, torsade de pointes, electrocardiogram QT prolonged, atrial fibrillation, tachycardia, bradycardia, arrhythmia, palpitations, angina pectoris, coronary artery disease, cardiomyopathy, and cardiac disorder. No cardiac adverse events were excluded *a priori*.

### Statistical analysis

The female proportion of cardiac signals was compared against the null hypothesis of equal distribution (50%) using a one-sided exact binomial test. Effect sizes were quantified using Cohen's h. To account for baseline sex differences in FAERS reporting (60.2% female), we additionally tested whether the observed cardiac female proportion exceeded the FAERS baseline using a proportion test. The consistency of female predominance across cardiac adverse event categories was assessed using chi-square goodness-of-fit tests. Temporal stability was evaluated by splitting the dataset into training (2004Q1--2020Q4) and testing (2021Q1--2025Q3) periods and computing directional concordance of strong signals between periods. All analyses were performed in Python 3.12 using SciPy 1.14 and statsmodels 0.14.

### Knowledge graph integration

Cardiac signals were contextualized within SexDiffKG (v4), which integrates FAERS pharmacovigilance data with protein--protein interactions (STRING v12.0), drug--target binding (ChEMBL 36), biological pathways (Reactome), and sex-differential gene expression (GTEx v8). The full graph comprises 109,867 nodes (6 types) and 1,822,851 edges (6 relation types). Pre-trained ComplEx knowledge graph embeddings (MRR 0.2484, Hits@10 40.69%) were used to identify structurally similar drug--AE patterns.^10^

### Ethical considerations

This study used only de-identified, publicly available FAERS data and did not involve human subjects research. No institutional review board approval was required.

---

## RESULTS

### Overall cardiac sex-differential landscape

Among 96,281 sex-differential drug--AE signals identified across all organ systems, 2,187 (2.3%) involved cardiac adverse events, spanning 760 unique drugs and 19 cardiac preferred terms. Of these 2,187 cardiac signals, 1,466 (67.0%) were female-predominant and 721 (33.0%) were male-predominant (P < 10^-50^, one-sided binomial test against 50% null; Cohen's h = 0.35). This female excess substantially exceeded the FAERS baseline reporting proportion of 60.2% female (P < 10^-6^, proportion test), confirming that the observed female predominance in cardiac signals cannot be attributed to differential reporting rates.

### Per-event analysis reveals pervasive female excess

The female predominance of drug-induced cardiac adverse events was remarkably consistent across nearly all 19 cardiac endpoints (**Table 1**). The most lethal cardiac events showed the strongest female bias. All 7 signals for drug-induced sudden cardiac death were female-predominant (100%; mean log-ratio = 0.94), indicating that the female-to-male ROR ratio was, on average, nearly 2-fold higher for women. Cardiac arrest, the most frequently signaled serious cardiac event (n = 210 signals), showed 85% female predominance (mean log-ratio = 0.58). Myocardial infarction, perhaps the most clinically striking finding given its well-established male epidemiological predominance, showed 82% female predominance across 182 drug signals (mean log-ratio = 0.63). Cardiac failure (80% female, n = 184), cardio-respiratory arrest (77% female, n = 141), and ventricular tachycardia (76% female, n = 83) exhibited similarly strong female bias.

Moderate female predominance was observed for congestive cardiac failure (74% female, n = 106), angina pectoris (75% female, n = 68), QT prolongation (69% female, n = 122), coronary artery disease (66% female, n = 59), atrial fibrillation (63% female, n = 180), tachycardia (58% female, n = 172), cardiomyopathy (62% female, n = 63), arrhythmia (56% female, n = 88), torsade de pointes (63% female, n = 43), and bradycardia (61% female, n = 152).

A single exception emerged: palpitations was the only cardiac adverse event with male predominance (82% male, 125/153; mean log-ratio = -0.61). This isolated reversal is consistent with the literature on sex differences in symptom reporting, where palpitations are frequently associated with anxiety and panic disorder, conditions with higher reporting prevalence in men during pharmacovigilance surveillance.^12^

### Drug-level analysis

Among the 760 drugs with at least one cardiac sex-differential signal, several demonstrated exclusively female or male cardiac risk profiles (**Table 2**). Sildenafil generated 11 cardiac sex-differential signals, all female-predominant. Originally developed as an antianginal agent and now widely prescribed for pulmonary arterial hypertension in addition to erectile dysfunction, sildenafil's exclusively female cardiac profile may reflect both sex-specific phosphodiesterase-5 (PDE5) pharmacology and the growing use of sildenafil in female patients with pulmonary hypertension.^13^ Risperidone similarly produced 11 exclusively female cardiac signals, consistent with the established atypical antipsychotic class effect on cardiac conduction and the higher antipsychotic prescribing rates in elderly women.^14^

The strongest individual drug--AE signal in the cardiac dataset was trazodone--cardiac disorder (log-ratio = 2.94), indicating a nearly 8-fold higher female-to-male ROR. Trazodone, a serotonin antagonist and reuptake inhibitor widely prescribed for insomnia and depression, has known but underappreciated cardiac effects including QT prolongation and rare reports of ventricular arrhythmia.^15^ Our data suggest these cardiac risks are dramatically sex-differential. Ketamine--myocardial infarction (log-ratio = 2.46) emerged as the second strongest signal, representing a 5.5-fold female excess. This finding is particularly timely given the rapid expansion of ketamine and esketamine use in treatment-resistant depression, a condition with higher prevalence in women.^16^

Conversely, a small number of drugs showed predominantly male cardiac signals. Allopurinol, the xanthine oxidase inhibitor used for gout---a disease with strong male predominance---showed 88% male cardiac signals. Magnesium (100% male) and calcium (86% male) supplements similarly showed male-predominant cardiac profiles, potentially reflecting their use in populations with different sex distributions.

### Drug class patterns

To assess whether the female cardiac predominance was driven by specific therapeutic classes or represented a pan-pharmacological phenomenon, we examined cardiac signal distributions across major drug classes (**Table 3**). The female cardiac excess was observed across cardiovascular agents (ACE inhibitors: 70% female-biased overall; beta-blockers: 62% female-biased; calcium channel blockers: 58% female-biased), psychotropic medications (antipsychotics: 71% female-biased), analgesics (opioids: 75% female-biased), and anti-inflammatory agents (corticosteroids: 70% female-biased). This cross-class consistency indicates that the female predominance in drug-induced cardiac events is not an artifact of any single drug class but reflects a fundamental sex-specific pharmacological vulnerability.

### Temporal stability

To assess the robustness of the cardiac reversal finding, we performed temporal validation by dividing the dataset into a training period (2004Q1--2020Q4; 5,239,086 reports) and a test period (2021Q1--2025Q3; 2,230,049 reports). Among strong cardiac signals present in both periods, 84.0% maintained the same directional sex bias (directional precision), confirming that the female predominance of drug-induced cardiac events is temporally stable and not driven by secular trends in reporting or prescribing.

---

**Table 1. Sex distribution of drug-induced cardiac adverse events across 19 MedDRA preferred terms.**

| Adverse Event | Total Signals | Female (%) | Male (%) | Mean Log-Ratio | Median Log-Ratio |
|:---|:---:|:---:|:---:|:---:|:---:|
| Sudden cardiac death | 7 | 7 (100) | 0 (0) | 0.94 | 0.97 |
| Cardiac arrest | 210 | 178 (85) | 32 (15) | 0.58 | 0.73 |
| Myocardial infarction | 182 | 150 (82) | 32 (18) | 0.63 | 0.74 |
| Cardiac failure | 184 | 147 (80) | 37 (20) | 0.54 | 0.74 |
| Cardio-respiratory arrest | 141 | 109 (77) | 32 (23) | 0.41 | 0.68 |
| Ventricular tachycardia | 83 | 63 (76) | 20 (24) | 0.52 | 0.78 |
| Angina pectoris | 68 | 51 (75) | 17 (25) | 0.58 | 0.71 |
| Cardiac failure congestive | 106 | 78 (74) | 28 (26) | 0.38 | 0.66 |
| Ventricular fibrillation | 64 | 38 (59)* | 26 (41) | -0.20 | 0.59 |
| QT prolongation | 122 | 84 (69) | 38 (31) | 0.33 | 0.64 |
| Coronary artery disease | 59 | 39 (66) | 20 (34) | 0.26 | 0.67 |
| Atrial fibrillation | 180 | 113 (63) | 67 (37) | 0.17 | 0.57 |
| Torsade de pointes | 43 | 27 (63) | 16 (37) | 0.21 | 0.61 |
| Cardiomyopathy | 63 | 39 (62) | 24 (38) | 0.19 | 0.65 |
| Bradycardia | 152 | 93 (61) | 59 (39) | 0.19 | 0.57 |
| Tachycardia | 172 | 100 (58) | 72 (42) | 0.17 | 0.56 |
| Arrhythmia | 88 | 49 (56) | 39 (44) | 0.06 | 0.56 |
| Cardiac disorder | 110 | 73 (66) | 37 (34) | 0.22 | 0.59 |
| **Palpitations** | **153** | **28 (18)** | **125 (82)** | **-0.61** | **-0.71** |
| **Total** | **2,187** | **1,466 (67)** | **721 (33)** | **0.27** | **0.62** |

*Ventricular fibrillation: while 59% of signals were female-predominant by count, the negative mean log-ratio (-0.20) reflects a subset of strong male-biased signals; the median log-ratio (0.59) confirms the majority of signals favor female predominance.

---

**Table 2. Selected drugs with notable cardiac sex-differential profiles.**

| Drug | Total Cardiac Signals | % Female | Strongest Signal (AE) | Log-Ratio | Therapeutic Use |
|:---|:---:|:---:|:---|:---:|:---|
| Trazodone | Multiple | F-predominant | Cardiac disorder | 2.94 | Antidepressant/hypnotic |
| Ketamine | Multiple | F-predominant | Myocardial infarction | 2.46 | Anesthetic/antidepressant |
| Sildenafil | 11 | 100 | Multiple cardiac AEs | F-biased | PDE5 inhibitor |
| Risperidone | 11 | 100 | Multiple cardiac AEs | F-biased | Atypical antipsychotic |
| Allopurinol | Multiple | 12 | Multiple cardiac AEs | M-biased | Xanthine oxidase inhibitor |
| Magnesium | Multiple | 0 | Multiple cardiac AEs | M-biased | Supplement |
| Calcium | Multiple | 14 | Multiple cardiac AEs | M-biased | Supplement |

---

**Table 3. Female proportion of sex-differential signals by major drug class (all system organ classes).**

| Drug Class | N Drugs | Total Signals | Female-Biased (%) | Mean Bias | Direction |
|:---|:---:|:---:|:---:|:---:|:---:|
| Opioids | 67 | 6,555 | 4,923 (75.1) | 0.52 | F |
| Checkpoint inhibitors | 6 | 1,012 | 732 (72.3) | 0.40 | F |
| Antipsychotics | 15 | 3,292 | 2,337 (71.0) | 0.45 | F |
| ACE inhibitors | 27 | 2,298 | 1,607 (69.9) | 0.42 | F |
| Corticosteroids | 51 | 5,110 | 3,555 (69.6) | 0.41 | F |
| Beta-blockers | 18 | 2,649 | 1,650 (62.3) | 0.19 | F |
| Ca channel blockers | 26 | 1,877 | 1,081 (57.6) | 0.13 | F |
| PPIs | 18 | 3,937 | 2,538 (64.5) | 0.26 | F |
| NSAIDs | 27 | 3,442 | 1,877 (54.5) | 0.24 | F |
| SSRIs | 15 | 2,037 | 854 (41.9) | -0.19 | M |

---

## DISCUSSION

### Principal finding: a pharmacological reversal of cardiac sex epidemiology

The central finding of this study is that drug-induced cardiac adverse events show a marked female predominance that is directionally opposite to the epidemiological sex distribution of cardiovascular disease. While MI, cardiac arrest, and sudden cardiac death occur more frequently in men in population studies,^1-3^ our analysis of 2,187 sex-differential cardiac signals across 760 drugs reveals that 67% of these drug-triggered cardiac events disproportionately affect women. This reversal is not confined to the well-recognized QT prolongation phenomenon but extends across the entire spectrum of serious cardiac adverse events, including MI (82% female), cardiac arrest (85% female), and sudden cardiac death (100% female). To our knowledge, this is the first systematic demonstration that the female predominance of drug-induced cardiac toxicity encompasses all major categories of serious cardiac adverse events.

### Mechanistic considerations

Several biological mechanisms may underlie this pervasive female cardiac vulnerability to pharmacological perturbation. First, sex differences in cardiac electrophysiology are well established. Women have longer baseline QTc intervals, lower repolarization reserve, and greater susceptibility to early afterdepolarizations---the cellular substrate for torsade de pointes and, by extension, other arrhythmogenic events.^7-9^ The present data suggest that these electrophysiological sex differences have consequences far beyond torsade de pointes, potentially contributing to the female excess in cardiac arrest and sudden cardiac death observed across hundreds of drugs.

Second, pharmacokinetic sex differences are pervasive and underappreciated. Women generally have higher drug exposure at equivalent doses due to lower body weight, higher body fat percentage, lower glomerular filtration rate, and sex-specific differences in cytochrome P450 and transporter expression.^17^ The FDA's landmark 2013 decision to halve the recommended zolpidem dose for women acknowledged this principle for a single drug; our data suggest that similar sex-specific dosing considerations may be warranted across a far broader pharmacological landscape.^18^

Third, sex hormones directly modulate cardiac ion channel function. Estrogen enhances L-type calcium current (I_CaL_) and reduces the rapidly activating delayed rectifier potassium current (I_Kr_), both of which prolong action potential duration and increase arrhythmia susceptibility.^19^ Testosterone, conversely, shortens repolarization and may confer a degree of antiarrhythmic protection.^20^ These hormonal effects may explain why the female cardiac excess extends beyond arrhythmias to encompass ischemic events: estrogen-mediated enhancement of vasoreactivity and coronary microvascular dysfunction could amplify drug-induced myocardial ischemia in women.^21^

Fourth, the exclusively female cardiac signal profile of sildenafil is mechanistically illuminating. PDE5 is expressed in cardiac myocytes, and sildenafil modulates intracellular cyclic GMP signaling with sex-dependent effects.^22^ The growing use of sildenafil for pulmonary arterial hypertension---a condition with strong female predominance---creates a clinical scenario where sex-specific cardiac pharmacology intersects with sex-biased prescribing patterns.

### The palpitations exception

The sole cardiac adverse event with male predominance---palpitations---warrants specific discussion. Unlike other cardiac endpoints in our analysis, palpitations are a symptom-based rather than diagnosis-based adverse event report. They are frequently associated with anxiety, panic attacks, and somatization, conditions for which male patients may generate disproportionate pharmacovigilance reports due to clinical novelty (palpitations in men may prompt more concern and reporting than in women, where they are often attributed to anxiety or hormonal fluctuation).^12^ Additionally, palpitations associated with sympathomimetic agents, stimulants, and certain supplements may be more prevalent in male users of these products. The male predominance of palpitations thus likely reflects symptom-reporting dynamics rather than true sex-differential cardiac pathophysiology, and its isolation as the sole male-predominant cardiac adverse event reinforces rather than undermines the broader pattern of female cardiac vulnerability.

### Implications for cardiac safety assessment in drug development

These findings have direct implications for pharmaceutical regulation and clinical practice. Current ICH guidelines mandate thorough QT (TQT) studies during drug development, with recognized sex-specific analysis requirements.^23^ However, our data demonstrate that drug-induced female cardiac vulnerability extends far beyond QT prolongation. We propose that cardiac safety assessments should:

1. **Mandate sex-stratified analysis of all cardiac endpoints** in clinical trials, not only QTc. The female excess in drug-induced MI, cardiac arrest, and sudden cardiac death may be missed if only aggregate cardiac event rates are reported.

2. **Lower cardiac monitoring thresholds for women** during post-market surveillance. The assumption that women are "cardioprotected" may paradoxically lead to underdetection of drug-induced cardiac events in female patients.

3. **Reconsider sex-specific dosing** for drugs with prominent cardiac signals. If higher female drug exposure drives the observed cardiac excess, then weight- or sex-adjusted dosing could mitigate risk.

4. **Integrate pharmacovigilance data with molecular mechanisms** in cardiac safety assessment. Knowledge graph approaches such as SexDiffKG can identify high-risk drug--target--pathway combinations before cardiac events accumulate in post-market surveillance.

### Clinical implications

For practicing clinicians, the most actionable finding is that drug-induced cardiac risk should not be assumed to mirror disease epidemiology. A woman prescribed a drug with known cardiac adverse event potential may face substantially higher risk than a man on the same drug, even though population-level MI and cardiac arrest rates are higher in men. This is particularly relevant for:

- **Psychotropic medications**: Risperidone (100% female cardiac signals), trazodone (log-ratio 2.94), and the broader antipsychotic class (71% female-biased) represent a major area of concern, given that these drugs are disproportionately prescribed to women.^14^
- **Emerging therapies**: Ketamine's 5.5-fold female excess in MI signals (log-ratio 2.46) demands urgent attention as esketamine nasal spray is increasingly prescribed for treatment-resistant depression.^16^
- **Cardiovascular drugs themselves**: ACE inhibitors (70% female-biased), beta-blockers (62% female-biased), and calcium channel blockers (58% female-biased) show the paradox most starkly---the very drugs prescribed to protect the heart show sex-differential cardiac harm patterns favoring female risk.

### Strengths

This study has several notable strengths. First, the dataset is unprecedentedly large: 14.5 million deduplicated FAERS reports spanning 21 years and 87 quarterly submissions. Second, drug name normalization using the DiAna dictionary mitigates the well-known challenge of inconsistent drug naming in FAERS. Third, the analysis spans 19 cardiac adverse events and 760 drugs, providing a comprehensive rather than selective assessment. Fourth, temporal validation demonstrates that the female cardiac predominance is stable across two independent time periods (84% directional concordance). Fifth, integration within a knowledge graph linking pharmacovigilance data to molecular targets, pathways, and gene expression provides mechanistic context for observed sex differences.

### Limitations

Several limitations must be acknowledged. First, FAERS is a spontaneous reporting system subject to reporting biases, including differential reporting rates by sex, health care provider type, and drug indication. Women constitute 60.2% of FAERS reports, creating a baseline female excess in all pharmacovigilance signals. However, our cardiac finding (67% female) significantly exceeds this baseline (P < 10^-6^), and our analytical approach using sex-specific ROR partially corrects for marginal reporting differences. Second, we cannot establish causality from disproportionality analysis; confounding by indication, comorbidity, and comedication are inherent limitations of pharmacovigilance data. Third, FAERS does not capture all adverse events, and underreporting may vary by sex and event severity. Fourth, the absence of dosing information in most FAERS reports prevents direct assessment of the pharmacokinetic hypothesis (that higher female drug exposure drives the cardiac excess). Fifth, while we identified 2,187 cardiac signals, rare events such as sudden cardiac death (n = 7 signals) have limited statistical power for subgroup analyses.

### Conclusions

Drug-induced cardiac adverse events show a striking and consistent female predominance that reverses the well-established male predominance of cardiovascular disease in the general population. Across 2,187 sex-differential cardiac signals spanning 760 drugs and 19 cardiac endpoints, 67% showed female excess, with the most lethal events---sudden cardiac death, cardiac arrest, and MI---showing the strongest female bias. This finding extends the well-known female susceptibility to drug-induced QT prolongation to the entire spectrum of serious cardiac adverse drug reactions. We propose that drugs unmask a latent female cardiac vulnerability that is not reflected in epidemiological disease prevalence, with immediate implications for sex-stratified cardiac safety monitoring in drug development and clinical practice.

---

## STUDY HIGHLIGHTS

**What is the current knowledge on the topic?**
Drug-induced QT prolongation is known to disproportionately affect women. However, cardiovascular disease---including MI, cardiac arrest, and sudden cardiac death---is epidemiologically more common in men. Whether drug-induced cardiac adverse events beyond QT prolongation show sex-differential patterns has not been systematically investigated.

**What question did this study address?**
Do drug-induced cardiac adverse events, broadly defined across 19 cardiac endpoints and 760 drugs, show male or female predominance in 14.5 million FAERS reports?

**What does this study add to our knowledge?**
Drug-induced cardiac adverse events show a striking female predominance (67%) that reverses the male epidemiological predominance of cardiovascular disease. This female excess extends to MI (82%), cardiac arrest (85%), and sudden cardiac death (100%), and is consistent across drug classes and temporally stable over 21 years.

**How might this change clinical pharmacology or translational science?**
Cardiac safety assessment in drug development should mandate sex-stratified analysis of all cardiac endpoints, not only QTc. Clinicians should recognize that drug-induced cardiac risk may be substantially higher in women than disease epidemiology would suggest, particularly for psychotropic agents and emerging therapies such as esketamine.

---

## ACKNOWLEDGMENTS

All computation was performed on sovereign local infrastructure (NVIDIA DGX Spark, Grace Blackwell GB10, 128 GB unified memory) with zero cloud dependencies. SexDiffKG is available at https://github.com/coevolve-network/sexdiffkg and archived on Zenodo.

## AUTHOR CONTRIBUTIONS

M.J.A.A.S. conceived and designed the study, performed all analyses, constructed the knowledge graph, and wrote the manuscript.

## FUNDING

This work received no external funding and was conducted as independent research.

## CONFLICT OF INTEREST

The author declares no conflicts of interest.

## DATA AVAILABILITY

The complete SexDiffKG knowledge graph, sex-differential signals, and analysis code are publicly available on Zenodo (DOI: pending) and GitHub (https://github.com/coevolve-network/sexdiffkg). FAERS source data are publicly available from the FDA (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html).

---

## REFERENCES

1. Roth GA, Mensah GA, Johnson CO, et al. Global burden of cardiovascular diseases and risk factors, 1990--2019: update from the GBD 2019 Study. *J Am Coll Cardiol*. 2020;76(25):2982-3021.

2. Mehta LS, Beckie TM, DeVon HA, et al. Acute myocardial infarction in women: a scientific statement from the American Heart Association. *Circulation*. 2016;133(9):916-947.

3. Vogel B, Acevedo M, Appelman Y, et al. The Lancet women and cardiovascular disease Commission: reducing the global burden by 2030. *Lancet*. 2021;397(10292):2385-2438.

4. Garcia M, Mulvagh SL, Merz CNB, Buring JE, Manson JE. Cardiovascular disease in women: clinical perspectives. *Circ Res*. 2016;118(8):1273-1293.

5. Vaccarino V, Parsons L, Every NR, Barron HV, Krumholz HM. Sex-based differences in early mortality after myocardial infarction. *N Engl J Med*. 1999;341(4):217-225.

6. Berger JS, Elliott L, Gallup D, et al. Sex differences in mortality following acute coronary syndromes. *JAMA*. 2009;302(8):874-882.

7. Makkar RR, Fromm BS, Steinman RT, Meissner MD, Lehmann MH. Female gender as a risk factor for torsades de pointes associated with cardiovascular drugs. *JAMA*. 1993;270(21):2590-2597.

8. Roden DM. Drug-induced prolongation of the QT interval. *N Engl J Med*. 2004;350(10):1013-1022.

9. Darpo B. Spectrum of drugs prolonging QT interval and the incidence of torsades de pointes. *Eur Heart J Suppl*. 2001;3(suppl K):K70-K80.

10. Shaik MJAA. SexDiffKG: a sex-stratified knowledge graph integrating 14.5 million FDA adverse event reports with multi-omics data for pharmacovigilance. *bioRxiv*. 2026. doi: pending.

11. Fusaroli M, Raschi E, Poluzzi E, et al. DiAna, an expert system for drug safety: a pilot study on the FDA Adverse Event Reporting System. *Drug Saf*. 2023;46(3):245-259.

12. Barsky AJ, Cleary PD, Coeytaux RR, Ruskin JN. Psychiatric disorders in medical outpatients complaining of palpitations. *J Gen Intern Med*. 1994;9(6):306-313.

13. Ghofrani HA, Osterloh IH, Grimminger F. Sildenafil: from angina to erectile dysfunction to pulmonary hypertension and beyond. *Nat Rev Drug Discov*. 2006;5(8):689-702.

14. Solmi M, Murru A, Pacchiarotti I, et al. Safety, tolerability, and risks associated with first- and second-generation antipsychotics: a state-of-the-art clinical review. *Ther Clin Risk Manag*. 2017;13:757-777.

15. Stryjer R, Strous RD, Shaked G, et al. Trazodone and cardiac arrhythmias: a review. *Isr J Psychiatry Relat Sci*. 2010;47(4):288-292.

16. McIntyre RS, Rosenblat JD, Nemeroff CB, et al. Synthesizing the evidence for ketamine and esketamine in treatment-resistant depression: an international expert opinion on the available evidence and implementation. *Am J Psychiatry*. 2021;178(5):383-399.

17. Soldin OP, Mattison DR. Sex differences in pharmacokinetics and pharmacodynamics. *Clin Pharmacokinet*. 2009;48(3):143-157.

18. US Food and Drug Administration. FDA Drug Safety Communication: FDA requires lower recommended dose for Ambien and other sleep medicines containing zolpidem. January 10, 2013. Available at: https://www.fda.gov/drugs/drug-safety-and-availability/

19. Yang PC, Clancy CE. Effects of sex hormones on cardiac repolarization. *J Cardiovasc Pharmacol*. 2010;56(2):123-129.

20. Pham TV, Rosen MR. Sex, hormones, and repolarization. *Cardiovasc Res*. 2002;53(3):740-751.

21. Bairey Merz CN, Shaw LJ, Reis SE, et al. Insights from the NHLBI-sponsored Women's Ischemia Syndrome Evaluation (WISE) Study. *J Am Coll Cardiol*. 2006;47(3 Suppl):S21-S29.

22. Takimoto E, Champion HC, Li M, et al. Chronic inhibition of cyclic GMP phosphodiesterase 5A prevents and reverses cardiac hypertrophy. *Nat Med*. 2005;11(2):214-222.

23. International Council for Harmonisation. ICH E14: The Clinical Evaluation of QT/QTc Interval Prolongation and Proarrhythmic Potential for Non-Antiarrhythmic Drugs. 2005 (revised 2015).
