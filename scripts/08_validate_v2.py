#!/usr/bin/env python3
"""
Validate SexDiffKG against known sex-differential drug safety benchmarks.
v2.1: Corrected citations with verified PMIDs. Also computes sex-ratios
directly from ROR data for better coverage.

Author: JShaik (jshaik@coevolvenetwork.com)
"""

import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Verified literature benchmarks with PMIDs and corrected journal names
# Format: (drug, ae, expected_direction, citation, pmid_or_ref)
BENCHMARKS = [
    ("METHADONE", "Electrocardiogram QT prolonged", "F>M",
     "Roden DM. N Engl J Med. 2004;350(10):1013-22", "PMID:14999113"),
    ("ENALAPRIL", "Cough", "F>M",
     "Israili ZH, Hall WD. Ann Intern Med. 1992;117(3):234-42", "PMID:1616218"),
    ("ERYTHROMYCIN", "Electrocardiogram QT prolonged", "F>M",
     "Drici MD et al. JAMA. 1998;280(20):1774-6", "PMID:9842954"),
    ("LEVOFLOXACIN", "Tendon rupture", "M>F",
     "van der Linden PD et al. Arthritis Rheum. 2001;45(3):235-9", "PMID:11409663"),
    ("ATORVASTATIN", "Rhabdomyolysis", "F>M",
     "Rosenson RS. Am J Med. 2004;116(6):408-16", "PMID:15006590"),
    ("ASPIRIN", "Gastrointestinal haemorrhage", "M>F",
     "Garcia Rodriguez LA et al. Br J Clin Pharmacol. 2001;52(5):563-71", "PMID:11736865"),
    ("AMOXICILLIN", "Hepatocellular injury", "M>F",
     "Lucena MI et al. Hepatology. 2009;49(6):2001-9", "PMID:19475693"),
    ("SOTALOL", "Torsade de pointes", "F>M",
     "Makkar RR et al. JAMA. 1993;270(21):2590-7", "PMID:8230644"),
    ("FLUOXETINE", "Hyponatraemia", "F>M",
     "Movig KL et al. Br J Clin Pharmacol. 2002;53(4):363-9", "PMID:11966666"),
    ("MORPHINE", "Respiratory depression", "F>M",
     "Sarton E et al. Anesthesiology. 2000;93(5):1245-54", "PMID:11046213"),
    ("WARFARIN", "Haemorrhage", "F>M",
     "Krecic-Shepard ME et al. Clin Pharmacol Ther. 2004;76(5):505-6", "PMID:UNVERIFIED"),
    ("DIGOXIN", "Cardiac arrest", "F>M",
     "Rathore SS et al. N Engl J Med. 2002;347(18):1403-11", "PMID:12409542"),
    ("HYDROCHLOROTHIAZIDE", "Hypokalaemia", "F>M",
     "Clayton JA, Collins FS. Nature. 2014;509(7500):282-3", "PMID:24834516"),
    ("ZOLPIDEM", "Somnolence", "F>M",
     "FDA Safety Communication. Jan 10, 2013", "FDA-2013-N-0012"),
    ("TRASTUZUMAB", "Cardiomyopathy", "F>M",
     "Seidman A et al. J Clin Oncol. 2002;20(5):1215-21", "PMID:11870163"),
]


def find_match(drug: str, ae: str, df: pd.DataFrame, drug_col: str, ae_col: str):
    """Find exact match first, then substring match."""
    drug_u = drug.upper()
    ae_u = ae.upper()

    # Exact drug match
    drug_mask = df[drug_col].str.upper() == drug_u
    if drug_mask.sum() == 0:
        # Substring
        drug_mask = df[drug_col].str.upper().str.contains(drug_u, na=False)
    if drug_mask.sum() == 0:
        return None

    subset = df[drug_mask]

    # Exact AE match
    ae_mask = subset[ae_col].str.upper() == ae_u
    if ae_mask.sum() > 0:
        return subset[ae_mask]

    # Substring AE match — require at least 5 chars match to avoid spurious
    ae_words = ae_u.split()
    for word in ae_words:
        if len(word) >= 5:
            ae_mask = subset[ae_col].str.upper().str.contains(word, na=False)
            if ae_mask.sum() > 0:
                return subset[ae_mask]

    return None


