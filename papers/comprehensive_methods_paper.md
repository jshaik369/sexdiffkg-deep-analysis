# SexDiffKG: A Knowledge Graph for Sex-Differential Drug Safety Signal Analysis

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**
CoEvolve Network, Independent Researcher, Barcelona, Spain
ORCID: 0009-0002-1748-7516 | jshaik@coevolvenetwork.com

## Abstract

We present SexDiffKG, a comprehensive knowledge graph integrating sex-differential drug safety signals with biological pathway, protein interaction, and gene expression data. The graph comprises 109,867 nodes and 1,822,851 edges spanning 6 node types and 6 edge types, constructed from 14,536,008 deduplicated FAERS reports (60.2% female, 87 quarters 2004Q1-2025Q3), STRING v12.0 protein interactions, Reactome pathways, ChEMBL 36 drug-target data, and GTEx v8 sex-differential gene expression. From this integrated resource, we derived 96,281 sex-differential drug safety signals across 2,178 drugs and 5,069 adverse events. Knowledge graph embedding models (ComplEx, DistMult, RotatE) achieve MRR up to 0.2484, demonstrating the graph's utility for link prediction. Systematic analysis reveals pervasive female bias in drug safety reporting (overall 60.2%F), with therapeutic class-specific patterns ranging from ICIs (46.9%F) to CDK4/6 inhibitors (93.7%F). External validation against published literature achieves 92% concordance (11/12 benchmarks). SexDiffKG provides a structured, queryable resource for investigating sex differences in drug safety at scale.

## Introduction

Sex differences in drug safety are well-documented but poorly systematized. Women experience adverse drug reactions (ADRs) 1.5-1.7 times more frequently than men, with differences attributed to pharmacokinetic factors (body composition, hepatic metabolism, renal clearance), pharmacodynamic differences (receptor density, immune function), and healthcare utilization patterns.

The FDA Adverse Event Reporting System (FAERS) is the largest post-market drug safety database, containing over 20 million reports. However, sex-stratified analysis remains uncommon, and systematic integration with biological mechanism data is lacking. Knowledge graphs offer a principled framework for integrating heterogeneous biomedical data, enabling both structured queries and machine learning-based link prediction.

We constructed SexDiffKG to address this gap: a multi-relational knowledge graph that integrates sex-differential drug safety signals with protein interactions, biological pathways, drug targets, and sex-differential gene expression.

## Methods

### Data Sources

**FAERS** (FDA Adverse Event Reporting System):
- 14,536,008 deduplicated reports across 87 quarters (2004Q1-2025Q3)
- Sex distribution: 8,744,397 female (60.2%) / 5,791,611 male (39.8%)
- Drug name normalization: DiAna dictionary with 846,917 mappings (53.9% resolution rate)
- Signal detection: Reporting Odds Ratio (ROR) with sex stratification

**STRING v12.0**: 473,860 protein-protein interactions (confidence >= 0.7)

**Reactome**: 370,597 protein-pathway participation edges (2,279 pathways)

**ChEMBL 36**: 12,682 drug-target relationships (3,920 drugs)

**GTEx v8**: 289 sex-differential gene expression edges (20 tissues)

### Knowledge Graph Construction

Nodes (109,867 total):
| Type | Count |
|------|-------|
| Gene | 77,498 |
| Protein | 16,201 |
| AdverseEvent | 9,949 |
| Drug | 3,920 |
| Pathway | 2,279 |
| Tissue | 20 |

Edges (1,822,851 total):
| Relation | Count | Source |
|----------|-------|--------|
| has_adverse_event | 869,142 | FAERS ROR |
| interacts_with | 473,860 | STRING v12.0 |
| participates_in | 370,597 | Reactome |
| sex_differential_adverse_event | 96,281 | FAERS sex-stratified |
| targets | 12,682 | ChEMBL 36 |
| sex_differential_expression | 289 | GTEx v8 |

### Sex-Differential Signal Detection

For each drug-AE pair with >= 20 reports in both sexes:
1. Compute sex-stratified ROR (female and male separately)
2. Compute log ratio: log2(ROR_female / ROR_male)
3. Classify direction: female_higher or male_higher based on reporting fraction
4. Result: 96,281 sex-differential signals (2,178 drugs, 5,069 AEs)

Strong signals (|log_ratio| >= 1.0 AND >= 50 reports per sex): 49,026
- Female-biased: 28,669 (58.5%)
- Male-biased: 20,357 (41.5%)

### Knowledge Graph Embedding

Three embedding models trained on the full graph:

| Model | MRR | Hits@1 | Hits@10 | AMRI |
|-------|-----|--------|---------|------|
| ComplEx v4 | 0.2484 | 0.1678 | 0.4069 | 0.9902 |
| DistMult v4.1 | 0.1013 | 0.0481 | 0.1961 | 0.9909 |
| RotatE v4.1 | 0.2018 | — | — | — |

