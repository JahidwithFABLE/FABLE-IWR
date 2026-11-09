#!/usr/bin/env python3
"""Export historical FABLE-C input tables using the accepted September repair route.

Scientific source: original `8 after finding problem with data sept 16.ipynb`,
final global FABLE3 export cell. The authoritative IWR coefficient input is the
REPAIRED historical Dataset A, not the pathway-specific 29,338-row net master.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

YEARS = (2000, 2005, 2010, 2015, 2020)
KEYS = ['country_iso3', 'year', 'fable_product']
PUBLIC_KEYS = ['CountryISO', 'Year', 'Crop']
SPAM_COLS = ['harvested_irrigated_ha', 'harvested_rainfed_ha',
             'harvesting_intensity_irrigated', 'harvesting_intensity_rainfed']
SHARE_COLS = ['surface_share', 'sprinkler_share', 'drip_share']
EFF = {'surface': 0.42, 'sprinkler': 0.7125, 'drip': 0.855}
SPAM_NAME = 'FABLE3_GLOBAL_SPAM_2000_2020_FINAL.csv'
IWR_NAME = 'FABLE3_GLOBAL_IWR_2000_2020_FINAL.csv'
GROSS_NAME = 'FABLE3_GLOBAL_GROSS_COEFFICIENT_DIAGNOSTIC.csv'
NET_CALC_NAME = 'FABLEC_NetIWR_Historical_2000_2020.csv'
SHARES_CALC_NAME = 'FABLEC_IrrigationTechnologyShares_2000_2020.csv'
EFF_CALC_NAME = 'FABLEC_IrrigationEfficiencies.csv'


def require_columns(df: pd.DataFrame, columns: list[str], label: str):
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f'{label}: missing columns {missing}')


def to_numeric(series: pd.Series, label: str) -> pd.Series:
    try:
        return pd.to_numeric(series, errors='raise')
    except (TypeError, ValueError) as exc:
        raise ValueError(f'Invalid numerical data in {label}') from exc


def normalize(df: pd.DataFrame, label: str, is_technology: bool = False) -> pd.DataFrame:
    df = df.copy()
    keys = ['country_iso3', 'year'] + ([] if is_technology else ['fable_product'])
    require_columns(df, keys, label)
    if df[keys].isna().any().any():
        raise ValueError(f'{label}: null keys')
    df['country_iso3'] = df.country_iso3.astype(str).str.strip().str.upper()
    if df.country_iso3.eq('').any():
        raise ValueError(f'{label}: blank country key')
    df['year'] = to_numeric(df.year, label + ' year').astype(int)
    if not is_technology:
        df['fable_product'] = (df.fable_product.astype(str).str.strip().str.lower()
                               .replace({'pineapple': 'pinapple'}))
        if df.fable_product.eq('').any():
            raise ValueError(f'{label}: blank crop key')
    df = df.loc[df.year.isin(YEARS)].copy()
    if df.duplicated(keys).any():
        raise ValueError(f'{label}: duplicate normalized keys')
    return df


def validate_efficiencies(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, ['technology', 'final_delivery_efficiency'], 'efficiencies')
    a = df.copy()
    a['technology'] = a.technology.astype(str).str.strip().str.lower()
    if a.technology.duplicated().any():
        raise ValueError('Duplicate technology efficiency')
    a['final_delivery_efficiency'] = to_numeric(a.final_delivery_efficiency, 'efficiency')
    if set(a.technology) != set(EFF):
        raise ValueError('Expected exactly surface, sprinkler, drip efficiencies')
    for name, value in EFF.items():
        got = float(a.loc[a.technology.eq(name), 'final_delivery_efficiency'].iloc[0])
        if not np.isclose(got, value, atol=1e-12, rtol=0):
            raise ValueError(f'Unexpected {name} efficiency; requires scientific approval')
    return a


def validate_technology(df: pd.DataFrame) -> pd.DataFrame:
    tech = normalize(df, 'approved shares', is_technology=True)
    require_columns(tech, SHARE_COLS, 'approved shares')
    for col in SHARE_COLS:
        tech[col] = to_numeric(tech[col], col)
    all_available = tech[SHARE_COLS].notna().all(axis=1)
    if ((tech[SHARE_COLS] < 0) | (tech[SHARE_COLS] > 1)).any().any():
        raise ValueError('Technology shares outside [0, 1]')
    sums = tech.loc[all_available, SHARE_COLS].sum(axis=1)
    if not np.isclose(sums.to_numpy(float), 1, atol=1e-8, rtol=0).all():
        raise ValueError('Complete technology shares must sum to one')
    if tech[SHARE_COLS].notna().any(axis=1).ne(all_available).any():
        raise ValueError('Partially missing technology share vector')
    return tech


def build_fablec_tables(master05: pd.DataFrame, final06: pd.DataFrame,
                       repaired_iwr: pd.DataFrame, approved_shares: pd.DataFrame,
                       efficiencies: pd.DataFrame,
                       require_global_products: bool = True):
    """Reconstruct original global SPAM + IWR FABLE3 schema; return QC and diagnostics.

    05 supplies the complete key universe; 06 takes precedence for nonnull fields;
    repaired IWR supplies the sole accepted historical net coefficient; country-year
    shares come from the accepted technology layer. Never fill missing with zero.
    """
    base = normalize(master05, '05 SPAM country master')
    overlay = normalize(final06, '06 harmonized SPAM')
    iwr = normalize(repaired_iwr, 'repaired historical IWR')
    tech = validate_technology(approved_shares)
    eff = validate_efficiencies(efficiencies)
    require_columns(base, SPAM_COLS, '05 SPAM country master')
    require_columns(overlay, SPAM_COLS, '06 harmonized SPAM')
    require_columns(iwr, ['iwr_m3_ha_yr'], 'repaired historical IWR')

    if require_global_products and base.fable_product.nunique() != 56:
        raise ValueError('Original full global SPAM panel must contain 56 distinct products')
    extra06 = overlay[KEYS].merge(base[KEYS], on=KEYS, how='left', indicator=True)
    if extra06._merge.ne('both').any():
        raise ValueError('06 harmonized SPAM includes keys absent from authoritative 05 panel')

    spam = base[KEYS + SPAM_COLS].rename(columns={c: c+'_05' for c in SPAM_COLS})
    spam = spam.merge(overlay[KEYS + SPAM_COLS].rename(
        columns={c: c+'_06' for c in SPAM_COLS}), on=KEYS, how='left', validate='one_to_one')
    for col in SPAM_COLS:
        v06 = to_numeric(spam[col+'_06'], col+'_06')
        v05 = to_numeric(spam[col+'_05'], col+'_05')
        spam[col] = v06.where(v06.notna(), v05)
    for col in ('harvested_irrigated_ha', 'harvested_rainfed_ha'):
        if (spam[col].dropna() < 0).any():
            raise ValueError(f'Negative harvested area in {col}')

    # Original repaired Dataset A retains both unit representations.  Protect
    # that accepted evidence rather than silently recalculating a changed value.
    if 'iwr_mm_yr' in iwr.columns:
        mm = to_numeric(iwr['iwr_mm_yr'], 'repaired IWR mm/year')
        m3ha = to_numeric(iwr['iwr_m3_ha_yr'], 'repaired IWR m3/ha/year')
        consistent = np.isclose(mm.to_numpy(float)*10, m3ha.to_numpy(float),
                                atol=1e-6, rtol=1e-9, equal_nan=True)
        if not consistent.all():
            raise ValueError('Repaired IWR mm/year and m3/ha/year disagree')

    iwr = iwr[KEYS + ['iwr_m3_ha_yr']].copy()
    iwr['iwr_m3_ha_yr'] = to_numeric(iwr['iwr_m3_ha_yr'], 'repaired IWR')
    if (iwr.iwr_m3_ha_yr.dropna() < 0).any():
        raise ValueError('Negative repaired IWR coefficient')
    excluded_keys = (iwr[KEYS].merge(spam[KEYS], on=KEYS, how='left', indicator=True)
                     .loc[lambda x: x._merge.eq('left_only'), KEYS].sort_values(KEYS).reset_index(drop=True))
    panel = spam[KEYS + SPAM_COLS].merge(iwr, on=KEYS, how='left', validate='one_to_one')
    panel = panel.merge(tech[['country_iso3','year']+SHARE_COLS],
                        on=['country_iso3','year'], how='left', validate='many_to_one')

    positive = panel.harvested_irrigated_ha.gt(0)
    missing_iwr = int((positive & panel.iwr_m3_ha_yr.isna()).sum())
    missing_tech = int((positive & panel[SHARE_COLS].isna().any(axis=1)).sum())
    if missing_iwr or missing_tech:
        raise ValueError('Positive irrigated harvested area without approved IWR or technology: '
                         f'net={missing_iwr}; shares={missing_tech}')
    if (panel.iwr_m3_ha_yr.dropna() < 0).any():
        raise ValueError('Negative exported net requirement')

    spam_export = pd.DataFrame({
        'CountryISO': panel.country_iso3, 'Year': panel.year, 'Crop': panel.fable_product,
        'irrigated_harvested': panel.harvested_irrigated_ha / 1000.0,
        'rainfed_harvested': panel.harvested_rainfed_ha / 1000.0,
        'harvesting_intensity_irrigated': panel.harvesting_intensity_irrigated,
        'harvesting_intensity_rainfed': panel.harvesting_intensity_rainfed})
    iwr_export = pd.DataFrame({
        'CountryISO': panel.country_iso3, 'Year': panel.year, 'Crop': panel.fable_product,
        'Requirement_ha': panel.iwr_m3_ha_yr,
        'Sur_shr': panel.surface_share, 'Spin_shr': panel.sprinkler_share,
        'Drip_shr': panel.drip_share})
    spam_export = spam_export.sort_values(PUBLIC_KEYS).reset_index(drop=True)
    iwr_export = iwr_export.sort_values(PUBLIC_KEYS).reset_index(drop=True)
    if spam_export[PUBLIC_KEYS].duplicated().any() or iwr_export[PUBLIC_KEYS].duplicated().any():
        raise ValueError('Duplicate export keys')
    if not spam_export[PUBLIC_KEYS].equals(iwr_export[PUBLIC_KEYS]):
        raise ValueError('SPAM/IWR export key mismatch')
    if require_global_products and (spam_export.Crop.nunique()!=56 or iwr_export.Crop.nunique()!=56):
        raise ValueError('Export lost one or more FABLE products')
    if require_global_products and set(spam_export.Year.unique())!=set(YEARS):
        raise ValueError('Missing FABLE historical reference year')

    complete = iwr_export[['Sur_shr','Spin_shr','Drip_shr']].notna().all(axis=1)
    share_sums = iwr_export.loc[complete, ['Sur_shr','Spin_shr','Drip_shr']].sum(axis=1)
    if not np.isclose(share_sums.to_numpy(float), 1, atol=1e-8, rtol=0).all():
        raise ValueError('Export shares fail sum-to-one QC')

    gross = iwr_export[PUBLIC_KEYS+['Requirement_ha','Sur_shr','Spin_shr','Drip_shr']].copy()
    gross['gross_multiplier'] = (gross.Sur_shr/EFF['surface'] +
                                 gross.Spin_shr/EFF['sprinkler'] +
                                 gross.Drip_shr/EFF['drip'])
    gross['gross_requirement_m3_ha_yr'] = gross.Requirement_ha*gross.gross_multiplier
    gross['additional_delivery_m3_ha_yr'] = gross.gross_requirement_m3_ha_yr-gross.Requirement_ha
    gross['gross_is_calculated'] = gross.gross_requirement_m3_ha_yr.notna()
    if (gross.loc[gross.gross_is_calculated, 'gross_requirement_m3_ha_yr']+1e-8 <
            gross.loc[gross.gross_is_calculated, 'Requirement_ha']).any():
        raise ValueError('Gross requirement below net requirement')

    report = {
        'status': 'PASS_FABLEC_HISTORICAL_EXPORT_QC',
        'method': 'original September final repaired historical IWR + 05 SPAM skeleton + 06 correction + accepted technology shares',
        'spam_rows': int(len(spam_export)), 'iwr_rows': int(len(iwr_export)),
        'countries': int(spam_export.CountryISO.nunique()),
        'products': int(iwr_export.Crop.nunique()),
        'years': sorted(int(y) for y in iwr_export.Year.unique()),
        'positive_irrigated_states': int(positive.sum()),
        'positive_area_missing_iwr': missing_iwr,
        'positive_area_missing_technology': missing_tech,
        'iwr_only_keys_excluded': int(len(excluded_keys)),
        'blank_iwr_states_retained': int(iwr_export.Requirement_ha.isna().sum()),
        'blank_technology_states_retained': int(iwr_export[ ['Sur_shr','Spin_shr','Drip_shr'] ].isna().any(axis=1).sum()),
        'zero_iwr_states_retained': int(iwr_export.Requirement_ha.eq(0).sum()),
        'complete_share_vectors': int(complete.sum()),
        'non56_country_year_panels': int(spam_export.groupby(['CountryISO','Year']).size().ne(56).sum()),
        'all_keys_identical': True,
        'efficiencies': {k:float(eff.loc[eff.technology.eq(k),'final_delivery_efficiency'].iloc[0]) for k in EFF},
        'historical_RCP_recomputed': False,
        'scope': 'accepted historical repaired Dataset A to historical FABLE3 export; no raw-ISIMIP reconstruction'}
    return spam_export, iwr_export, gross, excluded_keys, report



def build_calculator_inputs(iwr_export: pd.DataFrame, approved_shares: pd.DataFrame,
                            efficiencies: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create *additional* canonical FABLE-C inputs; preserve original FABLE3 exports.

    Do not invent missing historical coefficients or future values.  Coefficients
    are per hectare; irrigated area remains a separate Calculator calculation.
    """
    require_columns(iwr_export, PUBLIC_KEYS + ['Requirement_ha'], 'historical FABLE3 IWR')
    if iwr_export[PUBLIC_KEYS].isna().any().any() or iwr_export.duplicated(PUBLIC_KEYS).any():
        raise ValueError('Historical IWR has null/duplicate Calculator keys')
    net = iwr_export[PUBLIC_KEYS + ['Requirement_ha']].rename(columns={
        'CountryISO': 'country_iso3', 'Year': 'year', 'Crop': 'fable_product',
        'Requirement_ha': 'net_iwr_m3_ha_yr'}).copy()
    net['net_iwr_m3_ha_yr'] = to_numeric(net.net_iwr_m3_ha_yr, 'net coefficient')
    if (net.net_iwr_m3_ha_yr.dropna() < 0).any():
        raise ValueError('Negative historical net IWR coefficient')
    net['net_iwr_mm_yr'] = net.net_iwr_m3_ha_yr / 10.0
    net = net[['country_iso3','year','fable_product','net_iwr_mm_yr','net_iwr_m3_ha_yr']]
    net = net.sort_values(['country_iso3','year','fable_product']).reset_index(drop=True)

    tech = validate_technology(approved_shares)
    if tech[SHARE_COLS].isna().any().any():
        raise ValueError('Cannot export standalone Calculator technology inputs with blank shares')
    tech = tech[['country_iso3','year'] + SHARE_COLS].sort_values(
        ['country_iso3','year']).reset_index(drop=True)
    eff = validate_efficiencies(efficiencies)
    eff = eff[['technology','final_delivery_efficiency']].sort_values(
        'technology').reset_index(drop=True)
    return {NET_CALC_NAME: net, SHARES_CALC_NAME: tech, EFF_CALC_NAME: eff}


