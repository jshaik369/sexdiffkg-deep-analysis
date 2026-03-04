#!/usr/bin/env python3
"""
Compute sex-stratified disproportionality signals from FAERS data.

This module computes ROR (Reporting Odds Ratio), PRR (Proportional Reporting Ratio),
and sex-differential signals for drug-adverse event pairs, stratified by sex.

The analysis applies multiple testing correction (Benjamini-Hochberg FDR) and uses
DuckDB for efficient SQL-based computation on large FAERS datasets.
"""

import argparse
import logging
import math
from pathlib import Path
from typing import Dict, List, Tuple
import sys

import duckdb
import numpy as np
import pandas as pd
from scipy import stats


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Compute sex-stratified disproportionality signals from FAERS data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 04_compute_signals.py
  python 04_compute_signals.py --input-dir /custom/input --output-dir /custom/output
        """
    )
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=Path('/home/jshaik369/sexdiffkg/data/processed/faers_clean'),
        help='Directory containing processed FAERS parquet files'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('/home/jshaik369/sexdiffkg/results/signals'),
        help='Directory for output parquet and CSV files'
    )
    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> None:
    """Validate input directory and files exist."""
    input_dir = args.input_dir
    if not input_dir.is_dir():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    required_files = ['demo.parquet', 'drug_normalized.parquet', 'reac.parquet']
    for fname in required_files:
        fpath = input_dir / fname
        if not fpath.exists():
            logger.error(f"Required file missing: {fpath}")
            sys.exit(1)

    logger.info(f"Input directory: {input_dir}")
    logger.info(f"All required files found")


def setup_output_dir(output_dir: Path) -> None:
    """Create output directory if it doesn't exist."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")


def load_data_to_duckdb(input_dir: Path) -> duckdb.DuckDBPyConnection:
    """Load FAERS data into DuckDB and return connection."""
    logger.info("Loading FAERS data into DuckDB...")
    conn = duckdb.connect(':memory:')

    # Load demo table
    logger.info("Loading demo.parquet...")
    demo = pd.read_parquet(input_dir / 'demo.parquet')
    conn.register('demo', demo)
    logger.info(f"  Loaded {len(demo):,} reports")

    # Load drug_normalized table
    logger.info("Loading drug_normalized.parquet...")
    drug = pd.read_parquet(input_dir / 'drug_normalized.parquet')
    conn.register('drug_normalized', drug)
    logger.info(f"  Loaded {len(drug):,} drug entries")

    # Load reac table
    logger.info("Loading reac.parquet...")
    reac = pd.read_parquet(input_dir / 'reac.parquet')
    conn.register('reac', reac)
    logger.info(f"  Loaded {len(reac):,} adverse event entries")

    return conn


