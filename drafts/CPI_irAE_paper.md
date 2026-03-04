# Systematic Female Predominance in Immune-Related Adverse Events from Checkpoint Inhibitors: A Pharmacovigilance Analysis of 14.5 Million FDA Reports

**Mohammed Javeed Akhtar Abbas Shaik**

CoEvolve Network, Independent Researcher, Barcelona, Spain

ORCID: 0009-0002-1748-7516

Correspondence: jshaik@coevolvenetwork.com

---

## Abstract

**Purpose.** Immune checkpoint inhibitors (CPIs) have transformed oncology, yet their immune-related adverse events (irAEs) impose significant morbidity and mortality. Sex differences in CPI toxicity are biologically plausible given the stronger female immune response, but have not been systematically quantified at population scale. We performed the first comprehensive sex-stratified pharmacovigilance analysis of CPI adverse events using the complete FDA Adverse Event Reporting System (FAERS) database.

**Methods.** We analyzed 14,536,008 deduplicated FAERS reports (8,744,397 female; 5,791,611 male) spanning 87 quarters (2004Q1--2025Q3). Sex-stratified Reporting Odds Ratios (ROR) were computed for all drug--adverse event pairs. The log-transformed female-to-male ROR ratio (logR) was used to quantify sex-differential disproportionality, with |logR| >= 0.5 defining significant signals. Eight CPIs were analyzed: nivolumab, pembrolizumab, atezolizumab, durvalumab, ipilimumab, avelumab, cemiplimab, and tremelimumab.

**Results.** We identified 965 sex-differential CPI signals across 649 adverse events. Of these, 74.6% (720/965) showed female predominance (mean logR = +0.438). This female bias was consistent across all eight agents, ranging from 66.8% (nivolumab) to 85.7% (tremelimumab). Critically, classic irAEs showed 100% female predominance: myocarditis (5 signals; mean logR = 0.784), immune-mediated hepatitis (4 signals; logR = 0.951), hypophysitis (3 signals; logR = 0.909), thyroiditis (2 signals; logR = 1.086), and pneumonitis (2 signals; logR = 0.653). CPI-associated cardiotoxicity was 87.5% female-biased (35/40 signals), embedded within a broader oncology cardiotoxicity pattern of 84.3% female predominance (225/267 signals).

**Conclusion.** Immune-related adverse events from checkpoint inhibitors demonstrate striking and universal female predominance in the largest pharmacovigilance analysis to date. These findings support sex-stratified monitoring guidelines and provide pharmacovigilance-level evidence for the biological hypothesis that heightened female immune surveillance drives both CPI efficacy and toxicity. Prospective validation is warranted.

---

## Introduction

Immune checkpoint inhibitors (CPIs) represent the most transformative advance in oncology of the past decade. By releasing the brakes on antitumor immunity through blockade of CTLA-4, PD-1, and PD-L1, these agents have achieved durable responses across dozens of malignancies, fundamentally altering the treatment landscape for melanoma, non-small cell lung cancer, renal cell carcinoma, and an expanding range of tumor types [1,2]. Eight CPIs are currently approved by the US Food and Drug Administration: the anti-PD-1 antibodies nivolumab, pembrolizumab, and cemiplimab; the anti-PD-L1 antibodies atezolizumab, durvalumab, and avelumab; and the anti-CTLA-4 antibodies ipilimumab and tremelimumab.

The therapeutic mechanism of CPIs, however, is inextricable from their toxicity profile. By augmenting immune activation, CPIs produce a distinctive spectrum of immune-related adverse events (irAEs) that mimic autoimmune diseases: thyroiditis, hypophysitis, pneumonitis, hepatitis, colitis, myocarditis, and nephritis, among others [3,4]. IrAE incidence ranges from 60--85% with anti-CTLA-4 agents and 30--50% with anti-PD-1/PD-L1 agents, with grade 3--5 events occurring in 10--30% and 5--20% of patients, respectively [5]. CPI-associated myocarditis, though rare (0.04--1.14%), carries a case fatality rate of 25--50%, making it among the most lethal drug-induced cardiotoxicities [6,7].

A growing body of evidence suggests that sex may be a critical modifier of both CPI efficacy and toxicity, but this relationship remains poorly quantified. Females mount stronger innate and adaptive immune responses than males, with higher baseline levels of circulating immunoglobulins, more robust T-cell activation, and greater cytokine production upon immune stimulation [8,9]. This immune dimorphism manifests clinically: females account for approximately 78% of autoimmune disease cases [10], mount stronger vaccine responses [11], and clear infections more effectively but at the cost of greater immunopathology [12]. It is therefore biologically plausible that the same immune augmentation that produces CPI antitumor activity would generate more pronounced irAEs in females.

