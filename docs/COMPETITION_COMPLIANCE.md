# Competition code-submission compliance

This checklist maps the repository to *Attachment 5: Code Submission
Requirements* for the First Global University Student Life Science Challenge.

This GitHub repository is the official public code-submission location for the
project. It is organized for evaluator review rather than as a continuously
supported clinical or production service. [`README.md`](../README.md) and the
English technical documents are authoritative; [`README_CN.md`](../README_CN.md)
is a concise navigation aid.

| Requirement | Repository evidence | Status |
|---|---|---|
| Commented algorithm source and complete commands | `scripts/`, `hpc/`, `README.md`, full workflow notebook | Complete |
| Dependencies and interpreter/OS/CUDA/hardware disclosure | `requirements.txt`, `environment.yml`, `environments/`, `README.md`, `MODEL_CARD.md` | Complete; recovered production evidence and remaining distinctions are explicit |
| Model weights or invocation route | Official download commands and checkpoint names in README/notebook; weights not redistributed | Complete for third-party pretrained models |
| Full design -> optimization -> prediction/screening example | `notebooks/00_full_generation_to_selection.ipynb` | Complete |
| One-command main entry point | `bash run.sh` | Complete |
| Training entry, split, logs, and trained weights | Not applicable: no model was trained or fine-tuned by the team | Explicitly documented |
| Executable Notebook | Full GPU workflow and CPU screening-reproduction notebooks | Complete |
| Data source, preprocessing, licensing, and leakage controls | `docs/DATA_PROVENANCE.md` and `docs/REPRODUCIBILITY.md` | Complete |
| Model structure, parameters, hardware, time, scope, I/O, limitations | `MODEL_CARD.md`, `docs/PRODUCTION_ENVIRONMENT.md`, `docs/METHODS.md`, notebook | Complete, with recovered-vs-historical evidence distinguished |
| Prediction results, ranking logic, and uncertainty | `results/`, `docs/METHODS.md`, `MODEL_CARD.md` | Complete |
| Third-party names, versions, parameters, source, and license | `MODEL_CARD.md`, `docs/PRODUCTION_ENVIRONMENT.md`, `docs/REFERENCES.md`, README | Complete; BoltzGen 0.2.0 is historically confirmed and Boltz 2.2.1 is explicitly labeled as recovered |
| Standard final candidate file | `results/submission/results.csv` and convenience mirror `results.xlsx` | Complete |
| Structure filenames and files | `structure_file` column and `results/final_candidates/structures/` | Complete |
| Relative paths/configuration and fixed deterministic processing | `run.sh`, `scripts/`, `hpc/`, notebooks | Complete |
| Expected runtime and hardware | README quick-start table and `docs/PRODUCTION_ENVIRONMENT.md` | Complete for CPU reproduction and recovered production allocations |
| Random seeds and stochastic-run disclosure | `MODEL_CARD.md` and `docs/PRODUCTION_ENVIRONMENT.md` | Historical production seed was not recorded; limitation is explicitly disclosed and no value is fabricated |
| Third-party API/commercial platform record | No commercial API was used; Boltz automatic MSA behavior is documented in the Model Card and production record | Complete within retained evidence; service-side version and returned alignments were not archived |
| Originality and IP/license statement | `LICENSE`, `MODEL_CARD.md`, references | Complete |
| Public evaluator navigation | `README.md`, `README_CN.md`, and this checklist | Complete |

## Evaluator command

```bash
conda env create -f environment.yml
conda activate hiapp-d-peptide-analysis
bash run.sh
```

Expected terminal summary:

```text
Analysis rows: 9806
Hard gate: 904
P1/P2/P3: {'P1': 12, 'P2': 12, 'P3': 8}
P4 hard pass: 30; exported top 10
Wrote 12 candidates to .../results/submission/results.csv
```

Neural generation and prediction require the separate GPU environments and
Slurm workflow described in the primary notebook; the evaluator command above
reproduces the deposited ranking and standardized final submission on CPU.

## Disclosed historical limits

- No project model was trained or fine-tuned, so training scripts, train/test
  splits, training logs, and team-generated model weights are not applicable.
- The original stochastic production seed and upstream package source Git
  revisions were not recorded. Recovered package versions, checkpoint hashes,
  container hash, dependency snapshots, hardware evidence, and scheduler
  records are published instead.
- The exact GPU model for the historical BoltzGen jobs and the MSA
  service-side version/returned alignments remain unavailable and are not
  inferred.
- Wet-lab validation is in progress and intentionally excluded until controlled
  replicate-level results are ready for deposition.
