#!/usr/bin/env bash
#SBATCH --job-name=hiapp_bg_design
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=8
#SBATCH --output=logs/%x_%j.log
#SBATCH --error=logs/%x_%j.log

set -euo pipefail

: "${REPO_ROOT:?Set REPO_ROOT to the cloned repository}"
: "${BOLTZGEN_OUTPUT:?Set BOLTZGEN_OUTPUT}"
: "${BOLTZGEN_MOLDIR:?Set BOLTZGEN_MOLDIR}"
: "${BOLTZGEN_DESIGN_CHECKPOINT:?Set BOLTZGEN_DESIGN_CHECKPOINT}"
: "${CONDA_ENV_BOLTZGEN:=boltzgen}"

source "${CONDA_SH:-/opt/conda/etc/profile.d/conda.sh}"
conda activate "${CONDA_ENV_BOLTZGEN}"
mkdir -p "${BOLTZGEN_OUTPUT}" "$(dirname "${BOLTZGEN_OUTPUT}")" logs
cd "${REPO_ROOT}"

REUSE_ARGUMENT=()
if [[ "${BOLTZGEN_REUSE:-0}" == "1" ]]; then
  REUSE_ARGUMENT=(--reuse)
fi

boltzgen check configs/boltzgen/9ULZ.yaml
boltzgen run configs/boltzgen/9ULZ.yaml \
  --output "${BOLTZGEN_OUTPUT}" \
  --protocol peptide-anything \
  --steps design \
  --num_designs "${NUM_DESIGNS:-2000}" \
  --diffusion_batch_size "${DIFFUSION_BATCH_SIZE:-10}" \
  --moldir "${BOLTZGEN_MOLDIR}" \
  --design_checkpoints "${BOLTZGEN_DESIGN_CHECKPOINT}" \
  "${REUSE_ARGUMENT[@]}"