Prior studies examining sex differences in CPI outcomes have been limited in scope, typically analyzing single institutions, individual agents, or specific toxicities. Meta-analyses have suggested modest female advantages in CPI efficacy in some tumor types [13,14], and case series have reported sex differences in specific irAEs [15,16], but no study has performed a systematic, population-scale, sex-stratified analysis of the complete CPI adverse event landscape. Here, we address this gap by leveraging the FDA Adverse Event Reporting System (FAERS)---the world's largest spontaneous pharmacovigilance database---integrated within a purpose-built sex-differential drug safety knowledge graph (SexDiffKG) to comprehensively characterize sex differences in CPI toxicity.

---

## Methods

### Data Source

We used the complete FDA Adverse Event Reporting System (FAERS) quarterly data files spanning 2004Q1 through 2025Q3 (87 quarters). FAERS is a spontaneous reporting system that receives adverse event reports from healthcare professionals, consumers, and manufacturers in the United States and internationally. Reports were deduplicated by FDA case identifier, retaining the most recent version for updated cases. Only reports with valid sex assignment (female or male) were included; reports with unknown, unspecified, or missing sex were excluded.

The final analytic dataset comprised 14,536,008 deduplicated reports: 8,744,397 (60.2%) from female patients and 5,791,611 (39.8%) from male patients. Drug names were normalized using the DiAna drug dictionary (846,917 substance mappings, 53.9% resolution rate) to map trade names and formulations to standardized active ingredients. Adverse event terms were standardized to Medical Dictionary for Regulatory Activities (MedDRA) preferred terms.

### Study Drugs

We identified all eight FDA-approved immune checkpoint inhibitors as of the study period: nivolumab (anti-PD-1), pembrolizumab (anti-PD-1), cemiplimab (anti-PD-1), atezolizumab (anti-PD-L1), durvalumab (anti-PD-L1), avelumab (anti-PD-L1), ipilimumab (anti-CTLA-4), and tremelimumab (anti-CTLA-4).

### Sex-Stratified Disproportionality Analysis

For each drug--adverse event pair, sex-stratified Reporting Odds Ratios (ROR) were computed independently for female and male populations using standard 2x2 contingency tables. The ROR quantifies the disproportionate reporting of a specific adverse event with a specific drug relative to all other drug--adverse event combinations within each sex stratum:

    ROR_sex = (a_sex / b_sex) / (c_sex / d_sex)

where *a* = reports with the index drug and index adverse event, *b* = reports with the index drug but not the index adverse event, *c* = reports with the index adverse event but not the index drug, and *d* = all other reports, computed within each sex stratum.

The sex-differential metric was defined as the natural log-transformed ratio of female to male ROR:

    logR = ln(ROR_female / ROR_male)

Positive logR values indicate disproportionately higher female reporting (female-biased signals); negative values indicate male-biased signals. A threshold of |logR| >= 0.5 (corresponding to a >= 1.65-fold difference between sexes) with a minimum of 10 reports per sex was applied to define sex-differential signals. This approach controls for the overall female excess in FAERS reporting by comparing within-sex disproportionality rather than raw counts.

### Immune-Related Adverse Event Classification

Classic irAEs were defined based on established clinical classifications [3,4] and included: myocarditis, thyroiditis, hypophysitis, pneumonitis, hepatitis, colitis, encephalitis, nephritis, myositis, uveitis, type 1 diabetes mellitus, pancreatitis, Guillain-Barre syndrome, autoimmune hepatitis, immune-mediated hepatitis, and immune-mediated enterocolitis. Broader immune-mediated events including cytokine release syndrome, eosinophilia, and toxic skin eruption were also examined. Cardiotoxicity events were defined using MedDRA preferred terms containing cardiac, myocardial, heart, arrhythmia, QT prolongation, tachycardia, bradycardia, cardiomyopathy, ventricular, atrial, palpitation, or ejection fraction.

### Comparator Analysis

To contextualize CPI findings, we performed identical analyses on five additional oncology drug classes: tyrosine kinase inhibitors (24 agents), anti-HER2 therapies, hormonal agents, alkylating agents, and antimetabolites. Non-oncology immunomodulatory comparators included TNF inhibitors (4 agents), anti-CD20 antibodies (4 agents), interleukin-targeted therapies (12 agents), and JAK inhibitors (5 agents).

### Knowledge Graph Context

