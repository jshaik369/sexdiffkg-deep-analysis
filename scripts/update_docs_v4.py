#!/usr/bin/env python3
"""Update all publication documents with v4 ground truth numbers."""
import os

BASE = "/home/jshaik369/sexdiffkg"
PUB = f"{BASE}/Publication"

# ============================================================
# ISMB 2026 Abstract
# ============================================================
ismb = """SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph from 14.5 Million FDA Adverse Event Reports

Women experience adverse drug reactions (ADRs) at 1.5-1.7x the rate of men, yet most pharmacovigilance databases lack systematic sex-differential analysis. Existing biomedical knowledge graphs (Hetionet, DRKG, PharmKG) treat safety data in aggregate, leaving a critical gap in computational tools for sex-aware drug safety assessment.

We present SexDiffKG, the first knowledge graph specifically designed to capture sex-differential pharmacovigilance signals at scale. SexDiffKG integrates 14,536,008 FDA Adverse Event Reporting System (FAERS) reports spanning 2004-2025 with molecular target data from ChEMBL 36, protein interactions from STRING v12.0, pathway annotations from Reactome, and sex-differential gene expression from GTEx v8. Drug names are normalized using a 4-tier pipeline anchored by the DiAna dictionary (846,917 FAERS mappings), achieving 53.9% active-ingredient resolution. The resulting graph contains 109,867 nodes (6 entity types) and 1,822,851 edges (6 relation types).

Through sex-stratified Reporting Odds Ratio (ROR) analysis with minimum 10 reports per sex and |log(ROR_F/ROR_M)| >= 0.5 threshold, we identified 96,281 sex-differential drug-adverse event signals, with 53.8% showing female bias. DistMult knowledge graph embeddings (200 dimensions, 100 epochs) achieved MRR of 0.093 and AMRI of 0.9906, ranking correct triples in the top 0.94% of candidates. Signal validation against 40 literature benchmarks achieved 72.5% coverage and 82.8% directional precision, a 19.5 percentage-point improvement over our initial pipeline through DiAna-based drug normalization.

SexDiffKG provides a computational foundation for precision pharmacovigilance, with all data and code publicly available via GitHub and Zenodo.
"""

# ============================================================
# ASHG 2026 Abstract
# ============================================================
ashg = """SexDiffKG: A Knowledge Graph Revealing Sex-Differential Drug Safety Profiles from 14.5 Million FDA Reports

Sex-based differences in drug safety affect millions of patients, yet the genetic basis remains poorly characterized. We constructed SexDiffKG, integrating 14,536,008 FDA FAERS reports (2004-2025) with drug-gene target data from ChEMBL 36, protein interactions from STRING v12.0, and pathway annotations from Reactome into a knowledge graph of 109,867 nodes and 1,822,851 edges.

Drug names were normalized using the DiAna dictionary (846,917 FAERS mappings) in a 4-tier pipeline achieving 53.9% active-ingredient resolution. Through sex-stratified Reporting Odds Ratio analysis (|log(ROR_F/ROR_M)| >= 0.5, minimum 10 reports per sex), we identified 96,281 sex-differential signals (53.8% female-biased). Bridging FAERS drugs to ChEMBL targets revealed gene targets with sex-biased safety profiles: HDAC1/2/3/6 show exclusively female-biased safety, suggesting sex-differential epigenetic regulation affects drug response. ESR1 shows paradoxical male-biased safety. Coagulation factors F8/F9 are exclusively female-biased. Nicotinic AChR subunits are female-biased while epithelial Na channels SCNN1A/B/G are exclusively male-biased. JAK1 shows male-biased safety, consistent with sex differences in JAK-STAT signaling.

DistMult KG embeddings (200d, AMRI 0.9906) confirm meaningful pharmacogenomic structure. Signal validation against 40 benchmarks achieves 82.8% directional precision. These targets provide hypotheses for sex-aware pharmacogenomic research. Data: doi.org/10.5281/zenodo.18819192. Code: github.com/jshaik369/SexDiffKG.
"""

