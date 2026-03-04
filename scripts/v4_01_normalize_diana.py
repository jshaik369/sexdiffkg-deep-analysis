#!/usr/bin/env python3
"""
SexDiffKG v4 — Step 1: Drug Normalization with DiAna Dictionary
================================================================
Applies DiAna dictionary (846,917 FAERS drug name mappings, 98.94% coverage)
as primary normalization source, with ChEMBL + prod_ai as fallbacks.

Author: JShaik (jshaik@coevolvenetwork.com)
Date: 2026-03-03
"""

import json, logging, re, sqlite3, time
from pathlib import Path
import pandas as pd
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/v4_01_normalize_diana.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

BASE = Path.home() / "sexdiffkg"
DIANA_CSV = BASE / "data/raw/diana_dict/external_sources/DiAna_dictionary.csv"
CHEMBL_DB = Path.home() / "veda-kg/data/chembl/chembl_36/chembl_36_sqlite/chembl_36.db"
INPUT_DRUG = BASE / "data/processed/faers_clean/drug.parquet"
OUTPUT_DRUG = BASE / "data/processed/faers_clean/drug_normalized_v4.parquet"
OUTPUT_SUMMARY = BASE / "data/processed/faers_clean/drug_normalization_v4_summary.json"


def load_diana_dict():
    """Load DiAna FAERS drug name → active ingredient dictionary."""
    logger.info(f"Loading DiAna dictionary from {DIANA_CSV}")
    df = pd.read_csv(DIANA_CSV, sep=";", dtype=str, on_bad_lines="skip")
    logger.info(f"DiAna raw entries: {len(df):,}")
    
    # Build mapping: lowercase drugname -> uppercase Substance
    diana_map = {}
    for _, row in df.iterrows():
        drugname = str(row.get("drugname", "")).strip()
        substance = str(row.get("Substance", "")).strip()
        if drugname and substance and substance.lower() != "nan":
            diana_map[drugname.upper()] = substance.upper()
    
    logger.info(f"DiAna unique mappings: {len(diana_map):,}")
    return diana_map


