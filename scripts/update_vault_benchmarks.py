#!/usr/bin/env python3
"""Update vault benchmarks with actual validation results."""
import json
from pathlib import Path

vault = Path.home() / "AYURFEM-Vault/projects/sexdiffkg"
results_file = Path.home() / "sexdiffkg/results/validation_40_benchmarks.json"

with open(results_file) as f:
    data = json.load(f)

# Build the updated markdown
lines = [
    "# Expanded Validation Benchmarks — SexDiffKG",
    "",
    "## 40 Literature-Validated Drug-Sex-Adverse Event Associations",
    "",
    f"**Validation date:** {data['validation_date']}",
    f"**Signal file:** `~/sexdiffkg/results/signals_v2/sex_differential.parquet` (183,539 signals)",
    "",
    "---",
    "",
    "## Summary Statistics",
    "",
    f"| Metric | Value |",
    f"|--------|------:|",
    f"| Total benchmarks | {data['total_benchmarks']} |",
    f"| Found in signals | {data['found']}/40 ({data['coverage_pct']}%) |",
    f"| Correct direction | {data['correct_direction']}/{data['found']} ({data['precision_pct']}%) |",
    f"| Wrong direction | {data['wrong_direction']}/{data['found']} |",
    f"| Not found (drug or AE) | {data['not_found']}/40 |",
    "",
    "---",
    "",
    "## Full Results Table",
    "",
    "| # | Drug | Expected AE | Exp Dir | Status | Matched Signal | log(ROR ratio) |",
    "|---|------|-------------|---------|--------|----------------|:--------------:|",
]

for r in data['results']:
    num = r['num']
    drug = r['drug']
    ae = r['ae']
    exp = r['expected']
    status = r['status']
    detail = r['detail']

    emoji = {"CORRECT": "✅", "WRONG_DIR": "❌", "NOT_FOUND": "🔍", "AE_NOT_FOUND": "🔍", "SINGLE_SEX": "⚠️", "ERROR": "💥"}.get(status, "❓")

    if "matched:" in detail:
        parts = detail.split("matched: ")[1]
        matched_signal = parts.split(" log_ratio=")[0]
        log_ratio = parts.split("log_ratio=")[1].split(" ")[0]
    else:
        matched_signal = detail[:50]
        log_ratio = "—"

    lines.append(f"| {num} | {drug} | {ae} | {exp} | {emoji} {status} | {matched_signal[:45]} | {log_ratio} |")

