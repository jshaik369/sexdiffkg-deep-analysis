# AUDIT PACKAGE — SexDiffKG v4/v5

**Generated:** 2026-03-05T03:20:14.937506
**Author:** Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
**ORCID:** 0009-0002-1748-7516

## Purpose

This document enables any researcher to independently verify every number in SexDiffKG publications. Every claim has a verification path from source data to final number.

---

## 1. Source Data Verification

### FAERS (FDA Adverse Event Reporting System)
- **Source:** https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html
- **Quarters:** 87 (2004Q1 - 2025Q3)
- **Raw files:** `data/raw/faers/` (87 quarterly directories via symlinks)
- **Deduplication:** Script `scripts/01_deduplicate_faers.py` using caseid priority
- **Verification:** `wc -l data/processed/faers/dedup_reports.parquet` → 14,536,008 rows
- **Sex breakdown:** F: 8,744,397 / M: 5,791,611 (from `sex` column value counts)

### ChEMBL 36
- **Source:** https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_36/
- **Local:** `/home/jshaik369/veda-kg/data/chembl/chembl_36/chembl_36_sqlite/chembl_36.db` (29.7 GB)
- **Integrity:** SQLite `PRAGMA integrity_check` = ok
- **Verification:** `SELECT COUNT(*) FROM molecule_dictionary` → 2,878,135

### STRING v12.0
- **Source:** https://stringdb-downloads.org/download/protein.links.v12.0/9606.protein.links.v12.0.txt.gz
- **MD5:** `5b7c91d02926e723ad30e81ab9d009a4` (verified against fresh download 2026-03-05)
- **Interactions:** 13,715,404 human PPI edges
- **Local:** `data/raw/string/9606.protein.links.v12.0.txt.gz`

### Reactome
- **Source:** https://reactome.org/download-data (UniProt2Reactome_All_Levels.txt)
- **Pathways:** 2,279 human pathways in KG

### GTEx v8
- **Source:** https://gtexportal.org/
- **Sex-differential expression:** 289 tissue-gene pairs

### DiAna Drug Dictionary
- **Mappings:** 846,917 FAERS→active ingredient
- **Resolution:** 53.9% of FAERS drug mentions

## 2. KG v4 Canonical Numbers

| Metric | Value | Verification Command |
|--------|-------|---------------------|
| Total nodes | 109,867 | `wc -l data/kg_v4/nodes.tsv` - 1 (header) |
| Total edges | 1,822,851 | `wc -l data/kg_v4/edges.tsv` - 1 |
| Gene | 77,498 | `grep -c Gene data/kg_v4/nodes.tsv` |
| Protein | 16,201 | `grep -c Protein data/kg_v4/nodes.tsv` |
| AdverseEvent | 9,949 | `grep -c AdverseEvent data/kg_v4/nodes.tsv` |
| Drug | 3,920 | `grep -c Drug data/kg_v4/nodes.tsv` |
| Pathway | 2,279 | `grep -c Pathway data/kg_v4/nodes.tsv` |
| Tissue | 20 | `grep -c Tissue data/kg_v4/nodes.tsv` |

### MD5 Checksums (v4 canonical)
```
5a7331b1b0e7f11853444eb59e2b9166  data/kg_v4/nodes.tsv
b8e4890c2063bdf9357c76730881b440  data/kg_v4/edges.tsv
2d4e46b1265a9a9bd44bbfc7372a9e44  data/kg_v4/triples.tsv
```

### Edge Type Counts (v4)
| Edge Type | Count | Source |
|-----------|-------|--------|
| has_adverse_event | 869,142 | FAERS ROR analysis |
| interacts_with | 473,860 | STRING v12.0 (score > 400) |
| participates_in | 370,597 | Reactome pathways |
| sex_differential_adverse_event | 96,281 | FAERS sex-stratified ROR |
| targets | 12,682 | ChEMBL 36 drug-target |
| sex_differential_expression | 289 | GTEx v8 |

### Note on Duplicates
v4 edges.tsv contains 1,822,851 rows but only 1,532,674 unique (subject, predicate, object) triples.
290,177 duplicates arose from multiple evidence sources mapping same entity pairs.
Duplicates: has_adverse_event 254,164 + participates_in 29,105 + targets 6,908.
This does NOT affect analyses; code operates on unique triples.

## 3. Signal Verification

| Metric | Value | File |
|--------|-------|------|
| Total sex-diff signals | 96,281 | results/signals_v4/sex_differential_v4.parquet |
| Female-biased signals | 51,771 (53.8%) | direction == 'female_higher' |
| Male-biased signals | 44,510 (46.2%) | direction == 'male_higher' |
| Unique drugs | 2,178 | drug_name nunique |
| Unique AEs | 5,069 | adverse_event nunique |

