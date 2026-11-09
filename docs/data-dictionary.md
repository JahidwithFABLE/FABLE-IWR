# Scientific data dictionary (core fields)

This dictionary captures accepted concepts and mandatory field checks. It is **not** a claim that all original 37 net-master or 89 gross-master columns have been reconstructed; inspect the actual original header before approving a complete schema dictionary.

| Field | Meaning | Unit / constraint | Scope |
|---|---|---|---|
| `country_iso3` | Country ISO-3 code | Three-letter identifier | Country product states |
| `year` | Historical year | 2000, 2005, 2010, 2015, 2020 | Net/technology/gross |
| `pathway` | Climate pathway | `RCP26` or `RCP60` | Net/gross |
| `fable_product` | Canonical FABLE commodity | 56 products | Net/gross |
| `SPAM_irrigated_area_ha` | SPAM irrigated **harvested** area, not physical footprint | ha | Net/gross volumes |
| `water_requirement_mm_yr` | Net irrigation water requirement depth | mm yr⁻¹ | Net master |
| `water_requirement_m3_ha_yr` | Net per-hectare requirement | m³ ha⁻¹ yr⁻¹; = 10 × mm yr⁻¹ | Net master |
| `route_value_mm_yr` | Approved final route evidence value | mm yr⁻¹ | Frozen route export |
| `route_group`, `route_type` | Scientific support route and proxy provenance | categorical | Frozen route export |
| `confidence`, `semantic_status` | Evidence/confidence and semantic flags | categorical | Frozen route export |
| `surface_share`, `sprinkler_share`, `drip_share` | Country-year irrigation technology fractions | 0–1; sum to 1 | Technology |
| `technology`, `final_delivery_efficiency` | Irrigation system and frozen delivery efficiency | surface 0.42; sprinkler 0.7125; drip 0.855 | Efficiency table |

## Governing relations

- `water_requirement_m3_ha_yr = 10 × water_requirement_mm_yr`.
- `net_requirement_m3 = water_requirement_m3_ha_yr × SPAM_irrigated_area_ha`.
- `gross_requirement_m3_ha_yr = net_requirement_m3_ha_yr × (surface_share / 0.42 + sprinkler_share / 0.7125 + drip_share / 0.855)`.
- Gross volume multiplies this per-hectare gross rate by SPAM irrigated harvested area; do not substitute physical irrigated area.
- Gross irrigation withdrawal **requirement** is a modelled unconstrained demand, not an observed withdrawal or water supply.

See `docs/inputs.md` and `docs/methodology.md` for source-specific meanings and limitations.

## Optional historical FABLE-C inputs

The standalone historical export adds `net_iwr_mm_yr` (mm/yr) and `net_iwr_m3_ha_yr` (m³/ha/year), keyed by `country_iso3`, `year`, and `fable_product`, without an RCP dimension. Country-year shares and selected technology efficiencies are exported in separate files. Missing net coefficients remain missing. See `docs/fablec-integration.md` for the schema and workbook integration limits.
