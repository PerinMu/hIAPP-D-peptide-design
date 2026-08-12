#!/usr/bin/env bash
#SBATCH --job-name=boltz_lig
#SBATCH --time=02:00:00
#SBATCH --partition=gpu_4090
#SBATCH --gpus=1
#SBATCH --output=logs/%x_%j.log
#SBATCH --error=logs/%x_%j.log

# Public, configurable form of the historical Boltz single-YAML runner.

set -euo pipefail
export PYTHONUNBUFFERED=1

: "${PROJECT_ROOT:?Set PROJECT_ROOT to the server computation directory}"
: "${CONDA_ENV:?Set CONDA_ENV to the Boltz environment name}"
: "${BOLTZ_CACHE:?Set BOLTZ_CACHE to the model cache directory}"

source "${CONDA_SH:-/opt/conda/etc/profile.d/conda.sh}"
conda activate "${CONDA_ENV}"
if [[ -n "${CUDA_MODULE:-}" ]]; then
  module load "${CUDA_MODULE}"
fi
if [[ -n "${HTTP_PROXY_URL:-}" ]]; then
  export http_proxy=${HTTP_PROXY_URL}
  export https_proxy=${HTTP_PROXY_URL}
fi

INPUT_DIR=${PROJECT_ROOT}/input
LOG_DIR=${PROJECT_ROOT}/logs
OUT_ROOT=${BOLTZ_OUTPUTS:-${PROJECT_ROOT}/outputs_boltz2}
TMP_BASE=${PROJECT_ROOT}/tmp
mkdir -p "${LOG_DIR}" "${OUT_ROOT}" "${TMP_BASE}" "${BOLTZ_CACHE}"
export TMPDIR=${TMP_BASE}
export TEMP=${TMP_BASE}
export TMP=${TMP_BASE}

YAML_ARGUMENT=${1:?Usage: run_lig_one_large.sh YAML_PATH}
if [[ "${YAML_ARGUMENT}" = /* ]]; then
  YAML_PATH=${YAML_ARGUMENT}
elif [[ "${YAML_ARGUMENT}" == input/* ]]; then
  YAML_PATH=${PROJECT_ROOT}/${YAML_ARGUMENT}
else
  YAML_PATH=${INPUT_DIR}/${YAML_ARGUMENT}
fi
if [[ ! -f "${YAML_PATH}" ]]; then
  echo "[ERROR] YAML file not found: ${YAML_PATH}" >&2
  exit 1
fi

YAML_NAME=$(basename "${YAML_PATH}")
SAMPLE_ID=${YAML_NAME%.*}
RUN_DATE=$(date +%Y%m%d)
JOB_ID=${SLURM_JOB_ID:-manual}
OUT_DIR=${OUT_ROOT}/${SAMPLE_ID}_${RUN_DATE}_${JOB_ID}
DONE_FLAG=${TMP_BASE}/boltz_over_${JOB_ID}
rm -f "${DONE_FLAG}"

gpu_stat() {
  local stat_log=${LOG_DIR}/gpu_stat.${JOB_ID}.log
  rm -f "${stat_log}"
  while [[ ! -f "${DONE_FLAG}" ]]; do
    {
      echo "---- $(date +'%F %T')"
      nvidia-smi --format=csv \
        --query-gpu=memory.used,memory.free,utilization.gpu,utilization.memory
      free -g
    } >> "${stat_log}"
    sleep 5
  done
}
if [[ "${DEBUG:-0}" -eq 1 ]]; then
  export PYTHONFAULTHANDLER=1
  export TORCH_SHOW_CPP_STACKTRACES=1
  export BOLTZ_DEBUG=1
  gpu_stat &
fi

echo "[$(date +'%F %T')] YAML_PATH=${YAML_PATH}"
echo "[$(date +'%F %T')] OUT_DIR=${OUT_DIR}"
echo "[$(date +'%F %T')] BOLTZ_CACHE=${BOLTZ_CACHE}"

exit_code=0
boltz predict "${YAML_PATH}" \
  --out_dir "${OUT_DIR}" \
  --cache "${BOLTZ_CACHE}" \
  --accelerator gpu \
  --devices 1 \
  --diffusion_samples "${DIFFUSION_SAMPLES:-3}" \
  --use_potentials \
  --use_msa_server || exit_code=$?

touch "${DONE_FLAG}"
echo "$(date +'%F %T') exit_code=${exit_code}"
exit "${exit_code}"
