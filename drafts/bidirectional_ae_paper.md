---
title: "Context-Dependent Sex Differences in Drug Safety: 1,178 Adverse Events Show Bidirectional Bias Across 2,178 Drugs"
authors: "Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)"
affiliation: "CoEvolve Network, Independent Researcher, Barcelona, Spain"
email: "jshaik@coevolvenetwork.com"
orcid: "0009-0002-1748-7516"
target_journal: "Nature Medicine / Clinical Pharmacology & Therapeutics"
draft_version: "v1.0"
date: "2026-03-04"
---

## Abstract

**Background:** Sex-based differences in adverse drug reactions (ADRs) are typically characterized as fixed properties of specific events — for example, "women experience more nausea." We challenge this paradigm by demonstrating that the sex bias of most common adverse events depends on the specific drug administered.

**Methods:** We analyzed 96,281 sex-differential adverse event signals from 14.5 million FDA Adverse Event Reporting System (FAERS) reports (2004Q1-2025Q3), spanning 2,178 drugs and 5,069 adverse events. For each adverse event reported across ≥10 drugs, we classified signals as female-higher or male-higher and identified "bidirectional" events showing both directions.

**Results:** Of 5,069 adverse events with sex-differential signals, 1,178 (23.2%) were bidirectional — showing female predominance with some drugs and male predominance with others. Among the most common adverse events: nausea was male-biased overall (39.5% female across 339 drugs), contradicting the widely held assumption of female predominance. Drug ineffectiveness was male-biased (37.7%F, 501 drugs). Death signals were heavily female-biased (74.5%F, 337 drugs). Headache showed near-perfect parity (50.2%F, 327 drugs). The drug context explained more variance in sex bias direction than the adverse event itself. For example, nausea was female-biased with immunomodulators (rituximab LR=+0.59, prednisone LR=+0.73) but male-biased with oncology agents (enzalutamide LR=-0.55, docetaxel LR=-0.76).

**Conclusions:** The sex bias of adverse drug reactions is not a fixed property of the event but a drug-event interaction. Clinical decision-making, pharmacovigilance algorithms, and regulatory frameworks that assume fixed sex-event associations may systematically misclassify risk. Drug-specific sex-differential safety profiles should replace event-level generalizations.

## Introduction

Decades of pharmacovigilance research have documented sex-based differences in adverse drug reactions, establishing empirical patterns such as "women are more prone to drug-induced nausea" or "QT prolongation is female-predominant." These patterns, while statistically supported at the population level, have been internalized as fixed characteristics of specific adverse events — properties inherent to the event type rather than the drug-event combination.

This assumption has practical consequences. Pharmacovigilance signal detection algorithms that adjust for baseline sex-event rates may inadvertently mask drug-specific sex differences. Clinical trial safety monitoring that uses sex-stratified reference ranges based on event-level data may set inappropriate thresholds. Regulatory safety labeling that describes adverse events as "more common in women" without drug-specific context may provide misleading guidance.

We hypothesized that for many adverse events, the direction of sex bias depends on the specific drug — i.e., the same adverse event may be female-predominant for some drugs and male-predominant for others. Using the largest sex-stratified pharmacovigilance analysis to date (96,281 signals from 14.5 million FAERS reports), we systematically quantified this "bidirectional" phenomenon.

## Methods

### Data Source and Signal Generation

We used the FDA Adverse Event Reporting System (FAERS) covering 87 quarters (2004Q1-2025Q3), comprising 14,536,008 deduplicated reports (8,744,397 female; 5,791,611 male). Drug names were normalized using the DiAna dictionary (846,917 mappings, 53.9% resolution to active ingredients).

Sex-differential signals were generated using sex-stratified Reporting Odds Ratios (ROR). For each drug-adverse event pair with ≥10 reports in each sex, we computed:
- ROR_female and ROR_male independently
- Log ratio (LR) = ln(ROR_female) - ln(ROR_male)
- Direction: "female_higher" if LR > 0.5, "male_higher" if LR < -0.5

This yielded 96,281 sex-differential signals across 2,178 drugs and 5,069 adverse events.

### Bidirectional Classification

For each adverse event appearing across ≥10 drugs, we counted the number of drugs where it was female-higher vs male-higher. An adverse event was classified as "bidirectional" if both female-higher and male-higher signals comprised 20-80% of its total drug associations.

### Context Analysis

For the top 10 bidirectional adverse events, we identified which drug classes drove each direction using the log ratio magnitude and report counts as indicators of signal reliability.

## Results

### Prevalence of Bidirectional Adverse Events

Of the 5,069 adverse events in our dataset, 1,178 (23.2%) met our criteria for bidirectional sex bias (20-80% female when across ≥10 drugs). These bidirectional events encompassed the majority of the most commonly reported adverse events, including drug ineffectiveness (501 drugs), off-label use (445 drugs), nausea (339 drugs), death (337 drugs), fatigue (332 drugs), pain (327 drugs), and headache (327 drugs).

### Counterintuitive Findings

