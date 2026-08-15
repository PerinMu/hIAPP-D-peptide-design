# Portable HPC templates

These scripts provide a path-configurable Slurm implementation of the complete
GPU workflow. Inspect and edit every `#SBATCH` directive for your site.

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

All resource requests, environment names, cache locations, output paths, and
concurrency limits are controlled through command arguments or environment
variables, making the templates portable across Slurm clusters.

## Historical provenance recovery

Two site-specific, read-only collectors recover reproducibility metadata from
the original August 2026 cloud environments without rerunning a model:

- `collect_provenance_boltzgen_scz0223.sh` covers the Singularity-based
  BoltzGen and BoltzIF environment.
- `collect_provenance_boltz2_scxj525.sh` covers the Conda/CUDA Boltz-2
  environment and records the installed MSA-server implementation clues.

Run the applicable collector once with `bash` on its login node. It submits
itself as a one-GPU Slurm job, hashes checkpoints and containers without copying
them, captures package/GPU/Slurm metadata, and writes a `.tar.gz` archive plus a
SHA-256 sidecar under the project's `provenance/` directory. The collectors do
not read shell history, copy predicted structures, or export credentials. Review
the archive before publication because account paths and compute-node hostnames
are retained as provenance evidence.
