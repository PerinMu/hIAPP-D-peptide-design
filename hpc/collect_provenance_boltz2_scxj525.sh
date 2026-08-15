#!/usr/bin/env bash
# Run once on the scxj525 login node with:
#   bash collect_provenance_boltz2_scxj525.sh
# The script self-submits a one-GPU Slurm job and never reruns Boltz-2.
#SBATCH --job-name=prov_boltz2
#SBATCH --partition=gpu_4090
#SBATCH --gpus=1
#SBATCH --time=01:00:00
#SBATCH --output=provenance_boltz2_%j.log
#SBATCH --error=provenance_boltz2_%j.log

set -uo pipefail
umask 077

PROJECT_ROOT="${PROJECT_ROOT:-/data/run01/scxj525/XMY}"
CONDA_SH="${CONDA_SH:-/data/apps/miniforge3/25.11.0-1/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-py310_env}"
BOLTZ_CACHE="${BOLTZ_CACHE:-/data/run01/scxj525/boltz_cache}"
LEGACY_BOLTZ_CACHE="${LEGACY_BOLTZ_CACHE:-/data/home/scxj525/run/test/boltz_cache}"
PROVENANCE_ROOT="${PROVENANCE_ROOT:-${PROJECT_ROOT}/provenance}"

SELF_PATH="$(readlink -f "$0" 2>/dev/null || printf '%s' "$0")"

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    mkdir -p "${PROVENANCE_ROOT}"
    cd "${PROJECT_ROOT}" || exit 1
    JOB_ID="$(sbatch --parsable --gpus=1 -p gpu_4090 "${SELF_PATH}" --worker)" || exit 1
    echo "Submitted Boltz-2 provenance job: ${JOB_ID}"
    echo "Monitor with: parajobs"
    echo "After completion, run: ls -lh ${PROVENANCE_ROOT}/LATEST_boltz2.txt ${PROVENANCE_ROOT}/*.tar.gz*"
    exit 0
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BUNDLE="${PROVENANCE_ROOT}/boltz2_scxj525_${STAMP}_job${SLURM_JOB_ID}"
mkdir -p "${BUNDLE}/snapshots"

capture() {
    local output_file="$1"
    shift
    {
        printf 'COMMAND:'
        printf ' %q' "$@"
        printf '\n'
        "$@"
        printf '\nEXIT_CODE=%s\n' "$?"
    } >"${BUNDLE}/${output_file}" 2>&1
    return 0
}

copy_snapshot() {
    local source_path="$1"
    if [[ -f "${source_path}" ]]; then
        local safe_name
        safe_name="$(printf '%s' "${source_path}" | sed 's#^/##; s#/#__#g')"
        cp -L -- "${source_path}" "${BUNDLE}/snapshots/${safe_name}"
    fi
}

hash_one() {
    local path="$1"
    if [[ -f "${path}" || -L "${path}" ]]; then
        local resolved
        resolved="$(readlink -f "${path}" 2>/dev/null || printf '%s' "${path}")"
        printf 'PATH=%s\nRESOLVED=%s\n' "${path}" "${resolved}"
        stat -Lc 'SIZE_BYTES=%s\nMTIME=%y' "${path}" 2>/dev/null || true
        sha256sum "${path}" 2>/dev/null || true
        printf '\n'
    fi
}

if [[ -r /etc/profile.d/modules.sh ]]; then
    # shellcheck disable=SC1091
    source /etc/profile.d/modules.sh
fi
module load cuda/12.8 >/dev/null 2>&1 || true
# shellcheck disable=SC1090
source "${CONDA_SH}"
conda activate "${CONDA_ENV}"

cat >"${BUNDLE}/README.txt" <<EOF
Purpose: historical provenance recovery for the August 2026 hIAPP Boltz-2 campaign.
Collection time (UTC): ${STAMP}
Slurm job: ${SLURM_JOB_ID}
This bundle contains metadata, software manifests, hashes, endpoint-source clues, and small configuration snapshots.
It does not contain model weights, predicted structures, shell history, tokens, or full environment variables.
Review the bundle before external publication because hostnames and account paths are preserved for provenance.
EOF

