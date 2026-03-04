#!/usr/bin/env python3
"""
Fast Drug Normalization v2 — Uses FAERS prod_ai + ChEMBL synonym mapping.

Strategy:
1. Use prod_ai column (product active ingredient) — covers 90% of records
2. Build drug synonym dictionary from ChEMBL 36 molecule_synonyms table
3. Apply ChEMBL synonym mapping for remaining unmatched drugs
4. Final fallback: case-normalized drugname

Author: JShaik (jshaik@coevolvenetwork.com)
"""

import json
import logging
import re
import sqlite3
from pathlib import Path

import duckdb
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/drug_normalization_v2.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def clean_name(name: str) -> str:
    """Clean and standardize drug name."""
    if not isinstance(name, str):
        return ""
    name = name.upper().strip()
    name = re.sub(r"\s+", " ", name)
    # Remove dosage info in parentheses
    name = re.sub(r"\s*\(.*?\)\s*", " ", name)
    # Remove common suffixes
    for suffix in [" HYDROCHLORIDE", " HCL", " SODIUM", " POTASSIUM",
                   " MESYLATE", " MALEATE", " TARTRATE", " SULFATE",
                   " FUMARATE", " ACETATE", " SUCCINATE", " BESYLATE",
                   " CITRATE", " PHOSPHATE", " CALCIUM", " MAGNESIUM",
                   " DISODIUM", " DIHYDRATE", " MONOHYDRATE",
                   " EXTENDED RELEASE", " ER", " XR", " SR", " CR",
                   " INJECTION", " TABLET", " CAPSULE", " ORAL"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name.strip()


def build_chembl_synonym_dict(chembl_db_path: str) -> dict:
    """Build drug name -> preferred name dictionary from ChEMBL."""
    logger.info(f"Loading ChEMBL synonym dictionary from {chembl_db_path}")
    try:
        conn = sqlite3.connect(chembl_db_path)
        # Get preferred name for each molecule
        query = """
        SELECT UPPER(ms.synonyms) as synonym, md.pref_name
        FROM molecule_synonyms ms
        JOIN molecule_dictionary md ON ms.molregno = md.molregno
        WHERE md.pref_name IS NOT NULL AND ms.synonyms IS NOT NULL
        """
        df = pd.read_sql(query, conn)
        conn.close()

        synonym_dict = {}
        for _, row in df.iterrows():
            syn = row["synonym"].strip()
            pref = row["pref_name"].strip().upper()
            if syn and pref:
                synonym_dict[syn] = pref

        logger.info(f"Built ChEMBL synonym dictionary with {len(synonym_dict):,} entries")
        return synonym_dict
    except Exception as e:
        logger.error(f"Error loading ChEMBL: {e}")
        return {}


def main():
    input_dir = Path("data/processed/faers_clean")
    chembl_path = Path.home() / "veda-kg/data/chembl/chembl_36/chembl_36_sqlite/chembl_36.db"

    logger.info("=" * 60)
    logger.info("DRUG NORMALIZATION v2 — prod_ai + ChEMBL")
    logger.info("=" * 60)

    # Step 1: Load drug data with DuckDB for speed
    logger.info("Loading drug.parquet...")
    con = duckdb.connect()

    # Build prod_ai mapping: drugname -> most common prod_ai
    logger.info("Building prod_ai mapping...")
    prod_ai_map_df = con.execute("""
        SELECT drugname,
               UPPER(TRIM(prod_ai)) as active_ingredient,
               COUNT(*) as cnt
        FROM read_parquet('data/processed/faers_clean/drug.parquet')
        WHERE prod_ai IS NOT NULL AND prod_ai != ''
        GROUP BY drugname, UPPER(TRIM(prod_ai))
        ORDER BY drugname, cnt DESC
    """).fetchdf()

    # Keep only the most common prod_ai per drugname
    prod_ai_map = {}
    for _, row in prod_ai_map_df.drop_duplicates(subset=["drugname"], keep="first").iterrows():
        prod_ai_map[row["drugname"]] = row["active_ingredient"]

    logger.info(f"prod_ai mapping covers {len(prod_ai_map):,} unique drug names")

    # Step 2: Build ChEMBL synonym dictionary
    chembl_dict = {}
    if chembl_path.exists():
        chembl_dict = build_chembl_synonym_dict(str(chembl_path))
    else:
        logger.warning(f"ChEMBL database not found at {chembl_path}")

    # Step 3: Load full drug dataframe
    logger.info("Loading full drug dataframe...")
    df = pd.read_parquet(input_dir / "drug.parquet")
    logger.info(f"Loaded {len(df):,} drug records")

    # Step 4: Normalize
    logger.info("Applying normalization...")

    # Pre-compute all unique drugnames
    unique_drugs = df["drugname"].dropna().unique()
    logger.info(f"Unique drug names: {len(unique_drugs):,}")

    # Build final mapping: drugname -> (normalized_name, source)
    final_map = {}
    stats = {"prod_ai": 0, "chembl": 0, "cleaned": 0, "raw_upper": 0}

    for drug in unique_drugs:
        # Strategy 1: Use prod_ai if available
        if drug in prod_ai_map:
            final_map[drug] = (prod_ai_map[drug], "prod_ai")
            stats["prod_ai"] += 1
            continue

        # Strategy 2: Try ChEMBL synonym lookup
        drug_upper = drug.upper().strip() if isinstance(drug, str) else ""
        if drug_upper in chembl_dict:
            final_map[drug] = (chembl_dict[drug_upper], "chembl")
            stats["chembl"] += 1
            continue

        # Strategy 3: Clean the name and try ChEMBL again
        drug_cleaned = clean_name(drug)
        if drug_cleaned in chembl_dict:
            final_map[drug] = (chembl_dict[drug_cleaned], "chembl_cleaned")
            stats["chembl"] += 1
            continue

        # Strategy 4: Use cleaned name as fallback
        if drug_cleaned and drug_cleaned != drug_upper:
            final_map[drug] = (drug_cleaned, "cleaned")
            stats["cleaned"] += 1
        else:
            final_map[drug] = (drug_upper, "raw_upper")
            stats["raw_upper"] += 1

    logger.info("=" * 60)
    logger.info("NORMALIZATION STATISTICS")
    logger.info("=" * 60)
    logger.info(f"  prod_ai matches:  {stats['prod_ai']:,} ({stats['prod_ai']/len(unique_drugs)*100:.1f}%)")
    logger.info(f"  ChEMBL matches:   {stats['chembl']:,} ({stats['chembl']/len(unique_drugs)*100:.1f}%)")
    logger.info(f"  Cleaned fallback: {stats['cleaned']:,} ({stats['cleaned']/len(unique_drugs)*100:.1f}%)")
    logger.info(f"  Raw upper only:   {stats['raw_upper']:,} ({stats['raw_upper']/len(unique_drugs)*100:.1f}%)")
    total_mapped = stats["prod_ai"] + stats["chembl"]
    logger.info(f"  Total mapped:     {total_mapped:,} ({total_mapped/len(unique_drugs)*100:.1f}%)")
    logger.info("=" * 60)

    # Apply mapping to dataframe
    logger.info("Applying mapping to dataframe...")
    df["drugname_normalized"] = df["drugname"].map(lambda x: final_map.get(x, (x, "unknown"))[0] if pd.notna(x) else None)
    df["match_source"] = df["drugname"].map(lambda x: final_map.get(x, (x, "unknown"))[1] if pd.notna(x) else None)
    df["rxnorm_cui"] = None  # Not used in this version

    unique_after = df["drugname_normalized"].nunique()
    logger.info(f"Unique normalized drug names: {unique_after:,} (from {len(unique_drugs):,})")

    # Save
    output_file = input_dir / "drug_normalized.parquet"
    logger.info(f"Saving to {output_file}...")
    df.to_parquet(output_file, index=False)
    logger.info(f"Saved {len(df):,} records")

    # Save normalization summary
    summary = {
        "total_records": len(df),
        "unique_raw_drugs": len(unique_drugs),
        "unique_normalized_drugs": unique_after,
        "reduction_ratio": round(1 - unique_after / len(unique_drugs), 3),
        "stats": stats,
        "total_mapped_pct": round(total_mapped / len(unique_drugs) * 100, 1),
    }
    with open(input_dir / "drug_normalization_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("DRUG_NORM_V2_COMPLETE")


if __name__ == "__main__":
    main()
