# Information-Theoretic Characterization of Sex-Differential Drug Safety Signals

Mohammed Javeed Akhtar Abbas Shaik (J.Shaik)
CoEvolve Network, Independent Researcher, Barcelona, Spain
jshaik@coevolvenetwork.com | ORCID: 0009-0002-1748-7516

## Abstract

We apply information-theoretic measures to characterize sex-differential drug safety signals
from the FDA Adverse Event Reporting System (FAERS; 14.5M reports, 96,281 signals, 2,178 drugs).
Binary entropy analysis reveals an "entropy anti-regression": drugs with higher report volume
show LOWER entropy (more predictable sex distribution; ρ = −0.952, p = 2.3 × 10⁻⁵), confirming
that the sex bias intensification phenomenon translates to increased predictability in
information-theoretic terms. The most sex-predictable drugs include niraparib (H = 0.254,
95.8%F) and enzalutamide (H = 0.335, 6.2%F), while balanced drugs approach maximum entropy
(H = 1.0). Mutual information analysis identifies adverse events where drug identity most
strongly predicts reporter sex, with folliculitis (MI = 0.320), obesity (MI = 0.318), and
blood cholesterol increased (MI = 0.315) as top informative AEs. These findings establish
information theory as a complementary framework for pharmacovigilance signal prioritization,
where low-entropy drug-AE pairs warrant heightened sex-specific monitoring.

## Introduction

Traditional pharmacovigilance signal detection relies on disproportionality measures
(Reporting Odds Ratios, PRR, BCPNN) to identify drug-adverse event associations.
Sex-stratified analysis adds a layer by computing sex-specific rates. However, these
approaches do not directly quantify the information content of sex-differential signals
or the predictability of sex distributions across the pharmacopeia.

Information theory provides a natural framework for this analysis. The binary entropy
H(sex|drug) measures how uncertain we are about a reporter's sex given which drug they
reported, with H = 1.0 representing complete uncertainty (50/50) and H = 0 representing
perfect prediction. The mutual information I(drug; sex) for each adverse event quantifies
how much knowing the drug reduces uncertainty about sex.

## Methods

### Binary Entropy per Drug
For each drug d with mean female fraction p_d across its sex-differential signals:
H(d) = −p_d log₂(p_d) − (1 − p_d) log₂(1 − p_d)

### Mutual Information per Adverse Event
For each adverse event a:
I(drug; sex | a) = H(sex|a) − H(sex|drug, a)
where H(sex|a) is the overall binary entropy and H(sex|drug, a) is the
weighted-average conditional entropy across drugs.

### Entropy Anti-Regression
Drugs were divided into deciles by total report volume. The Spearman
correlation between volume decile and mean entropy tests whether
higher-volume drugs are more or less predictable.

## Results

### Drug Entropy Distribution
Among 1,394 drugs with ≥5 signals, mean entropy was 0.949 (close to maximum 1.0),
indicating that most drugs have relatively balanced sex distributions. However,
the distribution is left-skewed with a tail of highly predictable drugs.

**Most predictable (lowest entropy):**
- Niraparib: H = 0.254 (95.8%F) — PARP inhibitor for ovarian cancer
- Fulvestrant: H = 0.259 (95.6%F) — ER antagonist for breast cancer
- Palbociclib: H = 0.314 (94.3%F) — CDK4/6 inhibitor for breast cancer
- Enzalutamide: H = 0.335 (6.2%F) — AR antagonist for prostate cancer

### Entropy Anti-Regression
The correlation between report volume decile and mean entropy was strongly
negative (ρ = −0.952, p = 2.3 × 10⁻⁵): high-volume drugs have systematically
lower entropy. This is the information-theoretic expression of the anti-regression
phenomenon—drugs with more reports become more sex-predictable, not less.

Volume decile progression:
- D0 (lowest volume): H = 0.982, 52.4%F
- D5 (medium): H = 0.946, 55.9%F
- D9 (highest volume): H = 0.908, 64.1%F

### AE Mutual Information
Among 1,668 adverse events analyzed, mean MI was 0.100 bits. The most
informative AEs—where drug identity most strongly predicts sex—were:
1. Folliculitis (MI = 0.320, 46 drugs)
2. Obesity (MI = 0.318, 91 drugs)
3. Blood cholesterol increased (MI = 0.315, 122 drugs)
4. Hip arthroplasty (MI = 0.297, 42 drugs)

These high-MI AEs represent conditions where the sex distribution varies most
across drugs—suggesting drug-specific rather than condition-specific sex effects.

### Information Concentration
The distribution of sex information is not concentrated in a few drugs:
- Top 10 drugs: 0.3% of total entropy
- Top 100 drugs: 5.1% of total entropy
- Top 500 drugs: 32.9% of total entropy

This diffuse distribution suggests that sex-differential safety is a
system-wide property rather than driven by a few outlier drugs.

## Discussion

The information-theoretic framework offers several advantages over traditional
approaches:

1. **Unified scale**: Entropy provides a single metric (0–1) that captures
sex predictability regardless of direction, unlike female fraction which
conflates magnitude and direction.

2. **Prioritization**: Low-entropy drugs warrant heightened sex-specific
monitoring because their sex distributions are highly non-random.

3. **Anti-regression interpretation**: The entropy decrease with volume
(ρ = −0.952) demonstrates that the anti-regression phenomenon is not simply
a shift in means but a genuine increase in signal-to-noise ratio.

4. **AE-level insights**: Mutual information identifies adverse events where
drug-specific rather than generic sex effects dominate, focusing attention
on mechanistically interesting signals.

## Conclusion

Information-theoretic analysis reveals that sex-differential drug safety
signals follow a structured pattern: high-volume drugs are more sex-predictable
(entropy anti-regression), specific AEs carry high mutual information about
sex given drug identity, and sex information is diffusely distributed across
the pharmacopeia. This framework provides a complementary lens for
pharmacovigilance signal prioritization and sex-specific safety monitoring.

## Data Availability
SexDiffKG v4, all analysis outputs, and code available at:
https://github.com/jshaik369/sexdiffkg-deep-analysis

## Keywords
information theory, entropy, mutual information, pharmacovigilance, sex differences, FAERS
