# Computational methods

## Overview

The hIAPP workflow combines target preparation, peptide generation, sequence
redesign, reverse-D encoding, complex prediction, sequence-property calculation,
ranking, and manual structure review.

BoltzGen generates the initial sequence–structure hypotheses in an L-amino-acid
representation. The sequences are subsequently reversed and converted to
explicit D-stereochemical SMILES. This retro-inverso step is a design hypothesis,
not a proof that the generated L-backbone geometry is exactly retained. Complex
prediction and structure review test computational consistency; binding and
functional activity require experiment.

## Template preparation and candidate generation

PDB 9ULZ was used as the starting hIAPP fibril template. Chain D residues
19-37 were retained, and residues 21-37 were assigned as the binding region in
the BoltzGen input. BoltzGen was run with the `peptide-anything` protocol,
`design` step, 2,000 requested designs and a diffusion batch size of 10. The
design sequence table contained 1,956 unique sequences after deduplication.

BoltzIF was then used for backbone-conditioned sequence redesign. Four
sequences were sampled per backbone at sampling temperature 0.2, with cysteine
excluded. This produced 7,960 raw sequences and 7,854 unique sequences. Merging
the two sources produced 9,810 rows and 9,808 unique sequences.

For the retro-inverso representation used in this project, the L-sequence was
reversed and written in lower case to denote all-D residues. The convention is
recorded in both `sequence` (original L order) and `seq_rev` (D-peptide order).
Stereochemistry-aware, linear free-terminus SMILES were generated from
`seq_rev`. Ile and Thr side-chain stereocentres were handled explicitly.

## Sequence-level physicochemical descriptors

Each sequence was assigned deterministic composition-derived descriptors before
screening: average-residue molecular mass with terminal water, idealized net
charge at pH 7, estimated pI, Kyte-Doolittle mean hydropathy, polar,
hydrophobic, and aromatic residue fractions, and the longest hydrophobic run.
These inputs were combined into transparent 0-100 heuristics for solubility
tendency, aggregation risk, passive-permeability tendency, chemical stability,
and peptide drug-likeness.

The feature choices are grounded in established peptide hydropathy,
aggregation, permeability, and developability literature, but every composite
weight, class boundary, and screening cutoff is specific to this study. The
calculations are not experimentally calibrated property predictors. Exact
equations, pKa and residue tables, assumptions about modifications, and the
descriptor bibliography are provided in
[`docs/PHYSICOCHEMICAL.md`](PHYSICOCHEMICAL.md).

## Boltz-2 prediction

Each D-peptide SMILES was paired with the hIAPP sequence
`HSSNNFGAILSSTNVGSNTY` and the 9ULZ template. Boltz-2 returned complex
confidence metrics and three affinity prediction heads. Repeated/interrupted
cluster jobs were resumed by detecting missing `*_model_0.cif` files and
resubmitting their original YAML inputs. Batch outputs were merged by
`sample_id`; 9,806 design/IF rows entered the analysis table.

Boltz officially documents its affinity module for protein-small-molecule
complexes and advises against ligands larger than 56 atoms, with 128 atoms as a
hard limit. The reverse-D peptides in this study were supplied as explicit
ligand SMILES, so the affinity heads are treated only as a within-study ranking
signal. They are not interpreted as calibrated binding affinities and require
wet-lab confirmation.

## Direction-aware percentile scores

Let `R+(x)` be the fractional rank of a metric for which higher is better and
`R-(x)` the fractional rank for which lower is better. Ties use their average
rank. All ranks are calculated in the full 9,806-row mixed design/IF pool.

For affinity head `h`:

```text
H_h = [R-(pred_value_h) + R+(probability_h)] / 2
```

The affinity consensus and head spread are:

```text
A = median(H_0, H_1, H_2)
Delta_H = max(H_0, H_1, H_2) - min(H_0, H_1, H_2)
```

The structure bottleneck, structure score and developability score are:

```text
B = min(pTM, ipTM)
S = 0.60 R+(B) + 0.20 R+(confidence) + 0.20 R-(complex_PDE)
D = mean[R+(solubility), R-(aggregation), R+(stability),
         R+(drug_likeness), R-(liability_count)]
```

The main priority score is:

```text
O = 0.55 A + 0.30 S + 0.15 D
```

These scores are relative ranks, not probabilities or predicted experimental
effect sizes.

## Hard gate and P1-P3 tiers

The hard gate required all six affinity values to be present, `B >= 0.65`, a
solubility-tendency score of at least 40 and an aggregation-risk score of at
most 65. This retained 904 of the 9,806 candidates (9.22%).

P1 additionally required `B >= 0.70` and `Delta_H <= 0.35`. Candidates were
sorted by `O` and selected greedily while preferring normalized Levenshtein
similarity below 0.85 to previously selected sequences. Twelve P1 candidates
were retained. Twelve P2 candidates were then selected from the remainder by
the same overall score and de-redundancy procedure.

P3 was used to preserve model disagreement or physicochemical novelty. Novelty
was the median absolute, IQR-scaled distance from the reference-inhibitor
dataset median for aromatic fraction, estimated net charge at pH 7, estimated
pI and GRAVY. Candidates entered the P3 pool if `Delta_H > 0.35` or novelty was
at least the 75th percentile of the hard-gated pool. The exploration score was:

```text
E = 0.75 O + 0.25 R+(novelty)
```

Eight P3 candidates were selected after de-redundancy. The database set was
used only for this descriptive novelty distance, not as experimental negatives
and not as a source quota.

## P4 long-peptide branch

P4 excluded all P1-P3 sequences and required length 11 or 12 aa, `B >= 0.75`,
solubility >= 40, aggregation risk <= 65 and complete rank inputs. The
structure-emphasis and P4 scores were:

```text
S_P4 = 0.70 R+(B) + 0.20 R+[mean(pTM, ipTM)] + 0.10 R+(confidence)
O_P4 = 0.50 S_P4 + 0.35 A + 0.15 D
```

Thirty candidates passed and the top ten entered structural review. A prior
exploratory analysis used `B >= 0.72`; the finalized workflow and this
repository use `B >= 0.75` consistently.

## Structural review and final selection

The 32 P1-P3 candidates and 10 P4 candidates were reviewed for occupancy of the
intended hIAPP region, interface extent, steric clashes, chain continuity,
plausible polar/hydrophobic contacts and diversity. The final synthesis set was
P1 × 8, P2 × 1, P3 × 1, and P4 × 2, for 12 D-peptides total.

Selection is a hypothesis-generation step. Binding, aggregation inhibition,
selectivity and mechanism require experimental testing.

For a new stochastic generation run, the automated review pool may differ from
the historical pool. The final 12 must therefore be selected again with the
blank review sheet produced by `scripts/prepare_structure_review.py`; the
historical `final_12.csv` is an audit reference, not an automatic label file.

## Method references

Target biology, PDB 9ULZ, BoltzGen, Boltz-1/Boltz-2, physicochemical descriptor
foundations, and representative inhibitor literature are indexed in
[`docs/REFERENCES.md`](REFERENCES.md). The reference-inhibitor table has a
separate row-group provenance index at
[`data/designs/reference_inhibitor_sources.csv`](../data/designs/reference_inhibitor_sources.csv).
