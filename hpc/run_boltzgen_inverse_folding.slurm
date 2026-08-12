#!/usr/bin/env bash
#SBATCH --job-name=hiapp_bg_ifold
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=8
#SBATCH --output=logs/%x_%j.log
#SBATCH --error=logs/%x_%j.log

set -euo pipefail

: "${REPO_ROOT:?Set REPO_ROOT to the cloned repository}"
: "${BOLTZGEN_OUTPUT:?Set BOLTZGEN_OUTPUT from the design stage}"
: "${BOLTZGEN_IFOLD_OUTPUT:?Set BOLTZGEN_IFOLD_OUTPUT}"
: "${BOLTZGEN_MOLDIR:?Set BOLTZGEN_MOLDIR}"
: "${BOLTZGEN_IFOLD_CHECKPOINT:?Set BOLTZGEN_IFOLD_CHECKPOINT}"
: "${CONDA_ENV_BOLTZGEN:=boltzgen}"

source "${CONDA_SH:-/opt/conda/etc/profile.d/conda.sh}"
conda activate "${CONDA_ENV_BOLTZGEN}"
mkdir -p "${BOLTZGEN_IFOLD_OUTPUT}" logs
cd "${REPO_ROOT}"

REUSE_ARGUMENT=()
if [[ "${BOLTZGEN_REUSE:-0}" == "1" ]]; then
  REUSE_ARGUMENT=(--reuse)
fi

python scripts/run_boltzgen_inverse_folding.py \
  --design-dir "${BOLTZGEN_OUTPUT}/intermediate_designs" \
  --output-dir "${BOLTZGEN_IFOLD_OUTPUT}" \
  --moldir "${BOLTZGEN_MOLDIR}" \
  --checkpoint "${BOLTZGEN_IFOLD_CHECKPOINT}" \
  --sequences-per-backbone 4 \
  --temperature 0.2 \
  --avoid C \
  --devices "${NUM_GPUS:-4}" \
  --num-workers "${NUM_WORKERS:-4}" \
  "${REUSE_ARGUMENT[@]}"

