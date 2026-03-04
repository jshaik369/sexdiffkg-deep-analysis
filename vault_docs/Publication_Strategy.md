# SexDiffKG Publication Strategy & Competitive Landscape
## Generated: 2026-03-04

## COMPETITIVE POSITION

**SexDiffKG occupies a unique niche** — NO existing work combines all three of:
1. Large-scale sex-stratified pharmacovigilance signal detection
2. Multi-relational KG with drug-target-gene-pathway-tissue-AE integration
3. KG embedding models for link prediction

### Direct Competitors

| Competitor | Year | Journal | Scale | KG? | Embeddings? | How We Differ |
|---|---|---|---|---|---|---|
| **AwareDX** (Chandak/Tatonetti) | 2020 | Patterns (Cell) | 20,817 signals, 792 drugs | No | No | 96,281 signals (5x), full KG, embeddings, 2004-2025 data |
| **Watson et al.** | 2019 | eClinicalMedicine | 18M VigiBase reports | No | No | Descriptive only, no signal detection, no mechanistic layer |
| **Zucker & Prendergast** | 2020 | Biol Sex Diff | 86 drugs manually | No | No | 3,441 drugs computationally, genome-scale context |
| **Yu et al.** | 2016 | Sci Reports | 668 drugs | No | No | Much smaller, no KG, older FAERS |
| **Chandak et al. (UAB)** | 2024 | BMC Pharmacol Toxicol | Gene-regulatory networks | Partial | No | We do at far larger scale with unified KG |

### KG Competitors (Not Sex-Stratified)

| KG | Year | Journal | Size | Sex-Stratified? |
|---|---|---|---|---|
| **PrimeKG** | 2023 | Scientific Data | 129K nodes, 4M edges | No |
| **Hetionet** | 2017 | eLife | 47K nodes, 2.25M edges | No |
| **iKraph** | 2025 | Nature Mach Intel | 10.7M entities, 30.8M relations | No |
| **OpenPVSignal** | 2024 | Drug Safety | PV signal KG | No |
| **DD-CKG** | 2025 | Bioinformatics | Causal KG | No |

### Strongest Novelty Claim
"The first knowledge graph to integrate sex-stratified pharmacovigilance signals with multi-relational molecular data (drug targets, protein interactions, biological pathways, and tissue expression) and train KG embedding models for predicting sex-differential drug safety patterns."

---

## PUBLICATION PLAN (6 Papers)

### Paper 1: Data Resource — Scientific Data (IF 6.9) — Q2 2026
- Full data descriptor: KG construction, sources, schema, validation
- Establishes the resource. Published PrimeKG. Natural venue.

### Paper 2: ISMB 2026 Proceedings — Bioinformatics (IF 5.4) — SUBMITTED
- Condensed methods + key results (9 pages)

### Paper 3: PV Methods — Drug Safety (IF 3.65) — Q3 2026
- Sex-stratified ROR methodology, DiAna normalization, signal classification
- Top drug/AE findings, clinical implications, READUS-PV compliance
- Published DiAna and READUS-PV — reviewers understand methodology

### Paper 4: KGE Prediction — Briefings in Bioinformatics (IF 7.7) — Q4 2026
- ComplEx/DistMult/RotatE comparison, link prediction for novel signals
- Mechanistic pathway analysis, case studies

### Paper 5: Biology — Biology of Sex Differences (IF 5.1) — Q1 2027
- Biological interpretation: pathways, tissues, gene expression explaining sex-diff signals
- Zucker did 86 drugs manually; we do 3,441 computationally

### Paper 6: Cross-DB Validation — Pharmacoepidemiol Drug Saf — Q2 2027
- Validate signals against JADER (Japan), VigiBase (global), EudraVigilance (Europe)

---

## MUST-CITE REFERENCES

### Methods
- van Puijenbroek et al. 2002 — Original ROR method
- Rothman et al. 2004 — ROR advantages over PRR
- Fusaroli et al. 2024 — DiAna dictionary (Drug Safety)
- Ali et al. 2021 — PyKEEN (JMLR)
- Trouillon et al. 2016 — ComplEx (ICML)
- READUS-PV 2024 — Disproportionality reporting guidelines (Drug Safety)

### Competitors (cite and differentiate)
- Chandak et al. 2020 — AwareDX (Patterns)
- Zucker & Prendergast 2020 — PK predicts ADRs (Biol Sex Diff)
- Watson et al. 2019 — Global ADR sex differences (eClinicalMedicine)
- Yu et al. 2016 — Systematic FAERS sex differences (Sci Reports)

### KG Landscape
- Chandak, Huang, Zitnik 2023 — PrimeKG (Scientific Data)
- Himmelstein et al. 2017 — Hetionet (eLife)
- iKraph 2025 — Nature Machine Intelligence
- OpenPVSignal 2025 — Drug Safety
- KG in PV reviews 2024 — Clinical Therapeutics (2 papers)

---

## SUPPLEMENTARY DATA SOURCES

### Free Download
- OpenFDA FAERS API/Bulk: open.fda.gov
- WHO ATC Classification: whocc.no + GitHub scraper (github.com/fabkury/atcd)
- DrugBank Open Data: go.drugbank.com (academic license free)
- DailyMed/FDALabel: dailymed.nlm.nih.gov (sex-specific label warnings)
- JADER (Japan): pmda.go.jp
- EudraVigilance (public): adrreports.eu
- DiAna R Package: github.com/fusarolimichele/DiAna

### Restricted (Application Required)
- WHO VigiBase (full): who-umc.org (40M+ ICSRs, 160+ countries)
- EudraVigilance (full): EMA application
- DrugBank 6.0 (full): academic license
