#!/usr/bin/env python3
"""
SexDiffKG v4 — Step 2: Recompute Sex-Stratified Signals with DiAna-normalized drugs
=====================================================================================
Uses the v4 DiAna-normalized drug names for much better signal quality.
Computes ROR_female, ROR_male, sex-differential ratio for all drug-AE pairs.

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-03
"""

import json, logging, time, math
from pathlib import Path
import pandas as pd
import numpy as np
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/v4_02_compute_signals.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / "sexdiffkg"
DRUG_V4 = BASE / "data/processed/faers_clean/drug_normalized_v4.parquet"
DEMO = BASE / "data/processed/faers_clean/demo.parquet"
REAC = BASE / "data/processed/faers_clean/reac.parquet"
OUT_DIR = BASE / "results/signals_v4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_REPORTS_PER_SEX = 10
LOG_RATIO_THRESHOLD = 0.5


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("SexDiffKG v4 — Sex-Stratified Signal Computation (DiAna-normalized)")
    logger.info("=" * 70)

    con = duckdb.connect()
    con.execute("SET threads=16")
    con.execute("SET memory_limit='80GB'")

    # Load and join: drug (v4 normalized) + demo (sex) + reac (adverse event)
    logger.info("Computing drug-AE-sex contingency tables...")
    
    # Step 1: Count reports per drug-AE-sex combination (primary/secondary suspect drugs only)
    t0 = time.time()
    con.execute(f"""
        CREATE TEMP TABLE drug_ae_sex AS
        SELECT 
            d.drugname_normalized as drug_name,
            r.pt as adverse_event,
            dm.sex,
            COUNT(DISTINCT d.primaryid) as report_count
        FROM read_parquet('{DRUG_V4}') d
        JOIN read_parquet('{DEMO}') dm ON d.primaryid = dm.primaryid
        JOIN read_parquet('{REAC}') r ON d.primaryid = r.primaryid
        WHERE d.role_cod IN ('PS', 'SS')
          AND dm.sex IN ('F', 'M')
          AND d.drugname_normalized IS NOT NULL
          AND d.drugname_normalized != ''
          AND r.pt IS NOT NULL
          AND r.pt != ''
        GROUP BY d.drugname_normalized, r.pt, dm.sex
    """)
    cnt = con.execute("SELECT COUNT(*) FROM drug_ae_sex").fetchone()[0]
    logger.info(f"Drug-AE-sex combinations: {cnt:,} ({time.time()-t0:.1f}s)")

    # Step 2: Compute totals for 2x2 tables
    logger.info("Computing marginal totals...")
    t0 = time.time()
    
    # Total reports per sex
    con.execute(f"""
        CREATE TEMP TABLE sex_totals AS
        SELECT sex, COUNT(DISTINCT primaryid) as N
        FROM read_parquet('{DEMO}')
        WHERE sex IN ('F', 'M')
        GROUP BY sex
    """)
    sex_totals = dict(con.execute("SELECT * FROM sex_totals").fetchall())
    logger.info(f"Total reports: F={sex_totals.get('F',0):,}, M={sex_totals.get('M',0):,}")
    
    # Drug totals per sex
    con.execute(f"""
        CREATE TEMP TABLE drug_sex_totals AS
        SELECT d.drugname_normalized as drug_name, dm.sex,
               COUNT(DISTINCT d.primaryid) as drug_total
        FROM read_parquet('{DRUG_V4}') d
        JOIN read_parquet('{DEMO}') dm ON d.primaryid = dm.primaryid
        WHERE d.role_cod IN ('PS', 'SS') AND dm.sex IN ('F', 'M')
          AND d.drugname_normalized IS NOT NULL
        GROUP BY d.drugname_normalized, dm.sex
    """)
    
    # AE totals per sex
    con.execute(f"""
        CREATE TEMP TABLE ae_sex_totals AS
        SELECT r.pt as adverse_event, dm.sex,
               COUNT(DISTINCT r.primaryid) as ae_total
        FROM read_parquet('{REAC}') r
        JOIN read_parquet('{DEMO}') dm ON r.primaryid = dm.primaryid
        WHERE dm.sex IN ('F', 'M') AND r.pt IS NOT NULL
        GROUP BY r.pt, dm.sex
    """)
    logger.info(f"Marginal totals computed ({time.time()-t0:.1f}s)")

    # Step 3: Compute ROR for each drug-AE-sex triple
    logger.info("Computing ROR with 2x2 contingency tables...")
    t0 = time.time()
    
    con.execute(f"""
        CREATE TEMP TABLE ror_results AS
        SELECT 
            das.drug_name,
            das.adverse_event,
            das.sex,
            das.report_count as a,
            dst.drug_total - das.report_count as b,
            ast.ae_total - das.report_count as c,
            st.N - dst.drug_total - ast.ae_total + das.report_count as d,
            -- ROR = (a*d) / (b*c)
            CASE WHEN (dst.drug_total - das.report_count) > 0 
                  AND (ast.ae_total - das.report_count) > 0
                 THEN (das.report_count::DOUBLE * (st.N - dst.drug_total - ast.ae_total + das.report_count)::DOUBLE) 
                    / ((dst.drug_total - das.report_count)::DOUBLE * (ast.ae_total - das.report_count)::DOUBLE)
                 ELSE NULL END as ror,
            das.report_count as n_reports
        FROM drug_ae_sex das
        JOIN drug_sex_totals dst ON das.drug_name = dst.drug_name AND das.sex = dst.sex
        JOIN ae_sex_totals ast ON das.adverse_event = ast.adverse_event AND das.sex = ast.sex
        JOIN sex_totals st ON das.sex = st.sex
        WHERE das.report_count >= {MIN_REPORTS_PER_SEX}
    """)
    
    ror_count = con.execute("SELECT COUNT(*) FROM ror_results").fetchone()[0]
    logger.info(f"ROR computed for {ror_count:,} drug-AE-sex triples with >={MIN_REPORTS_PER_SEX} reports ({time.time()-t0:.1f}s)")

    # Step 4: Compute sex-differential signals
    logger.info("Computing sex-differential signals...")
    t0 = time.time()
    
    con.execute(f"""
        CREATE TEMP TABLE sex_diff AS
        SELECT 
            f.drug_name,
            f.adverse_event,
            f.ror as ror_female,
            m.ror as ror_male,
            f.n_reports as n_female,
            m.n_reports as n_male,
            LN(f.ror) - LN(m.ror) as log_ratio,
            CASE 
                WHEN LN(f.ror) - LN(m.ror) > {LOG_RATIO_THRESHOLD} THEN 'female_higher'
                WHEN LN(f.ror) - LN(m.ror) < -{LOG_RATIO_THRESHOLD} THEN 'male_higher'
                ELSE 'no_difference'
            END as direction
        FROM ror_results f
        JOIN ror_results m ON f.drug_name = m.drug_name AND f.adverse_event = m.adverse_event
        WHERE f.sex = 'F' AND m.sex = 'M'
          AND f.ror > 0 AND m.ror > 0
          AND f.ror IS NOT NULL AND m.ror IS NOT NULL
    """)
    
    # Get sex-differential signals only
    con.execute("""
        CREATE TEMP TABLE sex_diff_signals AS
        SELECT * FROM sex_diff
        WHERE direction != 'no_difference'
    """)
    
    total_signals = con.execute("SELECT COUNT(*) FROM sex_diff_signals").fetchone()[0]
    f_higher = con.execute("SELECT COUNT(*) FROM sex_diff_signals WHERE direction='female_higher'").fetchone()[0]
    m_higher = con.execute("SELECT COUNT(*) FROM sex_diff_signals WHERE direction='male_higher'").fetchone()[0]
    unique_drugs = con.execute("SELECT COUNT(DISTINCT drug_name) FROM sex_diff_signals").fetchone()[0]
    unique_aes = con.execute("SELECT COUNT(DISTINCT adverse_event) FROM sex_diff_signals").fetchone()[0]
    
    logger.info(f"Sex-differential signals: {total_signals:,}")
    logger.info(f"  Female-higher: {f_higher:,} ({f_higher/max(total_signals,1)*100:.1f}%)")
    logger.info(f"  Male-higher:   {m_higher:,} ({m_higher/max(total_signals,1)*100:.1f}%)")
    logger.info(f"  Unique drugs:  {unique_drugs:,}")
    logger.info(f"  Unique AEs:    {unique_aes:,}")
    logger.info(f"  ({time.time()-t0:.1f}s)")

    # Step 5: Save all ROR results
    logger.info("Saving results...")
    
    # Full ROR by sex
    ror_df = con.execute("SELECT * FROM ror_results ORDER BY drug_name, adverse_event, sex").fetchdf()
    ror_df.to_parquet(OUT_DIR / "ror_by_sex_v4.parquet", index=False)
    logger.info(f"Saved ror_by_sex_v4.parquet: {len(ror_df):,} rows")
    
    # Sex-differential signals
    sig_df = con.execute("SELECT * FROM sex_diff_signals ORDER BY ABS(log_ratio) DESC").fetchdf()
    sig_df.to_parquet(OUT_DIR / "sex_differential_v4.parquet", index=False)
    logger.info(f"Saved sex_differential_v4.parquet: {len(sig_df):,} rows")
    
    # All comparisons (including no_difference)
    all_df = con.execute("SELECT * FROM sex_diff ORDER BY drug_name, adverse_event").fetchdf()
    all_df.to_parquet(OUT_DIR / "all_sex_comparisons_v4.parquet", index=False)
    logger.info(f"Saved all_sex_comparisons_v4.parquet: {len(all_df):,} rows")
    
    # Strong signals (|log_ratio| > 1.0)
    strong = con.execute("SELECT COUNT(*) FROM sex_diff_signals WHERE ABS(log_ratio) > 1.0").fetchone()[0]
    
    elapsed = time.time() - start
    
    summary = {
        "version": "v4_diana",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": {
            "min_reports_per_sex": MIN_REPORTS_PER_SEX,
            "log_ratio_threshold": LOG_RATIO_THRESHOLD,
        },
        "results": {
            "total_ror_computed": int(ror_count),
            "total_sex_differential_signals": int(total_signals),
            "female_higher": int(f_higher),
            "male_higher": int(m_higher),
            "strong_signals_abs_gt_1": int(strong),
            "unique_drugs": int(unique_drugs),
            "unique_adverse_events": int(unique_aes),
        },
        "faers_totals": {k: int(v) for k, v in sex_totals.items()},
        "elapsed_seconds": round(elapsed, 1),
    }
    
    with open(OUT_DIR / "signal_computation_v4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    con.close()
    logger.info(f"Done in {elapsed:.0f}s")
    logger.info("V4_SIGNALS_COMPLETE")


if __name__ == "__main__":
    main()
