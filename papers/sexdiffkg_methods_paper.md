# SexDiffKG: A Knowledge Graph Framework for Systematic Discovery of Sex-Differential Drug Safety Signals

Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
CoEvolve Network, Independent Researcher, Barcelona, Spain
jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

## Abstract

Despite decades of pharmacovigilance data, systematic sex-differential drug safety analysis
remains fragmented. We present SexDiffKG, a knowledge graph (KG) framework that integrates
sex-stratified adverse event signals from the FDA Adverse Event Reporting System (FAERS;
14.5 million deduplicated reports, 2004-2025) with multi-omic biological context from STRING,
ChEMBL, Reactome, and GTEx. The resulting KG contains 109,867 nodes and 1,822,851 edges
spanning 6 node types and 6 relation types. Sex-differential signal extraction yielded
96,281 signals across 2,178 drugs and 5,069 adverse events, with 49,026 strong signals
(|log ROR ratio| ≥ 0.5). KG embedding models (ComplEx: MRR 0.248, Hits@10 40.7%;
RotatE: MRR 0.202; DistMult: MRR 0.101) learned meaningful representations of the
sex-differential safety landscape. Systematic analysis revealed: (1) a universal
anti-regression phenomenon where sex bias intensifies with report volume (Spearman ρ = 1.000,
Bootstrap CI: 0.988-1.000); (2) substantial within-class heterogeneity (17/20 drug classes
show statistically significant intra-class sex variation; TKIs: 33.8pp spread); (3) an
information-theoretic entropy anti-regression (ρ = -0.952); (4) a seriousness-sex gradient
(serious AEs: 51.2%F vs non-serious: 58.3%F, p = 8.2 × 10⁻⁸³); and (5) sex bias modularity
in the drug-AE network. Cross-validation against SIDER, OpenFDA, and DailyMed confirmed
structural consistency. The framework generated 27 focused paper drafts, 190+ publication
figures, and 150+ analysis JSONs. SexDiffKG establishes that sex-differential drug safety
is not a marginal phenomenon but a pervasive, structured, and biologically grounded feature
of the pharmacovigilance landscape requiring systematic consideration in regulatory science.

## 1. Introduction

### 1.1 The Sex Gap in Drug Safety
Women experience approximately 1.5-1.7 times more adverse drug reactions than men, yet most
clinical trials historically included predominantly male participants. This asymmetry has been
documented in individual drug analyses but never systematically characterized across the
entire pharmacovigilance landscape.

### 1.2 Knowledge Graphs for Drug Safety
Knowledge graphs provide a natural representation for the multi-relational structure of drug
safety data, connecting drugs to adverse events, biological targets, pathways, and tissue-specific
gene expression. KG embedding models can learn latent representations that capture complex
patterns invisible to individual signal analysis.

### 1.3 Contribution
SexDiffKG is the first comprehensive KG framework specifically designed for sex-differential
drug safety analysis. Our contributions include:
- A curated KG integrating sex-stratified FAERS signals with multi-omic biological context
- Systematic extraction and characterization of 96,281 sex-differential signals
- Discovery of universal structural properties (anti-regression, seriousness gradient, modularity)
- KG embedding models that learn sex-differential patterns
- Cross-database validation (SIDER, OpenFDA, DailyMed)
- An open-source framework for reproducible sex-differential pharmacovigilance

## 2. Methods

### 2.1 Data Sources and Integration

**FAERS Processing**
- Source: FDA FAERS quarterly data files, 2004Q1 through 2025Q3 (87 quarters)
- Deduplication: Case-level deduplication by case ID, retaining latest version
- Final corpus: 14,536,008 reports (8,744,397 female [60.2%], 5,791,611 male [39.8%])
- Drug normalization: DiAna dictionary with 846,917 drug name mappings (53.9% resolution)

**Sex-Differential Signal Extraction**
- Reporting Odds Ratios (ROR) computed separately for female and male reporters
- Log ROR ratio = log(ROR_female / ROR_male) quantifies sex differential
- Minimum threshold: ≥5 reports per sex-drug-AE combination
- Result: 96,281 sex-differential signals (51,771 female-higher, 44,510 male-higher)
- Strong signals (|log ratio| ≥ 0.5): 49,026 (28,669 female, 20,357 male)

**Biological Context Integration**
| Source | Data Type | Contribution |
|--------|-----------|-------------|
| STRING v12.0 | Protein-protein interactions | 473,860 edges |
| ChEMBL 36 | Drug-target interactions | 12,682 edges |
| Reactome | Pathway participation | 370,597 edges |
| GTEx v8 | Sex-differential expression | 289 edges |

### 2.2 Knowledge Graph Construction

**Node Types (6 types, 109,867 total)**
- Gene: 77,498 (from STRING, Reactome)
- Protein: 16,201 (from STRING)
- Adverse Event: 9,949 (from FAERS)
- Drug: 3,920 (from FAERS, ChEMBL)
- Pathway: 2,279 (from Reactome)
- Tissue: 20 (from GTEx)

**Edge Types (6 types, 1,822,851 total)**
- has_adverse_event: 869,142 (FAERS aggregate)
- interacts_with: 473,860 (STRING)
- participates_in: 370,597 (Reactome)
- sex_differential_adverse_event: 96,281 (FAERS sex-stratified)
- targets: 12,682 (ChEMBL)
- sex_differential_expression: 289 (GTEx)

