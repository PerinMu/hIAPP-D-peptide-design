#!/usr/bin/env python3
"""Create a blank, auditable manual structure-review sheet."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("top32", type=Path)
    parser.add_argument("p4_top10", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    top = pd.read_csv(args.top32)
    p4 = pd.read_csv(args.p4_top10)
    top["review_pool"] = top["priority"]
    p4["review_pool"] = "P4"
    fields = [
        "review_pool", "name", "sequence", "d_sequence", "seq_rev",
        "structure_bottleneck", "overall_score", "p4_score",
    ]
    combined = pd.concat([top, p4], ignore_index=True, sort=False)
    review = combined.reindex(columns=fields).copy()
    review["model0_cif"] = ""
    review["contacts_target_21_37"] = ""
    review["interface_hbond_count"] = ""
    review["steric_clash_flag"] = ""
    review["extended_or_implausible_flag"] = ""
    review["synthesis_flag"] = ""
    review["selected_for_experiment"] = ""
    review["reviewer"] = ""
    review["review_date"] = ""
    review["decision_reason"] = ""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    review.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Review rows: {len(review)} (P1-P3={len(top)}, P4={len(p4)})")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()

