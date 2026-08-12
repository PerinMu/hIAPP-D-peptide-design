# Scientific background and framework scope

## A general D-peptide design problem

Peptides can recognize extended, shallow, and conformational protein surfaces
that are often difficult to address with conventional small molecules. Their
therapeutic use is nevertheless constrained by proteolysis, short biological
half-life, self-association, and delivery. Replacing L-amino acids with their
D-enantiomers can markedly improve resistance to proteolytic degradation while
retaining the chemical diversity of a peptide interface. D-peptides are
therefore attractive starting points for inhibitors, diagnostics, and molecular
probes, especially when extracellular or aggregation-prone targets are involved.

Finding a useful D-peptide remains a multi-objective problem. High predicted
binding alone is insufficient: a candidate must also adopt a plausible bound
structure, remain soluble, avoid self-aggregation and obvious chemical
liabilities, cover an actionable target epitope, retain sequence diversity, and
be experimentally tractable. This repository treats those requirements as one
connected design funnel rather than isolated calculations.

## Established discovery routes

Mirror-image phage display is a foundational experimental route to D-peptide
ligands. An L-peptide is selected against a mirror-image D-target and then
synthesized in the D-configuration to bind the natural L-target. The method has
produced protease-resistant ligands, but access to a chemically synthesizable
mirror target can limit its practical target scope.

Structure-based computational approaches provide another powerful route.
Examples include mirror-transforming the target, identifying interaction
hotspots, grafting them onto predefined scaffolds, and ranking designs with
Rosetta or related empirical energy functions. Docking, global optimization,
binding free-energy calculations, and molecular dynamics have also helped
explain and optimize anti-amyloid D-peptides. These methods remain valuable,
particularly when a functional hotspot, scaffold family, or mechanistic
hypothesis is already known.

The framework in this repository is complementary to those approaches. It is
designed to reduce dependence on a single manually selected scaffold, motif, or
energy function while making large, target-conditioned candidate pools
practical to audit.

| Route | Candidate-generation principle | Typical strength | Common dependency |
|---|---|---|---|
| Mirror-image phage display | Experimental library selection against a mirror target | Direct enrichment from a large physical library | Chemically accessible D-target and experimental selection system |
| Hotspot/scaffold design | Transfer key interaction residues to opposite-chirality scaffolds and optimize with an energy function | Strong structural hypothesis and interpretable interface | Known hotspot or ligand, scaffold library, and energy-function search |
| Docking, free energy, and MD | Sample and score interactions for proposed candidates | Mechanistic detail and conformational analysis | Candidate starting set and substantial per-candidate computation |
| This framework | All-atom generative co-design followed by inverse folding, explicit D encoding, complex prediction, and multi-objective selection | Broad target-conditioned exploration with an auditable end-to-end funnel | Target structure/site definition, GPU inference, and experimental validation |

## What is technically new in this workflow

BoltzGen is an all-atom diffusion model that unifies biomolecular structure
prediction and binder design. For designed residues, it generates amino-acid
identity and atomic geometry together and can condition that process on a target
structure, binding-site labels, templates, covalent bonds, and other design
constraints. Its published scope includes proteins, peptides, nanobodies, and
multiple target modalities. The model authors experimentally evaluated the
platform across eight campaigns and 26 targets.

This repository turns that general model capability into a D-peptide-oriented
workflow:

1. define a target structure and intended binding region;
2. co-generate peptide sequence and all-atom structure in the target context;
3. use BoltzIF to diversify sequences conditioned on generated backbones;
4. reverse the sequence and encode every residue with explicit D
   stereochemistry in a linear-peptide SMILES representation;
5. independently predict the target–candidate complex with Boltz-2;
6. calculate transparent sequence-property descriptors;
7. apply hard gates, consensus ranking, diversity control, and structure review;
8. export a traceable experimental shortlist and assay-ready data schema.

