#!/usr/bin/env python3
"""Append deterministic sequence-level physicochemical ranking descriptors.

These are transparent heuristics used only for within-pool prioritization. They
are not experimental solubility, aggregation, permeability or stability data.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


AA = set("ACDEFGHIKLMNPQRSTVWY")
HYDROPHOBIC = set("AVILMFWY")
AROMATIC = set("FWY")
POLAR = set("RNDQEHKSTCY")
RESIDUE_MASS = {
    "A": 71.0788, "R": 156.1875, "N": 114.1038, "D": 115.0886,
    "C": 103.1388, "E": 129.1155, "Q": 128.1307, "G": 57.0519,
    "H": 137.1411, "I": 113.1594, "L": 113.1594, "K": 128.1741,
    "M": 131.1926, "F": 147.1766, "P": 97.1167, "S": 87.0782,
    "T": 101.1051, "W": 186.2132, "Y": 163.1760, "V": 99.1326,
}
KD = {
    "I": 4.5, "V": 4.2, "L": 3.8, "F": 2.8, "C": 2.5, "M": 1.9,
    "A": 1.8, "G": -0.4, "T": -0.7, "S": -0.8, "W": -0.9,
    "Y": -1.3, "P": -1.6, "H": -3.2, "E": -3.5, "Q": -3.5,
    "D": -3.5, "N": -3.5, "K": -3.9, "R": -4.5,
}
FULL_IAPP = "KCNTATCATQRLANFLVHSSNNFGAILSSTNVGSNTY"


def clamp(value: float, low: float = 0, high: float = 1) -> float:
    return max(low, min(high, value))


def js_round(value: float, digits: int = 2) -> float:
    """Match JavaScript Math.round used to create the committed reference table."""
    factor = 10 ** digits
    return math.floor((value + np.finfo(float).eps) * factor + 0.5) / factor


def mutate(sequence: str, changes: list[tuple[int, str]]) -> str:
    chars = list(sequence)
    for position, residue in changes:
        chars[position - 1] = residue
    return "".join(chars)


def derive_sequence(raw_value: object, name_value: object) -> tuple[str, str, str]:
    raw = "" if pd.isna(raw_value) else str(raw_value).replace("\u00a0", " ").strip()
    name = "" if pd.isna(name_value) else str(name_value).replace("\u00a0", " ").strip()
    if not raw:
        return "", "MISSING_SEQUENCE", "No sequence available; scores left blank."
    direct = raw.upper()
    if set(direct) <= AA:
        return direct, "OK", ""

    reconstructed = {
        "IAPP-GI": FULL_IAPP,
        "Pramlintide (PM)": mutate(FULL_IAPP, [(25, "P"), (28, "P"), (29, "P")]),
        "Arg-1": FULL_IAPP[:13] + "RRRR" + FULL_IAPP[17:],
        "Arg-2": FULL_IAPP[:22] + "RRRR" + FULL_IAPP[26:],
        "Mem-T": "DDDDD" + FULL_IAPP[17:],
    }
    if name in reconstructed:
        return reconstructed[name], "RECONSTRUCTED", (
            "Canonical sequence reconstructed from the row description; "
            "stated modifications are not modeled."
        )
    if name == "C5":
        return "NFGAILSS", "APPROX_MODIFIED", (
            "Peptide moiety scored; pyromellitic-acid conjugation is not modeled."
        )
    explicit = {
        "AP5": ("RGNWNESKMNEYSGWMLMLTMGR",
                "D-residue stereochemistry, N-acetylation, and C-terminal amidation are not modeled."),
        "β-cap-WW2": ("WKKLTVWIPGKWITVSAWTG",
                     "N-terminal cap, D-Pro stereochemistry, and C-terminal amidation are not modeled."),
        "C14-RRRR-NH2": ("RRRR",
                         "C14 lipid chain and C-terminal amidation are not modeled."),
    }
    if name in explicit:
        seq, note = explicit[name]
        return seq, "APPROX_MODIFIED", note + " Sequence-only approximation."

    work = raw
    notes: list[str] = []
    tests = [
        (r"Glc", "glycosylation ignored"),
        (r"N-Me", "N-methylation ignored"),
        (r"cyclo|cyclized", "cyclization ignored"),
        (r"\bAc[-W]", "N-acetylation/cap ignored"),
        (r"C14|tetradecanoyl", "C14 lipid chain ignored"),
        (r"NH2|NH₂|CONH2", "terminal amidation ignored"),
        (r"ΔF", "ΔF approximated as F"),
        (r"Aib", "Aib approximated as A"),
        (r"X2", "X2 approximated as F"),
    ]
    for pattern, note in tests:
        if re.search(pattern, work, re.I):
            notes.append(note)
    if re.search(r"[a-z]", re.sub(r"^(L|D)-", "", work, flags=re.I)):
        notes.append("D/L stereochemistry not modeled")

    work = re.sub(
        r"\([^)]*(?:p\s*=\s*D-Pro|lower[- ]case residues are D-aa|cyclized|C14\s*=)[^)]*\)",
        "",
        work,
        flags=re.I,
    )
    work = re.sub(r"\((?:GlcNAc|Glc|N-Me)\)", "", work, flags=re.I)
    work = re.sub(r"\(L\)$", "", work, flags=re.I)
    work = re.sub(r"^\s*[LD]-\s*", "", work, flags=re.I)
    work = re.sub(r"^\s*C14-", "", work, flags=re.I)
    work = re.sub(r"^\s*AcW-", "W-", work, flags=re.I)
    work = re.sub(r"^\s*Ac-", "", work, flags=re.I)
    work = re.sub(r"^\s*H2N-", "", work, flags=re.I)
    work = re.sub(r"-(?:CO)?NH2$", "", work, flags=re.I)
    work = re.sub(r"-NH₂$", "", work, flags=re.I)
    work = re.sub(r"^\s*cyclo\(", "", work, flags=re.I)
    work = re.sub(r"\)\s*$", "", work)
    work = re.sub(r"Cys", "C", work, flags=re.I)
    work = re.sub(r"Aib", "A", work, flags=re.I)
    work = re.sub(r"X2", "F", work, flags=re.I).replace("ΔF", "F")
    work = re.sub(r"[\s-]", "", work).upper()
    if not work or not set(work) <= AA:
        return "", "UNSUPPORTED_SEQUENCE", f"Could not derive a canonical sequence from: {raw}"
    note = "; ".join(dict.fromkeys(notes))
    note = note + ". Sequence-only approximation." if note else "Sequence normalized from descriptive notation."
    return work, "APPROX_MODIFIED", note


def net_charge(sequence: str, ph: float) -> float:
    count = sequence.count
    positive = 1 / (1 + 10 ** (ph - 9.69))
    positive += count("H") / (1 + 10 ** (ph - 6.00))
    positive += count("K") / (1 + 10 ** (ph - 10.50))
    positive += count("R") / (1 + 10 ** (ph - 12.50))
    negative = 1 / (1 + 10 ** (2.34 - ph))
    negative += count("D") / (1 + 10 ** (3.86 - ph))
    negative += count("E") / (1 + 10 ** (4.25 - ph))
    negative += count("C") / (1 + 10 ** (8.33 - ph))
    negative += count("Y") / (1 + 10 ** (10.07 - ph))
    return positive - negative


def estimate_pi(sequence: str) -> float:
    low, high = 0.0, 14.0
    for _ in range(80):
        middle = (low + high) / 2
        if net_charge(sequence, middle) > 0:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def score(sequence: str, parse_note: str) -> dict[str, object]:
    length = len(sequence)
    mw = sum(RESIDUE_MASS[aa] for aa in sequence) + 18.01528
    charge = net_charge(sequence, 7.0)
    charge_density = abs(charge) / length
    pi = estimate_pi(sequence)
    gravy = sum(KD[aa] for aa in sequence) / length
    fraction = lambda group: sum(aa in group for aa in sequence) / length
    polar = fraction(POLAR); hydrophobic = fraction(HYDROPHOBIC); aromatic = fraction(AROMATIC)
    run = best = 0
    for aa in sequence:
        run = run + 1 if aa in HYDROPHOBIC else 0
        best = max(best, run)

    agg_base = (
        0.30 * clamp((gravy + 0.5) / 3.0)
        + 0.25 * clamp((hydrophobic - 0.30) / 0.40)
        + 0.20 * clamp((best - 2) / 4)
        + 0.15 * clamp((aromatic - 0.05) / 0.25)
        + 0.10 * clamp((length - 8) / 30)
    )
    aggregation = 100 * clamp(agg_base * (1 - 0.30 * clamp(charge_density / 0.25)))
    solubility = 100 * clamp(
        0.35 * clamp((1.5 - gravy) / 3.5)
        + 0.20 * clamp((polar - 0.25) / 0.45)
        + 0.15 * clamp(charge_density / 0.22)
        + 0.15 * (1 - clamp((best - 2) / 4))
        + 0.15 * (1 - clamp((mw - 800) / 2500))
    )
    permeability = 100 * clamp(
        0.30 * (1 - clamp((mw - 500) / 1800))
        + 0.20 * (1 - clamp(abs(charge) / 3))
        + 0.15 * (1 - clamp((polar - 0.25) / 0.50))
        + 0.15 * (1 - clamp(abs(gravy - 0.5) / 2.5))
        + 0.20 * (1 - clamp((length - 4) / 12))
    )
    oxidation = sequence.count("M") + sequence.count("W")
    deamidation = len(re.findall(r"N(?=[GSTAQ])", sequence))
    aspartate = len(re.findall(r"D(?=[GSTP])", sequence))
    nterm = int(sequence.startswith(("Q", "E")))
    unpaired_cys = sequence.count("C") % 2
    liabilities = oxidation + deamidation + aspartate + nterm + unpaired_cys
    stability = clamp(
        100 - 8 * oxidation - 8 * deamidation - 6 * aspartate
        - 8 * nterm - 10 * unpaired_cys - min(20, max(0, length - 12) * 0.6),
        0, 100,
    )
    drug_likeness = clamp(
        0.35 * solubility + 0.25 * (100 - aggregation)
        + 0.20 * permeability + 0.20 * stability,
        0, 100,
    )
    issues = []
    if solubility < 40: issues.append("low solubility tendency")
    if aggregation >= 65: issues.append("high aggregation risk")
    if permeability < 40: issues.append("low passive-permeability tendency")
    if stability < 60: issues.append("sequence liability motifs")
    if mw > 2000: issues.append("high molecular size")
    if abs(charge) > 3: issues.append("high absolute charge")
    if parse_note: issues.append(parse_note)
    classify = lambda value, high=70, medium=40: "High" if value >= high else "Moderate" if value >= medium else "Low"
    return {
        "sequence_length_aa": length,
        "molecular_weight_da_est": js_round(mw, 2),
        "net_charge_ph7_est": js_round(charge, 3),
        "absolute_charge_density": js_round(charge_density, 3),
        "isoelectric_point_est": js_round(pi, 2),
        "gravy_kd": js_round(gravy, 3),
        "polar_fraction": js_round(polar, 3),
        "hydrophobic_fraction": js_round(hydrophobic, 3),
        "aromatic_fraction": js_round(aromatic, 3),
        "max_hydrophobic_run": best,
        "solubility_tendency_score_0_100": js_round(solubility, 1),
        "solubility_class": classify(solubility),
        "aggregation_risk_score_0_100": js_round(aggregation, 1),
        "aggregation_risk_class": "High" if aggregation >= 65 else "Moderate" if aggregation >= 35 else "Low",
        "passive_permeability_tendency_0_100": js_round(permeability, 1),
        "sequence_liability_count": liabilities,
        "sequence_stability_score_0_100": js_round(stability, 1),
        "peptide_drug_likeness_score_0_100": js_round(drug_likeness, 1),
        "developability_class": classify(drug_likeness, 70, 50),
        "developability_notes": "; ".join(issues) if issues else "No major sequence-level flag",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--sequence-column", default="sequence")
    parser.add_argument("--name-column", default="name")
    args = parser.parse_args()
    table = pd.read_csv(args.input, encoding="utf-8-sig")
    records = []
    for _, row in table.iterrows():
        sequence, status, note = derive_sequence(row.get(args.sequence_column), row.get(args.name_column))
        record: dict[str, object] = {"scoring_sequence": sequence, "scoring_status": status}
        if sequence:
            record.update(score(sequence, note))
        else:
            record.update({key: np.nan for key in score("A", "")})
            record["developability_notes"] = note
        records.append(record)
    scored = pd.DataFrame(records)
    table = table.drop(columns=[column for column in scored.columns if column in table.columns])
    output = pd.concat([table.reset_index(drop=True), scored], axis=1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Rows: {len(output)}")
    print(f"Status: {output['scoring_status'].value_counts(dropna=False).to_dict()}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
