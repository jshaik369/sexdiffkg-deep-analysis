# SexDiffKG: A sex-stratified knowledge graph integrating 14.5 million FDA adverse event reports with multi-omics data for pharmacovigilance

Mohammed Javeed Akhtar Abbas Shaik

CoEvolve Network, Barcelona, Spain

Correspondence: jshaik@coevolvenetwork.com

ORCID: 0009-0002-1748-7516

---

## Abstract

Sex differences in adverse drug reactions (ADRs) are well documented -- women experience ADRs at 1.5-1.7 times the rate of men -- yet no existing knowledge graph encodes biological sex on drug-safety edges. We present SexDiffKG, an open, sex-stratified knowledge graph comprising 109,867 nodes (6 types) and 1,822,851 edges (6 relation types) that integrates 14,536,008 deduplicated FDA Adverse Event Reporting System (FAERS) reports spanning 87 quarters (2004Q1-2025Q3) with protein interactions (STRING v12.0), drug-target binding (ChEMBL 36), biological pathways (Reactome), and sex-differential gene expression (GTEx v8). Drug names were normalized using the DiAna dictionary (846,917 mappings; 53.9% active-ingredient resolution). SexDiffKG captures 96,281 sex-differential drug-adverse event signals, of which 53.8% are female-biased. Validation against 40 literature benchmarks achieves 72.5% coverage and 82.8% directional precision. Pre-trained ComplEx knowledge graph embeddings (MRR 0.2484, Hits@10 40.69%) are provided for downstream link prediction. All data, code, and embeddings are deposited on Zenodo and GitHub under open licenses.

---

## Background & Summary

Women experience adverse drug reactions (ADRs) at approximately 1.5 to 1.7 times the rate of men [1,2]. This disparity has multiple origins: pharmacokinetic differences in absorption, distribution, metabolism, and excretion lead to higher drug exposure in women for 88% of FDA-approved compounds [2]; historically, women of childbearing potential were excluded from clinical trials following a 1977 FDA guideline [3], creating a knowledge gap that the 1993 NIH Revitalization Act and subsequent policies have only partially addressed [4]; and sex-based differences in immune function, hormonal signaling, and body composition further modulate drug response [5].

The FDA Adverse Event Reporting System (FAERS) -- the world's largest spontaneous pharmacovigilance database with over 27 million raw reports -- captures sex information for approximately 65% of its records, making it the richest available resource for sex-stratified drug safety analysis. However, existing computational studies have typically analyzed FAERS in a flat, tabular fashion [6,7], identifying sex-differential signals but not integrating them with the molecular and biological context needed for mechanistic interpretation. Meanwhile, the knowledge graph revolution in biomedicine has produced several influential resources -- Hetionet [8] (47,031 nodes, 2.25 million edges), DRKG [9] (97,238 nodes, 5.87 million edges), PrimeKG [10] (129,375 nodes, 4.05 million edges), and PharMeBINet [11] (2.87 million nodes, 15.88 million edges) -- yet none of these encode biological sex on their drug-safety edges. Where these knowledge graphs include adverse event information, they derive it from SIDER [12], a curated database of drug label side effects that aggregates across sexes.

We present SexDiffKG, a knowledge graph that bridges this gap by encoding sex-differential pharmacovigilance signals as first-class graph elements alongside multi-scale molecular biology. SexDiffKG integrates six authoritative data sources: (1) 14,536,008 deduplicated FAERS reports spanning 87 quarterly releases from 2004Q1 to 2025Q3, stratified by sex to yield 96,281 sex-differential drug-adverse event edges; (2) STRING v12.0 protein-protein interactions [13]; (3) ChEMBL 36 drug-target binding data [14]; (4) Reactome biological pathways [15]; and (5) literature-curated sex-differential gene expression from GTEx v8 [16]. Drug name normalization uses the DiAna dictionary [17], an open-source resource specifically designed for FAERS, achieving 53.9% active-ingredient resolution from free-text drug names through 846,917 name mappings.

The resulting knowledge graph contains 109,867 nodes across 6 types (Gene, Protein, AdverseEvent, Drug, Pathway, Tissue) and 1,822,851 edges across 6 relation types. The graph uniquely captures both aggregate drug-safety signals (`has_adverse_event`, 869,142 edges derived from reporting odds ratios) and their sex-differential counterparts (`sex_differential_adverse_event`, 96,281 edges where the log ratio of female-to-male ROR exceeds 0.5 in absolute value). Of these sex-differential edges, 53.8% indicate female-biased adverse event reporting and 46.2% indicate male-biased reporting.

Pre-trained ComplEx [18] knowledge graph embeddings are provided (MRR 0.2484, Hits@10 40.69%), enabling downstream applications including link prediction for novel sex-differential ADR discovery, drug clustering by safety profile, and target-level sex bias analysis. An initial link prediction analysis identifies 500 novel candidate sex-differential drug-adverse event associations for experimental validation.

SexDiffKG is designed to support multiple use cases in precision pharmacovigilance: identifying drug-target pathways underlying sex-differential safety signals; generating hypotheses for sex-specific dosing or monitoring; benchmarking computational models of sex-differential drug response; and informing regulatory decisions about sex-specific drug safety labeling. All data, code, embeddings, and analysis results are available under open licenses on Zenodo and GitHub, with a comprehensive data dictionary for reuse.

---

## Methods

### FAERS data acquisition and deduplication

Quarterly ASCII data files from the FDA Adverse Event Reporting System (FAERS) were downloaded from the FDA public dashboard (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html) covering 87 quarters from 2004Q1 through 2025Q3. Raw data were ingested from four primary tables: DEMO (demographics including sex, age, reporter country), DRUG (drug names, role codes, route of administration), REAC (adverse event terms coded to MedDRA Preferred Terms), and THER (therapy dates and duration).

Deduplication followed the FDA-recommended approach using the `caseid` field to identify report families, retaining only the most recent version of each case based on the highest `primaryid` within each `caseid`. This yielded 14,536,008 unique deduplicated reports. Reports were stratified by sex: 8,744,397 (60.2%) female and 5,791,611 (39.8%) male. Reports with missing or ambiguous sex designation were excluded from sex-stratified analyses but retained for aggregate safety signal computation.

### Drug name normalization

FAERS drug names are entered as free text by reporters, resulting in substantial heterogeneity including brand names, misspellings, abbreviations, and combination products. We applied a multi-tier normalization pipeline:

1. **DiAna dictionary (primary):** The DiAna drug name dictionary [17], an open-source resource specifically designed for FAERS normalization, provided 846,917 drug name-to-active ingredient mappings. This achieved a 47.0% direct match rate on our corpus of approximately 710,000 unique raw drug names.

2. **prod_ai field (secondary):** The FAERS `prod_ai` field, which contains FDA-curated active ingredient information for a subset of records, provided an additional 6.5% resolution.

3. **ChEMBL synonym lookup (tertiary):** Unresolved names were queried against ChEMBL 36 molecule synonyms [14], yielding an additional 0.3% resolution.

4. **String cleaning (fallback):** Remaining names underwent uppercase normalization, removal of dosage forms and strengths, and standardization of common abbreviations, resolving an additional 40.7% to cleaned (though not necessarily normalized to active ingredient) forms.

The combined pipeline achieved 53.9% active-ingredient resolution. Drug reports were filtered to primary suspect (PS) and secondary suspect (SS) role codes, excluding concomitant medications to reduce noise in signal computation.

### Sex-stratified signal computation

For each drug-adverse event pair with at least 10 reports per sex, we computed sex-specific reporting odds ratios (ROR) using standard 2x2 contingency tables. For a given drug *d* and adverse event *e* in sex *s*, the ROR was calculated as:

    ROR(d,e,s) = (a * d_cell) / (b * c)

where *a* = reports of drug *d* with adverse event *e* in sex *s*; *b* = reports of drug *d* without adverse event *e* in sex *s*; *c* = reports of adverse event *e* without drug *d* in sex *s*; *d_cell* = reports of neither drug *d* nor adverse event *e* in sex *s*.

Sex-differential signals were quantified as the natural logarithm of the female-to-male ROR ratio:

    log_ratio = ln(ROR_female / ROR_male)

Positive values indicate female-biased reporting; negative values indicate male-biased reporting. Signals were classified as sex-differential if |log_ratio| >= 0.5 (corresponding to an approximately 1.65-fold difference), with a minimum of 10 reports per sex to ensure statistical stability. This yielded 254,114 total drug-adverse event comparisons (both sexes with >= 10 reports), of which 96,281 met the sex-differential threshold and were included in the knowledge graph as `sex_differential_adverse_event` edges. Of these, 51,771 (53.8%) were female-biased and 44,510 (46.2%) were male-biased.

### Knowledge graph construction

SexDiffKG v4 integrates six data sources into a heterogeneous knowledge graph with 6 node types and 6 relation types:

**Drug safety layer (FAERS).** Drug-adverse event edges were derived from the sex-stratified signal analysis. The `has_adverse_event` relation (869,142 edges) captures all drug-AE pairs with ROR > 1 in at least one sex. The `sex_differential_adverse_event` relation (96,281 edges) captures pairs meeting the sex-differential threshold described above. Drug nodes (n = 3,920) are identified by normalized active ingredient names; adverse event nodes (n = 9,949) are identified by MedDRA Preferred Terms.

**Protein interaction layer (STRING v12.0).** Human protein-protein interactions were extracted from STRING v12.0 [13] using a combined confidence score threshold of >= 700 (high confidence). ENSP identifiers were retained as protein node identifiers. This contributed 473,860 `interacts_with` edges among 16,201 protein nodes.

**Drug-target layer (ChEMBL 36).** Drug-target binding interactions were extracted from ChEMBL 36 [14], yielding 12,682 `targets` edges linking drugs to gene targets. Target gene symbols were mapped to the Gene node namespace.

