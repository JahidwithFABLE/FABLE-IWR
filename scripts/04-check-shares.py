#!/usr/bin/env python3
"""Check approved country-year technology shares and delivery efficiencies."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

SHARES = ['surface_share','sprinkler_share','drip_share']
EFFICIENCIES = {'surface':0.42,'sprinkler':0.7125,'drip':0.855}


def check_shares(df, expected_rows=824):
    keys=['country_iso3','year']
    missing=set(keys+SHARES)-set(df.columns)
    if missing:raise ValueError(f'Missing share fields: {sorted(missing)}')
    if df[keys].isna().any().any() or df.duplicated(keys).any():raise ValueError('Duplicate/null country-year technology keys')
    values=df[SHARES].apply(pd.to_numeric,errors='raise').to_numpy(float)
    if not np.isfinite(values).all() or np.any(values < 0) or np.any(values > 1):
        raise ValueError('Nonfinite or out-of-range technology shares')
    if not np.allclose(values.sum(axis=1),1.0,atol=5e-3,rtol=0):
        raise ValueError('Some approved technology shares fail sum-to-one tolerance 0.005')
    if expected_rows is not None and len(df)!=expected_rows:raise ValueError(f'Expected {expected_rows} technology rows, got {len(df)}')
    return {'rows':len(df),'countries':int(df.country_iso3.nunique()),'duplicate_keys':0,'share_sum_status':'PASS'}


def efficiency_values(df):
    req=['technology','final_delivery_efficiency']
    missing=set(req)-set(df.columns)
    if missing:raise ValueError(f'Missing efficiency fields: {sorted(missing)}')
    values=df.set_index('technology')['final_delivery_efficiency']
    if values.index.duplicated().any():raise ValueError('Duplicate efficiency systems')
    for system,expected in EFFICIENCIES.items():
        if system not in values.index or not np.isclose(float(values[system]), expected, atol=1e-12,rtol=0):
            raise ValueError(f'Unexpected {system} efficiency; scientific re-approval needed')
    return {system:float(values[system]) for system in EFFICIENCIES}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--shares',type=Path,required=True)
    p.add_argument('--efficiencies',type=Path,required=True)
    p.add_argument('--allow-other-count',action='store_true')
    a=p.parse_args()
    report=check_shares(pd.read_csv(a.shares), None if a.allow_other_count else 824)
    report['efficiencies']=efficiency_values(pd.read_csv(a.efficiencies))
    print(json.dumps(report,indent=2))
    print('STATUS: PASS_APPROVED_TECHNOLOGY_EVIDENCE_QC')

if __name__ == '__main__':main()
