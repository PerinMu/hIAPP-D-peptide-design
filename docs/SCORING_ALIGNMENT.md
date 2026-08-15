# Competition scoring alignment

This page directs evaluators from each Track 1 scoring category to the strongest
repository evidence. It does not convert computational evidence into wet-lab
claims or predict a competition score.

## 1. Topic value and target understanding — 15 points

- [`BACKGROUND.md`](BACKGROUND.md) explains hIAPP biology, amyloid aggregation,
  D-peptide rationale, prior discovery routes, and the intended contribution of
  the generative framework.
- PDB 9ULZ chain D residues 19–37 and the intended residues 21–37 are defined in
  committed [BoltzGen](../configs/boltzgen/9ULZ.yaml) and
  [Boltz-2](../configs/boltz2/hIAPP_template.yaml) inputs.
- The [Model Card](../MODEL_CARD.md) separates model scope, peptide-specific
  limitations, and appropriate interpretation.

## 2. AI design and computational optimization — 25 points

- The [full GPU notebook](../notebooks/00_full_generation_to_selection.ipynb)
  covers target preparation, BoltzGen design, BoltzIF diversification,
  reverse-D stereochemical encoding, Boltz-2 prediction, retry recovery,
  scoring, and selection.
- [`METHODS.md`](METHODS.md) records exact filters, equations, ranking weights,
  priority tiers, sequence de-redundancy, and manual structure-review criteria.
- [`PHYSICOCHEMICAL.md`](PHYSICOCHEMICAL.md) documents every sequence descriptor,
  project heuristic, assumption, limitation, and supporting reference.
- The [production environment record](PRODUCTION_ENVIRONMENT.md) provides
  recovered versions, checkpoint/container hashes, GPU/CUDA evidence, timing,
  retries, and scheduler accounting.
- [`run.sh`](../run.sh) and the [CPU notebook](../notebooks/01_reproduce_screening.ipynb)
  independently reproduce the deposited 9,806 → 904 → 42 → 12 funnel.

## 3. Wet-lab validation quality — 25 points

- Wet-lab validation is in progress; no unverified measurement is included in
  this release.
- [`wetlab/`](../wetlab/) defines a traceable data layout and assay plan covering
  hIAPP-only/vehicle controls, positive controls L-TQNWVP and D-nfgail,
  concentration response, independent and technical replicates, raw ThT
  kinetics, prespecified exclusions, and an orthogonal endpoint where available.
- Model scores are explicitly labeled `not_measured` in the standardized result
  files and are not presented as activity.

## 4. Activity and mechanism analysis — 20 points

- The final manifest and 12 deposited [predicted complexes](../results/final_candidates/structures/)
  support candidate-specific interface review and testable binding hypotheses.
- The 76-entry reference-inhibitor set is used only for descriptor-space context;
  its sources and leakage boundary are documented in
  [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md).
- Comparative activity, stability, selectivity, and mechanism conclusions remain
  pending controlled experiments. Computational predictions are framed as
  prioritization evidence, not mechanistic proof.

## 5. Materials submission and presentation — 15 points

- [`README.md`](../README.md) provides installation, downloads, commands,
  expected outputs, runtime/resources, and a judge-first navigation path.
- [`COMPETITION_COMPLIANCE.md`](COMPETITION_COMPLIANCE.md) maps Attachment 5 to
  specific repository artifacts.
- [`results.csv`](../results/submission/results.csv), the formatted
  [`results.xlsx`](../results/submission/results.xlsx), and all referenced mmCIF
  structures are committed and cross-validated.
- The [Model Card](../MODEL_CARD.md), [data provenance](DATA_PROVENANCE.md),
  [reproducibility record](REPRODUCIBILITY.md), environment snapshots, and
  GitHub Actions checks make data, code, models, and outputs traceable.

Presentation slides and narration are submitted through the competition's
designated presentation channel rather than this code repository.