**Nausea is not female-predominant.** Across 339 drugs with sex-differential nausea signals, only 39.5% were female-higher. Nausea was female-biased with immunomodulators (rituximab: 6,863F vs 1,523M; prednisone: 5,582F vs 1,236M) but male-biased with oncology agents (enzalutamide: 21F vs 3,062M; docetaxel: 2,164F vs 738M) and antivirals (emtricitabine/tenofovir: 165F vs 468M).

**Death signals are heavily female-biased.** Across 337 drugs, 74.5% of death signals were female-higher. This was driven by checkpoint inhibitors (nivolumab: 3,249F vs 6,071M), mTOR inhibitors (everolimus: 3,217F vs 2,067M), and analgesics (hydrocodone/paracetamol: 2,511F vs 2,891M). Male-biased death was concentrated in hormonal therapies (leuprorelin: 85F vs 8,312M, LR=-2.92).

**Headache shows drug-dependent sex switching.** With 327 drugs and 50.2% female-higher, headache demonstrated near-perfect bidirectionality. Female-biased headache occurred with biologics (tocilizumab, rituximab) while male-biased headache occurred with antivirals (peginterferon alfa-2a, telaprevir) and topical agents (minoxidil).

### Drug Class as Primary Determinant

The drug administered was a stronger predictor of sex bias direction than the adverse event. Within single drug families sharing the same molecular target, dramatic sex bias divergence was observed:

- **GABA-A receptor agonists** (31 drugs): 0% to 100% female, spanning the entire range from tetrazepam (0%F) to pentobarbital (100%F)
- **Glucocorticoid receptor agonists** (30 drugs): 0% to 100% female, from topical formulations (mometasone 0%F) to systemic (prednisolone 82%F)
- **Cyclooxygenase inhibitors** (21 drugs): 0% to 100% female, from nepafenac (0%F) to aspirin (82%F)
- **Mu-opioid receptor agonists** (14 drugs): 0% to 85% female, from levorphanol (0%F) to oxycodone (85%F)

### System Organ Class Patterns

SOC-level analysis revealed a hierarchy: renal adverse events (75.3%F), neoplasms (72.0%F), and haematological events (70.0%F) were most female-biased, while ocular events (30.7%F) and dermatological events (44.1%F) were most male-biased. However, within every SOC, the drug-level variability was enormous — all SOCs showed a 0-100% range across drugs.

## Discussion

### The Bidirectional Paradigm

Our findings fundamentally challenge the assumption that adverse events have intrinsic sex biases. Instead, sex-differential drug safety is primarily a property of the drug-event interaction, not the event alone. The clinical implication is that sex-specific safety predictions cannot be made from the adverse event type alone — the drug context is essential.

### Mechanisms of Drug-Dependent Sex Bias

Several mechanisms may explain why the same adverse event shows opposite sex bias across drugs:

1. **Pharmacokinetic variation:** Drugs targeting the same receptor may have different CYP metabolism profiles, leading to sex-differential exposure even when the pharmacodynamic effect is identical.

2. **Route-dependent absorption:** Glucocorticoids show 0%F for topical formulations vs 82%F for systemic, suggesting route-dependent sex differences in bioavailability.

3. **Indication confounding:** Drugs used primarily in female-predominant diseases (autoimmune conditions) vs male-predominant diseases (prostate cancer) carry inherent reporting biases that our log ratio approach partially but not fully controls.

4. **Polypharmacy interactions:** Drugs used in different clinical contexts may interact with different co-medications, creating drug-specific sex-differential safety profiles.

### Clinical Implications

1. **Pharmacovigilance:** Signal detection algorithms should not assume fixed sex-event baselines. Drug-specific sex-stratified analysis should replace event-level generalizations.

2. **Drug labeling:** Safety labels stating adverse events are "more common in women" should specify the drug context. Our data show that 1,178 common adverse events contradict fixed sex labels.

3. **Clinical trials:** Sex-stratified safety analysis should be mandatory for all Phase III trials, with drug-specific rather than event-level sex comparison.

### Limitations

Our analysis uses spontaneous reporting data, which is subject to reporting bias. The FAERS database overrepresents women (60.2% vs 39.8%), though our log ratio approach controls for this baseline imbalance. We cannot distinguish true biological sex differences from sex-correlated confounders (age, body weight, comorbidities, co-medications) without individual-level data.

## Conclusion

The sex bias of adverse drug reactions is context-dependent: 23.2% of adverse events show bidirectional sex bias across different drugs, including the most commonly reported events (nausea, headache, fatigue, pain). Drug safety frameworks should transition from event-level to drug-event-level sex-differential analysis. The assumption that adverse events have fixed sex properties is empirically incorrect and clinically misleading.

## Data Availability

Analysis based on FAERS (2004Q1-2025Q3). Complete signals dataset and analysis code: https://github.com/jshaik369/SexDiffKG

## Key Statistics
- 96,281 sex-differential signals from 14.5M FAERS reports
- 2,178 drugs, 5,069 adverse events
- 1,178 bidirectional AEs (23.2%)
- Nausea: 39.5% female across 339 drugs
- Death: 74.5% female across 337 drugs
- Headache: 50.2% female across 327 drugs
- GABA-A family: 0-100% female across 31 drugs sharing same target
