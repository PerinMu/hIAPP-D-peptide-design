#!/usr/bin/env python3
"""Create the standardized competition candidate manifest and run metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata as package_metadata
from pathlib import Path

import pandas as pd

from screen_candidates import compute_scores


TRACK = "Track 1 - AI Macromolecule and Peptide Drug Design"
MODEL_VERSION = (
    "BoltzGen/BoltzIF 0.2.0; Boltz-2 2.2.1 "
    "(production environment recovered 2026-08-15)"
)
TARGET_SEQUENCE = "HSSNNFGAILSSTNVGSNTY"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_version(name: str) -> str:
    try:
        return package_metadata.version(name)
    except package_metadata.PackageNotFoundError:
        return "not-installed"


def git_revision(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unavailable"


def require_unique(table: pd.DataFrame, column: str, label: str) -> None:
    if table[column].isna().any() or not table[column].is_unique:
        raise ValueError(f"{label} must contain non-null, unique {column} values")


def build_results(scores_path: Path, final_path: Path, structures_dir: Path) -> pd.DataFrame:
    raw = pd.read_csv(scores_path)
    scored = compute_scores(raw)
    final = pd.read_csv(final_path).sort_values("final_rank")
    require_unique(final, "d_peptide_sequence", "Final manifest")
    require_unique(scored, "d_sequence", "Scored design pool")

    selected = final.merge(
        scored,
        left_on="d_peptide_sequence",
        right_on="d_sequence",
        how="left",
        validate="one_to_one",
        suffixes=("_final", "_score"),
    )
    if selected["overall_score"].isna().any():
        missing = selected.loc[selected["overall_score"].isna(), "d_peptide_sequence"].tolist()
        raise ValueError(f"Final candidates missing from scored pool: {missing}")

    missing_structures = [
        name for name in selected["structure_file"] if not (structures_dir / name).is_file()
    ]
    if missing_structures:
        raise FileNotFoundError(f"Missing final structure files: {missing_structures[:3]}")

    for name in selected["structure_file"]:
        text = (structures_dir / name).read_text(encoding="utf-8")
        if "A 1 'Model subunit A'" not in text or "X 2 'Model subunit X'" not in text:
            raise ValueError(f"Unexpected chain convention in {name}")
        atom_elements = {
            line.split()[2]
            for line in text.splitlines()
            if line.startswith(("ATOM ", "HETATM ")) and len(line.split()) > 2
        }
        if "H" in atom_elements:
            raise ValueError(f"Expected heavy-atom-only deposited model, found hydrogen in {name}")

    result = pd.DataFrame({
        "candidate_id": selected["final_rank"].map(lambda value: f"HIAPP-DP-{int(value):03d}"),
        "final_rank": selected["final_rank"].astype(int),
        "track": TRACK,
        "priority_tier": selected["priority"],
        "candidate_type": "linear reverse-D peptide",
        "d_peptide_sequence": selected["d_peptide_sequence"],
        "l_design_sequence": selected["l_sequence_final"],
        "smiles": selected["smiles"],
        "target": "human islet amyloid polypeptide (hIAPP)",
        "target_sequence": TARGET_SEQUENCE,
        "target_template": "PDB 9ULZ, chain D residues 19-37",
        "intended_binding_region": "hIAPP residues 21-37",
        "structure_file": selected["structure_file"].map(
            lambda name: f"results/final_candidates/structures/{name}"
        ),
        "structure_format": "mmCIF",
        "coordinate_unit": "angstrom",
        "target_chain_id": "A",
        "ligand_chain_id": "X",
        "protonation_status": "not assigned",
        "hydrogen_representation": "heavy atoms only; no explicit hydrogens",
        "ptm": selected["ptm"],
        "iptm": selected["iptm"],
        "min_ptm_iptm": selected["structure_bottleneck"],
        "confidence_score": selected["confidence_score"],
        "complex_iplddt": selected["complex_iplddt"],
        "complex_ipde": selected["complex_ipde"],
        "affinity_pred_value_head_0": selected["affinity_pred_value"],
        "affinity_pred_value_head_1": selected["affinity_pred_value1"],
        "affinity_pred_value_head_2": selected["affinity_pred_value2"],
        "affinity_probability_head_0": selected["affinity_probability_binary"],
        "affinity_probability_head_1": selected["affinity_probability_binary1"],
        "affinity_probability_head_2": selected["affinity_probability_binary2"],
        "affinity_consensus_relative": selected["affinity_consensus"],
        "structure_quality_relative": selected["structure_quality"],
        "developability_relative": selected["developability_score"],
        "overall_priority_score": selected["overall_score"],
        "solubility_tendency_0_100": selected["solubility_tendency_score_0_100"],
        "aggregation_risk_0_100": selected["aggregation_risk_score_0_100"],
        "sequence_stability_0_100": selected["sequence_stability_score_0_100"],
        "peptide_drug_likeness_0_100": selected["peptide_drug_likeness_score_0_100"],
        "model_and_version": MODEL_VERSION,
        "experimental_status": selected["experimental_status"],
        "measured_activity": selected["wetlab_activity"],
        "remarks": (
            "Computational shortlist; relative model/heuristic scores are not measured affinity "
            "or aggregation inhibition."
        ),
    })
    numeric = result.select_dtypes(include="number").columns.difference(["final_rank"])
    result[numeric] = result[numeric].round(6)
    return result


def validate_screening(screening_dir: Path) -> None:
    expected = {
        "hard_gate_904.csv": 904,
        "p1_p2_p3_top32.csv": 32,
        "p4_top10.csv": 10,
    }
    for filename, rows in expected.items():
        path = screening_dir / filename
        if not path.is_file() or len(pd.read_csv(path)) != rows:
            raise ValueError(f"Screening artifact failed validation: {path} (expected {rows} rows)")


def validate_final_review(final_path: Path, screening_dir: Path) -> None:
    """Verify the historical human choices against the recomputed tier pools."""
    final = pd.read_csv(final_path).sort_values("final_rank")
    if final["final_rank"].tolist() != list(range(1, 13)):
        raise ValueError("Final ranks must be the consecutive integers 1 through 12")
    if final["priority"].value_counts().to_dict() != {"P1": 8, "P2": 1, "P3": 1, "P4": 2}:
        raise ValueError("Historical final tier composition must be P1/P2/P3/P4 = 8/1/1/2")
    main_review = pd.read_csv(screening_dir / "p1_p2_p3_top32.csv")
    p4_review = pd.read_csv(screening_dir / "p4_top10.csv")
    pools = {tier: set(main_review.loc[main_review["priority"] == tier, "d_sequence"])
             for tier in ("P1", "P2", "P3")}
    pools["P4"] = set(p4_review["d_sequence"])
    for row in final.itertuples():
        if row.d_peptide_sequence not in pools[row.priority]:
            raise ValueError(f"Candidate is outside its review tier: {row.d_peptide_sequence}")
        if row.d_peptide_sequence != row.l_sequence[::-1].lower():
            raise ValueError(f"Reverse-D sequence mismatch: {row.d_peptide_sequence}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--final", type=Path, required=True)
    parser.add_argument("--structures", type=Path, required=True)
    parser.add_argument("--screening-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()

    validate_screening(args.screening_dir)
    validate_final_review(args.final, args.screening_dir)
    results = build_results(args.scores, args.final, args.structures)
    if len(results) != 12 or not results["candidate_id"].is_unique:
        raise ValueError("Standardized output must contain exactly 12 unique candidates")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False, encoding="utf-8")

    root = Path(__file__).resolve().parents[1]
    run_metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entry_point": "bash run.sh",
        "repository_commit": git_revision(root),
        "track": TRACK,
        "model_and_version": MODEL_VERSION,
        "production_model_version_caveat": (
            "BoltzGen 0.2.0 is confirmed by the historical inverse-folding log. "
            "Boltz 2.2.1 is the still-installed environment recovered on 2026-08-15; "
            "historical prediction logs did not print its version. Checkpoint SHA256 values "
            "and remaining evidence are recorded in MODEL_CARD.md."
        ),
        "inputs": {
            str(args.scores): sha256(args.scores),
            str(args.final): sha256(args.final),
        },
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "pandas": package_version("pandas"),
            "numpy": package_version("numpy"),
        },
        "randomness": (
            "No random operation is used by this CPU reproduction entry point. Neural generation "
            "and prediction are separate stochastic GPU stages documented in the full notebook."
        ),
        "code_sha256": {
            str(path.relative_to(root)): sha256(path)
            for path in [root / "run.sh", root / "scripts/screen_candidates.py",
                         root / "scripts/generate_submission_results.py"]
        },
        "structure_sha256": {
            name: sha256(args.structures / name)
            for name in pd.read_csv(args.final)["structure_file"]
        },
        "screening_sha256": {
            path.name: sha256(path) for path in sorted(args.screening_dir.glob("*.csv"))
        },
        "output_rows": len(results),
        "output_sha256": sha256(args.output),
    }
    args.metadata.write_text(json.dumps(run_metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} candidates to {args.output}")


if __name__ == "__main__":
    main()
