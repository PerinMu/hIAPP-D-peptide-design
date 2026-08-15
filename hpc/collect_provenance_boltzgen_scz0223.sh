#!/usr/bin/env bash
# Run once on the scz0223 login node with:
#   bash collect_provenance_boltzgen_scz0223.sh
# The script self-submits a one-GPU Slurm job and never reruns BoltzGen.
#SBATCH --job-name=prov_boltzgen
#SBATCH --gpus=1
#SBATCH --time=02:00:00
#SBATCH --output=provenance_boltzgen_%j.log
#SBATCH --error=provenance_boltzgen_%j.log

set -uo pipefail
umask 077

PROJECT_ROOT="${PROJECT_ROOT:-/HOME/scz0223/run/data/XMY}"
SOFTWARE_ROOT="${SOFTWARE_ROOT:-/data/run01/scz0223/soft/boltzgen}"
CONDA_SH="${CONDA_SH:-/data/apps/miniforge3/24.1.2/etc/profile.d/conda.sh}"
CONDA_ENV="${CONDA_ENV:-/data/run01/scz0223/.conda/envs/bg_new}"
SIF="${SIF:-${SOFTWARE_ROOT}/nvidia-cuda-12.4.1-cudnn-devel-ubuntu22.04.sif}"
MOLDIR="${MOLDIR:-${SOFTWARE_ROOT}/mols}"
DESIGN_CHECKPOINT="${DESIGN_CHECKPOINT:-${SOFTWARE_ROOT}/boltzgen1_diverse.ckpt}"
HF_HOME_ROOT="${HF_HOME_ROOT:-/HOME/scz0223/.cache/huggingface}"
PROVENANCE_ROOT="${PROVENANCE_ROOT:-${PROJECT_ROOT}/provenance}"

SELF_PATH="$(readlink -f "$0" 2>/dev/null || printf '%s' "$0")"

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    mkdir -p "${PROVENANCE_ROOT}"
    cd "${PROJECT_ROOT}" || exit 1
    JOB_ID="$(sbatch --parsable --gpus=1 "${SELF_PATH}" --worker)" || exit 1
    echo "Submitted BoltzGen provenance job: ${JOB_ID}"
    echo "Monitor with: parajobs"
    echo "After completion, run: ls -lh ${PROVENANCE_ROOT}/LATEST_boltzgen.txt ${PROVENANCE_ROOT}/*.tar.gz*"
    exit 0
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BUNDLE="${PROVENANCE_ROOT}/boltzgen_scz0223_${STAMP}_job${SLURM_JOB_ID}"
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

step() {
    printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"
}

if [[ -r /etc/profile.d/modules.sh ]]; then
    # shellcheck disable=SC1091
    source /etc/profile.d/modules.sh
fi
module load singularity/3.10.0 >/dev/null 2>&1 || module load singularity >/dev/null 2>&1 || true

container_exec() {
    singularity exec --nv \
        -B /data/apps:/data/apps \
        -B /data/run01/scz0223:/data/run01/scz0223 \
        -B /HOME/scz0223:/HOME/scz0223 \
        "${SIF}" \
        bash -c 'source "$1"; conda activate "$2"; shift 2; exec "$@"' \
        bash "${CONDA_SH}" "${CONDA_ENV}" "$@"
}

cat >"${BUNDLE}/README.txt" <<EOF
Purpose: historical provenance recovery for the August 2026 hIAPP BoltzGen/BoltzIF campaign.
Collection time (UTC): ${STAMP}
Slurm job: ${SLURM_JOB_ID}
This bundle contains metadata, software manifests, hashes, and small configuration snapshots.
It does not contain model weights, generated structures, shell history, tokens, or full environment variables.
Review the bundle before external publication because hostnames and account paths are preserved for provenance.
EOF

