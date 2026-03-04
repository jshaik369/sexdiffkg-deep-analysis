#!/usr/bin/env python3
"""Validate all 40 benchmarks against SexDiffKG v4 signal data (DiAna-normalized)."""
import duckdb
import json
from pathlib import Path

signal_file = Path.home() / "sexdiffkg/results/signals_v4/sex_differential_v4.parquet"
con = duckdb.connect()

benchmarks = [
    (1, "METHADONE", "QT prolongation", "F>M", ["Long QT", "Electrocardiogram QT"]),
    (2, "ENALAPRIL", "Cough", "F>M", ["Productive cough"]),
    (3, "ERYTHROMYCIN", "QT prolongation", "F>M", ["Long QT", "Electrocardiogram QT"]),
    (4, "LEVOFLOXACIN", "Tendon rupture", "M>F", ["Tendon disorder", "Tendinitis"]),
    (5, "ATORVASTATIN", "Rhabdomyolysis", "F>M", ["Myopathy", "Myalgia"]),
    (6, "ASPIRIN", "Gastrointestinal haemorrhage", "M>F", ["Gastrointestinal haemorrhage", "GI bleed"]),
    (7, "AMOXICILLIN", "Hepatocellular injury", "M>F", ["Hepato", "Liver", "Drug-induced liver"]),
    (8, "SOTALOL", "Torsade de pointes", "F>M", ["Torsade"]),
    (9, "FLUOXETINE", "Hyponatraemia", "F>M", ["Hyponatr"]),
    (10, "MORPHINE", "Respiratory depression", "F>M", ["Respiratory depression"]),
    (11, "WARFARIN", "Haemorrhage", "F>M", ["Haemorrhage", "Hemorrhage", "Bleeding"]),
    (12, "DIGOXIN", "Cardiac arrest", "F>M", ["Cardiac arrest"]),
    (13, "HYDROCHLOROTHIAZIDE", "Hypokalaemia", "F>M", ["Hypokal"]),
    (14, "ZOLPIDEM", "Somnolence", "F>M", ["Somno", "Drowsin", "Sedation"]),
    (15, "TRASTUZUMAB", "Cardiomyopathy", "F>M", ["Cardiom", "Ejection fraction"]),
    (16, "AMIODARONE", "QT prolongation", "F>M", ["Long QT", "Electrocardiogram QT"]),
    (17, "HALOPERIDOL", "Torsade de pointes", "F>M", ["Torsade"]),
    (18, "LISINOPRIL", "Cough", "F>M", ["Productive cough"]),
    (19, "RAMIPRIL", "Cough", "F>M", ["Productive cough"]),
    (20, "SIMVASTATIN", "Myopathy", "F>M", ["Myopathy", "Rhabdomyolysis"]),
    (21, "ROSUVASTATIN", "Myopathy", "F>M", ["Myopathy", "Rhabdomyolysis"]),
    (22, "TRAMADOL", "Vomiting", "F>M", ["Vomiting", "Nausea"]),
    (23, "OXYCODONE", "Respiratory depression", "F>M", ["Respiratory depression"]),
    (24, "ASPIRIN", "Gastrointestinal haemorrhage", "M>F", ["Gastrointestinal haemorrhage"]),
    (25, "IBUPROFEN", "Gastrointestinal haemorrhage", "M>F", ["Gastrointestinal haemorrhage"]),
    (26, "VALPROIC ACID", "Hepatotoxicity", "M>F", ["Hepato", "Liver"]),
    (27, "ISONIAZID", "Drug-induced liver injury", "F>M", ["Hepato", "Liver", "Drug-induced liver"]),
    (28, "ARIPIPRAZOLE", "Hyperprolactinaemia", "F>M", ["Hyperprolact", "Prolactin"]),
    (29, "OLANZAPINE", "Weight increased", "F>M", ["Weight", "Obesity"]),
    (30, "DIGOXIN", "Death", "F>M", ["Death", "Sudden cardiac death"]),
    (31, "METOPROLOL", "Hypotension", "F>M", ["Hypotension"]),
    (32, "HEPARIN", "Haemorrhage", "F>M", ["Haemorrhage", "Hemorrhage", "Bleeding"]),
    (33, "HYDROCHLOROTHIAZIDE", "Hyponatraemia", "F>M", ["Hyponatr"]),
    (34, "FUROSEMIDE", "Hyponatraemia", "F>M", ["Hyponatr"]),
    (35, "AMLODIPINE", "Oedema peripheral", "F>M", ["Oedema", "Edema", "Swelling"]),
    (36, "NIFEDIPINE", "Oedema peripheral", "F>M", ["Oedema", "Edema"]),
    (37, "DENOSUMAB", "Spinal fracture", "F>M", ["Spinal", "Vertebral", "Fracture"]),
    (38, "QUETIAPINE", "Weight increased", "F>M", ["Weight", "Obesity"]),
    (39, "ACETAMINOPHEN", "Hepatotoxicity", "F>M", ["Hepato", "Liver"]),
    (40, "LEUPROLIDE", "Precocious puberty", "F>M", ["Precocious", "Puberty"]),
]

results = []
found = 0
correct = 0
wrong_dir = 0
not_found = 0

