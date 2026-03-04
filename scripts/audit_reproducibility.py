#!/usr/bin/env python3
"""
SexDiffKG Reproducibility Audit
================================
Verifies pipeline reproducibility by checking:
1. Input/output file existence and properties
2. Python package versions
3. Data flow integrity
4. Generates reproducibility manifest

Author: Audit Module
Infrastructure: NVIDIA DGX Spark GB10 (ARM64, Python 3.13)
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# ============================================================
# CONFIGURATION
# ============================================================

HOME = Path.home()
BASE = HOME / "sexdiffkg"
DATA = BASE / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
KG = DATA / "kg"
RESULTS = BASE / "results"
SCRIPTS = BASE / "scripts"
AUDIT_OUT = RESULTS / "audits"

AUDIT_OUT.mkdir(parents=True, exist_ok=True)

# Expected package versions (from requirements.txt)
REQUIRED_PACKAGES = {
    "pandas": "2.0.0",
    "numpy": "1.24.0",
    "torch": "2.0.0",
    "pykeen": "1.9.0",
}

# Key output files to verify (phase -> output file path)
KEY_OUTPUTS = {
    "kg_nodes": KG / "nodes.tsv",
    "kg_edges": KG / "edges.tsv",
    "kg_triples": KG / "triples.tsv",
}

# Expected row counts for key files (conservative estimates)
EXPECTED_COUNTS = {
    "kg_nodes": (120000, 130000),      # (min, max)
    "kg_edges": (5800000, 6000000),
    "kg_triples": (5800000, 6000000),
}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def count_lines(filepath: Path) -> int:
    """Count lines in a file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception as e:
        return -1

def check_python_packages() -> Dict[str, str]:
    """Check installed package versions."""
    versions = {}
    for pkg in REQUIRED_PACKAGES.keys():
        try:
            module = __import__(pkg)
            version = getattr(module, "__version__", "unknown")
            versions[pkg] = version
        except ImportError:
            versions[pkg] = "NOT_INSTALLED"
    return versions

def verify_file_exists(filepath: Path) -> bool:
    """Check if file exists."""
    return filepath.exists() and filepath.is_file()

