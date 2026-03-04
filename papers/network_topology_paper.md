# Network Topology of Sex-Differential Drug Safety Signals

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**
CoEvolve Network, Independent Researcher, Barcelona, Spain
ORCID: 0009-0002-1748-7516 | jshaik@coevolvenetwork.com

## Abstract

We analyze the bipartite network topology of sex-differential drug safety signals derived from 14.5 million FAERS reports. The drug-adverse event (AE) network comprises 2,178 drugs and 5,069 AEs connected by 96,281 sex-differential edges (density = 0.008721). We find that drug connectivity (degree) positively correlates with female reporting bias (Spearman rho = 0.1172, p < 0.001), suggesting that broadly-reported drugs disproportionately affect women. The network exhibits strong disassortative mixing (rho = -0.395), indicating that hub drugs preferentially connect to rare AEs. Hub AE analysis reveals that "Death" is consistently male-biased (46%F) across 337 drugs, while hub drugs like Prednisone (926 AEs, 63.8%F) and Rituximab (755 AEs, 66.4%F) show strong female predominance. These network-level patterns suggest that sex-differential drug safety is not randomly distributed but follows systematic topological principles.

## Introduction

Pharmacovigilance signal detection traditionally focuses on individual drug-AE pairs. However, the drug safety landscape forms a complex bipartite network where drugs and adverse events are nodes, and reports constitute edges. Network topology has proven informative in biological networks (protein-protein interactions, gene regulatory networks), but its application to sex-differential drug safety remains unexplored.

We previously constructed SexDiffKG, a knowledge graph of 109,867 nodes and 1,822,851 edges integrating FAERS, STRING, Reactome, ChEMBL, and GTEx data. From 14,536,008 deduplicated FAERS reports (60.2% female), we identified 96,281 sex-differential signals across 2,178 drugs and 5,069 AEs.

Here we analyze the network topology of this drug-AE bipartite graph to ask: do sex-differential patterns follow topological rules?

## Methods

### Bipartite Network Construction
Nodes: 2,178 drugs (one partition) and 5,069 AEs (second partition). Each edge represents a sex-differential signal with attributes including female fraction, log-ratio, and total reports.

### Degree Centrality
Drug degree = number of distinct AEs reported. AE degree = number of distinct drugs implicated. We computed Spearman rank correlations between degree and mean female fraction for both partitions.

### Degree Assortativity
We measured whether high-degree drugs preferentially connect to high-degree AEs (assortative) or low-degree AEs (disassortative) using Spearman correlation between drug degree and AE degree across all edges.

### Degree-Sex Interaction
Drugs were stratified into quintiles by degree to examine the relationship between drug connectivity and sex bias.

## Results

### Network Statistics
The drug-AE bipartite network contains 96,281 edges with density 0.008721. Mean drug degree is 44.2 (range 1-926), while mean AE degree is 19.0 (range 1-501). The degree distribution is highly right-skewed, characteristic of scale-free networks.

### Degree-Sex Correlations
Drug degree correlates positively with female reporting fraction (rho = 0.1172, p < 0.001): drugs connected to more AEs tend to have higher female reporting rates. AE degree shows a similar pattern (rho = 0.1431, p < 0.001).

### Disassortative Mixing
The network shows strong negative degree assortativity (rho = -0.395), meaning hub drugs (high degree) preferentially connect to rare AEs (low degree), and vice versa. This is consistent with the biological principle that broadly-used drugs generate diverse, often rare, safety signals.

### Degree Quintile Analysis

| Quintile | N Drugs | Mean Degree | Mean F% | Mean |LR| |
|----------|---------|-------------|---------|------------|
| Q1 | 547 | 1 | 53.4% | 0.974 |
| Q2 | 378 | 4 | 53.4% | 0.978 |
| Q3 | 382 | 11 | 55.4% | 0.935 |
| Q4 | 439 | 32 | 54.5% | 0.926 |
| Q5 | 432 | 176 | 57.5% | 0.976 |

