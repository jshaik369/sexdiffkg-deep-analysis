#!/usr/bin/env python3
"""
SexDiffKG v4 - Step 10: Temporal Validation
=============================================
Train on FAERS 2004Q1-2020Q4, test on 2021Q1-2025Q3.
Tests whether signals discovered in earlier data predict signals in later data.
This validates temporal stability and reduces overfitting concerns.

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-04
"""

import json, logging, time
from pathlib import Path
import pandas as pd
import numpy as np
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/v4_10_temporal_validation.log'),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / 'sexdiffkg'
DRUG_V4 = BASE / 'data/processed/faers_clean/drug_normalized_v4.parquet'
DEMO = BASE / 'data/processed/faers_clean/demo.parquet'
REAC = BASE / 'data/processed/faers_clean/reac.parquet'
OUT_DIR = BASE / 'results/analysis'
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_REPORTS_PER_SEX = 10
LOG_RATIO_THRESHOLD = 0.5

# Temporal split: 2004Q1-2020Q4 = train, 2021Q1-2025Q3 = test
TRAIN_CUTOFF = '20201231'


def compute_signals_for_period(con, period_name, filter_clause):
    """Compute sex-differential signals for a time period."""
    logger.info(f'Computing signals for {period_name}...')
    t0 = time.time()

    # Create filtered demo table for this period
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE demo_period AS
        SELECT * FROM read_parquet('{DEMO}')
        WHERE sex IN ('F', 'M') {filter_clause}
    """)
    n_reports = con.execute('SELECT COUNT(*) FROM demo_period').fetchone()[0]
    n_f = con.execute("SELECT COUNT(*) FROM demo_period WHERE sex='F'").fetchone()[0]
    n_m = con.execute("SELECT COUNT(*) FROM demo_period WHERE sex='M'").fetchone()[0]
    logger.info(f'{period_name}: {n_reports:,} reports (F={n_f:,}, M={n_m:,})')

    if n_reports == 0:
        logger.error(f'No reports found for {period_name}!')
        return {'reports': 0, 'female': 0, 'male': 0, 'total_signals': 0,
                'strong_signals': 0, 'female_biased': 0, 'male_biased': 0}

    # Drug-AE-sex counts
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE das_{period_name} AS
        SELECT
            d.drugname_normalized as drug_name,
            r.pt as adverse_event,
            dm.sex,
            COUNT(DISTINCT d.primaryid) as report_count
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_period dm ON d.primaryid = dm.primaryid
        JOIN read_parquet('{REAC}') r ON d.primaryid = r.primaryid
        WHERE d.role_cod IN ('PS', 'SS')
          AND d.drugname_normalized IS NOT NULL AND d.drugname_normalized != ''
          AND r.pt IS NOT NULL AND r.pt != ''
        GROUP BY d.drugname_normalized, r.pt, dm.sex
    """)

    # Drug totals per sex
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE dst_{period_name} AS
        SELECT d.drugname_normalized as drug_name, dm.sex,
               COUNT(DISTINCT d.primaryid) as drug_total
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_period dm ON d.primaryid = dm.primaryid
        WHERE d.role_cod IN ('PS', 'SS') AND d.drugname_normalized IS NOT NULL
        GROUP BY d.drugname_normalized, dm.sex
    """)

    # AE totals per sex
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ast_{period_name} AS
        SELECT r.pt as adverse_event, dm.sex,
               COUNT(DISTINCT r.primaryid) as ae_total
        FROM read_parquet('{REAC}') r
        JOIN demo_period dm ON r.primaryid = dm.primaryid
        WHERE r.pt IS NOT NULL
        GROUP BY r.pt, dm.sex
    """)

    # Sex totals
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE st_{period_name} AS
        SELECT sex, COUNT(DISTINCT primaryid) as N
        FROM demo_period GROUP BY sex
    """)

    # Compute ROR
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ror_{period_name} AS
        SELECT
            das.drug_name, das.adverse_event, das.sex,
            das.report_count as a,
            CASE WHEN (dst.drug_total - das.report_count) > 0
                  AND (ast.ae_total - das.report_count) > 0
                 THEN (das.report_count::DOUBLE * (st.N - dst.drug_total - ast.ae_total + das.report_count)::DOUBLE)
                    / ((dst.drug_total - das.report_count)::DOUBLE * (ast.ae_total - das.report_count)::DOUBLE)
                 ELSE NULL END as ror
        FROM das_{period_name} das
        JOIN dst_{period_name} dst ON das.drug_name = dst.drug_name AND das.sex = dst.sex
        JOIN ast_{period_name} ast ON das.adverse_event = ast.adverse_event AND das.sex = ast.sex
        JOIN st_{period_name} st ON das.sex = st.sex
        WHERE das.report_count >= {MIN_REPORTS_PER_SEX}
    """)

    # Pivot to get F and M ROR side by side
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE signals_{period_name} AS
        SELECT
            f.drug_name, f.adverse_event,
            f.ror as ror_female, f.a as n_female,
            m.ror as ror_male, m.a as n_male,
            LN(f.ror / m.ror) as log_ror_ratio,
            CASE WHEN LN(f.ror / m.ror) > 0 THEN 'female' ELSE 'male' END as direction
        FROM ror_{period_name} f
        JOIN ror_{period_name} m ON f.drug_name = m.drug_name AND f.adverse_event = m.adverse_event
        WHERE f.sex = 'F' AND m.sex = 'M'
          AND f.ror > 0 AND m.ror > 0
          AND f.ror IS NOT NULL AND m.ror IS NOT NULL
    """)

    total = con.execute(f'SELECT COUNT(*) FROM signals_{period_name}').fetchone()[0]
    strong = con.execute(f"SELECT COUNT(*) FROM signals_{period_name} WHERE ABS(log_ror_ratio) >= {LOG_RATIO_THRESHOLD}").fetchone()[0]
    f_bias = con.execute(f"SELECT COUNT(*) FROM signals_{period_name} WHERE log_ror_ratio >= {LOG_RATIO_THRESHOLD}").fetchone()[0]
    m_bias = con.execute(f"SELECT COUNT(*) FROM signals_{period_name} WHERE log_ror_ratio <= -{LOG_RATIO_THRESHOLD}").fetchone()[0]

    logger.info(f'{period_name} signals: {total:,} total, {strong:,} strong (F={f_bias:,}, M={m_bias:,})')
    logger.info(f'{period_name} computed in {time.time()-t0:.1f}s')

    return {
        'reports': n_reports, 'female': n_f, 'male': n_m,
        'total_signals': total, 'strong_signals': strong,
        'female_biased': f_bias, 'male_biased': m_bias,
    }


def main():
    start = time.time()
    logger.info('=' * 70)
    logger.info('SexDiffKG v4 - Temporal Validation (2004-2020 train, 2021-2025 test)')
    logger.info('=' * 70)

    con = duckdb.connect()
    con.execute('SET threads=16')
    con.execute("SET memory_limit='80GB'")

    # Check demo columns for date field
    cols = con.execute(f"SELECT column_name FROM (DESCRIBE SELECT * FROM read_parquet('{DEMO}'))").fetchall()
    col_names = [c[0] for c in cols]
    logger.info(f'Demo columns: {col_names}')

    # FAERS demo table typically has: event_dt or init_fda_dt
    date_col = None
    for candidate in ['event_dt', 'init_fda_dt', 'fda_dt', 'rept_dt']:
        if candidate in col_names:
            date_col = candidate
            break

    if date_col is None:
        logger.warning(f'No standard date column found in demo. Available: {col_names}')
        # Try any column with 'dt' or 'date' in name
        for cn in col_names:
            if 'dt' in cn.lower() or 'date' in cn.lower():
                date_col = cn
                logger.info(f'Found date-like column: {date_col}')
                break

    if date_col is not None:
        logger.info(f'Using date column: {date_col}')
        # Sample values to understand format
        samples = con.execute(f"SELECT {date_col} FROM read_parquet('{DEMO}') WHERE {date_col} IS NOT NULL AND CAST({date_col} AS VARCHAR) != '' LIMIT 10").fetchall()
        logger.info(f'Sample dates: {[s[0] for s in samples]}')

        # Check coverage
        n_with_date = con.execute(f"SELECT COUNT(*) FROM read_parquet('{DEMO}') WHERE {date_col} IS NOT NULL AND CAST({date_col} AS VARCHAR) != ''").fetchone()[0]
        n_total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{DEMO}')").fetchone()[0]
        logger.info(f'Date coverage: {n_with_date:,} / {n_total:,} ({n_with_date/n_total*100:.1f}%)')

        train_filter = f"AND CAST({date_col} AS VARCHAR) <= '{TRAIN_CUTOFF}'"
        test_filter = f"AND CAST({date_col} AS VARCHAR) > '{TRAIN_CUTOFF}'"
    else:
        logger.warning('No date column found - using primaryid-based approximate split')
        # FAERS primaryids generally increase over time
        # 2004-2020 is ~77% of the 2004-2025 range (17/22 years)
        percentile = con.execute(f"SELECT PERCENTILE_CONT(0.77) WITHIN GROUP (ORDER BY CAST(primaryid AS BIGINT)) FROM read_parquet('{DEMO}')").fetchone()[0]
        logger.info(f'77th percentile primaryid: {percentile}')
        train_filter = f"AND CAST(primaryid AS BIGINT) <= {int(percentile)}"
        test_filter = f"AND CAST(primaryid AS BIGINT) > {int(percentile)}"

    # Compute signals for each period
    train_stats = compute_signals_for_period(con, 'train', train_filter)
    test_stats = compute_signals_for_period(con, 'test', test_filter)

    if train_stats['total_signals'] == 0 or test_stats['total_signals'] == 0:
        logger.error('One period has zero signals - cannot compute overlap')
        results = {
            'error': 'Insufficient data for temporal split',
            'train': train_stats,
            'test': test_stats,
        }
        outfile = OUT_DIR / 'temporal_validation_v4.json'
        with open(outfile, 'w') as f:
            json.dump(results, f, indent=2)
        return

    # Compare: how many test signals were predicted by train?
    logger.info('Computing temporal overlap...')

    # Strong signals in both periods
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE overlap AS
        SELECT
            tr.drug_name, tr.adverse_event,
            tr.log_ror_ratio as train_log_ratio,
            tr.direction as train_direction,
            te.log_ror_ratio as test_log_ratio,
            te.direction as test_direction,
            CASE WHEN tr.direction = te.direction THEN 1 ELSE 0 END as same_direction
        FROM signals_train tr
        JOIN signals_test te ON tr.drug_name = te.drug_name AND tr.adverse_event = te.adverse_event
        WHERE ABS(tr.log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
          AND ABS(te.log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
    """)

    overlap_total = con.execute('SELECT COUNT(*) FROM overlap').fetchone()[0]
    overlap_same = con.execute('SELECT SUM(same_direction) FROM overlap').fetchone()[0] or 0

    # Relaxed: strong in train, any signal in test
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE relaxed_overlap AS
        SELECT
            tr.drug_name, tr.adverse_event,
            tr.direction as train_direction,
            te.direction as test_direction,
            CASE WHEN tr.direction = te.direction THEN 1 ELSE 0 END as same_direction
        FROM signals_train tr
        JOIN signals_test te ON tr.drug_name = te.drug_name AND tr.adverse_event = te.adverse_event
        WHERE ABS(tr.log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
    """)

    relaxed_total = con.execute('SELECT COUNT(*) FROM relaxed_overlap').fetchone()[0]
    relaxed_same = con.execute('SELECT SUM(same_direction) FROM relaxed_overlap').fetchone()[0] or 0

    # Correlation between train and test log_ror_ratio
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE corr_data AS
        SELECT tr.log_ror_ratio as train_lr, te.log_ror_ratio as test_lr
        FROM signals_train tr
        JOIN signals_test te ON tr.drug_name = te.drug_name AND tr.adverse_event = te.adverse_event
    """)

    corr_n = con.execute('SELECT COUNT(*) FROM corr_data').fetchone()[0]
    if corr_n > 0:
        corr = con.execute('SELECT CORR(train_lr, test_lr) FROM corr_data').fetchone()[0]
    else:
        corr = None

    # New signals in test period (not strong in train)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE novel_test AS
        SELECT te.drug_name, te.adverse_event, te.log_ror_ratio, te.direction
        FROM signals_test te
        LEFT JOIN signals_train tr ON te.drug_name = tr.drug_name AND te.adverse_event = tr.adverse_event
            AND ABS(tr.log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
        WHERE ABS(te.log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
          AND tr.drug_name IS NULL
    """)
    novel_count = con.execute('SELECT COUNT(*) FROM novel_test').fetchone()[0]

    # Compile results
    results = {
        'analysis': 'Temporal Validation',
        'date_column_used': date_col if date_col else 'primaryid_percentile',
        'train_period': '2004Q1-2020Q4 (approximate)',
        'test_period': '2021Q1-2025Q3 (approximate)',
        'train': train_stats,
        'test': test_stats,
        'overlap': {
            'strong_in_both': overlap_total,
            'same_direction': int(overlap_same),
            'directional_precision_pct': round(overlap_same / overlap_total * 100, 1) if overlap_total > 0 else None,
        },
        'relaxed_overlap': {
            'train_strong_in_test_any': relaxed_total,
            'same_direction': int(relaxed_same),
            'directional_precision_pct': round(relaxed_same / relaxed_total * 100, 1) if relaxed_total > 0 else None,
        },
        'correlation': {
            'n_shared_pairs': corr_n,
            'pearson_r': round(corr, 4) if corr is not None else None,
        },
        'novel_test_signals': novel_count,
        'runtime_seconds': round(time.time() - start, 1),
    }

    # Save
    outfile = OUT_DIR / 'temporal_validation_v4.json'
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f'Results saved to {outfile}')

    # Print summary
    logger.info('=' * 70)
    logger.info('TEMPORAL VALIDATION SUMMARY')
    logger.info('=' * 70)
    logger.info(f"Train: {train_stats['reports']:,} reports -> {train_stats['strong_signals']:,} strong signals")
    logger.info(f"Test:  {test_stats['reports']:,} reports -> {test_stats['strong_signals']:,} strong signals")
    logger.info(f'Strong in both periods: {overlap_total:,}')
    if overlap_total > 0:
        logger.info(f'Same direction: {int(overlap_same):,} ({overlap_same/overlap_total*100:.1f}%)')
    logger.info(f'Relaxed overlap (train strong -> test any): {relaxed_total:,}')
    if relaxed_total > 0:
        logger.info(f'Same direction: {int(relaxed_same):,} ({relaxed_same/relaxed_total*100:.1f}%)')
    if corr is not None:
        logger.info(f'Pearson correlation (shared pairs): r={corr:.4f} (n={corr_n:,})')
    logger.info(f'Novel test signals (not in train): {novel_count:,}')
    logger.info(f'Runtime: {time.time()-start:.1f}s')


if __name__ == '__main__':
    main()
