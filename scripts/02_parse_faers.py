#!/usr/bin/env python3

"""
Parse FAERS quarterly ASCII ZIP files into Parquet format.

This script processes all ZIP files in the input directory, extracts the 7 tables
(DEMO, DRUG, REAC, OUTC, THER, INDI, RPSR) from the ascii/ subdirectory,
handles both old (2004-2012) and new (2012Q4+) column naming conventions,
consolidates them across quarters, and writes to Parquet format.

Old naming conventions (ISR, CASE, GNDR_COD, DRUG_SEQ, etc.) are normalized to
new conventions (primaryid, caseid, sex, drug_seq, etc.).
"""

import argparse
import json
import logging
import re
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Table names we expect in FAERS data
TABLE_NAMES = ["DEMO", "DRUG", "REAC", "OUTC", "THER", "INDI", "RPSR"]

# Key fields to ensure exist in each table
KEY_FIELDS = {
    "DEMO": ["primaryid", "caseid", "sex", "age", "age_cod", 
             "wt", "wt_cod", "fda_dt", "event_dt"],
    "DRUG": ["primaryid", "drug_seq", "drugname", "role_cod", "route"],
    "REAC": ["primaryid", "pt"],
    "OUTC": [],
    "THER": [],
    "INDI": [],
    "RPSR": [],
}

# Column name mappings from old (pre-2012Q4) to new naming conventions
OLD_TO_NEW_COLUMN_MAPPING = {
    # DEMO table mappings
    "isr": "primaryid",
    "case": "caseid",
    "i_f_cod": "i_f_code",
    "foll_seq": "foll_seq",  # Keep as-is
    "image": "image",  # Keep as-is
    "event_dt": "event_dt",  # Keep as-is
    "mfr_dt": "mfr_dt",  # Keep as-is
    "fda_dt": "fda_dt",  # Keep as-is
    "init_fda_dt": "init_fda_dt",  # Keep as-is
    "rept_cod": "rept_cod",  # Keep as-is
    "mfr_num": "mfr_num",  # Keep as-is
    "mfr_sndr": "mfr_sndr",  # Keep as-is
    "gndr_cod": "sex",
    "e_sub": "e_sub",  # Keep as-is
    "wt": "wt",  # Keep as-is
    "wt_cod": "wt_cod",  # Keep as-is
    "rept_dt": "rept_dt",  # Keep as-is
    "occp_cod": "occp_cod",  # Keep as-is
    "death_dt": "death_dt",  # Keep as-is
    "to_mfr": "to_mfr",  # Keep as-is
    "confid": "confid",  # Keep as-is
    "lit_ref": "lit_ref",  # Keep as-is
    "age": "age",  # Keep as-is
    "age_cod": "age_cod",  # Keep as-is
    "age_grp": "age_grp",  # Keep as-is
    "sex": "sex",  # Already new format
    "reporter_country": "reporter_country",  # Keep as-is
    "occr_country": "occr_country",  # Keep as-is
    # DRUG table mappings
    "drug_seq": "drug_seq",  # Keep as-is (already lowercased in both)
    "role_cod": "role_cod",  # Keep as-is
    "drugname": "drugname",  # Keep as-is
    "prod_ai": "prod_ai",  # Keep as-is
    "val_vbm": "val_vbm",  # Keep as-is
    "route": "route",  # Keep as-is
    "dose_vbm": "dose_vbm",  # Keep as-is
    "cum_dose_chr": "cum_dose_chr",  # Keep as-is
    "cum_dose_unit": "cum_dose_unit",  # Keep as-is
    "dechal": "dechal",  # Keep as-is
    "rechal": "rechal",  # Keep as-is
    "lot_num": "lot_num",  # Keep as-is
    "exp_dt": "exp_dt",  # Keep as-is
    "nda_num": "nda_num",  # Keep as-is
    "dose_amt": "dose_amt",  # Keep as-is
    "dose_unit": "dose_unit",  # Keep as-is
    "dose_form": "dose_form",  # Keep as-is
    "dose_freq": "dose_freq",  # Keep as-is
    # REAC table mappings
    "pt": "pt",  # Keep as-is
}


def extract_quarter_from_zip(zip_path: Path) -> str:
    """
    Extract quarter string (e.g., '2024Q3') from ZIP filename.
    
    Expected formats: FAERSASCII####Q#.ZIP, faersascii####q#.zip, etc.
    """
    match = re.search(r'(\d{2,4})[qQ]([1-4])', zip_path.stem)
    if match:
        year_str = match.group(1)
        quarter = match.group(2)
        # Handle 2-digit years (00-24 maps to 2000-2024)
        if len(year_str) == 2:
            year = 2000 + int(year_str)
        else:
            year = int(year_str)
        return f"{year}Q{quarter}"
    raise ValueError(f"Could not extract quarter from {zip_path.name}")


