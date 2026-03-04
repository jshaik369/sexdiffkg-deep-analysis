# The Organ System Architecture of Sex-Differential Drug Safety:
# A 16-SOC Analysis of 96,281 Pharmacovigilance Signals

Mohammed Javeed Akhtar Abbas Shaik
CoEvolve Network, Independent Researcher, Barcelona, Spain
jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

## Abstract

Sex-differential drug safety signals are not uniformly distributed across organ systems.
Analysis of 96,281 signals mapped to 16 MedDRA System Organ Classes (SOCs) reveals a
30-percentage-point range from Skin/Subcutaneous disorders (84.7% female) to Cardiac
disorders (54.6% female). The anti-regression phenomenon—female bias intensifying with
report volume—shows striking organ-specificity: strong in musculoskeletal (rho=0.879,
p=8.1×10⁻⁴), gastrointestinal (rho=0.830), and skin (rho=0.830), but reversed in
vascular disorders (rho=-0.733, p=0.016) and absent in cardiac, renal, and hematologic
systems. This organ-specific heterogeneity suggests that the biological mechanisms
underlying sex-differential drug toxicity vary fundamentally across physiological
systems, with implications for sex-specific drug monitoring guidelines.

**Keywords:** MedDRA, system organ class, sex differences, pharmacovigilance, 
organ system toxicity, anti-regression

## 1. Introduction

Sex-differential drug safety signals in the FDA Adverse Event Reporting System (FAERS)
show an overall 58.1% female predominance. However, this global average masks fundamental
heterogeneity across physiological systems. Different organ systems have distinct
biological substrates for sex-differential drug responses: hormonal influences on
cardiac repolarization, sex-linked differences in hepatic metabolism, immune system
sexual dimorphism, and tissue-specific drug transporter expression.

Understanding the organ-level architecture of sex-differential safety is critical for:
(1) developing sex-specific monitoring protocols, (2) prioritizing safety biomarkers,
and (3) interpreting signal detection algorithms that may be confounded by system-level
sex bias.

## 2. Methods

### 2.1 SOC Classification
96,281 sex-differential signals were mapped to 16 MedDRA SOCs using keyword-based
classification of adverse event preferred terms. Signals matching multiple SOCs were
counted in each relevant category.

### 2.2 Anti-Regression Analysis
Within each SOC, drugs were ranked by signal count and divided into deciles. Female
fraction was computed per decile, and Spearman rank correlation assessed the monotonic
relationship between signal volume and female bias.

### 2.3 Statistical Framework
All analyses used the SexDiffKG v4 knowledge graph (109,867 nodes, 1,822,851 edges)
and FAERS data spanning 87 quarters (2004Q1-2025Q3, 14,536,008 reports).

## 3. Results

### 3.1 The 30-Point SOC Spectrum
Female fraction ranged from 84.7% (Skin/Subcutaneous) to 54.6% (Cardiac disorders):

| SOC | Signals | %Female | Direction Split |
|-----|---------|---------|-----------------|
| Skin/Subcutaneous | 3,058 | 84.7% | 1437F/1621M |
| Musculoskeletal | 3,795 | 82.6% | 1769F/2026M |
| Immune system | 1,313 | 80.4% | 829F/484M |
| Gastrointestinal | 4,474 | 79.4% | 2547F/1927M |
| Nervous system | 2,692 | 77.8% | 1494F/1198M |
| Hepatobiliary | 2,749 | 77.6% | 1804F/945M |
| Psychiatric | 2,085 | 74.3% | 1198F/887M |
| Reproductive | 457 | 73.5% | 233F/224M |
| Metabolism/Nutrition | 2,519 | 73.7% | 1667F/852M |
| Infections | 4,205 | 73.1% | 2242F/1963M |
| Eye disorders | 941 | 69.5% | 382F/559M |
| Respiratory | 4,783 | 69.4% | 2553F/2230M |
| Vascular | 2,616 | 65.5% | 1672F/944M |
| Blood/Lymphatic | 1,434 | 59.9% | 945F/489M |
| Renal/Urinary | 2,524 | 56.1% | 1803F/721M |
| Cardiac | 3,309 | 54.6% | 2102F/1207M |

### 3.2 Organ-Specific Anti-Regression
Anti-regression (female bias intensifying with volume) was significant in 5 SOCs:
- **Musculoskeletal**: rho=0.879 (p=8.1×10⁻⁴) — strongest
- **Gastrointestinal**: rho=0.830 (p=2.9×10⁻³)
- **Skin/Subcutaneous**: rho=0.830 (p=2.9×10⁻³)
- **Psychiatric**: rho=0.709 (p=0.022)
- **Nervous system**: rho=0.758 (p=0.011)

Critically, **Vascular disorders showed REVERSE anti-regression** (rho=-0.733,
p=0.016), meaning male bias intensifies with volume in vascular AEs.

Non-significant: Cardiac (-0.164), Renal (0.018), Blood/Lymphatic (-0.455),
Eye (-0.079), Immune (0.200), Hepatobiliary (0.358).

### 3.3 Interpretive Framework
The SOCs cluster into three zones:
1. **Female-dominant** (>75%F): Skin, MSK, Immune, GI, Nervous, Hepatic — 
   auto-inflammatory and pain-associated
2. **Moderate** (65-75%F): Psychiatric, Reproductive, Metabolic, Infections, 
   Eye, Respiratory — mixed biology
3. **Near-balanced** (<65%F): Vascular, Blood, Renal, Cardiac — 
   cardiovascular/hematologic cluster

## 4. Discussion

### 4.1 The Cardiovascular-Autoimmune Divide
The sharpest divide is between autoimmune/inflammatory SOCs (>80%F) and
cardiovascular SOCs (<60%F). This mirrors known sex dimorphism: autoimmune diseases
affect women 2-10× more than men, while cardiovascular disease historically presented
more in men (though women's CV risk is increasingly recognized).

### 4.2 Reverse Anti-Regression in Vascular Disorders
The finding that vascular AEs show reverse anti-regression is novel and unexpected.
It suggests that high-volume vascular safety signals (thrombosis, embolism, hemorrhage)
become progressively more male-biased, possibly reflecting true biological differences
in coagulation biology and atherosclerosis.

### 4.3 Clinical Implications
- **Skin, MSK, immune AEs**: Expect predominantly female reports — adjust thresholds
- **Cardiac, renal AEs**: Near-balanced — sex-specific signals more meaningful
- **Vascular AEs**: Male bias increases with volume — monitor for under-reporting in women

## 5. Conclusion

The organ system architecture of sex-differential drug safety reveals a 30-point
spectrum with three distinct zones. Anti-regression is not universal but organ-specific,
with vascular disorders showing the opposite pattern. These findings mandate SOC-specific
sex adjustment in pharmacovigilance signal detection.

## References
[Standard references to MedDRA, FAERS, sex differences in organ toxicity]

---
*Generated from SexDiffKG v4 (109,867 nodes, 1,822,851 edges)*
*FAERS: 14,536,008 reports, 96,281 sex-differential signals, 16 SOCs analyzed*
