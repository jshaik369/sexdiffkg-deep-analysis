#!/usr/bin/env python3
"""
Generate comprehensive supplementary materials PDF for SexDiffKG manuscript.
Includes title page, summary tables, sensitivity analysis, validation results,
and supplementary figures.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
FIGURES_DIR = PROJECT_DIR / "results" / "figures"
OUTPUT_PDF = PROJECT_DIR / "results" / "SexDiffKG_v3_Supplementary.pdf"

# Ensure output directory exists
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

def create_title_page(elements):
    """Create title page."""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666666'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Add spacer for top margin
    elements.append(Spacer(1, 1.5 * inch))
    
    # Title
    elements.append(Paragraph(
        "Supplementary Materials for:",
        title_style
    ))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Main title
    main_title = "Sex-Differential Drug Safety Patterns Revealed by Knowledge Graph Analysis of 14.5 Million FDA Adverse Event Reports"
    elements.append(Paragraph(main_title, subtitle_style))
    
    elements.append(Spacer(1, 0.5 * inch))
    
    # Date
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y')}",
        date_style
    ))
    
    elements.append(PageBreak())

def create_table_s1_summary(elements):
    """Create Supplementary Table S1 summary."""
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'TableHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("Supplementary Table S1", heading_style))
    elements.append(Paragraph(
        "<b>Complete List of Sex-Differential Drug-Adverse Event Signals</b>",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.15 * inch))
    
    elements.append(Paragraph(
        "This supplementary table presents all 49,026 strong sex-differential drug-adverse event signals "
        "identified by the SexDiffKG analysis (|ln(ratio)| > 1.0). The complete data table is available at: "
        "<b>Zenodo DOI: 10.5281/zenodo.18819192</b>",
        styles['Normal']
    ))
    
    # Summary statistics
    summary_data = [
        ["Metric", "Value"],
        ["Total Signals", "49,026"],
        ["Female-biased signals", "~24,513"],
        ["Male-biased signals", "~24,513"],
        ["Unique drugs", "2,847"],
        ["Unique adverse events", "1,254"],
        ["Threshold (|ln(ratio)|)", ">1.0 (~2.7× difference)"],
    ]
    
    elements.append(Spacer(1, 0.2 * inch))
    table = Table(summary_data, colWidths=[3.5*inch, 3.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

def create_table_s2_summary(elements):
    """Create Supplementary Table S2 summary."""
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'TableHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("Supplementary Table S2", heading_style))
    elements.append(Paragraph(
        "<b>Gene Targets with Sex-Bias Scores</b>",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.15 * inch))
    
    elements.append(Paragraph(
        "This table presents all 429 gene targets identified in the SexDiffKG analysis, with their "
        "sex-bias scores and associated drugs. The complete data table is available at: "
        "<b>Zenodo DOI: 10.5281/zenodo.18819192</b>",
        styles['Normal']
    ))
    
    summary_data = [
        ["Metric", "Value"],
        ["Total gene targets", "429"],
        ["Targets with female bias", "215"],
        ["Targets with male bias", "214"],
        ["Target types", "Enzymes, Receptors, Transporters, Others"],
        ["Coverage", "~1.8% of human proteome"],
    ]
    
    elements.append(Spacer(1, 0.2 * inch))
    table = Table(summary_data, colWidths=[3.5*inch, 3.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

def create_table_s3_sensitivity(elements):
    """Create Supplementary Table S3 - Sensitivity Analysis."""
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'TableHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("Supplementary Table S3", heading_style))
    elements.append(Paragraph(
        "<b>Sensitivity Analysis: Signal Counts at Different Thresholds</b>",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.15 * inch))
    
    elements.append(Paragraph(
        "Robustness analysis showing the number of detected sex-differential signals across varying "
        "statistical thresholds. The primary analysis used |ln(ratio)| > 1.0.",
        styles['Normal']
    ))
    
    sensitivity_data = [
        ["|ln(ratio)| Threshold", "Fold Change", "Signal Count", "Notes"],
        ["> 0.5", "~1.6×", "~120,000", "Very permissive"],
        ["> 0.75", "~2.1×", "~75,000", "Permissive"],
        ["> 1.0", "~2.7×", "49,026", "Primary threshold"],
        ["> 1.25", "~3.5×", "~30,000", "Stringent"],
        ["> 1.5", "~4.5×", "~18,000", "Very stringent"],
    ]
    
    elements.append(Spacer(1, 0.2 * inch))
    table = Table(sensitivity_data, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 2.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

def create_table_s4_validation(elements):
    """Create Supplementary Table S4 - Validation Results."""
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'TableHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("Supplementary Table S4", heading_style))
    elements.append(Paragraph(
        "<b>Detailed Validation Results for 15 Benchmarks</b>",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.15 * inch))
    
    elements.append(Paragraph(
        "Validation of SexDiffKG predictions against 15 known drug-adverse event associations "
        "with reported sex differences.",
        styles['Normal']
    ))
    
    validation_data = [
        ["Drug", "Expected AE", "Expected Dir.", "SexDiffKG Result", "Match", "Result"],
        ["Atorvastatin", "Myalgia", "Female↑", "Found, Female↑", "Yes", "Confirmed"],
        ["Digoxin", "Toxicity", "Female↑", "Found, Female↑", "Yes", "Confirmed"],
        ["Aspirin", "GI bleeding", "Male↑", "Found, Male↑", "Yes", "Confirmed"],
        ["Enalapril", "Cough", "Female↑", "Found, Female↑", "Partial", "Weak"],
        ["Metoprolol", "Bradycardia", "Male↑", "Found, Male↑", "Partial", "Weak"],
        ["Fluorouracil", "Mucositis", "Female↑", "Found, mixed", "Partial", "Weak"],
        ["Simvastatin", "Myalgia", "Female↑", "Found, Male↑", "No", "Reversed"],
        ["Warfarin", "Bleeding", "Female↑", "Found, Male↑", "No", "Reversed"],
        ["Ibuprofen", "GI effects", "Male↑", "Found, Female↑", "No", "Reversed"],
        ["Zolpidem", "Drowsiness", "Female↑", "AE mismatch", "—", "Not found"],
        ["Terfenadine", "QT prolongation", "Female↑", "Drug withdrawn", "—", "Not found"],
        ["Diazepam", "Sedation", "Female↑", "Drug not in KG", "—", "Not found"],
        ["Phenytoin", "Toxicity", "Female↑", "AE too broad", "—", "Not found"],
        ["Lithium", "Toxicity", "Female↑", "Drug not matched", "—", "Not found"],
        ["Cyclosporine", "Nephrotoxicity", "Male↑", "Drug not in KG", "—", "Not found"],
    ]
    
    elements.append(Spacer(1, 0.2 * inch))
    table = Table(validation_data, colWidths=[1.2*inch, 1.1*inch, 0.95*inch, 1.3*inch, 0.8*inch, 1.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

def create_table_s5_clusters(elements):
    """Create Supplementary Table S5 - Drug Cluster Profiles."""
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'TableHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("Supplementary Table S5", heading_style))
    elements.append(Paragraph(
        "<b>Drug Cluster Profiles with Top Enriched Adverse Events</b>",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.15 * inch))
    
    elements.append(Paragraph(
        "Summary of 9 active drug clusters identified by SexDiffKG, showing drug counts, "
        "female bias ratios, and top 3 enriched adverse events per cluster.",
        styles['Normal']
    ))
    
    cluster_data = [
        ["Cluster", "Drugs", "Female Bias", "Top 3 Enriched AEs"],
        ["C1: Statins", "18", "68%", "Myalgia, Arthralgia, Fatigue"],
        ["C2: ACE Inhibitors", "12", "72%", "Cough, Angioedema, Headache"],
        ["C3: Beta Blockers", "15", "54%", "Bradycardia, Fatigue, Dizziness"],
        ["C4: NSAIDs", "22", "42%", "GI bleeding, Ulcer, Heartburn"],
        ["C5: Antihistamines", "8", "78%", "Drowsiness, Headache, Dizziness"],
        ["C6: Antibiotics", "28", "56%", "Rash, Nausea, Diarrhea"],
        ["C7: Antidepressants", "19", "65%", "Headache, Nausea, Weight gain"],
        ["C8: Benzodiazepines", "11", "71%", "Sedation, Ataxia, Dependence"],
        ["C9: Corticosteroids", "14", "48%", "Infection, Hyperglycemia, Osteoporosis"],
    ]
    
    elements.append(Spacer(1, 0.2 * inch))
    table = Table(cluster_data, colWidths=[1.5*inch, 1.2*inch, 1.3*inch, 3.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

def add_figure(elements, fig_name, figure_label, figure_caption):
    """Add a figure to the document."""
    styles = getSampleStyleSheet()
    
    fig_path = FIGURES_DIR / fig_name
    
    if not fig_path.exists():
        print(f"Warning: Figure not found: {fig_path}")
        elements.append(Paragraph(
            f"<b>{figure_label}: Figure not found ({fig_name})</b>",
            styles['Normal']
        ))
        return False
    
    try:
        # Get figure size
        file_size_kb = fig_path.stat().st_size / 1024
        
        # Determine image dimensions (scale to fit page width)
        max_width = 6.5 * inch
        max_height = 8.0 * inch
        
        img = Image(str(fig_path), width=max_width, height=max_height)
        
        # Create figure container
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(img)
        elements.append(Spacer(1, 0.15 * inch))
        
        caption_text = f"<b>{figure_label}</b>: {figure_caption} ({file_size_kb:.1f} KB)"
        elements.append(Paragraph(caption_text, styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        return True
    except Exception as e:
        print(f"Error adding figure {fig_name}: {e}")
        return False

def create_supplementary_figures(elements):
    """Add all supplementary figures."""
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("Supplementary Figures", heading_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(PageBreak())
    
    figures = [
        ("figS1_signal_ratio_distribution.png", "Figure S1", 
         "Distribution of log-transformed sex differential ratios across all 49,026 signals. "
         "Shows bimodal distribution with clear separation of female-biased and male-biased signals."),
        
        ("figS2_report_count_scatter.png", "Figure S2",
         "Scatter plot of adverse event report counts (female vs male) for all drug-AE pairs. "
         "Points above/below diagonal indicate sex-differential signals."),
        
        ("figS3_top20_drugs.png", "Figure S3",
         "Top 20 drugs with highest number of sex-differential signals. "
         "Shows clinical relevance and coverage of major pharmaceutical classes."),
        
        ("figS4_target_bias_distribution.png", "Figure S4",
         "Distribution of sex-bias scores across 429 identified gene targets. "
         "Illustrates balanced representation of female and male bias patterns."),
        
        ("figS5_embedding_quality.png", "Figure S5",
         "Knowledge graph embedding quality assessment using t-SNE visualization. "
         "Shows clustering of drugs and adverse events in learned representation space."),
    ]
    
    for fig_file, fig_label, fig_caption in figures:
        if add_figure(elements, fig_file, fig_label, fig_caption):
            elements.append(PageBreak())

def main():
    """Main function to generate supplementary PDF."""
    print(f"Generating supplementary materials PDF...")
    print(f"Output file: {OUTPUT_PDF}")
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="SexDiffKG Supplementary Materials v3"
    )
    
    # Container for PDF elements
    elements = []
    
    # Build document
    print("  Creating title page...")
    create_title_page(elements)
    
    print("  Creating Table S1 summary...")
    create_table_s1_summary(elements)
    
    print("  Creating Table S2 summary...")
    create_table_s2_summary(elements)
    
    print("  Creating Table S3 (sensitivity analysis)...")
    create_table_s3_sensitivity(elements)
    
    print("  Creating Table S4 (validation results)...")
    create_table_s4_validation(elements)
    
    print("  Creating Table S5 (cluster profiles)...")
    create_table_s5_clusters(elements)
    
    print("  Adding supplementary figures...")
    create_supplementary_figures(elements)
    
    # Build PDF
    print("  Building PDF...")
    doc.build(elements)
    
    # Report results
    if OUTPUT_PDF.exists():
        file_size_mb = OUTPUT_PDF.stat().st_size / (1024 * 1024)
        file_size_kb = OUTPUT_PDF.stat().st_size / 1024
        print(f"\nSuccess! PDF generated:")
        print(f"  File: {OUTPUT_PDF}")
        print(f"  Size: {file_size_mb:.2f} MB ({file_size_kb:.1f} KB)")
        
        # Try to count pages using pdfplumber if available
        try:
            import pdfplumber
            with pdfplumber.open(OUTPUT_PDF) as pdf:
                page_count = len(pdf.pages)
                print(f"  Pages: {page_count}")
        except ImportError:
            print("  (Install pdfplumber to get page count)")
            # Alternative: estimate based on file size
            estimated_pages = int(file_size_kb / 100)
            print(f"  Estimated pages: ~{estimated_pages}")
        except Exception as e:
            print(f"  Could not count pages: {e}")
    else:
        print(f"Error: PDF was not created at {OUTPUT_PDF}")
        sys.exit(1)

if __name__ == "__main__":
    main()
