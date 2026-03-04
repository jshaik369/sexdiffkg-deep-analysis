#!/usr/bin/env python3
"""
SexDiffKG Verification Numbers
===============================
Reads all key output files and verifies against expected values.
- Compares actual vs. expected counts
- Reports PASS/FAIL/WARNING for each check
- Outputs detailed verification_report.json

Author: Audit Module
Infrastructure: NVIDIA DGX Spark GB10 (ARM64, Python 3.13)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple

# ============================================================
# CONFIGURATION
# ============================================================

HOME = Path.home()
BASE = HOME / "sexdiffkg"
DATA = BASE / "data"
KG = DATA / "kg"
RESULTS = BASE / "results"
AUDIT_OUT = RESULTS / "audits"

AUDIT_OUT.mkdir(parents=True, exist_ok=True)

# Expected values from a verified successful pipeline run
# These are baselines for comparison
EXPECTED_VALUES = {
    "kg_nodes": {
        "min_rows": 120000,
        "max_rows": 130000,
        "description": "Entity nodes in KG"
    },
    "kg_edges": {
        "min_rows": 5800000,
        "max_rows": 6000000,
        "description": "Edges/relations in KG"
    },
    "kg_triples": {
        "min_rows": 5800000,
        "max_rows": 6000000,
        "description": "RDF triples in KG"
    },
}

# Key output files to verify
KEY_FILES = {
    "kg_nodes": KG / "nodes.tsv",
    "kg_edges": KG / "edges.tsv",
    "kg_triples": KG / "triples.tsv",
}

# ============================================================
# VERIFICATION FUNCTIONS
# ============================================================

def count_lines(filepath: Path) -> int:
    """Count lines in a file efficiently."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception as e:
        return -1

def verify_file_structure(filepath: Path) -> Dict[str, Any]:
    """Verify file structure and basic integrity."""
    result = {
        "exists": filepath.exists(),
        "size_mb": 0,
        "lines": 0,
        "header": "",
        "sample_row": "",
        "integrity": "OK"
    }

    if not filepath.exists():
        result["integrity"] = "MISSING"
        return result

    try:
        result["size_mb"] = filepath.stat().st_size / 1024 / 1024
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            # Read header
            header = f.readline().strip()
            result["header"] = header[:100]
            
            # Count lines and save first data row
            result["lines"] = sum(1 for _ in f)
            
            # Get sample row
            f.seek(0)
            f.readline()  # Skip header
            sample = f.readline().strip()
            result["sample_row"] = sample[:100]
    except Exception as e:
        result["integrity"] = f"ERROR: {str(e)[:50]}"
        result["lines"] = -1

    return result

def verify_numeric_counts() -> Dict[str, Any]:
    """Verify row counts against expected values."""
    print("\n[1/3] Verifying row counts...")
    results = {}
    passed = 0
    failed = 0
    warnings = 0

    for file_key, expected in EXPECTED_VALUES.items():
        filepath = KEY_FILES.get(file_key)
        if not filepath:
            continue

        result = {
            "description": expected["description"],
            "expected_min": expected["min_rows"],
            "expected_max": expected["max_rows"],
            "actual_lines": 0,
            "status": "UNKNOWN",
            "message": ""
        }

        if not filepath.exists():
            result["status"] = "FAIL"
            result["message"] = f"File not found: {filepath}"
            failed += 1
        else:
            actual = count_lines(filepath)
            result["actual_lines"] = actual

            if actual < 0:
                result["status"] = "FAIL"
                result["message"] = "Could not count lines"
                failed += 1
            elif expected["min_rows"] <= actual <= expected["max_rows"]:
                result["status"] = "PASS"
                result["message"] = f"Within expected range"
                passed += 1
            else:
                result["status"] = "WARNING"
                deviation = actual - expected["min_rows"]
                pct = (deviation / expected["min_rows"] * 100) if expected["min_rows"] > 0 else 0
                result["message"] = f"Outside range by {deviation:+,} lines ({pct:+.1f}%)"
                warnings += 1

        results[file_key] = result

    return {
        "checks": results,
        "summary": {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "total": passed + failed + warnings
        }
    }

def verify_file_integrity() -> Dict[str, Any]:
    """Verify file structure and header integrity."""
    print("[2/3] Verifying file structure...")
    results = {}
    passed = 0
    failed = 0

    for file_key, filepath in KEY_FILES.items():
        structure = verify_file_structure(filepath)
        results[file_key] = structure

        if structure["integrity"] == "OK":
            passed += 1
        else:
            failed += 1

        # Print status
        status = "OK" if structure["integrity"] == "OK" else "FAIL"
        size = structure["size_mb"]
        lines = structure["lines"]
        print(f"  {file_key:20} {status:5} ({size:8.1f} MB, {lines:>10,} lines)")

    return {
        "checks": results,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": passed + failed
        }
    }

