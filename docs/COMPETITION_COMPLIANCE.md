# Competition code-submission compliance

This checklist maps the repository to *Attachment 5: Code Submission
Requirements* for the First Global University Student Life Science Challenge.

| Requirement | Repository evidence | Status |
|---|---|---|
| Commented algorithm source and complete commands | `scripts/`, `hpc/`, `README.md`, full workflow notebook | Complete |
| Dependencies and interpreter/OS/CUDA/hardware disclosure | `requirements.txt`, `environment.yml`, `README.md`, `MODEL_CARD.md` | Complete; original model package revisions are disclosed as unavailable |
| Model weights or invocation route | Official download commands and checkpoint names in README/notebook; weights not redistributed | Complete for third-party pretrained models |
| Full design -> optimization -> prediction/screening example | `notebooks/00_full_generation_to_selection.ipynb` | Complete |
| One-command main entry point | `bash run.sh` | Complete |
| Training entry, split, logs, and trained weights | Not applicable: no model was trained or fine-tuned by the team | Explicitly documented |
| Executable Notebook | Full GPU workflow and CPU screening-reproduction notebooks | Complete |
| Data source, preprocessing, licensing, and leakage controls | `docs/DATA_PROVENANCE.md` and `docs/REPRODUCIBILITY.md` | Complete |
| Model structure, parameters, hardware, time, scope, I/O, limitations | `MODEL_CARD.md`, `docs/METHODS.md`, notebook | Complete, with historical provenance caveat |
| Prediction results, ranking logic, and uncertainty | `results/`, `docs/METHODS.md`, `MODEL_CARD.md` | Complete |
| Third-party names, versions, parameters, source, and license | `MODEL_CARD.md`, `docs/REFERENCES.md`, README | Complete, except exact production package revisions were not archived and are not fabricated |
| Standard final candidate file | `results/submission/results.csv` and convenience mirror `results.xlsx` | Complete |
| Structure filenames and files | `structure_file` column and `results/final_candidates/structures/` | Complete |
| Relative paths/configuration and fixed deterministic processing | `run.sh`, `scripts/`, `hpc/`, notebooks | Complete |
| Originality and IP/license statement | `LICENSE`, `MODEL_CARD.md`, references | Complete |

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