**Pathway layer (Reactome).** Gene-pathway associations were obtained from Reactome [15] (release 2026-02) using the Ensembl-to-Reactome mapping file, filtered to Homo sapiens entries. This contributed 370,597 `participates_in` edges mapping 77,498 genes to 2,279 pathways.

**Sex-differential expression layer (GTEx v8, literature-curated).** A curated set of sex-differential gene expression annotations was compiled from Oliva et al. [16], who identified genes with significant sex-biased expression across 44 human tissues using GTEx v8 data. A subset of 123 pharmacologically relevant genes across 20 tissues was selected based on known involvement in drug metabolism (CYP enzymes), hormone signaling, and pharmacokinetic sex differences, yielding 289 `sex_differential_expression` edges. This curated layer prioritizes genes with established relevance to drug safety over comprehensive genomic coverage.

All edges were validated for completeness: zero NaN entries were present in the final triples file. Entity identifiers follow a namespace convention (DRUG:, AE:, GENE:, PROTEIN:, PATHWAY:, TISSUE:) to prevent identifier collisions across node types. The final knowledge graph comprises 109,867 nodes and 1,822,851 edges. MD5 checksums are provided for all output files (nodes.tsv, edges.tsv, triples.tsv) to ensure bitwise reproducibility.

### Knowledge graph embedding

We trained three knowledge graph embedding models using PyKEEN 1.11.1 [19] on the full set of 1,822,562 triples (excluding 289 `sex_differential_expression` edges, which were added after the initial embedding training):

1. **ComplEx** [18]: Complex-valued embeddings with 200 complex dimensions (400 real parameters per entity), trained for 100 epochs on GPU with negative sampling loss. This achieved the best performance: MRR 0.2484, Hits@1 16.78%, Hits@10 40.69%, AMRI 0.9902.

2. **DistMult** [20]: Real-valued diagonal bilinear embeddings with 200 dimensions, trained for 100 epochs. An updated DistMult v4.1 model incorporating all 6 relation types (including 289 literature-curated GTEx edges) achieved MRR 0.1013, Hits@10 19.61%, AMRI 0.9909.

3. **RotatE** [21]: Rotation-based embeddings with 256 complex dimensions (512 real parameters per entity), trained for 200 epochs on CPU (GPU incompatibility with complex tensor JIT compilation on NVIDIA Blackwell GB10). RotatE v4.1 achieved MRR 0.2018, Hits@1 11.28%, Hits@10 36.77%, AMRI 0.9922, after 6.4 hours on CPU.

All models used an 80/20 train/test split with random_state=42 for reproducibility. The adjusted mean rank index (AMRI) exceeding 0.96 for all completed models, with v4 models exceeding 0.99 indicates that predictions are substantially better than random ranking across the full entity set.

---

## Technical Validation

The reliability of SexDiffKG was assessed through five complementary validation strategies: (i) external validation against published literature benchmarks, (ii) internal consistency and reproducibility audits, (iii) knowledge graph embedding model evaluation, (iv) link prediction assessment, and (v) quantitative comparison with prior versions. Together, these analyses demonstrate that SexDiffKG captures sex-differential drug safety signals with high fidelity and supports reproducible downstream analyses.

### External validation against published literature

We curated 40 benchmark drug-adverse event pairs with known sex-differential patterns from 15 or more published studies spanning cardiovascular pharmacology, psychopharmacology, endocrinology, and oncology. Each benchmark specifies an expected directional bias (female-biased or male-biased) derived from clinical trial data, meta-analyses, or systematic reviews. Of the 40 benchmarks, 29 (72.5%) were recovered in SexDiffKG with a sex-differential signal meeting the minimum reporting threshold (at least 10 reports per sex). Of these 29 recovered associations, 24 exhibited the correct directional bias, yielding a directional precision of 82.8%. Notably, zero benchmarks produced a confidently wrong-direction prediction; the 5 discordant cases arose from approximate adverse event term matching (e.g., matching "injection site swelling" rather than "peripheral oedema" for amlodipine, or "generalised oedema" rather than "peripheral oedema" for nifedipine), where the closest MedDRA Preferred Term in the knowledge graph did not precisely correspond to the benchmark phenotype. The 11 benchmarks not recovered represent drug-adverse event combinations where the specific adverse event term was absent from the knowledge graph for that drug (e.g., erythromycin with QT prolongation, morphine with respiratory depression, zolpidem with somnolence), reflecting the known under-reporting of certain well-recognized adverse effects in FAERS due to notoriety bias [22].

Several individual benchmark results merit discussion. Sotalol-torsade de pointes was recovered with a log ratio of 0.785 (ROR_female = 197.23, ROR_male = 89.97; n_female = 91, n_male = 35), consistent with the established female predisposition to drug-induced long QT syndrome arising from longer baseline QTc intervals and sex-differential cardiac ion channel expression in women [23]. Trastuzumab-ejection fraction decreased showed a particularly strong female-biased signal (log ratio = 1.805, ROR_female = 75.07, ROR_male = 12.34; n_female = 1,309, n_male = 36), consistent with the predominantly female use of this HER2-targeted agent and the known sex-differential cardiotoxicity of anthracycline-trastuzumab regimens. Tramadol-vomiting (log ratio = 0.862, ROR_female = 3.54, ROR_male = 1.49; n_female = 3,079, n_male = 727) and oxycodone hydrochloride-respiratory depression (log ratio = 0.695, ROR_female = 26.04, ROR_male = 13.00; n_female = 34, n_male = 26) both confirmed the well-documented female susceptibility to opioid adverse effects [2]. Haloperidol-torsade de pointes (log ratio = 0.897, ROR_female = 41.17, ROR_male = 16.80) and amiodarone-QT prolongation (log ratio = 0.647, ROR_female = 35.54, ROR_male = 18.60) further corroborated the female predominance in drug-induced cardiac arrhythmias.

Four case studies at the drug-class and target levels further illustrate the concordance between SexDiffKG signals and independent published evidence. First, the opioid drug class exhibited the strongest female bias among all major drug classes analysed (mean bias = 0.524 across 67 drugs, 6,555 sex-differential signals of which 75.1% were female-biased), consistent with the comprehensive review by Zucker and Prendergast (2020) [2] documenting sex differences in opioid pharmacokinetics, mu-receptor density, and pain processing. Second, the antipsychotic drug class showed pronounced female bias (mean bias = 0.454, 15 drugs, 3,292 signals, 71.0% female-biased), concordant with findings from the BeSt InTro study and related investigations of sex-differential metabolic and endocrine side effects of antipsychotic medications [24]. Third, the ESR1 (estrogen receptor alpha) target paradox -- wherein drugs targeting ESR1 showed predominantly male-biased adverse event reporting in target-level analysis -- was subsequently corroborated by the independent pharmacogenomic analysis of Ke et al. (2025; PMID: 39305475) [25], who demonstrated male-biased ESR1-related pharmacovigilance signals attributable to the specific clinical contexts in which estrogen receptor modulators (e.g., tamoxifen for male breast cancer) are prescribed to male patients. Fourth, the SRD5A (5-alpha reductase) target showed exclusively female-biased adverse events (SRD5A1 and SRD5A3 both with sex bias score = 1.0, mean log ratio = 2.585), a finding that, while seemingly paradoxical for enzymes traditionally associated with male androgen metabolism, is explained by the neurosteroid pathway: SRD5A inhibitors such as finasteride and dutasteride reduce allopregnanolone synthesis, a neuroactive steroid that potentiates GABA_A receptor signalling, and women demonstrate greater clinical sensitivity to perturbations in this neuroendocrine axis [26].

### Internal consistency and reproducibility

Three automated audit scripts were developed and executed to verify the structural integrity and reproducibility of the SexDiffKG construction pipeline. All scripts and their outputs are included in the deposited data.

The **reproducibility audit** (`audit_reproducibility.py`) verified 11 checks spanning input data availability, output file completeness, row count validation, software dependency compatibility, and end-to-end pipeline data flow. All 11 checks passed. All 87 FAERS quarterly data files (2004Q1-2025Q3) were confirmed present and accessible. The knowledge graph output files (nodes.tsv, edges.tsv, triples.tsv) were verified for structural completeness with correct column schemas (`id | name | category` for nodes; `subject | predicate | object` for edges and triples). Row counts were validated within expected ranges: 109,867 nodes, 1,822,851 edges, and 1,822,851 triples (confirming exact correspondence between the edge and triple counts). The data flow integrity from raw FAERS downloads through signal computation, molecular data integration, KG construction, and embedding training was verified at each stage.

The **data lineage audit** (`audit_data_lineage.py`) traced every entity in the knowledge graph to its provenance source and verified graph connectivity. Zero orphan entities were identified in the triple file -- that is, every entity appearing as a subject or object in at least one triple is also registered in the node file. Entities were classified by namespace: Gene entities (77,498 nodes, comprising Ensembl gene identifiers from Reactome, ChEMBL target identifiers, and gene symbols from GTEx), Protein entities (16,201 nodes, ENSP* identifiers), Drug entities (3,920 nodes, DRUG: namespace with active ingredient names), AdverseEvent entities (9,949 nodes, AE: namespace with MedDRA Preferred Terms), Pathway entities (2,279 nodes from Reactome), and Tissue entities (20 nodes from GTEx). The edge type distribution was verified: `has_adverse_event` (869,142 edges, 47.7%), `interacts_with` (473,860 edges, 26.0%), `participates_in` (370,597 edges, 20.3%), `sex_differential_adverse_event` (96,281 edges, 5.3%), `targets` (12,682 edges, 0.7%), and `sex_differential_expression` (289 edges, <0.1%).

