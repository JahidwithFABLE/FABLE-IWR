#!/usr/bin/env python3
"""Rebuild net-water numerical columns from an approved Cell-109 route layer.

This is not the source-selection model. Accepted route values, confidence and
area support must be generated/approved upstream using the research workflow.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED=['target_crop','country_iso3','year','pathway','SPAM_irrigated_area_ha',
          'route_value_mm_yr','route_group','route_type','confidence','semantic_status','final_value_available']
KEY=['country_iso3','fable_product','year','pathway']


def rebuild(routes):
    missing=set(REQUIRED)-set(routes.columns)
    if missing:raise ValueError(f'Accepted route fields missing: {sorted(missing)}')
    out=routes[REQUIRED].rename(columns={'target_crop':'fable_product','route_value_mm_yr':'water_requirement_mm_yr'}).copy()
    out['country_iso3']=out.country_iso3.astype(str).str.strip().str.upper()
    out['fable_product']=out.fable_product.astype(str).str.strip().str.lower()
    out['year']=pd.to_numeric(out.year,errors='raise').astype(int)
    out['water_requirement_mm_yr']=pd.to_numeric(out.water_requirement_mm_yr,errors='raise')
    out['SPAM_irrigated_area_ha']=pd.to_numeric(out.SPAM_irrigated_area_ha,errors='raise')
    if out.duplicated(KEY).any() or out[KEY].isna().any().any():raise ValueError('Non-unique/null accepted route keys')
    if not np.isfinite(out[['water_requirement_mm_yr','SPAM_irrigated_area_ha']].to_numpy(float)).all():
        raise ValueError('Missing/non-finite accepted values')
    if (out[['water_requirement_mm_yr','SPAM_irrigated_area_ha']]<0).any().any():
        raise ValueError('Negative requirement or irrigated area')
    out['water_requirement_m3_ha_yr']=out.water_requirement_mm_yr*10.0
    out['total_requirement_m3_before_system_losses']=out.water_requirement_m3_ha_yr*out.SPAM_irrigated_area_ha
    out['total_requirement_Mm3_before_system_losses']=out.total_requirement_m3_before_system_losses/1e6
    out['direct_target_LPJmL_simulation']=out.route_group.eq('DIRECT_LPJML')
    out['uses_proxy_or_harmonisation']=~out.direct_target_LPJmL_simulation
    out['geographic_completion_used']=out.route_group.astype(str).str.startswith(('GEOGRAPHIC_COMPLETION_','RUBBER_FINAL_F2','RUBBER_FINAL_F3'))
    out['irrigation_technology_adjusted']=False
    out['system_efficiency_applied']=False
    out['water_availability_constrained']=False
    out['requirement_semantic']='FABLE_HARMONISED_CROP_IRRIGATION_REQUIREMENT_ON_LPJML_PIRRWW_COMPATIBLE_SCALE_BEFORE_EXTERNAL_IRRIGATION_SYSTEM_LOSSES'
    return out.sort_values(KEY).reset_index(drop=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--routes',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--small-test',action='store_true')
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    out=rebuild(pd.read_csv(a.routes))
    if not a.small_test and len(out)!=29338:raise ValueError(f'Expected 29,338 accepted route states, got {len(out):,}')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.output,index=False)
    print(f'ACCEPTED_NET_NUMERIC_REBUILT: rows={len(out):,} output={a.output}')
    print('Full original scientific master metadata is not replayed by this compact code.')

if __name__=='__main__':main()
