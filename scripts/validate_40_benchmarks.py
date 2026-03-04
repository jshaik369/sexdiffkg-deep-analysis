#!/usr/bin/env python3
"""Validate all 40 benchmarks against SexDiffKG signal data."""
import duckdb
import json
from pathlib import Path

signal_file = Path.home() / "sexdiffkg/results/signals_v2/sex_differential.parquet"
con = duckdb.connect()

# All 40 benchmarks: (number, drug, ae_term, expected_direction)
benchmarks = [
    # Original 15
    (1, "METHADONE", "QT prolongation", "F>M"),
    (2, "ENALAPRIL", "Cough", "F>M"),
    (3, "ERYTHROMYCIN", "QT prolongation", "F>M"),
    (4, "LEVOFLOXACIN", "Tendon rupture", "M>F"),
    (5, "ATORVASTATIN", "Rhabdomyolysis", "F>M"),
    (6, "ASPIRIN", "Gastrointestinal haemorrhage", "M>F"),
    (7, "AMOXICILLIN", "Hepatocellular injury", "M>F"),
    (8, "SOTALOL", "Torsade de pointes", "F>M"),
    (9, "FLUOXETINE", "Hyponatraemia", "F>M"),
    (10, "MORPHINE", "Respiratory depression", "F>M"),
    (11, "WARFARIN", "Haemorrhage", "F>M"),
    (12, "DIGOXIN", "Cardiac arrest", "F>M"),
    (13, "HYDROCHLOROTHIAZIDE", "Hypokalaemia", "F>M"),
    (14, "ZOLPIDEM", "Somnolence", "F>M"),
    (15, "TRASTUZUMAB", "Cardiomyopathy", "F>M"),
    # New 25
    (16, "AMIODARONE", "QT prolongation", "F>M"),
    (17, "HALOPERIDOL", "Torsade de pointes", "F>M"),
    (18, "LISINOPRIL", "Cough", "F>M"),
    (19, "RAMIPRIL", "Cough", "F>M"),
    (20, "SIMVASTATIN", "Myopathy", "F>M"),
    (21, "ROSUVASTATIN", "Myopathy", "F>M"),
    (22, "TRAMADOL", "Vomiting", "F>M"),
    (23, "OXYCODONE", "Respiratory depression", "F>M"),
    (24, "ASPIRIN", "Gastrointestinal haemorrhage", "M>F"),  # dup of #6 w/ different source
    (25, "IBUPROFEN", "Gastrointestinal haemorrhage", "M>F"),
    (26, "VALPROIC ACID", "Hepatotoxicity", "M>F"),
    (27, "ISONIAZID", "Drug-induced liver injury", "F>M"),
    (28, "ARIPIPRAZOLE", "Hyperprolactinaemia", "F>M"),
    (29, "OLANZAPINE", "Weight increased", "F>M"),
    (30, "DIGOXIN", "Death", "F>M"),
    (31, "METOPROLOL", "Hypotension", "F>M"),
    (32, "HEPARIN", "Haemorrhage", "F>M"),
    (33, "HYDROCHLOROTHIAZIDE", "Hyponatraemia", "F>M"),
    (34, "FUROSEMIDE", "Hyponatraemia", "F>M"),
    (35, "AMLODIPINE", "Oedema peripheral", "F>M"),
    (36, "NIFEDIPINE", "Oedema peripheral", "F>M"),
    (37, "DENOSUMAB", "Spinal fracture", "F>M"),
    (38, "QUETIAPINE", "Weight increased", "F>M"),
    (39, "ACETAMINOPHEN", "Hepatotoxicity", "F>M"),
    (40, "LEUPROLIDE", "Precocious puberty", "F>M"),
]

results = []
found = 0
correct = 0
wrong_dir = 0
not_found = 0
single_sex = 0

