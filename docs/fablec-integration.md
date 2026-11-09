# Historical FABLE-C input export — accepted scientific route

## What this stage reproduces

The historical FABLE3 input design is documented in the ORIGINAL research notebook `8 after finding problem with data sept 16.ipynb`, final global export cell (the source is **not** published in this repo). It combines:

1. `05_FABLE_SPAM_country_product_2000_2020.csv.gz`: complete SPAM country × year × FABLE-product key skeleton.
2. `06_FABLE_C_SPAM_historical_input_2000_2020_HARMONIZED.csv.gz`: authoritative nonmissing corrected SPAM values, overlaid on 05 by country, year, product.
3. `FABLE_crop_irrigation_water_requirement_2000_2020_FINAL_REPAIRED.csv`: accepted historical *net* IWR coefficient, distinct from the separate RCP-resolved 29,338-row scientific master.
4. `12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv`: accepted country-year surface, sprinkler, drip shares.
5. `13_FABLE_irrigation_efficiency_parameters_FINAL.csv`: frozen delivery efficiencies, read for diagnostic gross coefficients.

The SPAM key panel is **authoritative**: IWR-only keys are reported but excluded. No missing value is silently interpreted as zero. `pineapple` is normalized to FABLE's original `pinapple` spelling before joins; duplicate keys after normalization are errors. All positive irrigated harvested-area records need a usable net coefficient and a complete technology share vector.

## Source paths on the original Windows workstation

| Dataset | Original source location | Local repository destination |
| --- | --- | --- |
| SPAM 05 country master | `C:\FABLE_JAHID\Python Scripts\FINAL SPAM SCRIPt\data\work\SPAMFABLE\05_final_release\country\05_FABLE_SPAM_country_product_2000_2020.csv.gz` | `data/spam/fablec/05_FABLE_SPAM_country_product_2000_2020.csv.gz` |
| SPAM 06 harmonized | `C:\FABLE_JAHID\Python Scripts\FINAL SPAM SCRIPt\data\work\SPAMFABLE\06_harmonized_irrigation\06_FABLE_C_SPAM_historical_input_2000_2020_HARMONIZED.csv.gz` | `data/spam/fablec/06_FABLE_C_SPAM_historical_input_2000_2020_HARMONIZED.csv.gz` |
| Repaired net IWR | `C:\FABLE_JAHID\WORK\Data\Water requirement data\FABLE final irrigation water requirement rebuild\FINAL_RELEASE_POST_SPAM_FIX\FABLE_crop_irrigation_water_requirement_2000_2020_FINAL_REPAIRED.csv` | `data/crop/fablec/FABLE_crop_irrigation_water_requirement_2000_2020_FINAL_REPAIRED.csv` |
| Final shares | `C:\FABLE_JAHID\WORK\Data\Water requirement data\FABLE crop water requirement outputs\final_release\12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv` | `data/technology/12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv` |
| Efficiencies | same `final_release` folder, `13_FABLE_irrigation_efficiency_parameters_FINAL.csv` | `data/technology/13_FABLE_irrigation_efficiency_parameters_FINAL.csv` |
| Original FABLE3 output (optional reference) | `C:\FABLE_JAHID\WORK\Data\FABLE3_GLOBAL_export\FABLE3_GLOBAL_IWR_2000_2020_FINAL.csv` | `data/reference/fablec/FABLE3_GLOBAL_IWR_2000_2020_FINAL.csv` |
| Original FABLE3 SPAM (optional reference) | same folder, `FABLE3_GLOBAL_SPAM_2000_2020_FINAL.csv` | `data/reference/fablec/FABLE3_GLOBAL_SPAM_2000_2020_FINAL.csv` |

Paths are from the original research notebook and might need local adjustment. `tools/collect-fablec-inputs.ps1` accepts optional source-root overrides and never overwrites copied files. If the approved repaired IWR is absent, **do not** silently substitute the pathway-resolved net master.

## Reproduce locally (PowerShell)

```powershell
cd "C:\Users\JAHID\Downloads\GIT HUB ready\FABLE-IWR-Audited-Working-Review\FABLE-IWR"
conda activate pythongeo
.\tools\collect-fablec-inputs.ps1
python scripts\08-export-fablec-historical.py --check --data-root data
python scripts\08-export-fablec-historical.py --execute --data-root data --output-root runs\fablec-historical-01 --reference-iwr data\reference\fablec\FABLE3_GLOBAL_IWR_2000_2020_FINAL.csv --reference-spam data\reference\fablec\FABLE3_GLOBAL_SPAM_2000_2020_FINAL.csv
```

