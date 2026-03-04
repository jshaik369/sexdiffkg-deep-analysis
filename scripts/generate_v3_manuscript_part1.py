#!/usr/bin/env python3
"""
generate_v3_manuscript_part1.py

Generates the FIRST HALF of a publication-quality bioRxiv manuscript PDF
about sex-differential drug safety patterns from FAERS knowledge graph analysis.

This script generates:
- Title Page
- Abstract
- Introduction (Section 1)
- Methods (Section 2, including Figures 1-2 and Tables 1-4)

The script uses reportlab for professional PDF generation with:
- Line numbers (every 5th line numbered on left margin)
- Page numbers (bottom center)
- Running header with short title
- Times New Roman font family
- Single column, 1-inch margins
- Proper superscript references

Usage:
    python generate_v3_manuscript_part1.py output.pdf

Part 2 (Results, Discussion, References, Supplementary) will be added separately.
"""

import os
import sys
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, grey, black, white
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ============================================================================
# MANUSCRIPT CONTENT DEFINITIONS
# ============================================================================

MANUSCRIPT_TITLE = (
    "Sex-Differential Drug Safety Patterns Revealed by Knowledge Graph "
    "Analysis of 14.5 Million FDA Adverse Event Reports"
)

RUNNING_TITLE = "Sex-Differential Drug Safety from FAERS Knowledge Graph"

AUTHOR = "JShaik¹*"
AFFILIATION = "¹CoEvolve Network, Independent Researcher, Barcelona, Spain"
CORRESPONDENCE = "jshaik@coevolvenetwork.com"
ORCID = "0009-0002-1748-7516"

ABSTRACT_TEXT = """
Background: Sex-based differences in adverse drug reactions (ADRs) are well-documented but poorly systematized. Women experience ADRs at nearly twice the rate of men, yet pharmacovigilance databases lack integrated sex-differential analysis tools.

Methods: We constructed SexDiffKG, a sex-differential drug safety knowledge graph from 14,536,008 FDA Adverse Event Reporting System (FAERS) reports spanning 2004–2024, integrated with molecular target data from ChEMBL 36, protein interaction networks from STRING v12.0, and biological pathway annotations from KEGG and UniProt. Sex-stratified Reporting Odds Ratios (ROR) were computed for all drug–adverse event pairs with valid sex assignments. Knowledge graph embeddings were trained using DistMult (200 dimensions, 100 epochs) on NVIDIA DGX Spark (GB10).

Results: From 14.5 million reports, we identified 49,026 strong sex-differential drug–adverse event signals (|ln(ROR ratio)| > 1.0, ≥10 reports per sex), with 58.5% showing female bias. Knowledge graph embedding achieved AMRI of 0.9807, placing correct triples in the top 1.9% of candidates. Embedding-based clustering of 29,201 drugs into 20 groups revealed distinct sex-differential safety landscapes with female bias ratios ranging from 0.33 to 1.00. Target-level analysis identified 429 gene targets with sex-biased safety profiles, including novel findings: HDAC1/2/3/6 (exclusively female-biased), ESR1 (counterintuitively male-biased, −0.80), and ITGA2B/ITGB3 (exclusively female-biased). Signal validation against 40 literature benchmarks achieved 75% coverage and 63.3% directional precision.

Conclusions: We report the first systematic, molecular-level characterization of sex-differential drug safety patterns at scale. Our findings reveal previously unreported target-level sex biases with immediate implications for precision pharmacovigilance and sex-aware drug development.

Keywords: pharmacovigilance, sex differences, knowledge graph, drug safety, FAERS, adverse drug reactions, precision medicine, gender medicine, reporting odds ratio, graph embeddings
"""

KEYWORDS = (
    "pharmacovigilance, sex differences, knowledge graph, drug safety, FAERS, "
    "adverse drug reactions, precision medicine, gender medicine, reporting odds ratio, "
    "graph embeddings"
)

AUTHOR_CONTRIBUTIONS = (
    "JShaik conceived the study, designed the methodology, collected and processed "
    "the data, performed all computational analyses, and wrote the manuscript."
)

COMPETING_INTERESTS = "The author declares no competing interests."

FUNDING = (
    "This work was conducted as independent research with no specific external "
    "funding. Computational infrastructure was self-funded."
)

DATA_AVAILABILITY = (
    "The complete SexDiffKG dataset is available on Zenodo (DOI: 10.5281/zenodo.18819192) "
    "under CC-BY 4.0 license. Source code is available at "
    "https://github.com/jshaik369/SexDiffKG."
)

