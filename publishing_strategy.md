# SexDiffKG Publishing Strategy & Action Plan
**Date:** 2026-03-04
**Author:** J.Shaik | CoEvolve Network

---

## I. PORTFOLIO OVERVIEW

### Paper Inventory: 35 drafts + 1 flagship manuscript
- **29 READY** (>5KB, well-structured IMRaD)
- **3 DRAFT** (2-5KB, needs work): soc_atlas, reproductive_paradox, embedding
- **3 STUB** (<2KB, merge candidates): glp1ra_diabetes, severe_ae_sex, hepatotoxicity_sex
- **1 COMPLETE manuscript**: `manuscript_scidata_COMPLETE.md` (77.8KB) — Scientific Data format

### Ground Truth Compliance
- 14/35 papers reference all 3 exact GT numbers (nodes/edges/reports)
- 29/35 correctly reference FAERS count
- 0 papers contain wrong/stale numbers

### Existing Publication Materials
- 3 conference abstracts (ISMB 2026, ASHG 2026, NeurIPS 2026)
- 4 cover letters (Drug Safety, Biology of Sex Differences, Briefings in Bioinformatics, Scientific Data)
- Zenodo deposit (existing)
- bioRxiv preprint (existing)
- GitHub repo: https://github.com/jshaik369/sexdiffkg-deep-analysis

---

## II. STRATEGIC PAPER GROUPING

### Tier 1: Flagship Papers (Submit First — Highest Impact)

#### Paper A: MAIN PAPER — "SexDiffKG: A Knowledge Graph for Systematic Discovery of Sex-Differential Drug Safety Signals"
- **Source**: `manuscript_scidata_COMPLETE.md` (77.8KB) OR merge `comprehensive_methods_paper.md` + `sexdiffkg_methods_paper.md`
- **Lead finding**: Severity-sex gradient (rho=0.93), anti-regression (rho=1.0), 82.9% composite validation
- **Target journals (ranked)**:
  1. **eClinicalMedicine (Lancet)** (IF 10.0, OA, **NO APC**) — published Watson et al. 2019 sex-diff ADR landmark; IDEAL
  2. **Biology of Sex Differences** (IF 5.1, OA, APC $3,190) — perfect scope, has sex-diff pharmacovig precedent
  3. **Clinical Pharmacology & Therapeutics** (IF 5.3) — includes "bioinformation and applied systems biology"
  4. **Drug Safety** (IF 3.8, 6-day median first decision) — fastest review in field, ISoP official journal
- **Preprint**: medRxiv (pharmacovigilance = health sciences scope)
- **Timeline**: Submit preprint week 1, journal submission week 2

#### Paper B: DISCOVERY — "The Severity-Sex Gradient in Drug Safety: Fatal Events Are Sex-Balanced While Mild Events Are 64% Female"
- **Source**: `severity_sex_gradient_paper.md` (8.8KB) + `seriousness_sex_gradient_paper.md` (7.9KB) — MERGE
- **Lead finding**: rho=0.93 (p=0.003), entirely novel
- **Target journals**:
  1. **Clinical Pharmacology & Therapeutics** (IF 6.3) — premier clinical pharmacology
  2. **Drug Safety** (IF 3.8) — core audience
  3. **British Journal of Clinical Pharmacology** (IF 3.1) — strong pharmacovigilance tradition
- **Preprint**: medRxiv
- **Timeline**: Week 2-3

#### Paper C: STATISTICAL INNOVATION — "The Anti-Regression Phenomenon: Female Drug Safety Bias Strengthens With Statistical Power"
- **Source**: `anti_regression_paper.md` (5.5KB) + `volume_gradient_paper.md` (12.3KB) + `universal_anti_regression_paper.md` (7.0KB) — MERGE best parts
- **Lead finding**: Perfect monotonicity (rho=1.0, p=6.6e-64), counter-intuitive
- **Target journals**:
  1. **Pharmacoepidemiology and Drug Safety** (IF 3.3, Wiley) — methodological home
  2. **Statistics in Medicine** (IF 2.3) — statistical novelty angle
  3. **Drug Safety** (IF 3.8)
- **Preprint**: medRxiv
- **Timeline**: Week 3-4

