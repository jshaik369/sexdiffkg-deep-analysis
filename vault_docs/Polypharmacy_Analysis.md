# Polypharmacy Sex-Differential Analysis (2026-03-04)

## Data
- Source: results/signals_v4/sex_differential_v4.parquet (96,281 signals)
- Results: results/analysis/polypharmacy_analysis.json

## Overview
- Single-drug signals: 90,421 (93.9%), 54.0% female-higher
- Combination signals: 5,860 (6.1%), 50.6% female-higher
- 271 unique combinations
- Combos are 3.4pp LESS female-biased than singles

## Key Patterns
- Opioid+paracetamol combos: 76-81% female (matching single opioid pattern)
- Inhaled corticosteroid/LABA (COPD): 14-38% female (disease population effect)
- Opioid combinations overall: 549 signals, 77.6% female

## Emergent Combination Effects
- SACUBITRIL;VALSARTAN (68% F) >> valsartan alone (49% F) -- heart failure emergent effect
- EMTRICITABINE;TENOFOVIR (48% F) << both singles (64% F) -- HIV PrEP male population
- FLUTICASONE;VILANTEROL (19% F) < either single -- COPD population effect

## Top Combinations
1. SULFAMETHOXAZOLE;TRIMETHOPRIM: 327 signals, 64% F
2. OXYCODONE;PARACETAMOL: 265 signals, 81% F
3. FLUTICASONE;SALMETEROL: 252 signals, 36% F
4. BUDESONIDE;FORMOTEROL: 245 signals, 38% F
5. CARBIDOPA;LEVODOPA: 217 signals, 62% F

## Publication Note
Polypharmacy sex differences are UNEXPLORED in literature. The emergent combination effects (where combo differs from components) could support a standalone methods paper.
