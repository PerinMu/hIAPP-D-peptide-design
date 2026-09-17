# Data provenance, licensing, and leakage controls

## Dataset inventory

| Data asset | Origin and date | Purpose | License/provenance status |
|---|---|---|---|
| PDB 9ULZ | RCSB Protein Data Bank; selected for the campaign on 2026-08-03 | hIAPP fibril template and binding-site definition | Accession and DOI recorded; cite [PDB 9ULZ](https://doi.org/10.2210/pdb9ULZ/pdb) and follow the RCSB PDB data-use policy |
| BoltzGen design table | Generated during the 2026-08-03 campaign from the committed input YAML | Initial candidate sequences | Project-generated model output; input and parameters committed |
| BoltzIF redesign table | Generated during the 2026-08-04 campaign | Backbone-conditioned sequence diversification | Project-generated model output; parameters committed |
| Boltz-2 score table | Generated 2026-08-04 to 2026-08-08, including retry batches | Complex-confidence and relative affinity signals | Project-generated model output; collection and retry scripts committed |
| Automatic MSA input | Requested through Boltz `--use_msa_server` during the prediction window | hIAPP target alignment context | Installed Boltz 2.2.1 default: `https://api.colabfold.com`; service version, request log, and returned alignment archive were not retained |
| Reference inhibitor set | Literature/source workbook, 76 usable entries with a grouped English source index | Descriptor-space context for P3 novelty only | Row-group source status and DOI verification flags are committed; original papers remain authoritative |
| Final 12 manifest and mmCIF files | Project screening and manual structure review | Experimental shortlist | Project-generated results; all values are computational unless explicitly labeled otherwise |

The repository does not contain a hidden or restricted dataset. Large
intermediate model-output trees are omitted from Git history and are described
in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Preprocessing and deduplication record

1. PDB 9ULZ chain D residues 19–37 were retained; residues 21–37 were marked as
   the intended binding region.
2. BoltzGen sequences were extracted from completed CIF files and deduplicated.
3. BoltzIF produced four redesigns per backbone at temperature 0.2 with
   cysteine excluded; sequences were deduplicated.
4. Design and inverse-folding tables were merged and deduplicated by sequence.
5. L sequences were reversed, written in the project lower-case D convention,
   and converted to explicit stereochemical SMILES.
6. Boltz-2 outputs were joined to candidates by sample identifier. Missing
   model-0 structures were detected and resubmitted.
7. Sequence properties, relative percentiles, hard gates, P1–P4 tiers, and the
   final review manifest were generated with committed scripts.

Exact row-count reconciliation is documented in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Train/validation/test splits

No team-developed model was trained or fine-tuned, so project-specific
train/validation/test splits are not applicable. BoltzGen, BoltzIF, and Boltz-2
are third-party pretrained models. Their upstream training corpora and split
policies are described by their authors.

## Leakage and overlap controls

- The reference-inhibitor set is not used as a labeled training, validation, or
  test set. It contributes only a four-descriptor novelty distance.
- No wet-lab activity measurement was used for threshold selection or final
  candidate ranking.
- All candidate percentile scores are computed within the design/IF pool.
- Two sequences carrying a combined source label were excluded consistently to
  reproduce the historical 9,806-row denominator; this is documented rather
  than silently relabeled.
- Possible overlap between external pretrained-model corpora and PDB 9ULZ or
  related hIAPP structures cannot be independently excluded. This is an
  external-model limitation, not evidence of project data leakage.
- The automatic MSA service was a third-party runtime dependency. Production
  commands used `--use_msa_server` without a URL override; the recovered Boltz
  2.2.1 source default is `https://api.colabfold.com`. The service-side version,
  request log, and returned alignment archive are unavailable.

## Integrity controls

`run.sh` records SHA256 checksums for its scored input, final-review manifest,
generated `results.csv`, generation code, screening tables and final structures.
The recovered model and container hashes are listed
in [`PRODUCTION_ENVIRONMENT.md`](PRODUCTION_ENVIRONMENT.md). New stochastic
inference campaigns should use new versioned output directories and capture
package versions, model revisions, checkpoint hashes, random seeds, GPU/driver
details, and scheduler logs before analysis.

## Missing provenance records

The following records are incomplete or were not retained. Upstream model
papers are linked in the Model Card; their training datasets have not been
independently inventoried here.

| Resource | Known information | Missing record or review |
|---|---|---|
| BoltzGen/BoltzIF upstream pretraining data | External pretrained models; model/package identifiers and author sources are in the Model Card | Exact datasets/releases, cutoff and acquisition dates, license applicability and overlap with the target/reference set have not been independently inventoried |
| Boltz-2 upstream training data | External model; recovered package and checkpoint hashes recorded | Exact structure/affinity dataset versions, cutoffs and applicable data permissions need an upstream source-based inventory |
| PDB 9ULZ | Accession, campaign selection date and local input structures retained | Campaign selection date is not a download timestamp; original retrieval log and applicable data-use terms should be retained if available |
| Reference inhibitor workbook | 76 usable entries and a row-group source mapping | Exact workbook version/acquisition date, unverified original papers and permissions for any redistributed source material need confirmation |
| Runtime MSA | Prediction window and recovered endpoint default | Database releases, service version, requests and returned alignments unavailable |
| Manual structure review | Final 12 identities, tiers and stage labels retained | A complete original 42-candidate review sheet with reasons, reviewer/date and rejected candidates is not deposited |

The reference set contains 76 usable **entries**, not necessarily 76 independent
papers. Source groups and their verification flags are given in
`data/designs/reference_inhibitor_sources.csv`. No reference-set activity AUC or
independent experimental validation is claimed.

Overlap with an external model's training data or an undisclosed evaluation
set has not been independently checked.