def find_table_file_in_ascii_dir(
    zip_ref: zipfile.ZipFile,
    table_name: str,
) -> Optional[str]:
    """
    Find the file corresponding to table_name in the ascii/ subdirectory within the ZIP.
    
    Handles case-insensitive matching and various naming conventions
    (e.g., ascii/DEMO12Q4.TXT, ascii/DEMO13Q1.txt, ascii/demo24q1.txt).
    """
    target_pattern = re.compile(
        rf"^{table_name}\d+[qQ]\d[\w]*\.txt$",
        re.IGNORECASE
    )
    
    for name in zip_ref.namelist():
        # Extract just the filename from potential path
        filename = name.split('/')[-1]
        # Look for files in ascii/ subdirectory
        if 'ascii' in name.lower() and target_pattern.match(filename):
            return name
    
    return None


def detect_encoding(file_bytes: bytes) -> str:
    """
    Attempt to detect file encoding (UTF-8 or Latin-1).
    Default to Latin-1 for FAERS files.
    """
    try:
        file_bytes.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        return 'latin-1'


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names:
    1. Convert to lowercase
    2. Strip whitespace
    3. Apply old-to-new mappings (ISR->primaryid, GNDR_COD->sex, etc.)
    """
    # First: lowercase and strip
    df.columns = df.columns.str.lower().str.strip()
    
    # Second: apply mapping for old naming conventions
    rename_dict = {}
    for col in df.columns:
        if col in OLD_TO_NEW_COLUMN_MAPPING:
            new_name = OLD_TO_NEW_COLUMN_MAPPING[col]
            if new_name != col:  # Only rename if different
                rename_dict[col] = new_name
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
        logger.debug(f"Renamed columns: {rename_dict}")
    
    return df


def read_delimited_file(
    file_bytes: bytes,
    encoding: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read a dollar-sign-delimited file into a DataFrame.
    """
    if encoding is None:
        encoding = detect_encoding(file_bytes)
    
    try:
        df = pd.read_csv(
            pd.io.common.BytesIO(file_bytes),
            sep='$',
            dtype=str,
            encoding=encoding,
            encoding_errors='ignore',
            on_bad_lines='skip',
        )
    except Exception as e:
        logger.warning(f"Failed to read with {encoding}: {e}. Retrying with latin-1.")
        df = pd.read_csv(
            pd.io.common.BytesIO(file_bytes),
            sep='$',
            dtype=str,
            encoding='latin-1',
            encoding_errors='ignore',
            on_bad_lines='skip',
        )
    
    # Normalize column names
    df = normalize_column_names(df)
    
    return df


def process_zip_file(
    zip_path: Path,
    quarter: str,
) -> Dict[str, pd.DataFrame]:
    """
    Extract and parse all 7 tables from a single ZIP file.
    Files are expected to be in ascii/ subdirectory.
    """
    tables = {name: None for name in TABLE_NAMES}
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for table_name in TABLE_NAMES:
                file_name = find_table_file_in_ascii_dir(zip_ref, table_name)
                
                if file_name is None:
                    logger.warning(
                        f"Could not find {table_name} file in ascii/ subdirectory "
                        f"of {zip_path.name}"
                    )
                    continue
                
                try:
                    file_bytes = zip_ref.read(file_name)
                    df = read_delimited_file(file_bytes)
                    
                    # Add quarter column
                    df['quarter'] = quarter
                    
                    tables[table_name] = df
                    logger.info(
                        f"Extracted {table_name} from {zip_path.name} ({file_name}): "
                        f"{len(df)} rows, {len(df.columns)} columns"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to process {table_name} from {zip_path.name}: {e}"
                    )
    
    except zipfile.BadZipFile:
        logger.error(f"Bad ZIP file: {zip_path}")
    
    return tables


def consolidate_tables(
    all_quarters_data: Dict[str, List[pd.DataFrame]],
) -> Dict[str, pd.DataFrame]:
    """
    Consolidate all DataFrames for each table type across all quarters.
    """
    consolidated = {}
    
    for table_name in TABLE_NAMES:
        dfs = all_quarters_data.get(table_name, [])
        
        if not dfs:
            logger.warning(f"No data found for table {table_name}")
            consolidated[table_name] = pd.DataFrame()
            continue
        
        # Concatenate all DataFrames for this table
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Ensure all key fields exist (even if empty)
        for key_field in KEY_FIELDS.get(table_name, []):
            if key_field not in combined_df.columns:
                logger.warning(
                    f"Key field '{key_field}' not found in {table_name}. "
                    f"Adding empty column."
                )
                combined_df[key_field] = None
        
        consolidated[table_name] = combined_df
        logger.info(
            f"Consolidated {table_name}: {len(combined_df)} total rows "
            f"from {len(dfs)} quarters"
        )
    
    return consolidated


