# IWR scientific notebooks

The irrigation source literature, 2000/2015 share anchors, 2005/2010 interpolation, 2020 carry-forward, approved completion rules, and application × conveyance efficiency parameters are documented in [`../docs/irrigation-technology-sources.md`](../docs/irrigation-technology-sources.md).

These notebooks are the editable scientific review sequence. Each scientific processing stage contains computation cells rather than merely calling a packaged script. **The accepted-net-to-gross script replay now agrees with the original gross release across 33 shared numeric fields.** Raw-source-to-net reconstruction and independent execution of every upstream notebook remain unverified.

| Order | Notebook | Purpose | Verification status |
|---|---|---|---|
| 00 | `00-workflow.ipynb` | Orchestrate available accepted-evidence checks | Data-dependent run pending |
| 01 | `01-download-isimip.ipynb` | Manifest-driven ISIMIP acquisition | Live download pending |
| 02 | `02-check-inputs.ipynb` | Source inventory and schema check | Real files pending |
| 03 | `03-spam-weights.ipynb` | SPAM irrigated harvested-area weighting | Synthetic test only |
| 04 | `04-isimip-lpjml.ipynb` | LPJmL gridded-to-country aggregation | Synthetic test only |
| 04b | `04b-gepic-pepic.ipynb` | GEPIC and PEPIC raw NetCDF aggregation | Real ISIMIP files pending |
| 05 | `05-isimip-model-qc.ipynb` | Three-model diagnostics | Real-source comparison pending |
| 06 | `06-crop-mapping.ipynb` | 56-product direct crop support | Accepted mapping replay pending |
| 07 | `07-proxy-evidence.ipynb` | Evidence-based scaling and proxy assessment | Frozen approved proxy evidence pending |
| 08 | `08-net-routes.ipynb` | Numeric net rebuild from accepted route layer | Original Cell 109 export pending |
| 09 | `09-irrigation-shares.ipynb` | Jägermeyr/Rohwer source processing | Original provider tables pending |
| 10 | `10-complete-shares.ipynb` | Country/year completion using original peer hierarchy | Approved 824-record comparison pending |
| 11 | `11-check-net.ipynb` | Final net master QC | Accepted net master script preflight passed; notebook-cell replay not separately established |
| 12 | `12-check-technology.ipynb` | Technology shares and efficiencies QC | Approved shares/efficiency script checks passed; notebook-cell replay not separately established |
| 13 | `13-build-withdrawal.ipynb` | Net-to-gross water requirements | Validated by companion script against 29,338-row reference (33 common fields); notebook-cell replay not separately established |
| 14 | `14-compare-release.ipynb` | Compare rebuilt vs archived final results | Validated by companion script against 29,338-row reference (33 common fields); notebook-cell replay not separately established |
| 15 | `15-aquastat-qc.ipynb` | External benchmarking without filling missing observations | Source-version check pending |

**Run order:** place approved source files under `data/` according to `docs/input-manifest.csv`, open the repository in Jupyter using the `pythongeo` environment, and execute the relevant notebook cells in order. Missing required source files should raise errors rather than trigger invented replacements. Keep the original research notebooks separately in the private handover archive, not in this public-facing candidate.

**Main remaining scientific dependency for full end-to-end reproducibility:** a reproducible replay of the accepted B2/D1/D2/D3 route selection and all proxy/scaling decisions from original upstream data. Frozen route evidence is a transparency-preserving interim solution, not independent scientific regeneration.
