#!/usr/bin/env python3
"""Merge design metadata with one or more Boltz score batches."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", action="append", type=Path, required=True,
                        help="Design/reference CSV; repeat for additional tables")
    parser.add_argument("--scores", action="append", type=Path, required=True,
                        help="Collected Boltz score CSV; later files override retries")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--design-key", default="seq_rev")
    parser.add_argument("--score-key", default="sample_id")
    args = parser.parse_args()

    designs = pd.concat(
        [pd.read_csv(path, encoding="utf-8-sig") for path in args.design],
        ignore_index=True,
        sort=False,
    )
    scores = pd.concat(
        [pd.read_csv(path, encoding="utf-8-sig") for path in args.scores],
        ignore_index=True,
        sort=False,
    )
    for frame, key, label in [
        (designs, args.design_key, "design"),
        (scores, args.score_key, "score"),
    ]:
        if key not in frame.columns:
            raise ValueError(f"{label} table is missing key column {key!r}")
        frame[key] = frame[key].astype("string").str.strip()

    empty_design = designs[args.design_key].isna() | designs[args.design_key].eq("")
    if empty_design.any():
        print(f"Dropping {int(empty_design.sum())} blank design/reference rows")
        designs = designs.loc[~empty_design].copy()

    duplicated = scores.duplicated(args.score_key, keep=False)
    if duplicated.any():
        print(
            f"Score retries: {scores.loc[duplicated, args.score_key].nunique()} IDs; "
            "keeping the last batch occurrence"
        )
    scores = scores.drop_duplicates(args.score_key, keep="last")

    collisions = {
        column: f"boltz_{column}"
        for column in scores.columns
        if column != args.score_key and column in designs.columns
    }
    scores = scores.rename(columns=collisions)
    merged = designs.merge(
        scores,
        how="left",
        left_on=args.design_key,
        right_on=args.score_key,
        validate="many_to_one",
        sort=False,
    )
    merged = merged.drop(columns=[args.score_key], errors="ignore")
    matched = int(merged["confidence_json_path"].notna().sum()) \
        if "confidence_json_path" in merged else 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Design rows: {len(designs)}")
    print(f"Unique score IDs: {len(scores)}")
    print(f"Rows with model_0 confidence output: {matched}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
