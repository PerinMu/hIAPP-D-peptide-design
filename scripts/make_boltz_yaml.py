#!/usr/bin/env python3
"""Generate one Boltz YAML input per peptide SMILES row."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip()).strip("._")
    if not cleaned:
        raise ValueError("Empty identifier after filename sanitization")
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("template_yaml", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--id-column", default="seq_rev")
    parser.add_argument("--smiles-column", default="smiles")
    parser.add_argument("--template-cif", type=Path,
                        help="Override the template CIF path stored in every generated YAML")
    args = parser.parse_args()

    template = args.template_yaml.read_text(encoding="utf-8")
    if template.count("__PEPTIDE_SMILES__") != 1:
        raise ValueError("Template must contain __PEPTIDE_SMILES__ exactly once")
    if args.template_cif:
        cif_value = json.dumps(str(args.template_cif))
        template, substitutions = re.subn(
            r"(?m)^(\s*-\s+cif:)\s*.*$", rf"\1 {cif_value}", template, count=1
        )
        if substitutions != 1:
            raise ValueError("Could not locate the first '- cif:' template line")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    seen = set()
    generated = 0
    with args.input_csv.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {args.id_column, args.smiles_column}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {sorted(missing)}")
        for row_number, row in enumerate(reader, 2):
            identifier = safe_name(row[args.id_column])
            smiles = str(row[args.smiles_column]).strip()
            if not smiles:
                raise ValueError(f"Empty SMILES at CSV row {row_number}")
            if identifier in seen:
                raise ValueError(f"Duplicate output identifier {identifier!r}")
            seen.add(identifier)
            document = template.replace("__PEPTIDE_SMILES__", smiles.replace("'", "''"))
            (args.output_dir / f"{identifier}.yaml").write_text(
                document, encoding="utf-8"
            )
            generated += 1
    print(f"Generated {generated} YAML files in {args.output_dir}")


if __name__ == "__main__":
    main()