step "Collecting system, Slurm, GPU, and container metadata"
capture system_identity.txt bash -c 'date -u; date; hostname; id; pwd; uname -a; cat /etc/os-release 2>/dev/null; lscpu; free -h'
capture slurm_environment.txt bash -c 'env | LC_ALL=C sort | grep -E "^(SLURM_|CUDA_VISIBLE_DEVICES=)" || true'
capture slurm_job.txt scontrol show job "${SLURM_JOB_ID}"
capture slurm_node.txt bash -c 'scontrol show node "${SLURMD_NODENAME:-$(hostname)}" 2>/dev/null || true'
capture slurm_config.txt bash -c 'scontrol show config 2>/dev/null | grep -E "^(ClusterName|SlurmctldHost|SlurmctldParameters|SelectType|GresTypes|SchedulerType|SlurmctldVersion)" || true'
capture historical_jobs_2026-08-03_to_08-11.txt bash -c 'sacct -u "$USER" -S 2026-08-03 -E 2026-08-11 -X --format=JobIDRaw,JobName%35,Partition,State,Elapsed,AllocTRES%45,Start,End,NodeList%30 2>/dev/null || true'
capture historical_node_records.txt bash -c 'sacct -u "$USER" -S 2026-08-03 -E 2026-08-11 -X -n -o NodeList 2>/dev/null | sed "s/^[[:space:]]*//;s/[[:space:]]*$//" | grep -Ev "^$|None|Unknown" | sort -u | while read -r spec; do scontrol show hostnames "$spec" 2>/dev/null || true; done | sort -u | while read -r node; do echo "HISTORICAL_NODE=$node"; scontrol show node "$node" 2>/dev/null || true; echo; done'
capture nvidia_smi.txt nvidia-smi
capture nvidia_query.csv nvidia-smi --query-gpu=index,name,uuid,driver_version,vbios_version,pci.bus_id,memory.total,compute_cap --format=csv
capture cuda_compiler.txt bash -c 'nvcc --version 2>/dev/null || true; ldconfig -p 2>/dev/null | grep -E "libcuda|libcudnn" | head -n 100 || true'
capture module_state.txt bash -lc 'source /etc/profile.d/modules.sh 2>/dev/null || true; module list 2>&1 || true; module show singularity/3.10.0 2>&1 || true'
capture singularity_version.txt singularity --version
capture singularity_inspect.txt singularity inspect "${SIF}"

step "Collecting the active BoltzGen/Conda environment"
capture boltzgen_version.txt container_exec boltzgen --version
capture boltzgen_help.txt container_exec boltzgen --help
capture python_runtime.txt container_exec python -c 'import importlib.metadata as m, platform, sys; print("python", sys.version); print("platform", platform.platform()); names=["boltzgen","torch","numpy","pandas","rdkit","lightning","pytorch-lightning"]; [(print(n, m.version(n)) if n in {d.metadata.get("Name","").lower() for d in m.distributions()} else None) for n in names]'
capture torch_runtime.txt container_exec python -c 'import torch; print("torch",torch.__version__); print("torch_cuda",torch.version.cuda); print("cudnn",torch.backends.cudnn.version()); print("cuda_available",torch.cuda.is_available()); print("device_count",torch.cuda.device_count()); [print(i,torch.cuda.get_device_name(i),torch.cuda.get_device_properties(i)) for i in range(torch.cuda.device_count())]'
capture pip_show.txt container_exec python -m pip show boltzgen torch numpy pandas rdkit lightning pytorch-lightning
capture pip_freeze.txt container_exec python -m pip freeze
capture conda_list.txt container_exec conda list
capture conda_explicit.txt container_exec conda list --explicit
capture conda_environment.yml container_exec conda env export --no-builds
capture boltzgen_module_path.txt container_exec python -c 'import boltzgen, inspect; print(boltzgen.__file__); print(inspect.getfile(boltzgen))'

step "Collecting source revisions and targeted model hashes"
capture git_repositories.txt bash -c '
for repo in "'$SOFTWARE_ROOT'" "'$SOFTWARE_ROOT'/test" "'$SOFTWARE_ROOT'/test/workbench"; do
  [[ -d "$repo" ]] || continue; echo "REPOSITORY_CANDIDATE=$repo"; git -C "$repo" rev-parse HEAD 2>/dev/null || true; git -C "$repo" describe --always --dirty --tags 2>/dev/null || true; git -C "$repo" remote -v 2>/dev/null || true; git -C "$repo" status --short 2>/dev/null || true; echo; done'

