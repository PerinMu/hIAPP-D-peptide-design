#!/usr/bin/env python3
"""Collect Boltz confidence model_0 and matching affinity JSON into one CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def sample_id(path: Path, prefix: str, suffix: str = "") -> str | None:
    stem = re.sub(r"\(\d+\)$", "", path.stem)
    match = re.match(rf"^{re.escape(prefix)}(.+?){re.escape(suffix)}$", stem)
    return match.group(1) if match else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    affinity = {}
    affinity_keys = []
    for path in sorted(args.outputs_dir.glob("**/affinity_*.json")):
        sid = sample_id(path, "affinity_")
        if not sid:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        affinity.setdefault(sid, []).append((path, data))
        for key in data:
            if key not in affinity_keys:
                affinity_keys.append(key)

    rows, confidence_keys = [], []
    for path in sorted(args.outputs_dir.glob("**/confidence_*_model_0.json")):
        sid = sample_id(path, "confidence_", "_model_0")
        if not sid:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in data:
            if key not in confidence_keys:
                confidence_keys.append(key)
        matches = affinity.get(sid, [])
        same_parent = [item for item in matches if item[0].parent == path.parent]
        match = same_parent[0] if len(same_parent) == 1 else matches[0] if len(matches) == 1 else None
        row = {"sample_id": sid, "confidence_json_path": str(path), "affinity_json_path": ""}
        row.update(data)
        if match:
            row["affinity_json_path"] = str(match[0])
            row.update(match[1])
        rows.append(row)

    fields = ["sample_id", "confidence_json_path", "affinity_json_path"] + confidence_keys + affinity_keys
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(rows, key=lambda x: (x["sample_id"], x["confidence_json_path"])):
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})
    print(f"Collected {len(rows)} model_0 confidence rows to {args.output}")


if __name__ == "__main__":
    main()

