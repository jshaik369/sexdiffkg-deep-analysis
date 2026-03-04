#!/usr/bin/env python3
"""
Temporal Trend Analysis of Sex-Differential Drug Safety Signals
================================================================
Analyzes how sex-differential adverse event reporting has changed
across FAERS quarterly data (2012Q4 - 2025Q3).

Approach:
1. Split 52 quarters into ~5 eras of roughly equal size
2. For each era, compute ROR by sex for each (drug, AE) pair
3. Track overall sex ratio trends
4. Identify signals that emerge, disappear, or reverse direction
5. Find top drugs/AEs with largest temporal shifts

Output: JSON results + summary statistics
"""

import json
import time
import warnings
import numpy as np
import pandas as pd
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings('ignore')

RESULTS_DIR = Path('/home/jshaik369/sexdiffkg/results/analysis')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = Path('/home/jshaik369/sexdiffkg/data/processed/faers_clean')

# ---- Configuration ----
MIN_REPORTS = 3          # Minimum reports for a cell in ROR
MIN_SIGNAL_COUNT = 5     # Minimum a+c for inclusion
ROR_THRESHOLD = 1.0      # Lower CI bound for signal
ERA_DEFINITIONS = {
    'Era1_2013-2015': ['2012Q4','2013Q1','2013Q2','2013Q3','2013Q4','2014Q1','2014Q2','2014Q3','2014Q4','2015Q1','2015Q2','2015Q3','2015Q4'],
    'Era2_2016-2017': ['2016Q1','2016Q2','2016Q3','2016Q4','2017Q1','2017Q2','2017Q3','2017Q4'],
    'Era3_2018-2019': ['2018Q1','2018Q2','2018Q3','2018Q4','2019Q1','2019Q2','2019Q3','2019Q4'],
    'Era4_2020-2022': ['2020Q1','2020Q2','2020Q3','2020Q4','2021Q1','2021Q2','2021Q3','2021Q4','2022Q1','2022Q2','2022Q3','2022Q4'],
    'Era5_2023-2025': ['2023Q1','2023Q2','2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4','2025Q1','2025Q2','2025Q3'],
}

def compute_ror(a, b, c, d):
    """Compute Reporting Odds Ratio with 95% CI."""
    if a == 0 or b == 0 or c == 0 or d == 0:
        return np.nan, np.nan, np.nan
    ror = (a * d) / (b * c)
    log_se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    lower = np.exp(np.log(ror) - 1.96 * log_se)
    upper = np.exp(np.log(ror) + 1.96 * log_se)
    return ror, lower, upper


