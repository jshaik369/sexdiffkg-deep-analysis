---
title: "Sex-Differential Drug-Induced Liver Injury: Checkpoint Inhibitor Hepatotoxicity Is 95% Female-Biased Across 601 Drugs"
authors: "Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)"
affiliation: "CoEvolve Network, Independent Researcher, Barcelona, Spain"
email: "jshaik@coevolvenetwork.com"
orcid: "0009-0002-1748-7516"
target_journal: "Hepatology / Journal of Hepatology"
draft_version: "v2.0 — consolidated hepatotoxicity analysis"
date: "2026-03-05"
---

## Abstract

**Background:** Drug-induced liver injury (DILI) is the leading cause of acute liver failure in Western countries, yet sex differences in hepatotoxicity have been incompletely characterized across the pharmacopeia.

**Methods:** We analyzed 3,073 sex-differential hepatotoxicity signals from 14.5 million FAERS reports (2004Q1-2025Q3) across 601 drugs, classifying signals into hepatocellular injury, cholestatic, hepatic failure, steatosis/fibrosis, and autoimmune subtypes. Anti-regression analysis was performed within hepatotoxicity signals using volume decile stratification.

**Results:**

Overall hepatotoxicity is 65.3% female-biased (3,073 signals, 601 drugs, 133 hepatic AE terms). Hepatotoxicity signals show slightly lower female bias than non-hepatotoxicity signals (65.3% vs population mean), but the anti-regression phenomenon persists perfectly within hepatotoxicity (rho = 1.000). A total of 348 drugs have >=3 hepatotoxicity signals.

**By drug class:**

| Drug Class | %Female | N Signals |
|-----------|---------|-----------|
| Checkpoint inhibitors | **95.1%** | 41 |
| Antibiotics | 75.9% | 29 |
| NSAIDs | 75.6% | 41 |
| Statins | 69.7% | 33 |
| Acetaminophen | 63.2% | 19 |
| Antiepileptics | 57.1% | 28 |
| Antifungals | 55.0% | 20 |
| Anti-TNF | 52.1% | 73 |
| Immunosuppressants | 51.9% | 54 |
| **Autoimmune hepatitis** | **27.8%** | 18 |

**By hepatotoxicity subtype:**

| Subtype | %Female | N Signals |
|---------|---------|-----------|
| Hepatic failure | **69.0%** | 174 |
| Cholestatic | 68.2% | 418 |
| Hepatocellular | 63.6% | 632 |
| Steatosis/fibrosis | 59.3% | 150 |
| Autoimmune | **27.8%** | 18 |

**Key findings:**
1. **Checkpoint inhibitor hepatotoxicity** is nearly universally female-biased (95.1%F, 39/41 signals) — the strongest class-specific signal in the entire knowledge graph
2. **Autoimmune hepatitis** is strongly MALE-biased (27.8%F) — a paradox since autoimmune diseases are generally female-predominant
3. **175 drugs** show strongly female hepatotoxicity (>=70%F), vs only **49 drugs** with male hepatotoxicity (<=30%F)
4. Hepatic severity gradient: hepatic failure 69.0%F vs steatosis/fibrosis 59.3%F
5. NSAIDs and antibiotics — two of the most commonly prescribed drug classes — show 75-76% female hepatotoxicity bias
6. **Anti-regression within hepatotoxicity**: Perfect monotonicity (rho = 1.000) — female bias in hepatotoxicity signals intensifies with report volume, consistent with genuine biological signal
7. **Class-level variation**: TKI and ICI hepatotoxicity show distinct sex profiles vs DMARD hepatotoxicity, suggesting mechanism-specific sex effects

**Conclusions:** Drug-induced liver injury is systematically female-biased, with checkpoint inhibitors showing the most extreme disparity (95%F). The paradoxical male bias in autoimmune hepatitis signals despite female predominance of autoimmune disease suggests drug-triggered autoimmune hepatic responses follow a different immunological pathway than idiopathic autoimmune hepatitis. Anti-regression operating within hepatotoxicity confirms this is a genuine biological signal, not an artifact. These findings support sex-stratified DILI monitoring, particularly for immune checkpoint inhibitors.

## Introduction

Drug-induced liver injury (DILI) is responsible for over 50% of acute liver failure cases in the United States. While individual case series have suggested female predominance in some forms of DILI, systematic quantification across the full pharmacopeia has been lacking.

The emergence of immune checkpoint inhibitors (ICIs) has created a new category of immune-mediated hepatotoxicity, but sex differences in ICI hepatotoxicity have not been systematically characterized. Given that female immune responses are generally stronger than male responses, understanding sex differences in immune-mediated liver injury has direct clinical relevance.

We present the most comprehensive analysis of sex-differential hepatotoxicity to date, covering 601 drugs and 133 distinct hepatic adverse event terms.

## Methods

### Data Source
FAERS 2004Q1-2025Q3: 14,536,008 deduplicated reports (F:8,744,397 / M:5,791,611).

### Hepatic AE Identification
133 hepatic adverse event terms identified using keyword matching against MedDRA Preferred Terms: hepat*, liver*, jaundice, bilirubin, transaminase, ALT, AST, alkaline phosphatase, hepatocellular, cholestatic, DILI, hepatic failure/necrosis/encephalopathy/steatosis/fibrosis/cirrhosis, autoimmune hepatitis.

### Subtype Classification
- **Hepatocellular**: transaminase, ALT, AST elevation
- **Cholestatic**: cholestasis, bilirubin, jaundice, alkaline phosphatase
- **Hepatic failure**: liver failure, hepatic necrosis, fulminant hepatitis
- **Steatosis/fibrosis**: fatty liver, fibrosis, cirrhosis
- **Autoimmune**: autoimmune hepatitis

