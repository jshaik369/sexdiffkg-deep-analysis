# The Seriousness-Sex Gradient: Serious Adverse Events Show Attenuated Female Bias in Pharmacovigilance

Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
CoEvolve Network, Independent Researcher, Barcelona, Spain
jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

## Abstract

Pharmacovigilance databases consistently show female preponderance in adverse event reporting.
However, whether this bias extends uniformly to serious versus non-serious events remains
unexplored. Analyzing 96,281 sex-differential signals from the FDA Adverse Event Reporting
System (FAERS; 14.5M reports, 2004–2025), we demonstrate a significant seriousness-sex gradient:
serious adverse events (life-threatening, fatal, disabling) average 51.2% female compared to
58.3% for non-serious events (Mann-Whitney p = 8.2 × 10⁻⁸³). Organ system analysis reveals
cardiac (53.1%F) and renal (52.9%F) events as the least female-biased, while dermatologic
(63.9%F) and musculoskeletal (62.7%F) show the strongest female preponderance. Anti-regression
analysis demonstrates that the sex-bias intensification with report volume operates
independently within all 16 organ systems (ρ > 0.6 in 14/16). The finding that serious
events approach parity while non-serious events skew female has direct implications for
signal detection thresholds and sex-stratified safety monitoring.

## Introduction

The FDA Adverse Event Reporting System (FAERS) contains a structural asymmetry:
approximately 60% of reports come from female patients. This baseline reporting
imbalance has been attributed to multiple factors including sex differences in
healthcare utilization, prescription patterns, and biological susceptibility.

A critical open question is whether this female preponderance is uniform across
the severity spectrum. If serious adverse events—those that are life-threatening,
result in death, or cause permanent disability—show a different sex distribution
than non-serious events, it would fundamentally alter the interpretation of
pharmacovigilance signals and the design of sex-stratified safety monitoring.

Using the SexDiffKG knowledge graph framework, we analyzed 96,281 sex-differential
adverse event signals across 2,178 drugs to quantify the seriousness-sex gradient.

## Methods

### Data Source
FAERS data spanning 2004Q1-2025Q3 (87 quarters, 14,536,008 deduplicated reports;
8,744,397 female, 5,791,611 male) were processed through the SexDiffKG pipeline.
Sex-differential signals were identified using Reporting Odds Ratios with a minimum
of 5 reports per sex-drug-AE combination.

### Seriousness Classification
Adverse events were classified as "serious" based on MedDRA preferred term keywords
associated with FDA serious outcome categories: fatal events (death, sudden death),
life-threatening events (cardiac arrest, anaphylaxis, sepsis), hospitalization
(stroke, myocardial infarction, pulmonary embolism), and disability (Stevens-Johnson
syndrome, agranulocytosis, organ failure). A total of 3,579 signals mapped to
serious AEs and 92,702 to non-serious AEs.

### Organ System Mapping
Signals were classified into 16 System Organ Classes using keyword-based mapping
from MedDRA preferred terms. Coverage reached 38.4% of all signals (36,951/96,281),
with the remainder being generic terms not classifiable to a single organ system.

### Anti-Regression Analysis
Within each SOC, drugs were ranked by total report volume and divided into quintiles.
The Spearman correlation between volume quintile and mean female fraction quantified
the anti-regression effect per organ system.

## Results

### The Seriousness-Sex Gradient
Serious adverse events showed significantly attenuated female bias compared to non-serious
events (51.2%F vs 58.3%F; Mann-Whitney U p = 8.2 × 10⁻⁸³). The difference of 7.1
percentage points represents a substantial attenuation—serious events approach demographic
parity while non-serious events maintain the expected female predominance.

Signal strength was comparable between categories (mean |log-ratio| 0.927 serious
vs 0.989 non-serious), indicating that the attenuated female bias in serious events
is not simply an artifact of weaker signals.

### Organ System Sex Spectrum
The 16 organ systems span a range from 53.1%F (cardiac) to 63.9%F (dermatologic):

**Most female-biased (>60%F):**
- Dermatologic: 63.9%F (2,684 signals)
- Musculoskeletal: 62.7%F (2,915 signals)
- Immune: 62.0%F (1,137 signals)
- Gastrointestinal: 61.9%F (3,496 signals)
- Metabolic: 60.0%F (1,751 signals)

**Near-parity (<55%F):**
- Cardiac: 53.1%F (3,186 signals)
- Renal: 52.9%F (2,045 signals)
- Infectious: 54.5%F (2,979 signals)
- Hematologic: 54.8%F (2,256 signals)

### Universal Anti-Regression Across Organ Systems
The anti-regression phenomenon—whereby female bias intensifies with increasing report
volume—was present in all 16 organ systems, with Spearman ρ > 0.6 in 14 out of 16
systems. The strongest anti-regression was observed in dermatologic, musculoskeletal,
immune, and gastrointestinal SOCs (ρ = 1.000 each), while cardiac showed the weakest
(ρ = 0.200), consistent with its overall near-parity profile.

### Cross-SOC Correlation Structure
Drug-level sex profiles showed moderate positive correlations across SOCs, suggesting
that drugs biased female in one organ system tend to be biased female in others.
However, cardiac and hematologic SOCs showed the weakest correlations with other
systems, indicating partially independent sex-differential mechanisms.

## Discussion

The seriousness-sex gradient we describe has several important implications:

1. **Signal detection**: Current disproportionality analyses do not routinely adjust
for the differential sex distribution between serious and non-serious events. Our
findings suggest that a signal at 55%F for a serious cardiac event may represent a
stronger female-specific risk than the same proportion for a non-serious dermatologic
event.

2. **Reporting bias decomposition**: The near-parity of serious events supports
the hypothesis that a substantial portion of the female reporting excess in FAERS
reflects differential healthcare utilization rather than true biological susceptibility.
Serious events—which are less discretionary to report—show less sex asymmetry.

3. **Organ-specific monitoring**: The 10.8pp spread from cardiac (53.1%F) to
dermatologic (63.9%F) indicates that sex-stratified safety monitoring should
use organ-specific rather than global baseline correction.

4. **Anti-regression universality**: The persistence of anti-regression within
all 16 organ systems, including those near parity (cardiac ρ = 0.200 but positive),
suggests this is a fundamental property of pharmacovigilance data, not an artifact
of specific drug classes or organ systems.

## Limitations
- Seriousness classification used keyword proxies rather than explicit FAERS
  outcome fields
- SOC mapping covered 38.4% of signals
- Reporter-level confounders (healthcare professional vs consumer reports) not assessed

## Conclusion
We identify a seriousness-sex gradient in pharmacovigilance: serious adverse events
approach sex parity (51.2%F) while non-serious events maintain the expected female
predominance (58.3%F). This 7.1pp difference, combined with organ-specific sex
profiles spanning from 53.1%F (cardiac) to 63.9%F (dermatologic), demonstrates
that the interpretation of sex-differential safety signals requires context-dependent
baseline correction. The universal anti-regression across all organ systems confirms
that sex bias intensification with report volume is a structural property of
pharmacovigilance databases requiring systematic consideration in safety signal
evaluation.

## Data Availability
SexDiffKG v4, all analysis outputs, and code available at:
https://github.com/jshaik369/sexdiffkg-deep-analysis

## Keywords
pharmacovigilance, sex differences, FAERS, adverse events, seriousness, organ systems
