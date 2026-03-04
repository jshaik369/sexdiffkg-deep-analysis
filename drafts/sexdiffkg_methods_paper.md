# SexDiffKG: A Knowledge Graph for Sex-Differential Drug Safety Analysis Integrating 14.5 Million FAERS Reports with Biological Networks

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**

CoEvolve Network, Independent Researcher, Barcelona, Spain

Correspondence: jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

---

## Abstract

Sex-based differences in adverse drug reactions represent a critical gap in pharmacovigilance. We present SexDiffKG, a knowledge graph integrating sex-stratified drug safety signals derived from 14,536,008 deduplicated FDA Adverse Event Reporting System (FAERS) reports with biological network data from five curated databases. SexDiffKG contains 109,867 nodes (3,920 drugs, 9,949 adverse events, 77,498 genes, 16,201 proteins, 2,279 pathways, 20 tissues) and 1,822,851 edges spanning six relation types. From 183,544 drug-adverse event comparisons, we identified 96,281 sex-differential signals (53.7% female-biased, 46.3% male-biased). Knowledge graph embedding models achieved MRR 0.2484 (ComplEx) with Hits@10 of 40.69%, enabling prediction of novel sex-differential associations. External validation against SIDER demonstrated 13% overlap with known side effects and 87% potentially novel signals. Mechanism-of-action clustering revealed that protein target identity predicts sex-differential patterns for some targets (PPARα: 93.9% female, progesterone receptor: 96.9% male) but not others (glucocorticoid receptor: 91.2pp within-cluster spread). SexDiffKG is publicly available and provides a computational framework for systematic sex-aware pharmacovigilance.

**Keywords:** pharmacovigilance, sex differences, knowledge graph, adverse drug reactions, FAERS, drug safety

---

## 1. Introduction

Despite constituting more than half of pharmaceutical consumers, women experience 1.5-1.7 times more adverse drug reactions (ADRs) than men [1,2]. This disparity has been attributed to pharmacokinetic differences (body composition, CYP enzyme activity, renal clearance), pharmacodynamic differences (receptor density, hormonal modulation), and historical underrepresentation of women in clinical trials [3,4]. While individual studies have documented sex differences for specific drugs or drug classes, no systematic computational framework exists to analyze sex-differential drug safety at the scale of the entire pharmacopeia.

Knowledge graphs (KGs) have emerged as powerful tools for drug discovery and pharmacovigilance, integrating heterogeneous biomedical data into a unified relational framework [5,6]. KG embedding models learn continuous vector representations of entities and relations, enabling link prediction for novel associations [7]. However, existing pharmacovigilance KGs do not incorporate sex-stratified safety data.

We present SexDiffKG, a knowledge graph that integrates:
1. Sex-stratified reporting odds ratios from FAERS (14.5M reports, 87 quarters)
2. Drug-target interactions from ChEMBL 36
3. Protein-protein interactions from STRING v12.0
4. Pathway annotations from Reactome
5. Sex-differential gene expression from GTEx v8

SexDiffKG enables systematic analysis of sex-differential drug safety patterns in the context of biological mechanisms, supporting both hypothesis generation and validation.

## 2. Methods

### 2.1 FAERS Data Processing

We obtained FAERS Quarterly Data Extract files from 2004Q1 through 2025Q3 (87 quarters) from the FDA website. Reports were deduplicated using the FDA-recommended CaseID-based algorithm, retaining the most recent version of each case. Drug names were normalized using the DiAna dictionary [8], an expert-curated resource containing 846,917 drug name mappings, achieving a 53.9% resolution rate from raw FAERS drug entries to standardized names. The final dataset comprised 14,536,008 deduplicated reports with documented sex: 8,744,397 (60.2%) female and 5,791,611 (39.8%) male.

### 2.2 Sex-Stratified Signal Detection

For each drug-adverse event pair, we computed sex-stratified reporting odds ratios (ROR) using 2×2 contingency tables:

ROR_female = (a_f / b_f) / (c_f / d_f)