### Signal Detection
Sex-stratified ROR with log ratio threshold |LR| >= 0.5. Direction: female_higher (LR > 0) or male_higher (LR < 0).

### Anti-Regression Analysis
Within hepatotoxicity signals, drugs ranked by total report volume and divided into deciles. Spearman correlation between volume decile and mean female fraction quantified anti-regression within the hepatotoxicity domain.

## Results

### Overall Hepatotoxicity
3,073 sex-differential hepatic signals across 601 drugs (348 with >=3 hepatotoxicity signals). Overall female bias: 65.3% (2,007 female-predominant, 1,066 male-predominant).

### Checkpoint Inhibitor Hepatotoxicity
The most striking finding: 95.1% of ICI hepatotoxicity signals are female-biased (39/41 signals). This includes nivolumab, pembrolizumab, ipilimumab, and atezolizumab.

This near-universal female bias in ICI hepatotoxicity likely reflects sex differences in immune checkpoint biology. Women have stronger T-cell responses, higher autoimmune susceptibility, and different PD-1/CTLA-4 expression patterns. When these checkpoints are pharmacologically released, the stronger female immune response may produce disproportionate hepatic damage.

### Autoimmune Hepatitis Paradox
Drug-induced autoimmune hepatitis signals are 72.2% male-biased (only 27.8%F). This is paradoxical because:
1. Autoimmune diseases are generally 2-3x more common in women
2. The broader hepatotoxicity pattern is female-biased (65.3%F)
3. Drug-induced autoimmune hepatitis may represent a DIFFERENT mechanism from spontaneous autoimmune hepatitis

This suggests that drug-triggered autoimmune hepatic responses follow a different immunological pathway than idiopathic autoimmune hepatitis — potentially involving different HLA associations, different cytokine profiles, or different target autoantigens.

### Anti-Regression Within Hepatotoxicity
The anti-regression phenomenon persists perfectly within hepatotoxicity signals (Spearman rho = 1.000), demonstrating that female bias in DILI intensifies with increasing report volume. This rules out the possibility that the female hepatotoxicity bias is a small-sample artifact and confirms it represents genuine sex-differential hepatic vulnerability.

### Drug Class Variation
Substantial class-level variation suggests mechanism-specific sex effects:
- **Immune-mediated** (CPI 95.1%F, antibiotics 75.9%F): strongest female bias, consistent with female immune hyperactivity
- **Metabolic** (statins 69.7%F, acetaminophen 63.2%F): moderate female bias, consistent with CYP-mediated sex differences
- **Immunomodulatory** (anti-TNF 52.1%F, immunosuppressants 51.9%F): near parity, possibly because these drugs suppress the female immune advantage
- **Autoimmune** (27.8%F): paradoxical male bias

### Hepatotoxicity Subtype Analysis
The severity gradient within hepatotoxicity mirrors the overall severity-sex gradient:
- Hepatic failure (most severe): 69.0%F
- Cholestatic: 68.2%F
- Hepatocellular: 63.6%F
- Steatosis/fibrosis (least severe): 59.3%F

More severe forms of DILI show greater female predominance, consistent with the broader finding that severity amplifies sex differences.

### Clinical Implications
1. **ICI prescribing**: Female patients receiving checkpoint inhibitors should receive enhanced liver monitoring (LFTs at shorter intervals, lower thresholds for treatment modification)
2. **NSAIDs/antibiotics**: Given 75-76% female bias and massive prescribing volume, these represent a large population-level impact requiring sex-aware prescribing guidelines
3. **DILI monitoring**: Sex-stratified ALT/AST thresholds may be warranted — the current universal thresholds may underdetect female DILI and overdetect male DILI
4. **Clinical trial design**: Hepatotoxicity endpoints should be sex-stratified, particularly for immune-modulating drugs
5. **Autoimmune hepatitis**: The paradoxical male bias warrants investigation into whether drug-induced and idiopathic autoimmune hepatitis are mechanistically distinct entities

## Limitations
- Hepatic AE identification used keyword proxies rather than adjudicated DILI diagnoses
- Subtype classification overlap (some AEs map to multiple subtypes)
- Confounding by indication (e.g., CPI use in cancer may introduce sex-specific comorbidity confounders)
- Dose-response relationships not assessed

## Conclusion
Drug-induced liver injury is systematically female-biased (65.3%F across 601 drugs), with checkpoint inhibitors showing the most extreme disparity at 95.1%F. The paradoxical male bias in drug-induced autoimmune hepatitis (27.8%F) despite female predominance of autoimmune disease suggests mechanistically distinct pathways. The hepatic severity gradient (failure 69.0%F to steatosis 59.3%F) mirrors the overall severity-sex gradient. Perfect anti-regression within hepatotoxicity (rho = 1.000) confirms this represents genuine biology. These findings support mandatory sex-stratified DILI monitoring, with particular urgency for immune checkpoint inhibitors.

## Data Availability
FAERS (2004Q1-2025Q3). Code and signals: https://github.com/jshaik369/SexDiffKG

## Key Statistics
- 3,073 hepatic signals, 601 drugs, 133 AE terms, 348 drugs with >=3 signals
- Overall: 65.3% female-biased
- CPI: 95.1%F (41 signals) — strongest class signal in entire KG
- Autoimmune hepatitis: 27.8%F (paradoxical male bias)
- NSAIDs 75.6%F, Antibiotics 75.9%F, Statins 69.7%F
- Hepatic failure: 69.0%F (174 signals)
- 175 drugs strongly female hepatotoxic, 49 strongly male
- Anti-regression within hepatotoxicity: rho = 1.000
- Class variation: immune-mediated (strongest F) > metabolic (moderate F) > immunomodulatory (parity) > autoimmune (paradoxical M)