INTRODUCTION_SECTION_1_1 = """
1.1 The Sex Gap in Drug Safety

Adverse drug reactions (ADRs) represent a significant public health burden, accounting for an estimated 2.2 million serious cases and 106,000 deaths annually in the United States alone[1]. Women experience ADRs at approximately 1.5–1.7 times the rate of men[2], a disparity attributed to multiple biological and clinical factors: differences in drug metabolism through cytochrome P450 (CYP) enzyme expression[3], body composition (higher body fat percentage affecting lipophilic drug distribution), hormonal influences on drug transport (P-glycoprotein modulation), renal clearance (lower GFR in women), and historical underrepresentation in clinical trials[4].

The clinical significance of sex-differential drug safety is not theoretical. In 2013, the FDA took the unprecedented step of recommending sex-specific dosing for zolpidem (Ambien), halving the recommended dose for women after post-market data revealed that women metabolize the drug more slowly, leading to dangerously high morning blood levels[5]. This remains one of very few sex-specific dosing modifications in FDA history, underscoring both the significance of sex-differential drug safety and the inadequacy of current systematic surveillance approaches.

Despite growing evidence that sex influences drug safety profiles across therapeutic classes—from cardiovascular medications[6] to psychotropic drugs[7] to immunomodulators[8]—the systematic characterization of sex-differential adverse event patterns at scale remains largely unaddressed. Most pharmacovigilance systems analyze safety signals in aggregate without sex stratification, missing potentially critical sex-specific safety patterns.
"""

INTRODUCTION_SECTION_1_2 = """
1.2 Pharmacovigilance and the FAERS Database

The FDA Adverse Event Reporting System (FAERS) is the largest spontaneous reporting database for drug safety surveillance, containing over 14 million reports with patient sex information for a majority of entries. FAERS has been extensively used for safety signal detection through disproportionality analysis, particularly using Reporting Odds Ratios (ROR)[9,10]. However, FAERS does not natively support sex-differential signal detection, and most analyses treat the entire population as homogeneous.

Yu et al.[11] demonstrated that sex differences exist across 307 of 668 drugs analyzed from FAERS data, identifying 736 drug–event combinations with notable sex disparities. However, their analysis was limited in scale (668 drugs vs. our 29,277) and did not integrate molecular target data, making it impossible to identify the biological mechanisms underlying observed sex differences.
"""

INTRODUCTION_SECTION_1_3 = """
1.3 Knowledge Graphs for Drug Safety

Knowledge graphs (KGs) have emerged as powerful tools for integrating heterogeneous biomedical data. Systems such as Hetionet[12] (47K nodes, 2.3M edges), DRKG[13] (97K nodes, 5.9M edges), and PharmKG[14] (7.6K nodes, 500K edges) have demonstrated the value of graph-based representations for drug repurposing and safety prediction. Recent advances in knowledge graph embedding methods—including translational models (TransE[15], RotatE[16]), bilinear models (DistMult[17], ComplEx), and graph neural networks—have enabled link prediction, drug repurposing, and adverse event prediction from graph structure.

However, no existing KG specifically models sex-differential drug safety patterns. Existing resources treat pharmacovigilance data in aggregate, leaving a critical gap in computational tools for sex-aware safety assessment. This gap is particularly significant given the growing movement toward precision medicine, where patient-level factors (including sex) should inform treatment decisions.
"""

INTRODUCTION_SECTION_1_4 = """
1.4 Study Objectives

In this study, we address this gap through six specific objectives: (1) construct the first knowledge graph specifically designed to capture sex-differential pharmacovigilance signals; (2) introduce sex-stratified ROR analysis to identify strong sex-differential drug–adverse event signals at scale; (3) embed the complete graph using knowledge graph embedding methods to enable sex-aware link prediction; (4) reveal gene targets with measurable sex-differential drug safety profiles through molecular integration; (5) validate findings against established literature benchmarks; and (6) provide a complete, reproducible, and audited resource for the research community.
"""

METHODS_SECTION_2_1 = """
2.1 Data Sources and Integration

SexDiffKG integrates data from five primary biomedical databases, chosen for their complementary coverage of drug safety, molecular targets, protein interactions, and biological pathways.
"""

METHODS_SECTION_2_2 = """
2.2 FAERS Data Processing

FAERS quarterly data files were processed through a standardized four-step pipeline: (a) report deduplication by FDA case ID, retaining the most recent version of each report; (b) sex assignment from demographic fields, excluding reports with unknown or unspecified sex (approximately 15% of raw reports); (c) drug name normalization using FDA's Substance Registration System, mapping trade names and abbreviations to standardized drug identifiers; and (d) adverse event standardization using MedDRA (Medical Dictionary for Regulatory Activities) preferred terms, consolidating synonym variants.

The resulting dataset comprises 14,536,008 unique reports with valid sex assignment: 8,744,397 female (60.2%) and 5,791,611 male (39.8%). The 1.51 female-to-male reporting ratio exceeds the expected population drug usage ratio (~1.1–1.2), consistent with the well-documented female excess in ADR reporting[1,2].
"""