capture system_identity.txt bash -c 'date -u; date; hostname; id; pwd; uname -a; cat /etc/os-release 2>/dev/null; lscpu; free -h'
capture slurm_environment.txt bash -c 'env | LC_ALL=C sort | grep -E "^(SLURM_|CUDA_VISIBLE_DEVICES=|CONDA_DEFAULT_ENV=|CONDA_PREFIX=)" || true; for n in http_proxy https_proxy HF_ENDPOINT; do [[ -n "${!n:-}" ]] && echo "$n=SET" || echo "$n=UNSET"; done'
capture slurm_job.txt scontrol show job "${SLURM_JOB_ID}"
capture slurm_node.txt bash -c 'scontrol show node "${SLURMD_NODENAME:-$(hostname)}" 2>/dev/null || true'
capture slurm_config.txt bash -c 'scontrol show config 2>/dev/null | grep -E "^(ClusterName|SlurmctldHost|SlurmctldParameters|SelectType|GresTypes|SchedulerType|SlurmctldVersion)" || true'
capture historical_jobs_2026-08-04_to_08-10.txt bash -c 'sacct -u "$USER" -S 2026-08-04 -E 2026-08-10 -X --format=JobIDRaw,JobName%35,Partition,State,Elapsed,AllocTRES%45,Start,End,NodeList%30 2>/dev/null || true'
capture historical_node_records.txt bash -c 'sacct -u "$USER" -S 2026-08-04 -E 2026-08-10 -X -n -o NodeList 2>/dev/null | sed "s/^[[:space:]]*//;s/[[:space:]]*$//" | grep -Ev "^$|None|Unknown" | sort -u | while read -r spec; do scontrol show hostnames "$spec" 2>/dev/null || true; done | sort -u | while read -r node; do echo "HISTORICAL_NODE=$node"; scontrol show node "$node" 2>/dev/null || true; echo; done'
capture nvidia_smi.txt nvidia-smi
capture nvidia_query.csv nvidia-smi --query-gpu=index,name,uuid,driver_version,vbios_version,pci.bus_id,memory.total,compute_cap --format=csv
capture cuda_compiler.txt bash -c 'nvcc --version 2>/dev/null || true; ldconfig -p 2>/dev/null | grep -E "libcuda|libcudnn" | head -n 100 || true'
capture module_state.txt bash -lc 'source /etc/profile.d/modules.sh 2>/dev/null || true; module list 2>&1 || true; module show cuda/12.8 2>&1 || true'

capture boltz_version.txt bash -c 'boltz --version 2>&1 || true; python -c "import importlib.metadata as m; print(m.version(\"boltz\"))"'
capture boltz_predict_help.txt boltz predict --help
capture python_runtime.txt python -c 'import importlib.metadata as m, platform, sys; print("python", sys.version); print("platform", platform.platform()); names=["boltz","torch","numpy","pandas","rdkit","jax","lightning","pytorch-lightning"]; installed={d.metadata.get("Name","").lower():d.version for d in m.distributions()}; [print(n,installed.get(n,"NOT_INSTALLED")) for n in names]'
capture torch_runtime.txt python -c 'import torch; print("torch",torch.__version__); print("torch_cuda",torch.version.cuda); print("cudnn",torch.backends.cudnn.version()); print("cuda_available",torch.cuda.is_available()); print("device_count",torch.cuda.device_count()); [print(i,torch.cuda.get_device_name(i),torch.cuda.get_device_properties(i)) for i in range(torch.cuda.device_count())]'
capture pip_show.txt python -m pip show boltz torch numpy pandas rdkit jax lightning pytorch-lightning
capture pip_freeze.txt python -m pip freeze
capture conda_list.txt conda list
capture conda_explicit.txt conda list --explicit
capture conda_environment.yml conda env export --no-builds
capture boltz_module_path.txt python -c 'import boltz, inspect; print(boltz.__file__); print(inspect.getfile(boltz))'

BOLTZ_PACKAGE_ROOT="$(python -c 'import pathlib, boltz; print(pathlib.Path(boltz.__file__).resolve().parent)' 2>/dev/null || true)"
if [[ -n "${BOLTZ_PACKAGE_ROOT}" && -d "${BOLTZ_PACKAGE_ROOT}" ]]; then
    capture msa_server_source_scan.txt bash -c 'grep -RInE "msa.server|msa_server|colabfold|mmseqs|api_url|endpoint" "'$BOLTZ_PACKAGE_ROOT'" --include="*.py" --include="*.yaml" --include="*.yml" 2>/dev/null | head -n 5000 || true'
    capture installed_boltz_source_manifest.txt bash -c 'find "'$BOLTZ_PACKAGE_ROOT'" -type f -name "*.py" -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum'
fi

