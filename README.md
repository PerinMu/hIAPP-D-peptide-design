# AI-assisted D-peptide design against hIAPP

[![Reproducibility checks](https://github.com/PerinMu/hIAPP-D-peptide-design/actions/workflows/validate.yml/badge.svg)](https://github.com/PerinMu/hIAPP-D-peptide-design/actions/workflows/validate.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, auditable workflow for generating, predicting, ranking, and
selecting D-peptide candidates against human islet amyloid polypeptide (hIAPP).
The pipeline combines BoltzGen, BoltzIF, Boltz-2, transparent sequence-property
calculations, multi-objective screening, and structure review.

![Computational design and screening workflow](docs/assets/workflow.png)

## Highlights

- **Complete design funnel:** structural target preparation, 2,000-design
  generation, inverse folding, 9,806-candidate prediction/ranking, four-layer
  prioritization, and a 12-peptide synthesis set.
- **Two levels of reproducibility:** a full GPU/Slurm notebook for end-to-end
  regeneration and a fast CPU notebook that reproduces every reported count
  from committed data.
- **Interpretable multi-objective selection:** affinity-head consensus,
  structure confidence, solubility, aggregation risk, stability, diversity, and
  manual interface review are documented separately.
- **Traceable evidence:** each final peptide connects to source sequences,
  prediction scores, selection tier, review stage, and a model-0 complex CIF.
- **Automated quality control:** GitHub Actions executes the screening notebook
  and checks scripts, HPC templates, language consistency, reference coverage,
  and candidate-count invariants on every update.

## Start here

| Resource | What it provides |
|---|---|
| **[Full design-to-selection notebook](notebooks/00_full_generation_to_selection.ipynb)** | Step-by-step BoltzGen generation, BoltzIF redesign, Boltz-2 prediction, retry handling, score collection, screening, and structure review on a Slurm GPU server. |
| **[Screening reproduction notebook](notebooks/01_reproduce_screening.ipynb)** | CPU-only reconstruction of every reported screening count and the final candidate manifest from committed data. |
| **[Final 12 candidates](results/final_candidates/final_12.csv)** | Machine-readable synthesis shortlist with priority tier, design provenance, experimental status, and structure filenames. |
| **[Predicted complexes](results/final_candidates/structures/)** | Boltz-2 model-0 CIF structures used during manual review. |
| **[Methods](docs/METHODS.md)** | Exact ranking equations, thresholds, tier definitions, and selection logic. |
| **[Physicochemical calculations](docs/PHYSICOCHEMICAL.md)** | Descriptor equations, assumptions, limitations, and supporting literature. |
| **[References](docs/REFERENCES.md)** | Target biology, model, descriptor, and representative inhibitor bibliography. |

## Key results

| Stage | Recorded result | Auditable artifact |
|---|---:|---|
| BoltzGen designs requested / completed | 2,000 / 1,990 | Full workflow notebook |
| Unique BoltzGen sequences | 1,956 | [`batch1_design.csv`](data/designs/batch1_design.csv) |
| BoltzIF sequences / unique | 7,960 / 7,854 | [`batch1_IF_02.csv`](data/designs/batch1_IF_02.csv) |
| Unique merged designs | 9,808 | [`merged_designs.csv`](data/designs/merged_designs.csv) |
| Designs entering ranking | 9,806 | [`merged_all_2_scored.csv`](data/scored/merged_all_2_scored.csv) |
| Hard-gated candidates | 904 | [`hard_gate_904.csv`](results/screening/hard_gate_904.csv) |
| P1 / P2 / P3 review candidates | 12 / 12 / 8 | [`p1_p2_p3_top32.csv`](results/screening/p1_p2_p3_top32.csv) |
| P4 eligible / structure-review candidates | 30 / 10 | [`p4_top10.csv`](results/screening/p4_top10.csv) |
| Final synthesis candidates | **12** | [`final_12.csv`](results/final_candidates/final_12.csv) |

The final shortlist comprises **P1 × 8, P2 × 1, P3 × 1, and P4 × 2**. Every
selected peptide is linked to a predicted hIAPP complex structure.

<details>
<summary><strong>Show the final 12 D-peptide sequences</strong></summary>

| Final rank | Tier | D-peptide sequence |
|---:|:---:|---|
| 1 | P1 | `dvdiiv` |
| 2 | P1 | `epirip` |
| 3 | P1 | `fsltiegssti` |
| 4 | P1 | `ninitpg` |
| 5 | P1 | `pnsitltsssg` |
| 6 | P1 | `slslssgevtv` |
| 7 | P1 | `ttiillsyd` |
| 8 | P1 | `vnpipy` |
| 9 | P2 | `sldikp` |
| 10 | P3 | `siiidstitls` |
| 11 | P4 | `fsvtlngsntv` |
| 12 | P4 | `lnvsislttag` |

Lower-case letters denote the all-D sequence convention used by this project.

</details>

## Scientific objective

hIAPP aggregation and islet amyloid are associated with beta-cell dysfunction
in type 2 diabetes. This project targets the amyloidogenic C-terminal region of
hIAPP with proteolytically attractive D-peptide candidates. PDB 9ULZ provides
the structural template: chain D residues 19–37 are retained, and residues
21–37 define the intended binding region.

The central optimization challenge is multi-objective. A useful candidate must
balance predicted binding, structural confidence, aggregation propensity,
solubility, chemical stability, diversity, and synthetic tractability. The
workflow therefore integrates model-derived signals with interpretable
physicochemical descriptors and explicit structure review instead of relying on
a single score.

## Workflow

1. **BoltzGen backbone generation** — 2,000 peptide designs using the
   `peptide-anything` protocol and PDB 9ULZ.
2. **BoltzIF sequence diversification** — four sequences per backbone at
   temperature 0.2, with cysteine excluded.
3. **Reverse-D encoding** — sequence reversal plus explicit D stereochemistry
   in linear-peptide SMILES.
4. **Boltz-2 prediction** — hIAPP–peptide complex structures, confidence
   metrics, and three affinity heads.
5. **Physicochemical characterization** — transparent sequence-only
   solubility, aggregation-risk, stability, permeability, and drug-likeness
   tendencies.
6. **Four-layer prioritization** — hard filters, multi-metric ranking, P1–P4
   tiers, sequence de-redundancy, and manual structure review.
7. **Experimental shortlist** — 12 diverse D-peptides with traceable scores and
   predicted complexes.

## Installation and dependencies

### 1. Clone the repository

```bash
git clone https://github.com/PerinMu/hIAPP-D-peptide-design.git
cd hIAPP-D-peptide-design
```

### 2. Analysis and notebook environment

Python 3.11 or newer is recommended. This environment reproduces screening,
tables, plots, physicochemical descriptors, and repository validation without
requiring model inference.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Core analysis dependencies are version-bounded in [`requirements.txt`](requirements.txt):
Pandas, NumPy, Matplotlib, Seaborn, OpenPyXL, JupyterLab, nbclient, and ipykernel.

### 3. GPU model environments

Use separate environments for BoltzGen and Boltz, following their official
installation guidance:

```bash
# BoltzGen: Python >=3.11; Python 3.12 follows the official example
conda create -n boltzgen python=3.12 -y
conda activate boltzgen
python -m pip install --upgrade boltzgen
boltzgen --help

# Boltz-2 with CUDA support
conda create -n boltz python=3.11 -y
conda activate boltz
python -m pip install --upgrade 'boltz[cuda]'
boltz predict --help
```

Production generation and prediction require a CUDA-capable NVIDIA GPU. The
repository provides Slurm templates for multi-job execution and retry recovery.

### 4. Model downloads and caches

BoltzGen downloads its required inference assets on first use. The official
documentation estimates approximately 6 GB and uses `~/.cache` by default.
Assets can be downloaded in advance and placed in a dedicated shared cache:

```bash
conda activate boltzgen
boltzgen download all --cache /path/to/boltzgen_cache
```

Alternatively, use `--cache /path/to/cache` with BoltzGen commands or set
`HF_HOME`. Boltz-2 downloads its checkpoints and molecular data on first use;
set `BOLTZ_CACHE` to control their location:

```bash
export BOLTZ_CACHE=/path/to/boltz_cache
```

Model weights are provided by the official projects and are not duplicated in
this repository. See the [BoltzGen installation and download guide](https://github.com/HannesStark/boltzgen)
and [Boltz installation guide](https://github.com/jwohlwend/boltz) for current
hardware and package details.

## Run the notebooks

### Complete design-to-selection workflow

Open the primary notebook:

```bash
jupyter lab notebooks/00_full_generation_to_selection.ipynb
```

The first parameter cell centralizes the server project root, Conda activation
script, environment names, cache paths, and checkpoints. Review the generated
commands with `RUN_CPU_STEPS=False` and `SUBMIT_GPU_STEPS=False`; enable the
corresponding switch when the configured paths are ready. The notebook then
guides the complete sequence:

```text
9ULZ preparation → 2,000 BoltzGen designs → BoltzIF redesign
→ reverse-D SMILES → Boltz-2 YAML generation → parallel prediction
→ failed-job recovery → score collection → physicochemical properties
→ P1–P4 screening → structure review → final 12
```

The GPU steps use the portable scripts in [`hpc/`](hpc/) and preserve a clear
record of each input, output, retry, and score table.

### Reproduce the screening results

```bash
source .venv/bin/activate
jupyter lab notebooks/01_reproduce_screening.ipynb
```

Run all cells in order. Assertions verify the complete funnel:

```text
9,806 ranked designs → 904 hard-gated candidates
→ P1/P2/P3 = 12/12/8 → P4 = 30 eligible, 10 reviewed
→ 12 final candidates
```

For a non-interactive reproducibility check:

```bash
jupyter nbconvert --to notebook --execute \
  notebooks/01_reproduce_screening.ipynb \
  --output /tmp/01_reproduce_screening.executed.ipynb \
  --ExecutePreprocessor.timeout=600
```

## Screening strategy

All percentile scores are calculated over the mixed BoltzGen/BoltzIF pool; no
source quota is applied.

- **Hard gate:** complete affinity heads, `min(pTM, ipTM) >= 0.65`, solubility
  tendency `>= 40`, and aggregation risk `<= 65`.
- **Affinity consensus:** median agreement across three direction-aware
  affinity-head scores.
- **Structure quality:** 60% structure bottleneck, 20% confidence, and 20%
  inverse complex PDE percentile.
- **Developability:** favorable percentiles of solubility, aggregation risk,
  stability, peptide drug-likeness, and sequence-liability count.
- **Main ranking:** 55% affinity consensus, 30% structure quality, and 15%
  developability.
- **P1–P3:** high-confidence, continuation, and exploration tiers with
  normalized Levenshtein de-redundancy.
- **P4:** a dedicated 11–12-aa branch emphasizing structure confidence and
  additional interface-forming potential.
- **Final review:** predicted binding-region occupancy, interface contacts,
  hydrogen bonds, clashes, chain continuity, sequence diversity, and synthetic
  feasibility.

Exact equations are available in [`docs/METHODS.md`](docs/METHODS.md).

## Transparent physicochemical calculations

[`scripts/score_sequence_properties.py`](scripts/score_sequence_properties.py)
implements deterministic, inspectable descriptors rather than a hidden trained
model. Direct outputs include molecular mass, idealized charge at pH 7,
estimated pI, Kyte–Doolittle mean hydropathy, residue fractions, and the longest
hydrophobic run. Composite 0–100 tendencies support within-pool prioritization.

Every equation, residue set, pKa assumption, weight, limitation, and supporting
reference is documented in
[`docs/PHYSICOCHEMICAL.md`](docs/PHYSICOCHEMICAL.md). The literature motivates
the descriptor concepts; the composite weights and thresholds are explicitly
identified as project-specific heuristics.

## Data and result provenance

| Path | Contents |
|---|---|
| [`configs/`](configs/) | PDB 9ULZ and BoltzGen/Boltz-2 input templates. |
| [`data/designs/`](data/designs/) | Generated sequences, merged reverse-D encodings, SMILES, and the reference-inhibitor set. |
| [`data/scored/`](data/scored/) | Committed structure, affinity, and sequence-property table used for reproduction. |
| [`results/screening/`](results/screening/) | Hard-gate, P1–P3, P4, and funnel-summary tables. |
| [`results/final_candidates/`](results/final_candidates/) | Final 12 manifest and predicted complexes. |
| [`scripts/`](scripts/) | Reusable extraction, conversion, prediction-input, collection, scoring, screening, and review utilities. |
| [`hpc/`](hpc/) | Slurm submission, bounded-concurrency, and failed-job recovery templates. |
| [`wetlab/`](wetlab/) | Structured assay plan and raw-data template for experimental validation. |

The 76-entry reference-inhibitor set is linked to a grouped English provenance
index in [`reference_inhibitor_sources.csv`](data/designs/reference_inhibitor_sources.csv).
The [data dictionary](docs/DATA_DICTIONARY.md) defines every analysis field.

## Reproducibility features

- Committed inputs, exact intermediate counts, score tables, and final
  structures.
- Two complementary notebooks: full GPU workflow and lightweight CPU
  reproduction.
- Path-configurable Slurm templates with bounded parallelism and resumable
  dispatch state.
- Automatic detection and regeneration of missing Boltz-2 outputs.
- Deterministic percentile scoring and sequence de-redundancy for a fixed input
  table.
- Assertions for every published funnel count and final-manifest membership.
- GitHub Actions validation of scripts, HPC syntax, English-language content,
  source coverage, screening outputs, and executable notebook reproduction.
- Explicit separation of model predictions, physicochemical heuristics, manual
  review, and future experimental evidence.

## Experimental validation

The computational shortlist is prepared for synthesis and wet-lab evaluation.
The planned validation includes ThT aggregation kinetics across peptide
concentrations, hIAPP-only and vehicle controls, positive controls L-TQNWVP and
D-nfgail, independent repeats, concentration-response analysis, and an
orthogonal morphology or structure assay where available. The
[`wetlab/`](wetlab/) directory provides a consistent raw-data schema so future
measurements can be linked directly to candidate IDs and analysis outputs.

No experimental activity value is inferred from a model score. Boltz-2 affinity
heads are used as relative prioritization signals for peptide ligands and are
interpreted together with structure confidence, developability, and wet-lab
results.

## Documentation

- [Computational methods](docs/METHODS.md)
- [Physicochemical equations and references](docs/PHYSICOCHEMICAL.md)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Reproducibility and count reconciliation](docs/REPRODUCIBILITY.md)
- [Scientific bibliography](docs/REFERENCES.md)

## Citation and license

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). Scientific
use should also cite BoltzGen, Boltz-2, and PDB 9ULZ as listed in
[`docs/REFERENCES.md`](docs/REFERENCES.md).

Repository code is released under the [MIT License](LICENSE). External model
weights, packages, and structural data remain subject to their respective
licenses and terms.
