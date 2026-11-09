# Irrigation technology shares and delivery efficiencies — source and methods note

## Scope

This document records the data lineage and equations used for the first FABLE irrigation-water-requirement (IWR) dataset. It distinguishes (a) **country–year shares of irrigation systems**, (b) **technology efficiency assumptions**, and (c) the resulting **crop-specific gross withdrawal requirements**. The shares are **not crop-specific**: for a given country and year, the same national technology mix is applied to all FABLE products.

## Original scientific references

1. **Jägermeyr, J., Gerten, D., Heinke, J., Schaphoff, S., Kummu, M., & Lucht, W. (2015).** *Water savings potentials of irrigation systems: global simulation of processes and linkages.* Hydrology and Earth System Sciences, 19, 3073–3091. https://doi.org/10.5194/hess-19-3073-2015  
   **Used for:** Supplementary **Table S1** country-level surface, sprinkler and drip/localized irrigation system areas/shares. Table S1 is a source compilation that draws on **FAO (2014), ICID (2012) and Rohwer et al. (2007)**; the publication year is **not** an observation year for each country. Original supplement is linked on the journal article page.
2. **Rohwer, J., Gerten, D., & Lucht, W. (2007).** *Development of Functional Irrigation Types for Improved Global Crop Modelling.* PIK Report No. 104, Potsdam Institute for Climate Impact Research. https://publications.pik-potsdam.de/pubman/item/item_14687  
   **Used for:** historical Annex A country information, Functional Irrigation Type (IFT) classifications when direct shares were unusable, and generic technology-specific application/conveyance efficiency assumptions.

FAO/AQUASTAT and ICID are **upstream sources of the Jägermeyr compilation** in this workflow. The separate recent AQUASTAT water-withdrawal benchmark is a **validation source**, not the derivation of the final surface/sprinkler/drip efficiency constants.

## Prepared local source tables and producing notebook

| Source input (local CSV, not redistributed here) | Scientific content | First-stage notebook |
|---|---|---|
| `data/technology/01_global_irrigation_system_source_jagermeyr2015.csv` | Harmonized Jägermeyr Table S1 evidence, shares and source/QC information | `notebooks/09-irrigation-shares.ipynb` |
| `data/technology/02_global_rohwer_irrigation_reference.csv` | Harmonized Rohwer Annex A/IFT evidence | `notebooks/09-irrigation-shares.ipynb` |
| `data/technology/03_FABLE_global_irrigation_system_shares_2000_2020.csv` | Original initial global model-anchor series; intermediate, **not** the approved final 824-row share table | `notebooks/09-irrigation-shares.ipynb` |
| `data/technology/12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv` | Accepted complete FABLE-required country–year shares (824 rows) | approved output, checked in `notebooks/12-check-technology.ipynb` |
| `data/technology/13_FABLE_irrigation_efficiency_parameters_FINAL.csv` | Three frozen application, conveyance and total-delivery efficiency records | original main IWR notebook Cell 114; checked in `notebooks/12-check-technology.ipynb` |

The first two prepared CSVs are *research-team processed source tables*: this repository does not claim they are original publisher-supplied files. Their exact expected locations are also in `docs/input-manifest.csv`. The intermediate `03_...csv` was not found by the local copy tool at its presumed path; an accepted reconstruction of its contents has **not** yet been demonstrated.

## Share reconstruction — original decisions

The original research notebook `01_build_global_irrigation_system_dataset_FINAL.ipynb.ipynb` defines these model anchors and steps:

- **Early anchor (assigned to 2000):** use Rohwer Annex A direct system shares where valid and near-complete (sum from 0.95 to 1.05), normalized to one. Otherwise use the published IFT category: Surface → (1,0,0), Sprinkler → (0,1,0), Micro → (0,0,1), Mixed → (0.5,0.5,0). These are explicit model representations, not newly observed area fractions.
- **Later anchor (assigned to 2015):** Jägermeyr Table S1 source compilation. Treat positive irrigation-area evidence paired with a 0/0/0 technology vector as a **missing system breakdown**, not zero actual irrigation. Where the early reference is missing and the later pattern is usable, back-cast it with a flag; where later composition is missing and an early pattern exists, carry forward the early pattern with a flag. Keep unresolved gaps unresolved.
- **2005 and 2010:** component-wise linear interpolation between valid early and later model anchors, then normalize valid nonzero vectors. A special genuine zero later vector does not justify interpolating towards a technology mix of zero; retain the earlier valid pattern with a high-uncertainty flag.
- **2020:** carry forward the later reference distribution. No unobserved post-2015 technology transition was added.
- Store provenance columns such as `method`, `source_status`, `reference_period`, anchor and cross-source QC information, rather than labelling interpolated estimates as observations.

