#!/usr/bin/env python3
"""Check and optionally copy original IWR inputs without modifying the originals.

Use a Windows source root corresponding to C:/FABLE_JAHID/WORK/Data.
Only explicitly named files are copied; raw ISIMIP trees remain local.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs' / 'input-manifest.csv'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def gather(source_root: Path, data_root: Path, mode: str = 'quick',
           copy: bool = False, hash_files: bool = False) -> list[dict]:
    with MANIFEST.open(newline='', encoding='utf-8') as handle:
        items = list(csv.DictReader(handle))
    report = []
    for entry in items:
        if entry['acquisition'] == 'export_from_session':
            state = 'REQUIRES_ORIGINAL_NOTEBOOK_EXPORT'
            report.append({**entry, 'status':state,'source_exists':False})
            continue
        if entry['acquisition'] == 'directory_or_manifest':
            state='MANUAL_BULK_SOURCE_CHECK'
            report.append({**entry,'status':state,'source_exists':False})
            continue
        if mode == 'quick' and entry['tier'] not in {'release','baseline'}:
            continue
        relative=Path(*entry['original_relative_path'].replace('\\','/').split('/'))
        src=source_root/relative
        variants=[src]
        if src.name.endswith('.csv.gz'):
            variants.append(src.with_suffix(''))
        elif src.suffix == '.csv':
            variants.append(Path(str(src)+'.gz'))
        found=next((x for x in variants if x.is_file()),None)
        dest=data_root/entry['destination']
        if found and found.name != src.name:
            dest=dest.with_suffix('') if found.suffix=='.csv' else Path(str(dest)+'.gz')
        status='FOUND' if found else 'MISSING'
        if found and dest.exists():
            status='ALREADY_PRESENT' if found.stat().st_size==dest.stat().st_size else 'DESTINATION_CONFLICT'
        elif found and copy:
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(found,dest)
            status='COPIED'
        row={**entry,'status':status,'source_exists':bool(found),
             'source':str(found or src),'destination_resolved':str(dest),
             'bytes':found.stat().st_size if found else None}
        if found and hash_files:
            row['sha256_source']=sha256(found)
            if dest.exists():
                row['sha256_destination']=sha256(dest)
                if row['sha256_source'] != row['sha256_destination']:
                    row['status']='HASH_MISMATCH'
        report.append(row)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path,required=True,
                   help='Original C:/FABLE_JAHID/WORK/Data directory')
    p.add_argument('--data-root',type=Path,default=ROOT/'data')
    p.add_argument('--mode',choices=['quick','full'],default='quick')
    p.add_argument('--copy',action='store_true',help='Opt-in copy; never overwrites')
    p.add_argument('--hash',action='store_true')
    p.add_argument('--report',type=Path,default=ROOT/'runs'/'input-collection.json')
    a=p.parse_args()
    if a.report.exists():raise FileExistsError(a.report)
    rows=gather(a.source_root,a.data_root,a.mode,a.copy,a.hash)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    summary={s:sum(x['status']==s for x in rows) for s in sorted(set(x['status'] for x in rows))}
    print(json.dumps({'summary':summary,'report':str(a.report)},indent=2))
    if any(x['status'] in {'HASH_MISMATCH','DESTINATION_CONFLICT'} for x in rows):
        raise SystemExit(2)

if __name__=='__main__':main()
