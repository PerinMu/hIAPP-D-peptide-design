#!/usr/bin/env python3
"""Copy every expected YAML whose sample ID has no model_0 CIF output."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("outputs_dir", type=Path)
    parser.add_argument("yaml_source_dir", type=Path)
    parser.add_argument("retry_dir", type=Path)
    args = parser.parse_args()

    args.retry_dir.mkdir(parents=True, exist_ok=True)
    yaml_files = sorted([
        *args.yaml_source_dir.glob("*.yaml"),
        *args.yaml_source_dir.glob("*.yml"),
    ])
    if not yaml_files:
        raise SystemExit(f"No YAML inputs found in {args.yaml_source_dir}")

    successful: set[str] = set()
    for cif in args.outputs_dir.glob("**/*_model_0.cif"):
        suffix = "_model_0"
        if cif.stem.endswith(suffix):
            successful.add(cif.stem[:-len(suffix)])

    manifest = []
    copied = 0
    for source in yaml_files:
        sample_id = source.stem
        success = sample_id in successful
        manifest.append((sample_id, "success" if success else "missing", source.name))
        if not success:
            shutil.copy2(source, args.retry_dir / source.name)
            copied += 1

    with (args.retry_dir / "missing_model0_manifest.tsv").open("w", encoding="utf-8") as handle:
        handle.write("sample_id\tmodel0_status\tsource_yaml\n")
        for row in manifest:
            handle.write("\t".join(row) + "\n")
    print(f"Expected YAMLs: {len(yaml_files)}")
    print(f"Successful sample IDs: {sum(row[1] == 'success' for row in manifest)}")
    print(f"Retry YAMLs: {copied}")


if __name__ == "__main__":
    main()
