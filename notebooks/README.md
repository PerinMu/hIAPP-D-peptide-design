# Reproducible generative D-peptide design notebooks

The notebooks present a reusable design architecture and its complete hIAPP
instantiation. Target structure, binding site, model paths, campaign size, and
execution switches are exposed explicitly so the workflow can be adapted
without rewriting the core scripts.

## 1. Full generation-to-selection workflow

Open [`00_full_generation_to_selection.ipynb`](00_full_generation_to_selection.ipynb)
to reproduce the complete GPU workflow. For a new target, replace the structural
inputs and parameter-cell values described in the notebook; the hIAPP run is the
fully documented reference configuration:

```text
PDB 9ULZ → BoltzGen → BoltzIF → reverse-D SMILES → Boltz-2
→ retry recovery → score collection → physicochemical descriptors
→ P1-P4 prioritization → structure review → final 12
```

The first parameter cell contains all server, environment, cache, and checkpoint
paths. Slurm submission and CPU processing are controlled independently.

## 2. Screening-only reproduction

Open [`01_reproduce_screening.ipynb`](01_reproduce_screening.ipynb) for the
fastest verification of the reported results. It executes on CPU from committed
data and asserts every funnel count, priority-tier count, structure link, and
final candidate.

```bash
jupyter lab notebooks/01_reproduce_screening.ipynb
```

The same notebook is executed automatically by GitHub Actions on every update.