def get_tsv_column_info(filepath: Path) -> Dict[str, Any]:
    """Get TSV file column information."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            header = f.readline().strip()
            if not header:
                return {"error": "empty_file", "columns": []}
            columns = header.split("\t")
            return {
                "columns": columns,
                "count": len(columns),
                "header_sample": header[:100]
            }
    except Exception as e:
        return {"error": str(e), "columns": []}

# ============================================================
# REPRODUCIBILITY CHECKS
# ============================================================

class ReproducibilityAudit:
    def __init__(self):
        self.manifest = {
            "timestamp": datetime.now().isoformat(),
            "audit_version": "1.0",
            "checks": {},
            "summary": {
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        self.issues = []

    def check_input_files(self) -> Dict[str, Any]:
        """Verify input files exist and have expected structure."""
        print("\n[1/5] Checking input files...")
        results = {}

        # Check FAERS downloads
        faers_dir = RAW / "faers"
        if faers_dir.exists():
            faers_files = list(faers_dir.glob("*.zip"))
            results["faers_downloads"] = {
                "exists": True,
                "count": len(faers_files),
                "sample_files": [f.name for f in faers_files[:3]]
            }
            if len(faers_files) > 0:
                self.manifest["summary"]["passed"] += 1
            else:
                self.manifest["summary"]["failed"] += 1
                self.issues.append("No FAERS ZIP files found")
        else:
            results["faers_downloads"] = {"exists": False}
            self.manifest["summary"]["failed"] += 1
            self.issues.append("FAERS directory not found")

        # Check source directories
        for source in ["string", "gtex", "chembl", "kegg", "uniprot", "rxnorm"]:
            source_dir = RAW / source
            results[f"{source}_dir"] = {
                "exists": source_dir.exists(),
                "is_dir": source_dir.is_dir() if source_dir.exists() else False
            }

        self.manifest["checks"]["input_files"] = results
        return results

    def check_output_files(self) -> Dict[str, Any]:
        """Verify key output files exist and have correct structure."""
        print("[2/5] Checking output files...")
        results = {}

        for key, filepath in KEY_OUTPUTS.items():
            if verify_file_exists(filepath):
                size = filepath.stat().st_size
                results[key] = {
                    "exists": True,
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2)
                }
                self.manifest["summary"]["passed"] += 1

                # For TSV files, get column info
                if filepath.suffix == ".tsv":
                    col_info = get_tsv_column_info(filepath)
                    results[key]["columns"] = col_info
            else:
                results[key] = {"exists": False}
                self.manifest["summary"]["failed"] += 1
                self.issues.append(f"Missing output file: {filepath.name}")

        self.manifest["checks"]["output_files"] = results
        return results

    def check_row_counts(self) -> Dict[str, Any]:
        """Verify row counts in key output files."""
        print("[3/5] Checking row counts...")
        results = {}

        for key, (min_count, max_count) in EXPECTED_COUNTS.items():
            filepath = KEY_OUTPUTS.get(key)
            if not filepath or not verify_file_exists(filepath):
                results[key] = {"exists": False}
                continue

            actual_count = count_lines(filepath)
            in_range = min_count <= actual_count <= max_count
            status = "PASS" if in_range else "WARNING"

            results[key] = {
                "actual_rows": actual_count,
                "expected_range": [min_count, max_count],
                "in_range": in_range,
                "status": status
            }

            if in_range:
                self.manifest["summary"]["passed"] += 1
            else:
                self.manifest["summary"]["warnings"] += 1
                self.issues.append(
                    f"Row count out of range for {key}: "
                    f"{actual_count} (expected {min_count}-{max_count})"
                )

        self.manifest["checks"]["row_counts"] = results
        return results

    def check_package_versions(self) -> Dict[str, Any]:
        """Verify Python package versions."""
        print("[4/5] Checking package versions...")
        results = {}
        versions = check_python_packages()

        for pkg, version in versions.items():
            expected = REQUIRED_PACKAGES.get(pkg, "unknown")
            results[pkg] = {
                "installed": version,
                "expected": expected,
                "match": version.startswith(expected.split(".")[0]) if version != "NOT_INSTALLED" else False
            }

            if results[pkg]["match"]:
                self.manifest["summary"]["passed"] += 1
            else:
                if version == "NOT_INSTALLED":
                    self.manifest["summary"]["failed"] += 1
                    self.issues.append(f"Package {pkg} not installed")
                else:
                    self.manifest["summary"]["warnings"] += 1

        self.manifest["checks"]["package_versions"] = results
        return results

    def check_data_flow(self) -> Dict[str, Any]:
        """Verify data flow integrity between pipeline phases."""
        print("[5/5] Checking data flow integrity...")
        results = {}

        # Check that key output of one phase is input to next
        flow_checks = [
            {
                "phase": "FAERS_Download -> KG_Build",
                "input": KG / "nodes.tsv",
                "description": "KG nodes created from processed FAERS + molecular data"
            },
            {
                "phase": "KG_Build -> Embeddings",
                "input": KG / "triples.tsv",
                "description": "Triple file used for embedding training"
            },
        ]

        for check in flow_checks:
            exists = verify_file_exists(check["input"])
            results[check["phase"]] = {
                "output_exists": exists,
                "description": check["description"]
            }
            if exists:
                self.manifest["summary"]["passed"] += 1
            else:
                self.manifest["summary"]["failed"] += 1
                self.issues.append(
                    f"Data flow break at {check['phase']}: "
                    f"missing {check['input'].name}"
                )

        self.manifest["checks"]["data_flow"] = results
        return results

    def run_all_checks(self) -> Dict[str, Any]:
        """Execute all reproducibility checks."""
        print("\n" + "="*60)
        print("SexDiffKG REPRODUCIBILITY AUDIT")
        print("="*60)

        self.check_input_files()
        self.check_output_files()
        self.check_row_counts()
        self.check_package_versions()
        self.check_data_flow()

        # Add issues summary
        self.manifest["issues"] = self.issues
        self.manifest["summary"]["total_checks"] = (
            self.manifest["summary"]["passed"] +
            self.manifest["summary"]["failed"] +
            self.manifest["summary"]["warnings"]
        )

        return self.manifest

    def print_summary(self):
        """Print audit summary."""
        print("\n" + "="*60)
        print("AUDIT SUMMARY")
        print("="*60)
        s = self.manifest["summary"]
        print(f"Passed:   {s['passed']}")
        print(f"Failed:   {s['failed']}")
        print(f"Warnings: {s['warnings']}")
        print(f"Total:    {s['total_checks']}")

        if self.issues:
            print("\n" + "-"*60)
            print("ISSUES FOUND:")
            print("-"*60)
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")

    def save_manifest(self, filepath: Path):
        """Save manifest to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.manifest, f, indent=2)
        print(f"\nManifest saved to: {filepath}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    audit = ReproducibilityAudit()
    manifest = audit.run_all_checks()
    audit.print_summary()

    output_file = AUDIT_OUT / "reproducibility_manifest.json"
    audit.save_manifest(output_file)

    sys.exit(0 if audit.manifest["summary"]["failed"] == 0 else 1)