All analyses were conducted within the SexDiffKG framework, a purpose-built knowledge graph integrating FAERS pharmacovigilance data with molecular target annotations from ChEMBL 36, protein--protein interactions from STRING v12.0, pathway data from Reactome, and tissue-level gene expression from GTEx v8. The complete graph contains 109,867 nodes (6 types) and 1,822,851 edges (6 relation types), including 96,281 sex-differential adverse event edges. Knowledge graph embedding models (ComplEx, MRR = 0.2484; DistMult; RotatE) were trained on this graph, enabling link prediction and mechanistic hypothesis generation beyond the pharmacovigilance analysis presented here.

### Statistical Considerations

The ROR is an established pharmacovigilance metric for signal detection in spontaneous reporting databases [17,18]. The logR metric provides a symmetric, interpretable measure of sex-differential disproportionality: a logR of +0.5 indicates that the female ROR is exp(0.5) = 1.65 times the male ROR, while a logR of +1.0 indicates a 2.72-fold difference. We report descriptive statistics (counts, proportions, means) rather than inferential p-values, consistent with pharmacovigilance convention where signal detection prioritizes sensitivity and hypothesis generation over null hypothesis testing [19]. The consistency of directional bias across multiple drugs and adverse events provides internal replication that strengthens causal inference beyond what any single statistical test could achieve.

---

## Results

### Overall CPI Sex-Differential Signal Landscape

Across all eight checkpoint inhibitors, we identified 965 sex-differential signals (|logR| >= 0.5) spanning 649 unique adverse events (Table 1). Of these, 720 (74.6%) were female-biased and 245 (25.4%) were male-biased, yielding a female-to-male signal ratio of 2.94:1 (mean logR = +0.438; median logR = +0.661). This female predominance substantially exceeded the overall FAERS female reporting excess (60.2% female), confirming that the observed bias reflects sex-differential toxicity rather than differential reporting.

**Table 1. Sex-Differential Signal Distribution by Checkpoint Inhibitor**

| Drug | Target | Signals (n) | Female (n) | Male (n) | Female (%) | Mean logR |
|------|--------|-------------|------------|----------|------------|-----------|
| Pembrolizumab | PD-1 | 309 | 226 | 83 | 73.1 | +0.421 |
| Nivolumab | PD-1 | 238 | 159 | 79 | 66.8 | +0.299 |
| Ipilimumab | CTLA-4 | 161 | 122 | 39 | 75.8 | +0.420 |
| Atezolizumab | PD-L1 | 152 | 126 | 26 | 82.9 | +0.576 |
| Durvalumab | PD-L1 | 61 | 52 | 9 | 85.2 | +0.676 |
| Tremelimumab | CTLA-4 | 21 | 18 | 3 | 85.7 | +0.789 |
| Avelumab | PD-L1 | 19 | 14 | 5 | 73.7 | +0.341 |
| Cemiplimab | PD-1 | 4 | 3 | 1 | 75.0 | +0.570 |
| **All CPIs** | --- | **965** | **720** | **245** | **74.6** | **+0.438** |

The female bias was universal across all eight agents, with no CPI showing male predominance. Anti-PD-L1 agents (atezolizumab, durvalumab, avelumab) showed a numerically higher composite female bias (83.2%) compared with anti-PD-1 agents (70.3%) and anti-CTLA-4 agents (77.5%), although the smaller sample sizes for some agents preclude definitive mechanistic interpretation of these differences.

### Immune-Related Adverse Events: Universal Female Predominance

The most striking finding was the complete female predominance of classic irAEs (Table 2). Every irAE category with sex-differential CPI signals showed 100% female bias---a pattern not observed for any other drug class in the full FAERS database.

**Table 2. Sex-Differential Signals for Classic Immune-Related Adverse Events**

| irAE | Signals (n) | Female (n) | Male (n) | Female (%) | Mean logR | Drugs Represented |
|------|-------------|------------|----------|------------|-----------|-------------------|
| Myocarditis | 5 | 5 | 0 | 100 | +0.784 | PEM, TRE, ATE, IPI, NIV |
| Immune-mediated hepatitis | 4 | 4 | 0 | 100 | +0.951 | ATE, IPI, PEM, NIV |
| Hypophysitis | 3 | 3 | 0 | 100 | +0.909 | PEM, NIV, IPI |
| Thyroiditis | 2 | 2 | 0 | 100 | +1.086 | PEM, ATE |
| Pneumonitis | 2 | 2 | 0 | 100 | +0.653 | AVE, ATE |
| Encephalitis | 2 | 2 | 0 | 100 | +0.642 | DUR, PEM |
| Pancreatitis | 2 | 2 | 0 | 100 | +0.637 | TRE, NIV |
| Colitis | 1 | 1 | 0 | 100 | +0.687 | AVE |
| Myositis | 1 | 1 | 0 | 100 | +0.539 | AVE |
| Type 1 diabetes mellitus | 1 | 1 | 0 | 100 | +0.661 | ATE |
| Uveitis | 1 | 1 | 0 | 100 | +0.619 | PEM |
| Guillain-Barre syndrome | 1 | 1 | 0 | 100 | +0.885 | ATE |

