# Wet-lab data area

The computational shortlist is complete and wet-lab validation is in progress.
No wet-lab measurements are included in this release. Do not replace this
statement with inferred or model-predicted activity.

Recommended raw table layout is provided in `raw/README.md`. A defensible assay
package should include:

- peptide identity, purity, lot and terminal modifications;
- hIAPP preparation/batch and disaggregation protocol;
- plate map, instrument settings and unmodified fluorescence reads;
- hIAPP-only, vehicle, positive and negative controls;
- L-TQNWVP and D-nfgail positive controls;
- multiple peptide concentrations or molar ratios;
- biological/independent repeats and technical replicates;
- predeclared exclusions and complete failed runs;
- kinetic parameters with uncertainty and an orthogonal endpoint if available.

Store immutable measurements in `wetlab/raw/`, tidy processed tables in
`wetlab/processed/`, and plots/statistical output in `wetlab/results/`.