def compare_export(fresh: pd.DataFrame, reference: pd.DataFrame, label: str) -> dict:
    """Compare reference export keys, schema and numerical fields; blanks equal blanks."""
    if list(fresh.columns) != list(reference.columns):
        raise ValueError(f'{label}: reference schema differs from original export schema')
    if reference[PUBLIC_KEYS].isna().any().any() or reference.duplicated(PUBLIC_KEYS).any():
        raise ValueError(f'{label}: invalid reference keys')
    merged = fresh.merge(reference, on=PUBLIC_KEYS, how='outer', suffixes=('_new','_ref'),
                         indicator=True, validate='one_to_one')
    unmatched = int(merged._merge.ne('both').sum())
    errors = {}
    for col in fresh.columns:
        if col in PUBLIC_KEYS: continue
        a = to_numeric(merged[col+'_new'], label+' fresh '+col).to_numpy(float)
        b = to_numeric(merged[col+'_ref'], label+' reference '+col).to_numpy(float)
        ok = np.isclose(a, b, atol=1e-6, rtol=1e-9, equal_nan=True)
        errors[col] = int((~ok & merged._merge.eq('both').to_numpy()).sum())
    success = unmatched == 0 and all(x == 0 for x in errors.values())
    return {'status': 'PASS_NUMERIC_REFERENCE_MATCH' if success else 'FAIL_NUMERIC_REFERENCE_MISMATCH',
            'fresh_rows': len(fresh), 'reference_rows': len(reference),
            'missing_or_extra_keys': unmatched, 'mismatch_counts': errors,
            'tolerance': {'atol': 1e-6, 'rtol': 1e-9}}


