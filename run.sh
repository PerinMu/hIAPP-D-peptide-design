#!/usr/bin/env bash
# One-command CPU reproduction entry point for the competition submission.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SCORES="${REPO_ROOT}/data/scored/merged_all_2_scored.csv"
FINAL="${REPO_ROOT}/results/final_candidates/final_12.csv"
OUTPUT_DIR="${REPO_ROOT}/results/submission"

usage() {
  echo "Usage: bash run.sh [--scores FILE] [--final FILE] [--output-dir DIR]" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scores|--final|--output-dir)
      if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
        echo "Missing value for $1" >&2; usage; exit 2
      fi
      case "$1" in
        --scores) SCORES="$2" ;;
        --final) FINAL="$2" ;;
        --output-dir) OUTPUT_DIR="$2" ;;
      esac
      shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

mkdir -p "${OUTPUT_DIR}/screening"

"${PYTHON_BIN}" "${REPO_ROOT}/scripts/screen_candidates.py" \
  "${SCORES}" "${OUTPUT_DIR}/screening"

"${PYTHON_BIN}" "${REPO_ROOT}/scripts/generate_submission_results.py" \
  --scores "${SCORES}" \
  --final "${FINAL}" \
  --structures "${REPO_ROOT}/results/final_candidates/structures" \
  --screening-dir "${OUTPUT_DIR}/screening" \
  --output "${OUTPUT_DIR}/results.csv" \
  --metadata "${OUTPUT_DIR}/run_metadata.json"

echo "Submission results: ${OUTPUT_DIR}/results.csv"
echo "Run metadata: ${OUTPUT_DIR}/run_metadata.json"
