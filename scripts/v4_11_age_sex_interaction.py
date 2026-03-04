#!/usr/bin/env python3
"""
SexDiffKG v4 - Step 11: Age-Sex Interaction Analysis
=====================================================
Investigate whether sex-differential ADR patterns change with age.
Key question: Do certain drugs show F-biased ADRs only in younger women
but not post-menopausal women? (hormonal hypothesis)

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-04
"""

import json, logging, time, math
from pathlib import Path
import pandas as pd
import numpy as np
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/v4_11_age_sex_interaction.log'),
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

MIN_REPORTS_PER_GROUP = 10
LOG_RATIO_THRESHOLD = 0.5

# Age groups (biologically meaningful for sex hormone differences)
AGE_GROUPS = {
    'young_adult': (18, 44),    # Reproductive age
    'middle_aged': (45, 64),    # Peri-/post-menopausal transition
    'elderly': (65, 120),       # Post-menopausal, andropause
}


def compute_signals_for_age_group(con, group_name, age_min, age_max):
    """Compute sex-differential signals for a specific age group."""
    logger.info(f'Computing signals for {group_name} (ages {age_min}-{age_max})...')
    t0 = time.time()

    # Create filtered demo table for this age group
    # FAERS age is in age + age_cod (YR, MON, WK, DY, HR, DEC)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE demo_age AS
        SELECT * FROM read_parquet('{DEMO}')
        WHERE sex IN ('F', 'M')
          AND age IS NOT NULL
          AND age_cod = 'YR'
          AND CAST(age AS DOUBLE) >= {age_min}
          AND CAST(age AS DOUBLE) < {age_max}
    """)

    n_reports = con.execute('SELECT COUNT(*) FROM demo_age').fetchone()[0]
    n_f = con.execute("SELECT COUNT(*) FROM demo_age WHERE sex='F'").fetchone()[0]
    n_m = con.execute("SELECT COUNT(*) FROM demo_age WHERE sex='M'").fetchone()[0]
    logger.info(f'{group_name}: {n_reports:,} reports (F={n_f:,}, M={n_m:,})')

    if n_reports < 1000 or n_f < 100 or n_m < 100:
        logger.warning(f'{group_name}: Too few reports, skipping')
        return None

    # Drug-AE-sex counts
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE das_{group_name} AS
        SELECT
            d.drugname_normalized as drug_name,
            r.pt as adverse_event,
            dm.sex,
            COUNT(DISTINCT d.primaryid) as report_count
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_age dm ON d.primaryid = dm.primaryid
        JOIN read_parquet('{REAC}') r ON d.primaryid = r.primaryid
        WHERE d.role_cod IN ('PS', 'SS')
          AND d.drugname_normalized IS NOT NULL AND d.drugname_normalized != ''
          AND r.pt IS NOT NULL AND r.pt != ''
        GROUP BY d.drugname_normalized, r.pt, dm.sex
    """)

    # Marginal totals
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE dst_{group_name} AS
        SELECT d.drugname_normalized as drug_name, dm.sex,
               COUNT(DISTINCT d.primaryid) as drug_total
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_age dm ON d.primaryid = dm.primaryid
        WHERE d.role_cod IN ('PS', 'SS') AND d.drugname_normalized IS NOT NULL
        GROUP BY d.drugname_normalized, dm.sex
    """)

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ast_{group_name} AS
        SELECT r.pt as adverse_event, dm.sex,
               COUNT(DISTINCT r.primaryid) as ae_total
        FROM read_parquet('{REAC}') r
        JOIN demo_age dm ON r.primaryid = dm.primaryid
        WHERE r.pt IS NOT NULL
        GROUP BY r.pt, dm.sex
    """)

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE st_{group_name} AS
        SELECT sex, COUNT(DISTINCT primaryid) as N
        FROM demo_age GROUP BY sex
    """)

    # ROR computation
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ror_{group_name} AS
        SELECT
            das.drug_name, das.adverse_event, das.sex,
            das.report_count as a,
            CASE WHEN (dst.drug_total - das.report_count) > 0
                  AND (ast.ae_total - das.report_count) > 0
                 THEN (das.report_count::DOUBLE * (st.N - dst.drug_total - ast.ae_total + das.report_count)::DOUBLE)
                    / ((dst.drug_total - das.report_count)::DOUBLE * (ast.ae_total - das.report_count)::DOUBLE)
                 ELSE NULL END as ror
        FROM das_{group_name} das
        JOIN dst_{group_name} dst ON das.drug_name = dst.drug_name AND das.sex = dst.sex
        JOIN ast_{group_name} ast ON das.adverse_event = ast.adverse_event AND das.sex = ast.sex
        JOIN st_{group_name} st ON das.sex = st.sex
        WHERE das.report_count >= {MIN_REPORTS_PER_GROUP}
    """)

    # Sex-differential signals
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE signals_{group_name} AS
        SELECT
            f.drug_name, f.adverse_event,
            f.ror as ror_female, f.a as n_female,
            m.ror as ror_male, m.a as n_male,
            LN(f.ror / m.ror) as log_ror_ratio,
            CASE WHEN LN(f.ror / m.ror) > 0 THEN 'female' ELSE 'male' END as direction
        FROM ror_{group_name} f
        JOIN ror_{group_name} m ON f.drug_name = m.drug_name AND f.adverse_event = m.adverse_event
        WHERE f.sex = 'F' AND m.sex = 'M'
          AND f.ror > 0 AND m.ror > 0
          AND f.ror IS NOT NULL AND m.ror IS NOT NULL
    """)

    total = con.execute(f'SELECT COUNT(*) FROM signals_{group_name}').fetchone()[0]
    strong = con.execute(f"SELECT COUNT(*) FROM signals_{group_name} WHERE ABS(log_ror_ratio) >= {LOG_RATIO_THRESHOLD}").fetchone()[0]
    f_bias = con.execute(f"SELECT COUNT(*) FROM signals_{group_name} WHERE log_ror_ratio >= {LOG_RATIO_THRESHOLD}").fetchone()[0]
    m_bias = con.execute(f"SELECT COUNT(*) FROM signals_{group_name} WHERE log_ror_ratio <= -{LOG_RATIO_THRESHOLD}").fetchone()[0]
    mean_lr = con.execute(f"SELECT AVG(log_ror_ratio) FROM signals_{group_name}").fetchone()[0]
    median_lr = con.execute(f"SELECT MEDIAN(log_ror_ratio) FROM signals_{group_name}").fetchone()[0]

    logger.info(f'{group_name}: {total:,} signals, {strong:,} strong (F={f_bias:,}, M={m_bias:,}), mean={mean_lr:.4f}, median={median_lr:.4f}')
    logger.info(f'{group_name} computed in {time.time()-t0:.1f}s')

    return {
        'age_range': f'{age_min}-{age_max}',
        'reports': n_reports, 'female': n_f, 'male': n_m,
        'total_signals': total, 'strong_signals': strong,
        'female_biased': f_bias, 'male_biased': m_bias,
        'f_pct': round(f_bias / strong * 100, 1) if strong > 0 else 0,
        'mean_log_ratio': round(mean_lr, 4) if mean_lr else None,
        'median_log_ratio': round(median_lr, 4) if median_lr else None,
    }


def analyze_drug_class_by_age(con, drug_class_name, drug_list):
    """Analyze sex bias for a drug class across age groups."""
    results = {}
    for gname in AGE_GROUPS:
        try:
            # Check if signals table exists for this age group
            drugs_str = "','".join(d.replace("'", "''") for d in drug_list)
            row = con.execute(f"""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN log_ror_ratio >= {LOG_RATIO_THRESHOLD} THEN 1 ELSE 0 END) as f_bias,
                    SUM(CASE WHEN log_ror_ratio <= -{LOG_RATIO_THRESHOLD} THEN 1 ELSE 0 END) as m_bias,
                    AVG(log_ror_ratio) as mean_lr
                FROM signals_{gname}
                WHERE drug_name IN ('{drugs_str}')
                  AND ABS(log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
            """).fetchone()
            results[gname] = {
                'total': row[0], 'f_bias': row[1], 'm_bias': row[2],
                'mean_log_ratio': round(row[3], 4) if row[3] else None,
            }
        except Exception as e:
            results[gname] = {'error': str(e)}
    return results


def main():
    start = time.time()
    logger.info('=' * 70)
    logger.info('SexDiffKG v4 - Age-Sex Interaction Analysis')
    logger.info('=' * 70)

    con = duckdb.connect()
    con.execute('SET threads=16')
    con.execute("SET memory_limit='80GB'")

    # Check age column availability
    sample = con.execute(f"""
        SELECT age_cod, COUNT(*) as n
        FROM read_parquet('{DEMO}')
        WHERE age IS NOT NULL AND age_cod IS NOT NULL
        GROUP BY age_cod
        ORDER BY n DESC
        LIMIT 10
    """).fetchall()
    logger.info(f'Age coding distribution: {sample}')

    n_yr = con.execute(f"""
        SELECT COUNT(*) FROM read_parquet('{DEMO}')
        WHERE age IS NOT NULL AND age_cod = 'YR' AND sex IN ('F', 'M')
    """).fetchone()[0]
    n_total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{DEMO}') WHERE sex IN ('F', 'M')").fetchone()[0]
    logger.info(f'Reports with age in years: {n_yr:,} / {n_total:,} ({n_yr/n_total*100:.1f}%)')

    # Compute signals per age group
    age_results = {}
    for gname, (age_min, age_max) in AGE_GROUPS.items():
        result = compute_signals_for_age_group(con, gname, age_min, age_max)
        if result:
            age_results[gname] = result

    # Analyze key drug classes across age groups
    logger.info('Analyzing drug classes across age groups...')

    # Define drug classes by common drug names
    drug_classes = {
        'opioids': ['TRAMADOL', 'OXYCODONE', 'HYDROCODONE', 'MORPHINE', 'FENTANYL',
                     'CODEINE', 'METHADONE', 'BUPRENORPHINE', 'TAPENTADOL', 'OXYMORPHONE'],
        'antipsychotics': ['QUETIAPINE', 'OLANZAPINE', 'RISPERIDONE', 'ARIPIPRAZOLE',
                          'CLOZAPINE', 'HALOPERIDOL', 'PALIPERIDONE', 'CARIPRAZINE',
                          'BREXPIPRAZOLE', 'LURASIDONE'],
        'ssris': ['SERTRALINE', 'FLUOXETINE', 'ESCITALOPRAM', 'PAROXETINE',
                  'CITALOPRAM', 'FLUVOXAMINE'],
        'statins': ['ATORVASTATIN', 'ROSUVASTATIN', 'SIMVASTATIN', 'PRAVASTATIN',
                    'LOVASTATIN', 'PITAVASTATIN'],
        'ace_inhibitors': ['LISINOPRIL', 'ENALAPRIL', 'RAMIPRIL', 'CAPTOPRIL',
                           'PERINDOPRIL', 'BENAZEPRIL', 'QUINAPRIL'],
        'hormonal': ['TAMOXIFEN', 'LETROZOLE', 'ANASTROZOLE', 'EXEMESTANE',
                     'FULVESTRANT', 'LEUPROLIDE', 'GOSERELIN'],
    }

    class_age_results = {}
    for class_name, drugs in drug_classes.items():
        class_age_results[class_name] = analyze_drug_class_by_age(con, class_name, drugs)

    # Find signals that flip direction across age groups
    logger.info('Finding age-dependent direction flips...')
    try:
        # Signals strong-F in young but strong-M (or neutral) in elderly
        con.execute(f"""
            CREATE OR REPLACE TEMP TABLE direction_flips AS
            SELECT
                y.drug_name, y.adverse_event,
                y.log_ror_ratio as young_lr,
                e.log_ror_ratio as elderly_lr,
                y.direction as young_dir,
                e.direction as elderly_dir
            FROM signals_young_adult y
            JOIN signals_elderly e ON y.drug_name = e.drug_name AND y.adverse_event = e.adverse_event
            WHERE ABS(y.log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
              AND ABS(e.log_ror_ratio) >= {LOG_RATIO_THRESHOLD}
              AND y.direction != e.direction
        """)
        n_flips = con.execute('SELECT COUNT(*) FROM direction_flips').fetchone()[0]
        logger.info(f'Direction flips (young vs elderly): {n_flips:,}')

        # Top flips by magnitude change
        top_flips = con.execute("""
            SELECT drug_name, adverse_event, young_lr, elderly_lr,
                   young_dir, elderly_dir, ABS(young_lr - elderly_lr) as delta
            FROM direction_flips
            ORDER BY delta DESC
            LIMIT 20
        """).fetchall()

        flips_list = []
        for row in top_flips:
            flips_list.append({
                'drug': row[0], 'ae': row[1],
                'young_log_ratio': round(row[2], 3), 'elderly_log_ratio': round(row[3], 3),
                'young_direction': row[4], 'elderly_direction': row[5],
                'delta': round(row[6], 3),
            })
        logger.info(f'Top direction flips: {json.dumps(flips_list[:5], indent=2)}')
    except Exception as e:
        logger.warning(f'Direction flip analysis failed: {e}')
        n_flips = 0
        flips_list = []

    # Compile results
    results = {
        'analysis': 'Age-Sex Interaction Analysis',
        'date': '2026-03-04',
        'age_coverage': {
            'reports_with_age_yr': n_yr,
            'total_reports': n_total,
            'coverage_pct': round(n_yr / n_total * 100, 1),
        },
        'age_groups': age_results,
        'drug_class_by_age': class_age_results,
        'direction_flips': {
            'count': n_flips,
            'top_20': flips_list,
        },
        'runtime_seconds': round(time.time() - start, 1),
    }

    outfile = OUT_DIR / 'age_sex_interaction_v4.json'
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f'Results saved to {outfile}')

    # Summary
    logger.info('=' * 70)
    logger.info('AGE-SEX INTERACTION SUMMARY')
    logger.info('=' * 70)
    for gname, stats in age_results.items():
        logger.info(f"{gname} ({stats['age_range']}): {stats['reports']:,} reports, "
                     f"{stats['strong_signals']:,} strong ({stats['f_pct']:.1f}% F), "
                     f"mean_lr={stats['mean_log_ratio']}")
    logger.info(f'Direction flips young->elderly: {n_flips}')
    logger.info(f'Runtime: {time.time()-start:.1f}s')


if __name__ == '__main__':
    main()
