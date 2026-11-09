# FABLE IWR V1 publication checklist

## Completed V1 review

- [x] Scientific methodology, input inventory and crop-water/technology documentation included.
- [x] Irrigation shares and efficiency derivation attributed to Jägermeyr et al. (2015) Table S1 and Rohwer et al. (2007), with anchor and gap-handling methods documented.
- [x] Separate scientific RCP pathway outputs distinguished from their operational FABLE Calculator use.
- [x] Editable notebook-first processing sequence and companion scripts included.
- [x] Approved final net master QC passed locally.
- [x] Approved technology QC passed: 824 records, 179 countries, 0 duplicate keys.
- [x] Reconstructed and reference gross masters have 29,338 rows each.
- [x] Numerical comparison passed: 0 missing/extra keys and 0 mismatches across 33 shared numeric fields.
- [x] 10 bundled scientific unit tests passed locally.
- [x] Numerical comparison summary saved in `docs/qc/gross-reference-comparison.json`.

## Publish responsibly

- [ ] Confirm organizational permission to publish the code, methodology and any dataset files you intend to include.
- [ ] Inspect the staged Git file list before pushing; do not publish raw source inputs, private notebooks or unapproved reference data.
- [ ] Choose a license only when rights to license the repository are clear.

## Planned scientific extensions

- [ ] Re-execute full original ISIMIP / LPJmL / GEPIC / PEPIC data processing.
- [ ] Export and independently reproduce all approved proxy, scaling and route-selection decisions.
- [ ] Establish raw-source-to-net numerical agreement and then automate the entire pipeline.

V1 is a documentation-and-notebook scientific release with **validated accepted-net-to-gross calculations**. It is not described as fully reprocessed from raw source datasets.
