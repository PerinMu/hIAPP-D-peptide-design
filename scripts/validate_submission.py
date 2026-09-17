#!/usr/bin/env python3
"""Compare a deposited-campaign rerun with committed results and audit its hashes.

This validates the historical hIAPP submission, not arbitrary new campaigns.
Run after run.sh. Paths may be absolute or relative to the current directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from generate_submission_results import sha256, validate_final_review, validate_screening


def validate(output_dir: Path, root: Path) -> None:
    generated = pd.read_csv(output_dir / "results.csv")
    committed = pd.read_csv(root / "results/submission/results.csv")
    workbook_path = root / "results/submission/results.xlsx"
    workbook = pd.read_excel(workbook_path, sheet_name="Submission")
    # Preserve row/column ordering and compare numerical values to CSV precision.
    for reference in (committed, workbook):
        pd.testing.assert_frame_equal(generated, reference, check_dtype=False,
                                      rtol=0, atol=1e-6)
    if set(pd.ExcelFile(workbook_path).sheet_names) != {"Submission", "Field Guide"}:
        raise ValueError("Unexpected workbook sheets")
    validate_screening(output_dir / "screening")
    validate_final_review(root / "results/final_candidates/final_12.csv",
                          output_dir / "screening")
    for name in ("hard_gate_904.csv", "p1_p2_p3_top32.csv", "p4_top10.csv"):
        pd.testing.assert_frame_equal(
            pd.read_csv(output_dir / "screening" / name),
            pd.read_csv(root / "results/screening" / name),
            check_dtype=False, rtol=0, atol=1e-10,
        )
    metadata = json.loads((output_dir / "run_metadata.json").read_text())
    if metadata["output_rows"] != 12 or metadata["output_sha256"] != sha256(output_dir / "results.csv"):
        raise ValueError("Output metadata mismatch")
    # Input hashes must match this deposited campaign, not merely files named by the run.
    expected_inputs = {
        sha256(root / "data/scored/merged_all_2_scored.csv"),
        sha256(root / "results/final_candidates/final_12.csv"),
    }
    if set(metadata["inputs"].values()) != expected_inputs:
        raise ValueError("Run inputs differ from the deposited campaign")
    structures = {Path(name).name: sha256(root / name) for name in generated["structure_file"]}
    if metadata["structure_sha256"] != structures:
        raise ValueError("Structure hashes differ from the current deposited structures")
    code = {name: sha256(root / name) for name in (
        "run.sh", "scripts/screen_candidates.py", "scripts/generate_submission_results.py")}
    if metadata["code_sha256"] != code:
        raise ValueError("Generation code has changed since the recorded run")
    screening = {p.name: sha256(p) for p in sorted((output_dir / "screening").glob("*.csv"))}
    if metadata["screening_sha256"] != screening:
        raise ValueError("Screening hashes differ from the recorded run")
    print("PASS: 12 candidates; review tiers; screening tables; CSV/XLSX; structures; run hashes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("results/submission"))
    args = parser.parse_args()
    validate(args.output_dir, Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    main()