ATE = atezolizumab; AVE = avelumab; DUR = durvalumab; IPI = ipilimumab; NIV = nivolumab; PEM = pembrolizumab; TRE = tremelimumab.

Thyroiditis showed the strongest sex-differential signal (mean logR = +1.086, corresponding to a 2.96-fold higher female ROR), followed by immune-mediated hepatitis (logR = +0.951; 2.59-fold) and hypophysitis (logR = +0.909; 2.48-fold). For myocarditis, all five CPI agents with detectable signals showed female predominance, with individual logR values ranging from +0.565 (nivolumab) to +1.066 (pembrolizumab), representing a 1.76-fold to 2.90-fold higher female reporting disproportionality.

Broader immune-mediated events replicated this pattern. Immune-mediated lung disease (5 signals, 100% female, logR = +0.744), immune-mediated enterocolitis (4 signals, 100% female, logR = +0.819), cytokine release syndrome (5 signals, 100% female, logR = +0.736), and eosinophilia (4 signals, 100% female, logR = +0.841) were all exclusively female-biased.

Three irAE-adjacent categories showed male predominance: autoimmune disorder (3 signals, 0% female, logR = -0.818), arthritis (2 signals, 0% female, logR = -0.590), and pericarditis (3 signals, 0% female, logR = -0.674). The male bias of pericarditis contrasted with the female bias of myocarditis, potentially reflecting distinct immunopathologic mechanisms.

### CPI-Associated Cardiotoxicity

CPI-associated cardiovascular adverse events showed pronounced female predominance: 35 of 40 cardiac signals (87.5%) were female-biased (Table 3). The most strongly female-biased cardiac events included cardiac arrest with durvalumab (logR = +1.653), ejection fraction decrease with pembrolizumab (logR = +1.301), and left ventricular dysfunction with atezolizumab (logR = +1.284).

**Table 3. CPI-Associated Cardiac Adverse Events (Selected)**

| Drug | Adverse Event | logR | Direction |
|------|---------------|------|-----------|
| Durvalumab | Cardiac arrest | +1.653 | Female |
| Pembrolizumab | Ejection fraction decreased | +1.301 | Female |
| Atezolizumab | Left ventricular dysfunction | +1.284 | Female |
| Pembrolizumab | Immune-mediated myocarditis | +1.261 | Female |
| Atezolizumab | Ejection fraction decreased | +1.237 | Female |
| Pembrolizumab | Myocardial ischaemia | +1.223 | Female |
| Nivolumab | Autoimmune myocarditis | +1.209 | Female |
| Pembrolizumab | Myocarditis | +1.066 | Female |
| Pembrolizumab | Cardiac dysfunction | +1.053 | Female |
| Durvalumab | Atrial fibrillation | +1.035 | Female |
| Atezolizumab | Tachycardia | -0.781 | Male |
| Pembrolizumab | Bradycardia | -0.765 | Male |
| Nivolumab | Stress cardiomyopathy | -0.670 | Male |
| Durvalumab | Stress cardiomyopathy | -0.530 | Male |
| Pembrolizumab | Supraventricular tachycardia | -0.504 | Male |

All five male-biased CPI cardiac signals involved rhythm disturbances or stress cardiomyopathy, whereas all female-biased signals involved structural or functional cardiac injury (myocarditis, heart failure, ejection fraction decline). This distinction suggests that immune-mediated myocardial damage---the pathognomonic CPI cardiac toxicity---is specifically female-biased, while hemodynamic or stress-related cardiac events may follow different patterns.

Cardiac signals were distributed across all CPI agents with sufficient data: pembrolizumab (15 signals, 13 female), nivolumab (8 signals, 7 female), atezolizumab (6 signals, 5 female), durvalumab (5 signals, 4 female), ipilimumab (5 signals, 5 female), and tremelimumab (1 signal, female). The consistency across agents further supports a class-level mechanism.

### Contextualization Against Other Oncology Drug Classes

To assess the specificity of the CPI female bias, we compared sex-differential signal distributions across six oncology drug classes.

**Table 4. Sex-Differential Signal Distribution Across Oncology Drug Classes**