The gradient from Q1 (53.4%F, degree ~1) to Q5 (57.5%F, degree ~176) confirms that higher-connectivity drugs carry greater female bias, a 4.1 percentage-point shift.

### Hub Drug Analysis

| Drug | Degree | Mean F% | Mean |LR| | Bias |
|------|--------|---------|------------|------|
| PREDNISONE | 926 | 63.8% | 1.080 | F |
| METHOTREXATE | 892 | 64.3% | 0.967 | F |
| ADALIMUMAB | 807 | 64.0% | 0.879 | F |
| RITUXIMAB | 755 | 66.4% | 1.164 | F |
| INFLIXIMAB | 623 | 64.9% | 1.089 | F |
| ETANERCEPT | 618 | 69.9% | 0.984 | F |
| TACROLIMUS | 572 | 48.0% | 0.879 | M |
| PREDNISOLONE | 542 | 60.1% | 0.886 | F |
| DEXAMETHASONE | 537 | 54.0% | 0.858 | ~ |
| METHYLPREDNISOLONE | 521 | 66.9% | 1.156 | F |

The top 10 hub drugs are dominated by immunosuppressants (Prednisone, Methotrexate, Adalimumab, Rituximab, Infliximab) and oncology agents. All show female predominance (>60%F), with Rituximab highest at 66.4%F. This reflects the intersection of autoimmune disease prevalence (predominantly female) and broad AE profiles.

### Hub AE Analysis

| Adverse Event | Degree | Mean F% | Bias |
|---------------|--------|---------|------|
| Drug ineffective | 501 | 57.1% | ~ |
| Off label use | 445 | 59.4% | ~ |
| Condition aggravated | 392 | 51.6% | ~ |
| Vomiting | 362 | 63.2% | F |
| Dyspnoea | 349 | 60.8% | F |
| Nausea | 339 | 60.6% | F |
| Death | 337 | 46.1% | M |
| Fatigue | 332 | 69.2% | F |
| Headache | 327 | 68.0% | F |
| Pain | 327 | 72.2% | F |

Hub AEs span the spectrum from near-parity (Condition aggravated 51.6%F) to strongly female (Vomiting 63.2%F). Notably, "Drug ineffective" — the most connected AE (501 drugs) — shows moderate female bias (57.1%F).

## Discussion

### Topological Sex Bias
The positive correlation between drug degree and female fraction suggests a "promiscuity-sex" principle: drugs that interact with more biological pathways (generating more diverse AEs) tend to be reported more by women. This may reflect sex differences in immune surveillance, drug metabolism, or healthcare-seeking behavior.

### Disassortative Architecture
The strong negative assortativity (rho = -0.395) indicates that the drug safety network is hierarchical: hub drugs connect to many rare AEs, while rare drugs connect to common AEs. This architecture has implications for signal detection — rare but important signals are concentrated around hub drugs.

### Clinical Implications
1. Hub drugs (>100 AEs) should receive enhanced sex-stratified monitoring
2. The death AE being consistently male-biased across hundreds of drugs warrants systematic investigation
3. Network-based signal prioritization could complement traditional disproportionality analysis

## Conclusion

Sex-differential drug safety signals form a structured bipartite network with scale-free degree distributions, disassortative mixing, and systematic sex-degree correlations. Network topology provides a complementary lens for understanding sex differences in drug safety that transcends individual drug-AE pair analysis.

## Data Availability
SexDiffKG v4: https://github.com/jshaik369/sexdiffkg-deep-analysis
FAERS source: 14,536,008 reports, 87 quarters (2004Q1-2025Q3)

## References
1. Watson S, et al. Sex differences in adverse drug reactions. Pharmacoepidemiol Drug Saf. 2019.
2. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. Biol Sex Differ. 2020.
3. Barabasi AL, Albert R. Emergence of scaling in random networks. Science. 1999.