lines.extend([
    "",
    "---",
    "",
    "## Analysis of Wrong-Direction Results",
    "",
    "Several benchmarks show opposite direction to literature expectation. Possible explanations:",
    "",
    "1. **FAERS reporting bias** — FAERS captures spontaneous reports, not incidence. If women report more generally, even M>F signals can appear F>M in reporting data.",
    "2. **Combination products** — Drug normalization matched combination formulations (e.g., HYDROCHLOROTHIAZIDE\\RAMIPRIL) where the combination drug's AE profile differs from the single agent.",
    "3. **Fuzzy AE matching** — LIKE-based matching may hit adjacent but different AE terms (e.g., 'Gastrointestinal neoplasm' instead of 'Gastrointestinal haemorrhage').",
    "4. **Age confounding** — Older women may dominate certain drug-AE pairs, shifting direction from biological sex effect to age-sex interaction.",
    "",
    "### Action Items for Improving Precision",
    "",
    "- [ ] Use exact MedDRA Preferred Term matching instead of LIKE",
    "- [ ] Run RxNorm-based normalization to reduce combination product noise",
    "- [ ] Add age-stratified sub-analysis for disputed benchmarks",
    "- [ ] Compute confidence intervals on log(ROR ratio) for each benchmark",
    "",
    "---",
    "",
    "## Literature Sources (PMIDs)",
    "",
    "| # | PMID | First Author | Year |",
    "|---|------|-------------|------|",
    "| 1 | 14999113 | Roden DM | 2004 |",
    "| 2 | 1616218 | Israili ZH | 1992 |",
    "| 3 | 9842954 | Drici MD | 1998 |",
    "| 4 | 11409663 | van der Linden PD | 2001 |",
    "| 5 | 15006590 | Rosenson RS | 2004 |",
    "| 6 | 11736865 | Garcia Rodriguez LA | 2001 |",
    "| 7 | 19475693 | Lucena MI | 2009 |",
    "| 8 | 8230644 | Makkar RR | 1993 |",
    "| 9 | 11966666 | Movig KL | 2002 |",
    "| 10 | 11046213 | Sarton E | 2000 |",
    "| 11 | — | Krecic-Shepard ME | 2004 |",
    "| 12 | 12409542 | Rathore SS | 2002 |",
    "| 13 | 24834516 | Clayton JA | 2014 |",
    "| 14 | FDA-2013-N-0012 | FDA | 2013 |",
    "| 15 | 11870163 | Seidman A | 2002 |",
    "| 16 | 40940052 | Bazmi et al | 2025 |",
    "| 17 | 37082456 | Díez-Escuté et al | 2023 |",
    "| 18 | 28767167 | Alharbi et al | 2017 |",
    "| 19 | 11338920 | Kim et al | 2000 |",
    "| 20 | 27578114 | Karalis et al | 2016 |",
    "| 21 | 25640999 | Magni et al | 2015 |",
    "| 22 | 37824028 | Gustafsson et al | 2023 |",
    "| 23 | 23027455 | Campesi et al | 2012 |",
    "| 24 | 41057033 | Montastruc et al | 2025 |",
    "| 25 | 24074752 | Sutcliffe et al | 2013 |",
    "| 26 | 38512019 | Ma & Wang | 2024 |",
    "| 27 | 35843842 | Floreani et al | 2022 |",
    "| 28 | 40817421 | Ramin et al | 2025 |",
    "| 29 | 40589655 | Moniem et al | 2025 |",
    "| 30 | 30819382 | Bots et al | 2019 |",
    "| 31 | 30157868 | Cui et al | 2018 |",
    "| 32 | 41438530 | Freitas et al | 2025 |",
    "| 33 | 40560472 | Maida et al | 2025 |",
    "| 34 | 39166106 | Hendriksen et al | 2024 |",
    "| 35 | 39602002 | Kthupi et al | 2024 |",
    "| 36 | 33439426 | Park et al | 2021 |",
    "| 37 | 39521365 | Martín-Pérez et al | 2024 |",
    "| 38 | 40449747 | Qi et al | 2025 |",
    "| 39 | 37013373 | Toniutto et al | 2023 |",
    "| 40 | 40604642 | Bazmi et al | 2025 |",
    "",
    "---",
    "",
    "*Generated by `~/sexdiffkg/scripts/validate_40_benchmarks.py` on 2026-02-27*",
    "*Results stored at `~/sexdiffkg/results/validation_40_benchmarks.json`*",
])

(vault / "Expanded_Validation_Benchmarks.md").write_text("\n".join(lines))
print(f"✓ Updated Expanded_Validation_Benchmarks.md ({len(lines)} lines)")

# Also update the full study with the new numbers
study = vault / "SexDiffKG_Full_Study.md"
text = study.read_text()

# Replace the old validation numbers
old_val = "86.7% coverage (13/15 found), 61.5% directional precision (8/13 correct direction)"
new_val = f"{data['coverage_pct']}% coverage ({data['found']}/40 found), {data['precision_pct']}% directional precision ({data['correct_direction']}/{data['found']} correct direction)"
if old_val in text:
    text = text.replace(old_val, new_val)
    study.write_text(text)
    print(f"✓ Updated SexDiffKG_Full_Study.md validation numbers")
else:
    # Try partial match
    import re
    pattern = r'86\.7% coverage \(13/15[^)]*\), 61\.5% directional precision \(8/13[^)]*\)'
    if re.search(pattern, text):
        text = re.sub(pattern, new_val, text)
        study.write_text(text)
        print(f"✓ Updated SexDiffKG_Full_Study.md validation numbers (regex)")
    else:
        print("⚠ Could not find old validation string in full study — manual update needed")
        # Search for nearby text
        for line_num, line in enumerate(text.split('\n')):
            if '86.7' in line or '61.5' in line or 'coverage' in line.lower() and 'precision' in line.lower():
                print(f"  Line {line_num}: {line[:100]}")

print("\nDone!")
