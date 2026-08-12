# AI-assisted D-peptide design against hIAPP

This repository documents a reproducible computational workflow for designing
D-peptide candidates against human islet amyloid polypeptide (hIAPP). It is
prepared as a competition submission and deliberately separates model-derived
prioritization from experimental evidence. Every public-facing document,
notebook, data annotation, and command-line interface is written in English.

![Computational design and screening workflow](docs/assets/workflow.png)

## Project question

hIAPP aggregation is associated with islet amyloid in type 2 diabetes. The
computational objective was to generate D-peptides predicted to bind the
amyloidogenic C-terminal region of hIAPP and to prioritize a small, diverse,
experimentally tractable set for synthesis. PDB 9ULZ was used as the structural
template; chain D residues 19-37 were retained and residues 21-37 defined the
intended binding region.

The design problem is difficult because peptide binding, structural confidence,
aggregation propensity, solubility, and chemical tractability must be balanced.
Model scores are therefore treated as relative prioritization evidence, not as
measured inhibition, affinity, selectivity or mechanism.

## Reproducibility at a glance

| Stage | Recorded result | Reproducible artifact |
|---|---:|---|
| Completed BoltzGen designs | 1,990 | `notebooks/00_full_generation_to_selection.ipynb` |
| Unique BoltzGen sequences | 1,956 | `data/designs/batch1_design.csv` |
| BoltzIF sequences / unique | 7,960 / 7,854 | `data/designs/batch1_IF_02.csv` |
| Unique merged designs | 9,808 | `data/designs/merged_designs.csv` |
| Rows used for design ranking | 9,806 | `data/scored/merged_all_2_scored.csv` |
| Hard-gated candidates | 904 | `results/screening/hard_gate_904.csv` |
| P1 / P2 / P3 review candidates | 12 / 12 / 8 | `results/screening/p1_p2_p3_top32.csv` |
| P4 eligible / review candidates | 30 / 10 | `results/screening/p4_top10.csv` |
| Final synthesis candidates | 12 | `results/final_candidates/final_12.csv` |

## What was done

1. **Candidate generation.** BoltzGen generated 2,000 designs. Sequence
   deduplication yielded 1,956 candidates.
2. **Backbone-conditioned redesign.** BoltzIF sampled four sequences per
   backbone at temperature 0.2 while excluding cysteine. The raw output
   contained 7,960 sequences and 7,854 unique sequences.
3. **D-peptide encoding.** The 9,808 unique L-peptide designs were converted to
   reverse-sequence D-peptide encodings (`seq_rev`, lower case) and to
   stereochemistry-aware linear-peptide SMILES.
4. **Structure and affinity prediction.** Boltz-2 was used to predict hIAPP-
   peptide complexes and three affinity heads. The recorded analysis used 9,806
   exact-source (`design` or `IF_02`) rows; two shared-source rows labeled
   `design; IF_02` were retained in the data but not ranked.
5. **Four-layer prioritization.** Hard filters, percentile-based multi-metric
   ranking, P1-P4 priority tiers, sequence de-redundancy and manual structural
   review reduced the pool to 12 D-peptides for synthesis.

The final computational shortlist contains P1 × 8, P2 × 1, P3 × 1, and P4 × 2.
The selected structures and a machine-readable table are included in
`results/final_candidates/`.

## Run the complete GPU workflow

The step-by-step server notebook starts from the 9ULZ input, installs BoltzGen
and Boltz using their official GitHub instructions, submits the 2,000-design
BoltzGen stage, runs the study-specific inverse-folding configuration, generates
all Boltz-2 YAMLs, dispatches prediction/retry batches, collects model outputs
and finishes with screening plus an auditable manual structure-review sheet:

```bash
jupyter lab notebooks/00_full_generation_to_selection.ipynb
```

Edit only the server paths in the first parameter cell. `RUN_CPU_STEPS` and
`SUBMIT_GPU_STEPS` default to `False`, so the notebook first prints every command
without modifying the server or submitting GPU work. It does not deploy or run
the models on the local Mac.

