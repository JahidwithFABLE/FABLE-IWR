# Scientific source lineage

The package was reconstructed from the archived original research notebooks under `Water_balance/` and `PIRRWW/`, not by designing a new crop water model. These original notebooks are retained outside the public repository.

| Original notebook | Scientific role | GitHub counterpart |
| --- | --- | --- |
| `PIRRWW/FINAL/3 script for downloading data.ipynb` and `.../Script for downloading data from ISIMIP.ipynb` | ISIMIP acquisition, request validation and processing context | `tools/download-isimip.py` provides manifest-driven acquisition; **not** full original API query replay |
| `Water requirement dataset/01_build_global_irrigation_system_dataset_FINAL.ipynb.ipynb` | Jägermeyr/Rohwer share anchors, interpolation, source QC | `scripts/02-system-shares.py`, based on original notebook operations |
| `Water requirement dataset/2 Script for preparing FABLE crop water requirement data.ipynb` | LPJmL harmonization, published crop analogues, robust route selection, Cell 109 accepted route and Cells 111–117 final release | `tools/rebuild-net-routes.py`, accepted net checks and gross calculations; original route-selection logic **not** replaced |
| `Water requirement dataset/5 QC and finding problem.ipynb` | Target route and temporal/spatial coverage diagnostics | Documented scientific QC decisions; not condensed into a new unverified model |
| `Water requirement dataset/6 Script for final FABLE crop irrigation water requirement dataset .ipynb` | Additional crop-coverage and external source decision process | Remains in research archive pending independent replay |
| `Water requirement dataset/8 after finding problem with data sept 16.ipynb` | Repair of incomplete IWR country-product-year states and downstream SPAM/FABLE consistency | Kept separate from the accepted 29,338-row crop-water requirement master; must not silently substitute its Dataset A for the later final route master |
| `PIRRWW/QC_ISIMIP2b_pirrww_LPJmL_GEPIC_PEPIC.ipynb` | Multimodel diagnostics | Evidence provenance, not a gross efficiency calculation |

**Important chronology:** `8 after finding problem with data sept 16.ipynb` contains a *Dataset A* with a different release purpose and schema. The 29,338-row crop requirement and 89-column gross master are associated with the later final release cells 111–117 of the main crop-water-requirement notebook. Do not merge these workflows only because the subject names are similar.

Do not upload entire unreviewed Jupyter development histories to a public repository without checking hard-coded local paths, provider downloads, credentials, organizational data, outputs and redistribution permissions.

## Irrigation technology citations and local inputs

Original share processing is in `Water_balance/Water requirement dataset/01_build_global_irrigation_system_dataset_FINAL.ipynb.ipynb`: Rohwer, Gerten & Lucht (2007) Annex A / functional irrigation types for the earlier model anchor, and Jägermeyr et al. (2015) Supplement Table S1 for the later reference anchor. The first two local prepared source files are `01_global_irrigation_system_source_jagermeyr2015.csv` and `02_global_rohwer_irrigation_reference.csv` (see `docs/input-manifest.csv`). The accepted final share and efficiency files derive from Cells 112–114 of the main original IWR notebook; the source-derived intermediate share series is not identical to the approved final 824 rows by assumption. Full explanation and references: [`irrigation-technology-sources.md`](irrigation-technology-sources.md).
