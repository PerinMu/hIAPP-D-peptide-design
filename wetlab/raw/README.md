# Raw-data schema

Create one CSV per experiment or append to a versioned master CSV with these
minimum fields:

```text
experiment_id,run_date,plate_id,well,time_min,fluorescence_au,
hIAPP_concentration_uM,peptide_id,peptide_concentration_uM,
condition_role,independent_repeat,technical_replicate,operator,
hIAPP_lot,peptide_lot,buffer,pH,temperature_C,notes
```

`condition_role` should explicitly identify `hIAPP_only`, `vehicle`,
`positive_control`, `negative_control`, or `candidate`. Never delete raw points;
record exclusions in a separate auditable table with reason and decision date.

