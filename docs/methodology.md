# IWR technical methodology — concise code companion

## Water requirement (net)

The scientific input follows the accepted water-coefficient route layer built from ISIMIP `pirrww` data (LPJmL direct targets where available), cross-model checks involving GEPIC/PEPIC, crop-needs and external evidence, and documented cross-crop proxy/temporal/geographic completion. Each accepted country × FABLE product × year × pathway state has a route and confidence designation. The original final scientific master contains **29,338 rows** for 56 products and pathways RCP26/RCP60. The code in this public package **does not rerun the full crop- and region-specific route-selection process**; it accepts its scientifically reviewed output.

The canonical net depth is `water_requirement_mm_yr` (mm/year), and:

\[
\text{NetIWR}_{m^3/ha/yr}=10\,\text{NetIWR}_{mm/yr}.
\]

Total net crop requirement before external system losses is the net unit area requirement (m³/ha/year) multiplied by the **SPAM irrigated harvested area** (hectares). Neither gross irrigation losses nor water availability is included at this stage.

## Country-year irrigation technologies

The original Jägermeyr/Rohwer source-processing workflow constructs two approximate anchors, early (~2000) and later (~2015), then uses linear interpolation for 2005 and 2010 when defensible. The later reference is carried forward to 2020; special zero-vector and source-gap cases are kept explicit. Source-derived shares and the approved full 824-record country-year technology layer are **distinct datasets**; frozen geographic completion cannot be inferred safely from the original two source tables alone.

The three shares (surface, sprinkler, drip) are fractions of their country-year irrigation-technology mix, with a sum of one for the approved model-ready rows.

## Gross irrigation withdrawal requirement

Efficiencies used by the original first-version model, as documented in Notebook Cell 114, are:

| Technology | Final delivery efficiency (fraction) | Gross multiplier (1/efficiency) |
| --- | ---: | ---: |
| Surface | 0.42 | ~2.380952 |
| Sprinkler | 0.7125 | ~1.403509 |
| Drip | 0.855 | ~1.169591 |

For crop requirement depth \(N\) and shares \(s_i\), the gross delivery multiplier is \(M=\sum_i s_i/\eta_i\). Gross requirement \(G=N\times M\); each technology component is \(G_i=N\times s_i/\eta_i\). The independent identity \(G=\sum_i G_i\) is asserted.

Converting depth to volume uses a factor 10 m³/ha per millimetre and multiplies by **irrigated harvested hectares**, not by physical irrigated hectares. Gross-minus-net is called the **additional delivery requirement** (not automatically consumptive loss; return flows are not modelled).

## What the code does not do

It does not quantify realized historical withdrawal, groundwater/rivers availability, environmental flow limits, consumptive loss, actual return flows, or unrestricted redistribution of provider source data. It does not replace the extensive accepted route-selection science in the original notebooks. For provenance, see `source-lineage.md`.
