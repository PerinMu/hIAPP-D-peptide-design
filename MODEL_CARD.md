# Model Card: generative reverse-D peptide design workflow

## Summary

This repository combines externally developed, open-source pretrained models
with project-specific stereochemical conversion, physicochemical descriptors,
multi-objective ranking, failure recovery, and structural review. The team did
**not** train or fine-tune BoltzGen, BoltzIF, or Boltz-2. No `train.py`, training
split, training log, or team-trained weight is therefore applicable.

The project contribution is an end-to-end reverse-D peptide design and
screening workflow, demonstrated against human islet amyloid polypeptide
(hIAPP). It turns model outputs into an auditable candidate funnel and a
standardized 12-candidate submission manifest.

## Components and provenance

| Component | Role | Production configuration | Source and license |
|---|---|---|---|
| BoltzGen 1 (`boltzgen` 0.2.0) | Target-conditioned all-atom sequence–structure generation | `peptide-anything`, design step, 2,000 requested designs, diffusion batch size 10, `boltzgen1_diverse.ckpt` | [Official repository](https://github.com/HannesStark/boltzgen), MIT License |
| BoltzIF (`boltzgen` 0.2.0) | Backbone-conditioned sequence redesign | Four sequences per backbone, temperature 0.2, cysteine excluded, `boltzgen1_ifold.ckpt` | Distributed through the BoltzGen project, MIT License |
| Boltz-2 (`boltz` 2.2.1, recovered environment) | Complex prediction and relative ranking signals | Explicit D-peptide SMILES, three diffusion samples, MSA server, potentials, model-0 structures retained | [Official repository](https://github.com/jwohlwend/boltz), MIT License |
| Automatic MSA generation | Target-sequence alignment input requested with `--use_msa_server` | The installed Boltz 2.2.1 default was `https://api.colabfold.com`; no URL override appears in the production command | [ColabFold paper](https://doi.org/10.1038/s41592-022-01488-1) |
| Project scoring code | Physicochemical descriptors and P1–P4 prioritization | Deterministic percentile scores and documented heuristic weights | This repository, MIT License |

Model weights are not redistributed. The full notebook follows the official
installation/download routes and records the required invocation parameters.

## Production-version record

On 2026-08-15, the still-present cloud environments, checkpoints, command
scripts, scheduler history, and selected historical logs were collected with
the read-only scripts in `hpc/`. Both provenance archives and all 75 internal
files passed SHA256 verification. Raw bundles remain private because they
contain account paths and compute-node names; the credential-free facts and
bundle checksums are recorded in
[`docs/PRODUCTION_ENVIRONMENT.md`](docs/PRODUCTION_ENVIRONMENT.md).

Recovered evidence is:

- the historical BoltzIF log explicitly reports `boltzgen 0.2.0`;
- the still-installed prediction environment reports `boltz 2.2.1`; prediction
  logs did not print the package version, so this is labeled as a recovered
  environment snapshot rather than an immutable per-job version record;
- `boltzgen1_diverse.ckpt` SHA256:
  `360af8bd6e59527ff6ec25dd81253967f3bd3567d200053b10680634751f8e3c`;
- `boltzgen1_ifold.ckpt` SHA256:
  `dd4cf108c94471bdc3a326b7b180fa3854dc019110fae780208c30b50bd56578`;
- `boltz2_conf.ckpt` SHA256:
  `090e82ac8c92f5e943fa1b39e7410a44027bea7243c0bbb3caa67a77fc1428e1`;
- `boltz2_aff.ckpt` SHA256:
  `dcc5cd3722b1c9eaa34267e4ae32f55cbbf1963f4c19319381ccfa30fdd2ca9e`;
- BoltzGen used a CUDA 12.4.1/cuDNN 9.1 Ubuntu 22.04 Singularity
  image; its SHA256 is
  `723659cab39561f553844c4074c8ec93e176908bc408b4e9d3b2dbe74c48124f`;
- Boltz-2 used CUDA 12.8, PyTorch 2.10.0+cu128, and RTX 4090 jobs;
- generation and inverse folding requested four GPUs; prediction used one RTX
  4090, six CPU cores, and 60 GB RAM per job, with up to eight concurrent jobs;
- scheduler history for the campaign window contains 10,322 `boltz_arr`
  allocations: 9,788 completed and 534 failed, totaling 459.26 allocated GPU
  hours before output-level recovery and deduplication;
- campaign-level observed throughput was approximately 128 candidates/hour,
  excluding queueing, interruptions, and retries.

The upstream source Git revisions and production stochastic seeds remain
unavailable: the models were installed as packages and the production commands
did not set or log a seed. The BoltzGen collection node exposed an RTX 3090 on
the same `gpu` partition, but the exact GPU model of the historical four-GPU
jobs was not printed and is not inferred. The MSA endpoint default is
recoverable; its service-side version, request log, and returned alignments are
not.

Future campaigns should capture the following before inference:

```bash
boltzgen --version
python -m pip show boltzgen boltz
python -m pip freeze > environment-models.txt
nvidia-smi > nvidia-smi.txt
git -C /path/to/boltzgen rev-parse HEAD
git -C /path/to/boltz rev-parse HEAD
sha256sum /path/to/boltzgen1_diverse.ckpt /path/to/boltzgen1_ifold.ckpt
```

For an MSA-server run, also preserve the exact target YAML, Boltz command,
endpoint configuration, submission timestamp, returned alignment files, and a
credential-free request log. Authentication tokens must never be committed.

## Intended use

- Generate and prioritize structure-guided reverse-D peptide hypotheses.
- Compare candidates within a fixed model/version/run context.
- Produce predicted complexes and an experimentally actionable shortlist.
- Adapt the same computational infrastructure to a new target after redefining
  its structure, binding site, campaign constraints, and assays.

## Inputs and outputs

Inputs include a target structure or sequence, intended binding region, peptide
design constraints, model checkpoints, and campaign parameters. The hIAPP case
uses PDB 9ULZ chain D residues 19–37 and specifies residues 21–37 as the binding
region.

Outputs include generated L-sequence/structure hypotheses, reverse-D sequences
and stereochemical SMILES, Boltz-2 complex predictions, relative affinity and
confidence signals, sequence-property descriptors, priority tiers, predicted
mmCIF complexes, and `results/submission/results.csv`.

## Performance and uncertainty

The reproducible deposited funnel is:

```text
9,806 ranked designs -> 904 hard-gated candidates
-> P1/P2/P3 = 12/12/8 and P4 = 30 eligible/10 reviewed
-> 12 final candidates
```

These counts measure pipeline execution and selection, not biological accuracy.
All affinity consensus, structure quality, developability, and overall priority
values are relative within-pool scores. They are not calibrated probabilities,
dissociation constants, or experimental effect sizes.

## Limitations

- BoltzGen generates an L-amino-acid sequence/structure hypothesis before the
  project applies reverse-D conversion. Retro-inverso conversion does not
  guarantee preservation of every backbone interaction.
- The Boltz-2 affinity module is documented primarily for protein–small-molecule
  complexes. Peptides were supplied as explicit ligands, so affinity heads are
  used only as relative ranking signals.
- External model training-data overlap with PDB 9ULZ or related amyloid
  structures cannot be independently audited by this project.
- Automatic MSA generation used the installed Boltz default
  `https://api.colabfold.com`; its service-side version and returned alignment
  archive were not deposited.
- Physicochemical composite scores are transparent project heuristics, not
  experimentally calibrated predictors.
- Manual structure review introduces expert judgment; review-stage provenance is
  retained, but a new stochastic generation run requires a new review.
- Wet-lab validation is in progress, but no measured hIAPP
  aggregation-inhibition value is included in the current public release.
  Model scores must not be presented as wet-lab activity.

## Data, leakage, and experimental boundary

No project model was trained, validated, or tuned on the 76-entry reference
inhibitor set. That set is used only for a descriptive novelty distance and is
not treated as an activity-labeled training or test dataset. No wet-lab outcome
was used to select the final 12. Data lineage and overlap controls are detailed
in [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md).

## Responsible interpretation

The workflow is for research hypothesis generation. Binding, aggregation
inhibition, selectivity, toxicity, stability, mechanism, and therapeutic value
require appropriately controlled experiments. Candidate structures and scores
should not be used for clinical decisions.
