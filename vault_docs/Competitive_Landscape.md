# Competitive Landscape: Biomedical Knowledge Graphs
**Updated:** 2026-03-04 03:00 CET (CW8)
**Purpose:** Position SexDiffKG in manuscript (Scientific Data, Nature)

## Comparison Table

| Knowledge Graph | Nodes | Edges | Node Types | Edge Types | Sex Analysis | FAERS | Year |
|---|---|---|---|---|---|---|---|
| **SexDiffKG** | **109,867** | **1,822,851** | 6 | 6 | **YES (96,281 edges)** | **YES (14.5M)** | 2026 |
| SPOKE | 27,056,367 | 53,264,489 | 21 | 55 | No | No | 2023 |
| PharMeBINet | 2,869,407 | 15,883,653 | 66 | 208 | No | No (SIDER) | 2022 |
| DRKG | 97,238 | 5,874,261 | 13 | 107 | No | No (SIDER) | 2020 |
| OpenBioLink | 180,992 | 4,563,407 | 7 | 28 | No | No | 2020 |
| PrimeKG | 129,375 | 4,050,249 | 10 | 30 | No | No (SIDER) | 2023 |
| Hetionet | 47,031 | 2,250,197 | 11 | 24 | No | No (SIDER) | 2017 |
| PharmKG | ~7,600 | 500,958 | 3 | 29 | No | No | 2021 |

## Key Differentiators

**No existing biomedical KG encodes sex-differential drug safety information.** This is the central novelty.

1. **Sex on every safety edge**: 96,281 sex-differential AE edges with directionality
2. **Direct FAERS integration**: 14.5M reports, 87 quarters (2004Q1-2025Q3), not via SIDER
3. **Pharmacovigilance signals with directionality**: 183,544 total, 49,026 strong (28,669 F / 20,357 M)
4. **Multi-scale biology + safety**: STRING PPI + Reactome pathways + ChEMBL targets + GTEx expression + FAERS

## Competitor Details

### Hetionet (Himmelstein et al., eLife 2017)
- Pioneering integrative network; 29 sources, 11 node types
- Side effects from SIDER (aggregate, not sex-stratified, not FAERS)
- doi:10.7554/eLife.26726

### DRKG (AWS, 2020)
- Built for COVID-19 repurposing; subsumes Hetionet
- No formal publication; GitHub only
- github.com/gnn4dr/DRKG

### PrimeKG (Chandak, Huang & Zitnik, Scientific Data 2023)
- Most comparable: 20 high-quality resources, published in same target journal
- Drug side effects from SIDER (not FAERS), no sex stratification
- doi:10.1038/s41597-023-01960-3

### PharMeBINet (Konigs et al., Scientific Data 2022)
- Extension of Hetionet (66 node types, 208 edge types)
- ADR info inherited from SIDER, no sex stratification
- doi:10.1038/s41597-022-01510-3

### SPOKE (Morris et al., Bioinformatics 2023)
- Largest curated KG (27M nodes, 53M edges, 41 databases)
- UCSF precision medicine platform, no sex/gender dimension
- doi:10.1093/bioinformatics/btad080

## Papers on Sex-Differential Pharmacovigilance (for Introduction)

### Foundational
1. **Zucker & Prendergast (2020)** - 86 FDA drugs; 88% show greater female exposure; 96% concordance with female ADRs. Biol Sex Differ 11:32
2. **Soldin & Mattison (2009)** - Seminal review on sex PK/PD differences. Clin Pharmacokinet 48(3):143-157
3. **Mazure & Fiellin (2018)** - Women experience ADRs ~1.5-1.7x more than men

### Computational
4. **Yu et al. (2016)** - First large-scale FAERS sex analysis: 307/668 drugs showed sex differences. Sci Rep 6:24955
5. **Chandak & Tatonetti (2020)** - AwareDX: ML on FAERS, 20,817 sex-specific ADEs. Patterns 1(7):100108
6. **Rushovich et al. (2023)** - After adjusting for drug use rates, sex disparity drops. JAMA Network Open

### KGs in Pharmacovigilance
7. **Scoping Review (2024)** - KGs used for ADR/DDI prediction; none integrate sex-differential analysis. Clinical Therapeutics
8. **Bean et al. (2017)** - KG with drugs/targets/ADRs, AUC 0.92, no sex stratification. Sci Rep

## Positioning Statement (for manuscript)

SexDiffKG occupies a unique niche at the intersection of three dimensions no existing KG addresses simultaneously:
1. Multi-scale molecular biology (PPI, pathways, targets, expression) — shared with PrimeKG, DRKG
2. Real-world pharmacovigilance at scale (14.5M FAERS reports) — not in any competitor
3. Sex-differential encoding (96,281 edges with directionality) — entirely novel

SexDiffKG is the first KG to embed sex-differential pharmacovigilance signals as first-class graph elements alongside molecular biology, enabling link prediction and mechanistic reasoning about sex-specific drug safety.
