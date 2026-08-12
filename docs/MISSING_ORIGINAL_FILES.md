# Original-file recovery status

The historical cluster scripts have now been recovered. Raw files contain a
username, private mount paths and a proxy endpoint, so they are not copied into
the public tree. Their SHA256 values are recorded in
`legacy/original_hpc/README.md`, and path-neutral counterparts are included in
`hpc/`.

## Recovered

1. `submit_keep8.sh`
   - Historical bounded-concurrency dispatcher.
   - Recorded call signature included the YAML directory, concurrency 8,
     polling interval 20, state directory, an array runner, job prefix and `1`.
   - Public counterpart: `hpc/submit_keep8.sh`.

2. `run_lig_array_large.sh`
   - Historical per-task or array Slurm runner passed to `submit_keep8.sh`.
   - Public counterpart: `hpc/run_lig_array_large.slurm`.

3. `run_lig_one_large.sh`
   - Named in the recommended historical server directory layout.
   - It may be an earlier single-YAML runner. The surviving
     `Design/run/screen_template.sh` contains the equivalent Boltz command and
     and the recovered file were used to prepare `hpc/run_lig_one_large.sh`.

4. `run_lig_array_large_fixed.sh`
   - Recovered and byte-for-byte identical to `run_lig_array_large.sh`.

5. `extract_missing_model0_to_batch2.py`
   - Recovered. The public `scripts/find_missing_model0.py` intentionally uses a
     more complete expected-YAML minus successful-CIF comparison.

## Reconstructed and validated

6. `extract_cif_sequences.py`
   - Original file was not found.
   - Replacement: `scripts/extract_cif_sequences.py`.
   - It exactly reconstructed both committed tables from retained source trees:
     1,990 design CIFs -> 1,956 unique sequences and 7,960 inverse-folding CIFs
     -> 7,854 unique sequences.

## Archival policy

Recovered originals remain unchanged in the private source folder. Do not add
them to public Git history. If an access-controlled archival deposit is later
created, preserve the raw bytes and verify them against the recorded SHA256.
