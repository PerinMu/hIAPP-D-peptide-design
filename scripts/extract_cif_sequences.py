#!/usr/bin/env python3
"""Extract and count one polymer entity sequence from BoltzGen CIF files.

BoltzGen design CIFs store the designed peptide as the first row of the
``_entity_poly`` loop and the fixed hIAPP target as the second row.  The entity
index is configurable so the assumption is explicit and auditable.
"""

from __future__ import annotations

import argparse
import csv
import shlex
from collections import Counter
from pathlib import Path


CANONICAL = set("ACDEFGHIKLMNPQRSTVWY")


def entity_poly_sequences(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "loop_":
            continue
        headers: list[str] = []
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].lstrip().startswith("_"):
            headers.append(lines[cursor].strip())
            cursor += 1
        if "_entity_poly.pdbx_seq_one_letter_code" not in headers:
            continue

        sequence_column = headers.index("_entity_poly.pdbx_seq_one_letter_code")
        rows: list[list[str]] = []
        while cursor < len(lines):
            value = lines[cursor].strip()
            if not value or value == "#":
                cursor += 1
                continue
            if value == "loop_" or value.startswith("_") or value.startswith("data_"):
                break
            tokens = shlex.split(value, comments=False, posix=True)
            if len(tokens) != len(headers):
                raise ValueError(
                    f"Unsupported multiline _entity_poly row in {path}:{cursor + 1}"
                )
            rows.append(tokens)
            cursor += 1
        return [row[sequence_column].replace(" ", "").upper() for row in rows]
    raise ValueError(f"No _entity_poly sequence loop found in {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--entity-index", type=int, default=1,
                        help="One-based _entity_poly row; BoltzGen designs use 1")
    parser.add_argument("--glob", default="*.cif")
    parser.add_argument("--exclude-suffix", default="_native.cif")
    args = parser.parse_args()

    files = sorted(
        path for path in args.input_dir.glob(args.glob)
        if path.is_file() and not path.name.endswith(args.exclude_suffix)
    )
    if not files:
        raise SystemExit(f"No CIF files found in {args.input_dir}")

    counts: Counter[str] = Counter()
    failures: list[str] = []
    for path in files:
        try:
            sequences = entity_poly_sequences(path)
            if not 1 <= args.entity_index <= len(sequences):
                raise ValueError(
                    f"entity index {args.entity_index} unavailable; found {len(sequences)}"
                )
            sequence = sequences[args.entity_index - 1]
            unknown = set(sequence) - CANONICAL
            if not sequence or unknown:
                raise ValueError(f"noncanonical sequence {sequence!r}; symbols={sorted(unknown)}")
            counts[sequence] += 1
        except Exception as exc:  # report every malformed file together
            failures.append(f"{path}: {exc}")

    if failures:
        preview = "\n".join(failures[:20])
        raise RuntimeError(f"Failed to parse {len(failures)} CIF files:\n{preview}")

    rows = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "sequence", "count"])
        writer.writeheader()
        for sequence, count in rows:
            writer.writerow({"name": f"{sequence}_{count}", "sequence": sequence, "count": count})

    print(f"Parsed {len(files)} CIF files")
    print(f"Unique sequences: {len(rows)}")
    print(f"Duplicate copies: {len(files) - len(rows)}")
    print(f"Output: {args.output_csv}")


if __name__ == "__main__":
    main()

