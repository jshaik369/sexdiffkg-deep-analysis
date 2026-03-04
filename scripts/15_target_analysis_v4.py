#!/usr/bin/env python3
"""
Target-level sex-bias analysis on v4 SexDiffKG signals.
Aggregates drug-level sex-differential signals to gene targets via ChEMBL drug-target mappings.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

base = Path('/home/jshaik369/sexdiffkg')
out_dir = base / 'results' / 'analysis'
out_dir.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. Load v4 signals
# ============================================================
print('Loading v4 signals...')
signals = pd.read_parquet(base / 'results/signals_v4/sex_differential_v4.parquet')
print(f'  Total v4 signals: {len(signals):,}')
print(f'  Direction breakdown:')
print(f'    female_higher: {(signals.direction == "female_higher").sum():,}')
print(f'    male_higher:   {(signals.direction == "male_higher").sum():,}')
print(f'  Unique drugs in signals: {signals.drug_name.nunique():,}')

# ============================================================
# 2. Load ChEMBL drug-target mappings
# ============================================================
print('\nLoading ChEMBL drug-target mappings...')
dt = pd.read_parquet(base / 'data/processed/molecular/drug_targets.parquet')
print(f'  Drug-target rows: {len(dt):,}')
print(f'  Unique drugs: {dt.drug_name.nunique():,}')
print(f'  Unique gene symbols: {dt.gene_symbol.nunique():,}')

# ============================================================
# 3. Join signals to targets via drug_name
# ============================================================
print('\nMatching signals to drug targets...')

# Normalize drug names for matching (uppercase both sides)
signals['drug_name_upper'] = signals['drug_name'].str.upper().str.strip()
dt['drug_name_upper'] = dt['drug_name'].str.upper().str.strip()

# Build drug_name -> gene_symbol mapping (one drug can have multiple targets)
drug_to_genes = dt.groupby('drug_name_upper')['gene_symbol'].apply(set).to_dict()

# Also build drug_name -> ensembl mapping for richer output
drug_to_ensembl = {}
for _, row in dt.iterrows():
    key = row['drug_name_upper']
    if key not in drug_to_ensembl:
        drug_to_ensembl[key] = {}
    if pd.notna(row.get('gene_symbol')) and pd.notna(row.get('ensembl_gene_id')):
        drug_to_ensembl[key][row['gene_symbol']] = row['ensembl_gene_id']

# Match signals to gene targets
matched_count = 0
unmatched_drugs = set()
target_signals = defaultdict(lambda: {'f_drugs': set(), 'm_drugs': set(), 'all_drugs': set(),
                                       'f_signals': 0, 'm_signals': 0, 'total_signals': 0,
                                       'log_ratios': [], 'ensembl_id': None})

for _, row in signals.iterrows():
    drug_upper = row['drug_name_upper']
    genes = drug_to_genes.get(drug_upper, set())
    if not genes:
        unmatched_drugs.add(drug_upper)
        continue
    matched_count += 1
    for gene in genes:
        ts = target_signals[gene]
        ts['all_drugs'].add(drug_upper)
        ts['total_signals'] += 1
        ts['log_ratios'].append(row['log_ratio'])
        if row['direction'] == 'female_higher':
            ts['f_drugs'].add(drug_upper)
            ts['f_signals'] += 1
        else:
            ts['m_drugs'].add(drug_upper)
            ts['m_signals'] += 1
        # Store ensembl ID
        if ts['ensembl_id'] is None:
            ens_map = drug_to_ensembl.get(drug_upper, {})
            if gene in ens_map:
                ts['ensembl_id'] = ens_map[gene]

matched_drugs = signals['drug_name_upper'].nunique() - len(unmatched_drugs)
print(f'  Signals matched to targets: {matched_count:,} / {len(signals):,} ({100*matched_count/len(signals):.1f}%)')
print(f'  Drugs matched: {matched_drugs:,} / {signals.drug_name_upper.nunique():,}')
print(f'  Gene targets touched: {len(target_signals):,}')

# ============================================================
# 4. Compute sex-bias score per target
# ============================================================
print('\nComputing sex-bias scores...')

rows = []
for gene, ts in target_signals.items():
    n_drugs = len(ts['all_drugs'])
    nf = len(ts['f_drugs'])
    nm = len(ts['m_drugs'])
    # Sex-bias score: fraction of F-higher minus fraction of M-higher (range [-1, +1])
    # +1 = all drug-signals are female-higher, -1 = all male-higher
    sex_bias_score = (nf - nm) / max(n_drugs, 1)
    mean_log_ratio = np.mean(ts['log_ratios']) if ts['log_ratios'] else 0.0
    median_log_ratio = np.median(ts['log_ratios']) if ts['log_ratios'] else 0.0
    
    rows.append({
        'gene_symbol': gene,
        'ensembl_id': ts['ensembl_id'],
        'total_drugs': n_drugs,
        'female_biased_drugs': nf,
        'male_biased_drugs': nm,
        'total_signals': ts['total_signals'],
        'f_signals': ts['f_signals'],
        'm_signals': ts['m_signals'],
        'female_fraction': round(nf / max(n_drugs, 1), 4),
        'sex_bias_score': round(sex_bias_score, 4),
        'mean_log_ratio': round(mean_log_ratio, 4),
        'median_log_ratio': round(median_log_ratio, 4),
    })

target_df = pd.DataFrame(rows)
target_df = target_df.sort_values('sex_bias_score', key=abs, ascending=False)

print(f'  Total gene targets: {len(target_df):,}')

# ============================================================
# 5. Filter targets with significant sex-bias
# ============================================================
# Criteria: |sex_bias_score| >= 0.5 AND total_drugs >= 5
sig_targets = target_df[(target_df['sex_bias_score'].abs() >= 0.5) & (target_df['total_drugs'] >= 5)]
print(f'  Significant targets (|score|>=0.5, drugs>=5): {len(sig_targets):,}')

# Also compute with looser threshold for comparison
sig_targets_loose = target_df[(target_df['sex_bias_score'].abs() >= 0.3) & (target_df['total_drugs'] >= 3)]
print(f'  Targets (|score|>=0.3, drugs>=3): {len(sig_targets_loose):,}')

# And the v3-comparable threshold (score != 0, drugs >= 2)
sig_targets_v3_compat = target_df[(target_df['sex_bias_score'].abs() > 0) & (target_df['total_drugs'] >= 2)]
print(f'  Targets v3-comparable (|score|>0, drugs>=2): {len(sig_targets_v3_compat):,}')

# ============================================================
# 6. Identify key findings
# ============================================================
print('\n' + '='*60)
print('KEY FINDINGS')
print('='*60)

# Exclusively F-biased (score = +1.0)
exclusively_f = target_df[(target_df['sex_bias_score'] == 1.0) & (target_df['total_drugs'] >= 2)]
print(f'\nExclusively female-biased (score=+1.0, drugs>=2): {len(exclusively_f)}')
for _, r in exclusively_f.sort_values('total_drugs', ascending=False).head(20).iterrows():
    print(f'  {r.gene_symbol:20s} drugs={r.total_drugs:3d}  signals={r.total_signals:5d}')

# Exclusively M-biased (score = -1.0)
exclusively_m = target_df[(target_df['sex_bias_score'] == -1.0) & (target_df['total_drugs'] >= 2)]
print(f'\nExclusively male-biased (score=-1.0, drugs>=2): {len(exclusively_m)}')
for _, r in exclusively_m.sort_values('total_drugs', ascending=False).head(20).iterrows():
    print(f'  {r.gene_symbol:20s} drugs={r.total_drugs:3d}  signals={r.total_signals:5d}')

# Top female-biased (by score, then by drugs)
print(f'\nTop 20 female-biased targets (score > 0):')
top_f = target_df[target_df['sex_bias_score'] > 0].sort_values(['sex_bias_score', 'total_drugs'], ascending=[False, False]).head(20)
for _, r in top_f.iterrows():
    print(f'  {r.gene_symbol:20s} score={r.sex_bias_score:+.4f}  drugs={r.total_drugs:3d}  F={r.female_biased_drugs:3d}  M={r.male_biased_drugs:3d}  mean_lr={r.mean_log_ratio:+.3f}')

# Top male-biased (by score, then by drugs)
print(f'\nTop 20 male-biased targets (score < 0):')
top_m = target_df[target_df['sex_bias_score'] < 0].sort_values(['sex_bias_score', 'total_drugs'], ascending=[True, False]).head(20)
for _, r in top_m.iterrows():
    print(f'  {r.gene_symbol:20s} score={r.sex_bias_score:+.4f}  drugs={r.total_drugs:3d}  F={r.female_biased_drugs:3d}  M={r.male_biased_drugs:3d}  mean_lr={r.mean_log_ratio:+.3f}')

# ============================================================
# 7. Check specific pharmacological targets of interest
# ============================================================
print('\n' + '='*60)
print('PHARMACOLOGICAL TARGETS OF INTEREST')
print('='*60)

targets_of_interest = [
    'HDAC1', 'HDAC2', 'HDAC3', 'HDAC6',  # Histone deacetylases
    'ESR1', 'ESR2',                          # Estrogen receptors
    'ITGA2B', 'ITGB3',                       # Platelet integrins
    'JAK1', 'JAK2', 'JAK3',                  # Janus kinases
    'F8', 'F9', 'F10', 'F2',                 # Coagulation factors
    'CHRNA1', 'CHRNA2', 'CHRNA3', 'CHRNA4', 'CHRNA5', 'CHRNA7',  # Nicotinic AChR alpha
    'CHRNB1', 'CHRNB2', 'CHRNB4',            # Nicotinic AChR beta
    'CHRNE',                                   # Nicotinic AChR epsilon
    'SCNN1A', 'SCNN1B', 'SCNN1G',            # Epithelial Na channels
]

for gene in targets_of_interest:
    match = target_df[target_df['gene_symbol'] == gene]
    if len(match) > 0:
        r = match.iloc[0]
        direction = 'FEMALE-biased' if r.sex_bias_score > 0 else 'MALE-biased' if r.sex_bias_score < 0 else 'NEUTRAL'
        print(f'  {gene:10s}  score={r.sex_bias_score:+.4f}  drugs={r.total_drugs:3d}  F={r.female_biased_drugs:3d}  M={r.male_biased_drugs:3d}  signals={r.total_signals:5d}  mean_lr={r.mean_log_ratio:+.4f}  [{direction}]')
    else:
        print(f'  {gene:10s}  NOT FOUND in v4 target analysis')

# ============================================================
# 8. Save results
# ============================================================
print('\n' + '='*60)
print('SAVING RESULTS')
print('='*60)

# Save full target table as TSV
target_df.to_csv(out_dir / 'v4_target_sex_bias.tsv', sep='\t', index=False)
print(f'Saved: {out_dir}/v4_target_sex_bias.tsv ({len(target_df)} rows)')

# Save significant targets
sig_targets.to_csv(out_dir / 'v4_target_sex_bias_significant.tsv', sep='\t', index=False)
print(f'Saved: {out_dir}/v4_target_sex_bias_significant.tsv ({len(sig_targets)} rows)')

# Build JSON summary
f_biased = target_df[target_df['sex_bias_score'] > 0]
m_biased = target_df[target_df['sex_bias_score'] < 0]
neutral = target_df[target_df['sex_bias_score'] == 0]

result_json = {
    'version': 'v4',
    'date': '2026-03-03',
    'input': {
        'signals_file': str(base / 'results/signals_v4/sex_differential_v4.parquet'),
        'drug_targets_file': str(base / 'data/processed/molecular/drug_targets.parquet'),
        'total_v4_signals': int(len(signals)),
        'signals_female_higher': int((signals.direction == 'female_higher').sum()),
        'signals_male_higher': int((signals.direction == 'male_higher').sum()),
        'unique_drugs_in_signals': int(signals.drug_name.nunique()),
    },
    'matching': {
        'signals_matched_to_targets': int(matched_count),
        'drugs_matched': int(matched_drugs),
        'drugs_unmatched': int(len(unmatched_drugs)),
        'match_rate_pct': round(100 * matched_count / len(signals), 2),
    },
    'target_counts': {
        'total_gene_targets': int(len(target_df)),
        'female_biased_targets': int(len(f_biased)),
        'male_biased_targets': int(len(m_biased)),
        'neutral_targets': int(len(neutral)),
        'significant_strict': {
            'criteria': '|score|>=0.5 AND drugs>=5',
            'count': int(len(sig_targets)),
        },
        'significant_loose': {
            'criteria': '|score|>=0.3 AND drugs>=3',
            'count': int(len(sig_targets_loose)),
        },
        'v3_comparable': {
            'criteria': '|score|>0 AND drugs>=2',
            'count': int(len(sig_targets_v3_compat)),
            'v3_count': 429,
        },
        'exclusively_female_biased': {
            'criteria': 'score=+1.0 AND drugs>=2',
            'count': int(len(exclusively_f)),
        },
        'exclusively_male_biased': {
            'criteria': 'score=-1.0 AND drugs>=2',
            'count': int(len(exclusively_m)),
        },
    },
    'top_female_biased': top_f[['gene_symbol', 'sex_bias_score', 'total_drugs', 'female_biased_drugs', 'male_biased_drugs', 'mean_log_ratio']].to_dict('records'),
    'top_male_biased': top_m[['gene_symbol', 'sex_bias_score', 'total_drugs', 'female_biased_drugs', 'male_biased_drugs', 'mean_log_ratio']].to_dict('records'),
    'pharmacological_targets': {},
}

# Add pharmacological targets of interest
for gene in targets_of_interest:
    match = target_df[target_df['gene_symbol'] == gene]
    if len(match) > 0:
        r = match.iloc[0]
        result_json['pharmacological_targets'][gene] = {
            'sex_bias_score': float(r.sex_bias_score),
            'total_drugs': int(r.total_drugs),
            'female_biased_drugs': int(r.female_biased_drugs),
            'male_biased_drugs': int(r.male_biased_drugs),
            'total_signals': int(r.total_signals),
            'mean_log_ratio': float(r.mean_log_ratio),
            'direction': 'female_biased' if r.sex_bias_score > 0 else 'male_biased' if r.sex_bias_score < 0 else 'neutral',
        }

json_path = out_dir / 'v4_target_analysis.json'
with open(json_path, 'w') as f:
    json.dump(result_json, f, indent=2)
print(f'Saved: {json_path}')

# ============================================================
# FINAL SUMMARY
# ============================================================
print('\n' + '='*60)
print('FINAL SUMMARY')
print('='*60)
print(f'v4 signals analyzed:             {len(signals):,}')
print(f'Signals matched to gene targets: {matched_count:,} ({100*matched_count/len(signals):.1f}%)')
print(f'Total gene targets:              {len(target_df):,}')
print(f'  Female-biased:                 {len(f_biased):,}')
print(f'  Male-biased:                   {len(m_biased):,}')
print(f'  Neutral:                       {len(neutral):,}')
print(f'Significant (|score|>=0.5, n>=5): {len(sig_targets):,}')
print(f'v3-comparable (|score|>0, n>=2):  {len(sig_targets_v3_compat):,} (v3 had 429)')
print(f'Exclusively F-biased:            {len(exclusively_f):,}')
print(f'Exclusively M-biased:            {len(exclusively_m):,}')
print('='*60)