The intermediate global series still had source gaps. The original approved FABLE-specific completion (main IWR research notebook Cells 112–113) worked on **required country–year keys** and prioritized:

1. An already complete and valid source country–year technology vector.
2. **R1:** nearest valid year for the *same country* (average on a symmetric tie).
3. **R2:** an average from at least two complete **same-year predefined regional peers**, from the frozen country-to-peer definitions in `config/technology-peers.csv`. This is not an unrestricted arbitrary regional mean.

Each completed record preserves a route and confidence indicator. The accepted final layer has **824 country–year rows from 179 countries**. Approved share QC found no duplicate country–year keys and each triplet sums to one. The code for source and completion replay lives in `notebooks/09-irrigation-shares.ipynb`, `notebooks/10-complete-shares.ipynb` and their script companions. **Only the accepted final table's QC, not end-to-end source-to-approved-table equality, has passed against the user's actual production data.**

## Selected technology efficiency baseline

The original main IWR research notebook, **Cell 114**, selected generic *application efficiency × conveyance efficiency* as the first-version delivery-efficiency baseline:

| System | Application efficiency | Conveyance efficiency | Selected delivery efficiency | 1 / delivery efficiency |
|---|---:|---:|---:|---:|
| Surface | 0.60 | 0.70 | **0.4200** | 2.380952 |
| Sprinkler | 0.75 | 0.95 | **0.7125** | 1.403509 |
| Drip/localized | 0.90 | 0.95 | **0.8550** | 1.169591 |

These constants are **model assumptions adopted from the generic Rohwer (2007)-style efficiency framework**. They are not a new measurement of each country's actual irrigation performance, and they do not reproduce the full country-specific Rohwer management/distribution factor. Original Cell 114 explicitly reviewed Jägermeyr field-application and beneficial-efficiency values but **did not select** them for this source-to-crop delivery baseline because those efficiency definitions have different numerators/system boundaries.

## Crop-specific gross withdrawal requirement

Let `N` be a FABLE product's net irrigation requirement in **mm/year**; let `s_surface`, `s_sprinkler`, `s_drip` be the **fractions** of the country's irrigation-system mix (sum = 1); and let `eta` represent the selected technology delivery efficiencies.

\[
M = \frac{s_{surface}}{0.42} + \frac{s_{sprinkler}}{0.7125} + \frac{s_{drip}}{0.855}
\]
\[
G_{mm/yr} = N_{mm/yr} \, M
\]
\[
G_{m^3/ha/yr} = 10 \, G_{mm/yr}
\]
\[
G_{m^3/yr} = G_{m^3/ha/yr} \, A_{SPAM,irrigated\ harvested\ ha}
\]

System-specific components follow `G_i = N × s_i / eta_i`, summing to `G`. The associated gross-minus-net quantity is termed **additional delivery requirement**, not automatically 'consumptive water loss': return flows are not separately modelled. The result is a **modelled unconstrained withdrawal requirement**, not an observed withdrawal or a surface/groundwater-availability assessment.

## Climate pathways and FABLE Calculator status

The scientific IWR dataset retains **RCP2.6 and RCP6.0** pathway-specific files (`RCP26`, `RCP60`). Those files are alternative source-simulation estimates; **they were not both directly integrated as operational RCP inputs into the FABLE Calculator**. The initial FABLE-C use described by the project was harmonized historical crop-specific coefficients. Avoid describing the scientific output folders as confirmed Calculator scenario integrations.

## Verification and reproducibility boundary

The user's local `pythongeo` run passed the accepted-net and technology preflight. A gross-withdrawal replay from the accepted net master and approved technology parameters matched the accepted gross master for **29,338 country–product–year–pathway records**, **33 shared numeric fields**, and **zero missing/extra keys or reported numeric mismatches** (under comparator tolerances). See `docs/qc/gross-reference-comparison.json`.

These results **do not prove** the raw Jägermeyr/Rohwer tables have been numerically reproduced into the same 824 approved rows, or that all raw ISIMIP → net-IWR proxy and scaling decisions have been independently regenerated. Input data, including third-party source tables and original institutional reference masters, are not automatically redistributed.
