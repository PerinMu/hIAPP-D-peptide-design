#!/usr/bin/env python3
"""Merge design CSV files, sum duplicate counts, and retain source labels."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path


def parse_source(spec: str) -> tuple[Path, str]:
    try:
        path, label = spec.rsplit("=", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use PATH=LABEL") from exc
    if not path or not label:
        raise argparse.ArgumentTypeError("Use non-empty PATH=LABEL")
    return Path(path), label


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", type=parse_source, required=True,
                        help="Input CSV and provenance label as PATH=LABEL; repeat as needed")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sequence-column", default="sequence")
    parser.add_argument("--count-column", default="count")
    args = parser.parse_args()

    merged: OrderedDict[str, dict] = OrderedDict()
    input_rows = 0
    for path, label in args.input:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {args.sequence_column, args.count_column}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"{path} missing columns: {sorted(missing)}")
            for row_number, row in enumerate(reader, 2):
                input_rows += 1
                sequence = "".join(str(row[args.sequence_column]).split()).upper()
                if not sequence:
                    raise ValueError(f"Empty sequence in {path}:{row_number}")
                count = int(row[args.count_column])
                item = merged.setdefault(sequence, {
                    "sequence": sequence, "count": 0, "sources": [],
                })
                item["count"] += count
                if label not in item["sources"]:
                    item["sources"].append(label)

    rows = sorted(merged.values(), key=lambda x: (-x["count"], x["sequence"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "sequence", "count", "source"])
        writer.writeheader()
        for item in rows:
            writer.writerow({
                "name": f"{item['sequence']}_{item['count']}",
                "sequence": item["sequence"],
                "count": item["count"],
                "source": "; ".join(item["sources"]),
            })
    print(f"Merged {input_rows} input rows into {len(rows)} unique sequences: {args.output}")


if __name__ == "__main__":
    main()

