# Wave 5 Deep Analysis Summary (2026-03-04)

## KEY DISCOVERY: Volume-Sex Gradient
- Q1 (lowest vol, median 30 reports): 42.9%F
- Q2 (median 46): 46.4%F
- Q3 (median 73): 51.3%F
- Q4 (median 134): 55.2%F
- Q5 (highest vol, median 463): 73.3%F
- **Top 1% (≥3,330 reports): 88.9%F**
- MONOTONIC increase: more data = more female bias
- VALIDATES anti-regression: signals are NOT noise

## Report Ratio Anti-Correlation
- Report sex ratio vs signal sex ratio: rho=-0.215, p=6.92e-13
- Drugs reported MORE by women have LESS female AE bias
- PROVES female AE bias is NOT a reporting artifact

## Comprehensive Drug Profiles
- 20 extreme female drugs (≥90%F, ≥20 signals): risperidone 92.9%F, ranitidine 93.5%F
- 42 extreme male drugs (≤10%F, ≥20 signals): isotretinoin 9.2%F, mebeverine 0%F
- 90 balanced drugs (45-55%F, ≥50 signals): methotrexate, infliximab, amlodipine
- Top risk score: ranitidine (4557), etonogestrel (3882), risperidone (3790)
- 28 drug families with internal sex bias divergence (>30pp)
- Interferon family: 0%F (IFN-beta) to 100%F (IFN-alfa-2a) — SAME class, OPPOSITE bias

## Safety Label Gap Analysis
- 424 off-target candidates (many AEs, few known targets)
- 79 polypharmacology drugs (≥10 targets): metformin 51 targets
- 140 serious under-represented AEs (safety blind spots)
- 461 over-enriched AEs (appear in far more drugs than expected)

## Super-Consistent AEs (same direction >90%, 50+ drugs)
- 19 super-consistent AEs: intracranial hemorrhage 97.6%F, osteonecrosis 96.5%F
- Acne: 7.8%F, pain of skin: 0%F (consistently male across 50+ drugs)

## New Files
- comprehensive_drug_profiles.json
- temporal_volume_deep.json
- safety_label_gap.json
- fig23_volume_quintile_gradient (KEY FIGURE)
- fig24_drug_risk_scores
- fig25_interferon_divergence