def compute_ror_signals(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Compute ROR, PRR, and signal flags using DuckDB.

    Returns a DataFrame with (drug, ae, sex, a, b, c, d, ROR, ROR_lower, ROR_upper,
    PRR, chi2, p_value, signal_flag).
    """
    logger.info("Computing ROR signals via DuckDB...")

    # One massive SQL query for efficiency
    query = """
    WITH filtered_data AS (
        -- Filter to PS/SS drugs and M/F sex
        SELECT
            d.primaryid,
            COALESCE(d.drugname_normalized, d.drugname) AS drug_name,
            r.pt,
            demo.sex
        FROM drug_normalized d
        INNER JOIN demo ON d.primaryid = demo.primaryid
        INNER JOIN reac r ON d.primaryid = r.primaryid
        WHERE d.role_cod IN ('PS', 'SS')
          AND demo.sex IN ('M', 'F')
    ),
    drug_ae_pairs AS (
        -- All unique drug-AE-sex combinations in data
        SELECT DISTINCT
            drug_name,
            pt,
            sex
        FROM filtered_data
    ),
    contingency_tables AS (
        -- Build 2x2 contingency table for each (drug, AE, sex) triple
        SELECT
            p.drug_name,
            p.pt,
            p.sex,
            -- a: reports with this drug AND this AE in this sex
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM filtered_data fd
                    WHERE fd.drug_name = p.drug_name
                      AND fd.pt = p.pt
                      AND fd.sex = p.sex
                      AND fd.primaryid = filtered_data.primaryid
                )
                THEN filtered_data.primaryid
            END) AS a,
            -- b: reports with this drug AND other AEs in this sex
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM filtered_data fd
                    WHERE fd.drug_name = p.drug_name
                      AND fd.sex = p.sex
                      AND fd.primaryid = filtered_data.primaryid
                )
                AND NOT EXISTS (
                    SELECT 1 FROM filtered_data fd
                    WHERE fd.drug_name = p.drug_name
                      AND fd.pt = p.pt
                      AND fd.sex = p.sex
                      AND fd.primaryid = filtered_data.primaryid
                )
                THEN filtered_data.primaryid
            END) AS b,
            -- c: reports with other drugs AND this AE in this sex
            COUNT(DISTINCT CASE
                WHEN EXISTS (
                    SELECT 1 FROM filtered_data fd
                    WHERE fd.pt = p.pt
                      AND fd.sex = p.sex
                      AND fd.primaryid = filtered_data.primaryid
                )
                AND NOT EXISTS (
                    SELECT 1 FROM filtered_data fd
                    WHERE fd.drug_name = p.drug_name
                      AND fd.sex = p.sex
                      AND fd.primaryid = filtered_data.primaryid
                )
                THEN filtered_data.primaryid
            END) AS c,
            -- d: reports with other drugs AND other AEs in this sex
            COUNT(DISTINCT CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM filtered_data fd
                    WHERE fd.drug_name = p.drug_name
                      AND fd.sex = p.sex
                      AND fd.primaryid = filtered_data.primaryid
                )
                AND NOT EXISTS (
                    SELECT 1 FROM filtered_data fd
                    WHERE fd.pt = p.pt
                      AND fd.sex = p.sex
                      AND fd.primaryid = filtered_data.primaryid
                )
                THEN filtered_data.primaryid
            END) AS d
        FROM drug_ae_pairs p
        CROSS JOIN filtered_data
        GROUP BY p.drug_name, p.pt, p.sex
    )
    SELECT * FROM contingency_tables
    WHERE a > 0;
    """

    # The above SQL is complex due to DuckDB limitations with correlated subqueries.
    # Instead, use a more pragmatic approach: compute in Python after getting the data.
    # Load all filtered data and compute contingency tables in Python for robustness.

    logger.info("Loading filtered data...")
    filtered_query = """
    SELECT
        d.primaryid,
        COALESCE(d.drugname_normalized, d.drugname) AS drug_name,
        r.pt,
        demo.sex
    FROM drug_normalized d
    INNER JOIN demo ON d.primaryid = demo.primaryid
    INNER JOIN reac r ON d.primaryid = r.primaryid
    WHERE d.role_cod IN ('PS', 'SS')
      AND demo.sex IN ('M', 'F')
    """

    filtered_df = conn.execute(filtered_query).fetchdf()
    logger.info(f"Loaded {len(filtered_df):,} drug-AE-sex associations")

    # Compute contingency tables in Python
    logger.info("Computing contingency tables and ROR statistics...")
    signal_results = []

    # Get unique drug-AE-sex combinations
    unique_combinations = filtered_df.groupby(['drug_name', 'pt', 'sex'])['primaryid'].nunique().reset_index()
    unique_combinations.columns = ['drug_name', 'pt', 'sex', 'a']

    # For each combination, compute b, c, d
    all_reports_per_sex = filtered_df.groupby('sex')['primaryid'].nunique().to_dict()
    all_drug_reports_per_sex = filtered_df.groupby(['drug_name', 'sex'])['primaryid'].nunique().reset_index()
    all_drug_reports_per_sex.columns = ['drug_name', 'sex', 'drug_reports']
    all_ae_reports_per_sex = filtered_df.groupby(['pt', 'sex'])['primaryid'].nunique().reset_index()
    all_ae_reports_per_sex.columns = ['pt', 'sex', 'ae_reports']

    for _, row in unique_combinations.iterrows():
        drug_name = row['drug_name']
        ae_pt = row['pt']
        sex = row['sex']
        a = int(row['a'])

        if a < 1:
            continue

        # Get b: drug + other AEs in this sex
        drug_reports = all_drug_reports_per_sex[
            (all_drug_reports_per_sex['drug_name'] == drug_name) &
            (all_drug_reports_per_sex['sex'] == sex)
        ]['drug_reports'].values
        b = int(drug_reports[0] - a) if len(drug_reports) > 0 else 0

        # Get c: other drugs + this AE in this sex
        ae_reports = all_ae_reports_per_sex[
            (all_ae_reports_per_sex['pt'] == ae_pt) &
            (all_ae_reports_per_sex['sex'] == sex)
        ]['ae_reports'].values
        c = int(ae_reports[0] - a) if len(ae_reports) > 0 else 0

        # Get d: other drugs + other AEs in this sex
        total_reports = all_reports_per_sex[sex]
        d = int(total_reports - a - b - c)

        # Ensure all values are non-negative
        if b < 0 or c < 0 or d < 0:
            continue

        # Compute ROR and PRR
        ror, ror_lower, ror_upper = compute_ror(a, b, c, d)
        prr, chi2, p_value = compute_prr(a, b, c, d)

        signal_results.append({
            'drug_name': drug_name,
            'pt': ae_pt,
            'sex': sex,
            'a': a,
            'b': b,
            'c': c,
            'd': d,
            'ror': ror,
            'ror_lower': ror_lower,
            'ror_upper': ror_upper,
            'prr': prr,
            'chi2': chi2,
            'p_value': p_value,
        })

    signal_df = pd.DataFrame(signal_results)
    logger.info(f"Computed {len(signal_df):,} drug-AE-sex combinations")

    return signal_df


def compute_ror(a: int, b: int, c: int, d: int) -> Tuple[float, float, float]:
    """
    Compute ROR (Reporting Odds Ratio) with 95% CI.

    ROR = (a*d) / (b*c)
    95% CI: exp(ln(ROR) ± 1.96 * sqrt(1/a + 1/b + 1/c + 1/d))

    Args:
        a: drug + AE
        b: drug + other AE
        c: other drug + AE
        d: other drug + other AE

    Returns:
        (ROR, lower_CI, upper_CI)
    """
    if b == 0 or c == 0:
        # Handle zero cells: use small pseudocount
        a_adj = a if a > 0 else 1
        b_adj = b if b > 0 else 0.5
        c_adj = c if c > 0 else 0.5
        d_adj = d if d > 0 else 1
    else:
        a_adj, b_adj, c_adj, d_adj = float(a), float(b), float(c), float(d)

    ror = (a_adj * d_adj) / (b_adj * c_adj)

    if ror <= 0:
        return np.nan, np.nan, np.nan

    ln_ror = math.log(ror)
    se_ln_ror = math.sqrt(1.0 / a_adj + 1.0 / b_adj + 1.0 / c_adj + 1.0 / d_adj)
    ci_width = 1.96 * se_ln_ror

    ror_lower = math.exp(ln_ror - ci_width)
    ror_upper = math.exp(ln_ror + ci_width)

    return ror, ror_lower, ror_upper


def compute_prr(a: int, b: int, c: int, d: int) -> Tuple[float, float, float]:
    """
    Compute PRR (Proportional Reporting Ratio) with chi-squared test.

    PRR = [a/(a+b)] / [c/(c+d)]
    Chi-squared: ((a+b+c+d) * (a*d - b*c)^2) / ((a+b)*(c+d)*(a+c)*(b+d))

    Args:
        a: drug + AE
        b: drug + other AE
        c: other drug + AE
        d: other drug + other AE

    Returns:
        (PRR, chi2_statistic, p_value)
    """
    if (a + b) <= 0 or (c + d) <= 0 or (a + c) <= 0 or (b + d) <= 0:
        return np.nan, np.nan, np.nan

    try:
        prr = (a / (a + b)) / (c / (c + d))
    except (ZeroDivisionError, FloatingPointError):
        return np.nan, np.nan, np.nan

    # Chi-squared statistic
    n = a + b + c + d
    numerator = (a * d - b * c) ** 2
    denominator = (a + b) * (c + d) * (a + c) * (b + d)

    if denominator == 0:
        chi2 = np.nan
        p_value = np.nan
    else:
        chi2 = n * numerator / denominator
        p_value = 1.0 - stats.chi2.cdf(chi2, df=1)

    return prr, chi2, p_value


def apply_fdr_correction(signal_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply Benjamini-Hochberg FDR correction separately within each sex stratum.

    Signals are identified as: ROR_lower > 1 AND a >= 5
    FDR correction applied to p_values within each sex.

    Args:
        signal_df: DataFrame with ROR results

    Returns:
        DataFrame with added 'signal_flag' column
    """
    logger.info("Applying Benjamini-Hochberg FDR correction...")

    signal_df['signal_flag'] = False

    for sex in signal_df['sex'].unique():
        sex_mask = signal_df['sex'] == sex
        sex_data = signal_df[sex_mask].copy()

        # Remove NaN p-values for FDR calculation
        valid_p_mask = ~sex_data['p_value'].isna()
        valid_indices = sex_data[valid_p_mask].index

        if len(valid_indices) == 0:
            continue

        p_values = signal_df.loc[valid_indices, 'p_value'].values
        # BH FDR correction at q=0.05
        rejected, corrected_p, _, _ = statsmodels_fdr(p_values, alpha=0.05)

        # Update signal_flag for this sex stratum
        for i, idx in enumerate(valid_indices):
            ror_lower = signal_df.loc[idx, 'ror_lower']
            a = signal_df.loc[idx, 'a']
            fdr_pass = rejected[i]

            # Signal if: ROR_lower > 1 AND a >= 5 AND FDR-corrected
            if not np.isnan(ror_lower) and ror_lower > 1.0 and a >= 5 and fdr_pass:
                signal_df.loc[idx, 'signal_flag'] = True

    logger.info(f"Identified {signal_df['signal_flag'].sum():,} signals after FDR correction")

    return signal_df


