# Portable HPC templates

These scripts capture the original workflow while removing cluster usernames,
private proxy endpoints and fixed absolute paths. Inspect and edit every `#SBATCH`
directive for your site.

1. Follow `notebooks/00_full_generation_to_selection.ipynb` for the full order.
2. Set `REPO_ROOT`, `PROJECT_ROOT`, environment names and model/cache paths.
3. Submit BoltzGen with `run_boltzgen_design.slurm` and
   `run_boltzgen_inverse_folding.slurm`.
4. Generate one YAML per peptide with `scripts/make_boltz_yaml.py`.
5. Submit a single test with
   `sbatch --array=1-1%1 run_lig_array_large.slurm input/example.yaml`.
6. Reproduce the historical dispatcher interface with
   `bash submit_keep8.sh input/batch 8 20 state run_lig_array_large.slurm boltz_arr 1`.
7. Recover incomplete jobs with `scripts/find_missing_model0.py`.
8. Collect score JSON and CIF files using the repository scripts.

The bounded dispatcher records submitted YAML stems in a state directory and
limits jobs whose names start with the chosen prefix. It does not delete or
overwrite model results.

The historical scripts were recovered. The current files preserve their control
flow while replacing usernames, private paths and proxy configuration with
environment variables. Original SHA256 values are recorded under
`legacy/original_hpc/README.md`.