### Validation
- **Benchmarks:** 40 literature-sourced drug-AE-sex direction pairs
- **Coverage:** 29/40 (72.5%) — found matching signal in KG
- **Directional precision:** 24/29 correct (82.8%)
- **Composite concordance:** 82.9% across 4 independent validation sources
- **File:** results/analysis/signal_validation_benchmarks.json

## 4. Embedding Verification

### ComplEx v4
| Metric | Value |
|--------|-------|
| Dimensions | 200 (complex, = 400 real) |
| Epochs | 100 |
| MRR | 0.2484 |
| Hits@1 | 0.1678 |
| Hits@10 | 0.4069 |
| AMRI | 0.9902 |
| File | results/kg_embeddings_v4/ComplEx/model.pt |

### DistMult v4.1
| Metric | Value |
|--------|-------|
| MRR | 0.1013 |
| Hits@1 | 0.0481 |
| Hits@10 | 0.1961 |
| AMRI | 0.9909 |
| File | results/kg_embeddings_v4/DistMult/ |

### RotatE v4.1
| Metric | Value |
|--------|-------|
| MRR | 0.2018 |
| Hits@1 | 0.1128 |
| Hits@10 | 0.3677 |
| AMRI | 0.9922 |
| File | results/kg_embeddings_v4/RotatE_v4.1/ |

## 5. KG v5 (Merged with VEDA-KG)

| Metric | Value |
|--------|-------|
| Total nodes | 246,056 |
| Total edges | 3,182,843 |
| Node types | 16 |
| Edge types | 18 |
| v4 unique triples preserved | 1,532,674 (100%) |
| New edges from VEDA | 1,650,169 |

### v5 New Node Types (from VEDA)
Gene (expanded), Compound, ClinicalTrial, Disease, Unknown, Symptom, Intervention, Herb, Dosha, Rasa, Guna

### v5 New Edge Types (from VEDA)
investigates, tests_intervention, treats, binds_to, modulates, encoded_by, associated_with, causes_adverse_event, corresponds_to, same_as, pacifies_dosha, aggravates_dosha

## 6. Key Discoveries (Verification Paths)

### Severity-Sex Gradient
- Spearman rho = 0.93, p = 0.003
- Verification: Group signals by outcome severity (fatal→mild), compute female fraction per group
- Fatal: 50.1%F, Serious: 52.8%F, Hospitalization: 53.3%F, Mild: 63.5%F

### Anti-Regression Effect
- Spearman rho = 1.000, p = 6.6e-64
- Female bias INCREASES with sample size (opposite of regression to mean)
- Perfect monotonicity across all report count bins

### 14.4-fold Asymmetry
- Female-extreme signals: 7,457 (|log_ratio| > 1.0, female_higher)
- Male-extreme signals: 519 (|log_ratio| > 1.0, male_higher)
- Ratio: 7,457 / 519 = 14.37x

## 7. Software Versions

| Software | Version |
|----------|---------|
| Python | 3.13+ |
| PyKEEN | 1.11.1 |
| PyTorch | 2.x |
| pandas | 2.x |
| numpy | 2.x |
| scipy | 1.x |

## 8. Hardware

| System | Specs |
|--------|-------|
| DGX Grace (primary) | 20 ARM cores, NVIDIA GB10 GPU (complex tensors incompatible — CPU only for KG embeddings) |
| Mac Mini M2 (secondary) | 4 CPU threads, 16GB RAM |
| Storage | NVMe (3.7TB) + 8TB Samsung SSD + 28TB HDD |

## 9. Audit Reports

| Report | Score | File |
|--------|-------|------|
| VEDA integrity | 41/41 (100%) | results/analysis/veda_integrity_audit.json |
| Molecular audit | 31/31 (100%) | results/analysis/molecular_audit_corrected.json |
| Final molecular audit | PASS | results/analysis/final_molecular_audit.json |
| Number cascade | 33/36 (91.7%, 0 fail) | results/analysis/number_cascade_audit.json |
| FAIR compliance | 15/15 (100%) | results/analysis/fair_compliance.json |
| Reproducibility | 39/40 (97.5%) | results/analysis/reproducibility_verification.json |
| ATC enrichment | 1,789/3,920 drugs | results/analysis/atc_enrichment.json |

## 10. GROUND_TRUTH.json Locations (RAID)

1. `/home/jshaik369/sexdiffkg/GROUND_TRUTH.json`
2. `/home/jshaik369/AYURFEM-Vault/projects/sexdiffkg/GROUND_TRUTH.json`
3. `/home/jshaik369/sexdiffkg/results/GROUND_TRUTH.json`
4. `/home/jshaik369/sexdiffkg/data/kg_v4/GROUND_TRUTH.json`

All 4 copies verified identical via JSON content hash.