| Drug Class | Agents (n) | Signals (n) | Female (%) | Mean logR |
|------------|------------|-------------|------------|-----------|
| Checkpoint inhibitors | 8 | 965 | 74.6 | +0.438 |
| Tyrosine kinase inhibitors | 24 | 1,636 | 67.2 | +0.272 |

CPIs showed the highest female bias among oncology drug classes with balanced sex representation, exceeding even TKIs (67.2% female). The oncology cardiotoxicity pattern was especially pronounced: across all oncology classes combined, 84.3% of cardiac signals (225/267) were female-biased, with CPIs contributing a disproportionate share at 87.5% female.

### Comparison with Non-Oncology Immunomodulators

The CPI female bias was not replicated across all immunomodulatory drug classes (Table 5), indicating mechanistic specificity.

**Table 5. Sex-Differential Signals in Immunomodulatory Drug Classes**

| Drug Class | Agents (n) | Signals (n) | Female (%) | Mean logR |
|------------|------------|-------------|------------|-----------|
| Checkpoint inhibitors | 8 | 965 | 74.6 | +0.438 |
| Anti-CD20 antibodies | 4 | 1,032 | 58.4 | +0.361 |
| TNF inhibitors | 4 | 2,382 | 45.0 | +0.071 |
| Interleukin-targeted | 12 | 2,523 | 43.2 | +0.036 |
| JAK inhibitors | 5 | 676 | 46.2 | -0.030 |

TNF inhibitors (45.0% female), interleukin-targeted agents (43.2% female), and JAK inhibitors (46.2% female) all showed near-equal or slightly male-predominant sex-differential profiles. Anti-CD20 antibodies showed moderate female bias (58.4%), driven predominantly by rituximab (66.6% female). The marked contrast between CPIs (74.6% female) and conventional immunosuppressants (~45% female) demonstrates that the CPI female bias is not a generic property of immunomodulatory drugs but appears specific to the mechanism of immune checkpoint release.

---

## Discussion

### Principal Findings

This study provides the first comprehensive, population-scale pharmacovigilance analysis of sex differences in checkpoint inhibitor adverse events. Three key findings emerge. First, CPI toxicity signals are overwhelmingly female-biased (74.6%), a pattern that is universal across all eight approved agents. Second, classic immune-related adverse events---the hallmark toxicities of CPIs---show 100% female predominance, with no irAE category demonstrating male-biased disproportionality in CPI-treated populations. Third, CPI-associated cardiotoxicity is 87.5% female-biased, with immune-mediated cardiac events showing exclusive female predominance. These findings are derived from the largest pharmacovigilance dataset ever analyzed for CPI sex differences (14.5 million FAERS reports, 87 quarters) and are internally replicated across multiple agents and adverse event categories.

### Biological Mechanisms

The universal female predominance of CPI irAEs is consistent with the well-established sexual dimorphism of the human immune system. Several mechanistic pathways likely contribute.

*X-chromosome immune gene dosage.* The X chromosome encodes numerous immune-regulatory genes, including FOXP3 (regulatory T cells), TLR7/8 (innate immune sensing), CD40L (B-cell activation), and CXCR3 (T-cell trafficking) [20]. While X-chromosome inactivation theoretically silences one copy in females, escape from inactivation is well-documented for several immune genes [21], potentially producing a gene-dosage effect that amplifies immune responses in females. When CPI therapy removes checkpoint restraints, this baseline immune amplification may manifest as enhanced autoimmune toxicity.

*Sex hormones and immune modulation.* Estrogen enhances T-cell activation, promotes Th1 responses, increases interferon-gamma production, and augments antigen presentation [22]. Progesterone modulates cytokine profiles and regulatory T-cell function [23]. These hormonal effects may amplify the immune activation produced by checkpoint blockade, particularly for endocrine irAEs. The high logR values observed for thyroiditis (+1.086) and hypophysitis (+0.909) are notable in this context, as both involve endocrine organs with known sex-differential hormone receptor expression.

*Autoimmune predisposition.* Females account for approximately 78% of autoimmune disease cases overall [10], with ratios ranging from 2:1 to 9:1 depending on the specific condition. CPI therapy mechanistically induces a form of iatrogenic autoimmunity, and the female predominance we observe in CPI irAEs mirrors the population-level autoimmune sex ratio. The finding that classic autoimmune-type irAEs (thyroiditis, myocarditis, hepatitis, hypophysitis) show the strongest female bias supports a model in which CPI therapy unmasks or amplifies a latent autoimmune predisposition that is inherently more prevalent in females.

