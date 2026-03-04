#!/usr/bin/env python3
"""Generate all venue-specific submission materials for SexDiffKG v4."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os

PUB = os.path.expanduser("~/sexdiffkg/Publication")

styles = getSampleStyleSheet()
title = ParagraphStyle('T', fontSize=13, leading=15, spaceAfter=4, fontName='Times-Bold', alignment=TA_CENTER)
h2 = ParagraphStyle('H2', fontSize=10, leading=12, spaceBefore=8, spaceAfter=3, fontName='Times-Bold')
body = ParagraphStyle('B', fontSize=10, leading=12.5, alignment=TA_JUSTIFY, fontName='Times-Roman', spaceAfter=4)

AUTHOR = "Mohammed Javeed Akhtar Abbas Shaik"
ORCID = "0009-0002-1748-7516"
EMAIL = "jshaik@coevolvenetwork.com"
AFFIL = "CoEvolve Network, Independent Researcher, Barcelona, Spain"
SIGN = f"Sincerely,<br/>{AUTHOR}<br/>ORCID: {ORCID}<br/>{AFFIL}<br/>{EMAIL}"

def make_pdf(filename, story):
    path = os.path.join(PUB, filename)
    doc = SimpleDocTemplate(path, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=1.0*inch, rightMargin=1.0*inch)
    doc.build(story)
    try:
        from PyPDF2 import PdfReader
        pages = len(PdfReader(path).pages)
    except Exception:
        pages = "?"
    print(f"  {filename}: {os.path.getsize(path):,} bytes, {pages} pages")
    return path

# ========== 1. ASHG 2026 Abstract ==========
print("1. ASHG 2026...")
s = []
s.append(Paragraph("ASHG 2026 Abstract Submission", title))
s.append(Spacer(1, 8))
s.append(Paragraph(f"<b>Title:</b> SexDiffKG: A Knowledge Graph Revealing Sex-Differential Drug Safety Profiles Across 317 Gene Targets from 14.5 Million FDA Reports", body))
s.append(Spacer(1, 4))
s.append(Paragraph(f"<b>Presenting Author:</b> {AUTHOR}, {AFFIL}", body))
s.append(Paragraph(f"<b>ORCID:</b> {ORCID}", body))
s.append(Spacer(1, 8))
s.append(Paragraph("<b>Abstract:</b>", h2))
s.append(Paragraph(
    "Sex-based differences in drug safety affect millions of patients, yet the genetic basis remains poorly characterized. "
    "We constructed SexDiffKG, integrating 14,536,008 FDA FAERS reports (2004-2025) with drug-gene target data from "
    "ChEMBL 36, protein interactions from STRING v12.0, and pathway annotations from Reactome into a knowledge graph "
    "of 109,867 nodes and 1,822,851 edges. Drug names were normalized using the DiAna dictionary (846,917 FAERS mappings) "
    "achieving 53.9% active-ingredient resolution.",
    body))
s.append(Paragraph(
    "Through sex-stratified Reporting Odds Ratio analysis (|log(ROR_F/ROR_M)| >= 0.5, min 10 reports/sex), we identified "
    "96,281 sex-differential signals (53.8% female-biased). Bridging FAERS drugs to ChEMBL targets revealed 317 gene "
    "targets with directional sex-biased safety profiles. Key findings: HDAC1/2/3/6 (histone deacetylases) show "
    "female-biased drug safety, suggesting sex-differential epigenetic regulation. ESR1 shows paradoxical male-biased "
    "safety. GNRHR and SRD5A1/3 (5-alpha reductases) are exclusively female-biased. PTGER3 (prostaglandin receptor) "
    "and OXTR (oxytocin receptor) are exclusively male-biased.",
    body))
s.append(Paragraph(
    "ComplEx KG embeddings (200d, 100 epochs) achieved MRR 0.248 and AMRI 0.990, confirming meaningful pharmacogenomic "
    "structure. Signal validation against 40 literature benchmarks achieves 82.8% directional precision. "
    "Data: doi.org/10.5281/zenodo.18819192. Code: github.com/jshaik369/SexDiffKG.",
    body))
make_pdf("SexDiffKG_ASHG2026_abstract.pdf", s)

# ========== 2. Briefings in Bioinformatics ==========
print("2. Briefings in Bioinformatics...")
s = []
s.append(Paragraph("Cover Letter - Briefings in Bioinformatics", title))
s.append(Spacer(1, 12))
s.append(Paragraph("Dear Editors,", body))
s.append(Paragraph(
    'We submit the manuscript entitled "SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph from 14.5 Million '
    'FDA Adverse Event Reports" for consideration as a Methods article in Briefings in Bioinformatics.',
    body))
s.append(Paragraph(
    "This work presents a novel computational methodology for sex-differential pharmacovigilance through knowledge graph "
    "construction and embedding. SexDiffKG integrates 14.5 million FAERS reports with molecular data from five open-access "
    "databases (ChEMBL 36, STRING v12.0, Reactome, GTEx v8) into a graph of 109,867 nodes and 1,822,851 edges. "
    "A key methodological contribution is the 4-tier drug normalization pipeline anchored by the DiAna dictionary "
    "(846,917 FAERS mappings, 53.9% active-ingredient resolution), which improved validation precision from 63.3% to "
    "82.8% on 40 literature benchmarks. Additional contributions include: ComplEx embedding achieving MRR 0.248 "
    "and AMRI 0.990 on a 110K-entity domain-specific graph; and a target sex-bias scoring framework identifying "
    "317 gene targets with sex-differential safety profiles.",
    body))
s.append(Paragraph(
    "The manuscript addresses a critical gap: no existing bioinformatics tool or knowledge graph provides systematic "
    "sex-differential drug safety analysis. All data sources use open licenses (CC-BY 4.0, Public Domain, CC-BY-SA 3.0).",
    body))
s.append(Paragraph(
    "All data and code are publicly available (GitHub: jshaik369/SexDiffKG, Zenodo DOI: 10.5281/zenodo.18819192).",
    body))
s.append(Paragraph(SIGN, body))
make_pdf("SexDiffKG_BriefBioinform_CoverLetter.pdf", s)

# ========== 3. Scientific Data ==========
print("3. Scientific Data...")
s = []
s.append(Paragraph("Cover Letter - Scientific Data", title))
s.append(Spacer(1, 12))
s.append(Paragraph("Dear Editors,", body))
s.append(Paragraph(
    'We submit the manuscript entitled "SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph from 14.5 Million '
    'FDA Adverse Event Reports" for consideration as a Data Descriptor in Scientific Data.',
    body))
s.append(Paragraph(
    "SexDiffKG is a publicly available knowledge graph resource for sex-differential pharmacovigilance at scale. "
    "The resource integrates five open-access biomedical databases - FAERS (14.5M reports, 2004-2025), "
    "ChEMBL 36, STRING v12.0, Reactome, and GTEx v8 - into a graph of 109,867 nodes (6 entity types) "
    "and 1,822,851 edges (6 relation types), including 96,281 sex-differential drug-adverse event signals. "
    "Drug names are normalized via a 4-tier pipeline (DiAna dictionary + ChEMBL + FDA prod_ai) achieving "
    "53.9% active-ingredient resolution.",
    body))
s.append(Paragraph(
    "The dataset includes ComplEx knowledge graph embeddings (MRR 0.248, Hits@10 40.7%), sex-bias scores for "
    "317 gene targets, and validation against 40 literature benchmarks (82.8% directional precision). "
    "All artifacts are deposited on Zenodo (DOI: 10.5281/zenodo.18819192) under CC-BY 4.0 license. "
    "All data sources are open-access, with no restrictive licensing (KEGG replaced by Reactome CC-BY 4.0).",
    body))
s.append(Paragraph(SIGN, body))
make_pdf("SexDiffKG_SciData_CoverLetter.pdf", s)

# ========== 4. Biology of Sex Differences ==========
print("4. Biology of Sex Differences...")
s = []
s.append(Paragraph("Cover Letter - Biology of Sex Differences", title))
s.append(Spacer(1, 12))
s.append(Paragraph("Dear Editors,", body))
s.append(Paragraph(
    'We submit the manuscript entitled "SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph from 14.5 Million '
    'FDA Adverse Event Reports" for consideration as a Research article in Biology of Sex Differences.',
    body))
s.append(Paragraph(
    "This manuscript directly addresses the journal's core mission: understanding sex-based biological differences "
    "with clinical relevance. SexDiffKG is the first knowledge graph purpose-built to capture sex-differential drug "
    "safety patterns, constructed from 14.5 million FDA adverse event reports integrated with molecular target data.",
    body))
s.append(Paragraph(
    "Key findings: (1) 96,281 sex-differential drug-adverse event signals (53.8% female-biased), quantifying the "
    "sex-differential ADR landscape at unprecedented scale; (2) HDAC inhibitors show female-biased safety profiles, "
    "with implications for cancer therapy where sex-differential epigenetic regulation may modulate drug response; "
    "(3) ESR1-targeting drugs show paradoxical male-biased safety; (4) Novel targets: GNRHR and SRD5A1/3 exclusively "
    "female-biased, PTGER3 and OXTR exclusively male-biased; (5) Signal validation achieves 82.8% directional "
    "precision against 40 literature benchmarks.",
    body))
s.append(Paragraph(
    "With 317 gene targets showing sex-biased drug safety profiles, SexDiffKG provides a systematic resource for "
    "researchers studying sex-based differences in pharmacology and precision medicine.",
    body))
s.append(Paragraph(SIGN, body))
make_pdf("SexDiffKG_BiolSexDiff_CoverLetter.pdf", s)

# ========== 5. Drug Safety ==========
print("5. Drug Safety...")
s = []
s.append(Paragraph("Cover Letter - Drug Safety", title))
s.append(Spacer(1, 12))
s.append(Paragraph("Dear Editors,", body))
s.append(Paragraph(
    'We submit the manuscript entitled "SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph from 14.5 Million '
    'FDA Adverse Event Reports" for consideration in Drug Safety.',
    body))
s.append(Paragraph(
    "Drug Safety is the premier journal for pharmacovigilance research, making it the natural venue for SexDiffKG - "
    "the first systematic computational approach to sex-differential drug safety analysis at scale. Women experience "
    "ADRs at 1.5-1.7x the rate of men, yet pharmacovigilance databases lack integrated sex-differential analysis.",
    body))
s.append(Paragraph(
    "SexDiffKG processes 14,536,008 FAERS reports (2004-2025) with drug names normalized via DiAna dictionary "
    "(53.9% active-ingredient resolution). Sex-stratified ROR analysis identifies 96,281 sex-differential signals. "
    "Signal validation against 40 literature benchmarks achieves 82.8% directional precision, a 19.5 percentage-point "
    "improvement over our initial pipeline, driven by DiAna-based drug normalization that eliminates variant-driven "
    "false positives.",
    body))
s.append(Paragraph(
    "Integration with ChEMBL 36 drug-target annotations enables target-level analysis identifying 317 gene targets "
    "with sex-differential safety profiles. ComplEx knowledge graph embeddings (MRR 0.248, AMRI 0.990) demonstrate "
    "the feasibility of computational sex-aware safety prediction. All data are publicly available under CC-BY 4.0.",
    body))
s.append(Paragraph(SIGN, body))
make_pdf("SexDiffKG_DrugSafety_CoverLetter.pdf", s)

print("\nAll v4 submission PDFs generated!")
