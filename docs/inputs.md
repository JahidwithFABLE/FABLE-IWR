# Input file contract

Put source files under the following directories **without renaming their table columns**. The paths are relative to `--data-root` and can live anywhere on Windows, Linux or macOS.

```text
data/
├── crop/
│   ├── 01_FABLE_crop_water_requirement_master_2000_2020_FINAL.csv.gz
│   └── accepted-routes.csv.gz                   # optional accepted Cell-109 output
├── technology/
│   ├── 01_global_irrigation_system_source_jagermeyr2015.csv # optional source replay
│   ├── 02_global_rohwer_irrigation_reference.csv             # optional source replay
│   ├── 12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv
│   └── 13_FABLE_irrigation_efficiency_parameters_FINAL.csv
├── reference/
│   └── 09_FABLE_gross_irrigation_withdrawal_requirement_master_2000_2020_FINAL.csv.gz
└── isimip/                                      # optional raw downloaded ISIMIP files
```

Files ending `.csv.gz` may be supplied as uncompressed `.csv` equivalents. Source files are private/local, protected by `.gitignore`; do not commit third-party datasets until distribution terms are reviewed.

**Net scientific master** must contain country (`country_iso3`), year (`year`), FABLE crop (`fable_product`), climate pathway (`pathway`), `water_requirement_mm_yr` (net irrigation depth in millimetres per year), `water_requirement_m3_ha_yr` (net depth in m³/ha/year) and `SPAM_irrigated_area_ha` (irrigated harvested area in hectares). The accepted file should have 29,338 rows, covering 56 FABLE crops, 179 countries, five years and RCP26/RCP60 where present.

**Approved technology share table** must have `country_iso3`, `year`, `surface_share`, `sprinkler_share`, and `drip_share`. The approved country-year coverage previously reported is 824 rows; the original complete layer contains technology completion method/confidence information. Do not replace missing source shares by assuming 100% surface irrigation.

**Efficiencies** are read from `technology` and `final_delivery_efficiency`. The frozen values are surface 0.42, sprinkler 0.7125 and drip 0.855, giving gross-to-net multipliers of approximately 2.380952, 1.403509 and 1.169591. These parameters are not learned from the new input data.

**Reference gross master** is optional for the build but mandatory to claim a numerical reference match. The comparison is on common numerical fields, not the complete original 89-column release schema.

**Accepted route evidence** must come from the final *scientifically reviewed* route layer (`global_full_route_audit_109`, Notebook Cell 109) with `target_crop`, `country_iso3`, `year`, `pathway`, `SPAM_irrigated_area_ha`, `route_value_mm_yr`, `route_group`, `route_type`, `confidence`, `semantic_status`, and `final_value_available`. The historical notebook did **not** necessarily save this exact layer to a named CSV; export it deliberately from the validated session if you want to run `tools/rebuild-net-routes.py`.
