#!/usr/bin/env python3
"""
SexDiffKG v4 - Step 14: Deep Per-Country FAERS Analysis (Fixed)
Author: JShaik (jshaik@coevolvenetwork.com) | Date: 2026-03-04
"""
import json, logging, time, re
from pathlib import Path
import duckdb

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('logs/v4_14_per_country_deep.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

BASE = Path.home() / 'sexdiffkg'
DRUG_V4 = BASE / 'data/processed/faers_clean/drug_normalized_v4.parquet'
DEMO = BASE / 'data/processed/faers_clean/demo.parquet'
REAC = BASE / 'data/processed/faers_clean/reac.parquet'
OUT_DIR = BASE / 'results/analysis'

MIN_REPORTS = 5
LR_THRESH = 0.5

DRUG_CLASSES = {
    'opioids': ['TRAMADOL','OXYCODONE','HYDROCODONE','MORPHINE','FENTANYL','CODEINE','METHADONE'],
    'antipsychotics': ['QUETIAPINE','OLANZAPINE','RISPERIDONE','ARIPIPRAZOLE','CLOZAPINE','HALOPERIDOL'],
    'ssris': ['SERTRALINE','FLUOXETINE','ESCITALOPRAM','PAROXETINE','CITALOPRAM'],
    'ace_inhibitors': ['LISINOPRIL','ENALAPRIL','RAMIPRIL','CAPTOPRIL'],
    'checkpoint_inhibitors': ['PEMBROLIZUMAB','NIVOLUMAB','ATEZOLIZUMAB','DURVALUMAB','IPILIMUMAB'],
    'nsaids': ['IBUPROFEN','NAPROXEN','DICLOFENAC','CELECOXIB','MELOXICAM'],
    'statins': ['ATORVASTATIN','ROSUVASTATIN','SIMVASTATIN','PRAVASTATIN'],
    'anticoagulants': ['WARFARIN','RIVAROXABAN','APIXABAN','DABIGATRAN'],
    'corticosteroids': ['PREDNISONE','METHYLPREDNISOLONE','DEXAMETHASONE','PREDNISOLONE'],
}

def safe_table_name(cc):
    return re.sub(r'[^A-Za-z0-9]', '_', cc)

def compute_country(con, cc, safe_cc):
    t0 = time.time()
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE das_{safe_cc} AS
        SELECT d.drugname_normalized as drug_name, r.pt as adverse_event, dm.sex,
               COUNT(DISTINCT d.primaryid) as report_count
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_{safe_cc} dm ON d.primaryid = dm.primaryid
        JOIN read_parquet('{REAC}') r ON d.primaryid = r.primaryid
        WHERE d.role_cod IN ('PS','SS') AND d.drugname_normalized IS NOT NULL AND d.drugname_normalized != ''
          AND r.pt IS NOT NULL AND r.pt != ''
        GROUP BY d.drugname_normalized, r.pt, dm.sex
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE dst_{safe_cc} AS
        SELECT d.drugname_normalized as drug_name, dm.sex, COUNT(DISTINCT d.primaryid) as drug_total
        FROM read_parquet('{DRUG_V4}') d
        JOIN demo_{safe_cc} dm ON d.primaryid = dm.primaryid
        WHERE d.role_cod IN ('PS','SS') AND d.drugname_normalized IS NOT NULL
        GROUP BY d.drugname_normalized, dm.sex
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ast_{safe_cc} AS
        SELECT r.pt as adverse_event, dm.sex, COUNT(DISTINCT r.primaryid) as ae_total
        FROM read_parquet('{REAC}') r
        JOIN demo_{safe_cc} dm ON r.primaryid = dm.primaryid
        WHERE r.pt IS NOT NULL GROUP BY r.pt, dm.sex
    """)
    con.execute(f"CREATE OR REPLACE TEMP TABLE st_{safe_cc} AS SELECT sex, COUNT(DISTINCT primaryid) as N FROM demo_{safe_cc} GROUP BY sex")

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ror_{safe_cc} AS
        SELECT das.drug_name, das.adverse_event, das.sex, das.report_count as a,
            CASE WHEN (dst.drug_total - das.report_count) > 0 AND (ast.ae_total - das.report_count) > 0
                 THEN (das.report_count::DOUBLE * (st.N - dst.drug_total - ast.ae_total + das.report_count)::DOUBLE)
                    / ((dst.drug_total - das.report_count)::DOUBLE * (ast.ae_total - das.report_count)::DOUBLE)
                 ELSE NULL END as ror
        FROM das_{safe_cc} das
        JOIN dst_{safe_cc} dst ON das.drug_name = dst.drug_name AND das.sex = dst.sex
        JOIN ast_{safe_cc} ast ON das.adverse_event = ast.adverse_event AND das.sex = ast.sex
        JOIN st_{safe_cc} st ON das.sex = st.sex
        WHERE das.report_count >= {MIN_REPORTS}
    """)

    con.execute(f"""
        CREATE OR REPLACE TABLE signals_{safe_cc} AS
        SELECT f.drug_name, f.adverse_event,
            f.ror as ror_female, f.a as n_female,
            m.ror as ror_male, m.a as n_male,
            LN(f.ror / m.ror) as log_ror_ratio,
            CASE WHEN LN(f.ror / m.ror) > 0 THEN 'female' ELSE 'male' END as direction
        FROM ror_{safe_cc} f
        JOIN ror_{safe_cc} m ON f.drug_name = m.drug_name AND f.adverse_event = m.adverse_event
        WHERE f.sex = 'F' AND m.sex = 'M' AND f.ror > 0 AND m.ror > 0
          AND f.ror IS NOT NULL AND m.ror IS NOT NULL
    """)

    total = con.execute(f'SELECT COUNT(*) FROM signals_{safe_cc}').fetchone()[0]
    strong = con.execute(f"SELECT COUNT(*) FROM signals_{safe_cc} WHERE ABS(log_ror_ratio) >= {LR_THRESH}").fetchone()[0]
    f_bias = con.execute(f"SELECT COUNT(*) FROM signals_{safe_cc} WHERE log_ror_ratio >= {LR_THRESH}").fetchone()[0]
    m_bias = con.execute(f"SELECT COUNT(*) FROM signals_{safe_cc} WHERE log_ror_ratio <= -{LR_THRESH}").fetchone()[0]
    mean_lr = con.execute(f"SELECT AVG(log_ror_ratio) FROM signals_{safe_cc}").fetchone()[0]

    # Drug class analysis
    class_res = {}
    for cn, drugs in DRUG_CLASSES.items():
        ds = "','".join(d.replace("'","''") for d in drugs)
        try:
            row = con.execute(f"""
                SELECT COUNT(*), SUM(CASE WHEN log_ror_ratio >= {LR_THRESH} THEN 1 ELSE 0 END),
                       SUM(CASE WHEN log_ror_ratio <= -{LR_THRESH} THEN 1 ELSE 0 END), AVG(log_ror_ratio)
                FROM signals_{safe_cc} WHERE drug_name IN ('{ds}') AND ABS(log_ror_ratio) >= {LR_THRESH}
            """).fetchone()
            if row[0] > 0:
                class_res[cn] = {'total': row[0], 'f': row[1], 'm': row[2],
                                 'f_pct': round(row[1]/row[0]*100,1), 'mlr': round(row[3],4) if row[3] else None}
        except:
            pass

    elapsed = time.time() - t0
    logger.info(f'{cc}: {total:,} total, {strong:,} strong (F={f_bias:,}, M={m_bias:,}), {elapsed:.1f}s')

    return {
        'total_signals': total, 'strong_signals': strong,
        'female_biased': f_bias, 'male_biased': m_bias,
        'f_pct': round(f_bias/strong*100, 1) if strong > 0 else 0,
        'mean_log_ratio': round(mean_lr, 4) if mean_lr else None,
        'drug_classes': class_res,
        'compute_seconds': round(elapsed, 1),
    }