### 2.3 KG Embedding Training

Models trained using PyKEEN 1.11.1 on the full KG (1,822,851 triples):

| Model | Embedding Dim | MRR | Hits@1 | Hits@10 | AMRI |
|-------|--------------|-----|--------|---------|------|
| ComplEx v4 | 256 (complex) | 0.2484 | 0.1678 | 0.4069 | 0.9902 |
| RotatE v4.1 | 512 (complex) | 0.2018 | — | — | — |
| DistMult v4.1 | 256 | 0.1013 | 0.0481 | 0.1961 | 0.9909 |

Training on CPU (DGX Grace 20 cores) due to NVRTC SM 12.1 incompatibility with
complex tensor CUDA kernels on Blackwell GB10 GPU.

### 2.4 Validation
- 40 literature benchmarks: 72.5% coverage, 82.8% directional precision
- SIDER cross-validation: structural consistency of drug-AE associations
- OpenFDA label concordance: sex-specific warnings align with signal direction
- DailyMed confirmation: label-reported sex differences match signal predictions

## 3. Results

### 3.1 The Anti-Regression Phenomenon
The most unexpected finding: sex bias INTENSIFIES rather than regresses to the mean
with increasing report volume.
- Drug report volume deciles: D0 (lowest) = 50.4%F → D9 (highest) = 80.3%F
- Spearman ρ = 1.000 (perfect monotone), Bootstrap CI: 0.988-1.000
- Robust across ALL sensitivity thresholds (min reports 5-500)
- Information-theoretic expression: entropy decreases with volume (ρ = -0.952)
- Persists after baseline normalization (normalized ρ = 0.809)

### 3.2 Within-Class Heterogeneity
Same pharmacological class, different sex safety profiles:
- 17/20 classes show statistically significant heterogeneity (KW p < 0.05)
- Largest spread: TKIs (33.8pp), Opioids (29.6pp), NSAIDs (29.4pp)
- Smallest spread: CDK4/6i (2.7pp), SGLT2i (3.7pp), DOACs (4.3pp)
- Drug class membership explains only part of sex-differential variation

### 3.3 Therapeutic Area Landscape
- Autoimmune: 66.6%F (JAK inhibitors 71.0%F)
- CNS: 57.2%F (antidepressants 61.3%F, Parkinson's 50.6%F)
- Oncology: 53.5%F (immuno-oncology 46.8%F)
- Metabolic: 54.6%F (obesity drugs 70.1%F, lipids 51.6%F)
- Kruskal-Wallis H = 2240, p ≈ 0

### 3.4 Seriousness-Sex Gradient
- Serious AEs: 51.2%F (approaches parity)
- Non-serious AEs: 58.3%F (maintains female predominance)
- Mann-Whitney p = 8.2 × 10⁻⁸³
- Organ system gradient: cardiac (53.1%F) to dermatologic (63.9%F)

### 3.5 Sex Bias Modularity
Female-biased drugs preferentially cause female-biased AEs:
- F-biased drugs × F-biased AEs: 24.4% of signals
- M-biased drugs × M-biased AEs: 4.1% of signals
- Modularity confirms structured rather than random sex-differential patterns

### 3.6 Rare Disease Paradox
Orphan drugs show near-parity (49.2%F) compared to common drugs (74.5%F),
a 25.3pp gap (p = 4.4 × 10⁻⁸²), attributable to disease biology and
smaller, more controlled study populations.

### 3.7 Normalization Analysis
After adjusting for the 60.2% female FAERS baseline:
- 55.1% of signals fall BELOW baseline (majority are not truly female-biased)
- 240 drugs are truly male-biased vs 93 truly female-biased
- Anti-regression persists after normalization (ρ = 0.809)

## 4. Discussion

### 4.1 Implications for Regulatory Science
The universal anti-regression and seriousness-sex gradient demonstrate that sex-differential
drug safety is not simply a function of reporting bias but reflects structured biological
and pharmacological differences. Current sex-blind signal detection thresholds may miss
important sex-specific risks.

### 4.2 Implications for Clinical Practice
The substantial within-class heterogeneity (17/20 classes) means that class-level sex
safety assumptions are insufficient. Individual drug monitoring with sex-specific
baselines is warranted.

### 4.3 Limitations
- FAERS is a spontaneous reporting system with known biases
- Baseline female predominance (60.2%) requires careful interpretation
- Seriousness and organ system classifications used keyword proxies
- KG embeddings capture statistical associations, not causal relationships

## 5. Conclusion

SexDiffKG reveals that sex-differential drug safety is a pervasive, structured, and
biologically grounded phenomenon spanning the entire pharmacovigilance landscape.
The anti-regression phenomenon, seriousness-sex gradient, within-class heterogeneity,
and therapeutic area differences establish a comprehensive foundation for sex-specific
pharmacovigilance. We release the complete KG, embeddings, analysis pipeline, and
all results as open resources for the community.

## Data Availability
- KG and embeddings: Zenodo DOI [to be assigned]
- Analysis code and results: https://github.com/jshaik369/sexdiffkg-deep-analysis
- bioRxiv preprint: [to be submitted]

## Keywords
knowledge graph, pharmacovigilance, sex differences, drug safety, FAERS, adverse events,
graph embeddings, anti-regression
