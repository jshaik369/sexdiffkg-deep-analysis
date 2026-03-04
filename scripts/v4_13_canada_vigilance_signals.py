#!/usr/bin/env python3
"""Canada Vigilance Sex-Differential Signals - Fixed column mapping
Author: JShaik | Date: 2026-03-04"""
import json, logging, time
from pathlib import Path
import duckdb

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('logs/v4_13_canada_vigilance.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

BASE = Path.home() / 'sexdiffkg'
CV = BASE / 'data/raw/international/canada_cvass/extracted/cvponline_extract_20241130'
OUT = BASE / 'results/analysis'
MIN_R = 5; LR = 0.5

def main():
    start = time.time()
    logger.info('='*70)
    logger.info('Canada Vigilance Sex-Differential Signal Analysis')
    logger.info('='*70)
    con = duckdb.connect()
    con.execute('SET threads=16; SET memory_limit=\'80GB\'')

    # Reports: column00=report_id, column10=gender_eng
    logger.info('Loading reports...')
    con.execute(f"""CREATE TABLE rpt AS SELECT * FROM read_csv('{CV}/reports.txt',
        delim='$', header=false, auto_detect=true, null_padding=true, ignore_errors=true)""")
    n_all = con.execute('SELECT COUNT(*) FROM rpt').fetchone()[0]
    sex_dist = con.execute("SELECT column10, COUNT(*) FROM rpt GROUP BY column10 ORDER BY COUNT(*) DESC").fetchall()
    logger.info(f'Total reports: {n_all:,}')
    for s, n in sex_dist: logger.info(f'  {s}: {n:,}')

    con.execute("""CREATE TABLE demo AS
        SELECT CAST(column00 AS VARCHAR) as rid,
               CASE WHEN column10='Female' THEN 'F' WHEN column10='Male' THEN 'M' ELSE NULL END as sex
        FROM rpt WHERE column10 IN ('Female','Male')""")
    n_s = con.execute('SELECT COUNT(*) FROM demo').fetchone()[0]
    n_f = con.execute("SELECT COUNT(*) FROM demo WHERE sex='F'").fetchone()[0]
    n_m = con.execute("SELECT COUNT(*) FROM demo WHERE sex='M'").fetchone()[0]
    logger.info(f'Sexed: {n_s:,} (F={n_f:,} [{n_f/n_s*100:.1f}%], M={n_m:,})')

    # Reactions: column1=report_id, column5=pt_name_eng
    logger.info('Loading reactions...')
    con.execute(f"""CREATE TABLE reac AS SELECT * FROM read_csv('{CV}/reactions.txt',
        delim='$', header=false, auto_detect=true, null_padding=true, ignore_errors=true)""")
    n_r = con.execute('SELECT COUNT(*) FROM reac').fetchone()[0]
    logger.info(f'Reactions: {n_r:,}')

    # Drugs: column01=report_id, column03=drugname, column04=involvement
    logger.info('Loading drugs...')
    con.execute(f"""CREATE TABLE drug AS SELECT * FROM read_csv('{CV}/report_drug.txt',
        delim='$', header=false, auto_detect=true, null_padding=true, ignore_errors=true)""")
    n_d = con.execute('SELECT COUNT(*) FROM drug').fetchone()[0]
    inv = con.execute("SELECT column04, COUNT(*) FROM drug GROUP BY column04 ORDER BY COUNT(*) DESC LIMIT 5").fetchall()
    logger.info(f'Drug links: {n_d:,}')
    for i, n in inv: logger.info(f'  {i}: {n:,}')

    # Drug-AE-sex counts (Suspect drugs only)
    logger.info('Computing drug-AE-sex counts...')
    con.execute(f"""CREATE TABLE das AS
        SELECT UPPER(d.column03) as drug_name, UPPER(r.column5) as ae, dm.sex,
               COUNT(DISTINCT CAST(d.column01 AS VARCHAR)) as rc
        FROM drug d
        JOIN demo dm ON CAST(d.column01 AS VARCHAR) = dm.rid
        JOIN reac r ON CAST(d.column01 AS VARCHAR) = CAST(r.column1 AS VARCHAR)
        WHERE d.column04 = 'Suspect'
          AND d.column03 IS NOT NULL AND d.column03 != ''
          AND r.column5 IS NOT NULL AND r.column5 != ''
        GROUP BY UPPER(d.column03), UPPER(r.column5), dm.sex""")
    logger.info(f'DAS combos: {con.execute("SELECT COUNT(*) FROM das").fetchone()[0]:,}')

    # Marginals
    con.execute(f"""CREATE TABLE dst AS
        SELECT UPPER(d.column03) as drug_name, dm.sex,
               COUNT(DISTINCT CAST(d.column01 AS VARCHAR)) as dt
        FROM drug d JOIN demo dm ON CAST(d.column01 AS VARCHAR) = dm.rid
        WHERE d.column04='Suspect' AND d.column03 IS NOT NULL
        GROUP BY UPPER(d.column03), dm.sex""")
    con.execute(f"""CREATE TABLE ast AS
        SELECT UPPER(r.column5) as ae, dm.sex,
               COUNT(DISTINCT CAST(r.column1 AS VARCHAR)) as at
        FROM reac r JOIN demo dm ON CAST(r.column1 AS VARCHAR) = dm.rid
        WHERE r.column5 IS NOT NULL
        GROUP BY UPPER(r.column5), dm.sex""")
    con.execute("CREATE TABLE st AS SELECT sex, COUNT(DISTINCT rid) as N FROM demo GROUP BY sex")

    # ROR
    logger.info('Computing ROR...')
    con.execute(f"""CREATE TABLE ror AS
        SELECT das.drug_name, das.ae, das.sex, das.rc as a,
            CASE WHEN (dst.dt - das.rc) > 0 AND (ast.at - das.rc) > 0
                 THEN (das.rc::DOUBLE * (st.N - dst.dt - ast.at + das.rc)::DOUBLE)
                    / ((dst.dt - das.rc)::DOUBLE * (ast.at - das.rc)::DOUBLE)
                 ELSE NULL END as ror
        FROM das JOIN dst ON das.drug_name=dst.drug_name AND das.sex=dst.sex
        JOIN ast ON das.ae=ast.ae AND das.sex=ast.sex
        JOIN st ON das.sex=st.sex
        WHERE das.rc >= {MIN_R}""")

    # Sex-differential signals
    con.execute(f"""CREATE TABLE sig AS
        SELECT f.drug_name, f.ae, f.ror as rf, f.a as nf, m.ror as rm, m.a as nm,
            LN(f.ror / m.ror) as lr,
            CASE WHEN LN(f.ror / m.ror) > 0 THEN 'female' ELSE 'male' END as dir
        FROM ror f JOIN ror m ON f.drug_name=m.drug_name AND f.ae=m.ae
        WHERE f.sex='F' AND m.sex='M' AND f.ror>0 AND m.ror>0
          AND f.ror IS NOT NULL AND m.ror IS NOT NULL""")

    total = con.execute('SELECT COUNT(*) FROM sig').fetchone()[0]
    strong = con.execute(f"SELECT COUNT(*) FROM sig WHERE ABS(lr)>={LR}").fetchone()[0]
    fb = con.execute(f"SELECT COUNT(*) FROM sig WHERE lr>={LR}").fetchone()[0]
    mb = con.execute(f"SELECT COUNT(*) FROM sig WHERE lr<=-{LR}").fetchone()[0]
    mlr = con.execute('SELECT AVG(lr) FROM sig').fetchone()[0]
    ud = con.execute('SELECT COUNT(DISTINCT drug_name) FROM sig').fetchone()[0]
    ua = con.execute('SELECT COUNT(DISTINCT ae) FROM sig').fetchone()[0]

    logger.info(f'=== RESULTS ===')
    logger.info(f'Total signals: {total:,}')
    logger.info(f'Strong: {strong:,} (F={fb:,} [{fb/strong*100:.1f}%], M={mb:,})')
    logger.info(f'Mean LR: {mlr:.4f}')
    logger.info(f'Unique drugs: {ud:,}, AEs: {ua:,}')

    # FAERS cross-reference
    logger.info('FAERS cross-reference...')
    xref = {}
    try:
        con.execute(f"""CREATE TABLE fsig AS SELECT drug_name, adverse_event, log_ror_ratio, direction
            FROM read_parquet('{BASE}/results/signals_v2/sex_differential.parquet')""")
        con.execute(f"""CREATE TABLE xr AS
            SELECT c.drug_name, c.ae, c.lr as cv, c.dir as cd,
                   f.log_ror_ratio as fl, f.direction as fd
            FROM sig c JOIN fsig f ON c.drug_name=UPPER(f.drug_name) AND c.ae=UPPER(f.adverse_event)
            WHERE ABS(c.lr)>={LR} AND ABS(f.log_ror_ratio)>={LR}""")
        no = con.execute('SELECT COUNT(*) FROM xr').fetchone()[0]
        ns = con.execute("SELECT COUNT(*) FROM xr WHERE cd=fd").fetchone()[0]
        cr = con.execute("SELECT CORR(cv,fl) FROM xr").fetchone()[0]
        xref = {'overlap': no, 'same_dir': ns,
                'agreement': round(ns/no*100,1) if no else 0,
                'pearson_r': round(cr,4) if cr else None}
        logger.info(f'Overlap: {no:,}, same dir: {ns:,} ({ns/no*100:.1f}%), r={cr:.4f}' if no and cr else f'Overlap: {no}')
    except Exception as e:
        logger.warning(f'FAERS xref failed: {e}')
        xref = {'error': str(e)}

    # Top drugs
    top = con.execute(f"""SELECT drug_name, COUNT(*), SUM(CASE WHEN dir='female' THEN 1 ELSE 0 END),
        SUM(CASE WHEN dir='male' THEN 1 ELSE 0 END), AVG(lr)
        FROM sig WHERE ABS(lr)>={LR} GROUP BY drug_name HAVING COUNT(*)>=5
        ORDER BY COUNT(*) DESC LIMIT 30""").fetchall()

    results = {
        'analysis': 'Canada Vigilance Sex-Differential Signals', 'date': '2026-03-04',
        'reports': {'total': n_all, 'with_sex': n_s, 'female': n_f, 'male': n_m,
                    'f_pct': round(n_f/n_s*100,1)},
        'reactions': n_r, 'drug_links': n_d, 'unique_drugs': ud, 'unique_aes': ua,
        'signals': {'total': total, 'strong': strong, 'fb': fb, 'mb': mb,
                    'f_pct': round(fb/strong*100,1) if strong else 0,
                    'mean_lr': round(mlr,4) if mlr else None},
        'faers_xref': xref,
        'top_drugs': [{'drug':r[0],'n':r[1],'fb':r[2],'mb':r[3],'mlr':round(r[4],4)} for r in top],
        'runtime': round(time.time()-start,1),
    }
    with open(OUT / 'canada_vigilance_signals_v4.json', 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f'Saved. Runtime: {time.time()-start:.1f}s')

if __name__ == '__main__':
    main()
