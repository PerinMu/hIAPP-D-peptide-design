# Competition submission checklist

## 1. Target value and biological understanding (15)

- [x] Identify hIAPP, its amyloidogenic region and the type 2 diabetes context.
- [x] State the D-peptide design objective and the multi-objective difficulty.
- [x] Separate model hypotheses from established disease biology.
- [x] Add a structured target, model, physicochemical, and inhibitor bibliography.
- [ ] Add one target/mechanism slide to the narrated presentation.

## 2. AI design and computational optimization (25)

- [x] Include the template, model inputs, candidate-generation logic and counts.
- [x] Provide complete score definitions, thresholds and source-neutral ranking.
- [x] Provide a step-by-step executable notebook and command-line scripts.
- [x] Preserve final predicted complexes and a machine-readable shortlist.
- [ ] Record exact software commits, checkpoint hashes, seeds and GPU details.
- [ ] Consider an optional orthogonal validation (for example MD/interface
      relaxation) and label it clearly if added later.

## 3. Wet-lab validation quality (25)

- [ ] Add synthesis QC (identity, purity and batch metadata).
- [ ] Run hIAPP-only, vehicle, positive and negative controls.
- [ ] Include L-TQNWVP and D-nfgail positive controls as planned.
- [ ] Measure concentration-response across predeclared peptide:hIAPP ratios.
- [ ] Use independent repeats and technical replicates; retain every raw read.
- [ ] Fit aggregation kinetics with uncertainty and define exclusions in advance.
- [ ] Add an orthogonal endpoint where feasible (TEM/AFM, sedimentation or
      another assay) to reduce ThT-specific interpretation risk.

## 4. Activity and mechanism analysis (20)

- [ ] Compare all 12 designs with both controls on activity and assay variance.
- [ ] Relate activity to interface contacts, length, affinity consensus and
      developability without claiming causation from correlation alone.
- [ ] Test stability/selectivity when feasible and document negative results.
- [ ] Propose a mechanism supported jointly by structural and experimental data.

## 5. Materials and presentation (15)

- [x] Code, data dictionary, provenance notes and final candidate files included.
- [x] Computational and wet-lab evidence are stored in separate directories.
- [ ] Replace the collective CFF author with final team names and contact details.
- [ ] Upload large raw artifacts to a release/data archive and record checksums.
- [ ] Run the repository verification commands before tagging the final version.
- [ ] Export a clear narrated presentation with the same counts and terminology.