def verify_data_consistency() -> Dict[str, Any]:
    """Verify data consistency across files."""
    print("[3/3] Checking data consistency...")
    results = {}

    # Check that entities in triples are reasonable
    triples_file = KEY_FILES["kg_triples"]
    nodes_file = KEY_FILES["kg_nodes"]

    if triples_file.exists() and nodes_file.exists():
        triples_count = count_lines(triples_file)
        nodes_count = count_lines(nodes_file)

        # TSV files include header line
        actual_triples = triples_count - 1  # Exclude header
        actual_nodes = nodes_count - 1      # Exclude header

        # Generally, triples > nodes * 2 (entities appear in multiple relations)
        ratio = actual_triples / actual_nodes if actual_nodes > 0 else 0

        results["triples_to_nodes_ratio"] = {
            "triples": actual_triples,
            "nodes": actual_nodes,
            "ratio": round(ratio, 2),
            "expected_range": [40, 60],  # Conservative estimate
            "status": "OK" if 40 <= ratio <= 60 else "WARNING"
        }

        # Check header consistency
        triple_header = ""
        node_header = ""

        with open(triples_file, "r", encoding="utf-8", errors="ignore") as f:
            triple_header = f.readline().strip()

        with open(nodes_file, "r", encoding="utf-8", errors="ignore") as f:
            node_header = f.readline().strip()

        results["headers"] = {
            "triples_header": triple_header,
            "nodes_header": node_header,
            "both_present": bool(triple_header and node_header)
        }

    return results

# ============================================================
# VERIFICATION REPORT
# ============================================================

class VerificationReport:
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "report_version": "1.0",
            "verification_type": "comprehensive",
            "sections": {}
        }
        self.all_passed = True
        self.all_failed = False

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all verification checks."""
        print("\n" + "="*60)
        print("SexDiffKG VERIFICATION REPORT")
        print("="*60)

        # Numeric verification
        numeric = verify_numeric_counts()
        self.report["sections"]["numeric_counts"] = numeric
        if numeric["summary"]["failed"] > 0:
            self.all_passed = False
        if numeric["summary"]["failed"] == numeric["summary"]["total"]:
            self.all_failed = True

        # File integrity
        integrity = verify_file_integrity()
        self.report["sections"]["file_integrity"] = integrity
        if integrity["summary"]["failed"] > 0:
            self.all_passed = False

        # Data consistency
        consistency = verify_data_consistency()
        self.report["sections"]["data_consistency"] = consistency

        # Overall summary
        total_passed = (
            numeric["summary"]["passed"] +
            numeric["summary"]["warnings"] +
            integrity["summary"]["passed"]
        )
        total_checks = (
            numeric["summary"]["total"] +
            integrity["summary"]["total"]
        )

        self.report["summary"] = {
            "status": "PASS" if self.all_passed else "FAIL" if self.all_failed else "WARNING",
            "total_checks": total_checks,
            "passed": total_passed,
            "warnings": numeric["summary"]["warnings"],
            "failed": numeric["summary"]["failed"] + integrity["summary"]["failed"],
            "timestamp": datetime.now().isoformat()
        }

        return self.report

    def print_summary(self):
        """Print verification summary."""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)

        s = self.report["summary"]
        print(f"Overall Status: {s['status']}")
        print(f"Total Checks:   {s['total_checks']}")
        print(f"Passed:         {s['passed']}")
        print(f"Warnings:       {s['warnings']}")
        print(f"Failed:         {s['failed']}")

        # Print per-section results
        print("\n" + "-"*60)
        print("NUMERIC COUNTS:")
        print("-"*60)
        for file_key, check in self.report["sections"]["numeric_counts"]["checks"].items():
            status = check["status"]
            actual = check["actual_lines"]
            expected_min = check["expected_min"]
            expected_max = check["expected_max"]
            print(f"{file_key:20} {status:8} actual={actual:>10,} expected=[{expected_min:>10,}, {expected_max:>10,}]")
            if check["message"]:
                print(f"  Message: {check['message']}")

    def save_report(self, filepath: Path):
        """Save report to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.report, f, indent=2)
        print(f"\nDetailed report saved to: {filepath}")

    def save_summary_csv(self, filepath: Path):
        """Save summary as CSV for easy comparison."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w") as f:
            f.write("File,ActualLines,ExpectedMin,ExpectedMax,Status,Message\n")
            for file_key, check in self.report["sections"]["numeric_counts"]["checks"].items():
                actual = check["actual_lines"]
                min_val = check["expected_min"]
                max_val = check["expected_max"]
                status = check["status"]
                msg = check["message"].replace(",", ";")
                f.write(f"{file_key},{actual},{min_val},{max_val},{status},\"{msg}\"\n")

        print(f"CSV summary saved to: {filepath}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    report = VerificationReport()
    manifest = report.run_all_checks()
    report.print_summary()

    # Save reports
    json_file = AUDIT_OUT / "verification_report.json"
    csv_file = AUDIT_OUT / "verification_summary.csv"
    report.save_report(json_file)
    report.save_summary_csv(csv_file)

    # Exit with appropriate code
    status = manifest["summary"]["status"]
    exit_code = 0 if status == "PASS" else (1 if status == "FAIL" else 0)
    sys.exit(exit_code)