### Tier 2: High-Impact Domain Papers (Submit Second Wave)

#### Paper D: IMMUNOLOGY — "Female Predominance in Checkpoint Inhibitor Adverse Events"
- **Source**: `CPI_irAE_paper.md` (36.8KB) — LARGEST, most complete paper
- **Target**: Journal for ImmunoTherapy of Cancer (IF 10.9) or JAMA Oncology (IF 28.4)
- **Timeline**: Week 4-5

#### Paper E: CARDIOLOGY — "Drug-Induced Cardiac Events Show Female Predominance Despite Male Epidemiological Prevalence"
- **Source**: `cardiac_reversal_paper.md` (35.2KB) — second largest
- **Target**: European Heart Journal - Cardiovascular Pharmacotherapy (IF 4.4) or Circulation (IF 35.5)
- **Timeline**: Week 4-5

#### Paper F: REGULATORY — "Sex-Specific Drug Safety Warnings Needed for 187 Medications"
- **Source**: `regulatory_paper.md` (22.1KB) — policy implications
- **Target**: JAMA Internal Medicine (IF 23.3) or BMJ (IF 42.7) — high impact, policy focus
- **Timeline**: Week 5-6

#### Paper G: SEX PARADOX — "Sex-Differential Drug Safety Signals Anti-Correlate with Reporter Sex"
- **Source**: `sex_paradox_paper.md` (10.1KB) + `reporter_decorrelation_paper.md` (5.2KB) — MERGE
- **Target**: Biology of Sex Differences (IF 4.9) — perfect scope fit
- **Timeline**: Week 5-6

### Tier 3: Specialist Domain Papers (Third Wave)

#### Paper H: HEPATOTOXICITY
- **Source**: `hepatotoxicity_paper.md` (6.7KB) — absorb `hepatotoxicity_sex_paper.md` stub
- **Target**: Hepatology Communications (IF 5.6) or Drug Safety

#### Paper I: THERAPEUTIC SPECTRUM
- **Source**: `cross_therapeutic_spectrum_paper.md` (9.0KB)
- **Target**: Pharmacoepidemiology and Drug Safety

#### Paper J: NETWORK TOPOLOGY
- **Source**: `network_topology_paper.md` (7.5KB)
- **Target**: Bioinformatics (IF 4.4) or Database (IF 3.6, OA, free APC)

#### Paper K: KNOWLEDGE GRAPH METHODOLOGY
- **Source**: `embedding_paper.md` (2.1KB — NEEDS EXPANSION) + model performance data
- **Target**: Briefings in Bioinformatics (IF 6.8) or Journal of Biomedical Informatics (IF 4.0)

#### Paper L: AGE-SEX INTERACTION
- **Source**: `age_sex_interaction_paper.md` (6.8KB)
- **Target**: Journal of Women's Health (IF 2.1) or Clinical Pharmacology & Therapeutics

---

## III. JOURNAL TARGET MATRIX

| Journal | IF | OA | APC | Scope Match | Priority Paper |
|---------|----|----|-----|-------------|---------------|
| BMJ | 42.7 | Hybrid | £3,000+ | Policy/regulatory | Paper F |
| JAMA Internal Medicine | 23.3 | Hybrid | ~$5,000 | Clinical impact | Paper F (alt) |
| JAMA Oncology | 28.4 | Hybrid | ~$5,000 | ICI/immunotherapy | Paper D (stretch) |
| Journal for ImmunoTherapy of Cancer | 10.9 | OA | ~$4,500 | ICI-focused | Paper D |
| PLOS Medicine | 9.9 | OA | $6,460 | Computational epi | Paper A |
| Briefings in Bioinformatics | 6.8 | Hybrid | ~$3,900 | KG methodology | Paper K |
| Clinical Pharmacology & Therapeutics | 6.3 | Hybrid | ~$4,200 | Clinical pharmacology | Paper B |
| Scientific Data | 5.8 | OA | ~$2,190 | Dataset/resource | Paper A (alt) |
| Biology of Sex Differences | 4.9 | OA | ~$2,790 | Sex differences | Paper G |
| Bioinformatics | 4.4 | OA | ~$2,800 | Computational bio | Paper J |
| Drug Safety | 3.8 | Hybrid | ~$3,860 | Core pharma | Paper B/C |
| Database (Oxford) | 3.6 | OA | ~FREE | Biological databases | Paper J (alt) |
| Pharmacoepidemiology & Drug Safety | 3.3 | Hybrid | ~$4,200 | Pharmacoepi | Paper C |
| BJCP | 3.1 | Hybrid | ~$3,700 | Clinical pharm | Paper B (alt) |
| BMJ Open | 2.3 | OA | £2,163 | Broad medical | Paper A (safe) |
| Journal of Women's Health | 2.1 | Hybrid | ~$3,200 | Women's health | Paper L |