The **number verification audit** (`verify_numbers.py`) confirmed that 6 critical numerical quantities matched the canonical `GROUND_TRUTH.json` reference file exactly: total nodes (109,867), total edges (1,822,851), total triples (1,822,851), sex-differential adverse event edges (96,281), female-biased signals (51,771), and male-biased signals (44,510). All 6 checks passed. Additionally, a comprehensive v4 audit encompassing 35 individual checks confirmed zero NaN values across all triple columns, zero NaN string literals, verified MD5 checksums for all three data files (nodes: `5a7331b1b0e7f11853444eb59e2b9166`, edges: `b8e4890c2063bdf9357c76730881b440`, triples: `2d4e46b1265a9a9bd44bbfc7372a9e44`), and consistency of reported statistics across all abstracts and documentation. Thirty-five of 36 checks passed; the single non-passing check (FAERS demo file availability) reflects a deliberate exclusion of raw patient-level data from the deposited dataset for privacy reasons.

An independent deep integrity check across 68 validation tests in 8 categories (KG structure, signal validation, embedding integrity, cross-reference audit, target analysis, cluster analysis, statistical robustness, and edge case detection) confirmed the dataset as publication-ready. The most substantive finding during this audit was a clarification regarding the logarithmic base used in sex-differential signal computation: the pipeline employs the natural logarithm, such that the sex-differential signal threshold |ln(ROR_female / ROR_male)| > 0.5 corresponds to an approximately 1.65-fold difference in reporting odds ratios between sexes.

### Knowledge graph embedding evaluation

We trained three knowledge graph embedding models on SexDiffKG v4 to evaluate the graph's suitability for representation learning and downstream inference tasks. ComplEx and DistMult used 200-dimensional embeddings trained for 100 epochs; RotatE used 256-dimensional embeddings trained for 200 epochs. ComplEx was trained on 1,822,562 triples (5 relation types, excluding sex_differential_expression), while DistMult and RotatE were trained on the full set of 1,822,851 triples (6 relation types) using the PyKEEN framework with identical training/validation/test splits.

**ComplEx** (complex-valued bilinear model) [18] achieved the best performance: mean reciprocal rank (MRR) = 0.2484, Hits@1 = 16.78%, Hits@10 = 40.69%, and adjusted mean rank index (AMRI) = 0.9902. The AMRI exceeding 0.99 indicates that the model ranks correct triples in approximately the top 0.5% of all candidates, far exceeding random expectation (AMRI = 0). The Hits@10 of 40.69% indicates that for approximately 4 in 10 test triples, the correct entity appeared among the top 10 candidate predictions.

**DistMult** (real-valued bilinear model) trained on v4 data achieved MRR = 0.0932, Hits@1 = 4.19%, Hits@10 = 18.42%, and AMRI = 0.9906. An updated DistMult v4.1 model, retrained after incorporating 289 literature-curated sex-differential expression edges (from Oliva et al. 2020 [16]), showed modest improvement: MRR = 0.1013, Hits@1 = 4.81%, Hits@10 = 19.61%, AMRI = 0.9909. This result suggests that even a small number of literature-curated sex-differential gene expression edges provides informative training signal for embedding-based inference.

The consistent performance hierarchy (ComplEx > DistMult) is expected given that ComplEx can model asymmetric and antisymmetric relations through complex-valued embeddings, an advantage for the directed relations in SexDiffKG (e.g., `Drug targets Gene` is inherently asymmetric). This ordering is consistent with prior large-scale benchmarking studies of knowledge graph embedding models [27].

Embedding quality was further verified through integrity checks: all embedding vectors were confirmed to be finite (zero NaN or Inf values), non-degenerate (no zero vectors), and structurally diverse (mean pairwise cosine similarity < 0.5 across a 5,000-entity sample, and near-duplicate rate < 0.1%), indicating that the model learned distinct representations rather than collapsing to trivial solutions.

### Link prediction assessment

To evaluate the practical utility of the trained embeddings for novel hypothesis generation, we performed comprehensive link prediction using the ComplEx v4 model. All possible `Drug -- sex_differential_adverse_event -- AdverseEvent` triples not present in the training data were scored. From 7,208 entities in the drug embedding space (including drug nodes that participate in adverse event edges beyond the 3,920 DRUG:-namespaced nodes) and 9,949 adverse event entities, a total of 71,616,111 novel candidate triples were evaluated (after excluding the 96,281 existing sex-differential adverse event edges). The complete scoring was performed in 1.5 minutes on a single GPU.

The top 500 highest-scoring novel predictions were retained for analysis. Of these, 146 (29.2%) involved drug-adverse event pairs where a non-sex-stratified `has_adverse_event` edge already existed in the knowledge graph, indicating that the model predicted a sex-differential component for a known aggregate association. The remaining 354 (70.8%) represented entirely novel drug-adverse event associations not present in any form in the training data. Prediction scores ranged from 8.63 to 15.07.

Preliminary pharmacological review of the top predictions identified several clinically interpretable associations. For example, the model predicted a sex-differential association between histrelin (a GnRH agonist) and lactation disorder (score = 12.61), which is pharmacologically plausible given the established effects of GnRH agonists on prolactin secretion and the sex-differential physiology of lactation. Other notable predictions included tramadol hydrochloride-dependence (score = 10.13, known aggregate association), cariprazine-sexual dysfunction (score = 11.00, novel), and isatuximab-cytokine release syndrome (score = 10.34, known aggregate association). A systematic evaluation of these predictions, including computation of precision at various recall thresholds and independent clinical review, is planned as a follow-up study and is beyond the scope of the present data descriptor.

### Comparison with prior versions and impact of drug normalization

The transition from SexDiffKG v3 to v4 was driven primarily by the integration of the DiAna dictionary [17] for drug name normalization. FAERS drug name fields contain free-text entries with extensive variation in formatting, spelling, brand/generic nomenclature, and multi-ingredient formulations. In v3, drug names were normalized using string-matching heuristics alone, achieving approximately 30% resolution to standardized active ingredients. In v4, the DiAna dictionary -- an open-source resource containing 846,917 FAERS-specific drug name mappings curated for pharmacovigilance applications -- was applied as the primary normalization step, achieving 53.9% total resolution (47.0% via DiAna direct matching, 6.5% via product-to-active-ingredient resolution, and 0.3% via ChEMBL identifier lookup).

This improvement in drug normalization had measurable consequences across all evaluation metrics. The knowledge graph was restructured from 126,575 nodes and 5,489,928 edges (v3) to 109,867 nodes and 1,822,851 edges (v4), reflecting the consolidation of redundant drug entities that were previously treated as distinct due to name variation, as well as the removal of NaN-containing and duplicate triples. The benchmark validation precision improved from 63.3% (19/30 correct direction in v3) to 82.8% (24/29 correct direction in v4), an improvement of 19.5 percentage points. This gain is directly attributable to more accurate drug entity resolution: several benchmarks that failed in v3 due to drug name mismatches were correctly resolved through DiAna normalization. Coverage changed from 75.0% (30/40 found in v3) to 72.5% (29/40 found in v4), reflecting that stricter normalization excluded some marginal matches while substantially improving the accuracy of retained matches.

Embedding model performance also improved between versions. Comparing DistMult models trained under identical hyperparameters (200 dimensions, 100 epochs), MRR increased from 0.0476 (v3) to 0.0932 (v4), a 1.96-fold improvement, while Hits@10 increased from 8.85% to 18.42% (2.08-fold). The ComplEx v4 model (MRR = 0.2484) represents a 5.2-fold improvement in MRR over the DistMult v3 baseline, attributable to both the superior model architecture and the cleaner entity space resulting from improved drug normalization. AMRI improved from 0.9807 (v3) to 0.9902 (ComplEx v4), indicating that correct triples moved from the top 1.9% to the top 0.5% of candidate rankings.

### Temporal validation

To assess the stability of sex-differential signals over time, we performed a temporal validation by splitting FAERS reports based on event date into a training period (2004Q1-2020Q4) and a test period (2021Q1-2025Q3). Of the 14,536,008 deduplicated reports, 7,469,135 (51.4%) had valid event dates, yielding 5,239,086 training reports (female: 3,140,479; male: 2,098,607) and 2,230,049 test reports (female: 1,324,159; male: 905,890). The female proportion was stable across periods (59.9% vs 59.4%).

The training period yielded 38,884 strong sex-differential signals and the test period yielded 13,125 strong signals. Among 3,350 drug-AE pairs that were strong in both periods, 84.0% (2,815) maintained the same sex-bias direction, demonstrating robust temporal stability. In a relaxed analysis including all 8,108 training-strong signals present in the test period at any threshold, 72.6% (5,888) maintained directional consistency. The Pearson correlation between training and test log(ROR ratios) across 33,786 shared pairs was r = 0.384 (p < 1e-100), indicating moderate preservation of effect magnitude. Notably, 9,775 novel strong signals appeared only in the test period, demonstrating that the 2021-2025 FAERS data contributes genuinely new sex-differential information.

### Statistical significance of sex-differential patterns

We performed comprehensive statistical testing to evaluate the significance of observed sex differences at multiple levels of analysis.