The innovation is the integration: a recent all-atom generative design model is
connected to an explicit stereochemical bridge, independent complex assessment,
developability-aware selection, failure recovery, and reproducible experimental
handoff. The workflow explores many more candidate hypotheses than manual
hotspot placement alone and avoids treating any single learned or physics-based
score as definitive.

## Evidence boundary

This project uses a **reverse-D design convention**: BoltzGen first explores an
L-amino-acid sequence/structure representation, after which the sequence is
reversed and encoded with D stereochemistry. This preserves the retro-inverso
side-chain-order hypothesis but does not guarantee preservation of every
backbone interaction. Boltz-2 predictions provide a computational consistency
check, not proof of binding or inhibition.

Accordingly, “better” in this repository means broader automated exploration,
fewer manually fixed design assumptions, explicit multi-objective selection,
and stronger computational traceability. It does **not** mean universally higher
experimental activity than mirror-image display, Rosetta, docking, or molecular
dynamics. A head-to-head benchmark with matched targets, budgets, and wet-lab
readouts would be required for that conclusion.

## hIAPP as the demonstration case

Human islet amyloid polypeptide is co-secreted with insulin. Its misfolding and
assembly into oligomers and amyloid fibrils are associated with pancreatic
beta-cell stress and type 2 diabetes pathology. The fibril surface therefore
provides a biologically meaningful test case for peptide inhibitors that must
balance target engagement against their own aggregation propensity.

The campaign uses PDB 9ULZ as its structural template, retains chain D residues
19–37, and marks residues 21–37 as the intended binding region. The implemented
pipeline requested 2,000 initial designs, expanded the pool with BoltzIF,
evaluated 9,806 unique design rows, retained 904 candidates after hard filters,
and selected 12 reverse-D peptides after tiered ranking and structure review.

These results demonstrate computational scalability, filtering logic, and
end-to-end traceability. The public release currently labels the 12 peptides as
an experimental shortlist. Claims of hIAPP aggregation inhibition will be made
only when raw fluorescence traces, peptide concentrations, controls, independent
repeats, analysis code, and an orthogonal endpoint are deposited in `wetlab/`.

## Generalization beyond hIAPP

The framework is not tied to amyloid biology. A new campaign can replace the
target structure and binding-site definition, modify peptide length and residue
constraints, select appropriate prediction templates, recalibrate screening
thresholds, and define target-specific functional and counter-screening assays.
The reusable components—candidate extraction, reverse-D conversion, YAML
generation, bounded Slurm dispatch, failed-job recovery, score collection,
descriptor calculation, ranking, and review-sheet generation—remain the same.

This separation between reusable infrastructure and target-specific scientific
judgment is central to the project: the code is portable, while biological
claims remain specific to the evidence collected for each target.

## Key literature

- Funke SA, Willbold D. Mirror image phage display—a method to generate
  D-peptide ligands for diagnostic or therapeutic applications. *Molecular
  BioSystems*. 2009;5:783–786. [doi:10.1039/b904138a](https://doi.org/10.1039/b904138a)
- Juraszek J, Kadam RU, Branduardi D, et al. De novo design of D-peptide
  ligands: application to influenza virus hemagglutinin. *PNAS*.
  2025;122:e2426554122. [doi:10.1073/pnas.2426554122](https://doi.org/10.1073/pnas.2426554122)
- Olubiyi OO, Frenzel D, Bartnik D, et al. Amyloid aggregation inhibitory
  mechanism of arginine-rich D-peptides. *Current Medicinal Chemistry*.
  2014;21:1448–1457. [doi:10.2174/0929867321666131129122247](https://doi.org/10.2174/0929867321666131129122247)
- Stark H, Faltings F, Choi M, et al. BoltzGen: Toward Universal Binder Design.
  *bioRxiv*. 2025. [doi:10.1101/2025.11.20.689494](https://doi.org/10.1101/2025.11.20.689494)

The complete target, model, physicochemical, and inhibitor bibliography is in
[`REFERENCES.md`](REFERENCES.md).
