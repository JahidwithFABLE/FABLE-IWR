# Connecting SPAM historical land inputs with FABLE irrigation water requirements — V1 technical note

## Purpose and boundary

This note explains how the **separate** SPAM-to-FABLE land dataset and FABLE-IWR dataset development workflows interact. It is a methodological description of the IWR dataset and its use in the FABLE framework, not evidence that both IWR climate pathways were deployed in the operational FABLE Calculator.

## 1. SPAM-based historical area inputs

Observed SPAM crop area data for 2000, 2005, 2010 and 2020 were mapped to the 56 FABLE products; the harmonized 2015 data are interpolated from 2010/2020 according to the separate SPAM processing methodology. The SPAM project distinguishes **irrigated harvested area** from **physical irrigation area** and retains country, crop and year mappings. Its dataset preparation, interpolation and validation belong to the separate SPAM repository. The IWR application uses the irrigated **harvested** hectares as the area weighting and volume-conversion denominator. One hectare may be harvested more than once in a year; physical area and harvested area must not be interchanged.

## 2. Net crop irrigation water requirement — scientific dataset

The IWR project uses ISIMIP crop-model outputs, particularly LPJmL `pirrww` as the broad direct-reference series, supported by GEPIC/PEPIC comparisons and further FAO seasonal crop-water-need, other crop-water and geographical/temporal proxy evidence. Crop-specific mapping, scaling and reviewed direct/proxy decision routes produced a 56-product historical scientific dataset for reference years **2000, 2005, 2010, 2015 and 2020**. The accepted net master contains **29,338 country–product–year–pathway records** across **179 countries**, with the available `RCP26` and `RCP60` components. Not every Cartesian combination exists.

The net coefficient `water_requirement_mm_yr` is millimetres per year. One millimetre per hectare equals **10 m³/ha**, hence:

`NetIWR_m3_ha_yr = NetIWR_mm_yr × 10`.

This represents net irrigation requirement and does **not** include the additional application/conveyance requirements of irrigation technology. Crop-water simulation evidence and accepted proxy/scaling decisions are separate from the technology adjustment below.

## 3. Country–year irrigation technology shares

The original technology-share source processing used two cited scientific works:

- **Rohwer, Gerten & Lucht (2007), PIK Report No. 104**, *Development of Functional Irrigation Types for Improved Global Crop Modelling* — Annex A historical irrigation-system patterns and Functional Irrigation Types (IFTs) for early-model reference.
- **Jägermeyr et al. (2015), HESS 19:3073–3091**, *Water savings potentials of irrigation systems: global simulation of processes and linkages* — **Supplement Table S1** country technology shares compiled using FAO (2014), ICID (2012), and Rohwer (2007).

The pipeline assigns an approximate Rohwer early model anchor to **2000**, the Jägermeyr source compilation as a later model anchor to **2015**, interpolates **2005/2010** and carries the later anchor to **2020**. These are not uniformly observed system-share time series. Missing information is flagged, not silently turned into 100% surface irrigation. The accepted country-year layer was completed using the original *same-country nearest valid year first; predefined same-year regional peers second* rules. It contains **824 records for 179 countries** and three fractions (`surface_share`, `sprinkler_share`, `drip_share`) summing to one.

**Important limitation:** these shares are **country–year**, not country–crop–year; every FABLE crop within a country-year receives the same system mix. Full detail, source paths, exception handling and reference links: [`irrigation-technology-sources.md`](irrigation-technology-sources.md).

## 4. Selected irrigation system efficiencies

The original main IWR notebook **Cell 114** selected a generic technology delivery baseline based on application efficiency multiplied by conveyance efficiency, consistent with the Rohwer (2007) methodological framework:

| Irrigation system | Application | Conveyance | Total delivery efficiency | Inverse multiplier |
|---|---:|---:|---:|---:|
| Surface | 0.60 | 0.70 | **0.42** | 2.380952 |
| Sprinkler | 0.75 | 0.95 | **0.7125** | 1.403509 |
| Drip | 0.90 | 0.95 | **0.855** | 1.169591 |

The baseline does **not** multiply by Rohwer's additional country-specific management/distribution factor; nor does it use Jägermeyr's beneficial-transpiration efficiency as though it were an application-and-conveyance delivery coefficient. The accepted efficiency parameter file has exactly **three rows**.

For crop net requirement `N` (mm/yr), the modeled gross source withdrawal requirement is:

\[
G_{mm/yr} = N_{mm/yr}\left(\frac{s_{surface}}{0.42} + \frac{s_{sprinkler}}{0.7125} + \frac{s_{drip}}{0.855}\right).
\]

To obtain gross annual volume, multiply `G` by **10 m³/ha/mm**, then by corresponding **SPAM irrigated harvested hectares**. The difference between modeled gross and net requirement is labelled **additional delivery requirement**, not necessarily consumptive water loss; return flows are not resolved by this calculation.

## 5. Climate pathways versus operational Calculator use

The scientific dataset exports separate **RCP2.6** (`RCP26`) and **RCP6.0** (`RCP60`) output layers (14,669 records each). The project's initial FABLE Calculator application used harmonized historical crop-specific coefficients; **both RCP-specific source outputs were not directly deployed as separate operational Calculator scenario inputs**. Dataset construction and FABLE-C scenario implementation are separate claims.

## 6. Release contents, evidence and limitations

The GitHub V1 contains editable notebook stages, code companions, source/input inventories, methodology and QC evidence. It does **not** automatically include the processed numerical CSV masters or third-party input datasets. Where permitted, those could be distributed separately.

Accepted-net → gross numerical reproduction is verified locally: **29,338 reconstructed vs 29,338 reference records, 33 shared numeric scientific fields, no reported mismatches**, plus accepted 824-row technology share QC and 10 local synthetic tests. The complete raw ISIMIP/LPJmL/GEPIC/PEPIC → selected proxy/scaling routes → accepted net master remains **not independently numerically replayed**. The country-share source-to-824-row derivation also awaits a full independent numerical comparison. All original research notebooks remain outside the public-facing repository.

## Key references

- Jägermeyr, J., Gerten, D., Heinke, J., Schaphoff, S., Kummu, M., & Lucht, W. (2015). *Water savings potentials of irrigation systems: global simulation of processes and linkages*. **Hydrology and Earth System Sciences**, 19, 3073–3091. https://doi.org/10.5194/hess-19-3073-2015 (see **Supplement Table S1**).
- Rohwer, J., Gerten, D., & Lucht, W. (2007). *Development of Functional Irrigation Types for Improved Global Crop Modelling*. **PIK Report No. 104**. https://publications.pik-potsdam.de/pubman/item/item_14687.