The Boltz affinity module is officially scoped to small-molecule ligands and
discourages inputs above 56 atoms (128-atom hard limit). Encoding a D-peptide as
a stereochemical ligand SMILES is therefore an extension used here for relative
prioritization, not a claim of calibrated peptide affinity. See the
[official Boltz prediction guide](https://github.com/jwohlwend/boltz/blob/main/docs/prediction.md)
before preparing new inputs.

## Run only the reproducible screening analysis

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab notebooks/01_reproduce_screening.ipynb
```

Run the cells from top to bottom. The notebook uses the committed scored CSV,
recomputes all percentile-derived scores, verifies the 904-candidate hard-filter
pool, reconstructs the P1-P3 and P4 candidate sets, and checks the final 12-row
manifest. It does not require a GPU.

For users starting from model outputs rather than the committed score table:

```bash
python scripts/collect_boltz_scores.py \
  --outputs-dir /path/to/boltz_outputs \
  --output results/boltz_scores.csv
```

Then merge those scores with the design table and compute the documented
sequence-level physicochemical descriptors before running the screening
notebook. The full generation/prediction stages require separate BoltzGen and
Boltz installations plus suitable GPU resources; the templates in `hpc/` show
the Slurm workflow without site-specific credentials.

## Physicochemical calculations

The sequence-property layer calculates transparent descriptors and composite
heuristics rather than invoking a hidden trained model. Direct descriptors
include estimated molecular mass, idealized charge and pI, Kyte-Doolittle mean
hydropathy, residue fractions, and the longest hydrophobic run. The solubility,
aggregation-risk, permeability, stability, and peptide drug-likeness scales are
project-specific combinations used only for relative ranking.

The exact equations, assumptions, and descriptor-level literature are in
[docs/PHYSICOCHEMICAL.md](docs/PHYSICOCHEMICAL.md). The implementation is in
[`scripts/score_sequence_properties.py`](scripts/score_sequence_properties.py).
No score should be reported as measured solubility, aggregation, stability,
permeability, or bioavailability.

## Screening logic

All percentile scores are calculated over the mixed design/IF pool; there are
no source quotas.

- Hard gate: complete affinity heads, `min(pTM, ipTM) >= 0.65`, solubility
  tendency >= 40 and aggregation risk <= 65. This retained 904 of 9,806 scored
  designs.
- Affinity consensus: each head combines the favorable percentile of its
  continuous prediction (lower is better) and binding probability (higher is
  better); the median of three heads is used.
- Structure quality: 60% `min(pTM, ipTM)`, 20% confidence and 20% inverse
  complex PDE percentiles.
- Developability: mean favorable percentile across solubility, aggregation
  risk, stability, peptide drug-likeness and liability count.
- Main score: 55% affinity consensus, 30% structure quality and 15%
  developability.
- P1: `min(pTM, ipTM) >= 0.70` and affinity-head spread <= 0.35, ranked by the
  main score. P2 continues down the main ranking. P3 retains affinity-head
  disagreement or physicochemical novelty. Normalized Levenshtein similarity
  (< 0.85 preferred) reduces redundancy.
- P4: previously unselected 11-12 aa peptides satisfying
  `min(pTM, ipTM) >= 0.75`, solubility >= 40 and aggregation risk <= 65. Its
  score is 50% structure-emphasis, 35% affinity consensus and 15%
  developability. Ten candidates entered structural review.

See [docs/METHODS.md](docs/METHODS.md) for the exact screening equations,
[docs/PHYSICOCHEMICAL.md](docs/PHYSICOCHEMICAL.md) for sequence-property
calculations, and [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) for field
definitions.

## Repository map

```text
configs/                 BoltzGen and Boltz-2 example inputs
data/designs/            candidate sequences and stereochemical SMILES
data/scored/             committed score table used by the notebook
docs/                    methods, equations, bibliography and provenance notes
hpc/                     portable Slurm and bounded-concurrency templates
notebooks/               full GPU workflow and CPU screening reproduction
results/final_candidates final 12 table and predicted complexes
scripts/                 reusable command-line workflow utilities
wetlab/                  blank raw-data template and planned analysis README
```

## Experimental status and planned validation

The 12 peptides were selected for synthesis. No wet-lab measurements are
claimed in this repository yet. The planned validation includes ThT aggregation
kinetics across peptide concentrations, hIAPP-only and vehicle controls,
positive controls (L-TQNWVP and D-nfgail), independent repeats, endpoint/kinetic
summary statistics, and orthogonal structure or morphology measurements where
available. Raw measurements should be added without modification under
`wetlab/raw/`, with analysis outputs generated separately.

## Reproducibility limits

- BoltzGen/Boltz checkpoints and external model caches are not redistributed.
- The complete backbone, NPZ and raw Boltz prediction trees are too large for a
  normal Git repository. Their provenance and expected locations are documented
  in `docs/REPRODUCIBILITY.md`; archive them in a release or data repository if
  required by the competition.
- Sequence-level developability values are heuristics for within-pool ranking;
  they are not measured solubility, permeability or stability.
- The D-peptide reverse-sequence representation is explicit. Lower-case letters
  are a data convention; synthesis orders must separately specify all-D residue
  stereochemistry and terminal modifications.
- The historical HPC scripts were recovered. Public path-neutral counterparts
  and original SHA256 provenance are included; raw scripts containing private
  cluster paths and a proxy endpoint are intentionally excluded.

## Documentation and references

- [Computational methods and exact screening equations](docs/METHODS.md)
- [Physicochemical descriptor equations and limitations](docs/PHYSICOCHEMICAL.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [End-to-end reproducibility and provenance](docs/REPRODUCIBILITY.md)
- [Scientific bibliography](docs/REFERENCES.md)
- [Reference-inhibitor source index](data/designs/reference_inhibitor_sources.csv)
- [Competition submission checklist](docs/COMPETITION_CHECKLIST.md)

The main external resources are the [official BoltzGen repository](https://github.com/HannesStark/boltzgen),
the [official Boltz repository](https://github.com/jwohlwend/boltz), and
[PDB 9ULZ](https://www.rcsb.org/structure/9ULZ). Cite their corresponding
publications and the PDB entry in any scientific use. Code in this repository is
released under the MIT License; third-party model weights and structural data
remain subject to their own terms.

## Citation

Repository citation metadata are provided in [`CITATION.cff`](CITATION.cff).
The competition team should replace the collective author entry with final team
member names and add a release DOI if the repository is archived in Zenodo.
