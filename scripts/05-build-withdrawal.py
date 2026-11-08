#!/usr/bin/env python3
"""Recalculate gross withdrawal science from approved net master and technology evidence.

Outputs are a numeric reconstruction, not a byte-identical 89-column original
release. Route selection and country-year share completion remain upstream.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

# These two stages use filenames with hyphens; source import keeps the public names concise.
CHECK_DIR=Path(__file__).resolve().parent
import importlib.util

def read_stage(filename):
    spec=importlib.util.spec_from_file_location(filename.replace('-','_'), CHECK_DIR / filename)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

netcheck=read_stage('03-check-net.py')
sharecheck=read_stage('04-check-shares.py')

KEYS=['country_iso3','year']
CALCULATOR=['country_iso3','year','fable_product','water_requirement_mm_yr',
  'water_requirement_m3_ha_yr','surface_share','sprinkler_share','drip_share',
  'surface_efficiency','sprinkler_efficiency','drip_efficiency',
  'gross_withdrawal_multiplier','composite_delivery_efficiency',
  'gross_irrigation_withdrawal_requirement_mm_yr',
  'gross_irrigation_withdrawal_requirement_m3_ha_yr',
  'additional_delivery_requirement_mm_yr','additional_delivery_requirement_m3_ha_yr',
  'route_group','confidence','technology_resolution_route','technology_completion_confidence']


def compute(net:pd.DataFrame, shares:pd.DataFrame, eff:dict, expected=True)->pd.DataFrame:
    netcheck.validate(net, 29338 if expected else None)
    sharecheck.check_shares(shares, 824 if expected else None)
    fields=KEYS+['surface_share','sprinkler_share','drip_share']
    for optional in ['country','technology_resolution_route','technology_completion_confidence']:
        if optional in shares.columns:fields.append(optional)
    out=net.merge(shares[fields],on=KEYS,how='left',validate='many_to_one',indicator='_technology_match')
    if not out['_technology_match'].eq('both').all():
        missing=out.loc[out['_technology_match'].ne('both'),KEYS].drop_duplicates().head(15)
        raise ValueError(f'Technology shares missing for crop states: {missing.to_dict("records")}')
    out=out.drop(columns='_technology_match')
    for s in ['surface','sprinkler','drip']:
        out[f'{s}_efficiency']=eff[s]
    out['gross_withdrawal_multiplier']=sum(out[f'{s}_share']/eff[s] for s in eff)
    out['composite_delivery_efficiency']=1/out['gross_withdrawal_multiplier']
    for s in eff:
        out[f'gross_{s}_mm_yr']=out['water_requirement_mm_yr']*out[f'{s}_share']/eff[s]
        out[f'gross_{s}_m3_ha_yr']=out[f'gross_{s}_mm_yr']*10.0
        out[f'gross_{s}_m3']=out[f'gross_{s}_m3_ha_yr']*out['SPAM_irrigated_area_ha']
        out[f'gross_{s}_Mm3']=out[f'gross_{s}_m3']/1e6
    out['gross_withdrawal_mm_yr']=sum(out[f'gross_{s}_mm_yr'] for s in eff)
    out['gross_withdrawal_m3_ha_yr']=out['gross_withdrawal_mm_yr']*10
    out['net_crop_requirement_m3']=out['water_requirement_m3_ha_yr']*out['SPAM_irrigated_area_ha']
    out['gross_withdrawal_m3']=out['gross_withdrawal_m3_ha_yr']*out['SPAM_irrigated_area_ha']
    out['net_crop_requirement_Mm3']=out['net_crop_requirement_m3']/1e6
    out['gross_withdrawal_Mm3']=out['gross_withdrawal_m3']/1e6
    out['system_loss_equivalent_mm_yr']=out['gross_withdrawal_mm_yr']-out['water_requirement_mm_yr']
    out['system_loss_equivalent_m3_ha_yr']=out['gross_withdrawal_m3_ha_yr']-out['water_requirement_m3_ha_yr']
    out['system_loss_equivalent_m3']=out['gross_withdrawal_m3']-out['net_crop_requirement_m3']
    out['system_loss_equivalent_Mm3']=out['system_loss_equivalent_m3']/1e6
    # Cell 116 terminology: these are additional delivery requirements, not consumptive loss.
    for tail in ['mm_yr','m3_ha_yr','m3','Mm3']:
        out[f'additional_delivery_requirement_{tail}']=out[f'system_loss_equivalent_{tail}']
    out['gross_irrigation_withdrawal_requirement_mm_yr']=out['gross_withdrawal_mm_yr']
    out['gross_irrigation_withdrawal_requirement_m3_ha_yr']=out['gross_withdrawal_m3_ha_yr']
    out['gross_irrigation_withdrawal_requirement_Mm3']=out['gross_withdrawal_Mm3']
    out['gross_requirement_status']='UNCONSTRAINED_REQUIREMENT'
    out['observed_withdrawal']=False
    out['water_availability_applied']=False
    out['return_flow_modelled']=False
    if not np.allclose(out['gross_withdrawal_mm_yr'],out['water_requirement_mm_yr']*out['gross_withdrawal_multiplier'],atol=1e-9,rtol=1e-12):
        raise ValueError('Independent multiplier identity failed')
    if (out['gross_withdrawal_mm_yr']+1e-8 < out['water_requirement_mm_yr']).any():
        raise ValueError('Gross requirement unexpectedly below net requirement')
    return out


def safe_write(df, path):
    if path.exists():raise FileExistsError(f'Refusing to overwrite: {path}')
    path.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(path,index=False)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--net',type=Path,required=True)
    p.add_argument('--shares',type=Path,required=True)
    p.add_argument('--efficiencies',type=Path,required=True)
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--small-test',action='store_true',help='Disable publication row-count gates for synthetic tests only')
    a=p.parse_args()
    eff=sharecheck.efficiency_values(pd.read_csv(a.efficiencies))
    out=compute(pd.read_csv(a.net),pd.read_csv(a.shares),eff,expected=not a.small_test)
    root=a.output_root
    products={
        'gross-master.csv.gz':out,
        'gross-RCP26.csv':out.loc[out.pathway.eq('RCP26'),[c for c in CALCULATOR if c in out.columns]].copy(),
        'gross-RCP60.csv':out.loc[out.pathway.eq('RCP60'),[c for c in CALCULATOR if c in out.columns]].copy(),
    }
    if not a.small_test and (len(products['gross-RCP26.csv'])!=14669 or len(products['gross-RCP60.csv'])!=14669):
        raise ValueError('Expected 14,669 country-crop-year states per pathway')
    if any((root/f).exists() for f in products):
        raise FileExistsError('Existing output file found; use a new --output-root')
    for name,table in products.items():
        safe_write(table,root/name)
    print(json.dumps({'rows':len(out),'countries':out.country_iso3.nunique(),
      'products':out.fable_product.nunique(),'pathways':out.pathway.value_counts().to_dict(),
      'output_root':str(root),'scope':'accepted-evidence numerical reconstruction'},indent=2))
    print('STATUS: PASS_GROSS_NUMERIC_RECONSTRUCTION_NOT_FULL_SOURCE_REPLAY')

if __name__=='__main__':main()
