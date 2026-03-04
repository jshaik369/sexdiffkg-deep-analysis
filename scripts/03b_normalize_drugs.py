#!/usr/bin/env python3
"""
FAERS Drug Name Normalization Script

Normalizes free-text drug names in FAERS to standardized active ingredients using:
1. DiAna dictionary approach (if available from GitHub)
2. RxNorm API fallback for unmatched drugs
3. Rate-limited API calls with checkpoint system

Author: FAERS Processing Pipeline
Date: 2026-02-26
"""

import argparse
import csv
import json
import logging
import re
import time
from collections import Counter
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import duckdb
import pandas as pd
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("drug_normalization.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DrugNormalizer:
    """Normalizes FAERS drug names using DiAna dictionary and RxNorm API."""

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        checkpoint_interval: int = 100,
        rate_limit_delay: float = 0.05,
    ):
        """
        Initialize the drug normalizer.

        Args:
            input_dir: Directory containing drug.parquet
            output_dir: Directory to save normalized output
            checkpoint_interval: Save progress every N API lookups
            rate_limit_delay: Delay between API calls (seconds)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.checkpoint_interval = checkpoint_interval
        self.rate_limit_delay = rate_limit_delay

        self.diana_dict: Dict[str, str] = {}
        self.rxnorm_cache: Dict[str, Dict] = {}
        self.checkpoint_file = self.output_dir / "drug_normalization_checkpoint.json"

        # RxNorm API endpoints
        self.rxnav_approximate_url = (
            "https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
        )
        self.rxnav_related_url = "https://rxnav.nlm.nih.gov/REST/rxcui"

        # Load checkpoint if exists
        self._load_checkpoint()

    def _load_checkpoint(self) -> None:
        """Load checkpoint data from previous runs."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, "r") as f:
                    checkpoint = json.load(f)
                    self.rxnorm_cache = checkpoint.get("rxnorm_cache", {})
                    logger.info(
                        f"Loaded checkpoint with {len(self.rxnorm_cache)} cached entries"
                    )
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")

    def _save_checkpoint(self) -> None:
        """Save current progress to checkpoint file."""
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump({"rxnorm_cache": self.rxnorm_cache}, f, indent=2)
                logger.info(
                    f"Saved checkpoint with {len(self.rxnorm_cache)} cached entries"
                )
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def download_diana_dictionary(self) -> bool:
        """
        Download DiAna drug dictionary from GitHub.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Attempting to download DiAna dictionary from GitHub...")
        try:
            # DiAna package repository
            repo_url = "https://raw.githubusercontent.com/fusarolimichele/DiAna_package/main"

            # Try multiple possible file locations in the repo
            possible_files = [
                f"{repo_url}/data/drug_mapping.csv",
                f"{repo_url}/data/drug_mapping.tsv",
                f"{repo_url}/data/DiAna_dict.csv",
                f"{repo_url}/data/DiAna_dict.tsv",
                f"{repo_url}/DiAna_dict.csv",
                f"{repo_url}/drug_mapping.csv",
            ]

            for url in possible_files:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"Successfully downloaded DiAna dictionary from {url}")
                        self._parse_diana_dictionary(response.text, url)
                        return True
                except Exception as e:
                    logger.debug(f"Failed to fetch from {url}: {e}")
                    continue

            logger.warning("DiAna dictionary not found in GitHub repository")
            return False

        except Exception as e:
            logger.error(f"Error downloading DiAna dictionary: {e}")
            return False

    def _parse_diana_dictionary(self, content: str, source_url: str) -> None:
        """
        Parse DiAna dictionary content.

        Args:
            content: Raw file content
            source_url: Source URL for logging
        """
        try:
            # Detect delimiter (CSV or TSV)
            delimiter = "\t" if "\t" in content.split("\n")[0] else ","

            reader = csv.DictReader(StringIO(content), delimiter=delimiter)
            count = 0

            for row in reader:
                # Try common column names for raw and normalized drug names
                raw_name = (
                    row.get("raw_drugname")
                    or row.get("drugname")
                    or row.get("drug_name")
                    or row.get("original_name")
                )
                normalized_name = (
                    row.get("active_ingredient")
                    or row.get("normalized_drugname")
                    or row.get("ingredient")
                    or row.get("standardized_name")
                )

                if raw_name and normalized_name:
                    # Clean and store mapping
                    raw_clean = self._clean_drug_name(raw_name)
                    self.diana_dict[raw_clean] = normalized_name.strip()
                    count += 1

            logger.info(f"Loaded {count} drug mappings from DiAna dictionary")

        except Exception as e:
            logger.error(f"Error parsing DiAna dictionary: {e}")

    def _clean_drug_name(self, drug_name: str) -> str:
        """
        Clean and standardize drug names.

        Args:
            drug_name: Raw drug name

        Returns:
            Cleaned drug name
        """
        if not isinstance(drug_name, str):
            return ""

        # Convert to uppercase
        name = drug_name.upper().strip()

        # Remove extra whitespace
        name = re.sub(r"\s+", " ", name)

        # Remove special characters except hyphens and parentheses
        name = re.sub(r"[^\w\s\-\(\)]", "", name)

        # Standardize common abbreviations
        abbreviations = {
            r"\bHCL\b": "HYDROCHLORIDE",
            r"\bHCL\b": "HYDROCHLORIDE",
            r"\bNACL\b": "SODIUM CHLORIDE",
            r"\bMG\b": "MILLIGRAM",
            r"\bIU\b": "INTERNATIONAL UNIT",
            r"\bUSP\b": "",
            r"\bBP\b": "",
            r"\bEP\b": "",
            r"\bNF\b": "",
        }

        for abbrev, expansion in abbreviations.items():
            name = re.sub(abbrev, expansion, name)

        # Remove trailing whitespace after abbreviation replacements
        name = name.strip()

        return name

    def query_rxnorm_approximate_term(self, drug_name: str) -> Optional[Dict]:
        """
        Query RxNorm API for approximate drug term match.

        Args:
            drug_name: Drug name to search

        Returns:
            Dictionary with RXCUI and preferred name, or None if not found
        """
        try:
            params = {"term": drug_name, "maxEntries": 1}
            response = requests.get(
                self.rxnav_approximate_url, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if (
                "approximateGroup" in data
                and data["approximateGroup"]["candidate"]
            ):
                candidate = data["approximateGroup"]["candidate"][0]
                return {
                    "rxcui": candidate.get("rxcui"),
                    "name": candidate.get("name"),
                }

            return None

        except Exception as e:
            logger.warning(f"Error querying RxNorm for '{drug_name}': {e}")
            return None

    def get_rxnorm_active_ingredient(self, rxcui: str) -> Optional[str]:
        """
        Get active ingredient for RXCUI from RxNorm.

        Args:
            rxcui: RxNorm CUI identifier

        Returns:
            Active ingredient name, or None if not found
        """
        try:
            url = f"{self.rxnav_related_url}/{rxcui}/related.json"
            params = {"tty": "IN"}  # IN = Ingredient
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "relatedGroup" in data and data["relatedGroup"]["conceptGroup"]:
                for group in data["relatedGroup"]["conceptGroup"]:
                    if group.get("tty") == "IN" and group.get("conceptProperties"):
                        ingredient = group["conceptProperties"][0]
                        return ingredient.get("name")

            return None

        except Exception as e:
            logger.warning(f"Error querying RxNorm for RXCUI {rxcui}: {e}")
            return None

    def normalize_drug_names(self, drugs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize drug names using DiAna dictionary and RxNorm API.

        Args:
            drugs_df: DataFrame with drug information

        Returns:
            DataFrame with normalized drug columns added
        """
        logger.info(f"Starting normalization of {len(drugs_df)} drug records")

        # Initialize result columns
        drugs_df["drugname_normalized"] = None
        drugs_df["rxnorm_cui"] = None
        drugs_df["match_source"] = None

        # Get unique drug names
        unique_drugs = drugs_df["drugname"].dropna().unique()
        logger.info(f"Found {len(unique_drugs)} unique drug names")

        # Track statistics
        diana_matches = 0
        rxnorm_matches = 0
        unmatched = []

        # Process each unique drug name
        for idx, drug_name in enumerate(unique_drugs):
            if pd.isna(drug_name):
                continue

            drug_clean = self._clean_drug_name(drug_name)

            # Try DiAna dictionary first
            if drug_clean in self.diana_dict:
                normalized = self.diana_dict[drug_clean]
                diana_matches += 1
                match_source = "diana"

            # Try RxNorm API
            elif drug_clean in self.rxnorm_cache:
                result = self.rxnorm_cache[drug_clean]
                normalized = result.get("normalized_name")
                rxcui = result.get("rxcui")
                rxnorm_matches += 1
                match_source = "rxnorm"

            else:
                # Query RxNorm API for new entries
                logger.info(f"Querying RxNorm for: {drug_clean}")
                approximate_match = self.query_rxnorm_approximate_term(drug_clean)

                if approximate_match:
                    rxcui = approximate_match.get("rxcui")
                    # Try to get active ingredient
                    active_ingredient = self.get_rxnorm_active_ingredient(rxcui)

                    if active_ingredient:
                        normalized = active_ingredient
                    else:
                        normalized = approximate_match.get("name")

                    # Cache result
                    self.rxnorm_cache[drug_clean] = {
                        "normalized_name": normalized,
                        "rxcui": rxcui,
                    }
                    rxnorm_matches += 1
                    match_source = "rxnorm"
                else:
                    normalized = None
                    rxcui = None
                    match_source = "unmatched"
                    unmatched.append(drug_name)

                # Apply rate limiting
                time.sleep(self.rate_limit_delay)

                # Save checkpoint periodically
                if (idx + 1) % self.checkpoint_interval == 0:
                    logger.info(f"Checkpoint: Processed {idx + 1} unique drugs")
                    self._save_checkpoint()

            # Update dataframe rows matching this drug name
            mask = drugs_df["drugname"] == drug_name
            drugs_df.loc[mask, "drugname_normalized"] = normalized
            if match_source == "rxnorm" and drug_clean in self.rxnorm_cache:
                drugs_df.loc[mask, "rxnorm_cui"] = self.rxnorm_cache[drug_clean].get(
                    "rxcui"
                )
            drugs_df.loc[mask, "match_source"] = match_source

        # Final checkpoint
        self._save_checkpoint()

        # Log statistics
        total_matched = diana_matches + rxnorm_matches
        match_rate = (total_matched / len(unique_drugs)) * 100 if unique_drugs.size > 0 else 0

        logger.info("=" * 60)
        logger.info("DRUG NORMALIZATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total unique drug names: {len(unique_drugs)}")
        logger.info(f"DiAna dictionary matches: {diana_matches}")
        logger.info(f"RxNorm API matches: {rxnorm_matches}")
        logger.info(f"Unmatched drugs: {len(unmatched)}")
        logger.info(f"Overall match rate: {match_rate:.1f}%")
        logger.info("=" * 60)

        # Log top 20 unmatched drugs
        if unmatched:
            unmatched_counter = Counter(unmatched)
            logger.info("Top 20 unmatched drug names:")
            for drug, count in unmatched_counter.most_common(20):
                logger.info(f"  {drug}: {count} occurrences")

        return drugs_df

    def process(self) -> None:
        """Main processing pipeline."""
        logger.info(f"Starting drug normalization pipeline")
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")

        # Load input data
        input_file = self.input_dir / "drug.parquet"
        if not input_file.exists():
            logger.error(f"Input file not found: {input_file}")
            raise FileNotFoundError(f"Drug parquet file not found: {input_file}")

        logger.info(f"Loading drug data from {input_file}")
        drugs_df = pd.read_parquet(input_file)
        logger.info(
            f"Loaded {len(drugs_df)} drug records with columns: {list(drugs_df.columns)}"
        )

        # Download DiAna dictionary
        diana_success = self.download_diana_dictionary()
        if diana_success:
            logger.info(f"Using DiAna dictionary with {len(self.diana_dict)} mappings")
        else:
            logger.info("DiAna dictionary not available, will rely on RxNorm API")

        # Normalize drug names
        normalized_df = self.normalize_drug_names(drugs_df)

        # Save normalized output
        output_file = self.output_dir / "drug_normalized.parquet"
        logger.info(f"Saving normalized drug data to {output_file}")
        normalized_df.to_parquet(output_file, index=False)
        logger.info(f"Successfully saved {len(normalized_df)} records")

        logger.info("Drug normalization pipeline completed successfully")


def main():
    """Entry point for the script."""
    parser = argparse.ArgumentParser(
        description="FAERS Drug Name Normalization using DiAna Dictionary and RxNorm API"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="/home/jshaik369/sexdiffkg/data/processed/faers_clean",
        help="Input directory containing drug.parquet",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/home/jshaik369/sexdiffkg/data/processed/faers_clean",
        help="Output directory for normalized drug data",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=100,
        help="Save checkpoint every N API lookups",
    )
    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=0.05,
        help="Delay between API calls in seconds (max 20/sec = 0.05s)",
    )

    args = parser.parse_args()

    # Create normalizer and process
    normalizer = DrugNormalizer(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        checkpoint_interval=args.checkpoint_interval,
        rate_limit_delay=args.rate_limit_delay,
    )
    normalizer.process()


if __name__ == "__main__":
    main()
