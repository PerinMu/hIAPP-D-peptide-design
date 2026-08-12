#!/usr/bin/env bash
#SBATCH --job-name=boltz_arr
#SBATCH --time=02:00:00
#SBATCH --partition=gpu_4090
#SBATCH --gpus=1
#SBATCH --output=logs/boltz_arr_%A_%a.log
#SBATCH --error=logs/boltz_arr_%A_%a.log

set -euo pipefail

: "${REPO_ROOT:?Set REPO_ROOT to this cloned repository}"
INPUT_PATH=${1:?Usage: sbatch run_lig_array_large.slurm YAML_PATH_OR_LIST}

if [[ "${INPUT_PATH}" == *.yaml || "${INPUT_PATH}" == *.yml ]]; then
  YAML_PATH=${INPUT_PATH}
  TASK_LABEL=${SLURM_ARRAY_TASK_ID:-1}
else
  : "${SLURM_ARRAY_TASK_ID:?Required for YAML-list mode}"
  YAML_PATH=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "${INPUT_PATH}")
  TASK_LABEL=${SLURM_ARRAY_TASK_ID}
fi

if [[ -z "${YAML_PATH}" || ! -f "${YAML_PATH}" ]]; then
  echo "[ERROR] YAML file not found: ${YAML_PATH:-<empty>}" >&2
  exit 1
fi
echo "[$(date +'%F %T')] ARRAY_TASK=${TASK_LABEL}"
echo "[$(date +'%F %T')] YAML_PATH=${YAML_PATH}"
exec bash "${REPO_ROOT}/hpc/run_lig_one_large.sh" "${YAML_PATH}"