def statsmodels_fdr(p_values: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray, float, str]:
    """
    Benjamini-Hochberg FDR control.

    Args:
        p_values: array of p-values
        alpha: FDR threshold (default 0.05)

    Returns:
        (rejected, corrected_p_values, threshold, method)
    """
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # BH threshold: p(i) <= (i/m)*alpha, where i is rank
    m = n
    ranks = np.arange(1, n + 1)
    thresholds = (ranks / m) * alpha

    # Find largest i where p(i) <= (i/m)*alpha
    mask = sorted_p <= thresholds
    if np.any(mask):
        threshold_idx = np.where(mask)[0][-1]
        threshold = thresholds[threshold_idx]
    else:
        threshold = 0.0

    # Map back to original order
    rejected = np.zeros(n, dtype=bool)
    rejected[sorted_indices[:threshold_idx + 1 if np.any(mask) else 0]] = True

    corrected_p = np.minimum.accumulate(sorted_p[::-1])[::-1]
    corrected_p = np.minimum(corrected_p * (m / ranks), 1.0)
    corrected_p_orig = np.empty(n)
    corrected_p_orig[sorted_indices] = corrected_p

    return rejected, corrected_p_orig, threshold, "Benjamini-Hochberg"


def compute_sex_differential_signals(signal_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute sex-differential signals for drug-AE pairs with signals in both sexes.

    For each (drug, AE) pair with signals in both M and F:
        log_ror_ratio = log(ROR_female) - log(ROR_male)
        direction: 'F>M' if positive, 'M>F' if negative

    Args:
        signal_df: DataFrame with ROR results and signal_flag

    Returns:
        DataFrame with sex-differential signals
    """
    logger.info("Computing sex-differential signals...")

    # Filter to signals only
    signals = signal_df[signal_df['signal_flag']].copy()

    # Get unique drug-AE pairs with signals
    drug_ae_pairs = signals.groupby(['drug_name', 'pt'])['sex'].apply(set).reset_index()

    # Find pairs with signals in both sexes
    both_sexes = drug_ae_pairs[
        drug_ae_pairs['sex'].apply(lambda x: 'M' in x and 'F' in x)
    ][['drug_name', 'pt']].copy()

    logger.info(f"Found {len(both_sexes):,} drug-AE pairs with signals in both sexes")

    sex_diff_results = []

    for _, row in both_sexes.iterrows():
        drug_name = row['drug_name']
        ae_pt = row['pt']

        # Get ROR for M and F
        male_row = signals[
            (signals['drug_name'] == drug_name) &
            (signals['pt'] == ae_pt) &
            (signals['sex'] == 'M')
        ]
        female_row = signals[
            (signals['drug_name'] == drug_name) &
            (signals['pt'] == ae_pt) &
            (signals['sex'] == 'F')
        ]

        if len(male_row) == 0 or len(female_row) == 0:
            continue

        ror_male = male_row['ror'].values[0]
        ror_female = female_row['ror'].values[0]

        # Skip if either ROR is NaN or <= 0
        if np.isnan(ror_male) or np.isnan(ror_female) or ror_male <= 0 or ror_female <= 0:
            continue

        log_ror_ratio = math.log(ror_female) - math.log(ror_male)
        direction = 'F>M' if log_ror_ratio > 0 else 'M>F'

        sex_diff_results.append({
            'drug_name': drug_name,
            'pt': ae_pt,
            'ror_male': ror_male,
            'ror_female': ror_female,
            'log_ror_ratio': log_ror_ratio,
            'direction': direction,
        })

    sex_diff_df = pd.DataFrame(sex_diff_results)
    logger.info(f"Computed {len(sex_diff_df):,} sex-differential signals")

    return sex_diff_df


def save_results(
    signal_df: pd.DataFrame,
    sex_diff_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Save results to output files."""
    logger.info("Saving results...")

    # ROR by sex
    ror_output = output_dir / 'ror_by_sex.parquet'
    signal_df.to_parquet(ror_output, index=False)
    logger.info(f"Saved {len(signal_df):,} ROR results to {ror_output}")

    # Sex-differential signals
    sex_diff_output = output_dir / 'sex_differential.parquet'
    sex_diff_df.to_parquet(sex_diff_output, index=False)
    logger.info(f"Saved {len(sex_diff_df):,} sex-differential signals to {sex_diff_output}")

    # Top 100 signals (CSV, human-readable)
    if len(sex_diff_df) > 0:
        top_signals = sex_diff_df.copy()
        top_signals['abs_log_ror_ratio'] = top_signals['log_ror_ratio'].abs()
        top_signals = top_signals.sort_values('abs_log_ror_ratio', ascending=False).head(100)
        top_signals = top_signals[[
            'drug_name', 'pt', 'ror_male', 'ror_female',
            'log_ror_ratio', 'direction'
        ]].copy()
        top_signals.columns = [
            'Drug', 'Adverse Event', 'ROR (Male)', 'ROR (Female)',
            'Log ROR Ratio', 'Direction'
        ]
        top_signals['ROR (Male)'] = top_signals['ROR (Male)'].round(3)
        top_signals['ROR (Female)'] = top_signals['ROR (Female)'].round(3)
        top_signals['Log ROR Ratio'] = top_signals['Log ROR Ratio'].round(4)

        csv_output = output_dir / 'top_signals.csv'
        top_signals.to_csv(csv_output, index=False)
        logger.info(f"Saved top 100 signals to {csv_output}")


def print_summary_log(
    signal_df: pd.DataFrame,
    sex_diff_df: pd.DataFrame,
) -> None:
    """Print summary statistics."""
    logger.info("=" * 80)
    logger.info("SUMMARY STATISTICS")
    logger.info("=" * 80)

    total_drug_ae_pairs = signal_df.groupby(['drug_name', 'pt']).ngroups
    logger.info(f"Total drug-AE pairs analyzed: {total_drug_ae_pairs:,}")

    signals_male = signal_df[(signal_df['sex'] == 'M') & (signal_df['signal_flag'])].shape[0]
    signals_female = signal_df[(signal_df['sex'] == 'F') & (signal_df['signal_flag'])].shape[0]
    logger.info(f"Signals identified (M): {signals_male:,}")
    logger.info(f"Signals identified (F): {signals_female:,}")

    logger.info(f"Sex-differential drug-AE pairs: {len(sex_diff_df):,}")

    if len(sex_diff_df) > 0:
        logger.info("\nTop 10 sex-differential signals (by |log_ror_ratio|):")
        top_10 = sex_diff_df.copy()
        top_10['abs_log_ror_ratio'] = top_10['log_ror_ratio'].abs()
        top_10 = top_10.sort_values('abs_log_ror_ratio', ascending=False).head(10)

        for idx, (_, row) in enumerate(top_10.iterrows(), 1):
            logger.info(
                f"  {idx}. {row['drug_name']} - {row['pt']} | "
                f"M={row['ror_male']:.3f} F={row['ror_female']:.3f} | "
                f"log_ratio={row['log_ror_ratio']:.4f} ({row['direction']})"
            )

    logger.info("=" * 80)


def main() -> None:
    """Main execution function."""
    logger.info("Starting sex-stratified disproportionality signal computation")

    # Parse arguments
    args = setup_arguments()

    # Validate inputs
    validate_inputs(args)
    setup_output_dir(args.output_dir)

    # Load data
    conn = load_data_to_duckdb(args.input_dir)

    # Compute ROR signals
    signal_df = compute_ror_signals(conn)

    if len(signal_df) == 0:
        logger.error("No valid signal data computed. Exiting.")
        sys.exit(1)

    # Apply FDR correction
    signal_df = apply_fdr_correction(signal_df)

    # Compute sex-differential signals
    sex_diff_df = compute_sex_differential_signals(signal_df)

    # Save results
    save_results(signal_df, sex_diff_df, args.output_dir)

    # Print summary
    print_summary_log(signal_df, sex_diff_df)

    logger.info("Computation complete")


if __name__ == '__main__':
    main()
