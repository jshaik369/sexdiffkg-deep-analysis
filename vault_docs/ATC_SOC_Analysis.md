# ATC/SOC Sex-Differential Drug Class Analysis (2026-03-04)

## Data Sources
- Signals: `results/signals_v4/sex_differential_v4.parquet` (96,281 signals)
- ATC mapping: `data/processed/kg_drug_atc_mapping.csv` (2,665 drug-ATC pairs)
- SOC mapping: `data/processed/ae_soc_mapping.csv` (9,949 AE-SOC mappings)
- ChEMBL 36 DB: `/home/jshaik369/veda-kg/data/chembl/chembl_36/chembl_36_sqlite/chembl_36.db`

## Coverage
- 1,424/2,178 drugs matched to ATC (65.4%)
- 100% AE coverage for SOC
- 137,665 signal-ATC pairs (inflated: 1 drug → multiple ATC codes)

## Key Finding: Systematic Female Bias Across Drug Classes

Most drug classes show female-predominant adverse event reporting. Only 2/11 ATC L1 categories are male-biased (Antiparasitics 36.3% F, Various 44.5% F).

### ATC Level 1 Summary
| Code | Class | Signals | Drugs | %F | Bias |
|------|-------|---------|-------|-----|------|
| H | Systemic Hormones | 4,928 | 41 | 65.0% | F |
| A | Alimentary/Metabolism | 13,848 | 171 | 58.3% | F |
| N | Nervous System | 22,425 | 272 | 58.2% | F |
| J | Anti-infectives | 7,424 | 162 | 57.9% | F |
| L | Antineoplastic/Immunomod | 27,627 | 318 | 57.8% | F |
| S | Sensory Organs | 12,626 | 117 | 57.8% | F |
| D | Dermatologicals | 10,889 | 110 | 56.1% | F |
| C | Cardiovascular | 11,455 | 145 | 54.6% | Balanced |
| R | Respiratory | 11,494 | 89 | 49.1% | Balanced |
| V | Various | 1,060 | 56 | 44.5% | M |
| P | Antiparasitic | 980 | 16 | 36.3% | M |

### Most Extreme L2 Groups
**Female-biased**: J02 Antimycotics (75.6%), J04 Antimycobacterials (74.2%), H02 Corticosteroids (69.2%), N02 Analgesics (66.4%)
**Male-biased**: P02 Anthelmintics (14.1%), G03 Sex Hormones (19.8%), V08 Contrast Media (20.7%)

### Notable L3 Findings
- N02A Opioids: 74.3% F (meanLogR=0.667)
- G04C BPH drugs: 84.1% F — paradoxical female bias in male-specific drug class

### SOC Summary
**Most F-biased SOCs**: Social circumstances (80.6%), Renal/urinary (67.2%), Cardiac (65.1%)
**Most M-biased SOCs**: Eye disorders (32.3%), Reproductive (34.2%)

## Files Created
- `results/analysis/atc_soc_analysis.json` — full structured results
- `data/processed/atc_drug_classification.csv` — ChEMBL ATC codes (4,569)
- `data/processed/atc_who_full.csv` — WHO ATC-DDD (7,345)
- `data/processed/atc_who_hierarchy.csv` — WHO hierarchy (6,030)
- `data/processed/drug_indications.csv` — ChEMBL indications (59,954)
- `data/processed/kg_drug_atc_mapping.csv` — KG drug mapping (2,665)
- `data/processed/ae_soc_mapping.csv` — AE-SOC mapping (9,949)

## Publication Implications
This analysis enables Drug Class Sex-Differential Safety Profiles paper (target: Drug Safety, IF 4.0).
Key narrative: systematic female vulnerability is NOT limited to specific drug classes but is a pan-therapeutic phenomenon, with magnitude varying by mechanism (partial agonists show less bias than full agonists).
