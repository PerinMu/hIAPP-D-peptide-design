#!/usr/bin/env bash
# Keep up to N independently submitted Slurm jobs active.
#
# Usage:
#   bash submit_keep8.sh YAML_DIR TARGET_ACTIVE CHECK_INTERVAL STATE_DIR \
#     ARRAY_SCRIPT JOB_NAME START_INDEX
#
# This path-neutral form keeps the historical seven-argument interface,
# one-element Slurm array submission, sorted index state, lock and resumability.

set -uo pipefail

YAML_DIR=${1:?Missing YAML directory}
TARGET_ACTIVE=${2:-8}
CHECK_INTERVAL=${3:-20}
STATE_DIR=${4:-"/tmp/keep8_${USER}"}
ARRAY_SCRIPT=${5:?Missing Slurm array script}
JOB_NAME=${6:-boltz_arr}
START_INDEX=${7:-1}

if [[ ! -d "${YAML_DIR}" ]]; then
  echo "[ERROR] YAML directory not found: ${YAML_DIR}" >&2
  exit 1
fi
if [[ ! -f "${ARRAY_SCRIPT}" ]]; then
  echo "[ERROR] Array script not found: ${ARRAY_SCRIPT}" >&2
  exit 1
fi
for value_name in TARGET_ACTIVE CHECK_INTERVAL START_INDEX; do
  value=${!value_name}
  if ! [[ "${value}" =~ ^[1-9][0-9]*$ ]]; then
    echo "[ERROR] ${value_name} must be a positive integer: ${value}" >&2
    exit 1
  fi
done

mkdir -p "${STATE_DIR}"
exec 9>"${STATE_DIR}/dispatcher.lock"
if ! flock -n 9; then
  echo "[ERROR] Another dispatcher is already using ${STATE_DIR}" >&2
  exit 1
fi

YAML_LIST="${STATE_DIR}/yaml_files.sorted.txt"
NEXT_FILE="${STATE_DIR}/next_index"
SUBMIT_LOG="${STATE_DIR}/submitted.tsv"
find "${YAML_DIR}" -maxdepth 1 -type f \
  \( -name '*.yaml' -o -name '*.yml' \) -print \
  | LC_ALL=C sort > "${YAML_LIST}"
TOTAL_YAMLS=$(wc -l < "${YAML_LIST}")
TOTAL_YAMLS=${TOTAL_YAMLS//[[:space:]]/}
if [[ "${TOTAL_YAMLS}" -eq 0 ]]; then
  echo "[ERROR] No YAML files found in ${YAML_DIR}" >&2
  exit 1
fi

if [[ -s "${NEXT_FILE}" ]]; then
  NEXT=$(cat "${NEXT_FILE}")
else
  NEXT=${START_INDEX}
  printf '%s\n' "${NEXT}" > "${NEXT_FILE}"
fi
if ! [[ "${NEXT}" =~ ^[1-9][0-9]*$ ]]; then
  echo "[ERROR] Invalid next index in ${NEXT_FILE}: ${NEXT}" >&2
  exit 1
fi
if [[ ! -f "${SUBMIT_LOG}" ]]; then
  printf 'time\tindex\tyaml_path\tsbatch_output\n' > "${SUBMIT_LOG}"
fi

active_jobs() {
  squeue -u "${USER}" -h -n "${JOB_NAME}" -t R,PD -o '%i' 2>/dev/null \
    | awk 'NF {count++} END {print count+0}'
}

save_next() {
  local temporary="${NEXT_FILE}.tmp.$$"
  printf '%s\n' "${NEXT}" > "${temporary}"
  mv -f "${temporary}" "${NEXT_FILE}"
}

submit_one() {
  local index=$1
  local yaml_path=$2
  local output
  local sbatch_arguments=(--array=1-1%1)
  local log_dir=${SLURM_LOG_DIR:-${PROJECT_ROOT:-}/logs}
  if [[ -n "${log_dir}" && "${log_dir}" != "/logs" ]]; then
    mkdir -p "${log_dir}"
    sbatch_arguments+=(
      --output="${log_dir}/${JOB_NAME}_%A_%a.log"
      --error="${log_dir}/${JOB_NAME}_%A_%a.log"
    )
  fi
  if output=$(sbatch "${sbatch_arguments[@]}" "${ARRAY_SCRIPT}" "${yaml_path}" 2>&1); then
    printf '%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "${index}" \
      "${yaml_path}" "${output}" | tee -a "${SUBMIT_LOG}"
    return 0
  fi
  echo "$(date '+%F %T') [WARN] sbatch failed for index ${index}: ${output}" >&2
  return 1
}

echo "YAML_DIR       = ${YAML_DIR}"
echo "TOTAL YAMLs    = ${TOTAL_YAMLS}"
echo "TARGET_ACTIVE  = ${TARGET_ACTIVE}"
echo "CHECK_INTERVAL = ${CHECK_INTERVAL}s"
echo "STATE_DIR      = ${STATE_DIR}"
echo "ARRAY_SCRIPT   = ${ARRAY_SCRIPT}"
echo "JOB_NAME       = ${JOB_NAME}"
echo "START/NEXT     = ${NEXT}"

trap 'echo "$(date "+%F %T") | Dispatcher stopped."; exit 0' INT TERM
while true; do
  if [[ "${NEXT}" -gt "${TOTAL_YAMLS}" ]]; then
    ACTIVE=$(active_jobs)
    if [[ "${ACTIVE}" -eq 0 ]]; then
      echo "$(date '+%F %T') | All YAMLs submitted and all jobs finished."
      exit 0
    fi
    echo "$(date '+%F %T') | All YAMLs submitted; ${ACTIVE} jobs still active."
    sleep "${CHECK_INTERVAL}"
    continue
  fi

  ACTIVE=$(active_jobs)
  SLOTS=$((TARGET_ACTIVE - ACTIVE))
  if [[ "${SLOTS}" -le 0 ]]; then
    echo "$(date '+%F %T') | Active=${ACTIVE}; next=${NEXT}; sleeping ${CHECK_INTERVAL}s"
    sleep "${CHECK_INTERVAL}"
    continue
  fi

  while [[ "${SLOTS}" -gt 0 && "${NEXT}" -le "${TOTAL_YAMLS}" ]]; do
    YAML_PATH=$(sed -n "${NEXT}p" "${YAML_LIST}")
    if [[ -z "${YAML_PATH}" ]]; then
      echo "[ERROR] No YAML path at index ${NEXT}" >&2
      exit 1
    fi
    if submit_one "${NEXT}" "${YAML_PATH}"; then
      NEXT=$((NEXT + 1))
      save_next
      SLOTS=$((SLOTS - 1))
      sleep 1
    else
      break
    fi
  done
  sleep "${CHECK_INTERVAL}"
done
