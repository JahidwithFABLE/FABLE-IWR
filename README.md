# FABLE Irrigation Water Requirements (IWR)

**Dataset methodology and scientific processing notebooks - Version 1.0**

This repository documents the development of crop-specific **net irrigation water requirements (IWR)** and **gross irrigation withdrawal requirements** for the FABLE framework. It brings together the scientific data sources, crop harmonization, evidence-based completion methods, irrigation-system assumptions, calculation notebooks and quality-control procedures used in the first IWR dataset.

## Dataset at a glance

| Feature | Coverage |
| --- | --- |
| FABLE products | 56 |
| Countries | 179 |
| Reference years | 2000, 2005, 2010, 2015, 2020 |
| Scientific dataset pathways | RCP2.6 and RCP6.0 (`RCP26`, `RCP60`); pathway files are **not** evidence that both were implemented in the operational FABLE Calculator |
| Accepted net IWR master | 29,338 country–product–year–pathway records |
| Accepted gross withdrawal master | 29,338 records |
| Irrigation technology shares | 824 country–year records |
| Irrigation system efficiencies | Surface 0.42; sprinkler 0.7125; drip 0.855 |

*Counts refer to the accepted original release, not a claim that every possible country–product–year combination exists.*

## Scientific workflow

1. **Source data:** collect and review ISIMIP irrigation-water simulations, including LPJmL and supplementary GEPIC/PEPIC comparisons, together with SPAM irrigated harvested-area data.
2. **Spatial and temporal harmonization:** aggregate gridded information into national, crop-specific evidence for the FABLE reference years and climate pathways.
3. **FABLE crop mapping:** harmonize model crop categories with the 56 FABLE products.
4. **Missing-crop completion:** document approved direct estimates, proxy crops, evidence-based scaling and geographical/temporal completion while retaining their provenance and confidence indicators.
5. **Net IWR dataset:** construct the accepted crop-specific net requirement coefficients in mm/year and m³/ha/year.
6. **Irrigation systems:** derive and complete country–year surface, sprinkler and drip shares using the reviewed source evidence.
7. **Gross requirement:** convert net IWR into gross irrigation withdrawal requirements using the approved irrigation-system efficiencies and shares.
8. **Quality control:** test coverage, consistency, unit conversions and numerical agreement with the original accepted release.

The methodology and source decisions are explained in [`docs/methodology.md`](docs/methodology.md), [`docs/irrigation-technology-sources.md`](docs/irrigation-technology-sources.md), [`docs/source-lineage.md`](docs/source-lineage.md) and [`docs/reproducibility.md`](docs/reproducibility.md).

## Irrigation technology data and references

The country–year technology shares were derived from **Rohwer, Gerten & Lucht (2007)** and **Jägermeyr et al. (2015), Supplement Table S1**. The generic system delivery efficiencies are based on the Rohwer-style *application × conveyance* assumptions, not directly copied from Table S1. Sources, interpolation, missing-country rules and limitations are documented in [`docs/irrigation-technology-sources.md`](docs/irrigation-technology-sources.md).

**Scenario-use distinction:** The scientific IWR release has separate `RCP26` and `RCP60` files. This does not mean both climate pathways were directly implemented in the operational FABLE Calculator; the initial Calculator application used harmonized historical crop-specific coefficients. Likewise, the files in this GitHub repository document the data processing but do **not** contain the released numerical CSV datasets themselves.

## Core calculation

For net crop-specific water requirement depth \(N\), country–year irrigation technology shares \(s_i\), and their delivery efficiencies \(\eta_i\):

\[
G = N\left(\frac{s_{surface}}{0.42}+\frac{s_{sprinkler}}{0.7125}+\frac{s_{drip}}{0.855}\right)
\]

Here \(G\) is the **gross irrigation withdrawal requirement**, not observed withdrawal. Convert mm/year to m³/ha/year by multiplying by 10. Volumes use SPAM **irrigated harvested area**, not total physical irrigated area. The additional gross-minus-net requirement is not necessarily consumptive loss, because return flows are not modelled.

## Repository organization

| Folder | Content |
| --- | --- |
| [`notebooks/`](notebooks/README.md) | 17 editable notebooks covering scientific processing stages and QC |
| `scripts/` | Companion Python scripts for reproducible calculations |
| `tools/` | Source-data acquisition and input-management utilities |
| [`docs/`](docs/methodology.md) | Methodology, sources, input inventory, data dictionary and validation evidence |
| `tests/` | Scientific calculation regression tests |
| `config/` | Explicit technology-completion peer definitions |
| `data/` | Locally supplied sources and reference outputs; not distributed by default |

## Running the V1 calculation checks

In a Python environment (developed on Windows using Conda `pythongeo`):

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run-iwr.py --check --data-root data
python run-iwr.py --execute --data-root data --output-root runs/replay-01
```

Input file names and destinations are in [`docs/input-manifest.csv`](docs/input-manifest.csv) and [`docs/inputs.md`](docs/inputs.md). The calculation runner uses the **accepted final net IWR and technology inputs** to replay the gross-withdrawal step. To study the upstream scientific methods, see the individual notebooks in processing order.

## V1 numerical checks

The first local data replay verified **29,338 reconstructed and reference gross records**, with **zero missing/extra keys** and **zero mismatches across 33 compared scientific numerical fields**. The approved technology layer passed its share checks (824 records, 179 countries), and all 10 bundled scientific unit tests passed. Evidence: [`docs/qc/gross-reference-comparison.json`](docs/qc/gross-reference-comparison.json).

**Reproducibility boundary:** V1 documents and implements the scientific stages, but a complete independent regeneration of the original accepted net IWR route choices from every raw ISIMIP source has not yet been numerically established. The 33-field match validates the **accepted-net-to-gross** calculation, not the entire source-to-net reconstruction. See [`docs/reproducibility.md`](docs/reproducibility.md) for details.

## Data access and release scope

The original research notebooks are retained separately from this public-facing repository. Large raw provider datasets, locally collected input files and institutional reference datasets are not automatically published. Source locations and required filenames are documented so that authorized users can supply them locally. The processed final datasets can be distributed separately **where data rights and institutional publication approval permit**.

## Related project

The irrigated harvested-area inputs connect this IWR workflow to the separate **SPAM-to-FABLE** harmonization project. See [`docs/spam-iwr-technical-note.md`](docs/spam-iwr-technical-note.md) for the technical connection.
