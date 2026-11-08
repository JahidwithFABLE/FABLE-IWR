#!/usr/bin/env python3
"""QC the accepted net crop-requirement master (scientific route selection is upstream)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

KEYS = ['country_iso3','fable_product','year','pathway']
REQUIRED = KEYS + ['water_requirement_mm_yr','water_requirement_m3_ha_yr','SPAM_irrigated_area_ha']


def validate(df: pd.DataFrame, expected_rows: int | None = 29338) -> dict:
    missing = sorted(set(REQUIRED)-set(df.columns))
    if missing: raise ValueError(f'Missing net master fields: {missing}')
    if df[KEYS].isna().any().any() or df.duplicated(KEYS).any():
        raise ValueError('Null or duplicated net master keys')
    v = df[['water_requirement_mm_yr','water_requirement_m3_ha_yr','SPAM_irrigated_area_ha']].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(v.to_numpy(dtype=float)).all() or (v < 0).any().any():
        raise ValueError('Net master has missing, negative or non-finite scientific values')
    if not np.allclose(v['water_requirement_m3_ha_yr'],v['water_requirement_mm_yr']*10,atol=1e-7,rtol=1e-10):
        raise ValueError('mm/year to m³/ha/year conversion differs from ×10')
    report = {'rows':len(df),'countries':int(df.country_iso3.nunique()),'products':int(df.fable_product.nunique()),
              'years':sorted(int(i) for i in df.year.unique()),'pathways':sorted(df.pathway.astype(str).unique().tolist()),
              'expected_rows':expected_rows,'expected_rows_match': expected_rows is None or len(df)==expected_rows}
    if expected_rows is not None and len(df)!=expected_rows:
        raise ValueError(f'Expected {expected_rows:,} net states, found {len(df):,}')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--net',type=Path,required=True)
    p.add_argument('--report',type=Path)
    p.add_argument('--allow-other-count',action='store_true',help='Use only for small test input, not release validation')
    a=p.parse_args()
    report=validate(pd.read_csv(a.net), None if a.allow_other_count else 29338)
    print(json.dumps(report,indent=2))
    if a.report:
        if a.report.exists():raise FileExistsError(a.report)
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('STATUS: PASS_ACCEPTED_NET_MASTER_NUMERIC_QC')

if __name__ == '__main__':main()
