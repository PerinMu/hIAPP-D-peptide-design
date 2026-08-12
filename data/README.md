# Data layout

- `designs/batch1_design.csv`: 1,956 unique BoltzGen design sequences.
- `designs/batch1_IF_02.csv`: 7,854 unique BoltzIF redesign sequences.
- `designs/merged_designs.csv`: 9,808 unique sequences after cross-source merge.
- `designs/merged_designs_reversed_smiles.csv`: D-sequence encoding and SMILES.
- `designs/reference_inhibitors_smiles.csv`: literature/reference inhibitor set used
  only for descriptor-space context.
- `designs/reference_inhibitor_sources.csv`: grouped English source-title mapping
  covering every reference entry; DOI verification status is explicit.
- `scored/merged_all_2_scored.csv`: structure, affinity and sequence-property
  table used by the reproducible notebook.

Treat files in `data/scored/` as immutable analysis inputs. Reruns should write
new outputs under `results/screening/` and document the source file checksum.

Reference-inhibitor sequences and modifications were transcribed from the study
workbook. A `title_from_source_workbook` status is traceable provenance, not a
claim that the citation or experimental result has been independently verified.
Verify the original paper before using any reference-set activity statement in a
manuscript or presentation.