{
    hash_one "${DESIGN_CHECKPOINT}"
    hash_one "${SIF}"
    root="${HF_HOME_ROOT}/hub/models--boltzgen--boltzgen-1/snapshots"
    if [[ -d "${root}" ]]; then
        find -L "${root}" -maxdepth 6 -type f \( -iname '*ifold*.ckpt' -o -iname '*diverse*.ckpt' -o -iname '*.safetensors' \) -print 2>/dev/null | sort -u | while read -r file; do
            hash_one "${file}"
        done
    fi
    find -L "${SOFTWARE_ROOT}" -maxdepth 2 -type f \( -iname '*ifold*.ckpt' -o -iname '*diverse*.ckpt' -o -iname '*.safetensors' \) -print 2>/dev/null | sort -u | while read -r file; do
        hash_one "${file}"
    done
} >"${BUNDLE}/model_and_container_sha256.txt" 2>&1

capture moldir_inventory.txt bash -c 'echo "MOLDIR='$MOLDIR'"; if [[ -d "'$MOLDIR'" ]]; then ls -ld "'$MOLDIR'"; find -L "'$MOLDIR'" -maxdepth 2 -type f -printf "%s\t%TY-%Tm-%TdT%TH:%TM:%TS\t%p\n" 2>/dev/null | head -n 500; else echo MISSING; fi'

step "Collecting small configuration snapshots and bounded project evidence"
for path in \
    "${PROJECT_ROOT}/inputs/9ULZ.yaml" \
    "${PROJECT_ROOT}/inputs/9ULZ.cif" \
    "${PROJECT_ROOT}/sing.sh" \
    "${PROJECT_ROOT}/run_sing.sh" \
    "${PROJECT_ROOT}/boltzgen_inverse_folding_only.sh" \
    "${PROJECT_ROOT}/boltzgen_inverse_folding_only_v2.sh"; do
    copy_snapshot "${path}"
done

capture project_file_manifest.txt bash -c 'find "'$PROJECT_ROOT'" -maxdepth 3 \( -path "'$PROJECT_ROOT'/outputs" -o -path "'$PROJECT_ROOT'/provenance" -o -path "'$PROJECT_ROOT'/logs" \) -prune -o -type f -printf "%TY-%Tm-%TdT%TH:%TM:%TS\t%s\t%p\n" 2>/dev/null | sort | head -n 20000'
capture output_counts.txt bash -c '
for d in "'$PROJECT_ROOT'/outputs/hIAPP_batch1" "'$PROJECT_ROOT'/outputs/hIAPP_batch1_ifold"; do
  echo "DIRECTORY=$d"; if [[ -d "$d" ]]; then printf "immediate_files="; find "$d" -maxdepth 1 -type f | wc -l; printf "immediate_directories="; find "$d" -mindepth 1 -maxdepth 1 -type d | wc -l; else echo MISSING; fi; echo; done'
capture relevant_log_lines.txt bash -c 'find "'$PROJECT_ROOT'/logs" -maxdepth 1 -type f -name "*.log" -printf "%T@ %p\n" 2>/dev/null | sort -nr | head -n 200 | cut -d" " -f2- | tr "\n" "\0" | xargs -0 -r grep -HEn "BoltzGen version|CHECKPOINT|MOLDIR|NUM_DESIGNS|DIFFUSION|TEMPERATURE|CUDA|GPU|SLURM_JOB_ID|error|warning" 2>/dev/null | head -n 10000 || true'
capture seed_scan.txt bash -c 'find "'$PROJECT_ROOT'" "'$SOFTWARE_ROOT'/test" -maxdepth 2 -type f \( -name "*.sh" -o -name "*.py" -o -name "*.yaml" -o -name "*.yml" \) -print0 2>/dev/null | xargs -0 -r grep -HnE "random.seed|manual_seed|seed[=: ]" 2>/dev/null | head -n 5000 || true'

step "Building the provenance archive"
find "${BUNDLE}" -type f ! -name MANIFEST.sha256 -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum >"${BUNDLE}/MANIFEST.sha256"
ARCHIVE="${BUNDLE}.tar.gz"
tar -C "${PROVENANCE_ROOT}" -czf "${ARCHIVE}" "$(basename "${BUNDLE}")"
sha256sum "${ARCHIVE}" >"${ARCHIVE}.sha256"
printf '%s\n' "${ARCHIVE}" >"${PROVENANCE_ROOT}/LATEST_boltzgen.txt"

echo "BoltzGen provenance collection complete."
echo "Archive: ${ARCHIVE}"
echo "Checksum: ${ARCHIVE}.sha256"
