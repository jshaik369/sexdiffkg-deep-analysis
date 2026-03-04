#!/usr/bin/env python3
"""
Validate SexDiffKG against known sex-differential drug safety benchmarks.

Uses 15 well-established drug-sex-AE pairs from published literature
to assess whether the knowledge graph correctly captures known signals.

References:
    - Zucker & Prendergast (2020) Biology of Sex Differences
    - Anderson (2005) J Am Med Womens Assoc  
    - Rosano et al. (2015) Pharmacol Res
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# =============================================================================
# 15 BENCHMARK DRUG-SEX-AE PAIRS
# Each: (drug, adverse_event, expected_direction, literature_source)
# direction: "F>M" = higher risk in females, "M>F" = higher risk in males
# =============================================================================
BENCHMARKS = [
    # 1. QT prolongation: Women have ~2x risk from QT-prolonging drugs
    ("METHADONE", "QT PROLONGED", "F>M",
     "Roden DM. NEJM 2004; Makkar RR et al. JAMA 1993"),
    # 2. ACE inhibitor cough: Women have 2-3x higher incidence
    ("ENALAPRIL", "COUGH", "F>M",
     "Israili ZH & Hall WD. Ann Intern Med 1992"),
    # 3. Drug-induced Long QT from erythromycin
    ("ERYTHROMYCIN", "QT PROLONGED", "F>M",
     "Drici MD et al. Clin Pharmacol Ther 1998"),
    # 4. Fluoroquinolone tendon rupture: Slightly higher in males
    ("LEVOFLOXACIN", "TENDON RUPTURE", "M>F",
     "van der Linden PD et al. Arthritis Rheum 2003"),
    # 5. Statin myopathy: More common in women
    ("ATORVASTATIN", "RHABDOMYOLYSIS", "F>M",
     "Rosenson RS. Am J Med 2004"),
    # 6. NSAID GI bleeding: Higher risk in males historically
    ("ASPIRIN", "GASTROINTESTINAL HAEMORRHAGE", "M>F",
     "Garcia Rodriguez LA. Lancet 2001"),
    # 7. Drug-induced liver injury from amoxicillin-clavulanate: Higher in males
    ("AMOXICILLIN", "DRUG-INDUCED LIVER INJURY", "M>F",
     "Lucena MI et al. Gastroenterology 2009"),
    # 8. TdP from sotalol: Women at higher risk
    ("SOTALOL", "TORSADE DE POINTES", "F>M",
     "Makkar RR et al. JAMA 1993"),
    # 9. SSRI hyponatremia: More common in elderly women
    ("FLUOXETINE", "HYPONATRAEMIA", "F>M",
     "Movig KL et al. Br J Clin Pharmacol 2002"),
    # 10. Opioid respiratory depression: Some evidence for sex diff
    ("MORPHINE", "RESPIRATORY DEPRESSION", "F>M",
     "Sarton E et al. Anesthesiology 2000"),
    # 11. Warfarin bleeding: Women generally more sensitive
    ("WARFARIN", "HAEMORRHAGE", "F>M",
     "Krecic-Shepard ME et al. Clin Pharmacol Ther 2004"),
    # 12. Digoxin toxicity: Higher mortality in women
    ("DIGOXIN", "CARDIAC ARREST", "F>M",
     "Rathore SS et al. NEJM 2002"),
    # 13. Diuretic hypokalemia: More common in women
    ("HYDROCHLOROTHIAZIDE", "HYPOKALAEMIA", "F>M",
     "Clayton JA & Collins FS. Nature 2014"),
    # 14. Zolpidem next-morning impairment: Higher in women (FDA halved dose)
    ("ZOLPIDEM", "SOMNOLENCE", "F>M",
     "FDA Safety Communication 2013"),
    # 15. Trastuzumab cardiotoxicity: Almost exclusively in females (breast cancer)
    ("TRASTUZUMAB", "CARDIOMYOPATHY", "F>M",
     "Seidman A et al. J Clin Oncol 2002"),
]


def load_signals(signals_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the sex-stratified signals and sex-differential signals."""
    ror_file = signals_dir / "ror_by_sex.parquet"
    sexdiff_file = signals_dir / "sex_differential.parquet"

    ror_df = pd.DataFrame()
    sexdiff_df = pd.DataFrame()

    if ror_file.exists():
        ror_df = pd.read_parquet(ror_file)
        logger.info(f"Loaded {len(ror_df):,} ROR signals")
    else:
        logger.warning(f"ROR file not found: {ror_file}")

    if sexdiff_file.exists():
        sexdiff_df = pd.read_parquet(sexdiff_file)
        logger.info(f"Loaded {len(sexdiff_df):,} sex-differential signals")
    else:
        logger.warning(f"Sex-differential file not found: {sexdiff_file}")

    return ror_df, sexdiff_df


def normalize_name(name: str) -> str:
    """Normalize drug/AE name for matching."""
    return name.upper().strip()


def fuzzy_match(query: str, candidates: pd.Series) -> Optional[str]:
    """Find the best fuzzy match for a drug/AE name."""
    query = normalize_name(query)

    # Exact match
    exact = candidates[candidates.str.upper() == query]
    if len(exact) > 0:
        return exact.iloc[0]

    # Substring match
    contains = candidates[candidates.str.upper().str.contains(query, na=False)]
    if len(contains) > 0:
        return contains.iloc[0]

    # Reverse substring match
    for candidate in candidates:
        if candidate and normalize_name(candidate) in query:
            return candidate

    return None