for num, drug, ae, expected, alts in benchmarks:
    ae_conds = ["UPPER(adverse_event) LIKE '%" + ae.upper() + "%'"]
    for alt in alts:
        ae_conds.append("UPPER(adverse_event) LIKE '%" + alt.upper() + "%'")
    ae_clause = " OR ".join(ae_conds)

    query = f"""
    SELECT drug_name, adverse_event, log_ratio, direction, ror_female, ror_male, n_female, n_male,
           CASE WHEN UPPER(drug_name) = '{drug}' THEN 0 ELSE 1 END as drug_rank,
           CASE WHEN UPPER(adverse_event) LIKE '%{ae.upper()}%' THEN 0 ELSE 1 END as ae_rank
    FROM read_parquet('{signal_file}')
    WHERE UPPER(drug_name) LIKE '%{drug}%' AND ({ae_clause})
    ORDER BY drug_rank, ae_rank, ABS(log_ratio) DESC
    LIMIT 5
    """
    try:
        df = con.execute(query).fetchdf()
    except Exception as e:
        results.append((num, drug, ae, expected, "ERROR", str(e)))
        not_found += 1
        continue

    if len(df) == 0:
        query2 = f"""
        SELECT COUNT(*) as cnt FROM read_parquet('{signal_file}')
        WHERE UPPER(drug_name) LIKE '%{drug}%'
        """
        cnt = con.execute(query2).fetchone()[0]
        if cnt == 0:
            results.append((num, drug, ae, expected, "NOT_FOUND", "Drug not in v4 signals"))
        else:
            results.append((num, drug, ae, expected, "AE_NOT_FOUND", f"Drug found ({cnt} signals) but AE not matched"))
        not_found += 1
        continue

    row = df.iloc[0]
    direction = row["direction"]
    log_ratio = row["log_ratio"]
    actual_ae = row["adverse_event"]
    actual_drug = row["drug_name"]
    found += 1

    if expected == "F>M":
        if direction == "female_higher":
            status = "CORRECT"
            correct += 1
        elif direction == "male_higher":
            status = "WRONG_DIR"
            wrong_dir += 1
        else:
            status = "UNKNOWN_DIR"
    elif expected == "M>F":
        if direction == "male_higher":
            status = "CORRECT"
            correct += 1
        elif direction == "female_higher":
            status = "WRONG_DIR"
            wrong_dir += 1
        else:
            status = "UNKNOWN_DIR"

    results.append((num, drug, ae, expected, status,
        f"matched: {actual_drug}|{actual_ae} log_ratio={log_ratio:.3f} dir={direction} "
        f"ROR_F={row['ror_female']:.2f} ROR_M={row['ror_male']:.2f} "
        f"n_F={int(row['n_female'])} n_M={int(row['n_male'])}"))

print("=" * 140)
print("SEXDIFFKG v4 BENCHMARK VALIDATION - 40 BENCHMARKS (DiAna-normalized signals)")
print("=" * 140)
print(f"\n{'#':>3} {'Drug':<25} {'AE':<32} {'Exp':>5} {'Status':<14} Details")
print("-" * 140)
for num, drug, ae, expected, status, detail in results:
    mark = {"CORRECT": "[OK]", "WRONG_DIR": "[XX]", "NOT_FOUND": "[??]",
            "AE_NOT_FOUND": "[??]", "ERROR": "[!!]"}.get(status, "[??]")
    print(f"{num:>3} {drug:<25} {ae:<32} {expected:>5} {mark} {status:<14} {detail[:90]}")

print()
print("=" * 140)
print("SUMMARY:")
print(f"  Found in v4 signals: {found}/40 ({found/40*100:.1f}%)")
if found > 0:
    print(f"  Correct direction:   {correct}/{found} ({correct/found*100:.1f}% directional precision)")
    print(f"  Wrong direction:     {wrong_dir}/{found}")
print(f"  Not found:           {not_found}/40")
print()
print("--- v3 vs v4 COMPARISON ---")
print(f"  v3: Coverage 30/40 (75.0%), Precision 19/30 (63.3%)")
if found > 0:
    print(f"  v4: Coverage {found}/40 ({found/40*100:.1f}%), Precision {correct}/{found} ({correct/found*100:.1f}%)")
    cov_delta = found / 40 * 100 - 75.0
    prec_delta = correct / found * 100 - 63.3
    sign_c = "+" if cov_delta >= 0 else ""
    sign_p = "+" if prec_delta >= 0 else ""
    print(f"  Delta: Coverage {sign_c}{cov_delta:.1f}pp, Precision {sign_p}{prec_delta:.1f}pp")
print("=" * 140)

output = {
    "validation_date": "2026-03-03",
    "signal_version": "v4_diana_normalized",
    "total_benchmarks": 40,
    "found": found,
    "correct_direction": correct,
    "wrong_direction": wrong_dir,
    "not_found": not_found,
    "coverage_pct": round(found / 40 * 100, 1),
    "precision_pct": round(correct / found * 100, 1) if found > 0 else 0,
    "v3_comparison": {
        "v3_found": 30, "v3_correct": 19,
        "v3_coverage": 75.0, "v3_precision": 63.3
    },
    "results": [
        {"num": r[0], "drug": r[1], "ae": r[2], "expected": r[3],
         "status": r[4], "detail": r[5]}
        for r in results
    ]
}
outfile = Path.home() / "sexdiffkg/results/validation_40_benchmarks_v4.json"
outfile.write_text(json.dumps(output, indent=2))
print(f"\nResults saved to {outfile}")
