#!/usr/bin/env python3
"""Download files from an approved ISIMIP URL manifest, with checksum audit.

Manifest columns: url, filename, sha256 (sha256 optional, but recommended).
The original ISIMIP queries must be documented when preparing the manifest.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
from pathlib import Path
from urllib.parse import urlparse
import requests


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(4*1024*1024),b''):h.update(part)
    return h.hexdigest()


def valid_manifest(path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not {'url','filename'}.issubset(reader.fieldnames or []):
            raise ValueError('Manifest must contain url and filename columns')
        items=list(reader)
    if not items:raise ValueError('Empty download manifest')
    seen=set()
    for row in items:
        parsed=urlparse(row['url'].strip())
        if parsed.scheme!='https' or not parsed.netloc:
            raise ValueError(f'Use an approved HTTPS source URL: {row["url"]}')
        name=row['filename'].strip()
        if not name or Path(name).name!=name or name in seen:
            raise ValueError(f'Invalid or duplicate destination filename: {name!r}')
        seen.add(name)
        sha=(row.get('sha256') or '').strip().lower()
        if sha and (len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha)):
            raise ValueError(f'Invalid SHA256 for {name}')
    return items


def download(row, folder):
    dest=folder/row['filename'].strip()
    expected=(row.get('sha256') or '').strip().lower()
    if dest.is_file():
        got=digest(dest)
        if expected and got!=expected:raise ValueError(f'Existing {dest} checksum mismatch')
        print(f'EXISTS {dest.name} SHA256={got}');return
    part=dest.with_name(dest.name+'.part')
    if part.exists():raise FileExistsError(f'Partial file already exists: {part}')
    with requests.get(row['url'].strip(),stream=True,timeout=(20,120)) as r:
        r.raise_for_status()
        with part.open('wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:f.write(chunk)
    got=digest(part)
    if expected and got!=expected:
        part.unlink()
        raise ValueError(f'SHA256 mismatch for {dest.name}; source may have changed')
    part.rename(dest)
    print(f'DOWNLOADED {dest.name} SHA256={got}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output-root',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--check',action='store_true')
    group.add_argument('--execute',action='store_true')
    a=p.parse_args()
    rows=valid_manifest(a.manifest)
    print(f'Approved ISIMIP manifest: {len(rows)} files')
    if a.check:
        for r in rows:print(r['filename'],r['url'])
        print('STATUS: PASS_DOWNLOAD_MANIFEST_PREFLIGHT_ONLY')
        return
    a.output_root.mkdir(parents=True,exist_ok=True)
    for row in rows:download(row,a.output_root)
    print('STATUS: PASS_DOWNLOADS_HASHED')

if __name__=='__main__':main()