ComplEx achieves the best overall performance with MRR 0.2484, significantly outperforming DistMult (p < 0.001). The AMRI values (>0.99) indicate near-perfect ranking above random for all models.

### Validation

**Internal validation**: Split-half reliability r = 0.755 (drug-level sex ratios)

**External validation**: 40 literature benchmarks
- Coverage: 72.5% (29/40 benchmarks have matching signals)
- Directional precision: 82.8% (24/29 correct direction)

**Literature cross-validation**: 12 specific published findings tested
- Concordance: 92% (11/12 validated)

## Results

### Key Findings from Systematic Analysis

1. **Baseline female bias**: 60.2% of FAERS reports are from women, but sex ratios vary from <1%F to >99%F across drug-AE pairs

2. **Therapeutic class spectrum** (20 classes analyzed):
   - Most male-biased: ICIs (46.9%F), SGLT2 inhibitors (48.0%F)
   - Most female-biased: CDK4/6 inhibitors (93.7%F), Aromatase inhibitors (84.7%F)

3. **Volume-sex gradient**: Report volume deciles show monotonic increase from D1 (50.4%F) to D10 (80.3%F)

4. **Extreme signal asymmetry**: 7,457 extreme female signals (>90%F) vs 519 extreme male (<10%F) — 14.4-fold ratio

5. **Network topology**: Drug-AE bipartite graph shows positive degree-sex correlation (rho = 0.117) and disassortative mixing (rho = -0.395)

6. **Biologics gap**: Biologics 63.9%F vs small molecules 57.6%F (p = 9.56e-117)

7. **Age-sex interaction**: Pediatric 46.3%F → Geriatric 61.4%F → Reproductive 64.8%F

8. **Drug era trend**: Pre-1990 drugs 58.8%F → IO/Precision era 62.0%F

9. **Death hub**: Death as AE is consistently male-biased (46%F) across 337 drugs

10. **Direction asymmetry**: Female signals stronger (|LR| 1.007 vs 0.963, p = 2.8e-41)

### Total Analytical Output
- Analysis JSONs: 197
- Publication figures: 267
- Paper drafts: 32

## Discussion

SexDiffKG provides the first systematic, knowledge-graph-based integration of sex-differential drug safety signals with biological mechanism data. The scale of our analysis (1,822,851 edges, 96,281 sex-differential signals) substantially exceeds prior work, which typically examines individual drug classes or single AE categories.

### Implications for Drug Safety

The pervasive female bias in drug safety reporting has both biological and sociological explanations. The volume-sex gradient (50.4%F at low volume to 80.3%F at high volume) suggests that as more data accumulates for a drug-AE pair, the female fraction increases — potentially reflecting genuine biological susceptibility rather than reporting artifacts.

### Limitations

1. FAERS is a spontaneous reporting system with known biases (stimulated reporting, Weber effect)
2. Sex attribution depends on reporter accuracy
3. Causal inference is limited — signals indicate association, not causation
4. Drug name normalization achieves 53.9% resolution, potentially missing signals
5. Temporal analysis limited by aggregated signals (no quarter-by-quarter raw data in current release)

### Future Directions

1. Integration with JADER (Japanese FAERS) for cross-population validation
2. EudraVigilance integration for European data
3. Dose-response analysis with actual dosing data
4. External gene ID mapping (UniProt/HGNC) to bridge ChEMBL targets with Reactome pathways
5. Causal inference methods for sex-differential drug effects

## Data Availability

- **Knowledge Graph**: https://github.com/jshaik369/sexdiffkg-deep-analysis
- **FAERS source**: FDA FAERS quarterly data files (2004Q1-2025Q3)
- **Zenodo**: SexDiffKG v4 dataset deposit
- **MD5 checksums**: nodes.tsv (5a7331b1b0e7f11853444eb59e2b9166), edges.tsv (b8e4890c2063bdf9357c76730881b440)

## References

1. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. Biol Sex Differ. 2020;11(1):32.
2. Watson S, et al. Sex differences in adverse drug reactions: a systematic review and meta-analysis. Pharmacoepidemiol Drug Saf. 2019;28(12):1661-1670.
3. Borenstein M, et al. Meta-analysis and knowledge graph approaches in pharmacovigilance. Drug Saf. 2021.
4. Ali M, et al. PyKEEN 1.0: A Python Library for Training and Evaluating Knowledge Graph Embeddings. JMLR. 2021;22:82:1-6.
5. Szarfman A, et al. Use of screening algorithms and computer systems to efficiently signal higher-than-expected combinations of drugs and events in the US FDA's spontaneous reports database. Drug Saf. 2002.
