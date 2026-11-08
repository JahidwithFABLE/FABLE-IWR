#!/usr/bin/env python3
"""Replay original Cell 113: complete required country-year irrigation shares.

Use valid source composition first, then nearest same-country year (mean on a
symmetric tie), then >=2 complete same-year pre-specified regional peers.
The code does not invent a technology split when evidence is missing.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

COLS = ['surface_share','sprinkler_share','drip_share']
KEYS = ['country_iso3','year']


def prepare_source(source: pd.DataFrame) -> pd.DataFrame:
    source = source.copy()
    if 'country_iso3' not in source and 'iso3' in source:
        source = source.rename(columns={'iso3':'country_iso3'})
    missing = set(KEYS+COLS)-set(source)
    if missing:raise ValueError(f'Missing source columns: {sorted(missing)}')
    source['country_iso3'] = source.country_iso3.astype(str).str.strip().str.upper()
    source['year'] = pd.to_numeric(source.year,errors='raise').astype(int)
    if source.duplicated(KEYS).any():raise ValueError('Non-unique source country-year keys')
    for col in COLS:source[col] = pd.to_numeric(source[col],errors='coerce')
    vals = source[COLS].to_numpy(float)
    source['is_complete'] = (np.isfinite(vals).all(axis=1) &
        (vals>=0).all(axis=1) & (vals<=1).all(axis=1) &
        np.isclose(vals.sum(axis=1),1.0,atol=0.005,rtol=0))
    return source


def complete(required: pd.DataFrame, source: pd.DataFrame, peers: pd.DataFrame,
             min_peers: int = 2) -> pd.DataFrame:
    missing = set(KEYS)-set(required)
    if missing:raise ValueError(f'Missing required keys: {sorted(missing)}')
    base = required[KEYS].drop_duplicates().copy()
    base['year'] = pd.to_numeric(base.year,errors='raise').astype(int)
    base['country_iso3'] = base.country_iso3.astype(str).str.strip().str.upper()
    if base[KEYS].isna().any().any():raise ValueError('Null required country-year key')
    source=prepare_source(source)
    if peers.duplicated('target_country_iso3').any():raise ValueError('Duplicate frozen peer assignments')
    peer_lookup=peers.set_index('target_country_iso3')
    complete_source=source[source.is_complete]
    results=[]
    for r in base.sort_values(KEYS).itertuples(index=False):
        iso,year=r.country_iso3,int(r.year)
        same=complete_source[(complete_source.country_iso3==iso)&(complete_source.year==year)]
        route='SOURCE_COMPLETE'
        confidence='SOURCE_RECORDED'
        donor_years=str(year)
        donors=iso
        if not same.empty:
            vec=same.iloc[0][COLS].to_numpy(float)
        else:
            alt=complete_source[complete_source.country_iso3==iso].copy()
            if not alt.empty:
                delta=(alt.year-year).abs()
                tied=alt[delta==delta.min()]
                vec=tied[COLS].mean(axis=0).to_numpy(float)
                donor_years=';'.join(map(str,sorted(tied.year.tolist())))
                route='R1_SAME_COUNTRY_NEAREST_VALID_YEAR'
                confidence='LOW'
            else:
                if iso not in peer_lookup.index:
                    raise ValueError(f'No approved regional peer definition for unresolved {iso} {year}')
                peers_for_country=str(peer_lookup.loc[iso,'peer_countries']).split(';')
                relevant=complete_source[(complete_source.year==year)&
                    complete_source.country_iso3.isin(peers_for_country)]
                if relevant.country_iso3.nunique()<min_peers:
                    raise ValueError(f'Insufficient approved complete same-year peers for {iso} {year}')
                vec=relevant[COLS].mean(axis=0).to_numpy(float)
                donors=';'.join(sorted(relevant.country_iso3.tolist()))
                donor_years=str(year)
                route='R2_SAME_YEAR_REGIONAL_PEER_MEAN'
                confidence='VERY_LOW'
        if not(np.isfinite(vec).all() and (vec>=-1e-10).all() and
               np.isclose(vec.sum(),1.0,atol=0.005,rtol=0)):
            raise ValueError(f'Invalid completed composition for {iso} {year}: {vec}')
        results.append(dict(zip(COLS,vec))|{'country_iso3':iso,'year':year,
            'technology_resolution_route':route,'technology_completion_confidence':confidence,
            'technology_donor_countries':donors,'technology_donor_years':donor_years})
    return pd.DataFrame(results).sort_values(KEYS).reset_index(drop=True)


def compare_reference(rebuilt:pd.DataFrame,approved:pd.DataFrame)->dict:
    approved=prepare_source(approved)
    merged=rebuilt.merge(approved,on=KEYS,how='outer',suffixes=('_new','_accepted'),indicator=True)
    bycol={}
    for col in COLS:
        both=merged['_merge'].eq('both').to_numpy()
        a=pd.to_numeric(merged[f'{col}_new'],errors='coerce').to_numpy(float)
        b=pd.to_numeric(merged[f'{col}_accepted'],errors='coerce').to_numpy(float)
        bycol[col]=int(np.count_nonzero(both & ~np.isclose(a,b,atol=1e-9,rtol=1e-9,equal_nan=True)))
    result={'rebuilt_rows':len(rebuilt),'approved_rows':len(approved),
            'missing_or_extra_keys':int(merged['_merge'].ne('both').sum()),
            'mismatches':bycol}
    result['status']='MATCH' if result['missing_or_extra_keys']==0 and not any(bycol.values()) else 'MISMATCH'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--net',type=Path,required=True)
    p.add_argument('--source-shares',type=Path,required=True)
    p.add_argument('--peers',type=Path,default=Path(__file__).resolve().parents[1]/'config'/'technology-peers.csv')
    p.add_argument('--reference',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    required=pd.read_csv(args.net,usecols=KEYS)
    out=complete(required,pd.read_csv(args.source_shares),pd.read_csv(args.peers))
    if len(out)!=824:raise ValueError(f'Expected 824 FABLE-required technology rows, got {len(out)}')
    evidence={'rows':len(out),'methods':out.technology_resolution_route.value_counts().to_dict()}
    if args.reference:
        evidence['reference_comparison']=compare_reference(out,pd.read_csv(args.reference))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(args.output,index=False)
    if args.report:
        if args.report.exists():raise FileExistsError(args.report)
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(evidence,indent=2))
    print(json.dumps(evidence,indent=2))
    if args.reference and evidence['reference_comparison']['status']!='MATCH':raise SystemExit(1)

if __name__=='__main__':main()