capture git_repositories.txt bash -c '
for root in "'$PROJECT_ROOT'" "${CONDA_PREFIX:-}"; do
  [[ -d "$root" ]] || continue
  find "$root" -maxdepth 5 -type d -name .git -print 2>/dev/null | sort | while read -r dotgit; do
    repo=${dotgit%/.git}; echo "REPOSITORY=$repo"; git -C "$repo" rev-parse HEAD 2>/dev/null || true; git -C "$repo" describe --always --dirty --tags 2>/dev/null || true; git -C "$repo" remote -v 2>/dev/null || true; git -C "$repo" status --short 2>/dev/null || true; echo; done
done'

{
    for root in "${BOLTZ_CACHE}" "${LEGACY_BOLTZ_CACHE}"; do
        echo "CACHE_ROOT=${root}"
        [[ -d "${root}" ]] || { echo MISSING; echo; continue; }
        find -L "${root}" -type f \( -iname '*.ckpt' -o -iname '*.pt' -o -iname '*.pth' -o -iname '*.safetensors' -o -size +100M \) -print 2>/dev/null | sort -u | while read -r file; do
            hash_one "${file}"
        done
    done
} >"${BUNDLE}/model_cache_sha256.txt" 2>&1

for path in \
    "${PROJECT_ROOT}/run_lig_one_large.sh" \
    "${PROJECT_ROOT}/run_lig_array_large.sh" \
    "${PROJECT_ROOT}/run_lig_array_large_fixed.sh" \
    "${PROJECT_ROOT}/submit_keep8.sh" \
    "${PROJECT_ROOT}/collect_boltz_merged.py" \
    "${PROJECT_ROOT}/collect_boltz_scores.py" \
    "${PROJECT_ROOT}/collect_boltz_cif.sh" \
    "${PROJECT_ROOT}/input/hIAPP_template.yaml" \
    "${PROJECT_ROOT}/input/merged_designs_reversed_smiles.csv" \
    "${PROJECT_ROOT}/summary/merged_all_1.csv" \
    "${PROJECT_ROOT}/summary/merged_all_2.csv"; do
    copy_snapshot "${path}"
done

capture project_file_manifest.txt bash -c 'find "'$PROJECT_ROOT'" -maxdepth 3 -type f -printf "%TY-%Tm-%TdT%TH:%TM:%TS\t%s\t%p\n" 2>/dev/null | sort'
capture yaml_batch_counts.txt bash -c 'for d in "'$PROJECT_ROOT'"/input/*yaml*; do [[ -d "$d" ]] || continue; printf "%s\t" "$d"; find "$d" -maxdepth 1 -type f \( -name "*.yaml" -o -name "*.yml" \) | wc -l; done'
capture output_counts.txt bash -c 'echo "OUTPUT_ROOT='$PROJECT_ROOT'/outputs"; if [[ -d "'$PROJECT_ROOT'/outputs" ]]; then printf "task_directories="; find "'$PROJECT_ROOT'/outputs" -mindepth 1 -maxdepth 1 -type d | wc -l; printf "model0_cif="; find "'$PROJECT_ROOT'/outputs" -type f -name "*_model_0.cif" | wc -l; du -sh "'$PROJECT_ROOT'/outputs"; else echo MISSING; fi'
capture relevant_log_lines.txt bash -c 'find "'$PROJECT_ROOT'/log" -maxdepth 1 -type f -name "*.log" -print0 2>/dev/null | xargs -0 -r grep -HEn "MODE=|YAML_PATH=|OUTDIR=|CACHEDIR=|Boltz|version|diffusion_samples|msa.server|msa_server|CUDA|GPU|SLURM_JOB_ID|exit_code|error|warning" 2>/dev/null | head -n 15000 || true'
capture seed_scan.txt bash -c 'grep -RInE "random.seed|manual_seed|seed[=: ]" "'$PROJECT_ROOT'" --include="*.sh" --include="*.py" --include="*.yaml" --include="*.yml" 2>/dev/null | head -n 5000 || true'

find "${BUNDLE}" -type f ! -name MANIFEST.sha256 -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum >"${BUNDLE}/MANIFEST.sha256"
ARCHIVE="${BUNDLE}.tar.gz"
tar -C "${PROVENANCE_ROOT}" -czf "${ARCHIVE}" "$(basename "${BUNDLE}")"
sha256sum "${ARCHIVE}" >"${ARCHIVE}.sha256"
printf '%s\n' "${ARCHIVE}" >"${PROVENANCE_ROOT}/LATEST_boltz2.txt"

echo "Boltz-2 provenance collection complete."
echo "Archive: ${ARCHIVE}"
echo "Checksum: ${ARCHIVE}.sha256"
