#!/usr/bin/env python3.13
"""Generate supplementary materials PDF for bioRxiv submission."""

import os
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, gray
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, HRFlowable
)
from reportlab.lib import colors

OUTPUT_DIR = os.path.expanduser("~/sexdiffkg/results")
SUPP_DIR = os.path.join(OUTPUT_DIR, "supplementary")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "SexDiffKG_supplementary.pdf")

styles = getSampleStyleSheet()

title_style = ParagraphStyle('SuppTitle', parent=styles['Title'],
    fontSize=16, leading=20, fontName='Times-Bold', alignment=TA_CENTER)
table_title = ParagraphStyle('TableTitle', parent=styles['Normal'],
    fontSize=11, leading=14, fontName='Times-Bold', spaceBefore=12, spaceAfter=6)
caption_style = ParagraphStyle('Caption', parent=styles['Normal'],
    fontSize=9, leading=11, fontName='Times-Italic', spaceAfter=8, spaceBefore=4, alignment=TA_CENTER)
cell_style = ParagraphStyle('Cell', parent=styles['Normal'],
    fontSize=7, leading=9, fontName='Times-Roman')
cell_bold = ParagraphStyle('CellBold', parent=cell_style, fontName='Times-Bold')
normal_style = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, leading=13, fontName='Times-Roman', spaceAfter=6)

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.setFillColor(gray)
    canvas.drawCentredString(letter[0]/2, 0.5*inch, f"S-{canvas.getPageNumber()}")
    canvas.setFont('Times-Italic', 8)
    canvas.drawString(inch, letter[1] - 0.5*inch, "SexDiffKG \u2014 Supplementary Materials")
    canvas.restoreState()

def read_tsv(filepath):
    """Read a TSV file, return headers and rows."""
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        headers = next(reader)
        rows = [row for row in reader]
    return headers, rows

def make_table_from_tsv(filepath, col_widths=None, max_rows=None):
    headers, rows = read_tsv(filepath)
    if max_rows:
        rows = rows[:max_rows]
    
    data = [[Paragraph(h, cell_bold) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c) if c else "", cell_style) for c in row])
    
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E0E0E0')),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor('#CCCCCC')),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F8F8')]),
    ]))
    return t

def add_figure(story, fig_path, caption_text, width=5.5*inch):
    if os.path.exists(fig_path):
        img = Image(fig_path, width=width, height=width*0.7)
        story.append(img)
        story.append(Paragraph(caption_text, caption_style))
        story.append(Spacer(1, 8))
    else:
        story.append(Paragraph(f"[Figure not found: {os.path.basename(fig_path)}]", normal_style))

def build_pdf():
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.85*inch, bottomMargin=0.85*inch)
    story = []
    W = letter[0] - 1.5*inch

    # Title page
    story.append(Spacer(1, 40))
    story.append(Paragraph("Supplementary Materials", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "SexDiffKG: A Sex-Differential Drug Safety Knowledge Graph<br/>"
        "from 14.5 Million FDA Adverse Event Reports",
        ParagraphStyle('SubTitle', parent=styles['Normal'],
            fontSize=12, leading=15, fontName='Times-Roman', alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("JShaik", ParagraphStyle('Auth', parent=styles['Normal'],
        fontSize=10, alignment=TA_CENTER, fontName='Times-Roman')))
    story.append(Paragraph("CoEvolve Network, Barcelona, Spain", 
        ParagraphStyle('Aff', parent=styles['Normal'],
            fontSize=9, alignment=TA_CENTER, fontName='Times-Italic', textColor=HexColor('#666666'))))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#AAAAAA')))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Contents: 10 Supplementary Tables (S1\u2013S10) and 11 Figures (1\u20136, S1\u2013S5)", normal_style))
    story.append(PageBreak())

    # ---- SUPPLEMENTARY TABLES ----
    tables_info = [
        ("Table S1", "KG Statistics Summary", "TableS1_KG_Statistics.tsv", None),
        ("Table S2", "Top 50 Female-Biased Strong Signals", "TableS2_Top50_Female_Biased_Signals.tsv", 25),
        ("Table S3", "Top 50 Male-Biased Strong Signals", "TableS3_Top50_Male_Biased_Signals.tsv", 25),
        ("Table S4", "Gene Target Sex-Bias Scores (429 targets)", "TableS4_Gene_Target_Sex_Bias_Scores.tsv", 30),
        ("Table S5", "Drug Cluster Profiles (K=20)", "TableS5_Cluster_Profiles.tsv", None),
        ("Table S6", "Embedding Parameters: DistMult vs RotatE", "TableS6_Embedding_Parameters.tsv", None),
        ("Table S7", "Signal Validation Benchmarks (15 drugs)", "TableS7_Signal_Validation_Benchmarks.tsv", None),
        ("Table S8", "Top 100 Drugs by Signal Count", "TableS8_Top100_Drugs_By_Signal_Count.tsv", 30),
        ("Table S9", "Top 100 Adverse Events by Signal Count", "TableS9_Top100_AEs_By_Signal_Count.tsv", 30),
        ("Table S10", "Data Source Provenance", "TableS10_Data_Provenance.tsv", None),
    ]

    for tname, tdesc, tfile, max_rows in tables_info:
        fpath = os.path.join(SUPP_DIR, tfile)
        if os.path.exists(fpath):
            story.append(Paragraph(f"<b>{tname}.</b> {tdesc}", table_title))
            if max_rows:
                story.append(Paragraph(f"(Showing first {max_rows} rows; full table available in supplementary data files)", caption_style))
            story.append(make_table_from_tsv(fpath, max_rows=max_rows))
            story.append(PageBreak())

    # ---- FIGURES ----
    story.append(Paragraph("<b>Supplementary Figures</b>", title_style))
    story.append(Spacer(1, 12))

    figures = [
        ("fig1_drug_pca_clusters.png", "<b>Figure 1.</b> Drug embedding PCA clusters (29,201 drugs, 20 clusters, 61.9% variance explained)."),
        ("fig2_signal_distribution.png", "<b>Figure 2.</b> Distribution of sex-differential signals and signal filtering pipeline."),
        ("fig3_kg_overview.png", "<b>Figure 3.</b> Knowledge graph composition: node and edge type distributions."),
        ("fig4_target_sex_bias.png", "<b>Figure 4.</b> Gene target sex-bias scores: top female-biased and male-biased targets."),
        ("fig5_faers_summary.png", "<b>Figure 5.</b> FAERS data summary and demographic breakdown by sex."),
        ("fig6_cluster_profiles.png", "<b>Figure 6.</b> Embedding cluster sex-differential profiles."),
        ("figS1_signal_ratio_distribution.png", "<b>Figure S1.</b> Full ln(ROR ratio) distribution for 49,026 strong signals."),
        ("figS2_report_count_scatter.png", "<b>Figure S2.</b> Sex-stratified report count scatter plot (log scale)."),
        ("figS3_top20_drugs.png", "<b>Figure S3.</b> Top 20 drugs by sex-differential signal count."),
        ("figS4_target_bias_distribution.png", "<b>Figure S4.</b> Target sex-bias score distribution across 429 targets."),
        ("figS5_embedding_quality.png", "<b>Figure S5.</b> Embedding quality assessment: cosine similarity and PCA variance."),
    ]

    for fname, caption in figures:
        fpath = os.path.join(FIG_DIR, fname)
        add_figure(story, fpath, caption)
        story.append(Spacer(1, 6))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Supplementary PDF: {OUTPUT_PDF}")
    print(f"Size: {os.path.getsize(OUTPUT_PDF):,} bytes")

if __name__ == "__main__":
    build_pdf()