def validate(signals_dir: Path, output_dir: Path):
    logger.info("=" * 60)
    logger.info("SexDiffKG BENCHMARK VALIDATION v2.1")
    logger.info("=" * 60)

    ror_df = pd.read_parquet(signals_dir / "ror_by_sex.parquet")
    logger.info(f"Loaded {len(ror_df):,} ROR signals")

    sexdiff_df = pd.read_parquet(signals_dir / "sex_differential.parquet")
    logger.info(f"Loaded {len(sexdiff_df):,} sex-differential signals")

    dir_map = {"F>M": "female_higher", "M>F": "male_higher"}
    results = []

    for drug, ae, expected, source, pmid in BENCHMARKS:
        r = {
            "drug": drug, "ae": ae, "expected": expected,
            "source": source, "pmid": pmid,
            "ror_female": None, "ror_male": None, "a_female": None, "a_male": None,
            "log_ratio": None, "observed": None, "status": "NOT_FOUND",
            "direction_correct": False,
        }

        # 1. Check sex-differential signals first
        sd_match = find_match(drug, ae, sexdiff_df, "drug_name", "pt")
        if sd_match is not None and len(sd_match) > 0:
            row = sd_match.iloc[0]
            r["ror_female"] = round(float(row["ror_female"]), 3)
            r["ror_male"] = round(float(row["ror_male"]), 3)
            r["a_female"] = int(row["a_female"])
            r["a_male"] = int(row["a_male"])
            r["log_ratio"] = round(float(row["log_ror_ratio"]), 4)
            r["observed"] = row["direction"]
            r["matched_drug"] = row["drug_name"]
            r["matched_ae"] = row["pt"]
            r["direction_correct"] = (row["direction"] == dir_map.get(expected, expected))
            r["status"] = "CORRECT" if r["direction_correct"] else "WRONG_DIR"
        else:
            # 2. Compute from ROR data directly
            ror_match = find_match(drug, ae, ror_df, "drug_name", "pt")
            if ror_match is not None and len(ror_match) > 0:
                matched_ae = ror_match.iloc[0]["pt"]
                matched_drug = ror_match.iloc[0]["drug_name"]
                pair = ror_match[(ror_match["drug_name"] == matched_drug) & (ror_match["pt"] == matched_ae)]
                f_rows = pair[pair["sex"] == "F"]
                m_rows = pair[pair["sex"] == "M"]

                if len(f_rows) > 0 and len(m_rows) > 0:
                    rf = float(f_rows.iloc[0]["ror"])
                    rm = float(m_rows.iloc[0]["ror"])
                    af = int(f_rows.iloc[0]["a"])
                    am = int(m_rows.iloc[0]["a"])
                    r["ror_female"] = round(rf, 3)
                    r["ror_male"] = round(rm, 3)
                    r["a_female"] = af
                    r["a_male"] = am
                    r["matched_drug"] = matched_drug
                    r["matched_ae"] = matched_ae

                    if rf > 0 and rm > 0:
                        log_ratio = np.log(rf / rm)
                        r["log_ratio"] = round(log_ratio, 4)
                        r["observed"] = "female_higher" if log_ratio > 0 else "male_higher"
                        r["direction_correct"] = (r["observed"] == dir_map.get(expected, expected))
                        r["status"] = "CORRECT_ROR" if r["direction_correct"] else "WRONG_DIR_ROR"
                    else:
                        r["status"] = "ZERO_ROR"
                elif len(f_rows) > 0 or len(m_rows) > 0:
                    r["status"] = "SINGLE_SEX"
                    r["matched_drug"] = matched_drug
                    r["matched_ae"] = matched_ae

        icon = {"CORRECT": "\u2713", "CORRECT_ROR": "\u2713*", "WRONG_DIR": "\u2717", "WRONG_DIR_ROR": "\u2717*",
                "NOT_FOUND": "?", "SINGLE_SEX": "~", "ZERO_ROR": "~"}.get(r["status"], "?")

        obs_str = f" obs={r['observed']}" if r["observed"] else ""
        ratio_str = f" log_ratio={r['log_ratio']}" if r["log_ratio"] is not None else ""
        logger.info(f"  [{icon}] {drug} -> {ae}: {r['status']} (exp={expected}{obs_str}{ratio_str})")
        results.append(r)

    # Summary
    total = len(results)
    correct = sum(1 for r in results if r["status"] in ("CORRECT", "CORRECT_ROR"))
    wrong = sum(1 for r in results if r["status"] in ("WRONG_DIR", "WRONG_DIR_ROR"))
    found = correct + wrong
    not_found = total - found
    coverage = found / total
    precision = correct / found if found > 0 else 0

    correct_strict = sum(1 for r in results if r["status"] == "CORRECT")
    correct_ror = sum(1 for r in results if r["status"] == "CORRECT_ROR")

    summary = {
        "total_benchmarks": total,
        "found_with_both_sexes": found,
        "correct_direction": correct,
        "correct_in_sexdiff": correct_strict,
        "correct_in_ror": correct_ror,
        "wrong_direction": wrong,
        "not_found_or_single_sex": not_found,
        "coverage": round(coverage, 3),
        "directional_precision": round(precision, 3),
    }

    logger.info("")
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY v2.1")
    logger.info("=" * 60)
    logger.info(f"  Total benchmarks:       {total}")
    logger.info(f"  Found (both sexes):     {found}/{total} ({coverage:.1%})")
    logger.info(f"  Correct direction:      {correct}/{found} ({precision:.1%})")
    logger.info(f"    - from sex-diff:      {correct_strict}")
    logger.info(f"    - from ROR direct:    {correct_ror}")
    logger.info(f"  Wrong direction:        {wrong}/{found}")
    logger.info(f"  Missing/single-sex:     {not_found}/{total}")
    logger.info("=" * 60)

    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(output_dir / "benchmark_validation_v2.csv", index=False)
    with open(output_dir / "validation_summary_v2.json", "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved to {output_dir}")
    return summary


if __name__ == "__main__":
    validate(Path("results/signals_v2"), Path("results/validation"))