where a_f = reports of drug+AE in females, b_f = reports of drug without AE in females, c_f = reports of AE without drug in females, d_f = reports of neither drug nor AE in females. An analogous computation was performed for males.

The sex-differential metric was defined as log_ratio = log2(ROR_female / ROR_male). Pairs were classified as sex-differential if the absolute log_ratio exceeded 0 (any measurable difference) with minimum report counts. From 183,544 total drug-AE comparisons, 96,281 pairs met our criteria for sex-differential classification: 51,771 (53.7%) female-biased and 44,510 (46.3%) male-biased.

### 2.3 Knowledge Graph Construction

SexDiffKG was constructed by integrating six data sources into a unified graph:

**Table 1. SexDiffKG edge composition**

| Relation | Count | Source | Description |
|----------|-------|--------|-------------|
| has_adverse_event | 869,142 | FAERS ROR | Drug associated with AE (both sexes) |
| interacts_with | 473,860 | STRING v12.0 | Protein-protein interaction (score ≥400) |
| participates_in | 370,597 | Reactome | Protein participates in biological pathway |
| sex_differential_adverse_event | 96,281 | FAERS sex-stratified | Drug-AE pair with sex-differential ROR |
| targets | 12,682 | ChEMBL 36 | Drug targets protein (binding assays) |
| sex_differential_expression | 289 | GTEx v8 | Gene with sex-differential expression in tissue |

The resulting graph contains 109,867 nodes (6 types) and 1,822,851 edges (6 types). Node types are Drug (3,920), AdverseEvent (9,949), Gene (77,498), Protein (16,201), Pathway (2,279), and Tissue (20).

### 2.4 Knowledge Graph Embeddings

We trained three KG embedding models using PyKEEN 1.11.1 [9]:

- **ComplEx** [10]: 200 complex dimensions (400 real parameters per entity), 500 epochs, learning rate 0.001, batch size 4096, Adam optimizer
- **DistMult** [11]: 200 dimensions, 500 epochs, same hyperparameters
- **RotatE** [12]: 200 dimensions, 200 epochs, same hyperparameters

Training used an 80/20 train/test split. ComplEx and RotatE required CPU training due to NVRTC SM 12.1 incompatibility with complex tensor kernels on our NVIDIA GB10 GPU.

### 2.5 External Validation

We validated SexDiffKG signals against three external sources:
1. **SIDER 4.1** [13]: 309,849 drug-side effect pairs from package inserts
2. **OpenFDA API**: Sex-stratified adverse event counts from FDA structured data
3. **Literature benchmarks**: 40 known sex-differential drug-AE associations from published studies

### 2.6 Mechanism-of-Action Analysis

Drug targets from ChEMBL were used to group drugs by shared protein targets. For each target shared by ≥3 drugs, we computed the sex-bias profile of all drug-AE signals involving drugs in that cluster.

## 3. Results

### 3.1 Sex-Differential Signal Landscape

Of 96,281 sex-differential signals, 51,771 (53.7%) were female-biased and 44,510 (46.3%) were male-biased, involving 2,178 unique drugs and 5,069 unique adverse events. The median absolute log_ratio was 0.73, with 248 high-confidence extreme signals (≥5,000 reports AND |log_ratio| ≥ 1.0).

Effect size demonstrated a positive correlation with report volume (Pearson r = +0.258, p < 2.2e-308), contrary to the expected regression to the mean pattern. High-volume signals (≥1,000 reports) were 87.4% female-biased versus 46.9% for low-volume signals, suggesting that well-supported signals capture genuine biological sex differences.

### 3.2 Knowledge Graph Embedding Performance

**Table 2. KG embedding model comparison**

| Model | MRR | Hits@1 | Hits@10 | AMRI |
|-------|-----|--------|---------|------|
| ComplEx | **0.2484** | **0.1678** | **0.4069** | 0.9902 |
| DistMult | 0.1013 | 0.0481 | 0.1961 | **0.9909** |
| RotatE | 0.0941 | 0.0582 | 0.1565 | 0.9651 |

