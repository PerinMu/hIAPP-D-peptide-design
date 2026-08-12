#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 6 ]]; then
  echo "Usage: $0 YAML_DIR [MAX_JOBS=8] [POLL_SECONDS=20] [STATE_DIR] [JOB_PREFIX=hiapp_boltz] [RUNNER]" >&2
  exit 2
fi

YAML_DIR="$(realpath "$1")"
MAX_JOBS="${2:-8}"
POLL_SECONDS="${3:-20}"
STATE_DIR="${4:-${YAML_DIR}/dispatch_state}"
JOB_PREFIX="${5:-hiapp_boltz}"
RUNNER="${6:-${RUNNER:-$(cd "$(dirname "$0")" && pwd)/run_boltz_one.slurm}}"

mkdir -p "${STATE_DIR}"
STATE_DIR="$(realpath "${STATE_DIR}")"
SUBMITTED="${STATE_DIR}/submitted.txt"
touch "${SUBMITTED}"

mapfile -t YAML_FILES < <(
  find "${YAML_DIR}" \
    -path "${STATE_DIR}" -prune -o \
    -type f \( -name '*.yaml' -o -name '*.yml' \) -print | sort
)
if (( ${#YAML_FILES[@]} == 0 )); then
  echo "No YAML files found under ${YAML_DIR}" >&2
  exit 1
fi

for yaml in "${YAML_FILES[@]}"; do
  stem="$(basename "${yaml%.*}")"
  if grep -Fxq "${stem}" "${SUBMITTED}"; then
    continue
  fi

  while true; do
    active="$(squeue -h -u "${USER}" -n "${JOB_PREFIX}" | wc -l | tr -d ' ')"
    if (( active < MAX_JOBS )); then
      break
    fi
    sleep "${POLL_SECONDS}"
  done

  sbatch --job-name="${JOB_PREFIX}" "${RUNNER}" "${yaml}"
  printf '%s\n' "${stem}" >> "${SUBMITTED}"
  sleep 1
done

echo "Submitted all new inputs. State: ${SUBMITTED}"