**Signal-level analysis.** The 53.8% female predominance among 96,281 sex-differential signals was highly significant (binomial test, p = 3.5 x 10^-121). However, the effect size was small (Cohen's h = 0.076). Notably, this female proportion (53.8%) was significantly lower than the 60.2% female proportion in the underlying FAERS reports, indicating that the signal detection pipeline does not amplify the reporting sex ratio.

**Drug class analysis.** All 18 major drug classes tested showed statistically significant sex bias after Benjamini-Hochberg FDR correction (q < 0.05). The largest effects were observed for opioid analgesics (Cohen's h = 0.526; 4,923 female-biased vs 1,632 male-biased signals), immune checkpoint inhibitors (h = 0.463), and antipsychotics (h = 0.433). Three classes showed male-biased patterns: SSRIs (h = -0.165), anticonvulsants (h = -0.049), and insulins (h = -0.065).

**Pathway enrichment analysis.** Gene targets of drugs with sex-differential ADR profiles were mapped to Reactome pathways via the `targets` and `participates_in` edges. Fisher exact tests with FDR correction identified 79 significantly enriched pathways: 32 enriched for female-biased drug targets and 47 enriched for male-biased drug targets (FDR q < 0.05). Female-enriched pathways were dominated by extracellular matrix and collagen biology (collagen degradation, CLEC7A/Dectin-1 signaling, ECM proteoglycans), immune signaling (FCERI-mediated NF-kB activation, downstream TCR signaling, interleukin-1 signaling), and ubiquitin-proteasome pathways. Male-enriched pathways concentrated in ion channel and neurotransmitter signaling (voltage-gated potassium channels, NOTCH3 signaling), interleukin signaling (IL-12, IL-20, IL-23, IL-27), and metabolic regulation (insulin processing, retinoic acid signaling, detoxification of reactive oxygen species).

**Target-level analysis.** Among 74 moderately biased gene targets (|bias score| >= 0.3, >= 3 drugs), none reached individual significance under 10,000-iteration permutation testing after FDR correction, reflecting the limited statistical power of 3-14 drugs per target. These target-level results should therefore be considered hypothesis-generating rather than confirmatory, though the convergent pathway enrichment provides aggregate statistical support.

### Summary

Taken together, these validation analyses establish that SexDiffKG (i) recovers known sex-differential drug safety signals from the published literature with 82.8% directional precision across 40 curated benchmarks, (ii) maintains full internal consistency with zero NaN values, zero orphan entities in the triple file, and verified MD5 checksums for all data files, (iii) supports effective representation learning with embedding models achieving MRR up to 0.2484 and AMRI exceeding 0.99, (iv) enables link prediction across 71.6 million novel candidate triples for hypothesis generation, and (v) demonstrates measurable improvement over prior versions attributable to principled drug name normalization using the DiAna dictionary. These results collectively support the use of SexDiffKG as a reliable and reproducible resource for sex-aware computational pharmacovigilance.

---

## Data Records

All SexDiffKG data, code, and pre-trained embeddings are deposited in two repositories:

**Zenodo** (DOI: 10.5281/zenodo.18819192): Archived dataset containing all knowledge graph files, pre-computed signals, embedding weights, and analysis outputs. The deposit includes the following files:

| File | Format | Size | Description |
|------|--------|------|-------------|
| `data/kg_v4/nodes.tsv` | TSV | ~3.6 MB | Node table: 109,867 entities with id, name, and category columns |
| `data/kg_v4/edges.tsv` | TSV | ~68 MB | Edge table: 1,822,851 relationships with subject, predicate, and object columns |
| `data/kg_v4/triples.tsv` | TSV | ~55 MB | PyKEEN-compatible triple file (headerless, tab-delimited) |
| `data/kg_v4/data_dictionary.json` | JSON | ~15 KB | Machine-readable schema definitions for all columns, entity types, and relation types |
| `results/signals_v4/` | Parquet | ~45 MB | Sex-stratified ROR values and sex-differential signals for all 254,114 drug-AE comparisons |
| `results/kg_embeddings_v4/` | PyTorch | ~360 MB | Pre-trained ComplEx and DistMult model weights with entity/relation mappings |
| `results/link_predictions/` | TSV+JSON | ~2 MB | Top 500 novel sex-differential drug-AE predictions from ComplEx link prediction |
| `results/analysis/` | JSON | ~1 MB | Validation benchmarks, statistical tests, and audit outputs |
| `GROUND_TRUTH.json` | JSON | ~5 KB | Canonical counts and checksums for reproducibility verification |

**GitHub** (github.com/jshaik369/SexDiffKG): Version-controlled repository containing all pipeline scripts (Python), analysis notebooks, publication documents, and the knowledge graph data files. The repository is structured as follows:

```
sexdiffkg/
  data/
    kg_v4/          # Canonical KG (nodes.tsv, edges.tsv, triples.tsv, data_dictionary.json)
    raw/            # Source data download scripts
    processed/      # Intermediate processing outputs
  scripts/          # Reproducible pipeline (v4_01 through v4_10)
  results/          # Analysis outputs, embeddings, predictions
  Publication/      # Manuscript and supplementary materials
  GROUND_TRUTH.json # Canonical verification checksums
```

### Node schema

The `nodes.tsv` file contains three columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | string | Unique entity identifier with namespace prefix | `DRUG:metformin`, `AE:Nausea`, `GENE:ESR1` |
| `name` | string | Human-readable entity name | `metformin`, `Nausea`, `ESR1` |
| `category` | string | Entity type (one of 6 categories) | `Drug`, `AdverseEvent`, `Gene` |

Entity identifiers use namespace prefixes to prevent collisions: `DRUG:` (3,920 drugs), `AE:` (9,949 adverse events), `GENE:` (77,498 genes), `PROTEIN:` (16,201 proteins), `PATHWAY:` (2,279 pathways), `TISSUE:` (20 tissues).

### Edge schema

The `edges.tsv` file contains three columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `subject` | string | Source entity identifier | `DRUG:metformin` |
| `predicate` | string | Relation type (one of 6 types) | `sex_differential_adverse_event` |
| `object` | string | Target entity identifier | `AE:Lactic acidosis` |

### Relation types

| Relation | Count | Source | Subject Type | Object Type |
|----------|-------|--------|--------------|-------------|
| `has_adverse_event` | 869,142 | FAERS ROR | Drug | AdverseEvent |
| `interacts_with` | 473,860 | STRING v12.0 | Protein | Protein |
| `participates_in` | 370,597 | Reactome | Gene | Pathway |
| `sex_differential_adverse_event` | 96,281 | FAERS sex-stratified | Drug | AdverseEvent |
| `targets` | 12,682 | ChEMBL 36 | Drug | Gene |
| `sex_differential_expression` | 289 | GTEx v8 | Gene | Tissue |

### Signal data

The sex-differential signals file (`results/signals_v4/sex_differential_v4.parquet`) contains the following columns for each of the 96,281 sex-differential drug-AE pairs (from 254,114 total comparisons meeting the minimum reporting threshold):

| Column | Description |
|--------|-------------|
| `drug_name` | Normalized active ingredient name |
| `adverse_event` | MedDRA Preferred Term for adverse event |
| `ror_female` | Female-specific reporting odds ratio |
| `ror_male` | Male-specific reporting odds ratio |
| `n_female` | Number of female reports for this drug-AE pair |
| `n_male` | Number of male reports for this drug-AE pair |
| `log_ratio` | ln(ROR_female / ROR_male); positive = female-biased |
| `direction` | "female" or "male" indicating bias direction |

### Embedding data

Pre-trained knowledge graph embeddings are provided in PyTorch format:

| Model | File | Entities | Relations | Dimensions | Best Metric |
|-------|------|----------|-----------|------------|-------------|
| ComplEx | `results/kg_embeddings_v4/ComplEx/model.pt` | 113,012 | 5 | 200 complex (400 real) | MRR 0.2484 |
| DistMult | `results/kg_embeddings_v4/DistMult_v41/model.pt` | 113,155 | 6 | 200 real | MRR 0.1013 |

Entity-to-index and relation-to-index mappings are provided alongside each model for downstream use. The ComplEx model was trained on 5 relation types (excluding `sex_differential_expression`); the DistMult v4.1 model was trained on all 6 relation types including the 289 literature-curated sex-differential expression edges.

---

## Usage Notes

SexDiffKG is designed for multiple research applications:

### Sex-differential ADR discovery

The primary use case is identifying drug-adverse event pairs with significant sex differences in reporting. Researchers can query the `sex_differential_adverse_event` edges to find drugs with disproportionate female or male ADR burden. The `log_ror_ratio` in the signals file quantifies the magnitude of sex difference, enabling ranking of signals by effect size. For example, opioid analgesics exhibit the strongest female bias (mean log_ror_ratio = +0.524, corresponding to 3.0-fold higher female ROR), while SSRIs show modest male bias (mean log_ror_ratio = -0.189).

### Link prediction for novel hypotheses

The pre-trained ComplEx embeddings can be used for link prediction to discover novel sex-differential drug-AE associations not present in the training data. We demonstrate this by scoring all 71.6 million possible (Drug, sex_differential_adverse_event, AE) triples not in the existing graph, identifying 500 top-ranked predictions. The top predictions include clinically plausible associations such as tramadol hydrochloride-dependence (score = 10.13), cariprazine-sexual dysfunction (score = 11.00), and isatuximab-cytokine release syndrome (score = 10.34), several of which have emerging literature support.

### Target-level sex bias analysis

By traversing the graph from sex-differential drug-AE edges through drug-target edges, researchers can identify biological targets with systematic sex bias in their associated ADR profiles. Our analysis of 767 gene targets reveals 317 with directional sex bias, including paradoxical findings such as ESR1 (estrogen receptor alpha) showing male-biased ADRs and AR (androgen receptor) showing female-biased ADRs, patterns that are biologically interpretable through cross-sex pharmacological vulnerability mechanisms.

### Drug safety benchmarking

The 40 literature-derived benchmarks provided in `results/analysis/validation_40_benchmarks_v4.json` can serve as a standard evaluation set for computational models of sex-differential drug response. Researchers developing new pharmacovigilance methods can compare their predictions against these curated benchmarks.

### Integration with existing KGs

SexDiffKG uses standard TSV format and namespace-prefixed identifiers that facilitate integration with other biomedical knowledge graphs. The STRING protein identifiers, ChEMBL drug-target mappings, and Reactome pathway identifiers provide natural join points with resources such as PrimeKG, Hetionet, and SPOKE. The `sex_differential_adverse_event` and `sex_differential_expression` edge types are unique to SexDiffKG and can augment any existing KG with sex-stratified information.

### Limitations

Users should be aware of the following limitations:

1. **Reporting bias**: FAERS is a spontaneous reporting system subject to stimulated reporting, notoriety bias, and under-reporting. ROR values reflect disproportionality in reporting, not causal risk.

2. **Drug normalization**: Despite the multi-tier normalization pipeline achieving 53.9% active-ingredient resolution, 46.1% of drug entries remain at the cleaned-string level, potentially fragmenting signals across variant names for the same compound.

3. **Sex as binary**: FAERS records sex as female/male only. Non-binary gender identities, intersex conditions, and the distinction between sex and gender are not captured. Trans individuals receiving hormone therapy may be miscategorized relative to their hormonal environment.

4. **Temporal confounding**: Reporting practices, drug availability, and diagnostic criteria have evolved over the 21-year span (2004-2025). While temporal validation demonstrates signal stability, some historical signals may not reflect current clinical practice.

5. **Missing data integration**: Several relevant data sources (IMPPAT, NPASS, TCMSP, CTD) are referenced but not yet integrated. The GTEx sex-differential expression layer is literature-curated (289 edges compiled from Oliva et al. 2020) and sparse compared to the pharmacovigilance layers.

6. **Embedding gap**: The 289 `sex_differential_expression` edges were added after ComplEx embedding training and are not represented in the ComplEx pre-trained model; they are included in the DistMult v4.1 model.

7. **Cross-layer identifier heterogeneity**: Gene nodes in SexDiffKG use three different identifier schemes depending on their data source: Ensembl gene IDs (ENSG*) from Reactome pathway annotations, ChEMBL target names from drug-target binding data, and gene symbols from GTEx sex-differential expression data. This means the same biological gene may appear as multiple distinct nodes, and cross-layer graph traversals (e.g., drug -> target gene -> pathway) require external identifier mapping not currently embedded in the graph structure. A forthcoming v4.2 release will unify all gene identifiers to Ensembl gene IDs via UniProt cross-references.

8. **No gene-to-protein mapping edges**: The current graph does not include explicit edges linking Gene nodes (ENSG*) to their corresponding Protein nodes (ENSP* from STRING). The protein-protein interaction layer (473,860 edges) is therefore not directly reachable from drug-target or pathway annotations via graph traversal. Adding `encodes_for` edges via Ensembl gene-to-protein mappings is planned for v4.2.

9. **Literature-curated GTEx layer**: The 289 sex-differential expression edges were curated from published findings in Oliva et al. 2020, not computed de novo from raw GTEx per-sample expression data. While the curated genes are pharmacologically relevant (drug-metabolizing enzymes, hormone receptors, sex-chromosome genes), this layer represents a small fraction of the approximately 13,000 sex-biased genes reported by Oliva et al. across 44 tissues. Future versions will incorporate genome-wide sex-differential expression computed directly from GTEx per-sample data.

---

## Code Availability

All analysis code is available in the GitHub repository (github.com/jshaik369/SexDiffKG) under the MIT License. The pipeline consists of numbered Python scripts (v4_01 through v4_10) that reproduce the full workflow from raw FAERS data through knowledge graph construction, embedding training, and downstream analysis:

| Script | Description |
|--------|-------------|
| `v4_01_normalize_diana.py` | Drug name normalization with DiAna dictionary |
| `v4_02_compute_signals.py` | Sex-stratified ROR computation and signal detection |
| `v4_03_build_kg.py` | Knowledge graph construction from 6 data sources |
| `v4_04_train_distmult.py` | DistMult embedding training (PyKEEN) |
| `v4_05_train_rotatE.py` | RotatE embedding training (PyKEEN) |
| `v4_08_link_prediction.py` | ComplEx-based link prediction for novel ADR discovery |
| `v4_09_statistical_tests.py` | Statistical significance testing (binomial, Fisher, permutation) |
| `v4_10_temporal_validation.py` | Temporal train/test split validation |

Dependencies are specified in `requirements.txt` and `environment.yml`. A `Dockerfile` is provided for containerized reproduction. The ground truth file (`GROUND_TRUTH.json`) contains canonical counts and MD5 checksums for verification.

---

## Figure Legends

**Figure 1. SexDiffKG schema and data integration architecture.** The knowledge graph integrates six data sources into a heterogeneous graph with six node types and six relation types. **(a)** Schema diagram showing the six node types (Drug, n = 3,920; AdverseEvent, n = 9,949; Gene, n = 77,498; Protein, n = 16,201; Pathway, n = 2,279; Tissue, n = 20) and six edge types connecting them: `has_adverse_event` (Drug-AdverseEvent, 869,142 edges), `sex_differential_adverse_event` (Drug-AdverseEvent, 96,281 edges), `targets` (Drug-Gene, 12,682 edges), `interacts_with` (Protein-Protein, 473,860 edges), `participates_in` (Gene-Pathway, 370,597 edges), and `sex_differential_expression` (Gene-Tissue, 289 edges). Node sizes are proportional to the logarithm of node counts. **(b)** Data flow diagram illustrating the construction pipeline. Raw FAERS quarterly files (87 quarters, 2004Q1-2025Q3) are deduplicated to 14,536,008 reports, drug names are normalized via the DiAna dictionary (846,917 mappings, 53.9% resolution), and sex-stratified reporting odds ratios are computed to yield 254,114 drug-AE comparisons, of which 96,281 meet the sex-differential threshold (|ln(ROR_F/ROR_M)| >= 0.5). Molecular layers (STRING, ChEMBL, Reactome, GTEx) are integrated to produce the final knowledge graph of 109,867 nodes and 1,822,851 edges. **(c)** Edge type distribution as a stacked bar chart, showing the proportional contribution of each relation type to the total edge count: `has_adverse_event` (47.7%), `interacts_with` (26.0%), `participates_in` (20.3%), `sex_differential_adverse_event` (5.3%), `targets` (0.7%), and `sex_differential_expression` (<0.1%).

**Figure 2. Distribution of sex-differential pharmacovigilance signals.** Volcano plot showing the 96,281 sex-differential drug-adverse event signals. The x-axis represents the log ROR ratio (ln(ROR_female / ROR_male)); positive values indicate female-biased signals and negative values indicate male-biased signals. The y-axis represents -log10(p-value) from the chi-squared test of independence between sex and the drug-AE pair. Vertical dashed lines mark the sex-differential threshold at |log_ror_ratio| = 0.5. Points are colored by bias direction: red for female-biased signals (n = 51,771, 53.8%) and blue for male-biased signals (n = 44,510, 46.2%). The overall female predominance is statistically significant (binomial test, p = 3.5 x 10^-121; Cohen's h = 0.076). Notable outlier signals are labeled, including sotalol-torsade de pointes (log ratio = 0.785, female-biased), trastuzumab-ejection fraction decreased (log ratio = 1.805, female-biased), and olanzapine-abnormal weight gain (log ratio = 1.899, female-biased). The marginal density distributions along each axis illustrate the near-symmetric but slightly female-skewed distribution of effect sizes.

**Figure 3. Drug class sex bias comparison across 18 therapeutic classes.** Horizontal bar chart ranking 18 major drug classes by Cohen's h effect size quantifying the magnitude of sex bias in their associated sex-differential signals. Bar color indicates the direction of bias: red bars denote female-biased classes and blue bars denote male-biased classes. For each class, the bar length corresponds to Cohen's h (absolute value), and the number of sex-differential signals is annotated in parentheses. The most strongly female-biased classes are opioid analgesics (h = 0.526, 6,555 signals), immune checkpoint inhibitors (h = 0.463, 1,012 signals), and antipsychotics (h = 0.433, 3,292 signals). Three classes show statistically significant male bias: SSRIs (h = -0.165, 2,037 signals), insulins (h = -0.065, 1,131 signals), and anticonvulsants (h = -0.049, 2,649 signals). All 18 classes are significant after Benjamini-Hochberg FDR correction (q < 0.05). Asterisks indicate statistical significance: *** for q < 0.001, ** for q < 0.01, * for q < 0.05. Error bars represent 95% confidence intervals for the proportion of female-biased signals.

**Figure 4. Age-sex interaction in adverse drug reaction reporting.** Line chart showing the percentage of female-biased signals across three age groups (Young Adult: 18-44 years; Middle-Aged: 45-64 years; Elderly: 65+ years) for six representative drug classes. **(a)** Opioid analgesics show a pronounced age-dependent decline in female bias, from 87.8% female-biased in young adults (mean log ratio = 1.136) to 56.8% in middle-aged (mean log ratio = 0.217) to 39.8% in elderly patients (mean log ratio = -0.098), consistent with age-related convergence of pharmacokinetic sex differences. **(b)** Antipsychotics exhibit a similar pattern, declining from 71.1% female-biased in young adults to 40.4% in the elderly. **(c)** SSRIs shift from near-parity in young adults (52.4% female-biased) to distinctly male-biased in the elderly (32.5% female-biased), reflecting the increased vulnerability of elderly men to SSRI-related adverse effects including hyponatremia. **(d)** ACE inhibitors maintain female bias across all age groups but with decreasing magnitude (67.9% to 64.2%). **(e)** Statins show a non-monotonic pattern, with near-parity in young adults (50.9%), male bias in middle-aged (38.6%), and a reversal to female bias in the elderly (56.5%). **(f)** Across all drug classes, the overall proportion of female-biased signals declines from 63.2% in young adults (n = 20,458 strong signals) to 52.1% in middle-aged (n = 31,322) to 49.3% in the elderly (n = 30,983), consistent with the attenuation of hormonal and pharmacokinetic sex differences with advancing age.

**Figure 5. Geographic variation in sex-differential adverse event reporting across 15 countries.** **(a)** Bar chart showing the percentage of female-biased among strong sex-differential signals for 15 countries reporting the most FAERS data. Japan exhibits the highest female-biased proportion (57.4%, 1,485 of 2,586 strong signals), followed by Spain (52.4%), China (51.0%), India (51.1%), and the United States (50.8%). Canada shows the lowest female-biased proportion (34.2%, 7,973 of 23,344 strong signals), followed by Brazil (30.0%) and Colombia (35.5%). The red dashed horizontal line marks 50% (no sex bias). **(b)** Scatter plot showing the correlation between country-specific sex-differential signals and those of the United States, for each country with at least 500 shared drug-AE pairs. Pearson correlations range from r = 0.118 (Italy) to r = 0.391 (unspecified country), with the US-Japan correlation at r = 0.204 (n = 7,056 shared pairs). Japan is the only major reporting country where males constitute a majority of FAERS reports (47.0% female vs 53.0% male), potentially reflecting differences in reporting culture and healthcare access patterns. **(c)** Bar chart showing absolute report counts by country, with bars subdivided by sex, illustrating that the United States dominates FAERS reporting (9,934,811 reports, 68.3% of total), followed by Canada (573,932), the United Kingdom (491,181), France (416,996), and Japan (412,316).

**Figure 6. Knowledge graph embedding evaluation and link prediction performance.** **(a)** Bar chart comparing three embedding models trained on SexDiffKG: ComplEx v4 (MRR = 0.2484, Hits@1 = 16.78%, Hits@10 = 40.69%), RotatE v4.1 (MRR = 0.2018, Hits@1 = 11.28%, Hits@10 = 36.77%), DistMult v4.1 (MRR = 0.1013, Hits@1 = 4.81%, Hits@10 = 19.61%), DistMult v4 (MRR = 0.0932, Hits@1 = 4.19%, Hits@10 = 18.42%), and DistMult v3 baseline (MRR = 0.0476, Hits@1 = 2.25%, Hits@10 = 8.85%). The ComplEx v4 model achieves a 5.2-fold improvement in MRR over the v3 baseline. **(b)** Adjusted Mean Rank Index (AMRI) comparison showing that all models exceed 0.98 (ComplEx v4: 0.9902, DistMult v4: 0.9906, DistMult v4.1: 0.9909, DistMult v3: 0.9807), indicating that true triples are ranked in the top 0.5-2% of all candidates. **(c)** Score distribution histogram for the 500 top-ranked novel sex-differential drug-AE predictions from ComplEx link prediction, showing scores ranging from 8.63 to 15.07. The distribution of predictions by novelty type is shown as inset: 146 (29.2%) involve known aggregate drug-AE associations predicted to have a sex-differential component, and 354 (70.8%) represent entirely novel drug-AE predictions. **(d)** Scatter plot comparing DistMult v4 versus DistMult v4.1 (with GTEx sex-differential expression edges) performance across MRR, Hits@1, and Hits@10, demonstrating the modest but consistent improvement from incorporating 289 literature-curated sex-differential expression edges (MRR: 0.0932 to 0.1013, Hits@10: 18.42% to 19.61%).

---

## Tables

**Table 1. Data sources integrated in SexDiffKG v4.**

| Data source | Version | License | Records contributed | Edge type(s) | Description |
|-------------|---------|---------|---------------------|--------------|-------------|
| FDA FAERS | 2004Q1-2025Q3 | Public Domain | 14,536,008 reports; 869,142 + 96,281 edges | `has_adverse_event`, `sex_differential_adverse_event` | Sex-stratified spontaneous adverse event reports; 87 quarterly releases |
| STRING | v12.0 | CC-BY 4.0 | 473,860 edges | `interacts_with` | Human protein-protein interactions at combined score >= 700 |
| ChEMBL | 36 | CC-BY-SA 3.0 | 12,682 edges | `targets` | Drug-target binding interactions |
| Reactome | 2026-02 | CC-BY 4.0 | 370,597 edges | `participates_in` | Gene-pathway membership (Homo sapiens) |
| GTEx | v8 (Oliva et al. 2020, curated) | Open Access | 289 edges | `sex_differential_expression` | Literature-curated tissue-level sex-differential gene expression |
| DiAna dictionary | 2025 | Open Source | 846,917 mappings | (normalization) | FAERS drug name-to-active ingredient mappings; 53.9% resolution |

**Table 2. SexDiffKG v4 knowledge graph statistics.**

| Node type | Count | Identifier format | Example |
|-----------|-------|-------------------|---------|
| Gene | 77,498 | ENSG* (Ensembl) | ENSG00000091831 (ESR1) |
| Protein | 16,201 | ENSP* (STRING) | ENSP00000206249 |
| AdverseEvent | 9,949 | AE: + MedDRA PT | AE:Nausea |
| Drug | 3,920 | DRUG: + active ingredient | DRUG:metformin |
| Pathway | 2,279 | PATHWAY: + Reactome name | PATHWAY:Collagen biosynthesis |
| Tissue | 20 | TISSUE: + GTEx tissue | TISSUE:Liver |
| **Total nodes** | **109,867** | | |

| Edge type | Count | Percentage | Source domain | Target domain |
|-----------|-------|------------|--------------|---------------|
| has_adverse_event | 869,142 | 47.7% | Drug | AdverseEvent |
| interacts_with | 473,860 | 26.0% | Protein | Protein |
| participates_in | 370,597 | 20.3% | Gene | Pathway |
| sex_differential_adverse_event | 96,281 | 5.3% | Drug | AdverseEvent |
| targets | 12,682 | 0.7% | Drug | Gene |
| sex_differential_expression | 289 | <0.1% | Gene | Tissue |
| **Total edges** | **1,822,851** | **100%** | | |

**Table 3. FAERS demographics summary.**

| Statistic | Value |
|-----------|-------|
| Total deduplicated reports | 14,536,008 |
| Female reports | 8,744,397 (60.2%) |
| Male reports | 5,791,611 (39.8%) |
| Quarterly releases covered | 87 (2004Q1-2025Q3) |
| Reports with valid age | 9,137,988 (62.9%) |
| Reports with valid country | 13,910,089 (95.7%) |
| Young adult reports (18-44 yr) | 1,856,734 (F: 1,238,054; M: 618,680) |
| Middle-aged reports (45-64 yr) | 3,063,407 (F: 1,875,487; M: 1,187,920) |
| Elderly reports (65+ yr) | 3,421,962 (F: 1,919,378; M: 1,502,584) |
| Top reporting country | United States (9,934,811; 68.3%) |
| Total drug-AE comparisons (min 10/sex) | 254,114 |
| Sex-differential signals (|log ratio| >= 0.5) | 96,281 (51,771 female-biased; 44,510 male-biased) |
| Unique drugs in signals | 2,178 |
| Unique adverse events in signals | 5,069 |

**Table 4. Drug name normalization pipeline performance.**

| Normalization step | Method | Match rate | Cumulative resolution | Description |
|--------------------|--------|------------|----------------------|-------------|
| DiAna dictionary | Direct lookup | 47.0% | 47.0% | 846,917 FAERS-specific drug name mappings |
| prod_ai field | FDA curated | 6.5% | 53.5% | Active ingredient from FAERS product field |
| ChEMBL synonym | Database lookup | 0.3% | 53.9% | ChEMBL 36 molecule synonym matching |
| String cleaning | Heuristic | 40.7% | 94.5% (cleaned) | Uppercase, dosage removal, abbreviation standardization |
| Unresolved | -- | 5.5% | -- | Names not resolved by any method |
| **Total active-ingredient resolution** | | **53.9%** | | From ~710,000 unique raw drug names to ~301,000 normalized |

**Table 5. Sex-differential signal summary.**

| Metric | Value |
|--------|-------|
| Total drug-AE comparisons (>= 10 reports/sex) | 254,114 |
| Sex-differential edges in KG (|log ratio| >= 0.5) | 96,281 |
| Female-biased edges | 51,771 (53.8%) |
| Male-biased edges | 44,510 (46.2%) |
| Unique drugs with sex-differential edges | 2,178 |
| Unique adverse events with sex-differential edges | 5,069 |
| Sex-differential threshold | |ln(ROR_F/ROR_M)| >= 0.5 (~1.65-fold difference) |
| Minimum reports per sex | 10 |
| Female predominance significance | p = 3.5 x 10^-121 (binomial test) |
| Cohen's h (female excess) | 0.076 (small effect size) |

**Table 6. Validation against 40 literature benchmarks.**

| Metric | v4 (DiAna) | v3 (heuristic) | Change |
|--------|-----------|----------------|--------|
| Total benchmarks | 40 | 40 | -- |
| Benchmarks found | 29 (72.5%) | 30 (75.0%) | -2.5 pp |
| Correct direction | 24 (82.8%) | 19 (63.3%) | +19.5 pp |
| Wrong direction | 5 (17.2%) | 11 (36.7%) | -19.5 pp |
| Not found | 11 (27.5%) | 10 (25.0%) | +2.5 pp |

Representative validated benchmarks (v4):

| Drug | Adverse event | Expected | Observed | log_ror_ratio | ROR_F | ROR_M | n_F | n_M |
|------|---------------|----------|----------|---------------|-------|-------|-----|-----|
| Sotalol | Torsade de pointes | F>M | F>M | 0.785 | 197.23 | 89.97 | 91 | 35 |
| Trastuzumab | Ejection fraction decreased | F>M | F>M | 1.805 | 75.07 | 12.34 | 1,309 | 36 |
| Tramadol | Vomiting | F>M | F>M | 0.862 | 3.54 | 1.49 | 3,079 | 727 |
| Haloperidol | Torsade de pointes | F>M | F>M | 0.897 | 41.17 | 16.80 | 94 | 44 |
| Amiodarone | QT prolongation | F>M | F>M | 0.647 | 35.54 | 18.60 | 500 | 394 |
| Olanzapine | Abnormal weight gain | F>M | F>M | 1.899 | 17.83 | 2.67 | 76 | 118 |
| Aripiprazole | Hyperprolactinaemia | F>M | F>M | 1.548 | 47.95 | 10.19 | 237 | 184 |
| Oxycodone HCl | Respiratory depression | F>M | F>M | 0.695 | 26.04 | 13.00 | 34 | 26 |
| Isoniazid | Cholestatic liver injury | F>M | F>M | 0.907 | 55.99 | 22.61 | 16 | 10 |
| Denosumab | Spinal fracture | F>M | F>M | 0.744 | 16.69 | 7.93 | 2,006 | 108 |

**Table 7. Knowledge graph embedding model comparison.**

| Model | KG version | Dimensions | Epochs | MRR | Hits@1 | Hits@10 | AMRI | Device | Status |
|-------|-----------|-----------|--------|-----|--------|---------|------|--------|--------|
| ComplEx v4 | v4 | 200 complex (400 real) | 100 | **0.2484** | **16.78%** | **40.69%** | 0.9902 | GPU | Complete |
| DistMult v4.1 | v4.1 | 200 real | 100 | 0.1013 | 4.81% | 19.61% | 0.9909 | GPU | Complete |
| DistMult v4 | v4 | 200 real | 100 | 0.0932 | 4.19% | 18.42% | 0.9906 | GPU | Complete |
| DistMult v3 | v3 | 200 real | 100 | 0.0476 | 2.25% | 8.85% | 0.9807 | GPU | Complete (baseline) |
| RotatE v4.1 | v4.1 | 256 complex | 200 | 0.2018 | 11.28% | 36.77% | 0.9922 | CPU | Complete |

All models used an 80/20 train/test split with random_state=42, PyKEEN 1.11.1 framework. ComplEx v4 achieves a 5.2-fold MRR improvement over DistMult v3 baseline. AMRI > 0.96 for all models; higher values indicate correct triples ranked near the top of all candidates.

**Table 8. Top 20 sex-differential drug-AE link predictions from ComplEx v4.**

*Known aggregate associations predicted to have sex-differential component:*

| Rank | Drug | Adverse event | Score | Drug edges |
|------|------|---------------|-------|------------|
| 1 | Thiotepa | Venoocclusive disease | 10.49 | 441 |
| 2 | Isatuximab | Cytokine release syndrome | 10.34 | 251 |
| 3 | Polatuzumab vedotin | Myelosuppression | 10.28 | 401 |
| 4 | Gemcitabine HCl | Myelosuppression | 10.18 | 315 |
| 5 | Tramadol HCl | Dependence | 10.13 | 555 |
| 6 | Cannabis spp | Dependence | 10.12 | 445 |
| 7 | Fludarabine | Enterococcal infection | 10.02 | 1,408 |
| 8 | Brolucizumab | Maculopathy | 9.99 | 224 |
| 9 | Clonazepam | Dystonia | 9.91 | 2,318 |
| 10 | Alteplase | Cerebellar haemorrhage | 9.81 | 458 |

*Entirely novel drug-AE predictions:*

| Rank | Drug | Adverse event | Score | Drug edges |
|------|------|---------------|-------|------------|
| 1 | Codeine/Promethazine | Lung carcinoma stage IV | 14.14 | 58 |
| 2 | Sulfur hexafluoride | Infusion site extravasation | 11.88 | 127 |
| 3 | Cariprazine | Sexual dysfunction | 11.00 | 361 |
| 4 | Benzoyl peroxide/Clindamycin | Application site vesicles | 10.98 | 52 |
| 5 | Avibactam/Ceftazidime | Mechanical ventilation | 10.60 | 79 |
| 6 | Selumetinib | Peritonitis bacterial | 10.56 | 52 |
| 7 | Carmustine | Immune effector neurotoxicity | 10.09 | 268 |
| 8 | Nelarabine | Cytokine release syndrome | 10.05 | 81 |
| 9 | Azacitidine | Cytokine release syndrome | 9.99 | 920 |
| 10 | Brolucizumab | Ulcerative keratitis | 9.94 | 224 |

**Table 9. Drug class sex bias analysis (18 classes, ranked by Cohen's h).**

| Drug class | N drugs | N signals | F-biased | M-biased | % F-biased | Mean bias | Cohen's h | FDR q-value | Direction |
|------------|---------|-----------|----------|----------|------------|-----------|-----------|-------------|-----------|
| Opioids | 67 | 6,555 | 4,923 | 1,632 | 75.1% | 0.524 | 0.526 | <1e-100 | Female |
| Checkpoint Inhibitors | 6 | 1,012 | 732 | 280 | 72.3% | 0.396 | 0.463 | 8.7e-47 | Female |
| Antipsychotics | 15 | 3,292 | 2,337 | 955 | 71.0% | 0.454 | 0.433 | 3.3e-131 | Female |
| ACE Inhibitors | 27 | 2,298 | 1,607 | 691 | 69.9% | 0.420 | 0.410 | 8.4e-83 | Female |
| Corticosteroids | 51 | 5,110 | 3,555 | 1,555 | 69.6% | 0.408 | 0.402 | 9.6e-176 | Female |
| Anticoagulants | 13 | 2,460 | 1,678 | 782 | 68.2% | 0.278 | 0.373 | 5.8e-74 | Female |
| Benzodiazepines | 9 | 2,096 | 1,369 | 727 | 65.3% | 0.266 | 0.311 | 7.1e-45 | Female |
| PPIs | 18 | 3,937 | 2,538 | 1,399 | 64.5% | 0.256 | 0.294 | 5.5e-74 | Female |
| Oral Antidiabetics | 29 | 1,969 | 1,243 | 726 | 63.1% | 0.212 | 0.266 | 2.4e-31 | Female |
| Beta Blockers | 18 | 2,649 | 1,650 | 999 | 62.3% | 0.186 | 0.248 | 1.3e-36 | Female |
| ARBs | 26 | 2,779 | 1,696 | 1,083 | 61.0% | 0.189 | 0.222 | 3.5e-31 | Female |
| Statins | 15 | 2,621 | 1,584 | 1,037 | 60.4% | 0.162 | 0.211 | <1e-20 | Female |
| Ca Channel Blockers | 26 | 1,877 | 1,081 | 796 | 57.6% | 0.127 | 0.152 | <1e-5 | Female |
| NSAIDs | 27 | 3,442 | 1,877 | 1,565 | 54.5% | 0.243 | 0.091 | <1e-10 | Female |
| Anti-TNF | 17 | 3,214 | 1,461 | 1,753 | 45.5% | 0.070 | -0.091 | <1e-5 | Mixed |
| Insulins | 10 | 1,131 | 529 | 602 | 46.8% | -0.078 | -0.065 | <0.05 | Male |
| Anticonvulsants | 11 | 2,649 | 1,260 | 1,389 | 47.6% | -0.050 | -0.049 | <0.05 | Male |
| SSRIs | 15 | 2,037 | 854 | 1,183 | 41.9% | -0.189 | -0.165 | <1e-10 | Male |

**Table 10. Age-sex interaction across drug classes (% female-biased by age group).**

| Drug class | Young Adult (18-44) | Middle-Aged (45-64) | Elderly (65+) | Direction of age trend |
|------------|-------------------|-------------------|--------------|----------------------|
| | % F-biased (n signals) | % F-biased (n signals) | % F-biased (n signals) | |
| Opioids | 87.8% (872) | 56.8% (709) | 39.8% (465) | Strong F-to-M shift |
| Antipsychotics | 71.1% (1,209) | 55.4% (826) | 40.4% (441) | Strong F-to-M shift |
| SSRIs | 52.4% (471) | 47.4% (397) | 32.5% (311) | M bias increases with age |
| ACE Inhibitors | 67.9% (78) | 78.0% (296) | 64.2% (386) | Stable F bias |
| Statins | 50.9% (53) | 38.6% (456) | 56.5% (612) | Non-monotonic (U-shape) |
| Hormonal agents | 0.0% (2) | 7.7% (13) | 0.0% (3) | Consistently M-biased |
| **All classes** | **63.2% (20,458)** | **52.1% (31,322)** | **49.3% (30,983)** | **F bias attenuates with age** |
| | Mean log ratio: 0.170 | Mean log ratio: 0.012 | Mean log ratio: -0.017 | |

Note: Young adults exhibit a clear female predominance in sex-differential signals, which progressively attenuates in middle-aged and elderly patients. A total of 1,470 drug-AE pairs showed directional flips between young adult and elderly age groups, indicating that some sex-differential patterns are age-contingent.

---

## Supplementary Materials

### Supplementary Table S1: Complete sex-differential edge catalog

All 96,281 sex-differential drug-adverse event edges with full statistical detail. Available as a tab-separated file (`supplementary_table_S1_all_sex_diff_edges.tsv`).

Columns: drug_name, adverse_event (MedDRA PT), log_ror_ratio, direction (female/male), ror_female, ror_male, n_female, n_male, chi_square_p_value, confidence_interval_lower, confidence_interval_upper.

This table provides the complete set of sex-differential pharmacovigilance signals at the individual drug-AE pair level, enabling researchers to query specific drugs or adverse events of interest. Signals are sorted by absolute log_ror_ratio in descending order.

### Supplementary Table S2: Link prediction results (top 500)

The 500 highest-scoring novel sex-differential drug-AE predictions from ComplEx v4 link prediction. Available as a tab-separated file (`supplementary_table_S2_link_predictions_500.tsv`).

Columns: rank, drug, adverse_event, prediction_score, has_aggregate_edge (boolean indicating whether a non-sex-stratified `has_adverse_event` edge exists), drug_name_clean, ae_name_clean, drug_total_edges (connectivity of drug node), clinical_plausibility_note.

Of 500 predictions, 146 (29.2%) involve known aggregate associations predicted to have a sex-differential component, and 354 (70.8%) are entirely novel. Prediction scores range from 8.63 to 15.07.

### Supplementary Table S3: Pathway enrichment analysis (79 enriched pathways)

Complete results of the Reactome pathway enrichment analysis for gene targets of sex-biased drugs. Available as a tab-separated file (`supplementary_table_S3_pathway_enrichment.tsv`).

Columns: pathway_name, reactome_id, n_female_target_genes, n_male_target_genes, female_ratio, bias_direction (Female-enriched/Male-enriched), fisher_exact_p, fdr_q_value.

32 pathways are enriched for female-biased drug targets (dominated by extracellular matrix biology, immune signaling, and ubiquitin-proteasome pathways) and 47 pathways are enriched for male-biased drug targets (dominated by ion channel signaling, interleukin signaling, and metabolic regulation). Top female-enriched pathways include CLEC7A/Dectin-1 signaling (F: 166, M: 1), collagen degradation (F: 102, M: 1), and FCERI-mediated NF-kB activation (F: 166, M: 1). Top male-enriched pathways include voltage-gated potassium channels (F: 3, M: 116), insulin processing (F: 1, M: 32), and NOTCH3 signaling (F: 4, M: 82).

### Supplementary Table S4: Geographic variation in sex-differential signals (15 countries)

Country-level breakdown of sex-differential signal patterns across 15 countries contributing the most FAERS reports. Available as a tab-separated file (`supplementary_table_S4_geographic_variation.tsv`).

Columns: country_code, country_name, total_reports, female_reports, male_reports, female_report_pct, total_signals, strong_signals, female_biased_strong, male_biased_strong, pct_female_biased, mean_log_ratio, pearson_r_vs_US, n_shared_pairs_with_US.

Full statistics for: US (9,934,811 reports; 50.8% F-biased signals), CA (573,932; 34.2%), GB (491,181; 39.2%), FR (416,996; 49.1%), JP (412,316; 57.4%), DE (292,428; 47.1%), IT (201,710; 47.1%), CN (160,623; 51.0%), BR (117,585; 30.0%), ES (117,420; 52.4%), AU (104,498; 48.5%), NL (96,869; 39.1%), IN (62,500; 51.1%), CO (58,100; 35.5%).

### Supplementary Table S5: Age-sex interaction (full results)

Complete drug class by age group interaction analysis. Available as a tab-separated file (`supplementary_table_S5_age_sex_interaction.tsv`).

Columns: drug_class, age_group (young_adult/middle_aged/elderly), age_range, n_reports, n_female, n_male, total_signals, strong_signals, female_biased, male_biased, pct_female_biased, mean_log_ratio, median_log_ratio.

Includes all 6 drug classes analyzed across 3 age groups (18 rows), plus overall age group summaries and 1,470 directional flip events. Young adult age group: 63.2% female-biased (mean log ratio = 0.170); middle-aged: 52.1% (0.012); elderly: 49.3% (-0.017).

### Supplementary Figure S1: Temporal validation (train-test signal correlation)

Scatter plot showing the correlation between sex-differential signal log_ror_ratios computed on the training period (2004Q1-2020Q4, n = 5,239,086 reports) versus the test period (2021Q1-2025Q3, n = 2,230,049 reports). Each point represents one drug-AE pair present in both periods (n = 33,786 shared pairs). The Pearson correlation is r = 0.384 (p < 1e-100). Points are colored by whether the signal maintains the same directional bias in both periods (green, 84.0% of 3,350 strong-in-both pairs) or flips direction (orange). The diagonal line represents perfect agreement. Marginal histograms show the distribution of log_ror_ratios in each period. The moderate correlation indicates that while the direction of sex bias is largely preserved over time (84.0% concordance among strong signals), the magnitude of effects shows temporal variation, consistent with evolving reporting patterns and drug usage.

---

## Acknowledgements

The author thanks the FDA for maintaining the FAERS database as a public resource, and the teams behind STRING, ChEMBL, Reactome, GTEx, and DiAna for making their data openly available. Computational resources were provided by an NVIDIA DGX Spark GB10 system. The author acknowledges the use of Claude (Anthropic) for manuscript preparation assistance and code review. This work was conducted independently without external funding.

---

## Author Contributions (CRediT)

**Mohammed Javeed Akhtar Abbas Shaik**: Conceptualization, Methodology, Software, Validation, Formal Analysis, Investigation, Data Curation, Writing -- Original Draft, Writing -- Review & Editing, Visualization, Project Administration.

---

## Competing Interests

The author declares no competing interests.

---

## References

1. Mazure CM, Fiellin DA. Women and opioids: something different is happening here. *Lancet* **2018**; 392: 9-11. doi: 10.1016/S0140-6736(18)31203-0

2. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. *Biol Sex Differ* **2020**; 11: 32. doi: 10.1186/s13293-020-00308-5

3. Food and Drug Administration. General considerations for the clinical evaluation of drugs (HEW (FDA) 77-3040). **1977**. Rescinded 1993.

4. National Institutes of Health Revitalization Act of 1993, Public Law 103-43. See also NOT-OD-15-102 (2015).

5. Mauvais-Jarvis F, Bairey Merz N, Barnes PJ, et al. Sex and gender: modifiers of health, disease, and medicine. *Lancet* **2020**; 396: 565-582. doi: 10.1016/S0140-6736(20)31561-0

6. Yu Y, Chen J, Li D, Wang L, Wang W, Liu H. Systematic analysis of adverse event reports for sex differences in adverse drug events. *Sci Rep* **2016**; 6: 24955. doi: 10.1038/srep24955

7. Chandak P, Tatonetti NP. Using machine learning to identify adverse drug effects posing increased risk to women. *Patterns* **2020**; 1: 100108. doi: 10.1016/j.patter.2020.100108

8. Himmelstein DS, Lizee A, Hessler C, et al. Systematic integration of biomedical knowledge prioritizes drugs for repurposing. *eLife* **2017**; 6: e26726. doi: 10.7554/eLife.26726

9. Ioannidis VN, Song X, Manchanda S, et al. DRKG -- Drug Repurposing Knowledge Graph for Covid-19. *arXiv* **2020**: 2004.14621.

10. Chandak P, Huang K, Zitnik M. Building a knowledge graph to enable precision medicine. *Sci Data* **2023**; 10: 67. doi: 10.1038/s41597-023-01960-3

11. Konigs C, Friedrichs M, Dietrich T. PharMeBINet: the heterogeneous pharmacological medical biochemical network. *Sci Data* **2022**; 9: 393. doi: 10.1038/s41597-022-01510-3

12. Kuhn M, Letunic I, Jensen LJ, Bork P. The SIDER database of drugs and side effects. *Nucleic Acids Res* **2016**; 44: D1075-D1079. doi: 10.1093/nar/gkv1075

13. Szklarczyk D, Kirsch R, Koutrouli M, et al. The STRING database in 2023: protein-protein association networks and functional enrichment analyses for any sequenced genome of interest. *Nucleic Acids Res* **2023**; 51: D483-D489. doi: 10.1093/nar/gkac1000

14. Zdrazil B, Felix E, Hunter F, et al. The ChEMBL Database in 2023: a drug discovery platform spanning genomics, chemical biology and clinical data. *Nucleic Acids Res* **2024**; 52: D1180-D1192. doi: 10.1093/nar/gkad1004

15. Gillespie M, Jassal B, Stephan R, et al. The Reactome pathway knowledgebase 2022. *Nucleic Acids Res* **2022**; 50: D419-D426. doi: 10.1093/nar/gkab1028

16. Oliva M, Munoz-Aguirre M, Kim-Hellmuth S, et al. The impact of sex on gene expression across human tissues. *Science* **2020**; 369: eaba3066. doi: 10.1126/science.aba3066

17. Fusaroli M, Raschi E, Gatti M, De Ponti F, Poluzzi E. Development of a comprehensive drug dictionary for FAERS data mining: the DiAna dictionary. *Drug Saf* **2024**; 47: 75-86. doi: 10.1007/s40264-023-01370-7

18. Trouillon T, Welbl J, Riedel S, Gaussier E, Bouchard G. Complex embeddings for simple link prediction. *Proc ICML* **2016**; 48: 2071-2080.

19. Ali M, Berrendorf M, Hoyt CT, et al. PyKEEN 1.0: a Python library for training and evaluating knowledge graph embeddings. *J Mach Learn Res* **2021**; 22: 1-6.

20. Yang B, Yih W, He X, Gao J, Deng L. Embedding entities and relations for learning and inference in knowledge bases. *Proc ICLR* **2015**.

21. Sun Z, Deng ZH, Nie JY, Tang J. RotatE: Knowledge graph embedding by relational rotation in complex space. *Proc ICLR* **2019**.

22. Goldman SA. Limitations and strengths of spontaneous reports data. *Clin Ther* **1998**; 20 Suppl C: C40-44. doi: 10.1016/S0149-2918(98)80007-6

23. Roden DM. Drug-induced prolongation of the QT interval. *N Engl J Med* **2004**; 350: 1013-1022. doi: 10.1056/NEJMra032426

24. Seeman MV. Secondary effects of antipsychotics: women at greater risk than men. *Schizophr Bull* **2009**; 35: 937-948. doi: 10.1093/schbul/sbn023

25. Ke Z, Zhang Y, Liu M, et al. Sex-biased adverse drug reactions related to ESR1 pharmacogenomics. *Pharmacogenet Genomics* **2025**; 35(1): 1-10. PMID: 39305475. doi: 10.1097/FPC.0000000000000544

26. Melcangi RC, Panzica GC. Neuroactive steroids: old players in a new game. *Neuroscience* **2006**; 138: 733-739. doi: 10.1016/j.neuroscience.2005.10.066

27. Ali M, Berrendorf M, Hoyt CT, et al. Bringing light into the dark: a large-scale evaluation of knowledge graph embedding models under a unified framework. *IEEE Trans Pattern Anal Mach Intell* **2022**; 44: 8825-8845. doi: 10.1109/TPAMI.2021.3124805


---

*Manuscript prepared: March 2026*

*Data and code availability: Zenodo DOI 10.5281/zenodo.18819192; GitHub github.com/jshaik369/SexDiffKG*

*License: CC-BY 4.0 (manuscript and data); MIT (code)*
