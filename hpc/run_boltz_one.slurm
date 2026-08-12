#!/usr/bin/env bash
#SBATCH --job-name=hiapp_boltz
#SBATCH --time=01:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/%x_%j.log
#SBATCH --error=logs/%x_%j.log

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: sbatch run_boltz_one.slurm INPUT.yaml" >&2
  exit 2
fi

: "${PROJECT_ROOT:?Set PROJECT_ROOT to the server project directory}"
: "${CONDA_ENV:?Set CONDA_ENV to the Boltz environment name}"
: "${BOLTZ_CACHE:?Set BOLTZ_CACHE to the model cache directory}"

YAML_PATH="$(realpath "$1")"
SAMPLE_ID="$(basename "${YAML_PATH%.*}")"
RUN_STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_ROOT="${BOLTZ_OUTPUTS:-${PROJECT_ROOT}/outputs}"
OUT_DIR="${OUT_ROOT}/${SAMPLE_ID}_${RUN_STAMP}_${SLURM_JOB_ID}"

mkdir -p "${PROJECT_ROOT}/logs" "${OUT_ROOT}" "${PROJECT_ROOT}/tmp"
source "${CONDA_SH:-/opt/conda/etc/profile.d/conda.sh}"
conda activate "${CONDA_ENV}"

export TMPDIR="${PROJECT_ROOT}/tmp"
export PYTHONUNBUFFERED=1

boltz predict "${YAML_PATH}" \
  --out_dir "${OUT_DIR}" \
  --cache "${BOLTZ_CACHE}" \
  --accelerator gpu \
  --devices 1 \
  --diffusion_samples "${DIFFUSION_SAMPLES:-3}" \
  --use_msa_server \
  --use_potentials
