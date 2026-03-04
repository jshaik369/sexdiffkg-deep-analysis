#!/usr/bin/env python3
"""
FAERS Level 1 Deduplication Script

Deduplicates FAERS DEMO table by keeping the latest report per caseid,
then filters related tables (drug, reac) to include only surviving primaryids.
Also filters for valid sex values (M/F only).

Level 1 deduplication logic:
- For each caseid: keep row with latest fda_dt
- If fda_dt tied: keep row with largest primaryid (cast to BIGINT)
- Filter DEMO to sex in ('M', 'F')
- Filter drug and reac to only include surviving primaryids
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import duckdb
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_directories(output_dir: Path) -> None:
    """Create output directory if it doesn't exist."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory ready: {output_dir}")


def load_parquet_files(input_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load parquet files from input directory."""
    demo_path = input_dir / "demo.parquet"
    drug_path = input_dir / "drug.parquet"
    reac_path = input_dir / "reac.parquet"

    logger.info(f"Loading demo.parquet from {demo_path}")
    demo_df = pd.read_parquet(demo_path)

    logger.info(f"Loading drug.parquet from {drug_path}")
    drug_df = pd.read_parquet(drug_path)

    logger.info(f"Loading reac.parquet from {reac_path}")
    reac_df = pd.read_parquet(reac_path)

    return demo_df, drug_df, reac_df


def deduplicate_demo(demo_df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate DEMO table using Level 1 logic:
    - For each caseid, keep row with latest fda_dt
    - If fda_dt tied, keep row with largest primaryid
    - Filter to sex in ('M', 'F')

    Uses DuckDB for efficient in-memory processing.
    """
    logger.info("Starting DEMO deduplication using DuckDB")
    logger.info(f"DEMO before deduplication: {len(demo_df):,} rows")

    # Log sex distribution before filtering
    sex_counts_before = demo_df['sex'].value_counts()
    logger.info(f"Sex distribution before filtering: {sex_counts_before.to_dict()}")

    # Register dataframe with DuckDB
    conn = duckdb.connect(":memory:")
    conn.register("demo", demo_df)

    # Deduplication query:
    # 1. Filter sex to M or F
    # 2. For each caseid, keep row with max fda_dt
    # 3. If fda_dt tied, keep row with max primaryid (cast to BIGINT)
    dedup_query = """
    WITH filtered AS (
        SELECT *
        FROM demo
        WHERE sex IN ('M', 'F')
    ),
    ranked AS (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY caseid
                   ORDER BY fda_dt DESC, CAST(primaryid AS BIGINT) DESC
               ) as rn
        FROM filtered
    )
    SELECT * EXCLUDE (rn)
    FROM ranked
    WHERE rn = 1
    ORDER BY primaryid
    """

    logger.info("Executing deduplication query")
    dedup_demo = conn.execute(dedup_query).df()
    conn.close()

    logger.info(f"DEMO after deduplication: {len(dedup_demo):,} rows")

    # Log sex distribution after deduplication
    sex_counts_after = dedup_demo['sex'].value_counts()
    logger.info(f"Sex distribution after dedup: {sex_counts_after.to_dict()}")

    removal_rate = 1 - (len(dedup_demo) / len(demo_df))
    logger.info(f"Reports removed: {len(demo_df) - len(dedup_demo):,} ({removal_rate*100:.2f}%)")

    return dedup_demo


def filter_related_tables(
    dedup_demo: pd.DataFrame,
    drug_df: pd.DataFrame,
    reac_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Filter drug and reac tables to only include primaryids that survived deduplication.
    """
    surviving_primaryids = set(dedup_demo['primaryid'].unique())
    logger.info(f"Surviving primaryids after dedup: {len(surviving_primaryids):,}")

    # Filter drug table
    logger.info(f"DRUG before filtering: {len(drug_df):,} rows")
    drug_filtered = drug_df[drug_df['primaryid'].isin(surviving_primaryids)].copy()
    logger.info(f"DRUG after filtering: {len(drug_filtered):,} rows")
    drug_removal_rate = 1 - (len(drug_filtered) / len(drug_df))
    logger.info(f"DRUG rows removed: {len(drug_df) - len(drug_filtered):,} ({drug_removal_rate*100:.2f}%)")

    # Filter reac table
    logger.info(f"REAC before filtering: {len(reac_df):,} rows")
    reac_filtered = reac_df[reac_df['primaryid'].isin(surviving_primaryids)].copy()
    logger.info(f"REAC after filtering: {len(reac_filtered):,} rows")
    reac_removal_rate = 1 - (len(reac_filtered) / len(reac_df))
    logger.info(f"REAC rows removed: {len(reac_df) - len(reac_filtered):,} ({reac_removal_rate*100:.2f}%)")

    return drug_filtered, reac_filtered


def write_output_files(
    output_dir: Path,
    demo_dedup: pd.DataFrame,
    drug_filtered: pd.DataFrame,
    reac_filtered: pd.DataFrame
) -> None:
    """Write deduplicated and filtered tables to output directory as Parquet."""
    logger.info("Writing deduplicated files to output directory")

    demo_output = output_dir / "demo.parquet"
    demo_dedup.to_parquet(demo_output, index=False)
    logger.info(f"Wrote DEMO to {demo_output} ({len(demo_dedup):,} rows)")

    drug_output = output_dir / "drug.parquet"
    drug_filtered.to_parquet(drug_output, index=False)
    logger.info(f"Wrote DRUG to {drug_output} ({len(drug_filtered):,} rows)")

    reac_output = output_dir / "reac.parquet"
    reac_filtered.to_parquet(reac_output, index=False)
    logger.info(f"Wrote REAC to {reac_output} ({len(reac_filtered):,} rows)")


def create_checkpoint(
    output_dir: Path,
    original_demo_count: int,
    dedup_demo_count: int,
    original_drug_count: int,
    filtered_drug_count: int,
    original_reac_count: int,
    filtered_reac_count: int,
    sex_distribution_before: Dict[str, int],
    sex_distribution_after: Dict[str, int]
) -> None:
    """Create a checkpoint JSON file with deduplication statistics."""
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "script": "03_deduplicate.py",
        "stage": "level_1_deduplication",
        "demo": {
            "original_count": int(original_demo_count),
            "deduplicated_count": int(dedup_demo_count),
            "removed_count": int(original_demo_count - dedup_demo_count),
            "removal_rate": float((original_demo_count - dedup_demo_count) / original_demo_count)
        },
        "drug": {
            "original_count": int(original_drug_count),
            "filtered_count": int(filtered_drug_count),
            "removed_count": int(original_drug_count - filtered_drug_count),
            "removal_rate": float((original_drug_count - filtered_drug_count) / original_drug_count)
        },
        "reac": {
            "original_count": int(original_reac_count),
            "filtered_count": int(filtered_reac_count),
            "removed_count": int(original_reac_count - filtered_reac_count),
            "removal_rate": float((original_reac_count - filtered_reac_count) / original_reac_count)
        },
        "sex_distribution": {
            "before": {str(k): int(v) for k, v in sex_distribution_before.items()},
            "after": {str(k): int(v) for k, v in sex_distribution_after.items()}
        }
    }

    checkpoint_path = output_dir / "checkpoint.json"
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    logger.info(f"Checkpoint saved to {checkpoint_path}")


def main() -> int:
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="FAERS Level 1 Deduplication: Remove duplicate reports and filter for valid sex"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("/home/jshaik369/sexdiffkg/data/processed/faers"),
        help="Input directory containing demo.parquet, drug.parquet, reac.parquet"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/home/jshaik369/sexdiffkg/data/processed/faers_clean"),
        help="Output directory for deduplicated files"
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("FAERS Level 1 Deduplication")
    logger.info("=" * 80)
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")

    try:
        # Create output directory
        create_directories(args.output_dir)

        # Load input files
        demo_df, drug_df, reac_df = load_parquet_files(args.input_dir)
        logger.info(f"Loaded DEMO: {len(demo_df):,} rows")
        logger.info(f"Loaded DRUG: {len(drug_df):,} rows")
        logger.info(f"Loaded REAC: {len(reac_df):,} rows")

        # Store original counts and sex distribution
        original_demo_count = len(demo_df)
        original_drug_count = len(drug_df)
        original_reac_count = len(reac_df)
        sex_dist_before = demo_df['sex'].value_counts().to_dict()

        # Deduplicate DEMO table
        demo_dedup = deduplicate_demo(demo_df)
        sex_dist_after = demo_dedup['sex'].value_counts().to_dict()

        # Filter DRUG and REAC tables
        drug_filtered, reac_filtered = filter_related_tables(demo_dedup, drug_df, reac_df)

        # Write output files
        write_output_files(args.output_dir, demo_dedup, drug_filtered, reac_filtered)

        # Create checkpoint
        create_checkpoint(
            args.output_dir,
            original_demo_count,
            len(demo_dedup),
            original_drug_count,
            len(drug_filtered),
            original_reac_count,
            len(reac_filtered),
            sex_dist_before,
            sex_dist_after
        )

        logger.info("=" * 80)
        logger.info("Deduplication completed successfully")
        logger.info("=" * 80)
        return 0

    except Exception as e:
        logger.error(f"Error during deduplication: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