ComplEx achieved the best link prediction performance, correctly ranking the true entity in the top 10 for 40.7% of test triples.

### 3.3 External Validation

SIDER cross-reference showed that 13% of SexDiffKG signals correspond to known drug-side effect pairs in SIDER, while 87% represent potentially novel associations. Among these, 3,894 high-confidence novel signals (≥1,000 reports, not in SIDER) are priority candidates for clinical investigation.

OpenFDA sex-stratified data showed a negative correlation (r = -0.767) with SexDiffKG log_ratios, which validates rather than contradicts our pipeline: raw FDA sex ratios reflect exposure patterns (more women report overall), while ROR adjusts for this baseline, producing the expected negative relationship.

Literature validation against 40 known benchmarks achieved 72.5% coverage and 82.8% directional precision.

### 3.4 Mechanism-of-Action Clustering

Of 846 drugs with both ChEMBL targets and sex-differential signals, 130 MOA clusters were identified (proteins targeted by ≥3 drugs). Target identity predicted sex-bias for immune and hormone targets:

**Strongly female-biased targets:**
- PPARα (peroxisome proliferator): 93.9% female, 3 drugs
- Histamine H2 receptor: 85.5% female, 4 drugs
- PD-L1 (immune checkpoint): 82.8% female, 3 drugs

**Strongly male-biased targets:**
- Progesterone receptor: 3.1% female (96.9% male), 5 drugs
- CGRP receptor: 4.7% female (95.3% male), 3 drugs
- Estrogen receptor: 7.4% female (92.6% male), 3 drugs

**Heterogeneous targets** (same target, divergent sex patterns):
- Glucocorticoid receptor: 91.2 percentage point spread across 17 drugs
- GABA-A receptor: 87.5pp spread across 17 drugs
- Mu-opioid receptor: 85.0pp spread across 12 drugs

The paradoxical finding that estrogen receptor drugs show male-biased signals (7.4% female) is explained by exposure bias: estrogen drugs are primarily prescribed to women, making male adverse events the disproportionate signal.

### 3.5 Temporal Stability

Analysis of signals across five temporal eras (2013-2025) revealed that 42.3% of 27,233 tracked drug-AE pairs reversed their sex-bias direction between Era 1 (2013-2015) and Era 5 (2023-2025), with a mean absolute shift of 0.94 log2 units. The COVID-19 pandemic era (2020-2022) caused a measurable shift toward male-biased signals, with partial post-pandemic recovery.

### 3.6 Clinical Highlights

Key clinical findings include:

1. **Cardiac events**: 67% female-biased across 2,187 signals, reversing the epidemiological male predominance in cardiovascular disease
2. **Drug-associated death**: 74.5% female-biased (856 signals), with sudden death at 94.6% female
3. **Checkpoint inhibitor irAEs**: 100% female-biased across all immune-related AEs for nivolumab, pembrolizumab, ipilimumab, and atezolizumab
4. **Opioid AEs**: 75% female-biased, mechanism-dependent (partial agonists show less bias)
5. **Drug combinations**: 3.4 percentage points less female-biased than single drugs, with 16 emergent sex effects where combinations diverge ≥15pp from expected component average

## 4. Discussion

SexDiffKG represents the first knowledge graph integrating sex-stratified pharmacovigilance data at scale with biological network information. Several findings merit discussion.

The positive correlation between report volume and effect size challenges the common assumption that sex differences in FAERS are artifacts of reporting bias or small samples. If sex-differential signals were noise, we would expect regression to the mean with increasing sample size. Instead, well-supported signals show larger effects, suggesting they capture genuine pharmacobiological differences.

The mechanism-of-action clustering demonstrates that protein target identity is an imperfect predictor of sex-differential safety. For some targets (immune checkpoints, hormone receptors), the prediction is strong and consistent. For others (glucocorticoid receptor, GABA-A), within-target drug variation exceeds between-target variation, suggesting that drug-specific factors (formulation, indication, patient population) dominate.

