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
| BoltzGen 1 | Target-conditioned all-atom sequence–structure generation | `peptide-anything`, design step, 2,000 requested designs, diffusion batch size 10, `boltzgen1_diverse.ckpt` | [Official repository](https://github.com/HannesStark/boltzgen), MIT License |
| BoltzIF | Backbone-conditioned sequence redesign | Four sequences per backbone, temperature 0.2, cysteine excluded, `boltzgen1_ifold.ckpt` | Distributed through the BoltzGen project, MIT License |
| Boltz-2 | Complex prediction and relative ranking signals | Explicit D-peptide SMILES, three diffusion samples, MSA server, potentials, model-0 structures retained | [Official repository](https://github.com/jwohlwend/boltz), MIT License |
| Automatic MSA generation | Target-sequence alignment input requested with `--use_msa_server` | Used during Boltz-2 jobs from 2026-08-04 to 2026-08-08; upstream Boltz documentation cites ColabFold | [ColabFold paper](https://doi.org/10.1038/s41592-022-01488-1) |
| Project scoring code | Physicochemical descriptors and P1–P4 prioritization | Deterministic percentile scores and documented heuristic weights | This repository, MIT License |

Model weights are not redistributed. The full notebook follows the official
installation/download routes and records the required invocation parameters.

## Production-version record

The August 2026 campaign preserved model names, checkpoint filenames, YAML
inputs, command-line parameters, CUDA container/module choices, score tables,
and predicted structures. It did **not** preserve the exact BoltzGen/Boltz
package versions, Git revisions, checkpoint SHA256 values, NVIDIA driver, or GPU
model reported by `nvidia-smi`. The specific MSA-server endpoint/version,
request log, and returned alignment archives were also not retained.

Recorded environment evidence is:

- BoltzGen: Ubuntu 22.04 CUDA 12.4.1 cuDNN development container;
- Boltz-2: CUDA 12.8 module and the Slurm partition named `gpu_4090`;
- generation: four GPUs requested for BoltzGen and BoltzIF;
- prediction: one GPU per Boltz-2 job, with up to eight concurrent jobs;
- recorded prediction throughput: approximately 128 candidates/hour at the
  campaign level, excluding queueing, interruptions, and retries.

Because the exact package revisions are not recoverable from the deposited
records, the standardized result file labels this field explicitly rather than
inventing a version. Future campaigns should capture the following before
inference:

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
- Automatic MSA generation depended on an external server, but its endpoint
  version and returned alignment archive were not deposited.
- Physicochemical composite scores are transparent project heuristics, not
  experimentally calibrated predictors.
- Manual structure review introduces expert judgment; review-stage provenance is
  retained, but a new stochastic generation run requires a new review.
- No measured hIAPP aggregation-inhibition value is included in the current
  public release. Model scores must not be presented as wet-lab activity.

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