def paths(data_root: Path) -> dict[str, Path]:
    return {
        'spam_master': data_root/'spam'/'fablec'/'05_FABLE_SPAM_country_product_2000_2020.csv.gz',
        'spam_harmonized': data_root/'spam'/'fablec'/'06_FABLE_C_SPAM_historical_input_2000_2020_HARMONIZED.csv.gz',
        'repaired_iwr': data_root/'crop'/'fablec'/'FABLE_crop_irrigation_water_requirement_2000_2020_FINAL_REPAIRED.csv',
        'shares': data_root/'technology'/'12_FABLE_irrigation_technology_shares_2000_2020_FINAL.csv',
        'efficiencies': data_root/'technology'/'13_FABLE_irrigation_efficiency_parameters_FINAL.csv'}


def save_output(folder: Path, spam: pd.DataFrame, iwr: pd.DataFrame,
                gross: pd.DataFrame, excluded: pd.DataFrame, report: dict,
                calculator_inputs: dict[str, pd.DataFrame] | None = None):
    folder.mkdir(parents=True, exist_ok=True)
    files = {SPAM_NAME: spam, IWR_NAME: iwr,
             GROSS_NAME: gross, 'QC_IWR_coefficients_outside_final_SPAM_panel.csv': excluded}
    files.update(calculator_inputs or {})
    if any((folder/name).exists() for name in [*files, 'historical-export-qc.json']):
        raise FileExistsError('Historical export output already exists; use a new output root')
    for name, df in files.items():
        df.to_csv(folder/name, index=False, na_rep='')
    (folder/'historical-export-qc.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=Path(__file__).resolve().parents[1]/'data')
    parser.add_argument('--output-root', type=Path, default=Path(__file__).resolve().parents[1]/'runs'/'fablec-historical-01')
    parser.add_argument('--reference-iwr', type=Path, help='Optional original FABLE3 global IWR historical export')
    parser.add_argument('--reference-spam', type=Path, help='Optional original FABLE3 global SPAM historical export')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    source_paths = paths(args.data_root)
    found = {k: v.is_file() for k, v in source_paths.items()}
    print(json.dumps({'inputs': {k: {'path': str(v), 'available': found[k]}
                                 for k,v in source_paths.items()}}, indent=2))
    if not all(found.values()):
        raise SystemExit('Missing required historical input files; see docs/fablec-integration.md')
    if args.check:
        print('STATUS: PASS_FABLEC_HISTORICAL_INPUT_CHECK_ONLY')
        return
    raw = {k: pd.read_csv(p, low_memory=False) for k,p in source_paths.items()}
    spam, iwr, gross, excluded, report = build_fablec_tables(
        raw['spam_master'],raw['spam_harmonized'],raw['repaired_iwr'],
        raw['shares'],raw['efficiencies'])
    comparisons = {}
    for label, file, df in [('iwr', args.reference_iwr, iwr), ('spam', args.reference_spam, spam)]:
        if file:
            if not file.is_file(): raise FileNotFoundError(file)
            comparisons[label] = compare_export(df, pd.read_csv(file,low_memory=False), label)
            if comparisons[label]['status'].startswith('FAIL'):
                raise ValueError(f'{label} reference comparison FAILED: {comparisons[label]}')
        else:
            comparisons[label] = {'status':'NOT_EVALUATED_NO_REFERENCE_PROVIDED'}
    report['reference_comparisons'] = comparisons
    calculator_inputs = build_calculator_inputs(iwr, raw['shares'], raw['efficiencies'])
    report['calculator_input_files'] = list(calculator_inputs)
    save_output(args.output_root,spam,iwr,gross,excluded,report, calculator_inputs)
    print(json.dumps(report,indent=2))
    print('STATUS: '+ ('PASS_FABLEC_HISTORICAL_NUMERIC_REFERENCE_MATCH'
                        if args.reference_iwr and args.reference_spam
                        else 'PASS_FABLEC_HISTORICAL_EXPORT_QC_ONLY'))


if __name__ == '__main__':
    main()