def main():
    start = time.time()
    logger.info('='*70)
    logger.info('Deep Per-Country FAERS Analysis')
    logger.info('='*70)
    con = duckdb.connect()
    con.execute('SET threads=16')
    con.execute("SET memory_limit='80GB'")

    # Get all countries
    country_dist = con.execute(f"""
        SELECT reporter_country, COUNT(*) as n,
               SUM(CASE WHEN sex='F' THEN 1 ELSE 0 END) as n_f,
               SUM(CASE WHEN sex='M' THEN 1 ELSE 0 END) as n_m
        FROM read_parquet('{DEMO}')
        WHERE reporter_country IS NOT NULL AND reporter_country != ''
          AND sex IN ('F', 'M')
        GROUP BY reporter_country
        HAVING COUNT(*) >= 3000 AND SUM(CASE WHEN sex='F' THEN 1 ELSE 0 END) >= 500
          AND SUM(CASE WHEN sex='M' THEN 1 ELSE 0 END) >= 500
        ORDER BY n DESC
    """).fetchall()
    logger.info(f'{len(country_dist)} countries with >= 3000 reports')

    country_results = {}
    for cc, n, nf, nm in country_dist:
        safe_cc = safe_table_name(cc)
        logger.info(f'\nProcessing {cc} (safe={safe_cc}, {n:,} reports)...')
        con.execute(f"""
            CREATE OR REPLACE TEMP TABLE demo_{safe_cc} AS
            SELECT * FROM read_parquet('{DEMO}')
            WHERE sex IN ('F','M') AND reporter_country = '{cc.replace("'","''")}'
        """)
        try:
            res = compute_country(con, cc, safe_cc)
            country_results[cc] = {'reports': n, 'female': nf, 'male': nm,
                                   'f_reporter_pct': round(nf/n*100, 1), **res}
        except Exception as e:
            logger.error(f'{cc} FAILED: {e}')
            country_results[cc] = {'error': str(e)}

    # Cross-country correlations
    logger.info('\nCross-country correlations...')
    good = [(cc, safe_table_name(cc)) for cc, r in country_results.items()
            if 'error' not in r and r.get('strong_signals', 0) > 100]
    corr_matrix = {}
    for i, (cc1, sc1) in enumerate(good):
        for cc2, sc2 in good[i+1:]:
            try:
                row = con.execute(f"""
                    SELECT CORR(a.log_ror_ratio, b.log_ror_ratio), COUNT(*)
                    FROM signals_{sc1} a JOIN signals_{sc2} b
                    ON a.drug_name = b.drug_name AND a.adverse_event = b.adverse_event
                    WHERE ABS(a.log_ror_ratio) >= {LR_THRESH} AND ABS(b.log_ror_ratio) >= {LR_THRESH}
                """).fetchone()
                if row[0] is not None and row[1] >= 10:
                    corr_matrix[f'{cc1}_vs_{cc2}'] = {'r': round(row[0],4), 'n': row[1]}
            except:
                pass

    # Ranking
    ranked = sorted([(cc,r) for cc,r in country_results.items() if 'error' not in r],
                    key=lambda x: x[1].get('f_pct', 0), reverse=True)
    logger.info('\n' + '='*70)
    logger.info('RANKING BY FEMALE BIAS')
    for i, (cc, r) in enumerate(ranked, 1):
        logger.info(f'{i:2d}. {cc}: {r["f_pct"]:5.1f}% F-biased ({r["strong_signals"]:,} strong) | {r["f_reporter_pct"]:.1f}% F reporters')

    results = {
        'analysis': 'Deep Per-Country FAERS Analysis', 'date': '2026-03-04',
        'n_countries': len(country_results),
        'country_results': country_results,
        'correlation_matrix': corr_matrix,
        'ranking': [{'rank': i+1, 'country': cc, 'f_bias_pct': r.get('f_pct',0),
                     'f_reporter_pct': r.get('f_reporter_pct',0), 'strong': r.get('strong_signals',0)}
                    for i, (cc, r) in enumerate(ranked)],
        'runtime_seconds': round(time.time() - start, 1),
    }
    outfile = OUT_DIR / 'per_country_deep_analysis_v4.json'
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f'\nSaved to {outfile}')
    logger.info(f'Total runtime: {time.time()-start:.1f}s')

if __name__ == '__main__':
    main()
