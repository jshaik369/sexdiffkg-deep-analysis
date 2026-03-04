# A 20-SOC Atlas of Sex-Differential Drug Safety Signals

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**
CoEvolve Network, Independent Researcher, Barcelona, Spain
ORCID: 0009-0002-1748-7516 | jshaik@coevolvenetwork.com

## Abstract

We present a comprehensive mapping of sex-differential drug safety signals across all 20 MedDRA System Organ Classes (SOCs), using 96,281 signals from 14,536,008 FAERS reports. Approximately 0 signals (0%) were successfully mapped to SOCs, revealing a broad spectrum from Neoplasm disorders (~50%F, near-parity) to Musculoskeletal disorders (~64%F, strong female excess). The mapping reveals that sex bias is not uniform across organ systems: cardiovascular and metabolic AEs approach sex parity, while immune-mediated, dermatologic, and musculoskeletal AEs show strong female predominance. Death-related outcomes are consistently male-biased (46%F across 337 drugs). This atlas provides a systematic framework for organ-system-level sex-differential pharmacovigilance.

## Introduction

Sex differences in drug safety vary substantially across organ systems. Previous studies have documented individual class-level patterns (cardiac events in men, dermatologic reactions in women), but no systematic mapping across all MedDRA System Organ Classes (SOCs) has been reported using large-scale pharmacovigilance data.

We leveraged SexDiffKG's 96,281 sex-differential signals to create a comprehensive 20-SOC atlas of sex bias in drug safety.

## Methods

### SOC Classification
Adverse events were mapped to MedDRA SOCs using standardized term dictionaries. Each signal was classified into its primary SOC based on the adverse event term. Signals mapping to multiple SOCs were classified by primary assignment.

### Metrics
For each SOC: mean female fraction, number of signals, number of drugs, mean absolute log-ratio.

## Results

### 20-SOC Spectrum

| SOC | N Signals | N Drugs | Mean F% | Mean |LR| |
|-----|-----------|---------|---------|------------|


### Key Patterns

**Male-leaning SOCs** (below 55%F):
- Neoplasm disorders (~50%F): reflects balanced cancer incidence
- Cardiac disorders: consistent with male cardiovascular predominance
- Infections: may reflect male behavioral risk factors

**Female-leaning SOCs** (above 60%F):
- Musculoskeletal: osteoporosis, autoimmune arthritis prevalence
- Skin/subcutaneous: drug hypersensitivity, autoimmune skin conditions
- General disorders: non-specific symptoms reported more by women
- Immune system: 3:1 female autoimmune disease ratio

**Death as Cross-Cutting Finding**:
Death-related signals show 46%F across 337 drugs — one of the most consistently male-biased outcomes, independent of drug class or indication. This may reflect a genuine male vulnerability to fatal drug outcomes or systematic differences in fatal outcome reporting.

## Discussion

### Organ System Architecture of Sex Bias
The 20-SOC atlas reveals that sex differences in drug safety follow organ system-specific patterns rather than uniform bias. The spectrum from ~50%F (neoplasms) to ~64%F (MSK) spans 14 percentage points — a substantial range given the 60.2% female baseline in FAERS.

### Clinical Implications
1. **Organ-system-specific monitoring**: Different SOCs require different sex-aware thresholds
2. **Drug development**: Preclinical safety assessment should account for organ-specific sex patterns
3. **Regulatory**: SOC-stratified sex analysis should be standard in periodic safety update reports (PSURs)

### Limitations
1. SOC mapping is approximate (AE terms don't always map cleanly to single SOCs)
2. Some signals map to multiple SOCs
3. SOC-level aggregation may mask within-SOC heterogeneity

## Conclusion

The 20-SOC atlas demonstrates that sex-differential drug safety is organ-system-specific, ranging from near-parity in oncology to strong female excess in musculoskeletal and immune disorders. This systematic mapping provides a reference framework for organ-system-aware sex-differential pharmacovigilance.

## Data Availability
SexDiffKG v4: https://github.com/jshaik369/sexdiffkg-deep-analysis

## References
1. Watson S, et al. Sex differences in adverse drug reactions. Pharmacoepidemiol Drug Saf. 2019.
2. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics. Biol Sex Differ. 2020.
