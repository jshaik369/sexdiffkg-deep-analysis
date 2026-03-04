#!/usr/bin/env python3
"""
SexDiffKG v4.2 — Step 2b: Sex-Stratified Signal Computation with Quality Controls
==================================================================================
Fixed version of v4_02 that restores quality controls lost from v3:
- P0 FIX: ae_sex_totals and sex_totals now filtered to PS/SS drugs only
- P1 FIX: 95% CI on ROR (Woolf's method)
- P1 FIX: Chi-squared p-values + Benjamini-Hochberg FDR correction
- P2 FIX: Haldane continuity correction for zero cells

Author: J.Shaik (jshaik@coevolvenetwork.com)
Date: 2026-03-04
"""

import json, logging, time
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/v4_02b_compute_signals.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / "sexdiffkg"
DRUG_V4 = BASE / "data/processed/faers_clean/drug_normalized_v4.parquet"
DEMO = BASE / "data/processed/faers_clean/demo.parquet"
REAC = BASE / "data/processed/faers_clean/reac.parquet"
OUT_DIR = BASE / "results" / "signals_v42"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_REPORTS_PER_SEX = 10
LOG_RATIO_THRESHOLD = 0.5


def apply_bh_fdr(p_values, alpha=0.05):
    """Benjamini-Hochberg FDR correction. Returns boolean array of rejections."""
    n = len(p_values)
    if n == 0:
        return np.array([], dtype=bool)

    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    thresholds = np.arange(1, n + 1) / n * alpha

    # Find largest k where p_(k) <= k/m * alpha
    pass_mask = sorted_p <= thresholds
    if pass_mask.any():
        cutoff = np.where(pass_mask)[0][-1]
        rejected = np.zeros(n, dtype=bool)
        rejected[sorted_idx[: cutoff + 1]] = True
    else:
        rejected = np.zeros(n, dtype=bool)

    return rejected


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("SexDiffKG v4.2 — Signal Computation with Quality Controls")
    logger.info("=" * 70)

    con = duckdb.connect()
    con.execute("SET threads=16")
    con.execute("SET memory_limit='80GB'")

    # ===== STEP 1: Drug-AE-sex counts (PS/SS only) =====
    logger.info("Computing drug-AE-sex contingency tables (PS/SS only)...")
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
          AND r.pt IS NOT NULL AND r.pt != ''
        GROUP BY d.drugname_normalized, r.pt, dm.sex
    """)
    cnt = con.execute("SELECT COUNT(*) FROM drug_ae_sex").fetchone()[0]
    logger.info(f"Drug-AE-sex combinations: {cnt:,} ({time.time()-t0:.1f}s)")

    # ===== STEP 2: Marginal totals — ALL FILTERED TO PS/SS =====
    logger.info("Computing marginal totals (PS/SS filtered)...")
    t0 = time.time()

    # P0 FIX: sex_totals now counts only reports with PS/SS drugs
    con.execute(f"""
        CREATE TEMP TABLE sex_totals AS
        SELECT dm.sex, COUNT(DISTINCT dm.primaryid) as N
        FROM read_parquet('{DEMO}') dm
        JOIN read_parquet('{DRUG_V4}') d ON dm.primaryid = d.primaryid
        WHERE dm.sex IN ('F', 'M')
          AND d.role_cod IN ('PS', 'SS')
          AND d.drugname_normalized IS NOT NULL
        GROUP BY dm.sex
    """)
    sex_totals = dict(con.execute("SELECT * FROM sex_totals").fetchall())
    logger.info(f"PS/SS reports: F={sex_totals.get('F',0):,}, M={sex_totals.get('M',0):,}")

    # Drug totals per sex (already correct in v4)
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

    # P0 FIX: ae_sex_totals now filtered to PS/SS drugs
    con.execute(f"""
        CREATE TEMP TABLE ae_sex_totals AS
        SELECT r.pt as adverse_event, dm.sex,
               COUNT(DISTINCT r.primaryid) as ae_total
        FROM read_parquet('{REAC}') r
        JOIN read_parquet('{DEMO}') dm ON r.primaryid = dm.primaryid
        JOIN read_parquet('{DRUG_V4}') d ON r.primaryid = d.primaryid
        WHERE dm.sex IN ('F', 'M')
          AND r.pt IS NOT NULL
          AND d.role_cod IN ('PS', 'SS')
          AND d.drugname_normalized IS NOT NULL
        GROUP BY r.pt, dm.sex
    """)
    logger.info(f"Marginal totals computed ({time.time()-t0:.1f}s)")

    # ===== STEP 3: ROR with CI, chi-squared, Haldane =====
    logger.info("Computing ROR with 95% CI, chi-squared, and Haldane correction...")
    t0 = time.time()

    con.execute(f"""
        CREATE TEMP TABLE ror_results AS
        SELECT
            das.drug_name,
            das.adverse_event,
            das.sex,
            das.report_count as a,
            GREATEST(dst.drug_total - das.report_count, 0) as b,
            GREATEST(ast.ae_total - das.report_count, 0) as c,
            GREATEST(st.N - dst.drug_total - ast.ae_total + das.report_count, 0) as d,
            das.report_count as n_reports,

            -- Haldane-adjusted cells (add 0.5 when any cell is 0)
            CASE WHEN (dst.drug_total - das.report_count) = 0
                   OR (ast.ae_total - das.report_count) = 0
                   OR (st.N - dst.drug_total - ast.ae_total + das.report_count) = 0
                 THEN das.report_count + 0.5 ELSE das.report_count::DOUBLE END as a_h,
            CASE WHEN (dst.drug_total - das.report_count) = 0
                   OR (ast.ae_total - das.report_count) = 0
                   OR (st.N - dst.drug_total - ast.ae_total + das.report_count) = 0
                 THEN GREATEST(dst.drug_total - das.report_count, 0) + 0.5
                 ELSE GREATEST(dst.drug_total - das.report_count, 0)::DOUBLE END as b_h,
            CASE WHEN (dst.drug_total - das.report_count) = 0
                   OR (ast.ae_total - das.report_count) = 0
                   OR (st.N - dst.drug_total - ast.ae_total + das.report_count) = 0
                 THEN GREATEST(ast.ae_total - das.report_count, 0) + 0.5
                 ELSE GREATEST(ast.ae_total - das.report_count, 0)::DOUBLE END as c_h,
            CASE WHEN (dst.drug_total - das.report_count) = 0
                   OR (ast.ae_total - das.report_count) = 0
                   OR (st.N - dst.drug_total - ast.ae_total + das.report_count) = 0
                 THEN GREATEST(st.N - dst.drug_total - ast.ae_total + das.report_count, 0) + 0.5
                 ELSE GREATEST(st.N - dst.drug_total - ast.ae_total + das.report_count, 0)::DOUBLE END as d_h

        FROM drug_ae_sex das
        JOIN drug_sex_totals dst ON das.drug_name = dst.drug_name AND das.sex = dst.sex
        JOIN ae_sex_totals ast ON das.adverse_event = ast.adverse_event AND das.sex = ast.sex
        JOIN sex_totals st ON das.sex = st.sex
        WHERE das.report_count >= {MIN_REPORTS_PER_SEX}
    """)

    ror_count = con.execute("SELECT COUNT(*) FROM ror_results").fetchone()[0]
    logger.info(f"ROR candidates: {ror_count:,} ({time.time()-t0:.1f}s)")

    # Fetch to pandas for CI + chi-squared + FDR
    logger.info("Fetching results for CI, chi-squared, and FDR...")
    t0 = time.time()
    ror_df = con.execute("SELECT * FROM ror_results").df()
    logger.info(f"Fetched {len(ror_df):,} rows ({time.time()-t0:.1f}s)")

    # Compute ROR from Haldane-adjusted cells
    ror_df["ror"] = (ror_df["a_h"] * ror_df["d_h"]) / (ror_df["b_h"] * ror_df["c_h"])

    # 95% CI (Woolf's method)
    ln_ror = np.log(ror_df["ror"])
    se = np.sqrt(1.0 / ror_df["a_h"] + 1.0 / ror_df["b_h"] + 1.0 / ror_df["c_h"] + 1.0 / ror_df["d_h"])
    ror_df["ror_lower"] = np.exp(ln_ror - 1.96 * se)
    ror_df["ror_upper"] = np.exp(ln_ror + 1.96 * se)

    # Chi-squared from original (non-Haldane) cells
    n_total = ror_df["a"] + ror_df["b"] + ror_df["c"] + ror_df["d"]
    ad_bc = ror_df["a"].astype(float) * ror_df["d"].astype(float) - ror_df["b"].astype(float) * ror_df["c"].astype(float)
    denom = (ror_df["a"] + ror_df["b"]).astype(float) * (ror_df["c"] + ror_df["d"]) * (ror_df["a"] + ror_df["c"]) * (ror_df["b"] + ror_df["d"])
    # Avoid division by zero
    denom = denom.replace(0, np.nan)
    ror_df["chi2"] = n_total.astype(float) * (ad_bc ** 2) / denom
    ror_df["p_value"] = 1.0 - scipy_stats.chi2.cdf(ror_df["chi2"].fillna(0), df=1)
    ror_df.loc[ror_df["chi2"].isna(), "p_value"] = 1.0

    # BH FDR correction per sex stratum
    logger.info("Applying Benjamini-Hochberg FDR correction per sex stratum...")
    ror_df["fdr_pass"] = False
    for sex in ["F", "M"]:
        mask = ror_df["sex"] == sex
        p_vals = ror_df.loc[mask, "p_value"].values
        rejected = apply_bh_fdr(p_vals, alpha=0.05)
        ror_df.loc[mask, "fdr_pass"] = rejected
        n_pass = rejected.sum()
        logger.info(f"  {sex}: {n_pass:,} / {len(p_vals):,} pass FDR (alpha=0.05)")

    # Signal flag: triple gate
    ror_df["signal"] = (
        (ror_df["ror_lower"] > 1.0) &
        (ror_df["a"] >= 5) &
        (ror_df["fdr_pass"])
    )
    n_signals = ror_df["signal"].sum()
    logger.info(f"Signals (ror_lower>1 AND a>=5 AND fdr_pass): {n_signals:,}")

    # ===== STEP 4: Sex-differential comparison =====
    logger.info("Computing sex-differential signals...")

    # Pivot to get female and male ROR side by side
    female = ror_df[ror_df["sex"] == "F"].set_index(["drug_name", "adverse_event"])
    male = ror_df[ror_df["sex"] == "M"].set_index(["drug_name", "adverse_event"])

    # Inner join on drug-AE pairs present in both sexes
    both = female.join(male, lsuffix="_f", rsuffix="_m", how="inner")

    # Filter: both must have valid ROR
    both = both[(both["ror_f"] > 0) & (both["ror_m"] > 0)].copy()

    both["log_ratio"] = np.log(both["ror_f"]) - np.log(both["ror_m"])
    both["direction"] = np.where(
        both["log_ratio"] > LOG_RATIO_THRESHOLD, "female_higher",
        np.where(both["log_ratio"] < -LOG_RATIO_THRESHOLD, "male_higher", "no_difference")
    )

    # All sex comparisons
    all_comparisons = both.reset_index()[["drug_name", "adverse_event",
        "ror_f", "ror_m", "ror_lower_f", "ror_upper_f", "ror_lower_m", "ror_upper_m",
        "n_reports_f", "n_reports_m",
        "chi2_f", "p_value_f", "fdr_pass_f",
        "chi2_m", "p_value_m", "fdr_pass_m",
        "signal_f", "signal_m",
        "log_ratio", "direction"]]
    all_comparisons.columns = ["drug_name", "adverse_event",
        "ror_female", "ror_male", "ror_lower_female", "ror_upper_female",
        "ror_lower_male", "ror_upper_male",
        "n_female", "n_male",
        "chi2_female", "p_value_female", "fdr_pass_female",
        "chi2_male", "p_value_male", "fdr_pass_male",
        "signal_female", "signal_male",
        "log_ratio", "direction"]

    # Sex-differential subset
    sex_diff = all_comparisons[all_comparisons["direction"] != "no_difference"].copy()

    total_comparisons = len(all_comparisons)
    total_diff = len(sex_diff)
    f_higher = (sex_diff["direction"] == "female_higher").sum()
    m_higher = (sex_diff["direction"] == "male_higher").sum()
    unique_drugs = sex_diff["drug_name"].nunique()
    unique_aes = sex_diff["adverse_event"].nunique()

    # Strong signals: both sexes pass triple gate AND sex-differential
    sex_diff_both_signal = sex_diff[sex_diff["signal_female"] & sex_diff["signal_male"]]
    logger.info(f"Sex-diff where BOTH sexes are signals: {len(sex_diff_both_signal):,}")

    logger.info(f"\n{'='*50}")
    logger.info(f"RESULTS SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Total comparisons (both sexes >= {MIN_REPORTS_PER_SEX}): {total_comparisons:,}")
    logger.info(f"Sex-differential (|log_ratio| >= {LOG_RATIO_THRESHOLD}): {total_diff:,}")
    logger.info(f"  Female-higher: {f_higher:,} ({100*f_higher/max(total_diff,1):.1f}%)")
    logger.info(f"  Male-higher: {m_higher:,} ({100*m_higher/max(total_diff,1):.1f}%)")
    logger.info(f"Unique drugs: {unique_drugs:,}")
    logger.info(f"Unique adverse events: {unique_aes:,}")

    # ===== STEP 5: Save =====
    logger.info("Saving results...")
    all_comparisons.to_parquet(OUT_DIR / "all_sex_comparisons_v42.parquet", index=False)
    sex_diff.to_parquet(OUT_DIR / "sex_differential_v42.parquet", index=False)

    # Also save per-sex ROR with all QC columns
    ror_out = ror_df[["drug_name", "adverse_event", "sex", "a", "b", "c", "d",
                       "ror", "ror_lower", "ror_upper", "chi2", "p_value",
                       "fdr_pass", "signal", "n_reports"]].copy()
    ror_out.to_parquet(OUT_DIR / "ror_per_sex_v42.parquet", index=False)

    # Summary JSON
    summary = {
        "version": "v4.2_with_qc",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": {
            "min_reports_per_sex": MIN_REPORTS_PER_SEX,
            "log_ratio_threshold": LOG_RATIO_THRESHOLD,
            "fdr_alpha": 0.05,
            "haldane_correction": True,
            "ci_method": "Woolf_95pct",
            "signal_criteria": "ror_lower>1 AND a>=5 AND fdr_pass",
        },
        "fixes_from_v4": [
            "ae_sex_totals filtered to PS/SS drugs (was counting ALL reports)",
            "sex_totals filtered to PS/SS drugs (was counting ALL reports)",
            "Added Haldane continuity correction (0.5 to all cells when any is 0)",
            "Added 95% CI via Woolf method",
            "Added chi-squared p-values",
            "Added BH FDR correction per sex stratum",
            "Added triple-gate signal flag (ror_lower>1 AND a>=5 AND fdr_pass)",
        ],
        "results": {
            "total_comparisons": int(total_comparisons),
            "sex_differential": int(total_diff),
            "female_higher": int(f_higher),
            "male_higher": int(m_higher),
            "unique_drugs": int(unique_drugs),
            "unique_adverse_events": int(unique_aes),
        },
        "ps_ss_report_totals": {k: int(v) for k, v in sex_totals.items()},
        "elapsed_seconds": round(time.time() - start, 1),
    }
    with open(OUT_DIR / "signal_computation_v42_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {OUT_DIR / 'signal_computation_v42_summary.json'}")

    con.close()
    elapsed = time.time() - start
    logger.info(f"\nTotal time: {elapsed:.1f}s")
    logger.info("DONE")


if __name__ == "__main__":
    main()