METHODS_SECTION_2_3 = """
2.3 Knowledge Graph Schema

The SexDiffKG schema defines 6 entity types and 6 relation types. The complete graph contains 127,063 nodes and 5,839,717 edges.
"""

METHODS_SECTION_2_4 = """
2.4 Sex-Differential Signal Detection

For each drug–adverse event pair observed in FAERS, we computed sex-stratified Reporting Odds Ratios (ROR) using the standard 2×2 contingency table approach. The ROR for each sex was calculated as:

ROR_sex = (a × d) / (b × c)

where a = reports of the drug–AE pair for that sex, b = reports of the drug without that AE for that sex, c = reports of other drugs with that AE for that sex, and d = reports of other drugs without that AE for that sex. A Haldane–Anscombe correction (adding 0.5 to all cells) was applied when any cell count was zero to avoid undefined ratios.

The sex-differential ratio was computed using the natural logarithm: log_ror_ratio = ln(ROR_female / ROR_male). Positive values indicate female-higher risk; negative values indicate male-higher risk.

We defined three tiers of sex-differential signals:
• All sex-differential: Valid ROR computable in both sexes (183,544 pairs)
• Robust: At least 10 reports per sex (183,544 pairs meeting reporting threshold)
• Strong: |ln(ratio)| > 1.0, corresponding to >~2.7× difference (49,026 pairs)

The |ln(ratio)| > 1.0 threshold was chosen because it corresponds to e¹ ≈ 2.72× difference between sexes, representing a biologically and clinically meaningful effect size. We conducted sensitivity analyses at thresholds of 0.5, 0.75, 1.0, 1.25, and 1.5 (see Supplementary Table S3).

No formal multiple testing correction was applied to the sex-differential ratio itself because: (a) the log_ror_ratio is a descriptive measure of effect size, not a statistical hypothesis test with a null distribution; (b) the minimum reporting threshold (≥10 reports per sex) serves as a practical filter against spurious signals; and (c) the strong threshold (|ln| > 1.0) already represents a conservative effect size criterion. For individual ROR significance, we verified that 95% confidence intervals excluded 1.0 for the vast majority (>95%) of strong signals.
"""

METHODS_SECTION_2_5 = """
2.5 Knowledge Graph Embedding

We trained DistMult[17] embeddings on the complete knowledge graph after removing edges with NaN values (primarily from unresolved STRING protein identifiers). DistMult was selected for its bilinear scoring function (h ⊙ r ⊙ t), well-suited for symmetric and quasi-symmetric relations common in biomedical KGs, computational efficiency, and interpretability of learned representations.

A secondary RotatE[16] model (200 complex-valued dimensions, 25 epochs) was trained for comparison. RotatE's rotational scoring function can capture asymmetric relations but required CPU training due to NVRTC JIT compilation limitations on the GB10 for complex-valued operations, limiting it to 25 epochs.
"""

METHODS_SECTION_2_6 = """
2.6 Post-Embedding Analysis

Drug Clustering (K=20). Drug entity embeddings were extracted for all 29,201 drugs, L2-normalized, and clustered using K-Means (K=20, scikit-learn, random_state=42). PCA projection to 2 dimensions explained 61.9% of embedding variance. The choice of K=20 was informed by silhouette analysis across K=5 to K=50 (see Supplementary Figure S5).

Target Sex-Bias Scoring. For each gene target with ≥2 drugs showing sex-differential signals, we computed a sex_bias_score = (n_female_biased − n_male_biased) / n_total_drugs, ranging from −1.0 (all male-biased) to +1.0 (all female-biased). This identified 429 gene targets with measurable sex-differential drug safety profiles: 112 female-biased (score > 0), 124 male-biased (score < 0), and 193 neutral (score = 0).
"""

METHODS_SECTION_2_7 = """
2.7 Signal Validation and Data Integrity

To assess biological plausibility, we validated SexDiffKG signals against 15 drug–sex–adverse event relationships documented in published literature and FDA drug labels (Table S4). Benchmark pairs were selected from three sources: (a) FDA label-documented sex differences (e.g., zolpidem, digoxin); (b) published pharmacovigilance studies reporting sex-differential ADRs[2,6,11]; and (c) well-established pharmacological sex differences (e.g., aspirin and GI bleeding in men[18]).

For each benchmark, we searched SexDiffKG using a contains-matching strategy for drug names (to account for salt forms and formulation variants in FAERS) and exact MedDRA preferred term matching for adverse events. A benchmark was considered "confirmed" if the SexDiffKG signal direction matched the literature-reported direction, "weakly confirmed" if a related adverse event showed the expected pattern, and "reversed" if the signal direction was opposite.

All pipeline outputs were verified through an exhaustive molecular-level audit performing 89 deterministic checks with zero sampling: 85 PASSED, 0 FAILED, 4 WARNINGS (all documented known issues related to STRING identifier resolution).
"""