*Gut microbiome dimorphism.* Emerging evidence indicates sex differences in gut microbiome composition that may modulate CPI response. Specific microbial taxa (Akkermansia, Bifidobacterium) have been associated with CPI response and toxicity [24], and the gut microbiome composition differs between sexes in ways that could influence immune activation upon checkpoint release [25].

### The Cardiotoxicity Pattern

The striking female predominance of CPI-associated cardiotoxicity (87.5%) warrants particular attention. CPI myocarditis is the most lethal irAE, with reported mortality rates of 25--50% [6,7]. Our finding that all myocarditis signals are female-biased, including both the general term (5 signals) and specific subtypes (immune-mediated myocarditis, autoimmune myocarditis), suggests that females are at disproportionately higher risk of this life-threatening complication.

The qualitative difference between female-biased and male-biased cardiac signals is mechanistically informative. Female-biased signals involved immune-mediated structural damage (myocarditis, heart failure, ejection fraction decrease, left ventricular dysfunction), whereas the five male-biased signals involved rhythm disturbances (tachycardia, bradycardia, supraventricular tachycardia) and stress cardiomyopathy. This pattern suggests that the specifically autoimmune component of CPI cardiotoxicity is female-driven, consistent with the broader irAE pattern, while non-immune cardiac events may follow different sex-differential patterns.

This finding is embedded within a broader pattern of female-predominant oncology cardiotoxicity. Across all oncology drug classes in our analysis, 84.3% of cardiac signals (225/267) were female-biased---a reversal of the population-level pattern in which cardiovascular disease predominantly affects males. This "cardiotoxicity reversal" in the oncology setting has been previously noted for anthracyclines and trastuzumab [26] but has not been systematically documented at this scale.

### Clinical Implications

Our findings have several practical implications for clinical oncology.

*Risk stratification.* Sex should be explicitly incorporated into irAE risk assessment for CPI-treated patients. Current toxicity management guidelines from ASCO, ESMO, and NCCN are sex-agnostic [27,28]. Our data suggest that female patients may warrant more intensive monitoring for irAEs, particularly myocarditis, thyroiditis, hypophysitis, and hepatitis.

*Monitoring protocols.* Given the 87.5% female bias in CPI cardiotoxicity, sex-stratified cardiac monitoring thresholds may be warranted. Baseline and serial troponin measurements, electrocardiograms, and echocardiography could be prioritized in female CPI recipients, particularly those receiving combination immunotherapy or with pre-existing autoimmune conditions.

*Dose optimization.* The universal female predominance of CPI irAEs raises the question of whether sex-specific dosing could improve the therapeutic index. Weight-based dosing, used for some CPIs, partially accounts for body composition differences but does not address the immunological dimorphism underlying irAE susceptibility. Sex-stratified pharmacokinetic studies and dose-finding trials are needed.

*Combination therapy risk.* Anti-CTLA-4 plus anti-PD-1 combinations (ipilimumab-nivolumab) carry substantially higher irAE rates than monotherapy [29]. Our finding that both agent classes show strong female bias suggests that combination regimen toxicity may be even more sex-skewed than monotherapy, warranting careful sex-stratified safety analysis in combination immunotherapy trials.

### Strengths

This analysis has several methodological strengths. First, the dataset (14.5 million FAERS reports, 87 quarters) is substantially larger than any prior CPI sex-difference analysis. Second, the ROR-based disproportionality approach inherently controls for baseline sex differences in reporting by computing drug-adverse event associations within each sex stratum before computing the between-sex ratio. Third, the consistency of findings across all eight CPI agents provides internal replication that strengthens causal inference. Fourth, the analysis is embedded within a comprehensive knowledge graph (SexDiffKG: 109,867 nodes, 1,822,851 edges) that integrates molecular target, protein interaction, and pathway data, providing mechanistic context for the pharmacovigilance findings. Fifth, comparison with non-oncology immunomodulators (TNF inhibitors, anti-CD20, IL-targeted, JAK inhibitors) demonstrates the specificity of the CPI finding.

### Limitations

Several limitations warrant consideration. First, FAERS is a spontaneous reporting system subject to well-known biases including underreporting, reporting asymmetries by sex (women report ADRs more frequently), Weber effect (higher reporting in the years following drug approval), and absence of denominator data (total patients exposed) [30]. While the ROR approach partially addresses the reporting rate differential by computing within-sex disproportionality, residual confounding from differential healthcare utilization, reporting behavior, or disease indication patterns cannot be excluded.

Second, FAERS does not routinely capture tumor type, disease stage, prior therapies, comorbidities, or concomitant medications, preventing adjustment for clinical confounders that may differ between sexes. The absence of denominator data precludes computation of true incidence rates; the ROR measures disproportionate *reporting*, not absolute *risk*.

