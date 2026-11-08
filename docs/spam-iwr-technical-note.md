# FABLE historical land and irrigation inputs — combined technical note

## Purpose

This note describes how the historical SPAM-based cropland dataset and the IWR-based water requirement dataset connect to the FABLE Calculator. They are maintained as **separate code repositories**. Their provenance and validation must remain distinct even where IWR uses SPAM irrigated area as a denominator or volume multiplier.

## 1. SPAM-based historical land and production area inputs

The observed land-data processing uses original SPAM releases for 2000, 2005, 2010 and 2020. Crop-specific harvested and physical areas are reconstructed at native five-arc-minute resolution and mapped to 56 FABLE products. The 2015 historical layer is an interpolated midpoint based on 2010 and 2020 spatial observations and a documented country crosswalk. SPAM2000 completion includes approved country-level and MIRCA-based harmonization where the original source evidence is inadequate. The output is a historical 2000–2020 Calculator input table with irrigated/rainfed harvested area and physical-area/intensity quantities.

The six SPAM clean-start stages have previous reference-validation PASS evidence. **That evidence belongs to the original validated scripts; a separate fresh run is still needed for any restructured GitHub code.** The SPAM workflow retains frozen upstream mapping/crosswalk and FAOSTAT/MIRCA decision evidence at particular steps and should not be described as independently reproducible from the raw SPAM downloads alone.

## 2. Irrigation-water requirement (IWR) coefficients

Country × FABLE-product × year × climate-pathway net irrigation water coefficients were developed using ISIMIP LPJmL `pirrww` as a principal direct crop pathway and supplementary evidence for crops and country-years lacking direct coverage. GEPIC and PEPIC provided model comparisons and checks. External crop and hydrological evidence, robust reference-scaling approaches, crop proxy decisions and geographic/temporal completion contributed to the final accepted route layer. Scientific justification for each route belongs in the full technical report.

The final crop water-requirement master is 29,338 records, with RCP26 and RCP60 Calculator scenarios separated into 14,669 records each. The canonical quantity is mm/year, converted as 1 mm over 1 ha = 10 m³/ha/year. The total requirement uses SPAM irrigated harvested hectares where area-weighted volumes are calculated. Crop requirements exclude irrigation technology inefficiencies and constraints on available surface/groundwater.

## 3. Irrigation systems and gross withdrawal requirements

Country-year shares of surface, sprinkler and drip irrigation were assembled from Jägermeyr and Rohwer sources, with documented time interpolation/carry-forward and separate source-gap completion. The final approved technology layer comprises 824 country-year rows. Generic delivery efficiencies used by the first-version calculation are 0.42, 0.7125 and 0.855 respectively. At any country-year state, gross withdrawal requirement is the net depth multiplied by the sum of each technology share divided by its efficiency.

This calculates an **unconstrained gross irrigation withdrawal requirement**, not observed realised irrigation withdrawal. Gross minus net is additional delivery requirement and should not automatically be called consumptive water loss because return flows are not modelled.

## 4. Interface and reproducibility boundary

The IWR code package contains a source-derived reconstruction of baseline technology-share anchors and a shorter **numerical replay** from the accepted net master and approved shares/efficiencies. It does not yet independently replay the full raw ISIMIP → crop-route-selection → missing-crop recovery workflow. The SPAM and IWR repositories must therefore carry separate validation manifests. Do not elevate a unit test or a frozen-evidence comparison into a full scientific reproduction claim.

## 5. Release governance

Metadata and code may be public only after their provenance, redistribution rights, institutional review and license have been checked. Raw SPAM/ISIMIP and third-party support datasets should be downloaded from permitted sources, rather than redistributed in the GitHub repositories without authorization.
