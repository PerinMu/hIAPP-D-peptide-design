#!/usr/bin/env python3
"""Convert upper-case L / lower-case D peptide sequences to linear SMILES."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


SIDE_CHAINS = {
    "A": "C", "R": "CCCNC(=N)N", "N": "CC(=O)N", "D": "CC(=O)O",
    "C": "CS", "Q": "CCC(=O)N", "E": "CCC(=O)O", "G": None,
    "H": "CC1=CN=C[NH]1", "I": "[C@@H](C)CC", "L": "CC(C)C",
    "K": "CCCCN", "M": "CCSC", "F": "CC1=CC=CC=C1", "P": None,
    "S": "CO", "T": "[C@H](O)C", "W": "CC1=CNC2=CC=CC=C12",
    "Y": "CC1=CC=C(O)C=C1", "V": "C(C)C",
}


def peptide_to_smiles(sequence: str) -> str:
    sequence = "".join(str(sequence).split())
    if not sequence or any(aa.upper() not in SIDE_CHAINS for aa in sequence):
        raise ValueError(f"Unsupported or empty peptide sequence: {sequence!r}")
    parts = []
    for index, aa in enumerate(sequence):
        final = index == len(sequence) - 1
        c_term = "C(=O)O" if final else "C(=O)"
        upper = aa.upper()
        if upper == "G":
            parts.append("NCC(=O)O" if final else "NCC(=O)")
        elif upper == "P":
            parts.append(f"N1[C{'@@' if aa.isupper() else '@'}H](CCC1){c_term}")
        elif aa == "I":
            parts.append(f"N[C@@H]([C@@H](C)CC){c_term}")
        elif aa == "i":
            parts.append(f"N[C@H]([C@H](C)CC){c_term}")
        elif aa == "T":
            parts.append(f"N[C@@H]([C@H](O)C){c_term}")
        elif aa == "t":
            parts.append(f"N[C@H]([C@@H](O)C){c_term}")
        else:
            chirality = "@@" if aa.isupper() else "@"
            parts.append(f"N[C{chirality}H]({SIDE_CHAINS[upper]}){c_term}")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--sequence-column", default="seq_rev")
    parser.add_argument("--smiles-column", default="smiles")
    args = parser.parse_args()

    with args.input.open(encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        if args.sequence_column not in (reader.fieldnames or []):
            raise ValueError(f"Missing sequence column {args.sequence_column!r}")
        fields = list(reader.fieldnames or [])
        if args.smiles_column not in fields:
            fields.append(args.smiles_column)
        rows = []
        for row_number, row in enumerate(reader, 2):
            try:
                row[args.smiles_column] = peptide_to_smiles(row[args.sequence_column])
            except ValueError as exc:
                raise ValueError(f"{exc} at CSV row {row_number}") from exc
            rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} peptide SMILES to {args.output}")


if __name__ == "__main__":
    main()

