# Reproducibility — V1 scope

The repository describes the original scientific workflow and supplies editable notebooks and companion scripts for IWR processing. The V1 gross calculation has been independently re-executed **from the accepted net IWR and approved irrigation-technology datasets**, and compared numerically with the accepted final gross master.

| Stage | V1 implementation | Verification status |
| --- | --- | --- |
| ISIMIP download | Manifest-based acquisition utility | Original full acquisition manifest / live source replay remains pending |
| SPAM-based aggregation and LPJmL / GEPIC / PEPIC | Editable processing notebooks | Synthetic tests passed for selected operations; full raw NetCDF replay pending |
| 56-product crop mapping and proxy/scaling | Mapping and proxy-evidence notebooks | Full accepted route-choice reconstruction and source-to-net parity pending |
| Technology-system shares | Source and country-year completion notebooks | Approved final 824-row table independently passed QC; rebuilding from original source needs comparison |
| Irrigation efficiencies and gross calculation | Executable notebook/script calculations | **29,338 rows and 33 shared numeric fields matched accepted gross master, zero mismatches** |
| External AQUASTAT benchmark | Notebook | Source-version and independent benchmark analysis not part of this V1 numerical-pass claim |

## V1 execution and validation

```powershell
python -m unittest discover -s tests -v
python run-iwr.py --check --data-root data
python run-iwr.py --execute --data-root data --output-root runs/replay-01
```

Evidence is saved under `docs/qc/gross-reference-comparison.json`, and the intended original inputs are named in `docs/input-manifest.csv`. The reconstructed gross output is a **scientific numerical replay**, not a byte-for-byte reproduction of every original metadata field.

The full accepted B2/D1/D2/D3 route-selection decisions and historical evidence should be preserved from the private original research notebooks; they must not be replaced with unverified generic proxy rules. Source data are kept local unless redistribution rights are established.

## Scientific source and scenario-use clarifications

The system-share sources are Jägermeyr et al. (2015, Supplement Table S1) and Rohwer et al. (2007, Annex A/IFT). The final efficiencies (0.42, 0.7125, 0.855) are **selected application × conveyance assumptions**, not direct observed efficiencies for 179 countries. Their detailed attribution is in [`irrigation-technology-sources.md`](irrigation-technology-sources.md). The RCP26/RCP60 scientific output layers should not be described as two already deployed FABLE-C scenario inputs.