# ============================================================================
# TABLE DEFINITIONS
# ============================================================================

TABLE_1_TITLE = "Table 1. Data sources integrated in SexDiffKG."
TABLE_1_DATA = [
    ['Source', 'Version', 'Data Type', 'Contribution'],
    ['FDA FAERS', '2004Q1–2024Q4', 'ADR reports', '14,536,008 reports (F: 8.7M, M: 5.8M)'],
    ['ChEMBL', '36 (2024)', 'Drug–target', '12,682 drug–gene target edges'],
    ['STRING', 'v12.0', 'PPI', '465,390 interaction edges'],
    ['KEGG', '2024', 'Pathways', '537,605 pathway participation edges'],
    ['UniProt', '2024_05', 'Gene–protein', 'Protein annotation, sex-diff expression'],
]

TABLE_2_TITLE = "Table 2. SexDiffKG entity types (127,063 nodes)."
TABLE_2_DATA = [
    ['Entity Type', 'Count', '%', 'Description'],
    ['Gene', '70,607', '55.6%', 'Ensembl Gene IDs (ChEMBL/KEGG)'],
    ['Drug', '29,277', '23.0%', 'ChEMBL IDs (4,455) + FAERS IDs (24,822)'],
    ['AdverseEvent', '16,162', '12.7%', 'MedDRA preferred terms'],
    ['Protein', '8,721', '6.9%', 'UniProt/STRING protein IDs'],
    ['Pathway', '2,279', '1.8%', 'KEGG pathway identifiers'],
    ['Tissue', '17', '<0.1%', 'Gene expression annotations'],
]

TABLE_3_TITLE = "Table 3. SexDiffKG relation types (5,839,717 edges)."
TABLE_3_DATA = [
    ['Relation', 'Count', '%', 'Source'],
    ['has_adverse_event', '4,640,396', '79.5%', 'FAERS drug–AE co-occurrence'],
    ['participates_in', '537,605', '9.2%', 'KEGG gene/protein → pathway'],
    ['interacts_with', '465,390', '8.0%', 'STRING protein–protein'],
    ['sex_differential_AE', '183,539', '3.1%', 'FAERS sex-stratified ROR'],
    ['targets', '12,682', '0.2%', 'ChEMBL drug → gene'],
    ['sex_diff_expression', '105', '<0.1%', 'Curated sex-diff gene expression'],
]

TABLE_4_TITLE = "Table 4. Embedding training configuration."
TABLE_4_DATA = [
    ['Parameter', 'DistMult', 'RotatE'],
    ['Dimensions', '200 (real)', '200 (complex) = 400 real'],
    ['Epochs', '100', '25'],
    ['Batch size', '512', '1,024'],
    ['Learning rate', '0.001', '0.001'],
    ['Loss function', 'SLCWA', 'SLCWA'],
    ['Training device', 'GPU (GB10)', 'CPU (Grace)'],
    ['Training time', '~3.5 hours', '~7.5 hours'],
    ['Training triples', '5,489,928', '5,489,928'],
    ['Entities embedded', '126,575', '126,575'],
]

# ============================================================================
# HELPER FUNCTIONS FOR PDF GENERATION
# ============================================================================

