# Autoimmune/Immunology Sex-Differential Analysis (2026-03-04)

## Data
- Source: `results/signals_v4/sex_differential_v4.parquet` (96,281 signals)
- Results: `results/analysis/autoimmune_sex_diff.json`
- 13,692 signals across 42 drugs, 6 classes

## Key Finding: Indication Drives Sex Bias More Than Mechanism

Drug class sex bias correlates with disease sex ratio, not drug mechanism:
- Lupus/transplant drugs (9:1 F disease) → 70-80% female AE bias
- RA drugs (3:1 F) → 50-60% female bias
- MS drugs (2-3:1 F) → paradoxically male-biased AEs
- Dermatology drugs (balanced disease) → male-biased AEs

## Drug Class Overview

| Class | Signals | %F | Key Driver |
|-------|---------|-----|-----------|
| Corticosteroids | 3,387 | 69.3% | Lupus/inflammatory |
| Conventional DMARDs | 3,692 | 57.9% | Mixed RA/transplant |
| Anti-CD20 | 1,032 | 58.4% | RA vs MS split |
| JAK inhibitors | 676 | 46.2% | RA balanced |
| TNF inhibitors | 2,382 | 45.0% | RA predominant |
| IL-targeted | 2,523 | 43.2% | Dermatology skew |

## Anti-CD20 Paradox (Same mechanism, opposite bias)
- Rituximab (RA/lymphoma): 66.6% F
- Ocrelizumab (MS): 28.7% F
- Ofatumumab (MS): 11.9% F
→ Same CD20 mechanism, opposite AE sex profile — driven by disease population

## Biologics vs Conventional
- Biologics: 46.6% F (5,937 signals)
- Conventional: 63.4% F (7,079 signals)
→ 17 percentage point gap

## Universal Sex Patterns Across ALL Classes
- **DVT**: 0/13 signals female-higher (universally male)
- **PE**: 1/15 signals female-higher (universally male)
- **ILD**: 8/8 signals female-higher (universally female)
- **Anaphylaxis**: predominantly female across TNF + DMARDs
- **TB**: 27% F — strong male predominance
- **Fungal infections**: 23% F — strong male predominance

## Publication Target
- Drug Safety (IF 4.0) or Arthritis & Rheumatology (IF 13.3)
- Paper: Indication-Dependent Sex Bias in Immunosuppressant Adverse Events
- Unique angle: Same mechanism (anti-CD20) shows opposite sex bias by disease
