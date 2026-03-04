#!/usr/bin/env python3.13
"""Generate ISMB 2026 Long Abstract (2-page PDF) for SexDiffKG."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import os

OUTPUT = os.path.expanduser("~/sexdiffkg/results/SexDiffKG_ISMB2026_abstract.pdf")
FIG_DIR = os.path.expanduser("~/sexdiffkg/results/figures")

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    topMargin=0.55*inch,
    bottomMargin=0.45*inch,
    leftMargin=0.7*inch,
    rightMargin=0.7*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'Title2', parent=styles['Title'],
    fontSize=12.5, leading=14.5, spaceAfter=3,
    fontName='Times-Bold',
)
author_style = ParagraphStyle(
    'Author', parent=styles['Normal'],
    fontSize=8.5, leading=10, alignment=TA_CENTER,
    fontName='Times-Roman', spaceAfter=2,
)
section_style = ParagraphStyle(
    'Section', parent=styles['Heading2'],
    fontSize=9.5, leading=11.5, spaceAfter=2, spaceBefore=5,
    fontName='Times-Bold',
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontSize=8.5, leading=10.5, alignment=TA_JUSTIFY,
    fontName='Times-Roman', spaceAfter=3,
)
caption_style = ParagraphStyle(
    'Caption', parent=styles['Normal'],
    fontSize=7.5, leading=9, alignment=TA_LEFT,
    fontName='Times-Italic', spaceAfter=4,
)
ref_style = ParagraphStyle(
    'Ref', parent=styles['Normal'],
    fontSize=7, leading=8.5,
    fontName='Times-Roman', spaceAfter=1,
)
table_style_obj = TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
    ('FONTSIZE', (0, 0), (-1, -1), 7.5),
    ('LEADING', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 3),
    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 1),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
])

story = []

# Title
story.append(Paragraph(
    "SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph<br/>from 14.5 Million FDA Adverse Event Reports",
    title_style
))

# Authors
story.append(Paragraph(
    "JShaik<super>1</super>",
    author_style
))
story.append(Paragraph(
    "<i><font size=7.5>1. CoEvolve Network, Independent Researcher, Barcelona, Spain — jshaik@coevolvenetwork.com</font></i>",
    author_style
))
story.append(Spacer(1, 3))

# Background
story.append(Paragraph("Background &amp; Motivation", section_style))
story.append(Paragraph(
    "Women experience adverse drug reactions (ADRs) at 1.5–1.7× the rate of men, driven by differences in "
    "CYP enzyme expression, body composition, hormonal modulation, and renal clearance [1]. Despite this, most "
    "pharmacovigilance databases analyze safety signals in aggregate without sex stratification. Existing "
    "biomedical knowledge graphs — Hetionet (47K nodes, 2.3M edges) [4], DRKG (97K nodes, 5.9M edges) [5], and "
    "PharmKG (7.6K nodes, 500K edges) — lack sex-differential analysis capability. No computational resource "
    "systematically captures sex-differential drug safety signals at scale.",
    body_style
))

# Methods
story.append(Paragraph("Methods", section_style))
story.append(Paragraph(
    "<b>Data Integration.</b> SexDiffKG integrates 14,536,008 FAERS reports (2004–2024; F: 8,744,397, M: 5,791,611) "
    "with drug–target binding from ChEMBL 36, protein–protein interactions from STRING v12.0, biological pathways "
    "from KEGG, and protein annotations from UniProt. Drug names were resolved to ChEMBL identifiers for 4,455 drugs "
    "(15.2% of 29,277), enabling molecular target integration.",
    body_style
))
story.append(Paragraph(
    "<b>Sex-Differential Signal Detection.</b> For each drug–adverse event pair, sex-stratified Reporting Odds Ratios "
    "(ROR) were computed. The sex-differential ratio uses the natural logarithm: log_ror_ratio = ln(ROR<sub>female</sub> / "
    "ROR<sub>male</sub>). We apply a strong threshold of |ln(ratio)| > 1.0 (>2.7× difference, ≥10 reports/sex), "
    "yielding 49,026 strong signals from 183,544 sex-differential signals.",
    body_style
))
story.append(Paragraph(
    "<b>KG Embedding &amp; Analysis.</b> DistMult (200d, 100 epochs, SLCWA loss) was trained on 5,489,928 triples "
    "(126,575 entities, 6 relations) on a GPU-accelerated workstation. Drug embeddings were clustered (K=20) and bridged to "
    "ChEMBL targets to compute per-gene sex-bias scores for 429 targets.",
    body_style
))

# Results
story.append(Paragraph("Results", section_style))

# KG stats
story.append(Paragraph(
    "<b>Knowledge Graph.</b> SexDiffKG contains 127,063 nodes (6 types: Gene 56%, Drug 23%, AdverseEvent 13%, "
    "Protein 7%, Pathway 2%, Tissue &lt;1%) and 5,839,717 edges (6 relations). From 14.5M FAERS reports, "
    "we identified 49,026 strong sex-differential signals (58.5% female-biased, median 3.7× difference) across "
    "3,441 drugs and 5,658 adverse events.",
    body_style
))

# Embedding results
story.append(Paragraph(
    "<b>Link Prediction.</b> DistMult achieved MRR 0.048, Hits@10 8.85%, and AMRI 0.9807, ranking correct "
    "triples in the top 1.9% of 13,466 candidates. RotatE (25 CPU epochs) achieved AMRI 0.003 (near-random), "
    "confirming DistMult's suitability for this graph's predominantly symmetric relations.",
    body_style
))

# Target findings table
story.append(Paragraph("<b>Gene Target Profiles.</b> Key findings from 429 targets with sex-biased safety patterns:", body_style))

target_data = [
    ['Target Class', 'Bias', 'Significance'],
    ['HDAC1/2/3/6', 'Female (+1.0)', 'First large-scale evidence of sex-specific HDAC inhibitor safety'],
    ['ESR1 (estrogen receptor)', 'Male (−0.80)', 'Counterintuitive; off-target effects in male patients'],
    ['ITGA2B/ITGB3 (platelet)', 'Female (+1.0)', 'Sex differences in hemostasis and antiplatelet therapy'],
    ['SCNN1A/B/G (Na+ channel)', 'Male (−1.0)', 'Consistent with known epithelial Na channel sex differences'],
    ['CHRNA/B/D/E/G (nAChR)', 'Female (+0.75)', 'Neuromuscular junction pharmacology differs by sex'],
]
t2 = Table(target_data, colWidths=[1.4*inch, 0.9*inch, 4.5*inch])
t2.setStyle(table_style_obj)
story.append(t2)
story.append(Spacer(1, 3))

# Figure
fig1_path = os.path.join(FIG_DIR, "fig1_drug_pca_clusters.png")
if os.path.exists(fig1_path):
    img = Image(fig1_path, width=4.2*inch, height=2.3*inch)
    story.append(img)
    story.append(Paragraph(
        "<b>Figure 1.</b> PCA projection of DistMult drug embeddings (29,201 drugs, 20 clusters, 61.9% variance). "
        "Clusters show distinct sex-differential safety profiles with female bias ratios from 0.33 to 1.00.",
        caption_style
    ))

# Validation
story.append(Paragraph(
    "<b>Validation.</b> Against 40 literature benchmarks: 30/40 benchmarks covered (75%), 19/30 directionally confirmed "
    "(63.3%). Confirmed: atorvastatin (female myalgia, 3.4×), digoxin (female toxicity), aspirin (male GI bleeding).",
    body_style
))

# Conclusion
story.append(Paragraph("Conclusion", section_style))
story.append(Paragraph(
    "SexDiffKG is the first knowledge graph for sex-differential drug safety, integrating pharmacovigilance "
    "at unprecedented scale with molecular target annotations. The 429 gene targets with sex-biased profiles "
    "— particularly the novel HDAC inhibitor finding — provide actionable hypotheses for precision pharmacovigilance. "
    "All data/code: https://github.com/jshaik369/SexDiffKG (DOI: 10.5281/zenodo.18819192). "
    "bioRxiv preprint: BIORXIV/2026/708761.",
    body_style
))

# References
story.append(Paragraph("References", section_style))
refs = [
    "[1] Zucker &amp; Prendergast (2020) <i>Biol Sex Differ</i> 11:32.",
    "[2] Watson et al. (2019) <i>Drug Safety</i> 42:445-453.",
    "[3] Yang et al. (2015) <i>ICLR</i> — DistMult.",
    "[4] Himmelstein et al. (2017) <i>eLife</i> 6:e26726 — Hetionet.",
    "[5] Ioannidis et al. (2020) <i>arXiv</i> 2010.09600 — DRKG.",
    "[6] Ali et al. (2021) <i>JMLR</i> 22:1-6 — PyKEEN.",
]
for r in refs:
    story.append(Paragraph(r, ref_style))

doc.build(story)
sz = os.path.getsize(OUTPUT)
print(f"Generated: {OUTPUT} ({sz:,} bytes)")

# Check page count
from PyPDF2 import PdfReader
reader = PdfReader(OUTPUT)
print(f"Pages: {len(reader.pages)}")
