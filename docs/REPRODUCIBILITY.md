# Reproducibility and data lineage

## Count reconciliation

| Stage | Rows / designs | Unique / usable | Evidence in repository |
|---|---:|---:|---|
| BoltzGen requested | 2,000 | - | run configuration and lab record |
| BoltzGen completed CIF/NPZ pairs | 1,990 | - | retained source tree; extraction validation |
| BoltzGen sequence table | 1,990 | 1,956 | `data/designs/batch1_design.csv` |
| BoltzIF raw output | 7,960 | 7,854 | lab record; unique table committed |
| Merged design + IF | 9,810 | 9,808 | `data/designs/merged_designs.csv` |
| Analysis design/IF rows | 9,806 | 9,806 | `data/scored/merged_all_2_scored.csv` |
| Hard-gated candidates | - | 904 | recomputed in notebook |
| P1/P2/P3/P4 review | - | 12/12/8/10 | recomputed in notebook |
| Final synthesis set | - | 12 | `results/final_candidates/final_12.csv` |

The merged table labels two cross-source duplicate sequences as
`design; IF_02`. The historical analysis selected exact source labels `design`
and `IF_02`, so these two shared-source rows were not included in the 9,806-row
analysis pool. This provenance-label decision, rather than a model-score gate,
explains the difference from 9,808 unique merged sequences. The notebook keeps
the recorded 9,806 denominator so that every published count is reproducible.

## Included artifacts

- 9ULZ structural template and BoltzGen YAML.
- Unique generation and inverse-folding sequence tables.
- Merged D-peptide sequence/SMILES table.
- Full 9,884-row scored CSV (9,806 design/IF plus reference rows).
- Final 12 predicted complex CIF files.
- Portable scripts for collection, merge, recovery and screening.
- Full GPU-server Notebook from official installation through structural review.

## Large artifacts intentionally omitted

- Approximately 2,000 BoltzGen backbone CIF/NPZ pairs.
- Approximately 7,960 inverse-folding CIF/NPZ pairs.
- Complete raw Boltz result tree and downloaded result archive.
- Generated YAML archives containing thousands of near-identical files.

These are reproducible from the committed inputs and scripts but are unsuitable
for ordinary Git history. For strict archival submission, attach them to a
versioned release or deposit them in a data repository and record checksums and
the permanent URL here.

## Software provenance to record before final submission

The original cluster notes did not capture immutable Git commit IDs for BoltzGen
or Boltz. Before the competition deadline, record the exact environment used:

```bash
boltzgen --version
python -m pip freeze > environment-boltzgen.txt
python -m pip show boltz > environment-boltz.txt
git -C /path/to/boltzgen rev-parse HEAD
git -C /path/to/boltz rev-parse HEAD
sha256sum /path/to/checkpoint.ckpt
```

Do not publish proxy endpoints, usernames, private mount paths or access tokens.

## Determinism

Percentile scoring and greedy sequence selection are deterministic for a fixed
input table and stable sort order. Neural generation and structure prediction
may vary with software/checkpoint versions, random seeds and hardware. Preserve
the original result table as immutable evidence and write new reruns to a new
versioned directory.

## Historical HPC script recovery

The cluster scripts `submit_keep8.sh`, `run_lig_array_large.sh`, its identical
`fixed` copy, `run_lig_one_large.sh` and the historical retry extractor were
recovered. Because they contain private paths and a proxy endpoint, the public
repository contains path-neutral counterparts plus a SHA256 provenance table in
`legacy/original_hpc/README.md`.