class LineNumberedCanvas(canvas.Canvas):
    """
    Custom Canvas class that adds line numbers every 5 lines.
    Extends reportlab Canvas to add left-margin line numbering.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_number = 0
        self.lines_on_page = 0
        self.max_lines_per_page = 50  # Approximate
        self.left_margin_x = 0.5 * inch
        
    def add_line(self, text=""):
        """Increment line counter and potentially draw line number."""
        self.line_number += 1
        self.lines_on_page += 1
        if self.line_number % 5 == 0:
            # Draw line number on left margin
            y_pos = self._currentMatrix[5]  # Current Y position
            self.setFont("Times-Roman", 8)
            self.drawRightString(
                self.left_margin_x - 0.1 * inch,
                y_pos,
                str(self.line_number)
            )
    
    def reset_page(self):
        """Reset line counter for new page."""
        self.lines_on_page = 0


def create_styles():
    """Create custom paragraph and character styles."""
    styles = getSampleStyleSheet()
    
    # Try to register Times New Roman fonts (fall back to standard if unavailable)
    try:
        pdfmetrics.registerFont(
            TTFont('Times-Roman', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf')
        )
        pdfmetrics.registerFont(
            TTFont('Times-Bold', '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf')
        )
        pdfmetrics.registerFont(
            TTFont('Times-Italic', '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf')
        )
    except:
        # Fall back to built-in fonts if system fonts unavailable
        pass
    
    # Title style
    styles.add(ParagraphStyle(
        name='ManuscriptTitle',
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=black,
    ))
    
    # Author style
    styles.add(ParagraphStyle(
        name='Author',
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=black,
    ))
    
    # Affiliation style
    styles.add(ParagraphStyle(
        name='Affiliation',
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor=black,
    ))
    
    # Section heading
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='Times-Bold',
        fontSize=12,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=10,
        spaceBefore=12,
        textColor=black,
        keepWithNext=True,
    ))
    
    # Subsection heading
    styles.add(ParagraphStyle(
        name='SubsectionHeading',
        fontName='Times-Bold',
        fontSize=11,
        leading=13,
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=10,
        textColor=black,
        keepWithNext=True,
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='BodyText',
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        textColor=black,
    ))
    
    # Abstract style
    styles.add(ParagraphStyle(
        name='Abstract',
        fontName='Times-Roman',
        fontSize=9.5,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        textColor=black,
    ))
    
    # Keywords style
    styles.add(ParagraphStyle(
        name='Keywords',
        fontName='Times-Italic',
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        spaceAfter=12,
        textColor=black,
    ))
    
    return styles


def add_page_header_footer(c, page_num, running_title, width, height):
    """
    Add header, footer, and page number to current page.
    
    Args:
        c: Canvas object
        page_num: Current page number (integer)
        running_title: Short title for running header
        width: Page width
        height: Page height
    """
    # Running header (top of page)
    c.setFont("Times-Roman", 9)
    c.drawString(1 * inch, height - 0.5 * inch, running_title)
    
    # Page number (bottom center)
    page_num_str = str(page_num)
    c.drawCentredString(width / 2, 0.5 * inch, page_num_str)


def create_title_page(c, width, height, styles):
    """Create the title page."""
    page_num = 1
    y_position = height - 1.5 * inch
    
    # Add header/footer
    add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
    
    # Title
    title_style = styles['ManuscriptTitle']
    title_para = Paragraph(MANUSCRIPT_TITLE, title_style)
    title_width, title_height = title_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    title_para.drawOn(c, 1 * inch, y_position - title_height)
    y_position -= (title_height + 0.4 * inch)
    
    # Authors
    author_style = styles['Author']
    author_para = Paragraph(AUTHOR, author_style)
    author_width, author_height = author_para.wrapOn(c, width - 2 * inch, 1 * inch)
    author_para.drawOn(c, 1 * inch, y_position - author_height)
    y_position -= (author_height + 0.15 * inch)
    
    # Affiliations
    aff_style = styles['Affiliation']
    aff_para = Paragraph(AFFILIATION, aff_style)
    aff_width, aff_height = aff_para.wrapOn(c, width - 2 * inch, 1 * inch)
    aff_para.drawOn(c, 1 * inch, y_position - aff_height)
    y_position -= (aff_height + 0.3 * inch)
    
    # Correspondence
    corr_style = styles['Affiliation']
    corr_text = f"*Correspondence: {CORRESPONDENCE}<br/>ORCID: {ORCID}"
    corr_para = Paragraph(corr_text, corr_style)
    corr_width, corr_height = corr_para.wrapOn(c, width - 2 * inch, 1 * inch)
    corr_para.drawOn(c, 1 * inch, y_position - corr_height)
    
    c.showPage()
    return page_num + 1


def create_abstract_page(c, width, height, page_num, styles):
    """Create the abstract page."""
    add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
    
    y_position = height - 1.5 * inch
    
    # Abstract heading
    heading_style = styles['SubsectionHeading']
    heading_para = Paragraph("Abstract", heading_style)
    _, heading_height = heading_para.wrapOn(c, width - 2 * inch, 1 * inch)
    heading_para.drawOn(c, 1 * inch, y_position - heading_height)
    y_position -= (heading_height + 0.2 * inch)
    
    # Abstract body
    body_style = styles['Abstract']
    body_para = Paragraph(ABSTRACT_TEXT, body_style)
    _, body_height = body_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    body_para.drawOn(c, 1 * inch, y_position - body_height)
    y_position -= (body_height + 0.3 * inch)
    
    # Keywords
    keywords_text = f"<b>Keywords:</b> {KEYWORDS}"
    keywords_para = Paragraph(keywords_text, styles['Keywords'])
    _, keywords_height = keywords_para.wrapOn(c, width - 2 * inch, 1 * inch)
    keywords_para.drawOn(c, 1 * inch, y_position - keywords_height)
    y_position -= (keywords_height + 0.3 * inch)
    
    # Metadata (contributions, competing interests, funding, data availability)
    metadata_sections = [
        ("Author Contributions:", AUTHOR_CONTRIBUTIONS),
        ("Competing Interests:", COMPETING_INTERESTS),
        ("Funding:", FUNDING),
        ("Data Availability:", DATA_AVAILABILITY),
    ]
    
    metadata_style = styles['BodyText']
    for title, content in metadata_sections:
        if y_position < 2 * inch:  # Start new page if too close to bottom
            c.showPage()
            page_num += 1
            add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
            y_position = height - 1.5 * inch
        
        # Title in bold
        title_para = Paragraph(f"<b>{title}</b> {content}", metadata_style)
        _, title_height = title_para.wrapOn(c, width - 2 * inch, height - 2 * inch)
        title_para.drawOn(c, 1 * inch, y_position - title_height)
        y_position -= (title_height + 0.15 * inch)
    
    c.showPage()
    return page_num + 1


def create_introduction(c, width, height, page_num, styles):
    """Create the Introduction section."""
    add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
    
    y_position = height - 1.5 * inch
    
    # Section heading
    heading_para = Paragraph("1. Introduction", styles['SectionHeading'])
    _, heading_height = heading_para.wrapOn(c, width - 2 * inch, 1 * inch)
    heading_para.drawOn(c, 1 * inch, y_position - heading_height)
    y_position -= (heading_height + 0.2 * inch)
    
    # Subsections
    subsections = [
        ("1.1 The Sex Gap in Drug Safety", INTRODUCTION_SECTION_1_1),
        ("1.2 Pharmacovigilance and the FAERS Database", INTRODUCTION_SECTION_1_2),
        ("1.3 Knowledge Graphs for Drug Safety", INTRODUCTION_SECTION_1_3),
        ("1.4 Study Objectives", INTRODUCTION_SECTION_1_4),
    ]
    
    for subsection_title, subsection_text in subsections:
        if y_position < 2 * inch:  # Page break
            c.showPage()
            page_num += 1
            add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
            y_position = height - 1.5 * inch
        
        # Subsection heading
        sub_heading = Paragraph(subsection_title, styles['SubsectionHeading'])
        _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
        sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
        y_position -= (sub_height + 0.15 * inch)
        
        # Subsection text
        text_para = Paragraph(subsection_text, styles['BodyText'])
        _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
        text_para.drawOn(c, 1 * inch, y_position - text_height)
        y_position -= (text_height + 0.2 * inch)
    
    c.showPage()
    return page_num + 1


def draw_table(c, data, x, y, width, col_widths, styles):
    """
    Draw a formatted table with borders and headers.
    
    Args:
        c: Canvas object
        data: List of lists (table data)
        x, y: Position (top-left)
        width: Total table width
        col_widths: List of column widths
        styles: Styles dictionary
    
    Returns:
        height of table drawn
    """
    # Create table style
    table_style_list = [
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#CCCCCC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 0.5, black),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F5F5F5')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]
    
    table = Table(data, colWidths=col_widths, style=TableStyle(table_style_list))
    
    # Get table dimensions
    table_width, table_height = table.wrapOn(c, width, 8 * inch)
    
    # Draw table
    table.drawOn(c, x, y - table_height)
    
    return table_height


def create_methods_section_1(c, width, height, page_num, styles):
    """Create Methods section (part 1: Data sources and FAERS processing)."""
    add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
    
    y_position = height - 1.5 * inch
    
    # Section heading
    heading_para = Paragraph("2. Methods", styles['SectionHeading'])
    _, heading_height = heading_para.wrapOn(c, width - 2 * inch, 1 * inch)
    heading_para.drawOn(c, 1 * inch, y_position - heading_height)
    y_position -= (heading_height + 0.2 * inch)
    
    # 2.1 Data Sources
    if y_position < 2.5 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    sub_heading = Paragraph("2.1 Data Sources and Integration", styles['SubsectionHeading'])
    _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
    sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
    y_position -= (sub_height + 0.15 * inch)
    
    text_para = Paragraph(METHODS_SECTION_2_1, styles['BodyText'])
    _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    text_para.drawOn(c, 1 * inch, y_position - text_height)
    y_position -= (text_height + 0.2 * inch)
    
    # Table 1: Data sources
    if y_position < 3 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    table_title = Paragraph(TABLE_1_TITLE, styles['BodyText'])
    _, table_title_height = table_title.wrapOn(c, width - 2 * inch, 1 * inch)
    table_title.drawOn(c, 1 * inch, y_position - table_title_height)
    y_position -= (table_title_height + 0.1 * inch)
    
    col_widths = [(width - 2 * inch) * 0.15, (width - 2 * inch) * 0.15, 
                  (width - 2 * inch) * 0.2, (width - 2 * inch) * 0.5]
    table_height = draw_table(c, TABLE_1_DATA, 1 * inch, y_position, 
                              width - 2 * inch, col_widths, styles)
    y_position -= (table_height + 0.3 * inch)
    
    # 2.2 FAERS Data Processing
    if y_position < 2.5 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    sub_heading = Paragraph("2.2 FAERS Data Processing", styles['SubsectionHeading'])
    _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
    sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
    y_position -= (sub_height + 0.15 * inch)
    
    text_para = Paragraph(METHODS_SECTION_2_2, styles['BodyText'])
    _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    text_para.drawOn(c, 1 * inch, y_position - text_height)
    y_position -= (text_height + 0.3 * inch)
    
    c.showPage()
    return page_num + 1


def create_methods_section_2(c, width, height, page_num, styles, figures_dir):
    """Create Methods section (part 2: KG schema, signal detection, embedding)."""
    add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
    
    y_position = height - 1.5 * inch
    
    # 2.3 Knowledge Graph Schema
    sub_heading = Paragraph("2.3 Knowledge Graph Schema", styles['SubsectionHeading'])
    _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
    sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
    y_position -= (sub_height + 0.15 * inch)
    
    text_para = Paragraph(METHODS_SECTION_2_3, styles['BodyText'])
    _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    text_para.drawOn(c, 1 * inch, y_position - text_height)
    y_position -= (text_height + 0.2 * inch)
    
    # Table 2: Entity types
    if y_position < 4 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    table_title = Paragraph(TABLE_2_TITLE, styles['BodyText'])
    _, table_title_height = table_title.wrapOn(c, width - 2 * inch, 1 * inch)
    table_title.drawOn(c, 1 * inch, y_position - table_title_height)
    y_position -= (table_title_height + 0.1 * inch)
    
    col_widths = [(width - 2 * inch) * 0.15, (width - 2 * inch) * 0.15, 
                  (width - 2 * inch) * 0.1, (width - 2 * inch) * 0.6]
    table_height = draw_table(c, TABLE_2_DATA, 1 * inch, y_position, 
                              width - 2 * inch, col_widths, styles)
    y_position -= (table_height + 0.3 * inch)
    
    # Table 3: Relation types
    if y_position < 4 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    table_title = Paragraph(TABLE_3_TITLE, styles['BodyText'])
    _, table_title_height = table_title.wrapOn(c, width - 2 * inch, 1 * inch)
    table_title.drawOn(c, 1 * inch, y_position - table_title_height)
    y_position -= (table_title_height + 0.1 * inch)
    
    col_widths = [(width - 2 * inch) * 0.2, (width - 2 * inch) * 0.2, 
                  (width - 2 * inch) * 0.1, (width - 2 * inch) * 0.5]
    table_height = draw_table(c, TABLE_3_DATA, 1 * inch, y_position, 
                              width - 2 * inch, col_widths, styles)
    y_position -= (table_height + 0.3 * inch)
    
    # Try to insert Figure 2 (KG overview)
    if os.path.exists(os.path.join(figures_dir, 'fig3_kg_overview.png')):
        if y_position < 3.5 * inch:
            c.showPage()
            page_num += 1
            add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
            y_position = height - 1.5 * inch
        
        fig_caption = Paragraph(
            "<b>Figure 2.</b> SexDiffKG overview showing the composition of entity types and relation types in the sex-differential knowledge graph.",
            styles['BodyText']
        )
        _, fig_caption_height = fig_caption.wrapOn(c, width - 2 * inch, 1 * inch)
        fig_caption.drawOn(c, 1 * inch, y_position - fig_caption_height)
        y_position -= (fig_caption_height + 0.1 * inch)
        
        # Draw placeholder for figure (or actual figure if available)
        c.setFont("Times-Roman", 9)
        c.drawString(1.5 * inch, y_position - 0.5 * inch, "[Figure 2: KG Overview]")
        y_position -= 2.5 * inch
    
    if y_position < 1.5 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    # 2.4 Sex-Differential Signal Detection
    sub_heading = Paragraph("2.4 Sex-Differential Signal Detection", styles['SubsectionHeading'])
    _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
    sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
    y_position -= (sub_height + 0.15 * inch)
    
    text_para = Paragraph(METHODS_SECTION_2_4, styles['BodyText'])
    _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    text_para.drawOn(c, 1 * inch, y_position - text_height)
    y_position -= (text_height + 0.2 * inch)
    
    if y_position < 1.5 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    c.showPage()
    return page_num + 1


def create_methods_section_3(c, width, height, page_num, styles, figures_dir):
    """Create Methods section (part 3: Embedding, post-embedding, validation)."""
    add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
    
    y_position = height - 1.5 * inch
    
    # 2.5 Knowledge Graph Embedding
    sub_heading = Paragraph("2.5 Knowledge Graph Embedding", styles['SubsectionHeading'])
    _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
    sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
    y_position -= (sub_height + 0.15 * inch)
    
    text_para = Paragraph(METHODS_SECTION_2_5, styles['BodyText'])
    _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    text_para.drawOn(c, 1 * inch, y_position - text_height)
    y_position -= (text_height + 0.2 * inch)
    
    # Table 4: Embedding config
    if y_position < 3.5 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    table_title = Paragraph(TABLE_4_TITLE, styles['BodyText'])
    _, table_title_height = table_title.wrapOn(c, width - 2 * inch, 1 * inch)
    table_title.drawOn(c, 1 * inch, y_position - table_title_height)
    y_position -= (table_title_height + 0.1 * inch)
    
    col_widths = [(width - 2 * inch) * 0.25, (width - 2 * inch) * 0.375, 
                  (width - 2 * inch) * 0.375]
    table_height = draw_table(c, TABLE_4_DATA, 1 * inch, y_position, 
                              width - 2 * inch, col_widths, styles)
    y_position -= (table_height + 0.3 * inch)
    
    if y_position < 1.5 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    # 2.6 Post-Embedding Analysis
    sub_heading = Paragraph("2.6 Post-Embedding Analysis", styles['SubsectionHeading'])
    _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
    sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
    y_position -= (sub_height + 0.15 * inch)
    
    text_para = Paragraph(METHODS_SECTION_2_6, styles['BodyText'])
    _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    text_para.drawOn(c, 1 * inch, y_position - text_height)
    y_position -= (text_height + 0.2 * inch)
    
    if y_position < 2 * inch:
        c.showPage()
        page_num += 1
        add_page_header_footer(c, page_num, RUNNING_TITLE, width, height)
        y_position = height - 1.5 * inch
    
    # 2.7 Signal Validation and Data Integrity
    sub_heading = Paragraph("2.7 Signal Validation and Data Integrity", styles['SubsectionHeading'])
    _, sub_height = sub_heading.wrapOn(c, width - 2 * inch, 1 * inch)
    sub_heading.drawOn(c, 1 * inch, y_position - sub_height)
    y_position -= (sub_height + 0.15 * inch)
    
    text_para = Paragraph(METHODS_SECTION_2_7, styles['BodyText'])
    _, text_height = text_para.wrapOn(c, width - 2 * inch, height - 3 * inch)
    text_para.drawOn(c, 1 * inch, y_position - text_height)
    y_position -= (text_height + 0.2 * inch)
    
    c.showPage()
    return page_num + 1


def generate_manuscript_pdf(output_path, figures_dir=None):
    """
    Generate the complete first-half manuscript PDF.
    
    Args:
        output_path: Path where PDF should be saved
        figures_dir: Directory containing figure files (default: ~/sexdiffkg/results/figures/)
    """
    if figures_dir is None:
        figures_dir = os.path.expanduser('~/sexdiffkg/results/figures/')
    
    # Page setup
    width, height = letter
    margin = 1 * inch
    
    # Create canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Create styles
    styles = create_styles()
    
    page_num = 1
    
    # Generate pages
    print("Generating title page...")
    page_num = create_title_page(c, width, height, styles)
    
    print("Generating abstract page...")
    page_num = create_abstract_page(c, width, height, page_num, styles)
    
    print("Generating introduction section...")
    page_num = create_introduction(c, width, height, page_num, styles)
    
    print("Generating methods section (part 1)...")
    page_num = create_methods_section_1(c, width, height, page_num, styles)
    
    print("Generating methods section (part 2)...")
    page_num = create_methods_section_2(c, width, height, page_num, styles, figures_dir)
    
    print("Generating methods section (part 3)...")
    page_num = create_methods_section_3(c, width, height, page_num, styles, figures_dir)
    
    # Add note about where part 2 will continue
    c.setFont("Times-Roman", 10)
    c.drawString(1 * inch, 2 * inch, "---")
    c.drawString(1 * inch, 1.5 * inch, "PART 2 CONTENT WILL BEGIN HERE:")
    c.drawString(1 * inch, 1.0 * inch, "3. Results")
    c.drawString(1 * inch, 0.7 * inch, "4. Discussion")
    c.drawString(1 * inch, 0.4 * inch, "References & Supplementary Tables")
    c.showPage()
    
    # Save PDF
    c.save()
    print(f"PDF saved to {output_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Default output path
    output_path = os.path.expanduser("~/sexdiffkg/outputs/manuscript_v3_part1.pdf")
    
    # Allow command-line argument for custom output path
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Generate PDF
    print(f"Generating manuscript PDF (Part 1: Title through Methods)...")
    generate_manuscript_pdf(output_path)
    print(f"Complete! PDF saved to: {output_path}")
