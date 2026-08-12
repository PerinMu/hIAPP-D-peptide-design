#!/usr/bin/env python3
"""Collect model_0 CIF files and write a manifest without overwriting outputs."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("outputs_dir", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)

    rows = []
    for task in sorted(x for x in args.outputs_dir.iterdir() if x.is_dir()):
        cifs = sorted(task.glob("**/*_model_0.cif"))
        for index, source in enumerate(cifs, 1):
            suffix = "" if len(cifs) == 1 else f"_{index}"
            name = f"{task.name}{suffix}_model_0.cif"
            shutil.copy2(source, args.destination / name)
            rows.append({"task_dir": task.name, "copied_name": name, "source_cif": str(source)})
    with (args.destination / "manifest.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else
                                ["task_dir", "copied_name", "source_cif"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Copied {len(rows)} model_0 structures to {args.destination}")


if __name__ == "__main__":
    main()