for num, drug, ae, expected in benchmarks:
    # Search with LIKE for flexibility
    query = f"""
    SELECT drug_name, pt, log_ror_ratio, direction, ror_female, ror_male, a_female, a_male
    FROM read_parquet('{signal_file}')
    WHERE UPPER(drug_name) LIKE '%{drug}%'
      AND UPPER(pt) LIKE '%{ae.upper().split()[0]}%'
    ORDER BY ABS(log_ror_ratio) DESC
    LIMIT 5
    """
    try:
        df = con.execute(query).fetchdf()
    except Exception as e:
        results.append((num, drug, ae, expected, "ERROR", str(e)))
        not_found += 1
        continue

    if len(df) == 0:
        # Try broader search on drug name only
        query2 = f"""
        SELECT drug_name, pt, log_ror_ratio, direction, ror_female, ror_male, a_female, a_male
        FROM read_parquet('{signal_file}')
        WHERE UPPER(drug_name) LIKE '%{drug}%'
        ORDER BY ABS(log_ror_ratio) DESC
        LIMIT 3
        """
        df2 = con.execute(query2).fetchdf()
        if len(df2) == 0:
            results.append((num, drug, ae, expected, "NOT_FOUND", "Drug not in signals"))
            not_found += 1
        else:
            results.append((num, drug, ae, expected, "AE_NOT_FOUND", f"Drug found ({len(df2)} signals) but AE not matched"))
            not_found += 1
        continue

    row = df.iloc[0]
    direction = row['direction']
    log_ratio = row['log_ror_ratio']
    actual_pt = row['pt']
    actual_drug = row['drug_name']
    found += 1

    # Determine if direction matches
    if expected == "F>M":
        if direction == 'female_higher':
            status = "CORRECT"
            correct += 1
        elif direction == 'male_higher':
            status = "WRONG_DIR"
            wrong_dir += 1
        else:
            status = "UNKNOWN_DIR"
    elif expected == "M>F":
        if direction == 'male_higher':
            status = "CORRECT"
            correct += 1
        elif direction == 'female_higher':
            status = "WRONG_DIR"
            wrong_dir += 1
        else:
            status = "UNKNOWN_DIR"
    else:
        status = "CHECK"

    results.append((num, drug, ae, expected, status,
                     f"matched: {actual_drug}|{actual_pt} log_ratio={log_ratio:.3f} dir={direction} ROR_F={row['ror_female']:.2f} ROR_M={row['ror_male']:.2f}"))

# Print results
print("=" * 100)
print(f"SEXDIFFKG BENCHMARK VALIDATION — 40 BENCHMARKS")
print("=" * 100)
print(f"\n{'#':>3} {'Drug':<25} {'AE':<30} {'Exp':>5} {'Status':<12} Details")
print("-" * 100)
for num, drug, ae, expected, status, detail in results:
    emoji = {"CORRECT": "✅", "WRONG_DIR": "❌", "NOT_FOUND": "🔍", "AE_NOT_FOUND": "🔍", "SINGLE_SEX": "⚠️", "ERROR": "💥"}.get(status, "❓")
    print(f"{num:>3} {drug:<25} {ae:<30} {expected:>5} {emoji} {status:<12} {detail[:60]}")

print("\n" + "=" * 100)
print(f"SUMMARY:")
print(f"  Found in signals: {found}/40 ({found/40*100:.1f}%)")
print(f"  Correct direction: {correct}/{found} ({correct/found*100:.1f}% of found)" if found > 0 else "  No signals found")
print(f"  Wrong direction: {wrong_dir}/{found}")
print(f"  Not found: {not_found}/40")
print("=" * 100)

# Save JSON
output = {
    "validation_date": "2026-02-27",
    "total_benchmarks": 40,
    "found": found,
    "correct_direction": correct,
    "wrong_direction": wrong_dir,
    "not_found": not_found,
    "coverage_pct": round(found/40*100, 1),
    "precision_pct": round(correct/found*100, 1) if found > 0 else 0,
    "results": [
        {"num": r[0], "drug": r[1], "ae": r[2], "expected": r[3], "status": r[4], "detail": r[5]}
        for r in results
    ]
}
outfile = Path.home() / "sexdiffkg/results/validation_40_benchmarks.json"
outfile.write_text(json.dumps(output, indent=2))
print(f"\nResults saved to {outfile}")
