#!/usr/bin/env python3
"""Numerically compare reconstructed gross-withdrawal columns to validated master.

Only shared scientific fields are compared. Original provenance fields not
reproduced by this shorter code are explicitly not claimed to be regenerated.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

KEYS=['country_iso3','year','fable_product','pathway']
FIELDS=[
 'water_requirement_mm_yr','water_requirement_m3_ha_yr','SPAM_irrigated_area_ha',
 'surface_share','sprinkler_share','drip_share',
 'surface_efficiency','sprinkler_efficiency','drip_efficiency',
 'gross_withdrawal_multiplier','composite_delivery_efficiency',
 'gross_surface_mm_yr','gross_sprinkler_mm_yr','gross_drip_mm_yr',
 'gross_withdrawal_mm_yr','gross_withdrawal_m3_ha_yr',
 'gross_surface_m3_ha_yr','gross_sprinkler_m3_ha_yr','gross_drip_m3_ha_yr',
 'gross_surface_m3','gross_sprinkler_m3','gross_drip_m3',
 'gross_withdrawal_m3','gross_withdrawal_Mm3',
 'net_crop_requirement_m3','net_crop_requirement_Mm3',
 'additional_delivery_requirement_mm_yr','additional_delivery_requirement_m3_ha_yr',
 'additional_delivery_requirement_m3','additional_delivery_requirement_Mm3',
 'gross_irrigation_withdrawal_requirement_mm_yr',
 'gross_irrigation_withdrawal_requirement_m3_ha_yr',
 'gross_irrigation_withdrawal_requirement_Mm3',
]

def compare(fresh,reference):
    for label,d in [('reconstructed',fresh),('reference',reference)]:
        missing=set(KEYS)-set(d.columns)
        if missing:raise ValueError(f'{label} missing key columns {sorted(missing)}')
        if d[KEYS].isna().any().any() or d.duplicated(KEYS).any():
            raise ValueError(f'{label} has duplicate or missing keys')
    common=[c for c in FIELDS if c in fresh.columns and c in reference.columns]
    if len(common)<10:raise ValueError(f'Too few comparable scientific fields: {common}')
    a=fresh[KEYS+common].merge(reference[KEYS+common],on=KEYS,how='outer',suffixes=('_fresh','_reference'),indicator=True,validate='one_to_one')
    missing_keys=int(a['_merge'].ne('both').sum())
    errs={}
    for col in common:
        l=pd.to_numeric(a[f'{col}_fresh'],errors='coerce').to_numpy(float)
        r=pd.to_numeric(a[f'{col}_reference'],errors='coerce').to_numpy(float)
        eq=np.isclose(l,r,atol=1e-6,rtol=1e-9,equal_nan=True)
        mismatch=int((~eq & a['_merge'].eq('both').to_numpy()).sum())
        errs[col]=mismatch
    result={'fresh_rows':len(fresh),'reference_rows':len(reference),
            'missing_or_extra_keys':missing_keys,'scientific_fields_compared':len(common),
            'fields_not_comparable':sorted(set(FIELDS)-set(common)),
            'mismatch_counts':errs,'mismatched_fields':{k:v for k,v in errs.items() if v},
            'status':'PASS_SHARED_NUMERIC_REFERENCE_MATCH' if missing_keys==0 and max(errs.values(),default=0)==0 else 'FAIL_NUMERIC_REFERENCE_MISMATCH',
            'scope':'shared numeric fields only; full original provenance/route selection not replayed'}
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fresh',type=Path,required=True)
    p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    report=compare(pd.read_csv(a.fresh,low_memory=False),pd.read_csv(a.reference,low_memory=False))
    print(json.dumps(report,indent=2))
    if a.report:
        if a.report.exists():raise FileExistsError(a.report)
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(report,indent=2),encoding='utf-8')
    if report['status'].startswith('FAIL'):raise SystemExit(1)
    print('STATUS:',report['status'])

if __name__=='__main__':main()
