#!/usr/bin/env python3
"""Validate a completed review sheet and export the experimental shortlist."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("review_csv", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-total", type=int, default=12)
    parser.add_argument("--expected-p4", type=int, default=2)
    args = parser.parse_args()
    table = pd.read_csv(args.review_csv, encoding="utf-8-sig")
    required = {"review_pool", "selected_for_experiment", "reviewer", "review_date", "decision_reason"}
    missing = required - set(table.columns)
    if missing:
        raise ValueError(f"Missing review columns: {sorted(missing)}")
    selected_text = table["selected_for_experiment"].fillna("").astype(str).str.strip().str.lower()
    selected = table[selected_text.isin({"yes", "y", "true", "1"})].copy()
    if len(selected) != args.expected_total:
        raise ValueError(f"Expected {args.expected_total} selected rows, found {len(selected)}")
    p4_count = int(selected["review_pool"].eq("P4").sum())
    if p4_count != args.expected_p4:
        raise ValueError(f"Expected {args.expected_p4} P4 rows, found {p4_count}")
    for column in ["reviewer", "review_date", "decision_reason"]:
        if selected[column].isna().any() or selected[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Selected rows require non-empty {column}")
    selected.insert(0, "selection_order", range(1, len(selected) + 1))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Final selection: {len(selected)}; P4: {p4_count}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