# ============================================================
# NeurIPS 2026 Abstract
# ============================================================
neurips = """SexDiffKG: Knowledge Graph Embeddings for Sex-Differential Drug Safety from 14.5 Million Pharmacovigilance Reports

We present SexDiffKG, a heterogeneous knowledge graph integrating 14.5 million FDA adverse event reports with molecular target, protein interaction, pathway, and sex-differential gene expression data from five biomedical databases. Drug names are normalized via a 4-tier pipeline anchored by the DiAna dictionary (53.9% active-ingredient resolution). The graph contains 109,867 nodes (6 types) and 1,822,851 edges (6 relations), including 96,281 sex-differential drug-adverse event signals identified through sex-stratified Reporting Odds Ratio analysis.

We train DistMult embeddings (200 dimensions, 100 epochs) achieving MRR of 0.093 and Adjusted Mean Rank Index (AMRI) of 0.9906, placing correct triples in the top 0.94% of candidates across 109,867 entities. DiAna-based drug normalization eliminates duplicate drug variants, yielding a 95.6% MRR improvement over our initial unnormalized pipeline.

Embedding-based drug clustering reveals distinct sex-differential safety profiles, and target-level analysis identifies gene targets with sex-biased patterns. Novel findings include exclusively female-biased HDAC inhibitor safety profiles and counterintuitive male-biased estrogen receptor drug safety. Signal validation against 40 literature benchmarks achieves 72.5% coverage and 82.8% directional precision. SexDiffKG is the first KG designed for sex-differential pharmacovigilance at scale, demonstrating that domain-specific drug normalization is critical for pharmacovigilance KG quality.
"""

