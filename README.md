# SexDiffKG Deep Analysis

**Sex-Differential Drug Safety Knowledge Graph — Publication-Ready Analysis Suite**

## Overview

Comprehensive clinical pharmacovigilance analyses derived from the SexDiffKG knowledge graph (v4), which integrates 14.5 million FAERS reports with molecular interaction networks, protein-protein interactions, and gene expression data.

### Contents

| Directory | Files | Description |
|-----------|-------|-------------|
| `analysis/` | 40 JSON + 20 TSV | Quantitative analysis results (signals, rankings, predictions) |
| `figures/` | 25 PNG + 21 PDF | Publication-quality figures (300 dpi) |
| `drafts/` | 2 papers | Full manuscript drafts (CPI irAE for JCO, Cardiac Reversal for CPT) |
| `vault_docs/` | 25 documents | Clinical analysis narratives and synthesis |
| `scripts/` | 83 Python scripts | Complete reproducible pipeline (FAERS → KG → analysis → figures) |
| `data_processed/` | 6 CSV + 6 Parquet | Drug classifications, AE mappings, molecular networks |

## Ten Major Findings

1. **Cardiac Reversal**: 67% of cardiac drug-AE signals are female-predominant — opposite to cardiovascular disease epidemiology
2. **Opioid Vulnerability**: 75% female across all opioid classes, mechanism-dependent severity patterns
3. **CPI irAEs**: 100% female-predominant across ALL checkpoint inhibitors (nivolumab, pembrolizumab, ipilimumab, atezolizumab)
4. **Anti-CD20 Paradox**: Same mechanism (rituximab), opposite sex bias by disease context
5. **Hepatotoxicity**: 2:1 female predominance, consistent across drug classes
6. **Psychotropic Receptor-Dependent Bias**: SSRIs female-biased, antipsychotics male-biased — receptor mechanism determines direction
7. **Death Signal**: 74% of death-associated drug-AE signals are female-predominant
8. **Temporal Reversal**: 42.3% of signals reversed sex-bias direction over 13 years of surveillance
9. **Pan-Therapeutic Female Vulnerability**: 8 of 11 ATC drug classes show female AE predominance
10. **KG Embedding Predictions**: ComplEx model (MRR 0.2484) predicts novel sex-differential signals validated by temporal holdout

## Data Source

- **FAERS**: 14,536,008 deduplicated reports (Female: 8,744,397 / Male: 5,791,611)
- **Temporal span**: 87 quarters (2004Q1–2025Q3)
- **SexDiffKG v4**: 109,867 nodes / 1,822,851 edges / 6 node types / 6 edge types
- **Signal detection**: 183,544 total signals, 49,026 strong (28,669 F / 20,357 M)
- **Drug normalization**: DiAna dictionary (846,917 mappings, 53.9% resolution)
- **Molecular sources**: STRING v12.0, ChEMBL 36, Reactome, GTEx v8

## Validation

- **40 literature benchmarks**: 72.5% coverage, 82.8% precision
- **Temporal holdout**: Signals from 2004-2019 predict 2020-2025 patterns
- **Cross-database**: Canada Vigilance concordance analysis
- **Geographic**: Multi-country FAERS reporter analysis

## Key Figures

| Figure | Description |
|--------|-------------|
| Fig 1 | Cardiac reversal: drug-AE sex bias vs. disease epidemiology |
| Fig 2 | Opioid mechanism-dependent sex-differential heatmap |
| Fig 3 | ATC therapeutic class forest plot |
| Fig 4 | Volcano plot: effect size vs. statistical significance |
| Fig 5 | Psychotropic receptor-mechanism analysis |
| Fig 6 | Temporal trend reversal patterns |
| Fig 7 | Network centrality and drug-target connectivity |
| Fig 8 | KG embedding norm distributions |
| Fig 9 | SOC-level sex bias summary |
| Fig 10 | Top drugs by sex-differential signal count |

## Manuscript Drafts

1. **CPI irAE Paper** (`drafts/CPI_irAE_paper.md`) — Targeted at *Journal of Clinical Oncology*
2. **Cardiac Reversal Paper** (`drafts/cardiac_reversal_paper.md`) — Targeted at *Clinical Pharmacology & Therapeutics*

## Models

| Model | MRR | Hits@10 | AMRI | Status |
|-------|-----|---------|------|--------|
| ComplEx v4 | **0.2484** | 40.69% | 0.9902 | Complete (best) |
| DistMult v4.1 | 0.1013 | 19.61% | 0.9909 | Complete |
| RotatE v4.1 | — | — | — | Training |

## Reproducibility

The `scripts/` directory contains the complete pipeline:
- `01-06`: Data acquisition, cleaning, normalization, KG construction
- `07-12`: Embedding training, evaluation, link prediction
- `13-16`: Clinical analysis, integrity checks, audits
- `v4_*`: Version 4 pipeline (canonical)
- `generate_*`: Figure and manuscript generation

## Citation

If you use this work, please cite:

> Shaik, M.J.A.A. (2026). SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph from 14.5 Million FAERS Reports. *bioRxiv* (preprint). DOI: pending

## Author

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**
CoEvolve Network, Independent Researcher, Barcelona, Spain
ORCID: [0009-0002-1748-7516](https://orcid.org/0009-0002-1748-7516)

## Related

- [SexDiffKG main repository](https://github.com/jshaik369/sexdiffkg) — Core KG data and pipeline
- Scientific Data manuscript (in preparation)
- ISMB 2026 abstract (submitted)

## License

This work is shared for academic and research purposes. Please contact the author for commercial use.