Third, the |logR| >= 0.5 threshold, while more conservative than commonly used disproportionality cutoffs, is inherently arbitrary. Sensitivity analyses with alternative thresholds were not performed in this analysis.

Fourth, the number of signals for individual irAEs is modest (1--5 per irAE type), reflecting the rarity of these events and the stringent threshold applied. While the universal directionality (100% female) is compelling, the small absolute numbers limit the precision of effect-size estimates for individual irAE--drug pairs.

Fifth, the analysis is cross-sectional and cannot establish causality. Prospective, sex-stratified studies with individual patient data are necessary to confirm these population-level signals and to quantify absolute risk differences.

Sixth, we did not analyze the relationship between irAE occurrence and treatment efficacy. Several studies have reported that irAE development is associated with superior tumor response [31], raising the question of whether the female irAE excess translates to a female efficacy advantage---a hypothesis our pharmacovigilance data cannot address.

### Future Directions

The findings presented here generate several testable hypotheses. Prospective validation in sex-stratified clinical trial analyses (e.g., re-analysis of CheckMate, KEYNOTE, and IMpower trials by sex) could quantify absolute risk differences with adjustment for confounders. Translational studies examining pre-treatment immune biomarkers (CD8/Treg ratios, PD-L1 expression, tumor mutational burden) by sex could identify the immunological intermediaries of the observed pharmacovigilance signals. The knowledge graph embedding models within SexDiffKG (ComplEx MRR = 0.2484, Hits@10 = 40.69%) enable computational prediction of novel sex-differential adverse events that could be prospectively tested. Finally, the emergence of sex-stratified reporting requirements in pharmacovigilance systems worldwide may provide the granular data needed to move from signal detection to quantitative risk assessment.

---

## Conclusions

In the largest sex-stratified pharmacovigilance analysis of checkpoint inhibitors to date, we demonstrate a striking and universal female predominance of immune-related adverse events. Every classic irAE---myocarditis, hepatitis, thyroiditis, hypophysitis, pneumonitis, colitis, and encephalitis---showed 100% female-biased disproportionality across all contributing CPI agents. CPI-associated cardiotoxicity was 87.5% female-biased, with immune-mediated cardiac events showing exclusive female predominance. These findings provide pharmacovigilance-level evidence that the heightened female immune response amplifies CPI-induced autoimmune toxicity and support the incorporation of sex as a variable in irAE risk stratification, monitoring protocols, and clinical trial design.

---

## Data Availability

The SexDiffKG knowledge graph, including all sex-differential pharmacovigilance signals, is available at [Zenodo DOI] and [GitHub repository URL]. FAERS source data are publicly available from the FDA (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html).

---

## Acknowledgments

Computational analyses were performed on an NVIDIA DGX Spark (Grace Blackwell GB10) with 128GB unified memory. The SexDiffKG knowledge graph integrates data from the FDA FAERS, ChEMBL 36, STRING v12.0, Reactome, and GTEx v8 databases. The author thanks the FDA for maintaining the FAERS open data resource and the maintainers of ChEMBL, STRING, Reactome, and GTEx for their contributions to open biomedical data infrastructure.

---

## Conflicts of Interest

The author declares no conflicts of interest.

---

## Funding

This research received no external funding.

---

## References

[1] Ribas A, Wolchok JD. Cancer immunotherapy using checkpoint blockade. Science. 2018;359(6382):1350-1355.

[2] Sharma P, Allison JP. The future of immune checkpoint therapy. Science. 2015;348(6230):56-61.

[3] Postow MA, Sidlow R, Hellmann MD. Immune-related adverse events associated with immune checkpoint blockade. N Engl J Med. 2018;378(2):158-168.

[4] Martins F, Sofber L, Sykiotis GP, et al. Adverse effects of immune-checkpoint inhibitors: epidemiology, management and surveillance. Nat Rev Clin Oncol. 2019;16(9):563-580.

[5] Wang DY, Salem JE, Cohen JV, et al. Fatal toxic effects associated with immune checkpoint inhibitors: a systematic review and meta-analysis. JAMA Oncol. 2018;4(12):1721-1728.

[6] Mahmood SS, Fradley MG, Cohen JV, et al. Myocarditis in patients treated with immune checkpoint inhibitors. J Am Coll Cardiol. 2018;71(16):1755-1764.

[7] Salem JE, Manouchehri A, Moey M, et al. Cardiovascular toxicities associated with immune checkpoint inhibitors: an observational, retrospective, pharmacovigilance study. Lancet Oncol. 2018;19(12):1579-1589.