def validate_benchmark(
    drug: str,
    ae: str,
    expected_direction: str,
    source: str,
    ror_df: pd.DataFrame,
    sexdiff_df: pd.DataFrame,
) -> Dict:
    """Validate a single benchmark pair."""
    result = {
        "drug": drug,
        "adverse_event": ae,
        "expected_direction": expected_direction,
        "literature_source": source,
        "found_in_ror": False,
        "found_in_sexdiff": False,
        "observed_direction": None,
        "log_ror_ratio": None,
        "ror_male": None,
        "ror_female": None,
        "direction_correct": False,
        "status": "NOT_FOUND",
    }

    # Search in sex-differential signals
    if len(sexdiff_df) > 0:
        drug_match = fuzzy_match(drug, sexdiff_df["drug_name"])
        if drug_match:
            drug_rows = sexdiff_df[sexdiff_df["drug_name"] == drug_match]
            ae_match = fuzzy_match(ae, drug_rows["pt"])
            if ae_match:
                match_row = drug_rows[drug_rows["pt"] == ae_match].iloc[0]
                result["found_in_sexdiff"] = True
                result["observed_direction"] = match_row["direction"]
                result["log_ror_ratio"] = round(match_row["log_ror_ratio"], 4)
                result["ror_male"] = round(match_row["ror_male"], 3)
                result["ror_female"] = round(match_row["ror_female"], 3)
                # Map benchmark directions to signal directions
                dir_map = {"F>M": "female_higher", "M>F": "male_higher"}
                expected_mapped = dir_map.get(expected_direction, expected_direction)
                result["direction_correct"] = (
                    match_row["direction"] == expected_mapped
                )
                result["status"] = (
                    "CORRECT" if result["direction_correct"] else "WRONG_DIRECTION"
                )
                result["matched_drug"] = drug_match
                result["matched_ae"] = ae_match

    # Search in ROR signals (for coverage even if not in sexdiff)
    if len(ror_df) > 0 and not result["found_in_sexdiff"]:
        drug_match = fuzzy_match(drug, ror_df["drug_name"])
        if drug_match:
            drug_rows = ror_df[ror_df["drug_name"] == drug_match]
            ae_match = fuzzy_match(ae, drug_rows["pt"])
            if ae_match:
                result["found_in_ror"] = True
                result["status"] = "IN_ROR_ONLY"
                result["matched_drug"] = drug_match
                result["matched_ae"] = ae_match

    return result


def run_validation(signals_dir: Path, output_dir: Path) -> Dict:
    """Run full benchmark validation."""
    logger.info("=" * 60)
    logger.info("SexDiffKG BENCHMARK VALIDATION")
    logger.info("=" * 60)

    ror_df, sexdiff_df = load_signals(signals_dir)

    results = []
    for drug, ae, direction, source in BENCHMARKS:
        result = validate_benchmark(drug, ae, direction, source, ror_df, sexdiff_df)
        results.append(result)
        status_icon = {
            "CORRECT": "✓",
            "WRONG_DIRECTION": "✗",
            "IN_ROR_ONLY": "~",
            "NOT_FOUND": "?",
        }.get(result["status"], "?")
        obs = result.get("observed_direction", "")
        obs_str = f", got {obs}" if obs else ""
        logger.info(
            f"  [{status_icon}] {drug} → {ae}: {result['status']}"
            f" (expected {direction}{obs_str})"
        )

    # Summary statistics
    total = len(results)
    correct = sum(1 for r in results if r["status"] == "CORRECT")
    wrong_dir = sum(1 for r in results if r["status"] == "WRONG_DIRECTION")
    ror_only = sum(1 for r in results if r["status"] == "IN_ROR_ONLY")
    not_found = sum(1 for r in results if r["status"] == "NOT_FOUND")
    found = correct + wrong_dir  # found in sex-differential signals
    coverage = found / total if total > 0 else 0
    precision = correct / found if found > 0 else 0

    summary = {
        "total_benchmarks": total,
        "correct_direction": correct,
        "wrong_direction": wrong_dir,
        "in_ror_only": ror_only,
        "not_found": not_found,
        "coverage": round(coverage, 3),
        "directional_precision": round(precision, 3),
    }

    logger.info("")
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Total benchmarks: {total}")
    logger.info(f"  Correct direction: {correct}/{total} ({correct/total*100:.1f}%)")
    logger.info(f"  Wrong direction:   {wrong_dir}/{total}")
    logger.info(f"  In ROR only:       {ror_only}/{total}")
    logger.info(f"  Not found:         {not_found}/{total}")
    logger.info(f"  Coverage:          {coverage:.1%}")
    logger.info(f"  Dir. precision:    {precision:.1%}")
    logger.info("=" * 60)

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)

    results_df = pd.DataFrame(results)
    results_file = output_dir / "benchmark_validation.csv"
    results_df.to_csv(results_file, index=False)
    logger.info(f"Saved detailed results to {results_file}")

    summary_file = output_dir / "validation_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved summary to {summary_file}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate SexDiffKG against literature benchmarks"
    )
    parser.add_argument(
        "--signals-dir",
        type=str,
        default="results/signals",
        help="Directory containing signal parquet files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/validation",
        help="Directory to save validation results",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(args.log_level)

    run_validation(Path(args.signals_dir), Path(args.output_dir))
