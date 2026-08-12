#!/usr/bin/env python3
"""Recompute hIAPP multi-metric screening and export auditable candidate tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PRED_COLS = ["affinity_pred_value", "affinity_pred_value1", "affinity_pred_value2"]
PROB_COLS = ["affinity_probability_binary", "affinity_probability_binary1", "affinity_probability_binary2"]


def favorable_percentile(series: pd.Series, higher_is_better: bool) -> pd.Series:
    return series.rank(pct=True, method="average", ascending=higher_is_better)


def edit_similarity(a: str, b: str) -> float:
    if not a or not b:
        return float(a == b)
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (char_a != char_b)))
        previous = current
    return 1 - previous[-1] / max(len(a), len(b))


def greedy_pick(pool: pd.DataFrame, count: int, already: list[dict], limit: float = 0.85) -> list[dict]:
    picked, deferred = [], []
    for idx, row in pool.iterrows():
        refs = already + picked
        similarity = max((edit_similarity(row["d_sequence"], x["sequence"]) for x in refs), default=0.0)
        item = {"index": idx, "sequence": row["d_sequence"], "max_similarity": similarity}
        (picked if similarity < limit and len(picked) < count else deferred).append(item)
        if len(picked) == count:
            break
    for item in deferred:
        if len(picked) == count:
            break
        if item["index"] not in {x["index"] for x in picked}:
            picked.append(item)
    if len(picked) != count:
        raise RuntimeError(f"Could only select {len(picked)} of {count} candidates")
    return picked


def compute_scores(table: pd.DataFrame) -> pd.DataFrame:
    candidate = table[table["source"].isin(["design", "IF_02"])].copy()
    candidate["l_sequence"] = candidate["sequence"].astype(str).str.upper()
    candidate["d_sequence"] = candidate["seq_rev"].fillna(
        candidate["l_sequence"].str[::-1].str.lower()
    ).astype(str).str.lower()

    heads = []
    for index, (pred, prob) in enumerate(zip(PRED_COLS, PROB_COLS)):
        candidate[f"{pred}_pct"] = favorable_percentile(candidate[pred], False)
        candidate[f"{prob}_pct"] = favorable_percentile(candidate[prob], True)
        head = f"affinity_head_{index}_score"
        candidate[head] = candidate[[f"{pred}_pct", f"{prob}_pct"]].mean(axis=1)
        heads.append(head)
    candidate["affinity_consensus"] = candidate[heads].median(axis=1)
    candidate["affinity_head_spread"] = candidate[heads].max(axis=1) - candidate[heads].min(axis=1)
    candidate["structure_bottleneck"] = candidate[["ptm", "iptm"]].min(axis=1)
    candidate["structure_mean"] = candidate[["ptm", "iptm"]].mean(axis=1)
    candidate["structure_quality"] = (
        0.60 * favorable_percentile(candidate["structure_bottleneck"], True)
        + 0.20 * favorable_percentile(candidate["confidence_score"], True)
        + 0.20 * favorable_percentile(candidate["complex_pde"], False)
    )
    dev = pd.DataFrame({
        "solubility": favorable_percentile(candidate["solubility_tendency_score_0_100"], True),
        "aggregation": favorable_percentile(candidate["aggregation_risk_score_0_100"], False),
        "stability": favorable_percentile(candidate["sequence_stability_score_0_100"], True),
        "drug_likeness": favorable_percentile(candidate["peptide_drug_likeness_score_0_100"], True),
        "liability": favorable_percentile(candidate["sequence_liability_count"], False),
    }, index=candidate.index)
    candidate["developability_score"] = dev.mean(axis=1)
    candidate["overall_score"] = (
        0.55 * candidate["affinity_consensus"]
        + 0.30 * candidate["structure_quality"]
        + 0.15 * candidate["developability_score"]
    )

    database = table[table["source"].eq("database")]
    distances = []
    for column in ["aromatic_fraction", "net_charge_ph7_est", "isoelectric_point_est", "gravy_kd"]:
        median = database[column].median()
        scale = database[column].quantile(0.75) - database[column].quantile(0.25)
        if not np.isfinite(scale) or scale <= 1e-9:
            scale = database[column].std()
        if not np.isfinite(scale) or scale <= 1e-9:
            scale = 1.0
        distance = f"{column}_distance"
        candidate[distance] = (candidate[column] - median).abs() / scale
        distances.append(distance)
    candidate["reference_distance"] = candidate[distances].median(axis=1)
    candidate["reference_distance_pct"] = favorable_percentile(candidate["reference_distance"], True)
    return candidate


def select(candidate: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    complete = candidate[PRED_COLS + PROB_COLS].notna().all(axis=1)
    gate = complete & candidate["structure_bottleneck"].ge(0.65) \
        & candidate["solubility_tendency_score_0_100"].ge(40) \
        & candidate["aggregation_risk_score_0_100"].le(65)
    hard_pool = candidate[gate].sort_values("overall_score", ascending=False) \
        .drop_duplicates("d_sequence", keep="first")

    selected, labels = [], {}
    p1_pool = hard_pool[hard_pool["structure_bottleneck"].ge(0.70)
                        & hard_pool["affinity_head_spread"].le(0.35)]
    for item in greedy_pick(p1_pool, 12, selected):
        selected.append(item); labels[item["index"]] = "P1"
    remaining = hard_pool[~hard_pool.index.isin(labels)].sort_values("overall_score", ascending=False)
    for item in greedy_pick(remaining, 12, selected):
        selected.append(item); labels[item["index"]] = "P2"
    novelty_cutoff = hard_pool["reference_distance"].quantile(0.75)
    remaining = hard_pool[~hard_pool.index.isin(labels)].copy()
    remaining = remaining[remaining["affinity_head_spread"].gt(0.35)
                          | remaining["reference_distance"].ge(novelty_cutoff)]
    remaining["exploration_score"] = 0.75 * remaining["overall_score"] \
        + 0.25 * remaining["reference_distance_pct"]
    remaining = remaining.sort_values("exploration_score", ascending=False)
    for item in greedy_pick(remaining, 8, selected):
        selected.append(item); labels[item["index"]] = "P3"
    top32 = hard_pool.loc[list(labels)].copy()
    top32["priority"] = pd.Series(labels)
    top32["priority_order"] = top32["priority"].map({"P1": 1, "P2": 2, "P3": 3})
    top32 = top32.sort_values(["priority_order", "overall_score"], ascending=[True, False])

    candidate = candidate.copy()
    candidate["length_aa"] = candidate["d_sequence"].str.len()
    candidate["structure_emphasis"] = (
        0.70 * favorable_percentile(candidate["structure_bottleneck"], True)
        + 0.20 * favorable_percentile(candidate["structure_mean"], True)
        + 0.10 * favorable_percentile(candidate["confidence_score"], True)
    )
    candidate["p4_score"] = 0.50 * candidate["structure_emphasis"] \
        + 0.35 * candidate["affinity_consensus"] + 0.15 * candidate["developability_score"]
    p4_pool = candidate[~candidate["d_sequence"].isin(top32["d_sequence"])].copy()
    p4_pool = p4_pool[p4_pool["length_aa"].isin([11, 12])
                      & p4_pool["structure_bottleneck"].ge(0.75)
                      & p4_pool["solubility_tendency_score_0_100"].ge(40)
                      & p4_pool["aggregation_risk_score_0_100"].le(65)]
    p4_pool = p4_pool.sort_values(["p4_score", "structure_bottleneck", "affinity_consensus"],
                                  ascending=False).drop_duplicates("d_sequence", keep="first")
    return hard_pool, top32, p4_pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    table = pd.read_csv(args.input)
    scored = compute_scores(table)
    hard_pool, top32, p4_pool = select(scored)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    hard_pool.to_csv(args.output_dir / "hard_gate_904.csv", index=False)
    top32.to_csv(args.output_dir / "p1_p2_p3_top32.csv", index=False)
    p4_pool.head(10).to_csv(args.output_dir / "p4_top10.csv", index=False)
    print(f"Analysis rows: {len(scored)}")
    print(f"Hard gate: {len(hard_pool)}")
    print(f"P1/P2/P3: {top32['priority'].value_counts().sort_index().to_dict()}")
    print(f"P4 hard pass: {len(p4_pool)}; exported top 10")


if __name__ == "__main__":
    main()

