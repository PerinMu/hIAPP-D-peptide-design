# Physicochemical descriptor implementation

## Purpose and interpretation

`scripts/score_sequence_properties.py` calculates deterministic sequence-only
features for relative prioritization inside this candidate pool. It does not
implement an experimentally trained solubility, aggregation, permeability,
stability, or drug-likeness model. The 0-100 scales, weights, class labels, and
screening cutoffs are study-specific heuristics.

The calculations assume an unmodified, linear peptide with free termini.
Sequence-only approximations for modified literature peptides are explicitly
flagged. D/L stereochemistry does not change residue composition, molecular
mass, or the idealized Henderson-Hasselbalch charge calculation, but it can
change conformation, proteolysis, self-association, and experimental behavior;
those effects are outside this descriptor layer.

## Direct descriptors

| Output | Implementation | Literature basis | Important limitation |
|---|---|---|---|
| `sequence_length_aa` | Number of canonical residues | Direct count | Modifications are excluded. |
| `molecular_weight_da_est` | Sum of average residue masses plus one water molecule | ExPASy/ProtParam conventions [1] | Uses average, not monoisotopic, masses and free termini. |
| `net_charge_ph7_est` | Sum of fractional ionization for termini, D/E/C/Y and H/K/R at pH 7 | Henderson-Hasselbalch formulation and fixed pKa values [1,2] | Ignores local environment, salt, terminal modifications, and coupled ionization. |
| `isoelectric_point_est` | Bisection over pH 0-14 until estimated net charge is zero | Standard sequence-based pI calculation [1,2] | Uses the same idealized fixed-pKa model. |
| `gravy_kd` | Arithmetic mean of Kyte-Doolittle residue hydropathy values | Kyte and Doolittle [3] | A one-dimensional scale cannot represent conformation or amphiphilic patterning. |
| Composition fractions | Fraction of polar, hydrophobic, or aromatic residues | Transparent residue sets in the script | Residue-set choices are study definitions. |
| `max_hydrophobic_run` | Longest consecutive run in `AVILMFWY` | Hydrophobic patterning is relevant to peptide self-association [4,5] | This is not AGGRESCAN and has no calibrated probability interpretation. |

## Composite heuristic scores

Let `clip(x)` truncate a value to `[0,1]`; `n` is sequence length; `MW` is the
estimated molecular weight; `q` is estimated net charge at pH 7;
`rho = abs(q)/n`; `H` is GRAVY; `f_pol`, `f_hyd`, and `f_aro` are composition
fractions; and `r_hyd` is the longest hydrophobic run.

### Aggregation-risk tendency

```text
base = 0.30 clip((H + 0.5)/3.0)
     + 0.25 clip((f_hyd - 0.30)/0.40)
     + 0.20 clip((r_hyd - 2)/4)
     + 0.15 clip((f_aro - 0.05)/0.25)
     + 0.10 clip((n - 8)/30)

aggregation_risk = 100 clip(base * [1 - 0.30 clip(rho/0.25)])
```

Hydrophobicity, hydrophobic/aromatic patterning, chain length, and charge are
well-motivated aggregation-related features [4-6]. The exact formula and the
`35/65` class boundaries are original project heuristics, not an implementation
or validation of AGGRESCAN.

### Solubility tendency

```text
solubility = 100 clip(
    0.35 clip((1.5 - H)/3.5)
  + 0.20 clip((f_pol - 0.25)/0.45)
  + 0.15 clip(rho/0.22)
  + 0.15 [1 - clip((r_hyd - 2)/4)]
  + 0.15 [1 - clip((MW - 800)/2500)]
)
```

The component choices reflect the established dependence of peptide
developability and solubility on hydrophobicity, charge, size, pH, and
self-association [6,7]. The weights and the hard-screen threshold of 40 were
chosen for this within-pool prioritization and are not a solubility measurement.

### Passive-permeability tendency