If the optional original exports are unavailable, **omit** the `--reference-iwr` and `--reference-spam` flags; the script will build the new tables and report `NOT_EVALUATED_NO_REFERENCE_PROVIDED`. With both original reference files supplied, it performs key-by-key numerical regression (absolute tolerance 1e-6; relative tolerance 1e-9). Use a new output-root directory each time.

## Output schemas (original FABLE3-compatible)

`FABLE3_GLOBAL_IWR_2000_2020_FINAL.csv`:

| Column | Meaning | Unit |
| --- | --- | --- |
| `CountryISO` | ISO-3 country | code |
| `Year` | historical year | 2000/2005/2010/2015/2020 |
| `Crop` | FABLE crop (incl. `pinapple`) | original calculator product code |
| `Requirement_ha` | **net** crop IWR coefficient | m³/ha/year |
| `Sur_shr` | surface system fraction | 0–1 |
| `Spin_shr` | sprinkler system fraction | 0–1 |
| `Drip_shr` | drip system fraction | 0–1 |

`FABLE3_GLOBAL_SPAM_2000_2020_FINAL.csv` contains the same key panel with `irrigated_harvested` and `rainfed_harvested` in **1,000 ha**, plus irrigated/rainfed harvesting intensity. Missing fields remain blank. This is the historical country/crop panel, **not** a raw SPAM file.

A **separate diagnostic**, `FABLE3_GLOBAL_GROSS_COEFFICIENT_DIAGNOSTIC.csv`, contains `gross_multiplier` and `gross_requirement_m3_ha_yr` obtained using country-year shares and efficiencies (0.42/0.7125/0.855). It is **not** a verified FABLE-C input sheet; do not import it over the net `Requirement_ha` column. The separate original efficiencies table remains an input and is not falsely represented as a new country-dependent observational dataset.

The exporter also saves `QC_IWR_coefficients_outside_final_SPAM_panel.csv` and `historical-export-qc.json` with row coverage, missing-value diagnostics, historical export status, and optional original-export comparison outcomes. Local source paths are printed by the input check, not copied into the release QC JSON.

## Additional canonical Calculator-input tables

Alongside the original FABLE3 seven-column IWR and matched SPAM exports, the exporter creates these **three separate historical inputs**, based on exactly the same accepted repaired IWR and approved technology parameters:

| File | Columns | Intended use |
| --- | --- | --- |
| `FABLEC_NetIWR_Historical_2000_2020.csv` | `country_iso3`, `year`, `fable_product`, `net_iwr_mm_yr`, `net_iwr_m3_ha_yr` | Scenario-neutral **net** coefficient per crop-country-year; blank values remain blank |
| `FABLEC_IrrigationTechnologyShares_2000_2020.csv` | `country_iso3`, `year`, `surface_share`, `sprinkler_share`, `drip_share` | Approved country-year system fractions; blanks fail the standalone-export QC |
| `FABLEC_IrrigationEfficiencies.csv` | `technology`, `final_delivery_efficiency` | Surface 0.42, sprinkler 0.7125, drip 0.855; the original constants, not estimates recalibrated by this script |

The canonical `net_iwr_mm_yr` is exactly `net_iwr_m3_ha_yr / 10`; the exporter also checks `iwr_mm_yr` versus `iwr_m3_ha_yr` when both appear in the repaired input. The script neither creates crop-year futures after 2020 nor fills missing values. The additional exports are derived data products and do **not** replace the original FABLE3 regression-reference files.

**FABLE-C use:** `req_ha` may use the net m³/ha/year coefficient after verifying workbook crop labels. `with_ha` can use the same coefficient multiplied by the country-year weighted inverse efficiency, while the workbook retains `TotReq = Irrarea × req_ha × 0.001` and `TotWith = Irrarea × with_ha × 0.001` where `Irrarea` is in 1,000 ha and totals are million m³/year. This package does not modify an Excel workbook or independently verify the 58 workbook labels against the 56 FABLE scientific products. In particular, `pinapple` and the additional fibre labels require an explicit mapping check; do not silently assign missing crop coefficients.

## Integration boundary

This is a *prepared historical country-crop coefficient export*, not an automatic modification of a FABLE Excel workbook. An operational workbook's exact destination sheet/table, naming and whether shares/efficiencies are applied elsewhere must be checked against that specific FABLE-C version before importing. Do not multiply the coefficients by irrigated harvested area when supplying `Requirement_ha` to a Calculator that already calculates area and irrigation withdrawals. Do not apply efficiency multipliers twice.

**Verification boundary:** The earlier 29,338-row / 33-field gross validation verifies accepted-net → gross. It does **not** verify this historical FABLE3 export. The new stage has synthetic regression tests; original historical output parity is pending until the specific reference CSVs are supplied and compared.