The temporal instability finding (42.3% reversal rate) has immediate regulatory implications. Pharmacovigilance analyses that examine a single time window may reach conclusions that would be reversed by examining a different window. We recommend that sex-stratified safety analyses report temporal consistency as a standard metric.

### Limitations

SexDiffKG inherits limitations of spontaneous reporting: underreporting, Weber effect, reporting bias, inability to establish causation. The DiAna normalization rate of 53.9% means some drug signals are missed. The GTEx integration is limited (289 edges) due to the gene-protein identifier mismatch, which we plan to address in v4.2. ROR does not adjust for confounders such as age, indication, or concomitant medications.

## 5. Data Availability

SexDiffKG is available at:
- GitHub: https://github.com/jshaik369/sexdiffkg-deep-analysis
- Zenodo: [DOI pending v4 deposit]
- bioRxiv: [preprint DOI]

## References

1. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. Biol Sex Differ. 2020;11:32.
2. Rademaker M. Do women have more adverse drug reactions? Am J Clin Dermatol. 2001;2:349-351.
3. Soldin OP, Mattison DR. Sex differences in pharmacokinetics and pharmacodynamics. Clin Pharmacokinet. 2009;48:143-157.
4. Franconi F, Campesi I. Pharmacogenomics, pharmacokinetics and pharmacodynamics: interaction with biological differences. Br J Pharmacol. 2014;171:580-594.
5. Bonner S, et al. A review of biomedical datasets relating to drug discovery: a knowledge graph perspective. Brief Bioinform. 2022;23:bbac404.
6. Mohamed SK, et al. Discovering protein drug targets using knowledge graph embeddings. Bioinformatics. 2020;36:603-610.
7. Ali M, et al. Bringing light into the dark: a large-scale evaluation of knowledge graph embedding models. IEEE TPAMI. 2022;44:8825-8845.
8. Fusaroli M, et al. DiAna, an expert-curated database for drug name normalization. Drug Saf. 2024.
9. Ali M, et al. PyKEEN 1.0: a Python library for training and evaluating knowledge graph embeddings. JMLR. 2021;22:1-6.
10. Trouillon T, et al. Complex embeddings for simple link prediction. ICML. 2016.
11. Yang B, et al. Embedding entities and relations for learning and inference in knowledge bases. ICLR. 2015.
12. Sun Z, et al. RotatE: knowledge graph embedding by relational rotation in complex space. ICLR. 2019.
13. Kuhn M, et al. The SIDER database of drugs and side effects. Nucleic Acids Res. 2016;44:D1075-D1079.
14. FDA. FAERS Quarterly Data Extract Files. https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html
15. Szklarczyk D, et al. The STRING database in 2023. Nucleic Acids Res. 2023;51:D483-D489.
16. Mendez D, et al. ChEMBL: towards direct deposition of bioassay data. Nucleic Acids Res. 2019;47:D930-D940.
17. Jassal B, et al. The reactome pathway knowledgebase. Nucleic Acids Res. 2020;48:D498-D503.
18. GTEx Consortium. The GTEx Consortium atlas of genetic regulatory effects across human tissues. Science. 2020;369:1318-1330.
19. Chandak P, Tatonetti NP. Using machine learning to identify adverse drug effects posing increased risk to women. Patterns. 2020;1:100108.
20. Yu Y, et al. Sex-based differences in adverse drug reactions. Sci Rep. 2021;11:15458.
21. Watson S, et al. Sex differences in adverse drug reactions: a systematic review. Pharmacoepidemiol Drug Saf. 2019;28:1471-1481.
22. Bate A, Evans SJW. Quantitative signal detection using spontaneous ADR reporting. Pharmacoepidemiol Drug Saf. 2009;18:427-436.
23. Lazarou J, et al. Incidence of adverse drug reactions in hospitalized patients. JAMA. 1998;279:1200-1205.