```text
permeability = 100 clip(
    0.30 [1 - clip((MW - 500)/1800)]
  + 0.20 [1 - clip(abs(q)/3)]
  + 0.15 [1 - clip((f_pol - 0.25)/0.50)]
  + 0.15 [1 - clip(abs(H - 0.5)/2.5)]
  + 0.20 [1 - clip((n - 4)/12)]
)
```

Peptide permeability depends on desolvation, exposed polarity, hydrogen
bonding, charge, lipophilicity, size, and conformation [8-10]. This simplified
linear-sequence score does not calculate polar surface area, hydrogen-bond
exposure, conformational shielding, active uptake, or experimental PAMPA/Caco-2
permeability. It was retained as a descriptive field and was not used in the
hard gate or the five-feature developability percentile.

### Sequence liabilities and stability tendency

The liability count adds:

- M and W residues as oxidation flags;
- `N[GSTAQ]` motifs as deamidation flags;
- `D[GSTP]` motifs as aspartate isomerization/hydrolysis flags;
- N-terminal Q/E as a cyclization flag;
- an odd number of cysteines as an unpaired-cysteine flag.

```text
stability = clip(
    100 - 8 oxidation - 8 deamidation - 6 aspartate
        - 8 N-terminal-cyclization - 10 unpaired-cysteine
        - min(20, max(0, n - 12) * 0.6),
    0, 100
)
```

Primary-sequence review for oxidation, deamidation, isomerization, and other
chemical liabilities is standard early peptide developability practice [11].
The penalties are project-specific; they are not degradation rates.

### Peptide drug-likeness tendency

```text
drug_likeness = clip(
    0.35 solubility
  + 0.25 (100 - aggregation_risk)
  + 0.20 permeability
  + 0.20 stability,
    0, 100
)
```

This is a balanced ranking convenience, not a validated drug-likeness model.
It must not be used to claim bioavailability, safety, efficacy, or formulation
success.

## References

1. Gasteiger E, et al. Protein identification and analysis tools on the ExPASy
   server. 2005. [doi:10.1385/1-59259-890-0:571](https://doi.org/10.1385/1-59259-890-0:571)
2. Kozlowski LP. IPC - Isoelectric Point Calculator. *Biol Direct*. 2016.
   [doi:10.1186/s13062-016-0159-9](https://doi.org/10.1186/s13062-016-0159-9)
3. Kyte J, Doolittle RF. *J Mol Biol*. 1982.
   [doi:10.1016/0022-2836(82)90515-0](https://doi.org/10.1016/0022-2836(82)90515-0)
4. Conchillo-Sole O, et al. *BMC Bioinformatics*. 2007.
   [doi:10.1186/1471-2105-8-65](https://doi.org/10.1186/1471-2105-8-65)
5. Betush RJ, Urban JM, Nilsson BL. *Biopolymers*. 2018.
   [doi:10.1002/bip.23099](https://doi.org/10.1002/bip.23099)
6. Zapadka KL, et al. *Interface Focus*. 2017.
   [doi:10.1098/rsfs.2017.0030](https://doi.org/10.1098/rsfs.2017.0030)
7. Bak A, et al. *AAPS J*. 2015.
   [doi:10.1208/s12248-014-9688-2](https://doi.org/10.1208/s12248-014-9688-2)
8. Conradi RA, et al. *Pharm Res*. 1991.
   [doi:10.1023/A:1015825912542](https://doi.org/10.1023/A:1015825912542)
9. Rezai T, et al. *J Am Chem Soc*. 2006.
   [doi:10.1021/ja063076p](https://doi.org/10.1021/ja063076p)
10. Di L. *AAPS J*. 2015.
    [doi:10.1208/s12248-014-9687-3](https://doi.org/10.1208/s12248-014-9687-3)
11. Furman JL, Chiu M, Hunter MJ. Early engineering approaches to improve
    peptide developability and manufacturability. *AAPS J*. 2015;17:111-120.
    [doi:10.1208/s12248-014-9681-9](https://doi.org/10.1208/s12248-014-9681-9)
