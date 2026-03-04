#!/usr/bin/env python3
"""
Fast sex-stratified disproportionality signal computation using pure DuckDB SQL.
Replaces the slow row-by-row Python approach.
"""
import argparse
import logging
import math
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data/processed/faers_clean")
    parser.add_argument("--output-dir", default="results/signals")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(":memory:")
    # Allow more memory usage
    conn.execute("SET memory_limit='80GB'")
    conn.execute("SET threads TO 8")

    logger.info("Loading data...")
    demo = pd.read_parquet(input_dir / "demo.parquet")
    conn.register("demo", demo)
    logger.info(f"  DEMO: {len(demo):,} rows")

    drug = pd.read_parquet(input_dir / "drug_normalized.parquet")
    conn.register("drug", drug)
    logger.info(f"  DRUG: {len(drug):,} rows")

    reac = pd.read_parquet(input_dir / "reac.parquet")
    conn.register("reac", reac)
    logger.info(f"  REAC: {len(reac):,} rows")

    # ---- Step 1: ROR by sex using pure SQL ----
    logger.info("Computing ROR by sex (pure SQL)...")
    ror_query = """
    WITH base AS (
        SELECT DISTINCT
            COALESCE(dr.drugname_normalized, dr.drugname) AS drug_name,
            r.pt AS pt,
            d.sex AS sex,
            d.primaryid
        FROM demo d
        JOIN drug dr ON d.primaryid = dr.primaryid
        JOIN reac r ON d.primaryid = r.primaryid
        WHERE d.sex IN ('M', 'F')
          AND dr.drugname IS NOT NULL
          AND r.pt IS NOT NULL
    ),
    -- Count reports per drug-AE-sex (a)
    drug_ae_sex AS (
        SELECT drug_name, pt, sex, COUNT(DISTINCT primaryid) AS a
        FROM base
        GROUP BY drug_name, pt, sex
        HAVING COUNT(DISTINCT primaryid) >= 3
    ),
    -- Total reports per sex
    total_per_sex AS (
        SELECT sex, COUNT(DISTINCT primaryid) AS N
        FROM base
        GROUP BY sex
    ),
    -- Drug totals per sex (a+b)
    drug_per_sex AS (
        SELECT drug_name, sex, COUNT(DISTINCT primaryid) AS drug_total
        FROM base
        GROUP BY drug_name, sex
    ),
    -- AE totals per sex (a+c)
    ae_per_sex AS (
        SELECT pt, sex, COUNT(DISTINCT primaryid) AS ae_total
        FROM base
        GROUP BY pt, sex
    ),
    -- Assemble contingency table
    contingency AS (
        SELECT
            das.drug_name,
            das.pt,
            das.sex,
            das.a,
            (dps.drug_total - das.a) AS b,
            (aps.ae_total - das.a) AS c,
            (tps.N - dps.drug_total - aps.ae_total + das.a) AS d
        FROM drug_ae_sex das
        JOIN drug_per_sex dps ON das.drug_name = dps.drug_name AND das.sex = dps.sex
        JOIN ae_per_sex aps ON das.pt = aps.pt AND das.sex = aps.sex
        JOIN total_per_sex tps ON das.sex = tps.sex
    )
    SELECT
        drug_name, pt, sex, a, b, c, d,
        CASE WHEN b > 0 AND c > 0 THEN (CAST(a AS DOUBLE) * d) / (CAST(b AS DOUBLE) * c) ELSE NULL END AS ror,
        CASE WHEN b > 0 AND c > 0 AND a > 0 AND d > 0
             THEN EXP(LN((CAST(a AS DOUBLE) * d) / (CAST(b AS DOUBLE) * c)) - 1.96 * SQRT(1.0/a + 1.0/b + 1.0/c + 1.0/d))
             ELSE NULL END AS ror_lower,
        CASE WHEN b > 0 AND c > 0 AND a > 0 AND d > 0
             THEN EXP(LN((CAST(a AS DOUBLE) * d) / (CAST(b AS DOUBLE) * c)) + 1.96 * SQRT(1.0/a + 1.0/b + 1.0/c + 1.0/d))
             ELSE NULL END AS ror_upper
    FROM contingency
    WHERE b >= 0 AND c >= 0 AND d >= 0
    ORDER BY drug_name, pt, sex
    """

    logger.info("Executing ROR query...")
    ror_df = conn.execute(ror_query).df()
    logger.info(f"ROR results: {len(ror_df):,} drug-AE-sex combinations")

    # Flag signals: ROR lower CI > 1 means statistically significant
    ror_df["signal"] = ror_df["ror_lower"] > 1.0

    # Save ROR by sex
    ror_file = output_dir / "ror_by_sex.parquet"
    ror_df.to_parquet(ror_file, index=False)
    logger.info(f"Saved ROR by sex: {ror_file} ({len(ror_df):,} rows)")

    signals_count = ror_df["signal"].sum()
    logger.info(f"Significant signals (ROR lower CI > 1): {signals_count:,}")

    # ---- Step 2: Sex-differential signals ----
    logger.info("Computing sex-differential signals...")

    # Pivot to get male and female ROR side by side
    male = ror_df[ror_df["sex"] == "M"][["drug_name", "pt", "ror", "a"]].rename(
        columns={"ror": "ror_male", "a": "a_male"}
    )
    female = ror_df[ror_df["sex"] == "F"][["drug_name", "pt", "ror", "a"]].rename(
        columns={"ror": "ror_female", "a": "a_female"}
    )

    both = male.merge(female, on=["drug_name", "pt"], how="inner")

    # Compute log ratio
    both["log_ror_ratio"] = np.where(
        (both["ror_male"] > 0) & (both["ror_female"] > 0),
        np.log(both["ror_female"] / both["ror_male"]),
        np.nan
    )

    # Direction
    both["direction"] = np.where(
        both["log_ror_ratio"] > 0, "female_higher",
        np.where(both["log_ror_ratio"] < 0, "male_higher", "equal")
    )

    # Minimum report count for reliability
    both["min_reports"] = both[["a_male", "a_female"]].min(axis=1)

    # Filter: at least 10 reports in each sex + abs log ratio > 0.5
    sex_diff = both[
        (both["min_reports"] >= 10) & (both["log_ror_ratio"].abs() > 0.5)
    ].sort_values("log_ror_ratio", key=abs, ascending=False)

    sex_diff_file = output_dir / "sex_differential.parquet"
    sex_diff.to_parquet(sex_diff_file, index=False)
    logger.info(f"Saved sex-differential signals: {sex_diff_file} ({len(sex_diff):,} rows)")

    female_higher = (sex_diff["direction"] == "female_higher").sum()
    male_higher = (sex_diff["direction"] == "male_higher").sum()
    logger.info(f"  Female higher risk: {female_higher:,}")
    logger.info(f"  Male higher risk: {male_higher:,}")

    # Top 10 strongest sex-differential signals
    logger.info("Top 10 sex-differential signals:")
    for _, row in sex_diff.head(10).iterrows():
        logger.info(f"  {row['drug_name']} → {row['pt']}: "
                     f"log_ratio={row['log_ror_ratio']:.2f} ({row['direction']})")

    conn.close()
    logger.info("Signal computation COMPLETE")

if __name__ == "__main__":
    main()
