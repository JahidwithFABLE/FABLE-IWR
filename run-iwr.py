#!/usr/bin/env python3
"""Run an accepted-evidence IWR numerical replay in a new, isolated folder."""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def run(script,*args):
    cmd=[sys.executable,str(ROOT/'scripts'/script),*map(str,args)]
    print('\n$', ' '.join(cmd), flush=True)
    subprocess.run(cmd,check=True)


def choose(root,filename):
    a=root/filename
    options=[a, Path(str(a).replace('.csv.gz','.csv'))] if a.name.endswith('.csv.gz') else [a,Path(str(a)+'.gz')]
    for path in options:
        if path.is_file():return path
    raise FileNotFoundError(f'Missing accepted input: {a}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root',type=Path,default=ROOT/'data')
    p.add_argument('--output-root',type=Path,default=ROOT/'runs'/'accepted-evidence-replay')
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--check',action='store_true')
    group.add_argument('--execute',action='store_true')
    a=p.parse_args()
    net=choose(a.data_root,'crop/01_FABLE_crop_water_requirement_master_2000_2020_FINAL.csv.gz')
    shares=choose(a.data_root,'technology/12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv')
    eff=choose(a.data_root,'technology/13_FABLE_irrigation_efficiency_parameters_FINAL.csv')
    run('01-check-inputs.py','--data-root',a.data_root)
    run('03-check-net.py','--net',net)
    run('04-check-shares.py','--shares',shares,'--efficiencies',eff)
    if a.check:
        print('STATUS: PASS_IWR_PREPARED_EVIDENCE_PREFLIGHT_ONLY')
        return
    if a.output_root.exists() and any(a.output_root.iterdir()):
        raise FileExistsError(f'Use an empty, separate output root: {a.output_root}')
    run('05-build-withdrawal.py','--net',net,'--shares',shares,'--efficiencies',eff,
        '--output-root',a.output_root)
    ref=a.data_root/'reference'/'09_FABLE_gross_irrigation_withdrawal_requirement_master_2000_2020_FINAL.csv.gz'
    if not ref.is_file():ref=ref.with_suffix('')
    if not ref.is_file():
        print('STATUS: GROSS_NUMERIC_BUILT_REFERENCE_NOT_COMPARED')
        print('Provide the saved 09_FABLE gross master under data/reference/ to verify numerical equality.')
        return
    run('06-compare-release.py','--fresh',a.output_root/'gross-master.csv.gz','--reference',ref,
        '--report',a.output_root/'numeric-reference-comparison.json')
    print('STATUS: PASS_IWR_ACCEPTED_EVIDENCE_NUMERIC_REPLAY_REFERENCE_MATCH')

if __name__=='__main__': main()
