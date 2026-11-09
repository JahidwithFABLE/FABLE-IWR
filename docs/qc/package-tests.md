# Package test evidence — historical export extension

- Date: 2026-11-09
- Command: `python -m unittest discover -s tests -v`
- Result: **21 tests passed**, 0 failures or errors, in this review runtime.
- Scope: synthetic scientific and export-schema tests, including standalone net IWR, country-year irrigation shares, frozen efficiency parameters and original seven-column FABLE3 export preservation.
- Not a production input run. Original repaired historical CSVs and FABLE3 reference export CSVs were absent; production key-by-key numerical parity and Excel workbook compatibility remain **not evaluated**.
- Existing gross accepted-net-to-gross **29,338-row / 33-field** reference comparison is documented separately in `gross-reference-comparison.json`, based on the prior user's `pythongeo` run.