---

## IV. PREPRINT STRATEGY

### Recommendation: Dual Preprint
1. **medRxiv** for clinical/pharmacovigilance papers (Papers A, B, C, D, E, F, G, L)
   - Scope: health sciences, clinical epidemiology
   - Free, DOI issued immediately
   - Screened for clinical relevance

2. **bioRxiv** for computational/methodology papers (Papers J, K)
   - Scope: biological sciences, computational biology, bioinformatics
   - Free, DOI issued immediately
   - Wider bioinformatics audience

### Timing
- Post preprints 1-2 weeks BEFORE journal submission
- This establishes priority and generates early citations
- Update existing bioRxiv preprint with latest v4 data

---

## V. CONFERENCE STRATEGY

### ISMB 2026 (July 12-16, Washington DC) — CRITICAL
**Deadline: April 9, 2026 (35 days away)**

**Action Items (URGENT):**
1. UPDATE ABSTRACT — Current versions have stale v3 numbers!
   - Fix: 109,867 nodes (not 127,063), 1,822,851 edges (not 5.8M)
   - Fix: ComplEx MRR 0.2484 (not DistMult 0.048)
   - Fix: Reactome (not KEGG)
   - Fix: 96,281 signals (not 183,539)
2. DESIGN POSTER — No actual poster file exists yet
   - Use fig263 (stats card) + fig264 (validation) as base
   - Need 48×36 inch or A0 PDF
3. REGISTER on submission portal
4. Target March 26 for final draft per checklist

### ASHG 2026 — Abstract exists, needs v4 update
### NeurIPS 2026 — Abstract exists, KG methodology angle

---

## VI. MERGE/CLEANUP PLAN

### Papers to MERGE (reduce redundancy)
1. `severity_sex_gradient_paper.md` + `seriousness_sex_gradient_paper.md` → **Paper B**
2. `anti_regression_paper.md` + `volume_gradient_paper.md` + `universal_anti_regression_paper.md` → **Paper C**
3. `sex_paradox_paper.md` + `reporter_decorrelation_paper.md` → **Paper G**
4. `hepatotoxicity_paper.md` ← absorb `hepatotoxicity_sex_paper.md` (stub)
5. `severity_sex_gradient_paper.md` ← absorb `severe_ae_sex_paper.md` (stub)

### Papers to EXPAND
1. `embedding_paper.md` (2.1KB → needs 5KB+ for Paper K)
2. `soc_atlas_paper.md` (4.3KB → needs 6KB+)
3. `reproductive_paradox_paper.md` (3.6KB → needs 5KB+)

### Papers to RETIRE (absorbed into merges)
- `hepatotoxicity_sex_paper.md` → merged into hepatotoxicity_paper.md
- `severe_ae_sex_paper.md` → merged into severity_sex_gradient_paper.md
- `glp1ra_diabetes_paper.md` → standalone or merge into cross_therapeutic_spectrum

---

## VII. SUBMISSION TIMELINE (12-Week Plan)

