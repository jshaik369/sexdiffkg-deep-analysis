---
title: "Sex-Differential Drug-Induced Liver Injury: Checkpoint Inhibitor Hepatotoxicity Is 95% Female-Biased Across 601 Drugs"
authors: "Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)"
affiliation: "CoEvolve Network, Independent Researcher, Barcelona, Spain"
email: "jshaik@coevolvenetwork.com"
orcid: "0009-0002-1748-7516"
target_journal: "Hepatology / Journal of Hepatology"
draft_version: "v1.0"
date: "2026-03-04"
---

## Abstract

**Background:** Drug-induced liver injury (DILI) is the leading cause of acute liver failure in Western countries, yet sex differences in hepatotoxicity have been incompletely characterized across the pharmacopeia.

**Methods:** We analyzed 3,073 sex-differential hepatotoxicity signals from 14.5 million FAERS reports (2004Q1-2025Q3) across 601 drugs, classifying signals into hepatocellular injury, cholestatic, hepatic failure, steatosis/fibrosis, and autoimmune subtypes.

**Results:**

Overall hepatotoxicity is 65.3% female-biased (3,073 signals, 601 drugs, 133 hepatic AE terms).

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
1. **Checkpoint inhibitor hepatotoxicity** is nearly universally female-biased (95.1%F) — the strongest class-specific signal in the entire KG
2. **Autoimmune hepatitis** is strongly MALE-biased (27.8%F) — a paradox since autoimmune diseases are generally female-predominant
3. **175 drugs** show strongly female hepatotoxicity (>=70%F), vs only **49 drugs** with male hepatotoxicity (<=30%F)
4. Hepatic severity gradient: severe liver failure 69.3%F vs mild hepatic effects 63.7%F
5. NSAIDs and antibiotics — two of the most commonly prescribed drug classes — show 75-76% female hepatotoxicity bias

**Conclusions:** Drug-induced liver injury is systematically female-biased, with checkpoint inhibitors showing the most extreme disparity (95%F). The paradoxical male bias in autoimmune hepatitis signals despite female predominance of autoimmune disease adds another dimension to the sex-differential pharmacovigilance landscape. These findings support sex-stratified DILI monitoring, particularly for immune checkpoint inhibitors.

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

## Results

### Overall Hepatotoxicity
3,073 sex-differential hepatic signals across 601 drugs. Overall female bias: 65.3% (2,007 female-predominant, 1,066 male-predominant).

### Checkpoint Inhibitor Hepatotoxicity
The most striking finding: 95.1% of ICI hepatotoxicity signals are female-biased (39/41 signals). This includes nivolumab, pembrolizumab, ipilimumab, and atezolizumab.

This near-universal female bias in ICI hepatotoxicity likely reflects sex differences in immune checkpoint biology. Women have stronger T-cell responses, higher autoimmune susceptibility, and different PD-1/CTLA-4 expression patterns. When these checkpoints are pharmacologically released, the stronger female immune response may produce disproportionate hepatic damage.

### Autoimmune Hepatitis Paradox
Drug-induced autoimmune hepatitis signals are 72.2% male-biased (only 27.8%F). This is paradoxical because:
1. Autoimmune diseases are generally 2-3x more common in women
2. The broader hepatotoxicity pattern is female-biased (65.3%F)
3. Drug-induced autoimmune hepatitis may represent a DIFFERENT mechanism from spontaneous autoimmune hepatitis

This suggests that drug-triggered autoimmune hepatic responses follow a different immunological pathway than idiopathic autoimmune hepatitis.

### Clinical Implications
1. **ICI prescribing**: Female patients receiving checkpoint inhibitors should receive enhanced liver monitoring
2. **NSAIDs/antibiotics**: Given 75-76% female bias and massive prescribing volume, these represent a large population-level impact
3. **DILI monitoring**: Sex-stratified ALT/AST thresholds may be warranted
4. **Clinical trial design**: Hepatotoxicity endpoints should be sex-stratified

## Data Availability
FAERS (2004Q1-2025Q3). Code and signals: https://github.com/jshaik369/SexDiffKG

## Key Statistics
- 3,073 hepatic signals, 601 drugs, 133 AE terms
- Overall: 65.3% female-biased
- CPI: 95.1%F (41 signals) — strongest class signal
- Autoimmune hepatitis: 27.8%F (paradoxical male bias)
- NSAIDs 75.6%F, Antibiotics 75.9%F, Statins 69.7%F
- Hepatic failure: 69.0%F (174 signals)
- 175 drugs strongly female hepatotoxic, 49 strongly male
