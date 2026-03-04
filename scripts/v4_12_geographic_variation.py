#!/usr/bin/env python3
"""
SexDiffKG v4 - Step 12: Geographic Variation in Sex-Differential Signals
=========================================================================
Analyze whether sex-differential ADR patterns vary by reporter country.
Tests whether sex bias is universal or culturally/geographically modulated.

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
        logging.FileHandler('logs/v4_12_geographic_variation.log'),
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

# Top reporter countries to analyze (by expected volume)
TOP_COUNTRIES = ['US', 'JP', 'GB', 'FR', 'DE', 'CA', 'IT', 'ES', 'BR', 'KR']


def compute_signals_for_country(con, country_code):
    """Compute sex-differential signals for a specific country."""
    logger.info(f'Computing signals for {country_code}...')
    t0 = time.time()

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE demo_country AS
        SELECT * FROM read_parquet('{DEMO}')
        WHERE sex IN ('F', 'M')
          AND reporter_country = '{country_code}'
    """)

    n_reports = con.execute('SELECT COUNT(*) FROM demo_country').fetchone()[0]
    n_f = con.execute("SELECT COUNT(*) FROM demo_country WHERE sex='F'").fetchone()[0]
    n_m = con.execute("SELECT COUNT(*) FROM demo_country WHERE sex='M'").fetchone()[0]
    logger.info(f'{country_code}: {n_reports:,} reports (F={n_f:,}, M={n_m:,})')

    if n_reports < 5000 or n_f < 1000 or n_m < 1000:
        logger.warning(f'{country_code}: Too few reports ({n_reports:,}), skipping')
        return None

    # Drug-AE-sex counts
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE das_geo AS
        SELECT
            d.drugname_normalized as drug_name,
            r.pt as adverse_event,
            dm.sex,
            COUNT(DISTINCT d.primaryid) as report_count
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_country dm ON d.primaryid = dm.primaryid
        JOIN read_parquet('{REAC}') r ON d.primaryid = r.primaryid
        WHERE d.role_cod IN ('PS', 'SS')
          AND d.drugname_normalized IS NOT NULL AND d.drugname_normalized != ''
          AND r.pt IS NOT NULL AND r.pt != ''
        GROUP BY d.drugname_normalized, r.pt, dm.sex
    """)

    # Marginal totals
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE dst_geo AS
        SELECT d.drugname_normalized as drug_name, dm.sex,
               COUNT(DISTINCT d.primaryid) as drug_total
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_country dm ON d.primaryid = dm.primaryid
        WHERE d.role_cod IN ('PS', 'SS') AND d.drugname_normalized IS NOT NULL
        GROUP BY d.drugname_normalized, dm.sex
    """)

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ast_geo AS
        SELECT r.pt as adverse_event, dm.sex,
               COUNT(DISTINCT r.primaryid) as ae_total
        FROM read_parquet('{REAC}') r
        JOIN demo_country dm ON r.primaryid = dm.primaryid
        WHERE r.pt IS NOT NULL
        GROUP BY r.pt, dm.sex
    """)

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE st_geo AS
        SELECT sex, COUNT(DISTINCT primaryid) as N
        FROM demo_country GROUP BY sex
    """)

    # ROR
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ror_geo AS
        SELECT
            das.drug_name, das.adverse_event, das.sex,
            das.report_count as a,
            CASE WHEN (dst.drug_total - das.report_count) > 0
                  AND (ast.ae_total - das.report_count) > 0
                 THEN (das.report_count::DOUBLE * (st.N - dst.drug_total - ast.ae_total + das.report_count)::DOUBLE)
                    / ((dst.drug_total - das.report_count)::DOUBLE * (ast.ae_total - das.report_count)::DOUBLE)
                 ELSE NULL END as ror
        FROM das_geo das
        JOIN dst_geo dst ON das.drug_name = dst.drug_name AND das.sex = dst.sex
        JOIN ast_geo ast ON das.adverse_event = ast.adverse_event AND das.sex = ast.sex
        JOIN st_geo st ON das.sex = st.sex
        WHERE das.report_count >= {MIN_REPORTS_PER_SEX}
    """)

    # Sex-differential signals
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE signals_geo AS
        SELECT
            f.drug_name, f.adverse_event,
            f.ror as ror_female, f.a as n_female,
            m.ror as ror_male, m.a as n_male,
            LN(f.ror / m.ror) as log_ror_ratio,
            CASE WHEN LN(f.ror / m.ror) > 0 THEN 'female' ELSE 'male' END as direction
        FROM ror_geo f
        JOIN ror_geo m ON f.drug_name = m.drug_name AND f.adverse_event = m.adverse_event
        WHERE f.sex = 'F' AND m.sex = 'M'
          AND f.ror > 0 AND m.ror > 0
          AND f.ror IS NOT NULL AND m.ror IS NOT NULL
    """)

    total = con.execute('SELECT COUNT(*) FROM signals_geo').fetchone()[0]
    strong = con.execute(f"SELECT COUNT(*) FROM signals_geo WHERE ABS(log_ror_ratio) >= {LOG_RATIO_THRESHOLD}").fetchone()[0]
    f_bias = con.execute(f"SELECT COUNT(*) FROM signals_geo WHERE log_ror_ratio >= {LOG_RATIO_THRESHOLD}").fetchone()[0]
    m_bias = con.execute(f"SELECT COUNT(*) FROM signals_geo WHERE log_ror_ratio <= -{LOG_RATIO_THRESHOLD}").fetchone()[0]
    mean_lr = con.execute('SELECT AVG(log_ror_ratio) FROM signals_geo').fetchone()[0]

    elapsed = time.time() - t0
    logger.info(f'{country_code}: {total:,} signals, {strong:,} strong '
                f'(F={f_bias:,} [{f_bias/strong*100:.1f}%], M={m_bias:,}), '
                f'mean_lr={mean_lr:.4f}, {elapsed:.1f}s')

    return {
        'country': country_code,
        'reports': n_reports, 'female': n_f, 'male': n_m,
        'f_report_pct': round(n_f / n_reports * 100, 1),
        'total_signals': total, 'strong_signals': strong,
        'female_biased': f_bias, 'male_biased': m_bias,
        'f_bias_pct': round(f_bias / strong * 100, 1) if strong > 0 else 0,
        'mean_log_ratio': round(mean_lr, 4) if mean_lr else None,
    }