| Week | Action |
|------|--------|
| 1 | Fix ISMB abstract (v4 numbers). Update bioRxiv preprint. Resolve 5 inconsistencies. |
| 2 | Submit Paper A preprint (medRxiv). Begin Paper A journal submission (PLOS Medicine). |
| 3 | Submit Paper B preprint. Merge severity papers. Submit Paper B (CPT). |
| 3-4 | Design ISMB poster. Submit Paper C preprint + journal (PDS). |
| 4 | Submit by April 9 ISMB deadline. |
| 5-6 | Submit Papers D (JITC), E (EHCVP), F (BMJ/JAMA IM). |
| 6-7 | Submit Paper G (Biol Sex Diff). Expand embedding paper. |
| 7-8 | Submit Papers H, I, J (domain journals). |
| 9-10 | Submit Paper K (Briefings in Bioinformatics). Paper L (JWH). |
| 11-12 | Follow up on reviews. Prepare revisions. Update Zenodo v4. |

---

## VIII. BUDGET CONSIDERATIONS

### Estimated APC Costs (if all go OA)
- Tier 1 (3 papers): ~$12,000-16,000
- Tier 2 (4 papers): ~$12,000-18,000
- Tier 3 (5 papers): ~$10,000-15,000
- Total potential: $34,000-49,000

### Cost Reduction Strategies
1. **Database (Oxford)** — often waives APC for bioinformatics papers
2. **Hybrid journals** — choose subscription-access (free) where possible
3. **Institutional waivers** — check if CoEvolve Network qualifies
4. **bioRxiv/medRxiv** — free preprints establish priority regardless
5. **PLOS fee waivers** — available for developing country researchers
6. **Green OA** — post accepted manuscripts on institutional repository after embargo

### Recommended Strategy: Selective OA
- Paper A (main paper) → FULL OA (highest visibility needed)
- Papers B, D, F → OA if budget allows (high impact)
- Papers C, G, H-L → subscription access (save costs)

---

## IX. PRE-SUBMISSION CHECKLIST

Before submitting ANY paper:
- [ ] All numbers match GROUND_TRUTH.json (109,867 / 1,822,851 / 14,536,008)
- [ ] Reactome (NOT KEGG) referenced
- [ ] ComplEx v4 MRR 0.2484 (not stale values)
- [ ] DiAna normalization (846,917 mappings, 53.9%)
- [ ] Author: Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
- [ ] ORCID: 0009-0002-1748-7516
- [ ] Affiliation: CoEvolve Network, Independent Researcher, Barcelona, Spain
- [ ] GitHub/Zenodo DOI referenced
- [ ] No v3 numbers anywhere
- [ ] Death statistics use standardized 50.1%F Fatal category
- [ ] Cardiotoxicity exception documented if anti-regression mentioned
- [ ] OpenFDA excluded from composite validation or flagged

---

## X. KEY METRICS FOR IMPACT

### What Makes SexDiffKG Publishable at High Impact
1. **Scale**: 14.5M reports, 96,281 signals, 2,178 drugs — largest sex-differential analysis ever
2. **Novelty**: Severity-sex gradient (rho=0.93) — never systematically quantified
3. **Counter-intuitive**: Anti-regression — more data makes signal stronger, not weaker
4. **Clinical utility**: 108 urgent signals, 187 drugs needing sex-specific warnings
5. **Validation**: 82.9% composite concordance across 4+ independent sources
6. **Reproducibility**: Full KG + code on GitHub + Zenodo, ComplEx embeddings available
7. **Timeliness**: Growing regulatory push for sex-stratified drug safety analysis (FDA, EMA)

---

## XI. COMPETITIVE LANDSCAPE

### Key Competitors/Prior Work
1. **Watson et al. 2019** — Sex differences in GI ADRs (FAERS, 2004-2011). We extend to 2025Q3, 20× more drugs.
2. **Zucker & Prendergast 2020** — Sex differences in ADR reporting. We add KG + embeddings + validation.
3. **Conforti et al. 2018** — ICI sex differences. Our Paper D is 10× larger dataset.
4. **PreciseADR (2025, Advanced Science)** — GNN for ADR prediction with demographics. Our ComplEx approach is complementary.
5. **Chandak et al. (Cell Patterns 2020)** — ML for sex-differential ADRs. We have 5× more data and KG validation.

### Our Advantages
- Latest FAERS data (through 2025Q3 vs most papers using 2011-2020)
- Knowledge graph integration (unique — no competitor combines KG + sex-differential signals)
- Comprehensive validation (82.9% across 4 sources vs typically 1 validation)
- 35 ready papers covering every major domain
