#!/usr/bin/env python3
"""
SexDiffKG v4 - Step 15: SIDER Cross-Reference Analysis
Author: JShaik (jshaik@coevolvenetwork.com) | Date: 2026-03-04

Cross-references SIDER (drug label side effects) with SexDiffKG sex-differential
signals to quantify the gap between what labels disclose and what real-world data
shows about sex differences in adverse drug reactions.

SIDER 4.1 format (meddra_all_se.tsv):
  col0: flat CID    col1: stereo CID    col2: UMLS CUI original
  col3: MedDRA type (PT/LLT)           col4: UMLS CUI mapped    col5: SE name

SexDiffKG signals (sex_differential.parquet):
  drug_name, pt, ror_male, a_male, ror_female, a_female, log_ror_ratio, direction, min_reports
"""
import json, logging, time, re, sys
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('logs/v4_15_sider_cross_ref.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

BASE = Path.home() / 'sexdiffkg'
SIDER_DIR = BASE / 'data/raw/international/sider'
SIGNALS_FILE = BASE / 'results/signals_v2/sex_differential.parquet'
OUT_DIR = BASE / 'results/analysis'
OUT_FILE = OUT_DIR / 'sider_cross_reference_v4.json'

# Drug classes for aggregation analysis
DRUG_CLASSES = {
    'opioids': ['tramadol','oxycodone','hydrocodone','morphine','fentanyl','codeine','methadone','buprenorphine'],
    'antipsychotics': ['quetiapine','olanzapine','risperidone','aripiprazole','clozapine','haloperidol','paliperidone','ziprasidone'],
    'ssris': ['sertraline','fluoxetine','escitalopram','paroxetine','citalopram','fluvoxamine'],
    'snris': ['venlafaxine','duloxetine','desvenlafaxine','milnacipran','levomilnacipran'],
    'benzodiazepines': ['diazepam','lorazepam','alprazolam','clonazepam','midazolam','temazepam','oxazepam'],
    'ace_inhibitors': ['lisinopril','enalapril','ramipril','captopril','benazepril','fosinopril','perindopril'],
    'arbs': ['losartan','valsartan','irbesartan','candesartan','olmesartan','telmisartan'],
    'nsaids': ['ibuprofen','naproxen','diclofenac','celecoxib','meloxicam','piroxicam','indomethacin','ketoprofen'],
    'statins': ['atorvastatin','rosuvastatin','simvastatin','pravastatin','lovastatin','fluvastatin'],
    'anticoagulants': ['warfarin','rivaroxaban','apixaban','dabigatran','enoxaparin','heparin'],
    'checkpoint_inhibitors': ['pembrolizumab','nivolumab','atezolizumab','durvalumab','ipilimumab','avelumab'],
    'corticosteroids': ['prednisone','prednisolone','dexamethasone','methylprednisolone','hydrocortisone','budesonide'],
    'ppis': ['omeprazole','pantoprazole','lansoprazole','esomeprazole','rabeprazole'],
    'fluoroquinolones': ['ciprofloxacin','levofloxacin','moxifloxacin','ofloxacin','norfloxacin'],
    'beta_blockers': ['metoprolol','atenolol','propranolol','carvedilol','bisoprolol','nebivolol'],
    'calcium_channel_blockers': ['amlodipine','nifedipine','diltiazem','verapamil','felodipine'],
    'diabetes_oral': ['metformin','glipizide','glyburide','sitagliptin','pioglitazone','canagliflozin','empagliflozin','dapagliflozin'],
    'anticonvulsants': ['levetiracetam','lamotrigine','valproic acid','carbamazepine','gabapentin','pregabalin','topiramate','phenytoin'],
    'hormonal_contraceptives': ['ethinyl estradiol','levonorgestrel','norethindrone','desogestrel','etonogestrel','drospirenone'],
    'thyroid': ['levothyroxine','liothyronine','methimazole','propylthiouracil'],
}

# Thresholds
STRONG_LRR = 1.0     # |log_ror_ratio| >= 1.0 => 2.7x difference between sexes
MODERATE_LRR = 0.5   # |log_ror_ratio| >= 0.5 => 1.65x difference
MIN_REPORTS_ROBUST = 50  # min reports for robust signals


def normalize_name(name):
    """Normalize drug/AE name for matching."""
    if not name or not isinstance(name, str):
        return ''
    s = name.strip().lower()
    # Remove common salt forms
    for suffix in [' hydrochloride', ' hcl', ' sodium', ' potassium', ' calcium',
                   ' mesylate', ' maleate', ' fumarate', ' tartrate', ' sulfate',
                   ' acetate', ' succinate', ' besylate', ' citrate', ' phosphate',
                   ' bromide', ' chloride', ' nitrate', ' oxide']:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def normalize_ae(name):
    """Normalize adverse event name for matching."""
    if not name or not isinstance(name, str):
        return ''
    s = name.strip().lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def load_sider():
    """Load SIDER drug names and side effects."""
    logger.info("Loading SIDER data...")

    # Load drug names
    drug_names = {}
    dn_file = SIDER_DIR / 'drug_names.tsv'
    with open(dn_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                cid = parts[0]
                name = parts[1]
                drug_names[cid] = name

    logger.info(f"  Loaded {len(drug_names)} SIDER drug name mappings")

    # Load side effects - only PT level (preferred terms), not LLT (lowest level terms)
    se_file = SIDER_DIR / 'meddra_all_se.tsv'
    se_data = []
    with open(se_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 6:
                flat_cid = parts[0]
                meddra_type = parts[3]
                se_name = parts[5]
                if meddra_type == 'PT':
                    se_data.append({
                        'cid': flat_cid,
                        'se_name': se_name
                    })

    se_df = pd.DataFrame(se_data)
    logger.info(f"  Loaded {len(se_df)} SIDER side effects (PT level)")
    logger.info(f"  Covering {se_df['cid'].nunique()} unique drugs, {se_df['se_name'].nunique()} unique SEs")

    # Map CID to drug name
    se_df['drug_name'] = se_df['cid'].map(drug_names)
    mapped = se_df['drug_name'].notna().sum()
    logger.info(f"  {mapped}/{len(se_df)} SE records have mapped drug names ({100*mapped/len(se_df):.1f}%)")

    # Load indications (7 cols: CID, UMLS, method, concept, MedDRA_type, UMLS_mapped, indication)
    ind_file = SIDER_DIR / 'meddra_all_indications.tsv'
    ind_data = []
    with open(ind_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                flat_cid = parts[0]
                meddra_type = parts[4]  # col4 is MedDRA type (PT/LLT)
                ind_name = parts[6]     # col6 is indication name
                if meddra_type == 'PT':
                    ind_data.append({
                        'cid': flat_cid,
                        'indication': ind_name
                    })
    if ind_data:
        ind_df = pd.DataFrame(ind_data)
        ind_df['drug_name'] = ind_df['cid'].map(drug_names)
    else:
        ind_df = pd.DataFrame(columns=['cid', 'indication', 'drug_name'])
    logger.info(f"  Loaded {len(ind_df)} SIDER indications (PT level)")

    return drug_names, se_df, ind_df


def load_sexdiffkg_signals():
    """Load SexDiffKG sex-differential signals."""
    logger.info("Loading SexDiffKG sex-differential signals...")
    df = pd.read_parquet(SIGNALS_FILE)
    logger.info(f"  Loaded {len(df)} signals ({df['drug_name'].nunique()} drugs, {df['pt'].nunique()} PTs)")
    logger.info(f"  Direction: {df['direction'].value_counts().to_dict()}")
    return df


def build_matching_indices(sider_se_df, signals_df):
    """Build normalized name indices for fuzzy matching."""
    logger.info("Building name matching indices...")

    # Normalize SIDER drug names
    sider_drugs = sider_se_df['drug_name'].dropna().unique()
    sider_drug_norm = {}
    for d in sider_drugs:
        norm = normalize_name(d)
        if norm:
            sider_drug_norm[norm] = d

    # Normalize SexDiffKG drug names
    sdkg_drugs = signals_df['drug_name'].unique()
    sdkg_drug_norm = {}
    for d in sdkg_drugs:
        norm = normalize_name(d)
        if norm:
            if norm not in sdkg_drug_norm:
                sdkg_drug_norm[norm] = []
            sdkg_drug_norm[norm].append(d)

    # Match SIDER drugs to SexDiffKG drugs
    drug_mapping = {}  # SIDER drug name -> SexDiffKG drug name
    for norm, sider_name in sider_drug_norm.items():
        if norm in sdkg_drug_norm:
            drug_mapping[sider_name] = sdkg_drug_norm[norm][0]

    logger.info(f"  Matched {len(drug_mapping)}/{len(sider_drugs)} SIDER drugs to SexDiffKG ({100*len(drug_mapping)/len(sider_drugs):.1f}%)")

    # Build AE matching index (SIDER SE name -> SexDiffKG PT)
    sider_ses = sider_se_df['se_name'].unique()
    sdkg_pts = signals_df['pt'].unique()

    sider_ae_norm = {}
    for ae in sider_ses:
        norm = normalize_ae(ae)
        if norm:
            sider_ae_norm[norm] = ae

    sdkg_ae_norm = {}
    for pt in sdkg_pts:
        norm = normalize_ae(pt)
        if norm:
            if norm not in sdkg_ae_norm:
                sdkg_ae_norm[norm] = []
            sdkg_ae_norm[norm].append(pt)

    ae_mapping = {}  # SIDER SE name -> SexDiffKG PT
    for norm, sider_ae in sider_ae_norm.items():
        if norm in sdkg_ae_norm:
            ae_mapping[sider_ae] = sdkg_ae_norm[norm][0]

    logger.info(f"  Matched {len(ae_mapping)}/{len(sider_ses)} SIDER SEs to SexDiffKG PTs ({100*len(ae_mapping)/len(sider_ses):.1f}%)")

    return drug_mapping, ae_mapping


def cross_reference(sider_se_df, signals_df, drug_mapping, ae_mapping):
    """Cross-reference SIDER label SEs with SexDiffKG sex-differential signals."""
    logger.info("Cross-referencing SIDER with SexDiffKG...")

    # Build signal lookup: (drug_upper, pt_upper) -> signal row
    signal_lookup = {}
    for _, row in signals_df.iterrows():
        key = (row['drug_name'], row['pt'])
        signal_lookup[key] = row

    # Process each SIDER drug-SE pair
    results = []
    matched_pairs = 0
    unmatched_drug = 0
    unmatched_ae = 0
    total_pairs = 0

    seen = set()
    for _, row in sider_se_df.iterrows():
        sider_drug = row['drug_name']
        sider_se = row['se_name']

        if pd.isna(sider_drug):
            continue

        pair_key = (sider_drug, sider_se)
        if pair_key in seen:
            continue
        seen.add(pair_key)
        total_pairs += 1

        sdkg_drug = drug_mapping.get(sider_drug)
        sdkg_ae = ae_mapping.get(sider_se)

        if not sdkg_drug:
            unmatched_drug += 1
            continue
        if not sdkg_ae:
            unmatched_ae += 1
            continue

        signal_key = (sdkg_drug, sdkg_ae)
        signal = signal_lookup.get(signal_key)

        results.append({
            'sider_drug': sider_drug,
            'sider_se': sider_se,
            'sdkg_drug': sdkg_drug,
            'sdkg_pt': sdkg_ae,
            'has_signal': signal is not None,
            'log_ror_ratio': float(signal['log_ror_ratio']) if signal is not None else None,
            'direction': signal['direction'] if signal is not None else None,
            'ror_male': float(signal['ror_male']) if signal is not None else None,
            'ror_female': float(signal['ror_female']) if signal is not None else None,
            'min_reports': int(signal['min_reports']) if signal is not None else None,
        })
        if signal is not None:
            matched_pairs += 1

    logger.info(f"  Total unique SIDER drug-SE pairs: {total_pairs}")
    logger.info(f"  Pairs where both drug+SE map to SexDiffKG: {len(results)}")
    logger.info(f"  Of those, pairs WITH sex-differential signal: {matched_pairs}")
    logger.info(f"  Unmatched due to drug: {unmatched_drug}, due to SE: {unmatched_ae}")

    return pd.DataFrame(results), total_pairs, unmatched_drug, unmatched_ae


def analyze_results(xref_df, signals_df, sider_se_df, drug_mapping, ae_mapping, total_pairs, unmatched_drug, unmatched_ae):
    """Comprehensive analysis of the cross-reference results."""
    logger.info("Analyzing cross-reference results...")

    results = {}

    # --- 1. Overview stats ---
    has_signal = xref_df[xref_df['has_signal']]
    no_signal = xref_df[~xref_df['has_signal']]

    # Strong signals
    strong = has_signal[has_signal['log_ror_ratio'].abs() >= STRONG_LRR]
    moderate = has_signal[has_signal['log_ror_ratio'].abs() >= MODERATE_LRR]
    robust = has_signal[has_signal['min_reports'] >= MIN_REPORTS_ROBUST]
    robust_strong = has_signal[(has_signal['log_ror_ratio'].abs() >= STRONG_LRR) & (has_signal['min_reports'] >= MIN_REPORTS_ROBUST)]

    results['overview'] = {
        'total_sider_drug_se_pairs': total_pairs,
        'matchable_pairs': len(xref_df),
        'pairs_with_sex_diff_signal': len(has_signal),
        'pairs_without_sex_diff_signal': len(no_signal),
        'pct_with_signal': round(100 * len(has_signal) / len(xref_df), 2) if len(xref_df) > 0 else 0,
        'pairs_with_strong_signal_lrr_gte_1': len(strong),
        'pct_strong': round(100 * len(strong) / len(xref_df), 2) if len(xref_df) > 0 else 0,
        'pairs_with_moderate_signal_lrr_gte_05': len(moderate),
        'pct_moderate': round(100 * len(moderate) / len(xref_df), 2) if len(xref_df) > 0 else 0,
        'pairs_with_robust_signal_min50': len(robust),
        'pairs_strong_and_robust': len(robust_strong),
        'unmatched_drug': unmatched_drug,
        'unmatched_ae': unmatched_ae,
        'matching': {
            'sider_drugs_total': int(sider_se_df['drug_name'].dropna().nunique()),
            'sider_drugs_matched': len(drug_mapping),
            'sider_ses_total': int(sider_se_df['se_name'].nunique()),
            'sider_ses_matched': len(ae_mapping),
        }
    }
    logger.info(f"  {len(has_signal)}/{len(xref_df)} matchable pairs have sex-differential signals ({results['overview']['pct_with_signal']}%)")
    logger.info(f"  {len(strong)} strong (|LRR|>=1.0), {len(moderate)} moderate (|LRR|>=0.5)")

    # --- 2. Direction breakdown ---
    if len(has_signal) > 0:
        dir_counts = has_signal['direction'].value_counts().to_dict()
        results['direction_breakdown'] = {
            'female_higher': int(dir_counts.get('female_higher', 0)),
            'male_higher': int(dir_counts.get('male_higher', 0)),
            'pct_female_higher': round(100 * dir_counts.get('female_higher', 0) / len(has_signal), 2),
            'pct_male_higher': round(100 * dir_counts.get('male_higher', 0) / len(has_signal), 2),
        }

    # --- 3. Most sex-differential SIDER side effects ---
    # For each SIDER SE, compute mean absolute LRR across drugs
    se_stats = has_signal.groupby('sider_se').agg(
        mean_abs_lrr=('log_ror_ratio', lambda x: x.abs().mean()),
        max_abs_lrr=('log_ror_ratio', lambda x: x.abs().max()),
        n_drugs=('sider_drug', 'nunique'),
        pct_female_higher=('direction', lambda x: 100 * (x == 'female_higher').sum() / len(x)),
        n_signals=('log_ror_ratio', 'count'),
    ).reset_index()
    se_stats = se_stats.sort_values('mean_abs_lrr', ascending=False)

    # Top 30 most sex-differential SEs (min 3 drugs)
    se_multi = se_stats[se_stats['n_drugs'] >= 3].head(30)
    results['most_sex_differential_side_effects'] = []
    for _, row in se_multi.iterrows():
        results['most_sex_differential_side_effects'].append({
            'side_effect': row['sider_se'],
            'mean_abs_log_ror_ratio': round(float(row['mean_abs_lrr']), 4),
            'max_abs_log_ror_ratio': round(float(row['max_abs_lrr']), 4),
            'n_drugs_in_sider': int(row['n_drugs']),
            'n_signals': int(row['n_signals']),
            'pct_female_higher': round(float(row['pct_female_higher']), 1),
        })

    # --- 4. Side effects that are consistently female-biased (>=80% female) ---
    female_biased = se_stats[(se_stats['n_drugs'] >= 3) & (se_stats['pct_female_higher'] >= 80)].sort_values('mean_abs_lrr', ascending=False).head(20)
    results['consistently_female_biased_ses'] = []
    for _, row in female_biased.iterrows():
        results['consistently_female_biased_ses'].append({
            'side_effect': row['sider_se'],
            'mean_abs_lrr': round(float(row['mean_abs_lrr']), 4),
            'n_drugs': int(row['n_drugs']),
            'pct_female_higher': round(float(row['pct_female_higher']), 1),
        })

    # --- 5. Side effects that are consistently male-biased (>=80% male) ---
    male_biased = se_stats[(se_stats['n_drugs'] >= 3) & (se_stats['pct_female_higher'] <= 20)].sort_values('mean_abs_lrr', ascending=False).head(20)
    results['consistently_male_biased_ses'] = []
    for _, row in male_biased.iterrows():
        results['consistently_male_biased_ses'].append({
            'side_effect': row['sider_se'],
            'mean_abs_lrr': round(float(row['mean_abs_lrr']), 4),
            'n_drugs': int(row['n_drugs']),
            'pct_male_higher': round(100 - float(row['pct_female_higher']), 1),
        })

    # --- 6. Drug-level analysis ---
    drug_stats = has_signal.groupby('sider_drug').agg(
        n_ses_with_signal=('sider_se', 'nunique'),
        mean_abs_lrr=('log_ror_ratio', lambda x: x.abs().mean()),
        max_abs_lrr=('log_ror_ratio', lambda x: x.abs().max()),
        pct_female_higher=('direction', lambda x: 100 * (x == 'female_higher').sum() / len(x)),
    ).reset_index()

    # Total SIDER SEs per drug
    total_per_drug = xref_df.groupby('sider_drug')['sider_se'].nunique().reset_index()
    total_per_drug.columns = ['sider_drug', 'total_ses_matchable']
    drug_stats = drug_stats.merge(total_per_drug, on='sider_drug', how='left')
    drug_stats['pct_ses_sex_diff'] = 100 * drug_stats['n_ses_with_signal'] / drug_stats['total_ses_matchable']

    # Top 30 drugs by % of SEs that are sex-differential
    top_drugs = drug_stats[drug_stats['total_ses_matchable'] >= 10].sort_values('pct_ses_sex_diff', ascending=False).head(30)
    results['drugs_highest_sex_diff_pct'] = []
    for _, row in top_drugs.iterrows():
        results['drugs_highest_sex_diff_pct'].append({
            'drug': row['sider_drug'],
            'total_matchable_ses': int(row['total_ses_matchable']),
            'ses_with_sex_diff': int(row['n_ses_with_signal']),
            'pct_sex_differential': round(float(row['pct_ses_sex_diff']), 1),
            'mean_abs_lrr': round(float(row['mean_abs_lrr']), 4),
            'pct_female_higher': round(float(row['pct_female_higher']), 1),
        })

    # --- 7. Drug class analysis ---
    results['drug_class_analysis'] = {}
    for cls, members in DRUG_CLASSES.items():
        members_norm = {normalize_name(m) for m in members}
        # Find SIDER drugs matching this class
        class_drugs = []
        for sider_drug, sdkg_drug in drug_mapping.items():
            if normalize_name(sider_drug) in members_norm or normalize_name(sdkg_drug) in members_norm:
                class_drugs.append(sider_drug)

        if not class_drugs:
            continue

        class_xref = xref_df[xref_df['sider_drug'].isin(class_drugs)]
        class_signals = class_xref[class_xref['has_signal']]

        if len(class_xref) == 0:
            continue

        class_strong = class_signals[class_signals['log_ror_ratio'].abs() >= STRONG_LRR]

        results['drug_class_analysis'][cls] = {
            'drugs_matched': class_drugs,
            'n_drugs': len(class_drugs),
            'total_matchable_pairs': len(class_xref),
            'pairs_with_signal': len(class_signals),
            'pct_with_signal': round(100 * len(class_signals) / len(class_xref), 2) if len(class_xref) > 0 else 0,
            'pairs_with_strong_signal': len(class_strong),
            'mean_abs_lrr': round(float(class_signals['log_ror_ratio'].abs().mean()), 4) if len(class_signals) > 0 else 0,
            'pct_female_higher': round(100 * (class_signals['direction'] == 'female_higher').sum() / len(class_signals), 1) if len(class_signals) > 0 else 0,
        }
        logger.info(f"  Class {cls}: {len(class_drugs)} drugs, {len(class_signals)}/{len(class_xref)} pairs with signal ({results['drug_class_analysis'][cls]['pct_with_signal']}%)")

    # Sort classes by pct_with_signal
    sorted_classes = sorted(results['drug_class_analysis'].items(), key=lambda x: x[1]['pct_with_signal'], reverse=True)
    results['drug_class_ranking'] = [
        {'class': cls, 'pct_with_signal': data['pct_with_signal'], 'n_drugs': data['n_drugs'],
         'mean_abs_lrr': data['mean_abs_lrr'], 'pct_female_higher': data['pct_female_higher']}
        for cls, data in sorted_classes
    ]

    # --- 8. The "label gap" analysis ---
    # What fraction of sex-differential signals are NOT in SIDER (i.e., FAERS shows sex diffs that labels don't mention)
    # This is the inverse: signals that exist but are not in SIDER at all
    sider_drug_set = set(drug_mapping.values())  # SexDiffKG drug names that are in SIDER
    sider_ae_set = set(ae_mapping.values())  # SexDiffKG PT names that are in SIDER

    # All signals for SIDER-available drugs
    shared_drug_signals = signals_df[signals_df['drug_name'].isin(sider_drug_set)]
    logger.info(f"  SexDiffKG signals for SIDER-matched drugs: {len(shared_drug_signals)}")

    # Build set of SIDER drug-SE pairs (using SexDiffKG names)
    sider_pairs_sdkg = set()
    for _, row in xref_df.iterrows():
        if row['sdkg_drug'] and row['sdkg_pt']:
            sider_pairs_sdkg.add((row['sdkg_drug'], row['sdkg_pt']))

    # For each signal in shared drugs, check if the SE is listed in SIDER for that drug
    n_in_sider = 0
    n_not_in_sider = 0
    unlisted_signals = []
    for _, row in shared_drug_signals.iterrows():
        pair = (row['drug_name'], row['pt'])
        if pair in sider_pairs_sdkg:
            n_in_sider += 1
        else:
            n_not_in_sider += 1
            if abs(row['log_ror_ratio']) >= STRONG_LRR and row['min_reports'] >= MIN_REPORTS_ROBUST:
                unlisted_signals.append({
                    'drug': row['drug_name'],
                    'adverse_event': row['pt'],
                    'log_ror_ratio': round(float(row['log_ror_ratio']), 4),
                    'direction': row['direction'],
                    'min_reports': int(row['min_reports']),
                })

    unlisted_signals.sort(key=lambda x: abs(x['log_ror_ratio']), reverse=True)

    results['label_gap_analysis'] = {
        'description': 'Sex-differential signals in SexDiffKG for drugs also in SIDER. Shows which signals are/are not listed as side effects in drug labels.',
        'total_sexdiff_signals_for_sider_drugs': len(shared_drug_signals),
        'signals_for_listed_ses': n_in_sider,
        'signals_for_unlisted_ses': n_not_in_sider,
        'pct_unlisted': round(100 * n_not_in_sider / len(shared_drug_signals), 2) if len(shared_drug_signals) > 0 else 0,
        'interpretation': f'{n_not_in_sider} out of {len(shared_drug_signals)} sex-differential signals ({round(100*n_not_in_sider/len(shared_drug_signals),1) if len(shared_drug_signals) > 0 else 0}%) are for drug-AE pairs NOT listed in SIDER labels. These represent potential undisclosed sex-differential risks.',
        'top_unlisted_strong_signals': unlisted_signals[:50],
    }
    logger.info(f"  Label gap: {n_not_in_sider}/{len(shared_drug_signals)} signals are NOT in SIDER ({results['label_gap_analysis']['pct_unlisted']}%)")

    # --- 9. Summary statistics ---
    results['summary'] = {
        'sider_version': '4.1',
        'sider_drugs': int(sider_se_df['drug_name'].dropna().nunique()),
        'sider_side_effects_pt': int(sider_se_df['se_name'].nunique()),
        'sider_drug_se_pairs_pt': total_pairs,
        'sexdiffkg_signals': len(signals_df),
        'sexdiffkg_drugs': int(signals_df['drug_name'].nunique()),
        'sexdiffkg_pts': int(signals_df['pt'].nunique()),
        'drugs_matched': len(drug_mapping),
        'ses_matched': len(ae_mapping),
        'key_finding': f"Of {len(xref_df)} matchable SIDER drug-SE pairs, {len(has_signal)} ({results['overview']['pct_with_signal']}%) show sex-differential patterns in FAERS real-world data. {len(strong)} pairs show strong (>2.7x) sex differences.",
        'label_gap_finding': results['label_gap_analysis']['interpretation'],
    }

    return results


def main():
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (BASE / 'logs').mkdir(parents=True, exist_ok=True)

    # Load data
    drug_names, sider_se_df, sider_ind_df = load_sider()
    signals_df = load_sexdiffkg_signals()

    # Build matching indices
    drug_mapping, ae_mapping = build_matching_indices(sider_se_df, signals_df)

    # Cross-reference
    xref_df, total_pairs, unmatched_drug, unmatched_ae = cross_reference(
        sider_se_df, signals_df, drug_mapping, ae_mapping)

    # Analyze
    results = analyze_results(xref_df, signals_df, sider_se_df, drug_mapping, ae_mapping,
                              total_pairs, unmatched_drug, unmatched_ae)

    # Save
    with open(OUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Results saved to {OUT_FILE}")

    elapsed = time.time() - t0
    logger.info(f"Completed in {elapsed:.1f}s")

    # Print key findings
    print("\n" + "="*80)
    print("SIDER x SexDiffKG Cross-Reference -- Key Findings")
    print("="*80)
    print(f"\nSIDER: {results['summary']['sider_drugs']} drugs, {results['summary']['sider_side_effects_pt']} SEs, {results['summary']['sider_drug_se_pairs_pt']} pairs")
    print(f"SexDiffKG: {results['summary']['sexdiffkg_drugs']} drugs, {results['summary']['sexdiffkg_pts']} PTs, {results['summary']['sexdiffkg_signals']} signals")
    print(f"Matched: {results['summary']['drugs_matched']} drugs, {results['summary']['ses_matched']} SEs")
    print(f"\n{results['summary']['key_finding']}")
    print(f"\n{results['summary']['label_gap_finding']}")

    ov = results['overview']
    print(f"\n--- Signal Severity ---")
    print(f"  Strong (|LRR| >= 1.0): {ov['pairs_with_strong_signal_lrr_gte_1']} ({ov['pct_strong']}%)")
    print(f"  Moderate (|LRR| >= 0.5): {ov['pairs_with_moderate_signal_lrr_gte_05']} ({ov['pct_moderate']}%)")

    db = results.get('direction_breakdown', {})
    print(f"\n--- Direction ---")
    print(f"  Female-higher: {db.get('female_higher', 0)} ({db.get('pct_female_higher', 0)}%)")
    print(f"  Male-higher: {db.get('male_higher', 0)} ({db.get('pct_male_higher', 0)}%)")

    print(f"\n--- Top 10 Most Sex-Differential SIDER Side Effects ---")
    for i, se in enumerate(results['most_sex_differential_side_effects'][:10]):
        print(f"  {i+1}. {se['side_effect']}: mean|LRR|={se['mean_abs_log_ror_ratio']:.3f}, "
              f"{se['n_drugs_in_sider']} drugs, {se['pct_female_higher']:.0f}% female-higher")

    print(f"\n--- Drug Class Ranking (by % of SEs that are sex-differential) ---")
    for cls in results['drug_class_ranking']:
        print(f"  {cls['class']}: {cls['pct_with_signal']}% sex-diff, "
              f"{cls['n_drugs']} drugs, mean|LRR|={cls['mean_abs_lrr']:.3f}, "
              f"{cls['pct_female_higher']:.0f}% female-higher")

    print(f"\n--- Label Gap ---")
    lg = results['label_gap_analysis']
    print(f"  {lg['pct_unlisted']}% of sex-differential signals are for AEs NOT in SIDER labels")
    print(f"  Top unlisted strong signals:")
    for sig in lg['top_unlisted_strong_signals'][:5]:
        print(f"    {sig['drug']} + {sig['adverse_event']}: LRR={sig['log_ror_ratio']:.3f} ({sig['direction']}, n={sig['min_reports']})")

    print()
    return results


if __name__ == '__main__':
    main()