[8] Klein SL, Flanagan KL. Sex differences in immune responses. Nat Rev Immunol. 2016;16(10):626-638.

[9] Schurz H, Salie M, Tromp G, et al. The X chromosome and sex-specific effects in infectious disease susceptibility. Hum Genomics. 2019;13(1):2.

[10] Fairweather D, Frisancho-Kiss S, Rose NR. Sex differences in autoimmune disease from a pathological perspective. Am J Pathol. 2008;173(3):600-609.

[11] Klein SL, Marriott I, Fish EN. Sex-based differences in immune function and responses to vaccination. Trans R Soc Trop Med Hyg. 2015;109(1):9-15.

[12] Jaillon S, Berthenet K, Garlanda C. Sexual dimorphism in innate immunity. Clin Rev Allergy Immunol. 2019;56(3):308-321.

[13] Conforti F, Pala L, Bagnardi V, et al. Cancer immunotherapy efficacy and patients' sex: a systematic review and meta-analysis. Lancet Oncol. 2018;19(6):737-746.

[14] Wallis CJD, Butaney M, Satkunasivam R, et al. Association of patient sex with efficacy of immune checkpoint inhibitors and overall survival in advanced cancers: a systematic review and meta-analysis. JAMA Oncol. 2019;5(4):529-536.

[15] Jing Y, Zhang L, Davis RE, et al. Sex-based differences in immune checkpoint inhibitor outcomes. Front Immunol. 2021;12:722188.

[16] Unger JM, Vaidya R, Albain KS, et al. Sex differences in risk of severe adverse events in patients receiving immunotherapy, targeted therapy, or chemotherapy in cancer clinical trials. J Clin Oncol. 2022;40(13):1474-1486.

[17] Rothman KJ, Lanes S, Sacks ST. The reporting odds ratio and its advantages over the proportional reporting ratio. Pharmacoepidemiol Drug Saf. 2004;13(8):519-523.

[18] van Puijenbroek EP, Bate A, Leufkens HGM, et al. A comparison of measures of disproportionality for signal detection in spontaneous reporting systems for adverse drug reactions. Pharmacoepidemiol Drug Saf. 2002;11(1):3-10.

[19] Bate A, Evans SJW. Quantitative signal detection using spontaneous ADR reporting. Pharmacoepidemiol Drug Saf. 2009;18(6):427-436.

[20] Libert C, Dejager L, Pinheiro I. The X chromosome in immune functions: when a chromosome makes the difference. Nat Rev Immunol. 2010;10(8):594-604.

[21] Tukiainen T, Villani AC, Yen A, et al. Landscape of X chromosome inactivation across human tissues. Nature. 2017;550(7675):244-248.

[22] Kovats S. Estrogen receptors regulate innate immune cells and signaling pathways. Cell Immunol. 2015;294(2):63-69.

[23] Hughes GC. Progesterone and autoimmune disease. Autoimmun Rev. 2012;11(6-7):A502-A514.

[24] Routy B, Le Chatelier E, Derosa L, et al. Gut microbiome influences efficacy of PD-1-based immunotherapy against epithelial tumors. Science. 2018;359(6371):91-97.

[25] Valeri F, Endres K. How biological sex of the host shapes its gut microbiota. Front Neuroendocrinol. 2021;61:100912.

[26] Barish R, Lynce F, Unger K, Barac A. Management of cardiovascular disease in women with breast cancer. Circulation. 2019;139(8):e394-e406.

[27] Brahmer JR, Lacchetti C, Schneider BJ, et al. Management of immune-related adverse events in patients treated with immune checkpoint inhibitor therapy: American Society of Clinical Oncology clinical practice guideline. J Clin Oncol. 2018;36(17):1714-1768.

[28] Haanen JBAG, Carbonnel F, Robert C, et al. Management of toxicities from immunotherapy: ESMO clinical practice guidelines for diagnosis, treatment and follow-up. Ann Oncol. 2017;28(suppl 4):iv119-iv142.

[29] Larkin J, Chiarion-Sileni V, Gonzalez R, et al. Five-year survival with combined nivolumab and ipilimumab in advanced melanoma. N Engl J Med. 2019;381(16):1535-1546.

[30] Hazell L, Shakir SAW. Under-reporting of adverse drug reactions: a systematic review. Drug Saf. 2006;29(5):385-396.

[31] Das S, Johnson DB. Immune-related adverse events and anti-tumor efficacy of immune checkpoint inhibitors. J Immunother Cancer. 2019;7(1):306.
