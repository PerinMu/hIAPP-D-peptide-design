# Recovered production environment

## Evidence boundary

The original cloud environments remained available after the August 2026 hIAPP
campaign. On 2026-08-15, the read-only collectors in `hpc/` captured package
metadata, checkpoint/container hashes, selected historical logs, scheduler
records, GPU/CUDA snapshots, installed source manifests, and small configuration
files. The two downloaded archives and all files listed by their internal
manifests passed SHA256 verification.

The raw archives are not published because they retain account paths,
compute-node names, and unrelated scheduler records. Their integrity hashes are:

| Private evidence bundle | SHA256 |
|---|---|
| BoltzGen/BoltzIF recovery bundle | `86e56f4d1ab5e28323823d163c598e4c0ec37f617ad69dece046698757a962c2` |
| Boltz-2 recovery bundle | `d36f2582eacf3797a0cb04c6cc987322e5c075e778d5c570ea89ed13608b4e53` |

This document publishes only credential-free facts relevant to reproduction.

## Software stack

| Stage | Recovered software | Python/runtime | Evidence strength |
|---|---|---|---|
| BoltzGen design and BoltzIF | `boltzgen` 0.2.0; PyTorch 2.9.1+cu128; NumPy 2.0.2; pandas 2.3.3; RDKit 2025.9.3; PyTorch Lightning 2.6.0 | Python 3.12.12 in Singularity CE 3.10.0 | `boltzgen 0.2.0` appears in the historical inverse-folding log and recovered environment |
| Boltz-2 prediction | `boltz` 2.2.1; PyTorch 2.10.0+cu128; NumPy 1.26.4; pandas 2.3.3; RDKit 2025.9.6; PyTorch Lightning 2.5.0.post0 | Python 3.10.20 in Conda | Recovered still-installed environment; historical prediction logs did not print the package version |

Complete sanitized package snapshots are committed under `environments/`.
Upstream source Git revisions were not recoverable because the model packages
were installed without their source repositories.

## Model and container integrity

| Artifact | Size (bytes) | SHA256 |
|---|---:|---|
| `boltzgen1_diverse.ckpt` | 1,930,847,192 | `360af8bd6e59527ff6ec25dd81253967f3bd3567d200053b10680634751f8e3c` |
| `boltzgen1_ifold.ckpt` | 12,582,656 | `dd4cf108c94471bdc3a326b7b180fa3854dc019110fae780208c30b50bd56578` |
| `boltz2_conf.ckpt` | 2,286,561,469 | `090e82ac8c92f5e943fa1b39e7410a44027bea7243c0bbb3caa67a77fc1428e1` |
| `boltz2_aff.ckpt` | 2,062,139,170 | `dcc5cd3722b1c9eaa34267e4ae32f55cbbf1963f4c19319381ccfa30fdd2ca9e` |
| BoltzGen CUDA 12.4.1/cuDNN development SIF | 4,754,161,664 | `723659cab39561f553844c4074c8ec93e176908bc408b4e9d3b2dbe74c48124f` |

The Singularity image identifies Ubuntu 22.04, CUDA 12.4.1, and cuDNN 9.1.0.70.
The active BoltzGen Python environment contains PyTorch built for CUDA 12.8.

## Hardware and scheduler record

| Stage | Allocation and observed runtime evidence |
|---|---|
| BoltzGen design | Final recorded four-GPU job completed in 22 min 34 s with 24 CPU cores and 240 GB RAM requested |
| BoltzIF | Final temperature-0.2 four-GPU job completed in 9 min 02 s with 24 CPU cores and 240 GB RAM requested |
| Boltz-2 | One RTX 4090, six CPU cores, and 60 GB RAM per prediction allocation; up to eight jobs were dispatched concurrently |

Historical prediction logs explicitly identify RTX 4090. The 2026-08-15
Boltz-2 recovery node reported driver 580.82.07 and CUDA toolkit 12.8.61. The
BoltzGen recovery node exposed an RTX 3090 with driver 535.104.05 on the same
generic `gpu` partition; historical four-GPU BoltzGen logs do not print their
GPU model, so RTX 3090 is not asserted as the exact production hardware.

Scheduler records from 2026-08-04 through 2026-08-08 contain 10,322 allocations
under the campaign job name `boltz_arr`: 9,788 completed and 534 failed. Their
aggregate allocated runtime is 459.26 GPU hours. These are scheduler-level
attempts, including retries; they are not equivalent to unique successful
candidate outputs. Output reconciliation remains documented separately.

## MSA service and stochasticity

Production commands set `--use_msa_server` and did not set
`--msa_server_url`. In the recovered Boltz 2.2.1 source, the default is
`https://api.colabfold.com`, using the MMseqs2/ColabFold client path. The
service-side version, credential-free request log, and returned alignments were
not archived.

No production BoltzGen/BoltzIF/Boltz-2 script in the recovered configuration
sets or records a stochastic seed. An unrelated RFdiffusion script and a later
multi-seed utility were detected but are not evidence of the hIAPP production
seed. The stochastic seed therefore remains unavailable.

## Reproduction interpretation

Checkpoint hashes and the BoltzGen historical version are strong production
evidence. The Boltz-2 package version, current drivers, and current node details
are post-campaign recovery snapshots collected seven days after the final
prediction jobs. They make the surviving environment auditable but must not be
misrepresented as immutable per-job telemetry.
