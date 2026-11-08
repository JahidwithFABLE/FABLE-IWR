# V1 quality-control evidence

## Completed on the original accepted input/reference datasets

- Accepted net IWR master preflight: **PASS_ACCEPTED_NET_MASTER_NUMERIC_QC**.
- Technology QC: **824** records, **179** countries, **0** duplicate country-year keys; shares sum check **PASS**.
- Delivery efficiencies: surface **0.42**, sprinkler **0.7125**, drip **0.855**.
- Gross requirement replay: **29,338** reconstructed records and **29,338** reference records.
- Missing or extra matching keys: **0**.
- Compared scientific fields: **33**.
- Numerical mismatches: **0**, under the numerical comparator's configured tolerances.
- Comparison result: **PASS_SHARED_NUMERIC_REFERENCE_MATCH**.
- Local automated scientific unit tests: **10/10 passed** on the user's Windows `pythongeo` environment.

The saved comparison summary is [`qc/gross-reference-comparison.json`](qc/gross-reference-comparison.json). It contains the complete field-level mismatch counts.

## Scope and remaining validation

This confirms the **accepted net coefficients + approved technology shares + efficiencies → gross withdrawal calculation** for the compared fields. It does **not** confirm independent source-to-net equivalence for all original ISIMIP, LPJmL, GEPIC/PEPIC, SPAM mapping, proxy/scaling and route-selection processing. The original research notebooks and intermediate evidence should be retained for a later independent source replay.

The 89-column original gross release is not claimed to be byte-identical to the reconstructed output, because the comparison is restricted to 33 shared scientific numeric fields.