def write_to_parquet(
    tables: Dict[str, pd.DataFrame],
    output_dir: Path,
) -> Dict[str, Tuple[int, float]]:
    """
    Write consolidated tables to Parquet files using pandas.
    
    Returns: Dict mapping table_name -> (row_count, file_size_mb)
    """
    output_stats = {}
    
    for table_name, df in tables.items():
        if df.empty:
            logger.warning(f"Skipping empty table: {table_name}")
            continue
        
        output_file = output_dir / f"{table_name.lower()}.parquet"
        
        try:
            # Write to Parquet using pandas
            df.to_parquet(output_file, index=False, compression='snappy')
            
            # Get file size
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            row_count = len(df)
            
            output_stats[table_name.lower()] = (row_count, file_size_mb)
            
            logger.info(
                f"Wrote {table_name} to {output_file.name}: "
                f"{row_count} rows, {file_size_mb:.2f} MB"
            )
        
        except Exception as e:
            logger.error(f"Failed to write {table_name} to Parquet: {e}")
    
    return output_stats


def write_checkpoint(
    checkpoint_path: Path,
    processed_zips: Set[str],
) -> None:
    """Write checkpoint JSON tracking which ZIPs have been parsed."""
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "processed_zips": sorted(list(processed_zips)),
        "count": len(processed_zips),
    }
    
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    logger.info(f"Wrote checkpoint to {checkpoint_path}")


def load_checkpoint(checkpoint_path: Path) -> Set[str]:
    """Load previously processed ZIPs from checkpoint."""
    if not checkpoint_path.exists():
        return set()
    
    try:
        with open(checkpoint_path, 'r') as f:
            data = json.load(f)
        return set(data.get("processed_zips", []))
    except Exception as e:
        logger.warning(f"Failed to load checkpoint: {e}")
        return set()


def main(input_dir: Path, output_dir: Path) -> None:
    """Main function to orchestrate FAERS parsing."""
    # Validate input directory
    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Checkpoint file
    checkpoint_path = output_dir / "checkpoint.json"
    processed_zips = load_checkpoint(checkpoint_path)
    
    # Find all ZIP files
    zip_files = sorted(input_dir.glob("*.zip")) + sorted(
        input_dir.glob("*.ZIP")
    )
    zip_files = list(dict.fromkeys(zip_files))  # Remove duplicates
    
    if not zip_files:
        raise ValueError(f"No ZIP files found in {input_dir}")
    
    logger.info(f"Found {len(zip_files)} ZIP files to process")
    
    # Data structure to hold all quarters' data
    all_quarters_data: Dict[str, List[pd.DataFrame]] = {
        name: [] for name in TABLE_NAMES
    }
    
    # Row count tracking per quarter per table
    row_counts_per_quarter: Dict[str, Dict[str, int]] = {}
    
    # Process each ZIP file
    for zip_path in zip_files:
        if zip_path.name in processed_zips:
            logger.info(f"Skipping already processed ZIP: {zip_path.name}")
            continue
        
        try:
            quarter = extract_quarter_from_zip(zip_path)
            logger.info(f"Processing {zip_path.name} ({quarter})")
            
            # Extract tables from ZIP
            tables_from_zip = process_zip_file(zip_path, quarter)
            
            # Aggregate by table type
            for table_name, df in tables_from_zip.items():
                if df is not None and not df.empty:
                    all_quarters_data[table_name].append(df)
                    
                    if quarter not in row_counts_per_quarter:
                        row_counts_per_quarter[quarter] = {}
                    row_counts_per_quarter[quarter][table_name] = len(df)
            
            # Mark as processed
            processed_zips.add(zip_path.name)
            
        except Exception as e:
            logger.error(f"Failed to process {zip_path.name}: {e}")
    
    # Log row counts per quarter
    logger.info("Row counts per quarter per table:")
    for quarter in sorted(row_counts_per_quarter.keys()):
        logger.info(f"  {quarter}:")
        for table_name in TABLE_NAMES:
            count = row_counts_per_quarter[quarter].get(table_name, 0)
            logger.info(f"    {table_name}: {count}")
    
    # Consolidate tables across all quarters
    logger.info("Consolidating tables across all quarters...")
    consolidated_tables = consolidate_tables(all_quarters_data)
    
    # Write to Parquet files
    logger.info("Writing consolidated tables to Parquet...")
    output_stats = write_to_parquet(consolidated_tables, output_dir)
    
    # Write checkpoint
    write_checkpoint(checkpoint_path, processed_zips)
    
    # Final summary
    logger.info("=" * 60)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 60)
    for table_name in TABLE_NAMES:
        table_lower = table_name.lower()
        if table_lower in output_stats:
            row_count, file_size = output_stats[table_lower]
            logger.info(
                f"{table_name}: {row_count:,} rows, {file_size:.2f} MB"
            )
        else:
            logger.info(f"{table_name}: No data")
    
    if output_stats:
        total_rows = sum(count for count, _ in output_stats.values())
        total_size = sum(size for _, size in output_stats.values())
        logger.info(f"Total: {total_rows:,} rows, {total_size:.2f} MB")
    logger.info("=" * 60)
    
    logger.info("Parsing complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse FAERS quarterly ASCII ZIP files into Parquet format"
    )
    
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("/home/jshaik369/sexdiffkg/data/raw/faers"),
        help="Input directory containing FAERS ZIP files",
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/home/jshaik369/sexdiffkg/data/processed/faers"),
        help="Output directory for Parquet files",
    )
    
    args = parser.parse_args()
    
    try:
        main(args.input_dir, args.output_dir)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
