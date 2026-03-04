# Extreme Sex-Differential Drug Safety Signals: A Systematic Analysis of 14.5 Million FAERS Reports

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**
CoEvolve Network, Independent Researcher, Barcelona, Spain
ORCID: 0009-0002-1748-7516 | jshaik@coevolvenetwork.com

## Abstract

We systematically identify and characterize extreme sex-differential drug safety signals from 14,536,008 FAERS reports. Using thresholds of >90% female or <10% female with >= 100 total reports, we find 7,457 extreme female-biased signals versus only 519 extreme male-biased signals — a 14.4-fold asymmetry. The most extreme signals combine large effect sizes with high report volumes: Minoxidil/Adverse drug reaction (combined score 58.3, 0.2%F, 8,480 reports) and Docetaxel/Alopecia (98.7%F, 20,319 reports). We identify paradoxical signals where sex-typical drugs produce opposite-sex-biased AEs (e.g., Risperidone/Galactorrhoea at 11%F). The 14.4-fold female excess in extreme signals substantially exceeds the baseline 60.2% female reporting rate, suggesting biological and pharmacological mechanisms beyond reporting bias.

## Introduction

While the overall FAERS database shows a 60.2% female reporting rate, the distribution of sex ratios across drug-AE pairs is highly heterogeneous. Some signals show near-complete sex dominance (>90% or <10% female), representing extreme sex-differential pharmacovigilance signals that may reflect fundamental biological differences in drug response, disease prevalence, or prescribing patterns.

Previous work has documented individual sex-differential signals, but no systematic analysis has characterized the full landscape of extreme signals. Using SexDiffKG (109,867 nodes, 1,822,851 edges) and 96,281 sex-differential signals, we identify and classify the most extreme sex-differential drug safety signals.

## Methods

### Signal Identification
From 96,281 sex-differential signals (2,178 drugs x 5,069 AEs), we defined extreme signals as:
- **Extreme female**: >90% female AND >= 100 total reports
- **Extreme male**: <10% female AND >= 100 total reports

### Scoring
Combined score = |log_ratio| x log10(total_reports), balancing effect size with evidence volume.

### Paradoxical Signal Detection
Signals where sex-typical drugs (e.g., testosterone, oral contraceptives) produce unexpected opposite-sex-biased AEs.

## Results

### Extreme Signal Counts
- Extreme female (>90%F, >= 100 reports): **7,457 signals**
- Extreme male (<10%F, >= 100 reports): **519 signals**
- Ratio: **14.4:1** female:male

This asymmetry far exceeds the baseline 60.2% female rate, indicating that the right tail of the sex-ratio distribution is dramatically more populated by female-biased signals.

### Top Signals by Effect Size (|log_ratio|)

| Drug | Adverse Event | |LR| | F% | Reports | Bias |
|------|---------------|------|-----|---------|------|
| TESTOSTERONE | Prostatic disorder | 8.869 | 54.3% | 46 | ~ |
| PERTUZUMAB | Carbohydrate antigen 15-3 increased | 7.391 | 52.4% | 21 | ~ |
| ETONOGESTREL | Foetal exposure during pregnancy | 6.568 | 42.9% | 70 | ~ |
| HYDROXYPROGESTERONE | Abortion spontaneous | 6.456 | 89.7% | 117 | F |
| MINOXIDIL | Adverse drug reaction | 6.448 | 0.2% | 8,480 | M |
| CARBIDOPA;LEVODOPA | Embedded device | 6.447 | 23.6% | 717 | M |
| ETONOGESTREL | Premature baby | 6.421 | 43.9% | 41 | ~ |
| CARBIDOPA;LEVODOPA | Device expulsion | 6.412 | 37.8% | 127 | M |
| ETONOGESTREL | Injury associated with device | 6.327 | 72.7% | 55 | F |
| ETHINYLESTRADIOL;ETONOGESTREL | Medical device discomfort | 6.030 | 84.0% | 119 | F |

Testosterone/Prostatic disorder leads with |LR| = 8.869, though at 54.3%F this reflects the complex interaction of sex-hormone-related prescribing.

### Top Signals by Combined Score

| Drug | Adverse Event | Score | |LR| | F% | Reports | Bias |
|------|---------------|-------|------|-----|---------|------|
| MINOXIDIL | Adverse drug reaction | 58.3 | 6.448 | 0.2% | 8,480 | M |
| OXYCODONE | Infusion related reaction | 43.1 | 5.496 | 99.6% | 2,533 | F |
| CARBIDOPA;LEVODOPA | Embedded device | 42.4 | 6.447 | 23.6% | 717 | M |
| OXYCODONE | Pericarditis | 42.3 | 5.396 | 99.6% | 2,519 | F |
| ADALIMUMAB | Pemphigus | 41.8 | 4.743 | 99.8% | 6,782 | F |
| RISPERIDONE | Abnormal weight gain | 41.8 | 4.564 | 0.7% | 9,412 | M |
| METHOTREXATE | Glossodynia | 41.4 | 4.745 | 99.8% | 6,118 | F |
| OXYCODONE | Blister | 40.4 | 5.056 | 99.4% | 2,936 | F |
| GOLIMUMAB | Pericarditis | 40.0 | 4.810 | 99.7% | 4,072 | F |
| HYDROXYCHLOROQUINE | Pericarditis | 39.7 | 4.770 | 99.8% | 4,079 | F |

