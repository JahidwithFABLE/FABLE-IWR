# V1 quality-control evidence

## Completed on the original accepted input/reference datasets

- Accepted net IWR master preflight: **PASS_ACCEPTED_NET_MASTER_NUMERIC_QC**.
- Technology QC: **824** records, **179** countries, **0** duplicate country-year keys; share sum check **PASS**.
- Delivery efficiencies: surface **0.42**, sprinkler **0.7125**, drip **0.855**.
- Gross requirement replay: **29,338** reconstructed records and **29,338** reference records.
- Missing or extra matching keys: **0**.
- Compared scientific fields: **33**.
- Numerical mismatches: **0** within the comparator tolerances.
- Comparison result: **PASS_SHARED_NUMERIC_REFERENCE_MATCH**.
- Local scientific unit tests for the original 17-notebook stage: **10/10 passed** on the user's Windows `pythongeo` environment.

Saved comparison summary: [`qc/gross-reference-comparison.json`](qc/gross-reference-comparison.json).

## New historical FABLE-C export extension (pending production reference parity)

- Added `scripts/08-export-fablec-historical.py` and a native calculation notebook `notebooks/16-fablec-historical-export.ipynb`.
- Synthetic tests for SPAM 05+06 overlay, repaired net IWR, crop spelling, positive-area QC, share sums, efficiency constants, the three standalone Calculator CSVs and reference mismatch detection pass in the package review runtime (**21/21** total bundled tests). This is not production numerical validation.
- Original historical FABLE3 output reference files were not included in the upload. **No real-data export-to-original parity claim is made**. To establish parity, use the flags `--reference-iwr` and `--reference-spam` against original approved CSVs. The new code does not independently reconstruct the repaired Dataset A from raw source models.

## Boundaries

Accepted-net → gross equivalence applies only to the 33 shared scientific numeric fields, not the original 89-column release metadata. The separate original ISIMIP source → 56-product net IWR route-choice reconstruction remains pending. Permission to redistribute any institutional or provider datasets requires review.
