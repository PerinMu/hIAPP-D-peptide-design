# Notebooks

## Full workflow

[00_full_generation_to_selection.ipynb](00_full_generation_to_selection.ipynb)
contains installation and execution steps for:

```text
BoltzGen → BoltzIF → reverse-D SMILES → Boltz-2 → screening → structure review
```

Configure server paths, environments, caches, and checkpoints in the first
parameter cell. CPU processing and Slurm submission have separate execution
switches, both disabled by default. Wait for each GPU job to finish before
processing its output. New runs may produce different sequences and counts.

## CPU reproduction

[01_reproduce_screening.ipynb](01_reproduce_screening.ipynb) uses the saved score
table to reproduce the filters and rankings. It checks candidate counts, tiers,
structure files, and final-selection membership.

```bash
jupyter lab notebooks/01_reproduce_screening.ipynb
```

GitHub Actions executes this notebook on each push and pull request.