def main():
    start = time.time()
    logger.info('=' * 70)
    logger.info('SexDiffKG v4 - Geographic Variation Analysis')
    logger.info('=' * 70)

    con = duckdb.connect()
    con.execute('SET threads=16')
    con.execute("SET memory_limit='80GB'")

    # Check country column and top countries
    logger.info('Checking reporter country distribution...')
    country_dist = con.execute(f"""
        SELECT reporter_country, COUNT(*) as n
        FROM read_parquet('{DEMO}')
        WHERE reporter_country IS NOT NULL AND reporter_country != ''
          AND sex IN ('F', 'M')
        GROUP BY reporter_country
        ORDER BY n DESC
        LIMIT 20
    """).fetchall()

    logger.info('Top 20 reporter countries:')
    for cc, n in country_dist:
        logger.info(f'  {cc}: {n:,}')

    n_with_country = sum(n for _, n in country_dist)
    n_total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{DEMO}') WHERE sex IN ('F', 'M')").fetchone()[0]
    logger.info(f'Country coverage: {n_with_country:,} / {n_total:,} ({n_with_country/n_total*100:.1f}%)')

    # Use actual top countries from data
    actual_top = [cc for cc, n in country_dist if n >= 5000]
    logger.info(f'Countries with >= 5000 reports: {actual_top}')

    # Compute signals per country
    country_results = {}
    for cc in actual_top[:15]:  # Top 15 countries
        result = compute_signals_for_country(con, cc)
        if result:
            country_results[cc] = result

    # Cross-country comparison: correlation of sex bias for shared drug-AE pairs
    # Compare US vs JP (largest Western vs largest Asian reporter)
    logger.info('Computing cross-country correlations...')
    cross_country = {}

    countries_with_data = list(country_results.keys())
    if len(countries_with_data) >= 2:
        ref_country = countries_with_data[0]  # Usually US

        for other in countries_with_data[1:]:
            # Compute signals for both countries and correlate
            # We need to recompute to get paired data
            try:
                # Compute for reference
                ref_result = compute_signals_for_country(con, ref_country)

                # Save ref signals
                con.execute("CREATE OR REPLACE TEMP TABLE signals_ref AS SELECT * FROM signals_geo")

                # Compute for other
                other_result = compute_signals_for_country(con, other)

                # Correlate
                corr_data = con.execute("""
                    SELECT CORR(r.log_ror_ratio, o.log_ror_ratio), COUNT(*)
                    FROM signals_ref r
                    JOIN signals_geo o ON r.drug_name = o.drug_name AND r.adverse_event = o.adverse_event
                """).fetchone()

                if corr_data[0] is not None:
                    cross_country[f'{ref_country}_vs_{other}'] = {
                        'pearson_r': round(corr_data[0], 4),
                        'n_shared': corr_data[1],
                    }
                    logger.info(f'{ref_country} vs {other}: r={corr_data[0]:.4f} (n={corr_data[1]:,})')
            except Exception as e:
                logger.warning(f'Cross-country {ref_country} vs {other} failed: {e}')

    # Compile results
    results = {
        'analysis': 'Geographic Variation in Sex-Differential Signals',
        'date': '2026-03-04',
        'country_distribution': {cc: n for cc, n in country_dist[:20]},
        'country_results': country_results,
        'cross_country_correlations': cross_country,
        'runtime_seconds': round(time.time() - start, 1),
    }

    outfile = OUT_DIR / 'geographic_variation_v4.json'
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f'Results saved to {outfile}')

    # Summary
    logger.info('=' * 70)
    logger.info('GEOGRAPHIC VARIATION SUMMARY')
    logger.info('=' * 70)
    for cc, stats in sorted(country_results.items(), key=lambda x: x[1]['reports'], reverse=True):
        logger.info(f"{cc}: {stats['reports']:,} reports, "
                     f"{stats['strong_signals']:,} strong ({stats['f_bias_pct']:.1f}% F), "
                     f"mean_lr={stats['mean_log_ratio']}")
    if cross_country:
        logger.info('Cross-country correlations:')
        for pair, data in cross_country.items():
            logger.info(f"  {pair}: r={data['pearson_r']:.4f} (n={data['n_shared']:,})")
    logger.info(f'Runtime: {time.time()-start:.1f}s')


if __name__ == '__main__':
    main()
