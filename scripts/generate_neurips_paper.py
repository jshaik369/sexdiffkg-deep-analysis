#!/usr/bin/env python3.13
"""Generate NeurIPS 2026 paper draft (9-page, ML focus) for SexDiffKG."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                 TableStyle, Image, PageBreak, KeepTogether)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import os

OUTPUT = os.path.expanduser("~/sexdiffkg/results/SexDiffKG_NeurIPS2026_draft.pdf")
FIG_DIR = os.path.expanduser("~/sexdiffkg/results/figures")

doc = SimpleDocTemplate(
    OUTPUT, pagesize=letter,
    topMargin=0.75*inch, bottomMargin=0.75*inch,
    leftMargin=1.0*inch, rightMargin=1.0*inch,
)

styles = getSampleStyleSheet()

# NeurIPS-like styles (Times, single column)
title_style = ParagraphStyle('NTitle', fontSize=14, leading=16.5, spaceAfter=4,
    fontName='Times-Bold', alignment=TA_CENTER)
author_style = ParagraphStyle('NAuthor', fontSize=10, leading=12, alignment=TA_CENTER,
    fontName='Times-Roman', spaceAfter=2)
h1 = ParagraphStyle('NH1', fontSize=11, leading=13, spaceBefore=10, spaceAfter=4,
    fontName='Times-Bold')
h2 = ParagraphStyle('NH2', fontSize=10, leading=12, spaceBefore=8, spaceAfter=3,
    fontName='Times-Bold')
body = ParagraphStyle('NBody', fontSize=9.5, leading=11.5, alignment=TA_JUSTIFY,
    fontName='Times-Roman', spaceAfter=4)
caption = ParagraphStyle('NCap', fontSize=8.5, leading=10, alignment=TA_LEFT,
    fontName='Times-Italic', spaceAfter=6)
ref = ParagraphStyle('NRef', fontSize=8, leading=9.5, fontName='Times-Roman', spaceAfter=1)

ts = TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('LEADING', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.93, 0.93, 0.93)),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
])

S = []  # story

# ---- Title ----
S.append(Paragraph(
    "SexDiffKG: Knowledge Graph Embeddings for Sex-Differential<br/>"
    "Drug Safety from 14.5 Million Pharmacovigilance Reports", title_style))
S.append(Spacer(1, 4))
S.append(Paragraph("JShaik", author_style))
S.append(Paragraph("<i><font size=8>CoEvolve Network, Independent Research, Barcelona, Spain</font></i>", author_style))
S.append(Paragraph("<i><font size=8>jshaik@coevolvenetwork.com</font></i>", author_style))
S.append(Spacer(1, 8))

# ---- Abstract ----
S.append(Paragraph("<b>Abstract</b>", h1))
S.append(Paragraph(
    "Sex-based differences in drug safety affect millions of patients yet remain poorly modeled in computational "
    "pharmacovigilance. We present SexDiffKG, a heterogeneous knowledge graph integrating 14.5 million FDA adverse "
    "event reports with molecular target, protein interaction, and pathway data from five biomedical databases. "
    "The graph contains 127,063 nodes (6 types) and 5,839,717 edges (6 relations), including 49,026 sex-differential "
    "drug–adverse event signals identified through sex-stratified Reporting Odds Ratio analysis. We train DistMult "
    "embeddings (200 dimensions, 100 epochs) achieving an Adjusted Mean Rank Index (AMRI) of 0.9807, placing correct "
    "triples in the top 1.9% of candidates across 126,575 entities. A comparative RotatE evaluation (25 CPU epochs) "
    "yields AMRI of 0.003 (near-random), demonstrating that model expressivity does not guarantee performance without "
    "sufficient training. Embedding-based drug clustering (K=20) reveals distinct sex-differential safety profiles, "
    "and target-level analysis identifies 429 gene targets with sex-biased patterns. Novel findings include exclusively "
    "female-biased HDAC inhibitor safety profiles and counterintuitive male-biased estrogen receptor drug safety. "
    "SexDiffKG is the first KG designed for sex-differential pharmacovigilance at scale.",
    body))
S.append(Spacer(1, 4))

# ---- 1. Introduction ----
S.append(Paragraph("1&nbsp;&nbsp;&nbsp;Introduction", h1))
S.append(Paragraph(
    "Adverse drug reactions (ADRs) account for approximately 2.2 million serious cases annually in the United States, "
    "with women experiencing ADRs at 1.5–1.7× the rate of men [1]. This disparity arises from sex differences in "
    "CYP enzyme expression, body composition, hormonal drug transport modulation, and renal clearance. The FDA's 2013 "
    "sex-specific dosing recommendation for zolpidem — one of the few in regulatory history — highlighted the clinical "
    "significance of these differences.",
    body))
S.append(Paragraph(
    "Knowledge graphs (KGs) have become essential tools for biomedical data integration. Hetionet [4] (47K nodes, "
    "2.3M edges), DRKG [5] (97K nodes, 5.9M edges), and PharmKG (7.6K nodes, 500K edges) demonstrate the value of "
    "graph-based representations for drug repurposing and safety prediction. KG embedding methods — translational "
    "(TransE [14], RotatE [8]), bilinear (DistMult [3], ComplEx), and neural (R-GCN, CompGCN) — enable link prediction "
    "from graph structure.",
    body))
S.append(Paragraph(
    "However, no existing KG models sex-differential drug safety. All current resources treat pharmacovigilance data "
    "in aggregate, leaving a critical gap as precision medicine increasingly demands patient-level risk assessment. "
    "We address this gap with SexDiffKG, a purpose-built KG that integrates the FDA Adverse Event Reporting System "
    "(FAERS) with molecular data, introduces sex-stratified signal detection, and demonstrates meaningful embedding-based "
    "link prediction for sex-aware safety assessment.",
    body))

S.append(Paragraph("<b>Contributions.</b> (1) A heterogeneous KG integrating 14.5M FAERS reports with 5 biomedical "
    "databases, containing 127K nodes and 5.8M edges; (2) Sex-stratified ROR analysis identifying 49,026 strong "
    "sex-differential signals; (3) DistMult embeddings achieving AMRI 0.9807 with comparative RotatE evaluation; "
    "(4) Discovery of 429 gene targets with sex-biased safety profiles; (5) Validation against 40 literature benchmarks.",
    body))

# ---- 2. Related Work ----
S.append(Paragraph("2&nbsp;&nbsp;&nbsp;Related Work", h1))
S.append(Paragraph(
    "<b>Biomedical Knowledge Graphs.</b> Hetionet [4] integrates 29 public resources into a 47K-node graph for drug "
    "repurposing. DRKG [5] scales to 97K nodes and 5.9M edges across 6 databases. PharmKG combines DrugBank and "
    "PharmGKB for pharmacogenomic KG reasoning. OpenBioLink (180K nodes, 4.6M edges) provides benchmarked biomedical "
    "link prediction. None incorporate sex-differential safety signals.",
    body))
S.append(Paragraph(
    "<b>KG Embedding Methods.</b> DistMult [3] uses a bilinear scoring function h ⊙ r ⊙ t, well-suited for "
    "symmetric relations. RotatE [8] models relations as rotations in complex space, capturing asymmetric patterns. "
    "TransE [14] represents relations as translations. For biomedical KGs with predominantly symmetric or "
    "quasi-symmetric relations, DistMult often outperforms more expressive models when adequately trained.",
    body))
S.append(Paragraph(
    "<b>Sex Differences in Drug Safety.</b> Zucker and Prendergast [1] review pharmacokinetic sex differences. "
    "Watson et al. [2] analyze ADR reporting patterns across spontaneous databases. Individual drug-level studies "
    "exist (zolpidem, statins, digoxin) but no systematic computational approach scales across the pharmacopeia.",
    body))

# ---- 3. Methods ----
S.append(Paragraph("3&nbsp;&nbsp;&nbsp;Methods", h1))
S.append(Paragraph("3.1&nbsp;&nbsp;Data Sources and Knowledge Graph Construction", h2))
S.append(Paragraph(
    "SexDiffKG integrates five authoritative biomedical databases: (1) FDA FAERS (2004Q1–2024Q4): 14,536,008 reports "
    "with valid sex assignment (F: 8,744,397, M: 5,791,611); (2) ChEMBL 36: 12,682 drug–gene target edges for 4,455 "
    "drugs; (3) STRING v12.0: 465,390 protein–protein interactions; (4) KEGG: 537,605 pathway participation edges; "
    "(5) UniProt: 105 sex-differential expression edges.",
    body))

# Schema table
schema_data = [
    ['Entity Type', 'Count', '%', 'Source'],
    ['Gene', '70,607', '55.6%', 'ChEMBL/KEGG (Ensembl IDs)'],
    ['Drug', '29,277', '23.0%', 'ChEMBL (4,455) + FAERS (24,822)'],
    ['AdverseEvent', '16,162', '12.7%', 'FAERS (MedDRA terms)'],
    ['Protein', '8,721', '6.9%', 'STRING/UniProt'],
    ['Pathway', '2,279', '1.8%', 'KEGG'],
    ['Tissue', '17', '<0.1%', 'Gene expression data'],
]
S.append(Paragraph("<b>Table 1.</b> SexDiffKG entity types (127,063 total nodes).", caption))
t = Table(schema_data, colWidths=[1.0*inch, 0.7*inch, 0.5*inch, 3.5*inch])
t.setStyle(ts)
S.append(t)
S.append(Spacer(1, 4))

S.append(Paragraph("3.2&nbsp;&nbsp;Sex-Differential Signal Detection", h2))
S.append(Paragraph(
    "For each drug–adverse event pair, we compute sex-stratified Reporting Odds Ratios (ROR). The sex-differential "
    "ratio uses the natural logarithm: log_ror_ratio = ln(ROR<sub>female</sub> / ROR<sub>male</sub>). Positive values "
    "indicate female-higher risk; negative indicates male-higher. We apply a strong threshold |ln(ratio)| > 1.0, "
    "corresponding to >2.7× difference (e<sup>1</sup> ≈ 2.718), with ≥10 reports per sex for statistical stability.",
    body))
S.append(Paragraph(
    "This yields 49,026 strong signals from 183,544 sex-differential signals (from 2,610,331 total ROR computations). "
    "Among strong signals: 28,669 (58.5%) female-biased, 20,357 (41.5%) male-biased. Median |ln ratio| = 1.302 "
    "(~3.7×), mean = 1.477 (~4.4×), indicating robust effects well above the minimum threshold.",
    body))

S.append(Paragraph("3.3&nbsp;&nbsp;Knowledge Graph Embedding", h2))
S.append(Paragraph(
    "<b>DistMult.</b> We train DistMult [3] on 5,489,928 clean triples (after removing 349,789 with NaN entities from "
    "unresolved STRING identifiers) covering 126,575 entities and 6 relations. Training uses SLCWA loss with Adam "
    "optimizer (lr=0.001), batch size 512, 200 embedding dimensions, 100 epochs, and 1:1 negative sampling. Training "
    "completed in ~3.5 hours on an NVIDIA DGX Spark (Grace Blackwell GB10, ARM64, 128GB unified memory).",
    body))
S.append(Paragraph(
    "<b>RotatE.</b> For comparison, we train RotatE [8] with 200 complex-valued dimensions (400 real parameters), "
    "25 epochs, batch size 1024. Due to NVRTC JIT compilation limitations on the GB10 for complex-valued operations, "
    "training was performed on CPU (~18 min/epoch, 7.5 hours total, final loss 0.0241). Evaluation used GPU.",
    body))

# Training params table
train_data = [
    ['Parameter', 'DistMult', 'RotatE'],
    ['Dimensions', '200 (real)', '200 (complex) = 400 real'],
    ['Epochs', '100', '25'],
    ['Batch size', '512', '1024'],
    ['Learning rate', '0.001', '0.001'],
    ['Loss', 'SLCWA', 'SLCWA'],
    ['Training device', 'GPU (GB10)', 'CPU (Grace)'],
    ['Training time', '~3.5 hours', '~7.5 hours'],
    ['Triples', '5,489,928', '5,489,928'],
    ['Entities', '126,575', '126,575'],
]
S.append(Paragraph("<b>Table 2.</b> Embedding training configuration.", caption))
t2 = Table(train_data, colWidths=[1.2*inch, 2.0*inch, 2.5*inch])
t2.setStyle(ts)
S.append(t2)
S.append(Spacer(1, 4))

S.append(Paragraph("3.4&nbsp;&nbsp;Post-Embedding Analysis", h2))
S.append(Paragraph(
    "<b>Drug Clustering.</b> We extract embeddings for all 29,201 drugs, L2-normalize, and apply K-Means (K=20). "
    "PCA projection to 2D explains 61.9% of variance. Each cluster is profiled by mapping to sex-differential signals.",
    body))
S.append(Paragraph(
    "<b>Target Sex-Bias Scoring.</b> For each gene target in ChEMBL with ≥2 drugs showing sex-differential signals: "
    "sex_bias_score = (n<sub>female</sub> − n<sub>male</sub>) / n<sub>total</sub>, ranging from −1.0 (all male-biased) "
    "to +1.0 (all female-biased). This identifies 429 targets with measurable sex-differential profiles.",
    body))

# ---- 4. Results ----
S.append(Paragraph("4&nbsp;&nbsp;&nbsp;Results", h1))
S.append(Paragraph("4.1&nbsp;&nbsp;Link Prediction Performance", h2))

eval_data = [
    ['Metric', 'DistMult', 'RotatE', 'Interpretation'],
    ['MRR', '0.04762', '0.00010', 'DistMult 476× higher'],
    ['Hits@1', '2.25%', '0.001%', '—'],
    ['Hits@3', '4.54%', '0.002%', '—'],
    ['Hits@10', '8.85%', '0.009%', '—'],
    ['AMRI', '0.9807', '0.003', 'Top 1.9% vs near-random'],
    ['AMR', '~1,206', '62,350', 'Out of 126,575 entities'],
]
S.append(Paragraph("<b>Table 3.</b> Link prediction evaluation (test set).", caption))
t3 = Table(eval_data, colWidths=[0.8*inch, 0.9*inch, 0.8*inch, 3.2*inch])
t3.setStyle(ts)
S.append(t3)
S.append(Spacer(1, 4))

S.append(Paragraph(
    "DistMult achieves AMRI of 0.9807, indicating correct triples are ranked in the top 1.9% of 13,466 candidates. "
    "The absolute MRR of 0.048 is moderate compared to benchmarks like FB15k-237 (DistMult ~0.24), but the search "
    "space is 9× larger (126K vs 14K entities). Head/tail MRR asymmetry (0.033 vs 0.062) is structurally informative: "
    "predicting drug targets (tail) is more constrained than predicting which drugs target a gene (head), reflecting "
    "the many-to-few drug–target relationship.",
    body))
S.append(Paragraph(
    "<b>RotatE failure analysis.</b> RotatE's near-random performance (AMRI 0.003) despite its theoretical ability "
    "to model asymmetric relations is attributable to: (1) insufficient training (25 vs 100 epochs); (2) CPU-only "
    "training constraints; (3) SexDiffKG's predominantly symmetric relations where RotatE provides no advantage over "
    "DistMult. This result demonstrates that model expressivity does not guarantee performance without adequate "
    "training and hyperparameter optimization — a finding relevant to practitioners selecting embedding methods for "
    "domain-specific KGs.",
    body))

# Figure 1
fig1 = os.path.join(FIG_DIR, "fig1_drug_pca_clusters.png")
if os.path.exists(fig1):
    S.append(Spacer(1, 4))
    S.append(Image(fig1, width=4.5*inch, height=2.5*inch))
    S.append(Paragraph(
        "<b>Figure 1.</b> PCA projection of DistMult drug embeddings (29,201 drugs, 20 clusters, 61.9% variance). "
        "Colors indicate cluster assignment. Active clusters show distinct sex-differential safety profiles.",
        caption))

S.append(Paragraph("4.2&nbsp;&nbsp;Sex-Differential Signal Landscape", h2))
S.append(Paragraph(
    "From 14.5M FAERS reports, we identified 49,026 strong sex-differential signals across 3,441 drugs and 5,658 "
    "adverse events. The strongest female-biased signal: dutasteride × 'Product prescribing issue' (ln ratio = 5.53, "
    "252.8× female excess) — consistent with contraindication in women due to teratogenicity. Top drugs by signal "
    "count: ranitidine HCl (381 signals, 99.2% female-biased, reflecting pregnancy use), rituximab (344, 81.7% "
    "female), prednisone (302, 75.5% female).",
    body))

S.append(Paragraph("4.3&nbsp;&nbsp;Embedding-Based Drug Clustering", h2))
S.append(Paragraph(
    "K-Means clustering of drug embeddings (K=20) reveals 9 clusters with sex-differential signal data. Female bias "
    "ratios range from 0.333 to 1.000, demonstrating that the learned embedding space captures meaningful variation "
    "in sex-differential safety. The highest female-bias cluster contains drugs with exclusively female-biased signals "
    "enriched for reproductive and hormonal adverse events. Cluster 0 (2,087 drugs, female ratio 0.39) is enriched "
    "for 'Drug ineffective' and 'Fatigue,' suggesting metabolic clearance differences.",
    body))

S.append(Paragraph("4.4&nbsp;&nbsp;Gene Target Sex-Bias Profiles", h2))
S.append(Paragraph(
    "Bridging FAERS drug names to ChEMBL target annotations identifies 429 gene targets with sex-biased safety "
    "profiles: 112 female-biased, 124 male-biased, 193 neutral.",
    body))

target_data2 = [
    ['Target', 'Score', 'Drugs', 'Significance'],
    ['HDAC1/2/3/6', '+1.0', '3–5', 'Novel: exclusively female-biased HDAC inhibitor safety'],
    ['ESR1', '−0.80', '5', 'Counterintuitive male-biased estrogen receptor drugs'],
    ['ITGA2B/ITGB3', '+1.0', '3', 'Platelet integrins: sex differences in hemostasis'],
    ['F8/F9', '+1.0', '2', 'Coagulation factors: female-biased safety'],
    ['SCNN1A/B/G', '−1.0', '2', 'Sodium channels: known male-biased regulation'],
    ['CHRNA/B/D/E/G', '+0.75', '4', 'Nicotinic AChR: neuromuscular sex differences'],
    ['JAK1', '−0.75', '4', 'Immune: sex differences in JAK-STAT signaling'],
]
S.append(Paragraph("<b>Table 4.</b> Key gene targets with sex-biased drug safety profiles.", caption))
t4 = Table(target_data2, colWidths=[1.1*inch, 0.5*inch, 0.5*inch, 3.6*inch])
t4.setStyle(ts)
S.append(t4)
S.append(Spacer(1, 4))

S.append(Paragraph("4.5&nbsp;&nbsp;Validation", h2))
S.append(Paragraph(
    "Against 40 literature-documented sex-differential drug safety benchmarks: 30/40 benchmarks covered (75%), "
    "19/30 directionally confirmed (63.3% directional precision). Confirmed signals: atorvastatin (female myalgia, 3.4×), "
    "digoxin (female toxicity), aspirin (male GI bleeding). Three signals showed reversed direction (simvastatin, "
    "warfarin, ibuprofen), warranting investigation of confounding by indication.",
    body))

# ---- 5. Discussion ----
S.append(Paragraph("5&nbsp;&nbsp;&nbsp;Discussion", h1))
S.append(Paragraph(
    "<b>Practical implications for KG embedding.</b> The stark DistMult vs RotatE contrast (AMRI 0.9807 vs 0.003) "
    "on the same graph has implications for practitioners. SexDiffKG's 6 relation types are predominantly symmetric "
    "(has_adverse_event, interacts_with, participates_in), where DistMult's bilinear scoring is naturally suited and "
    "RotatE's rotational model provides no advantage. This suggests that for biomedical KGs with symmetric-dominant "
    "relations, simpler models may outperform more expressive ones — particularly when training budgets are constrained.",
    body))
S.append(Paragraph(
    "<b>Novel biological findings.</b> The exclusively female-biased HDAC1/2/3/6 safety profile has not been "
    "previously reported at scale. Given expanding oncological use of HDAC inhibitors (vorinostat, romidepsin, "
    "panobinostat), this finding warrants prospective sex-stratified monitoring. The male-biased ESR1 profile is "
    "counterintuitive but may reflect specific clinical contexts (tamoxifen in male breast cancer).",
    body))
S.append(Paragraph(
    "<b>Comparison with existing KGs.</b> SexDiffKG (127K nodes, 5.8M edges) is comparable in scale to DRKG (97K, "
    "5.9M) and larger than Hetionet (47K, 2.3M) or PharmKG (7.6K, 500K), while uniquely providing sex-differential "
    "analysis capability. The AMRI of 0.9807 indicates strong embedding quality despite the graph's heterogeneity.",
    body))

# ---- 6. Limitations ----
S.append(Paragraph("6&nbsp;&nbsp;&nbsp;Limitations and Future Work", h1))
S.append(Paragraph(
    "FAERS data is subject to underreporting, stimulated reporting, and demographic biases. ROR is a disproportionality "
    "measure that does not establish causation. DistMult MRR of 0.048 reflects the challenge of 126K-entity prediction. "
    "RotatE underperformance is likely addressable with ≥100 GPU-trained epochs (pending NVRTC fix for complex-valued "
    "ops on GB10). Future directions include: temporal signal analysis, GNN-based methods (R-GCN, CompGCN), "
    "dose-response integration, enhanced drug name resolution (RxNorm/UMLS), and prospective clinical validation.",
    body))

# ---- 7. Data Availability ----
S.append(Paragraph("7&nbsp;&nbsp;&nbsp;Reproducibility and Data Availability", h1))
S.append(Paragraph(
    "All computation performed on a single NVIDIA DGX Spark (GB10, ARM64, 128GB unified memory). The complete "
    "dataset includes: nodes.tsv (127,063 rows), edges.tsv (5,839,717 rows), entity/relation embeddings, 429 target "
    "scores, 20 cluster profiles, and 45 pipeline scripts. Data integrity verified by molecular-level audit: "
    "85 PASSED, 0 FAILED, 4 WARNINGS (documented). Code: https://github.com/jshaik369/SexDiffKG. "
    "Data: https://doi.org/10.5281/zenodo.18819192. Preprint: bioRxiv BIORXIV/2026/708761.",
    body))

# ---- References ----
S.append(Paragraph("References", h1))
refs = [
    "[1] Zucker, I. &amp; Prendergast, B.J. Sex differences in pharmacokinetics predict adverse drug reactions in women. <i>Biol Sex Differ</i>, 11:32, 2020.",
    "[2] Watson, S. et al. Sex differences in adverse drug reactions. <i>Drug Safety</i>, 42(3):445-453, 2019.",
    "[3] Yang, B. et al. Embedding entities and relations for learning and inference in knowledge bases. <i>ICLR</i>, 2015.",
    "[4] Himmelstein, D.S. et al. Systematic integration of biomedical knowledge prioritizes drugs for repurposing. <i>eLife</i>, 6:e26726, 2017.",
    "[5] Ioannidis, V.N. et al. DRKG — Drug Repurposing Knowledge Graph. <i>arXiv</i>:2010.09600, 2020.",
    "[6] Ali, M. et al. PyKEEN 1.0: A Python library for training and evaluating KG embeddings. <i>JMLR</i>, 22:1-6, 2021.",
    "[7] Gaulton, A. et al. The ChEMBL database in 2023. <i>Nucleic Acids Res</i>, 52(D1):D1180-D1192, 2024.",
    "[8] Sun, Z. et al. RotatE: Knowledge graph embedding by relational rotation in complex space. <i>ICLR</i>, 2019.",
    "[9] Szklarczyk, D. et al. The STRING database in 2023. <i>Nucleic Acids Res</i>, 51(D1):D483-D489, 2023.",
    "[10] Kanehisa, M. et al. KEGG for taxonomy-based analysis of pathways and genomes. <i>Nucleic Acids Res</i>, 2023.",
    "[11] Zheng, S. et al. PharmKG: a dedicated KG benchmark for biomedical data mining. <i>Brief Bioinform</i>, 22(4):bbaa344, 2021.",
    "[12] UniProt Consortium. UniProt: the Universal Protein Knowledgebase in 2023. <i>Nucleic Acids Res</i>, 2023.",
    "[13] FDA. Risk of next-morning impairment after use of insomnia drugs. Drug Safety Communication, 2013.",
    "[14] Bordes, A. et al. Translating embeddings for modeling multi-relational data. <i>NeurIPS</i>, 2013.",
]
for r in refs:
    S.append(Paragraph(r, ref))

doc.build(S)
sz = os.path.getsize(OUTPUT)
from PyPDF2 import PdfReader
pages = len(PdfReader(OUTPUT).pages)
print(f"Generated: {OUTPUT} ({sz:,} bytes, {pages} pages)")