def load_chembl_synonyms():
    """Load ChEMBL drug synonyms as fallback."""
    if not CHEMBL_DB.exists():
        logger.warning(f"ChEMBL not found at {CHEMBL_DB}")
        return {}
    
    logger.info(f"Loading ChEMBL synonyms from {CHEMBL_DB}")
    conn = sqlite3.connect(str(CHEMBL_DB))
    query = """
    SELECT UPPER(TRIM(ms.synonyms)) as synonym, UPPER(TRIM(md.pref_name)) as pref_name
    FROM molecule_synonyms ms
    JOIN molecule_dictionary md ON ms.molregno = md.molregno
    WHERE md.pref_name IS NOT NULL AND ms.synonyms IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    chembl_map = {}
    for _, row in df.iterrows():
        syn = row["synonym"].strip()
        pref = row["pref_name"].strip()
        if syn and pref:
            chembl_map[syn] = pref
    
    logger.info(f"ChEMBL synonym entries: {len(chembl_map):,}")
    return chembl_map


def clean_name(name):
    """Basic string cleaning for drug names."""
    if not isinstance(name, str):
        return ""
    name = name.upper().strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\s*\(.*?\)\s*", " ", name)
    for suffix in [" HYDROCHLORIDE", " HCL", " SODIUM", " POTASSIUM",
                   " MESYLATE", " MALEATE", " TARTRATE", " SULFATE",
                   " FUMARATE", " ACETATE", " SUCCINATE", " BESYLATE",
                   " CITRATE", " PHOSPHATE", " CALCIUM", " MAGNESIUM",
                   " EXTENDED RELEASE", " ER", " XR", " SR", " CR",
                   " INJECTION", " TABLET", " CAPSULE", " ORAL",
                   " DISODIUM", " DIHYDRATE", " MONOHYDRATE"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name.strip()


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("SexDiffKG v4 — Drug Normalization with DiAna")
    logger.info("=" * 70)
    
    # Load all dictionaries
    diana_map = load_diana_dict()
    chembl_map = load_chembl_synonyms()
    
    # Load prod_ai mapping from drug.parquet
    logger.info("Building prod_ai mapping...")
    con = duckdb.connect()
    prod_ai_df = con.execute("""
        SELECT drugname,
               UPPER(TRIM(prod_ai)) as active_ingredient,
               COUNT(*) as cnt
        FROM read_parquet(?)
        WHERE prod_ai IS NOT NULL AND prod_ai != ''
        GROUP BY drugname, UPPER(TRIM(prod_ai))
        ORDER BY drugname, cnt DESC
    """, [str(INPUT_DRUG)]).fetchdf()
    
    prod_ai_map = {}
    for _, row in prod_ai_df.drop_duplicates(subset=["drugname"], keep="first").iterrows():
        prod_ai_map[row["drugname"]] = row["active_ingredient"]
    logger.info(f"prod_ai mapping: {len(prod_ai_map):,} entries")
    
    # Load drug dataframe
    logger.info(f"Loading {INPUT_DRUG}...")
    df = pd.read_parquet(INPUT_DRUG)
    logger.info(f"Loaded {len(df):,} drug records")
    
    unique_drugs = df["drugname"].dropna().unique()
    logger.info(f"Unique drug names: {len(unique_drugs):,}")
    
    # 4-tier normalization: DiAna → prod_ai → ChEMBL → string cleaning
    final_map = {}
    stats = {"diana": 0, "prod_ai": 0, "chembl": 0, "cleaned": 0, "raw_upper": 0}
    
    for drug in unique_drugs:
        drug_upper = drug.upper().strip() if isinstance(drug, str) else ""
        
        # Tier 1: DiAna dictionary (highest priority — 98.94% FAERS coverage)
        if drug_upper in diana_map:
            final_map[drug] = (diana_map[drug_upper], "diana")
            stats["diana"] += 1
            continue
        
        # Also try cleaned version in DiAna
        drug_cleaned = clean_name(drug)
        if drug_cleaned in diana_map:
            final_map[drug] = (diana_map[drug_cleaned], "diana")
            stats["diana"] += 1
            continue
        
        # Tier 2: prod_ai from FAERS structured labels
        if drug in prod_ai_map:
            # Cross-check with DiAna: if prod_ai result is in DiAna values, use it
            prod_ai_val = prod_ai_map[drug]
            final_map[drug] = (prod_ai_val, "prod_ai")
            stats["prod_ai"] += 1
            continue
        
        # Tier 3: ChEMBL synonym lookup
        if drug_upper in chembl_map:
            final_map[drug] = (chembl_map[drug_upper], "chembl")
            stats["chembl"] += 1
            continue
        if drug_cleaned in chembl_map:
            final_map[drug] = (chembl_map[drug_cleaned], "chembl")
            stats["chembl"] += 1
            continue
        
        # Tier 4: String cleaning fallback
        if drug_cleaned and drug_cleaned != drug_upper:
            final_map[drug] = (drug_cleaned, "cleaned")
            stats["cleaned"] += 1
        else:
            final_map[drug] = (drug_upper, "raw_upper")
            stats["raw_upper"] += 1
    
    # Report
    logger.info("=" * 70)
    logger.info("NORMALIZATION RESULTS")
    logger.info("=" * 70)
    total = len(unique_drugs)
    for tier, count in stats.items():
        logger.info(f"  {tier:12s}: {count:>8,} ({count/total*100:5.1f}%)")
    mapped = stats["diana"] + stats["prod_ai"] + stats["chembl"]
    logger.info(f"  {'TOTAL MAPPED':12s}: {mapped:>8,} ({mapped/total*100:5.1f}%)")
    logger.info("=" * 70)
    
    # Apply to dataframe
    logger.info("Applying normalization to dataframe...")
    df["drugname_normalized"] = df["drugname"].map(
        lambda x: final_map.get(x, (x, "unknown"))[0] if pd.notna(x) else None
    )
    df["norm_source"] = df["drugname"].map(
        lambda x: final_map.get(x, (x, "unknown"))[1] if pd.notna(x) else None
    )
    
    unique_after = df["drugname_normalized"].nunique()
    logger.info(f"Normalized unique drugs: {unique_after:,} (from {total:,}, {(1-unique_after/total)*100:.1f}% reduction)")
    
    # Save
    logger.info(f"Saving to {OUTPUT_DRUG}...")
    df.to_parquet(OUTPUT_DRUG, index=False)
    
    elapsed = time.time() - start
    
    summary = {
        "version": "v4_diana",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_records": len(df),
        "unique_raw_drugs": int(total),
        "unique_normalized_drugs": int(unique_after),
        "reduction_pct": round((1 - unique_after / total) * 100, 1),
        "stats": {k: int(v) for k, v in stats.items()},
        "total_mapped_pct": round(mapped / total * 100, 1),
        "diana_entries_used": len(diana_map),
        "chembl_entries_used": len(chembl_map),
        "prod_ai_entries_used": len(prod_ai_map),
        "elapsed_seconds": round(elapsed, 1),
    }
    with open(OUTPUT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Done in {elapsed:.0f}s. Summary saved to {OUTPUT_SUMMARY}")
    logger.info("V4_NORMALIZE_COMPLETE")


if __name__ == "__main__":
    main()
