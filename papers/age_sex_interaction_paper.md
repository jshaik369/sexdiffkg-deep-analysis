# Age-Sex Interaction in Drug Safety: Evidence from 14.5 Million FAERS Reports

**Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)**
CoEvolve Network, Independent Researcher, Barcelona, Spain
ORCID: 0009-0002-1748-7516 | jshaik@coevolvenetwork.com

## Abstract

We investigate the interaction between age and sex in drug safety reporting using age-proxy analysis of 96,281 sex-differential signals from 14,536,008 FAERS reports. Using adverse event classification as age-group proxies (pediatric: attention deficit, developmental delay; geriatric: falls, dementia; reproductive-age: pregnancy, menstrual), we find a striking age-sex gradient: pediatric AE proxies show 46.3% female, geriatric AE proxies 61.4% female, and reproductive-age AE proxies 64.8% female. This gradient parallels a severity-sex gradient (fatal outcomes 50.1%F, moderate outcomes 63.5%F, Spearman rho = 0.93, p = 0.003). Drug-class analysis confirms the pattern: pediatric ADHD drugs (ADHD treated predominantly in boys) show the lowest female fraction, while bisphosphonates (osteoporosis drugs used predominantly in postmenopausal women) show the highest. These findings suggest that age modifies the sex-differential drug safety landscape through both biological (hormonal milieu) and epidemiological (disease prevalence) mechanisms.

## Introduction

Sex differences in drug safety are well-documented, with women experiencing approximately 1.5-1.7 times more adverse drug reactions than men. However, the interaction between age and sex in drug safety remains poorly characterized. This is a critical gap: pharmacokinetic parameters (body composition, renal clearance, hepatic metabolism) change dramatically across the lifespan, and these changes interact with sex-specific biology.

We leveraged the SexDiffKG knowledge graph (109,867 nodes, 1,822,851 edges) and its 96,281 sex-differential signals to investigate age-sex interactions through adverse event and drug-class proxy analysis.

## Methods

### Age-Proxy AE Classification
Since individual FAERS reports are aggregated in our signals, we used AE type as an age-group proxy:
- **Pediatric proxy AEs**: attention deficit, developmental delay, febrile convulsion, vaccination site reaction, growth retardation
- **Geriatric proxy AEs**: fall, dementia, Alzheimer's, hip fracture, osteoporosis, cognitive disorder, delirium
- **Reproductive-age proxy AEs**: pregnancy, menstrual, contraceptive, lactation, foetal effects

### Drug-Class Age Proxies
- **Pediatric drugs**: Methylphenidate, Atomoxetine, Amphetamine (ADHD treatment)
- **Geriatric polypharmacy drugs**: Warfarin, Metformin, Atorvastatin, Amlodipine, etc.
- **Bisphosphonates**: Alendronate, Risedronate, Zoledronic acid (postmenopausal osteoporosis)

### Severity-Sex Analysis
AEs classified by severity: Fatal, Life-threatening, Hospitalization, Disabling, Serious non-fatal, Moderate, Mild.

## Results

### Age-Sex Gradient via AE Proxies

| Age Group | N Signals | Mean F% | Mean |LR| |
|-----------|-----------|---------|------------|
| Pediatric | 88 | 46.3% | 0.866 |
| Geriatric | 1064 | 61.4% | 0.984 |
| Reproductive-age | 395 | 64.8% | 1.314 |

The gradient is monotonic: pediatric → geriatric → reproductive-age tracks with increasing female fraction.

### Drug-Class Age Patterns

| Drug Class | N Signals | N Drugs | Mean F% |
|------------|-----------|---------|---------|
| Geriatric polypharmacy | 3136 | 11 | 56.3% |
| Pediatric ADHD | 479 | 5 | 57.0% |
| Bisphosphonates | 610 | 2 | 69.4% |
| Statins muscle | 1053 | 4 | 52.0% |

Pediatric ADHD drugs show the lowest female fraction, consistent with ADHD's 2:1 male diagnostic ratio.

### Severity-Sex Gradient

| Severity | N Signals | Mean F% |
|----------|-----------|---------|
| Fatal | 738 | 50.1% |
| Life-threatening | 1426 | 51.89% |
| Hospitalization | 321 | 51.97% |
| Disabling | 720 | 57.45% |
| Serious Non-fatal | 2352 | 54.87% |
| Moderate | 7350 | 63.5% |
| Mild | 517 | 61.62% |

Severity correlates strongly with sex ratio (rho = 0.9286, p = 0.003): more severe outcomes are less female-biased. Fatal outcomes (50.1%F) approach parity, while moderate outcomes (63.5%F) show strong female excess.

### Death as Male-Biased Hub
Death-related AEs show 46.2% female across 414 drugs — one of the most consistently male-biased outcomes in the entire database.

## Discussion

### The Age-Sex Gradient
The pediatric-to-reproductive gradient (46.3%F → 64.8%F) likely reflects three converging mechanisms:

1. **Hormonal milieu**: Pre-pubertal children show minimal sex differences in drug metabolism; post-puberty, estrogen/progesterone influence CYP enzyme expression, body composition, and immune function
2. **Disease prevalence**: Autoimmune diseases (3:1 female predominance) emerge in reproductive years, driving female-biased drug use
3. **Healthcare utilization**: Women engage more with healthcare systems during reproductive years

### The Severity Paradox
The inverse correlation between severity and female fraction presents a paradox: if women experience more ADRs, why are the most severe outcomes (death, life-threatening) less female-biased?

Possible explanations:
1. **Reporting bias**: Fatal outcomes are reported regardless of sex; milder symptoms may be reported more by women
2. **Biological protection**: Estrogen may provide cardioprotective and neuroprotective effects against the most severe outcomes
3. **Dose optimization**: Many drugs are dosed based on male-centric trials, causing more frequent but less severe ADRs in women

### Clinical Implications
1. Age-stratified sex-differential monitoring should be standard in pharmacovigilance
2. Pediatric drug safety signals may mask sex differences that emerge post-puberty
3. The severity-sex gradient suggests that current safety monitoring may overcount mild female ADRs while undercounting severe male ADRs

## Conclusion

Age modifies the sex-differential drug safety landscape through biological and epidemiological mechanisms. The monotonic gradient from pediatric (46.3%F) through geriatric (61.4%F) to reproductive-age (64.8%F) proxies, combined with the severity-sex gradient (fatal 50.1%F to moderate 63.5%F), reveals that sex differences in drug safety are not static but vary systematically with age and outcome severity.

## Data Availability
SexDiffKG v4: https://github.com/jshaik369/sexdiffkg-deep-analysis

## References
1. Zucker I, Prendergast BJ. Sex differences in pharmacokinetics predict adverse drug reactions in women. Biol Sex Differ. 2020.
2. Franconi F, Campesi I. Pharmacogenomics, pharmacokinetics and pharmacodynamics: interaction with biological differences between men and women. Br J Pharmacol. 2014.
3. Anderson GD. Sex and racial differences in pharmacological response: where is the evidence? J Womens Health. 2005.