The combined score prioritizes signals with both large effect sizes AND substantial evidence bases, identifying the most clinically actionable extreme signals.

### Extreme Female Signals (>90%F)

| Drug | Adverse Event | F% | Reports |
|------|---------------|-----|---------|
| DOCETAXEL | Alopecia | 98.7% | 20,319 |
| RITUXIMAB | Rheumatoid arthritis | 92.9% | 16,146 |
| TOCILIZUMAB | Pain | 91.2% | 16,089 |
| INFLIXIMAB | Rheumatoid arthritis | 92.0% | 13,859 |
| TOCILIZUMAB | Arthralgia | 90.1% | 13,829 |
| ADALIMUMAB | Alopecia | 94.8% | 12,867 |
| METHOTREXATE | Rash | 90.0% | 12,557 |
| PREDNISONE | Pain | 90.1% | 12,359 |

Extreme female signals are dominated by:
1. **Autoimmune-disease drugs** (Rituximab, Tocilizumab) — reflecting 3:1 female autoimmune prevalence
2. **Chemotherapy AEs** (Docetaxel/Alopecia) — potential pharmacokinetic sex differences
3. **Pain/musculoskeletal** — consistent with higher female pain reporting

### Extreme Male Signals (<10%F)

| Drug | Adverse Event | F% | Reports |
|------|---------------|-----|---------|
| RANITIDINE | Prostate cancer | 0.6% | 54,130 |
| RISPERIDONE | Gynaecomastia | 0.1% | 24,407 |
| RISPERIDONE | Abnormal weight gain | 0.7% | 9,412 |
| ENZALUTAMIDE | Fatigue | 0.3% | 9,182 |
| MINOXIDIL | Adverse drug reaction | 0.2% | 8,480 |
| LEUPRORELIN | Death | 1.0% | 8,397 |
| LEUPRORELIN | Intercepted product preparation error | 5.5% | 7,136 |
| SILDENAFIL | Drug ineffective | 7.5% | 6,533 |

Extreme male signals cluster around:
1. **Prostate-related** (Ranitidine/Prostate cancer) — anatomical exclusivity
2. **Drug-induced hormonal effects** (Risperidone/Gynaecomastia) — pharmacological sex specificity
3. **Cardiovascular** — consistent with male cardiovascular disease predominance

### Paradoxical Signals
We identified 7 cases where typically-female AEs showed male predominance, and 1 cases of the reverse. These paradoxical signals are of particular pharmacological interest as they suggest drug-specific mechanisms that override expected sex patterns.

## Discussion

### The 14.4-Fold Asymmetry
The dramatic excess of extreme female signals (7,457 vs 519) cannot be explained by the baseline 60.2% female reporting rate alone. Under a simple proportional model, we would expect approximately 2-3x female excess; the observed 14.4x suggests:

1. **Biological amplification**: Sex-specific pharmacokinetic/pharmacodynamic pathways
2. **Disease landscape**: Female-predominant diseases (autoimmune, osteoporosis) require more drugs with broad AE profiles
3. **Reporting dynamics**: Healthcare utilization differences may concentrate extreme ratios in the female direction

### Clinical Implications
1. **Drug development**: Extreme signals should trigger mandatory sex-stratified safety analyses
2. **Prescribing guidance**: Drugs with extreme sex-differential signals warrant sex-specific monitoring protocols
3. **Regulatory policy**: The 14.4x asymmetry suggests systematic under-investigation of sex differences in drug safety

### Paradoxical Signals as Pharmacological Windows
Paradoxical signals — where drug effects override expected sex patterns — provide unique insight into drug-specific mechanisms. These signals may reveal novel off-target effects or sex-specific metabolic pathways.

## Conclusion

Extreme sex-differential drug safety signals show a striking 14.4-fold female excess that far exceeds baseline reporting asymmetry. The most extreme signals combine biological plausibility with substantial evidence, and paradoxical signals offer windows into drug-specific sex-differential mechanisms. Systematic characterization of extreme signals should become a standard component of pharmacovigilance practice.

## Data Availability
SexDiffKG v4: https://github.com/jshaik369/sexdiffkg-deep-analysis
FAERS source: 14,536,008 reports, 87 quarters (2004Q1-2025Q3)

## References
1. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. Biol Sex Differ. 2020.
2. Soldin OP, Mattison DR. Sex differences in pharmacokinetics and pharmacodynamics. Clin Pharmacokinet. 2009.
3. Anderson GD. Sex and racial differences in pharmacological response: where is the evidence? J Womens Health. 2005.
