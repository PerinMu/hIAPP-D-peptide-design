# Data dictionary

## Core identity and provenance

| Column | Meaning |
|---|---|
| `name` | Original design identifier. |
| `sequence` | Original L-amino-acid sequence used during generation. |
| `seq_rev` | Reverse-order, lower-case all-D sequence convention used for synthesis/prediction. |
| `source` | `design`, `IF_02`, or `database`; source is not a score. |
| `smiles` | Linear, free-terminus peptide SMILES with explicit stereochemistry. |

## Boltz-2 fields

| Column | Direction in this workflow | Meaning |
|---|---:|---|
| `confidence_score` | higher | Overall model confidence. |
| `ptm` | higher | Predicted TM-like complex confidence. |
| `iptm` | higher | Predicted interface confidence. |
| `complex_pde` | lower | Predicted complex distance/error feature. |
| `complex_ipde` | lower | Interface counterpart retained for inspection. |
| `affinity_pred_value[1,2]` | lower | Continuous output from affinity head 0, 1 or 2. |
| `affinity_probability_binary[1,2]` | higher | Binary binding probability output from the corresponding head. |

The affinity fields are combined through within-pool percentiles. No raw
affinity field is interpreted as a measured dissociation constant.

## Sequence-level descriptors

| Column | Direction | Interpretation |
|---|---:|---|
| `scoring_sequence` | descriptive | Canonical residue string used for sequence-only calculations. |
| `scoring_status` | descriptive | `OK`, reconstructed, approximated, missing, or unsupported input status. |
| `sequence_length_aa` | descriptive | Number of canonical residues. |
| `molecular_weight_da_est` | descriptive | Sum of average residue masses plus one terminal water molecule. |
| `solubility_tendency_score_0_100` | higher | Sequence-composition heuristic; not measured solubility. |
| `aggregation_risk_score_0_100` | lower | Sequence aggregation-risk heuristic. |
| `passive_permeability_tendency_0_100` | descriptive | Sequence-only passive-permeability tendency; not measured permeability. |
| `sequence_stability_score_0_100` | higher | Penalty-based chemical-liability heuristic. |
| `peptide_drug_likeness_score_0_100` | higher | Composite prioritization heuristic. |
| `sequence_liability_count` | lower | Count of defined sequence liability motifs. |
| `aromatic_fraction` | descriptive | Fraction of F/W/Y residues. |
| `net_charge_ph7_est` | descriptive | Henderson-Hasselbalch charge estimate at pH 7. |
| `isoelectric_point_est` | descriptive | Estimated pI under the same simplified charge model. |
| `gravy_kd` | descriptive | Kyte-Doolittle mean hydropathy. |
| `max_hydrophobic_run` | descriptive | Longest consecutive run among the project-defined hydrophobic residue set. |

Exact formulas, pKa values, residue sets, references, and limitations are in
[`PHYSICOCHEMICAL.md`](PHYSICOCHEMICAL.md). The literature supports the selected
descriptor concepts; it does not validate the repository's custom 0-100
composite weights or cutoffs.

## Derived notebook fields

| Column | Definition |
|---|---|
| `structure_bottleneck` | `min(ptm, iptm)`. |
| `affinity_head_0_score` etc. | Mean favorable percentile of a head's value and probability. |
| `affinity_consensus` | Median of three head scores. |
| `affinity_head_spread` | Maximum minus minimum head score. |
| `structure_quality` | 60/20/20 weighted percentile score. |
| `developability_score` | Mean of five favorable sequence-property percentiles. |
| `overall_score` | 55/30/15 affinity/structure/developability score. |
| `reference_distance` | Median robust distance from database medians in four descriptor dimensions. |
| `p4_score` | 50/35/15 structure-emphasis/affinity/developability score. |
