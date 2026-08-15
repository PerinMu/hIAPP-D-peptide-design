# Data provenance, licensing, and leakage controls

## Dataset inventory

| Data asset | Origin and date | Purpose | License/provenance status |
|---|---|---|---|
| PDB 9ULZ | RCSB Protein Data Bank; selected for the campaign on 2026-08-03 | hIAPP fibril template and binding-site definition | Accession and DOI recorded; cite [PDB 9ULZ](https://doi.org/10.2210/pdb9ULZ/pdb) and follow the RCSB PDB data-use policy |
| BoltzGen design table | Generated during the 2026-08-03 campaign from the committed input YAML | Initial candidate sequences | Project-generated model output; input and parameters committed |
| BoltzIF redesign table | Generated during the 2026-08-04 campaign | Backbone-conditioned sequence diversification | Project-generated model output; parameters committed |
| Boltz-2 score table | Generated 2026-08-04 to 2026-08-08, including retry batches | Complex-confidence and relative affinity signals | Project-generated model output; collection and retry scripts committed |
| Automatic MSA input | Requested through Boltz `--use_msa_server` during the prediction window | hIAPP target alignment context | Upstream Boltz documentation cites ColabFold; exact endpoint/version and returned alignment archive were not retained |
| Reference inhibitor set | Literature/source workbook, mapped to 76 English source records | Descriptor-space context for P3 novelty only | Row-group source status and DOI verification flags are committed; original papers remain authoritative |
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
- The automatic MSA service was a third-party runtime dependency. Its request
  details are partially recoverable from the command flag and YAML input, but
  the server version and response archive are unavailable.

## Integrity controls

`run.sh` records SHA256 checksums for its scored input, final-review manifest,
and generated `results.csv`. New stochastic inference campaigns should use new
versioned output directories and capture package versions, model revisions,
checkpoint hashes, random seeds, GPU/driver details, and scheduler logs before
analysis.