# ============================================================
# README.md
# ============================================================
readme = """# SexDiffKG

**A Sex-Differential Knowledge Graph for Drug Safety from 14.5 Million FDA Adverse Event Reports**

[![bioRxiv](https://img.shields.io/badge/bioRxiv-2026.709170-b31b1b.svg)](https://doi.org/10.1101/2026.709170)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data: CC-BY 4.0](https://img.shields.io/badge/Data-CC--BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](Dockerfile)

---

## Overview

SexDiffKG is the first knowledge graph where **biological sex is encoded on every drug-safety edge**. It integrates 14.5 million FDA FAERS adverse event reports with molecular interaction networks to reveal sex-differential drug safety patterns at scale.

**Key finding:** 96,281 drug-adverse event pairs show sex-differential signals, with 53.8% biased toward women. Signal validation against 40 literature benchmarks achieves 82.8% directional precision.

## Key Statistics

| Metric | Value |
|--------|-------|
| FAERS reports (deduplicated, M/F) | 14,536,008 |
| Female reports | 8,744,397 (60.2%) |
| Male reports | 5,791,611 (39.8%) |
| FAERS quarters | 87 (2004 Q1 - 2025 Q3) |
| Knowledge graph nodes | 109,867 (6 types) |
| Knowledge graph edges | 1,822,851 (6 relations) |
| Sex-differential signals | 96,281 |
| Female-biased signals | 51,771 (53.8%) |
| Male-biased signals | 44,510 (46.2%) |
| Unique drugs (normalized) | 2,178 |
| Unique adverse events | 5,069 |
| DistMult MRR | 0.093 |
| DistMult AMRI | 0.9906 |
| Literature validation | 72.5% coverage, 82.8% precision (40 benchmarks) |

## Data Sources

All data sources are **freely available** and **open access**:

| Source | What | License | Edges |
|--------|------|---------|------:|
| [FDA FAERS](https://open.fda.gov) | Adverse event reports (2004 Q1 - 2025 Q3) | Public Domain | 869,142 |
| [ChEMBL 36](https://www.ebi.ac.uk/chembl/) | Drug-target interactions | CC-BY-SA 3.0 | 12,682 |
| [STRING v12.0](https://string-db.org) | Protein-protein interactions (score >= 700) | CC-BY 4.0 | 473,860 |
| [Reactome](https://reactome.org) | Pathway annotations | CC-BY 4.0 | 370,597 |
| [GTEx v8](https://gtexportal.org) | Sex-differential gene expression (Oliva et al. 2020) | Open Access | 289 |

## Drug Normalization

SexDiffKG v4 introduces a 4-tier drug normalization pipeline:

1. **DiAna dictionary** (47.0%): 846,917 FAERS drug name mappings from [DiAna](https://github.com/fusarolimichele/DiAna_package)
2. **prod_ai field** (6.5%): FDA product active ingredient
3. **ChEMBL synonyms** (0.3%): Cross-reference against ChEMBL 36
4. **String cleaning** (40.7%): Uppercase + special character removal

Total active-ingredient resolution: **53.9%**, reducing 710K raw drug names to 301K normalized entries.

## Quick Start

### Option 1: Conda

```bash
git clone https://github.com/jshaik369/SexDiffKG.git
cd SexDiffKG
conda env create -f environment.yml
conda activate sexdiffkg
```

### Option 2: Docker

```bash
docker build -t sexdiffkg .
docker run -it sexdiffkg
```

### Option 3: pip

```bash
pip install -r requirements.txt
```

## Pipeline

The pipeline consists of numbered Python scripts in `scripts/`:

```
01_download_faers.py          # Download 87 quarterly FAERS ZIP files from openFDA
02_parse_faers.py             # Parse DEMO, DRUG, REAC tables
03_deduplicate.py             # Deduplicate + filter to M/F only
v4_01_normalize_diana.py      # 4-tier drug normalization (DiAna + prod_ai + ChEMBL + raw)
v4_02_compute_signals.py      # Sex-stratified ROR computation via DuckDB (16 threads)
v4_03_build_kg.py             # Knowledge graph assembly (FAERS + ChEMBL + STRING + Reactome + GTEx)
v4_04_train_distmult.py       # DistMult training via PyKEEN (200d, 100 epochs)
v4_05b_train_rotatE_fixed.py  # RotatE + ComplEx training
validate_40_benchmarks_v4.py  # Literature benchmark validation (40 drug-AE pairs)
```

## Output Files

```
data/kg_v4/nodes.tsv                          # 109,867 nodes
data/kg_v4/edges.tsv                          # 1,822,851 edges
data/kg_v4/triples.tsv                        # NaN-free triples for embedding training
results/signals_v4/sex_differential_v4.parquet # 96,281 sex-differential signals
results/kg_embeddings/                         # Trained models + embeddings
results/validation_40_benchmarks_v4.json       # Validation results
results/analysis/sexdiffkg_statistics.json     # Canonical ground truth statistics
```

## Notable Findings

- **HDAC inhibitors** (HDAC1/2/3/6): Exclusively female-biased safety profiles
- **Estrogen receptor drugs** (ESR1): Counterintuitively male-biased safety signals
- **Platelet integrins** (ITGA2B/ITGB3): Exclusively female-biased
- **Validation precision**: 82.8% directional precision on 40 literature benchmarks

## Reproducibility

- **Hardware:** Tested on NVIDIA DGX Spark (Grace Blackwell, 128GB unified memory)
- **Training time:** ~2 hours for DistMult (200d, 100 epochs, CUDA)
- **Total pipeline:** ~6 hours end-to-end
- **Disk space:** ~11 GB for full dataset

## Citation

If you use SexDiffKG in your research, please cite:

```bibtex
@article{akhtarabbas2026sexdiffkg,
  title={SexDiffKG: A Sex-Differential Knowledge Graph for Drug Safety
         from 14.5 Million FDA Adverse Event Reports},
  author={Shaik, Mohammed Javeed Akhtar Abbas},
  journal={bioRxiv},
  year={2026},
  doi={10.1101/2026.709170}
}
```

## License

- **Code:** MIT License
- **Data:** CC-BY 4.0

## Author

**Mohammed Javeed Akhtar Abbas Shaik**
ORCID: [0009-0002-1748-7516](https://orcid.org/0009-0002-1748-7516)
Email: jshaik@coevolvenetwork.com
Affiliation: CoEvolve Network, Independent Researcher, Barcelona, Spain
"""

# Write all files
files = {
    f"{PUB}/ISMB2026_short_abstract.txt": ismb.strip(),
    f"{PUB}/ASHG2026_abstract.txt": ashg.strip(),
    f"{PUB}/NeurIPS2026_abstract.txt": neurips.strip(),
    f"{BASE}/README.md": readme.strip(),
}

for path, content in files.items():
    with open(path, "w") as f:
        f.write(content + "\n")
    print(f"Updated: {path} ({len(content)} chars)")

print("\nAll publication docs updated with v4 ground truth numbers.")
