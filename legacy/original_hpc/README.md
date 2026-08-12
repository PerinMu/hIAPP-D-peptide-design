# Historical HPC script provenance

The original cluster scripts were recovered after the portable repository was
prepared. They contained usernames, private mount paths and a proxy endpoint,
so raw copies are intentionally not included in this public repository.

| Original filename | SHA256 | Public counterpart |
|---|---|---|
| `submit_keep8.sh` | `34a84d00ea10e65122ed261a4baf6d10710b9c64df5a09ab8311cd7b28216869` | `hpc/submit_keep8.sh` |
| `run_lig_array_large.sh` | `2d94bde169cde9ebb9631e75669c11d0299c739a36d4c6889c7ff5e2c6854ec8` | `hpc/run_lig_array_large.slurm` |
| `run_lig_array_large_fixed.sh` | `2d94bde169cde9ebb9631e75669c11d0299c739a36d4c6889c7ff5e2c6854ec8` | same as above |
| `run_lig_one_large.sh` | `0abbba3f72d6f349cfdb26557eafb1342b556cd6a84e72b40b31d6943cfe5d61` | `hpc/run_lig_one_large.sh` |
| `extract_missing_model0_to_batch2.py` | `9f82e7b242c3d5d82342fd2df66676595159794dd7b9a3284f67afca792c2703` | `scripts/find_missing_model0.py` |

The two array-runner files are byte-for-byte identical. The public dispatcher
retains the historical seven-argument interface, sorted local state,
one-element arrays, locking and resume behavior. The public retry extractor is
deliberately stricter: it compares every expected YAML ID with successful
`model_0` CIF IDs, so it also detects inputs for which no output task directory
was created.

