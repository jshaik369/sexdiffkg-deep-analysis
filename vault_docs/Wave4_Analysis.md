# Wave 4 Deep Analysis Summary (2026-03-04)

## Analyses Completed

### 1. Severity-Sex Gradient
- **KEY FINDING**: More severe AEs are more female-biased
- Moderate: 50.2%F → Serious: 69.5%F → Life-threatening/Fatal: 68.2%F
- 78 drugs have 100% female life-threatening signals
- Top: Risperidone (20 signals 100%F), Vincristine (16 signals 100%F)
- Sildenafil: 13 life-threatening signals, ALL female (effect=1.43)

### 2. Multi-Drug AE Landscape  
- 246 universal sex-diff AEs (affect 100+ drugs)
- 115 consistently female AEs (≥90%F): intracranial hemorrhage 97.6%F, osteonecrosis 96.5%F
- 121 consistently male AEs (≤10%F): pain of skin 0%F, acne 7.8%F
- 585 paradoxical AEs (30-70%F — direction depends on which drug)
- Effect size gradient: |LR| 0.5-1: 52.5%F → |LR| 2+: 59.4%F

### 3. Drug Repurposing & Syndrome Analysis
- 724 drugs with ≥20 signals but ≤2 known targets (target discovery candidates)
- 116 divergent target pairs (same protein target, opposite sex bias — max 100pp spread)
- Top shared-target divergence: 5-HT2A, glucocorticoid receptor, EGFR, GABA-A
- AE co-occurrence syndromes: pyrexia+rash (144 drugs), fatigue+headache (143 drugs)

### 4. Protein Network Topology
- 413 unique drug targets with sex-differential signal data
- 152 female-biased, 149 male-biased, 112 mixed targets
- KG GAP: No gene_encodes_protein bridge (ChEMBL targets → Gene names, PPI → Protein ENSP IDs)
- v4.2 must add this bridge for full network analysis

### 5. Regulatory Implications Paper
- Paper #5 drafted: 187 drugs needing sex-specific warnings
- JAMA format, ~4000 words
- 113 female-warning + 74 male-warning drugs
- Key stat: 1 in 11 drugs meets stringent warning criteria

### 6. Molecular Audit
- 57 JSON files audited
- 3 files with stale v3 numbers → ARCHIVED to archive_stale/
- 2 duplicate pairs consolidated
- 4 missing PDFs generated
- All 5 paper drafts: CLEAN

## New Figures
- fig16_divergent_targets (same target, opposite bias)
- fig17_top_signal_drugs (top 20 by count)
- fig18_ae_syndromes (co-occurrence)
- fig19_target_sex_distribution (F/M/mixed)
- fig20_severity_effect_gradient (dual panel)
- fig21_universal_ae_spectrum (30 AEs)
- fig22_consistent_sex_aes (split F/M panel)

## New JSON Files
- protein_network_topology.json
- repurposing_analysis.json
- pathway_sex_enrichment.json
- severity_sex_interaction.json
- multi_drug_ae_landscape.json
- molecular_audit_wave4.json
