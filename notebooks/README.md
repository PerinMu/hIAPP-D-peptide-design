# Reproducible notebooks

## 1. Full generation-to-selection workflow

Open [`00_full_generation_to_selection.ipynb`](00_full_generation_to_selection.ipynb)
to reproduce the complete GPU workflow:

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
