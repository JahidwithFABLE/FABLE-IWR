#!/usr/bin/env python3
"""Check source and accepted-evidence inputs without writing scientific data."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

INPUTS = {
    'jagermeyr': 'technology/01_global_irrigation_system_source_jagermeyr2015.csv',
    'rohwer': 'technology/02_global_rohwer_irrigation_reference.csv',
    'net_master': 'crop/01_FABLE_crop_water_requirement_master_2000_2020_FINAL.csv.gz',
    'approved_shares': 'technology/12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv',
    'efficiencies': 'technology/13_FABLE_irrigation_efficiency_parameters_FINAL.csv',
}


def locate(root: Path, rel: str) -> Path:
    path = root / rel
    alternatives = [path]
    if path.name.endswith('.csv.gz'):
        alternatives.append(path.with_suffix(''))
    elif path.name.endswith('.csv'):
        alternatives.append(Path(str(path)+'.gz'))
    return next((p for p in alternatives if p.is_file()), path)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(4*1024*1024), b''):
            h.update(part)
    return h.hexdigest()


def inspect(root: Path) -> dict:
    records = {}
    for key, relative in INPUTS.items():
        path = locate(root, relative)
        rec = {'path': str(path), 'available': path.is_file()}
        if path.is_file():
            rec['sha256'] = digest(path)
            rec['columns'] = list(pd.read_csv(path, nrows=0).columns)
        records[key] = rec
    return records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root', type=Path, required=True)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    records = inspect(args.data_root)
    print(json.dumps(records, indent=2))
    if args.report:
        if args.report.exists():
            raise FileExistsError(args.report)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(records, indent=2), encoding='utf-8')
    # Raw technology inputs are only needed for optional standalone source rebuild.
    required = ('net_master', 'approved_shares', 'efficiencies')
    missing = [name for name in required if not records[name]['available']]
    if missing:
        raise SystemExit(f'MISSING_REQUIRED_ACCEPTED_EVIDENCE: {missing}')
    print('STATUS: PASS_IWR_ACCEPTED_EVIDENCE_PREFLIGHT_ONLY')

if __name__ == '__main__':
    main()