def main():
    t0 = time.time()
    print("=" * 70)
    print("TEMPORAL TREND ANALYSIS: Sex-Differential Drug Safety Signals")
    print("=" * 70)

    # ---- Load data ----
    print("\n[1/6] Loading data...")

    demo = pd.read_parquet(DATA_DIR / 'demo.parquet', columns=['primaryid', 'sex', 'quarter'])
    demo = demo[demo['sex'].isin(['F', 'M'])].copy()
    print(f"  Demo: {len(demo):,} reports (F={sum(demo.sex=='F'):,}, M={sum(demo.sex=='M'):,})")

    drug = pd.read_parquet(DATA_DIR / 'drug_normalized_v4.parquet',
                           columns=['primaryid', 'drugname_normalized', 'role_cod'])
    # Keep primary suspect + secondary suspect drugs
    drug = drug[drug['role_cod'].isin(['PS', 'SS'])].copy()
    drug = drug[drug['drugname_normalized'].notna() & (drug['drugname_normalized'] != 'UNSPECIFIED')]
    drug = drug[['primaryid', 'drugname_normalized']].drop_duplicates()
    drug.rename(columns={'drugname_normalized': 'drug'}, inplace=True)
    print(f"  Drug records (PS/SS, normalized): {len(drug):,}")

    reac = pd.read_parquet(DATA_DIR / 'reac.parquet', columns=['primaryid', 'pt'])
    reac = reac[reac['pt'].notna()].drop_duplicates()
    print(f"  Reaction records: {len(reac):,}")

    # ---- Section 2: Overall quarterly trends ----
    print("\n[2/6] Computing quarterly sex ratio trends...")

    quarterly_sex = demo.groupby(['quarter', 'sex']).size().unstack(fill_value=0)
    quarterly_sex.columns = ['F', 'M']
    quarterly_sex['total'] = quarterly_sex['F'] + quarterly_sex['M']
    quarterly_sex['pct_female'] = (quarterly_sex['F'] / quarterly_sex['total'] * 100).round(2)
    quarterly_sex['fm_ratio'] = (quarterly_sex['F'] / quarterly_sex['M']).round(4)
    quarterly_sex = quarterly_sex.sort_index()

    print(f"  Quarters: {len(quarterly_sex)}")
    print(f"  Female % range: {quarterly_sex['pct_female'].min():.1f}% - {quarterly_sex['pct_female'].max():.1f}%")
    print(f"  Overall F/M ratio: {quarterly_sex['F'].sum()/quarterly_sex['M'].sum():.4f}")

    quarterly_trends = []
    for q, row in quarterly_sex.iterrows():
        quarterly_trends.append({
            'quarter': q,
            'female': int(row['F']),
            'male': int(row['M']),
            'total': int(row['total']),
            'pct_female': float(row['pct_female']),
            'fm_ratio': float(row['fm_ratio'])
        })

    # ---- Section 3: Era-level signal computation ----
    print("\n[3/6] Computing ROR signals by era (this is the heavy part)...")

    # Merge demo with drug and reaction
    print("  Merging demo + drug...")
    demo_drug = demo.merge(drug, on='primaryid', how='inner')
    print(f"  Demo-drug pairs: {len(demo_drug):,}")

    print("  Merging with reactions...")
    triplets = demo_drug.merge(reac, on='primaryid', how='inner')
    print(f"  Triplets (report-drug-reaction): {len(triplets):,}")

    # Free memory
    del demo_drug, drug, reac
    import gc; gc.collect()

    # Map quarters to eras
    quarter_to_era = {}
    for era_name, quarters in ERA_DEFINITIONS.items():
        for q in quarters:
            quarter_to_era[q] = era_name

    triplets['era'] = triplets['quarter'].map(quarter_to_era)
    triplets = triplets[triplets['era'].notna()].copy()
    print(f"  Triplets with era mapping: {len(triplets):,}")

    # Compute per-era sex-specific counts
    era_signals = {}
    era_summaries = {}

    for era_name in sorted(ERA_DEFINITIONS.keys()):
        print(f"\n  Processing {era_name}...")
        era_data = triplets[triplets['era'] == era_name]

        era_total_f = era_data[era_data['sex'] == 'F']['primaryid'].nunique()
        era_total_m = era_data[era_data['sex'] == 'M']['primaryid'].nunique()

        # Count (drug, pt, sex) combinations
        counts = era_data.groupby(['drug', 'pt', 'sex'])['primaryid'].nunique().reset_index()
        counts.rename(columns={'primaryid': 'count'}, inplace=True)

        # Pivot to get F and M counts side by side
        pivot = counts.pivot_table(index=['drug', 'pt'], columns='sex', values='count', fill_value=0)
        if 'F' not in pivot.columns:
            pivot['F'] = 0
        if 'M' not in pivot.columns:
            pivot['M'] = 0
        pivot = pivot.reset_index()

        # Total reports for each drug across all AEs, by sex
        drug_total_f = era_data[era_data['sex'] == 'F'].groupby('drug')['primaryid'].nunique()
        drug_total_m = era_data[era_data['sex'] == 'M'].groupby('drug')['primaryid'].nunique()

        # Total reports for each PT across all drugs, by sex
        pt_total_f = era_data[era_data['sex'] == 'F'].groupby('pt')['primaryid'].nunique()
        pt_total_m = era_data[era_data['sex'] == 'M'].groupby('pt')['primaryid'].nunique()

        # For ROR: a = drug+AE+sex, b = drug+notAE+sex, c = notDrug+AE+sex, d = notDrug+notAE+sex
        signals_list = []

        for _, row in pivot.iterrows():
            drug_name = row['drug']
            pt_name = row['pt']

            for sex in ['F', 'M']:
                a = int(row[sex])
                if a < MIN_REPORTS:
                    continue

                total_sex = era_total_f if sex == 'F' else era_total_m
                b_drug = drug_total_f.get(drug_name, 0) if sex == 'F' else drug_total_m.get(drug_name, 0)
                c_pt = pt_total_f.get(pt_name, 0) if sex == 'F' else pt_total_m.get(pt_name, 0)

                b = b_drug - a
                c = c_pt - a
                d = total_sex - a - b - c

                if b <= 0 or c <= 0 or d <= 0:
                    continue

                ror, lower, upper = compute_ror(a, b, c, d)
                if np.isnan(ror):
                    continue

                signals_list.append({
                    'drug': drug_name,
                    'pt': pt_name,
                    'sex': sex,
                    'a': a, 'b': b, 'c': c, 'd': d,
                    'ror': ror, 'ror_lower': lower, 'ror_upper': upper,
                    'signal': lower > ROR_THRESHOLD
                })

        signals_df = pd.DataFrame(signals_list)
        era_signals[era_name] = signals_df

        n_signals = signals_df['signal'].sum() if len(signals_df) > 0 else 0
        n_f_signals = signals_df[(signals_df['sex']=='F') & (signals_df['signal'])].shape[0] if len(signals_df) > 0 else 0
        n_m_signals = signals_df[(signals_df['sex']=='M') & (signals_df['signal'])].shape[0] if len(signals_df) > 0 else 0

        era_summaries[era_name] = {
            'reports_female': int(era_total_f),
            'reports_male': int(era_total_m),
            'total_pairs_evaluated': len(signals_df),
            'total_signals': int(n_signals),
            'female_signals': int(n_f_signals),
            'male_signals': int(n_m_signals),
            'signal_fm_ratio': round(n_f_signals / n_m_signals, 4) if n_m_signals > 0 else None,
        }

        print(f"    Reports: F={era_total_f:,}, M={era_total_m:,}")
        print(f"    Pairs evaluated: {len(signals_df):,}")
        print(f"    Signals: {n_signals:,} (F={n_f_signals:,}, M={n_m_signals:,})")

    # ---- Section 4: Sex-differential signal comparison across eras ----
    print("\n[4/6] Computing sex-differential trends across eras...")

    era_names_sorted = sorted(ERA_DEFINITIONS.keys())
    first_era = era_names_sorted[0]
    last_era = era_names_sorted[-1]

    # Build sex-differential scores per era
    sex_diff_by_era = {}
    for era_name, signals_df in era_signals.items():
        if len(signals_df) == 0:
            continue

        # Get signal pairs where both F and M exist
        f_signals = signals_df[signals_df['sex'] == 'F'][['drug', 'pt', 'ror', 'ror_lower', 'a', 'signal']].copy()
        f_signals.rename(columns={'ror': 'ror_f', 'ror_lower': 'lower_f', 'a': 'a_f', 'signal': 'signal_f'}, inplace=True)

        m_signals = signals_df[signals_df['sex'] == 'M'][['drug', 'pt', 'ror', 'ror_lower', 'a', 'signal']].copy()
        m_signals.rename(columns={'ror': 'ror_m', 'ror_lower': 'lower_m', 'a': 'a_m', 'signal': 'signal_m'}, inplace=True)

        merged = f_signals.merge(m_signals, on=['drug', 'pt'], how='inner')
        merged['log_ror_ratio'] = np.log2(merged['ror_f'] / merged['ror_m'])
        merged['min_reports'] = merged[['a_f', 'a_m']].min(axis=1)

        sex_diff_by_era[era_name] = merged

    # ---- Section 5: Identify trending, emerging, and reversing signals ----
    print("\n[5/6] Identifying temporal signal patterns...")

    # Compare first era vs last era for signals present in both
    if first_era in sex_diff_by_era and last_era in sex_diff_by_era:
        early = sex_diff_by_era[first_era][['drug', 'pt', 'log_ror_ratio', 'a_f', 'a_m']].copy()
        early.rename(columns={'log_ror_ratio': 'ratio_early', 'a_f': 'af_early', 'a_m': 'am_early'}, inplace=True)

        late = sex_diff_by_era[last_era][['drug', 'pt', 'log_ror_ratio', 'a_f', 'a_m']].copy()
        late.rename(columns={'log_ror_ratio': 'ratio_late', 'a_f': 'af_late', 'a_m': 'am_late'}, inplace=True)

        comparison = early.merge(late, on=['drug', 'pt'], how='inner')
        comparison['shift'] = comparison['ratio_late'] - comparison['ratio_early']
        comparison['direction_early'] = np.where(comparison['ratio_early'] > 0, 'female_biased', 'male_biased')
        comparison['direction_late'] = np.where(comparison['ratio_late'] > 0, 'female_biased', 'male_biased')
        comparison['reversed'] = comparison['direction_early'] != comparison['direction_late']

        # Filter to signals with enough reports
        comparison_strong = comparison[
            (comparison['af_early'] >= 10) & (comparison['am_early'] >= 10) &
            (comparison['af_late'] >= 10) & (comparison['am_late'] >= 10)
        ].copy()

        # Biggest shifts toward female bias
        top_toward_female = comparison_strong.nlargest(20, 'shift')[
            ['drug', 'pt', 'ratio_early', 'ratio_late', 'shift', 'direction_early', 'direction_late', 'reversed',
             'af_early', 'am_early', 'af_late', 'am_late']
        ]

        # Biggest shifts toward male bias
        top_toward_male = comparison_strong.nsmallest(20, 'shift')[
            ['drug', 'pt', 'ratio_early', 'ratio_late', 'shift', 'direction_early', 'direction_late', 'reversed',
             'af_early', 'am_early', 'af_late', 'am_late']
        ]

        # Reversed signals
        reversed_signals = comparison_strong[comparison_strong['reversed']].copy()
        reversed_signals['abs_shift'] = reversed_signals['shift'].abs()
        reversed_signals = reversed_signals.nlargest(30, 'abs_shift')

        n_compared = len(comparison_strong)
        n_reversed = int(comparison_strong['reversed'].sum())

        print(f"  Pairs compared (first vs last era, >=10 reports each): {n_compared:,}")
        print(f"  Reversed direction: {n_reversed:,} ({n_reversed/n_compared*100:.1f}%)")
        print(f"  Mean absolute shift: {comparison_strong['shift'].abs().mean():.4f}")
    else:
        comparison_strong = pd.DataFrame()
        top_toward_female = pd.DataFrame()
        top_toward_male = pd.DataFrame()
        reversed_signals = pd.DataFrame()
        n_compared = 0
        n_reversed = 0

    # ---- Section 6: Drug-class and AE-class level trends ----
    print("\n[6/6] Computing aggregate temporal trends...")

    # Track per-era: median log_ror_ratio, % female-biased, distribution stats
    temporal_aggregate = []
    for era_name in era_names_sorted:
        if era_name not in sex_diff_by_era:
            continue
        df = sex_diff_by_era[era_name]
        # Filter to pairs with decent counts
        strong = df[(df['a_f'] >= 5) & (df['a_m'] >= 5)].copy()

        n_pairs = len(strong)
        if n_pairs == 0:
            continue

        pct_f_biased = (strong['log_ror_ratio'] > 0).sum() / n_pairs * 100
        pct_m_biased = (strong['log_ror_ratio'] < 0).sum() / n_pairs * 100

        temporal_aggregate.append({
            'era': era_name,
            'n_pairs': int(n_pairs),
            'median_log2_ror_ratio': round(float(strong['log_ror_ratio'].median()), 4),
            'mean_log2_ror_ratio': round(float(strong['log_ror_ratio'].mean()), 4),
            'std_log2_ror_ratio': round(float(strong['log_ror_ratio'].std()), 4),
            'pct_female_biased': round(pct_f_biased, 2),
            'pct_male_biased': round(pct_m_biased, 2),
            'q25_log2_ratio': round(float(strong['log_ror_ratio'].quantile(0.25)), 4),
            'q75_log2_ratio': round(float(strong['log_ror_ratio'].quantile(0.75)), 4),
        })

    # ---- Top AEs with strongest sex-differential trends ----
    ae_trends = {}
    for era_name in era_names_sorted:
        if era_name not in sex_diff_by_era:
            continue
        df = sex_diff_by_era[era_name]
        strong = df[(df['a_f'] >= 5) & (df['a_m'] >= 5)]
        ae_medians = strong.groupby('pt')['log_ror_ratio'].median()
        for pt, val in ae_medians.items():
            if pt not in ae_trends:
                ae_trends[pt] = {}
            ae_trends[pt][era_name] = round(float(val), 4)

    # Find AEs present in all 5 eras with consistent female or male bias
    consistent_ae = []
    for pt, era_vals in ae_trends.items():
        if len(era_vals) == 5:
            vals = [era_vals[e] for e in era_names_sorted]
            trend = vals[-1] - vals[0]
            consistent_ae.append({
                'pt': pt,
                'values_by_era': era_vals,
                'trend_shift': round(trend, 4),
                'mean_ratio': round(np.mean(vals), 4),
                'all_female_biased': all(v > 0 for v in vals),
                'all_male_biased': all(v < 0 for v in vals),
            })

    consistent_ae.sort(key=lambda x: abs(x['trend_shift']), reverse=True)

    # ---- Top drugs with strongest temporal shifts ----
    drug_trends = {}
    for era_name in era_names_sorted:
        if era_name not in sex_diff_by_era:
            continue
        df = sex_diff_by_era[era_name]
        strong = df[(df['a_f'] >= 10) & (df['a_m'] >= 10)]
        drug_medians = strong.groupby('drug')['log_ror_ratio'].agg(['median', 'count'])
        for drug_name, row in drug_medians.iterrows():
            if drug_name not in drug_trends:
                drug_trends[drug_name] = {}
            drug_trends[drug_name][era_name] = {
                'median_ratio': round(float(row['median']), 4),
                'n_pairs': int(row['count'])
            }

    # Drugs present in all 5 eras
    persistent_drugs = []
    for drug_name, era_vals in drug_trends.items():
        if len(era_vals) == 5:
            vals = [era_vals[e]['median_ratio'] for e in era_names_sorted]
            counts = [era_vals[e]['n_pairs'] for e in era_names_sorted]
            trend = vals[-1] - vals[0]
            persistent_drugs.append({
                'drug': drug_name,
                'values_by_era': {e: era_vals[e] for e in era_names_sorted},
                'trend_shift': round(trend, 4),
                'mean_ratio': round(np.mean(vals), 4),
                'total_pairs': sum(counts),
            })

    persistent_drugs.sort(key=lambda x: abs(x['trend_shift']), reverse=True)

    # ---- Compile final results ----
    runtime = time.time() - t0

    results = {
        'analysis': 'Temporal Trend Analysis of Sex-Differential Drug Safety Signals',
        'data': {
            'source': 'FAERS 2012Q4-2025Q3 (deduplicated)',
            'total_reports': int(demo['primaryid'].nunique()),
            'female_reports': int((demo['sex']=='F').sum()),
            'male_reports': int((demo['sex']=='M').sum()),
            'quarters': 52,
            'eras': 5,
        },
        'quarterly_reporting_trends': quarterly_trends,
        'era_signal_summaries': era_summaries,
        'temporal_aggregate_trends': temporal_aggregate,
        'first_vs_last_era_comparison': {
            'first_era': first_era,
            'last_era': last_era,
            'pairs_compared': n_compared,
            'reversed_direction': int(n_reversed),
            'reversal_pct': round(n_reversed/n_compared*100, 2) if n_compared > 0 else None,
            'mean_absolute_shift': round(float(comparison_strong['shift'].abs().mean()), 4) if len(comparison_strong) > 0 else None,
        },
        'top_20_shifts_toward_female': top_toward_female.to_dict('records') if len(top_toward_female) > 0 else [],
        'top_20_shifts_toward_male': top_toward_male.to_dict('records') if len(top_toward_male) > 0 else [],
        'top_30_reversed_signals': reversed_signals[
            ['drug', 'pt', 'ratio_early', 'ratio_late', 'shift', 'direction_early', 'direction_late',
             'af_early', 'am_early', 'af_late', 'am_late']
        ].to_dict('records') if len(reversed_signals) > 0 else [],
        'top_50_ae_temporal_trends': consistent_ae[:50],
        'top_50_drug_temporal_trends': persistent_drugs[:50],
        'consistently_female_biased_aes': [x for x in consistent_ae if x['all_female_biased']][:30],
        'consistently_male_biased_aes': [x for x in consistent_ae if x['all_male_biased']][:30],
        'runtime_seconds': round(runtime, 1),
    }

    # Save results
    output_path = RESULTS_DIR / 'temporal_trend_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"RESULTS SAVED: {output_path}")
    print(f"Runtime: {runtime:.1f}s")
    print(f"{'='*70}")

    # Print key findings
    print("\n" + "="*70)
    print("KEY FINDINGS SUMMARY")
    print("="*70)

    print("\n--- Quarterly F/M Reporting Ratio Trend ---")
    early_qs = quarterly_trends[:6]
    late_qs = quarterly_trends[-6:]
    early_avg = np.mean([q['fm_ratio'] for q in early_qs])
    late_avg = np.mean([q['fm_ratio'] for q in late_qs])
    print(f"  Early 6 quarters avg F/M ratio: {early_avg:.4f}")
    print(f"  Late 6 quarters avg F/M ratio: {late_avg:.4f}")
    print(f"  Change: {late_avg - early_avg:+.4f}")

    print("\n--- Era Signal Summaries ---")
    for era_name in era_names_sorted:
        s = era_summaries[era_name]
        sfmr = s.get('signal_fm_ratio', 'N/A')
        print(f"  {era_name}: {s['total_signals']:,} signals (F={s['female_signals']:,}, M={s['male_signals']:,}, F/M={sfmr})")

    print("\n--- Aggregate Sex-Bias Trends Across Eras ---")
    for item in temporal_aggregate:
        print(f"  {item['era']}: median log2(F/M ROR)={item['median_log2_ror_ratio']:+.4f}, "
              f"{item['pct_female_biased']:.1f}% female-biased, n={item['n_pairs']:,}")

    print("\n--- Top 10 Drug-AE Pairs Shifting Toward FEMALE Bias ---")
    for i, row in enumerate(results['top_20_shifts_toward_female'][:10]):
        print(f"  {i+1}. {row['drug']} + {row['pt']}: shift={row['shift']:+.3f} "
              f"({row['direction_early']}->{row['direction_late']})")

    print("\n--- Top 10 Drug-AE Pairs Shifting Toward MALE Bias ---")
    for i, row in enumerate(results['top_20_shifts_toward_male'][:10]):
        print(f"  {i+1}. {row['drug']} + {row['pt']}: shift={row['shift']:+.3f} "
              f"({row['direction_early']}->{row['direction_late']})")

    print("\n--- Top 10 REVERSED Signals (changed sex-bias direction) ---")
    for i, row in enumerate(results['top_30_reversed_signals'][:10]):
        print(f"  {i+1}. {row['drug']} + {row['pt']}: {row['direction_early']}->{row['direction_late']} "
              f"(shift={row['shift']:+.3f})")

    print("\n--- Top 10 AEs with Largest Temporal Sex-Bias Shifts ---")
    for i, item in enumerate(consistent_ae[:10]):
        vals = [item['values_by_era'][e] for e in era_names_sorted]
        direction = "F-biased" if item['mean_ratio'] > 0 else "M-biased"
        print(f"  {i+1}. {item['pt']}: shift={item['trend_shift']:+.4f} ({direction}), "
              f"trajectory: {' -> '.join(f'{v:+.3f}' for v in vals)}")

    print("\n--- Top 10 Drugs with Largest Temporal Sex-Bias Shifts ---")
    for i, item in enumerate(persistent_drugs[:10]):
        vals = [item['values_by_era'][e]['median_ratio'] for e in era_names_sorted]
        direction = "F-biased" if item['mean_ratio'] > 0 else "M-biased"
        print(f"  {i+1}. {item['drug']}: shift={item['trend_shift']:+.4f} ({direction}), "
              f"trajectory: {' -> '.join(f'{v:+.3f}' for v in vals)}")

    n_consistently_f = len([x for x in consistent_ae if x['all_female_biased']])
    n_consistently_m = len([x for x in consistent_ae if x['all_male_biased']])
    print(f"\n--- Consistency ---")
    print(f"  AEs consistently female-biased across all 5 eras: {n_consistently_f}")
    print(f"  AEs consistently male-biased across all 5 eras: {n_consistently_m}")
    print(f"  Drugs tracked across all 5 eras: {len(persistent_drugs)}")

    print(f"\nDone in {runtime:.1f}s")

if __name__ == '__main__':
    main()
