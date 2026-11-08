#!/usr/bin/env python3
"""Rebuild baseline country-year irrigation-system shares from Jägermeyr and Rohwer.

This reproduces the original 2000/2015 anchor and intermediate-year rules.
It does NOT perform the subsequent country-gap completion to the 824-row
technology release, which requires the separately approved evidence file.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def display(value):
    if hasattr(value,'head'):
        print(value.head(12).to_string(index=False))
    else:
        print(value)

def rebuild(jagermeyr: Path, rohwer: Path, output_root: Path):
    global jag_raw,roh_raw,OUTPUT_DIR,QC_DIR,COUNTRY_DIR,TARGET_YEARS,EARLY_MODEL_YEAR,LATE_MODEL_YEAR
    for p in (jagermeyr,rohwer):
        if not p.is_file(): raise FileNotFoundError(p)
    OUTPUT_DIR=output_root
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        raise FileExistsError(f'Refusing non-empty output folder: {OUTPUT_DIR}')
    QC_DIR=OUTPUT_DIR/'QC'
    COUNTRY_DIR=OUTPUT_DIR/'country_exports'
    for p in (OUTPUT_DIR,QC_DIR,COUNTRY_DIR):p.mkdir(parents=True,exist_ok=True)
    TARGET_YEARS=[2000,2005,2010,2015,2020]
    EARLY_MODEL_YEAR,LATE_MODEL_YEAR=2000,2015
    jag_raw=pd.read_csv(jagermeyr)
    roh_raw=pd.read_csv(rohwer)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Scientific operations adapted from original share notebook, part 1
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def share_sum_ok(series, tol=0.005):
        total = series.fillna(0).sum(axis=1)
        return np.isclose(total, 1.0, atol=tol) | np.isclose(total, 0.0, atol=tol)

    def values_in_0_1(df, cols):
        return (df[cols].isna() | (df[cols] >= 0) & (df[cols] <= 1)).all(axis=1)
    jag = jag_raw.copy()
    jag_area_cols = ['surface_area_1000ha', 'sprinkler_area_1000ha', 'drip_localized_area_1000ha']
    jag_share_cols = ['surface_share', 'sprinkler_share', 'drip_localized_share']
    jag['qc_missing_iso3'] = jag['iso3'].isna()
    jag['qc_duplicate_iso3'] = jag['iso3'].notna() & jag['iso3'].duplicated(keep=False)
    jag['qc_negative_area'] = jag[jag_area_cols].fillna(0).lt(0).any(axis=1)
    jag['qc_share_out_of_range'] = ~values_in_0_1(jag, jag_share_cols)
    jag['qc_area_sum_calc'] = jag[jag_area_cols].fillna(0).sum(axis=1)
    jag['qc_area_sum_diff'] = (jag['qc_area_sum_calc'] - jag['system_area_sum_1000ha'].fillna(0)).abs()
    jag['qc_area_sum_review'] = jag['qc_area_sum_diff'] > 0.1
    jag['qc_share_sum_calc'] = jag[jag_share_cols].fillna(0).sum(axis=1)
    jag['qc_share_sum_problem'] = ~share_sum_ok(jag[jag_share_cols])
    system_total = jag['qc_area_sum_calc']
    for system, area_col, share_col in [('surface', 'surface_area_1000ha', 'surface_share'), ('sprinkler', 'sprinkler_area_1000ha', 'sprinkler_share'), ('drip', 'drip_localized_area_1000ha', 'drip_localized_share')]:
        calc = np.where(system_total > 0, jag[area_col].fillna(0) / system_total, 0)
        jag[f'qc_{system}_share_from_area'] = calc
        jag[f'qc_{system}_reported_vs_area_diff'] = (jag[share_col].fillna(0) - calc).abs()
    jag['qc_reported_vs_area_max_diff'] = jag[['qc_surface_reported_vs_area_diff', 'qc_sprinkler_reported_vs_area_diff', 'qc_drip_reported_vs_area_diff']].max(axis=1)
    jag['qc_reported_vs_area_review'] = jag['qc_reported_vs_area_max_diff'] > 0.02
    jag['qc_critical'] = jag[['qc_missing_iso3', 'qc_duplicate_iso3', 'qc_negative_area', 'qc_share_out_of_range', 'qc_share_sum_problem']].any(axis=1)
    jag['qc_review'] = jag[['qc_area_sum_review', 'qc_reported_vs_area_review']].any(axis=1)
    jag['qc_status'] = np.select([jag['qc_critical'], jag['qc_review']], ['FAIL', 'REVIEW'], default='PASS')
    roh = roh_raw.copy()
    roh_share_cols = ['annexA_surface_share', 'annexA_sprinkler_share', 'annexA_micro_share']
    efficiency_cols = ['application_efficiency', 'conveyance_efficiency', 'management_factor', 'project_efficiency', 'actual_project_efficiency']
    roh['qc_missing_iso3'] = roh['iso3'].isna()
    roh['qc_duplicate_iso3'] = roh['iso3'].notna() & roh['iso3'].duplicated(keep=False)
    roh['qc_annexA_share_sum'] = roh[roh_share_cols].fillna(0).sum(axis=1)
    roh['qc_any_negative_share'] = roh[roh_share_cols].fillna(0).lt(0).any(axis=1)
    roh['qc_any_share_gt1'] = roh[roh_share_cols].fillna(0).gt(1).any(axis=1)
    roh['qc_share_out_of_range'] = roh['qc_any_negative_share'] | roh['qc_any_share_gt1']
    roh['qc_direct_share_usable'] = ~roh['qc_share_out_of_range'] & roh['qc_annexA_share_sum'].between(0.95, 1.05)
    roh['qc_partial_or_invalid_annexA'] = (roh['qc_annexA_share_sum'] > 0) & ~roh['qc_direct_share_usable']
    roh['qc_efficiency_out_of_range'] = False
    for col in efficiency_cols:
        roh['qc_efficiency_out_of_range'] = roh['qc_efficiency_out_of_range'] | ~(roh[col].isna() | roh[col].between(0, 1))
    VALID_IFT = {'Surface', 'Sprinkler', 'Micro', 'Mixed'}
    roh['qc_invalid_ift'] = roh['ift'].notna() & ~roh['ift'].isin(VALID_IFT)
    roh['qc_critical'] = roh[['qc_missing_iso3', 'qc_invalid_ift']].any(axis=1)
    roh['qc_review'] = roh[['qc_duplicate_iso3', 'qc_partial_or_invalid_annexA', 'qc_share_out_of_range', 'qc_efficiency_out_of_range']].any(axis=1)
    roh['qc_status'] = np.select([roh['qc_critical'], roh['qc_review']], ['FAIL', 'REVIEW'], default='PASS')
    print('JÄGERMEYR QC')
    print(jag['qc_status'].value_counts(dropna=False))
    print('\nROHWER QC')
    print(roh['qc_status'].value_counts(dropna=False))
    print('\nRohwer usable direct Annex A share rows:', int(roh['qc_direct_share_usable'].sum()))
    print('Rohwer rows requiring IFT/fallback treatment:', int((~roh['qc_direct_share_usable']).sum()))
    print('Rohwer duplicate ISO3 rows:', int(roh['qc_duplicate_iso3'].sum()))
    print('Rohwer source efficiency anomalies (kept as QC only):', int(roh['qc_efficiency_out_of_range'].sum()))

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Scientific operations adapted from original share notebook, part 2
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    roh['selection_score'] = roh['qc_direct_share_usable'].astype(int) * 100 + roh['ift_category'].eq('known').astype(int) * 20 + roh['ift_category'].eq('assigned').astype(int) * 10 + roh['ift'].notna().astype(int)
    roh_best = roh.sort_values(['iso3', 'selection_score'], ascending=[True, False]).drop_duplicates(subset='iso3', keep='first').copy()
    IFT_SHARES = {'Surface': (1.0, 0.0, 0.0), 'Sprinkler': (0.0, 1.0, 0.0), 'Micro': (0.0, 0.0, 1.0), 'Mixed': (0.5, 0.5, 0.0)}

    def normalize_shares(s, p, d):
        vals = np.array([s, p, d], dtype=float)
        vals[np.abs(vals) < 1e-12] = 0.0
        vals = np.clip(vals, 0, 1)
        total = vals.sum()
        if total > 0:
            vals = vals / total
        return tuple(vals)

    def derive_early_anchor(row):
        if bool(row['qc_direct_share_usable']):
            s, p, d = normalize_shares(row['annexA_surface_share'], row['annexA_sprinkler_share'], row['annexA_micro_share'])
            return pd.Series({'surface_share_2000': s, 'sprinkler_share_2000': p, 'drip_share_2000': d, 'anchor2000_method': 'ROHWER_DIRECT_ANNEX_A_NORMALIZED', 'anchor2000_quality': 'SOURCE_PATTERN_NORMALIZED'})
        if row['ift'] in IFT_SHARES:
            s, p, d = IFT_SHARES[row['ift']]
            quality = 'IFT_DERIVED_KNOWN' if row['ift_category'] == 'known' else 'IFT_DERIVED_ASSIGNED' if row['ift_category'] == 'assigned' else 'IFT_DERIVED'
            return pd.Series({'surface_share_2000': s, 'sprinkler_share_2000': p, 'drip_share_2000': d, 'anchor2000_method': 'ROHWER_IFT_DERIVED', 'anchor2000_quality': quality})
        return pd.Series({'surface_share_2000': np.nan, 'sprinkler_share_2000': np.nan, 'drip_share_2000': np.nan, 'anchor2000_method': 'NO_USABLE_ROHWER_ANCHOR', 'anchor2000_quality': 'MISSING'})
    roh_anchor = pd.concat([roh_best.reset_index(drop=True), roh_best.reset_index(drop=True).apply(derive_early_anchor, axis=1)], axis=1)
    print('Rohwer model-anchor methods')
    print(roh_anchor['anchor2000_method'].value_counts(dropna=False))
    missing_rohwer_anchor = roh_anchor[roh_anchor['surface_share_2000'].isna()][['iso3', 'country', 'ift', 'ift_category', 'qc_status']]
    print('\nRows still needing Jägermeyr fallback:', len(missing_rohwer_anchor))
    display(missing_rohwer_anchor.head(30))

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Scientific operations adapted from original share notebook, part 3
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    cross = jag[['iso3', 'country', 'surface_share', 'sprinkler_share', 'drip_localized_share', 'system_area_sum_1000ha', 'aquastat_total_equipped_1000ha', 'icid_total_equipped_1000ha', 'actually_irrigated_pct_fao', 'qc_status', 'notes', 'source_compilation']].rename(columns={'surface_share': 'later_surface_share', 'sprinkler_share': 'later_sprinkler_share', 'drip_localized_share': 'later_drip_share', 'qc_status': 'jagermeyr_qc_status', 'notes': 'jagermeyr_notes'}).merge(roh_anchor[['iso3', 'surface_share_2000', 'sprinkler_share_2000', 'drip_share_2000', 'anchor2000_method', 'anchor2000_quality', 'annexA_reference_period']], on='iso3', how='left')
    cross['later_share_sum'] = cross[['later_surface_share', 'later_sprinkler_share', 'later_drip_share']].fillna(0).sum(axis=1)
    cross['positive_irrigation_evidence'] = (cross['system_area_sum_1000ha'].fillna(0) > 0) | (cross['aquastat_total_equipped_1000ha'].fillna(0) > 0) | (cross['icid_total_equipped_1000ha'].fillna(0) > 0) | (cross['actually_irrigated_pct_fao'].fillna(0) > 0)
    cross['jagermeyr_missing_system_breakdown'] = np.isclose(cross['later_share_sum'], 0.0, atol=1e-12) & cross['positive_irrigation_evidence']
    for system in ['surface', 'sprinkler', 'drip']:
        cross[f'diff_{system}_abs'] = (cross[f'later_{system}_share'] - cross[f'{system}_share_2000']).abs()
    cross['max_system_share_difference'] = cross[['diff_surface_abs', 'diff_sprinkler_abs', 'diff_drip_abs']].max(axis=1)
    cross['cross_source_status'] = np.select([cross['jagermeyr_missing_system_breakdown'], cross['surface_share_2000'].isna(), cross['max_system_share_difference'] > 0.5, cross['max_system_share_difference'] > 0.25], ['JAGERMEYR_SYSTEM_BREAKDOWN_MISSING', 'NO_ROHWER_REFERENCE', 'LARGE_DIFFERENCE', 'MODERATE_DIFFERENCE'], default='CONSISTENT')
    no_early = cross['surface_share_2000'].isna()
    later_valid = ~cross['jagermeyr_missing_system_breakdown']
    backcast_mask = no_early & later_valid
    for system in ['surface', 'sprinkler', 'drip']:
        cross.loc[backcast_mask, f'{system}_share_2000'] = cross.loc[backcast_mask, f'later_{system}_share']
    cross.loc[backcast_mask, 'anchor2000_method'] = 'JAGERMEYR_BACKCAST_FALLBACK'
    cross.loc[backcast_mask, 'anchor2000_quality'] = 'FALLBACK_NO_ROHWER'
    has_early = cross['surface_share_2000'].notna()
    later_missing_with_early = cross['jagermeyr_missing_system_breakdown'] & has_early
    for system in ['surface', 'sprinkler', 'drip']:
        cross.loc[later_missing_with_early, f'later_{system}_share'] = cross.loc[later_missing_with_early, f'{system}_share_2000']
    cross['later_anchor_method'] = 'JAGERMEYR_TABLE_S1'
    cross.loc[later_missing_with_early, 'later_anchor_method'] = 'ROHWER_CARRY_FORWARD_FOR_MISSING_JAGERMEYR_BREAKDOWN'
    unresolved = cross['jagermeyr_missing_system_breakdown'] & cross['surface_share_2000'].isna()
    cross.loc[unresolved, 'later_surface_share'] = np.nan
    cross.loc[unresolved, 'later_sprinkler_share'] = np.nan
    cross.loc[unresolved, 'later_drip_share'] = np.nan
    cross.loc[unresolved, 'later_anchor_method'] = 'UNRESOLVED_SOURCE_GAP'
    print('Cross-source status')
    print(cross['cross_source_status'].value_counts(dropna=False))
    print('\nEarly-anchor methods after fallback')
    print(cross['anchor2000_method'].value_counts(dropna=False))
    print('\nJägermeyr missing system breakdown rows:', int(cross['jagermeyr_missing_system_breakdown'].sum()))
    print('Resolved using Rohwer carry-forward:', int(later_missing_with_early.sum()))
    print('Still unresolved source gaps:', int(unresolved.sum()))
    if unresolved.any():
        display(cross.loc[unresolved, ['iso3', 'country', 'aquastat_total_equipped_1000ha', 'actually_irrigated_pct_fao', 'cross_source_status', 'later_anchor_method']])

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Scientific operations adapted from original share notebook, part 4
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    records = []
    for _, row in cross.iterrows():
        for year in TARGET_YEARS:
            s0 = row['surface_share_2000']
            p0 = row['sprinkler_share_2000']
            d0 = row['drip_share_2000']
            s1 = row['later_surface_share']
            p1 = row['later_sprinkler_share']
            d1 = row['later_drip_share']
            unresolved_source_gap = any((pd.isna(x) for x in [s0, p0, d0, s1, p1, d1]))
            early_zero_vector = False
            later_zero_vector = False
            if not unresolved_source_gap:
                early_sum = s0 + p0 + d0
                later_sum = s1 + p1 + d1
                early_zero_vector = np.isclose(early_sum, 0.0, atol=1e-12)
                later_zero_vector = np.isclose(later_sum, 0.0, atol=1e-12)
                if not early_zero_vector:
                    s0, p0, d0 = normalize_shares(s0, p0, d0)
                if not later_zero_vector:
                    s1, p1, d1 = normalize_shares(s1, p1, d1)
            if unresolved_source_gap:
                s = p = d = np.nan
                method = 'UNRESOLVED_SOURCE_GAP'
                source_status = 'REVIEW_NOT_MODEL_READY'
                reference_period = 'No defensible system-share vector available from included sources'
            elif year == 2000:
                s, p, d = (s0, p0, d0)
                method = row['anchor2000_method']
                source_status = row['anchor2000_quality']
                reference_period = row['annexA_reference_period'] if pd.notna(row['annexA_reference_period']) else 'Later-reference back-cast; no usable Rohwer anchor'
            elif year in [2005, 2010]:
                if not early_zero_vector and later_zero_vector:
                    s, p, d = (s0, p0, d0)
                    method = 'CARRY_FORWARD_EARLY_PATTERN_TO_ZERO_LATER_ANCHOR'
                    source_status = 'DERIVED_CARRY_FORWARD_HIGH_UNCERTAINTY'
                    reference_period = 'Early system pattern retained because the later source reports a zero system vector; no intermediate system distribution can be inferred'
                else:
                    fraction = (year - EARLY_MODEL_YEAR) / (LATE_MODEL_YEAR - EARLY_MODEL_YEAR)
                    s = s0 + fraction * (s1 - s0)
                    p = p0 + fraction * (p1 - p0)
                    d = d0 + fraction * (d1 - d0)
                    method = 'LINEAR_INTERPOLATION_BETWEEN_MODEL_ANCHORS'
                    source_status = 'DERIVED_INTERPOLATED_HIGH_UNCERTAINTY' if row['cross_source_status'] in ['LARGE_DIFFERENCE', 'MODERATE_DIFFERENCE'] else 'DERIVED_INTERPOLATED'
                    reference_period = 'Between early Rohwer-based and later Jägermeyr-based model anchors'
            elif year == 2015:
                s, p, d = (s1, p1, d1)
                method = row['later_anchor_method']
                if row['later_anchor_method'] == 'ROHWER_CARRY_FORWARD_FOR_MISSING_JAGERMEYR_BREAKDOWN':
                    source_status = 'DERIVED_CARRY_FORWARD_SOURCE_GAP'
                    reference_period = 'Rohwer-based system pattern carried forward because Jägermeyr system breakdown is missing'
                else:
                    source_status = 'SOURCE_COMPILATION_USED_AS_MODEL_ANCHOR'
                    reference_period = 'FAO (2014), ICID (2012), Rohwer et al. (2007) compilation'
            elif year == 2020:
                s, p, d = (s1, p1, d1)
                if row['later_anchor_method'] == 'ROHWER_CARRY_FORWARD_FOR_MISSING_JAGERMEYR_BREAKDOWN':
                    method = 'ROHWER_CARRY_FORWARD_FOR_MISSING_JAGERMEYR_BREAKDOWN'
                    source_status = 'DERIVED_CARRY_FORWARD_SOURCE_GAP'
                    reference_period = 'Rohwer-based system pattern retained through 2020 because Jägermeyr system breakdown is missing'
                else:
                    method = 'CARRY_FORWARD_LATER_REFERENCE'
                    source_status = 'DERIVED_CARRY_FORWARD'
                    reference_period = 'Later reference retained; no post-2015 source included'
            if not pd.isna(s):
                current_sum = s + p + d
                if not np.isclose(current_sum, 0.0, atol=1e-12):
                    s, p, d = normalize_shares(s, p, d)
            records.append({'iso3': row['iso3'], 'country': row['country'], 'year': year, 'surface_share': s, 'sprinkler_share': p, 'drip_share': d, 'method': method, 'source_status': source_status, 'reference_period': reference_period, 'early_anchor_method': row['anchor2000_method'], 'early_anchor_quality': row['anchor2000_quality'], 'later_anchor_method': row['later_anchor_method'], 'jagermeyr_qc_status': row['jagermeyr_qc_status'], 'cross_source_status': row['cross_source_status']})
    final = pd.DataFrame(records).sort_values(['iso3', 'year']).reset_index(drop=True)
    print('Final rows:', len(final))
    print('Countries/entities:', final['iso3'].nunique())
    print('Years:', sorted(final['year'].unique()))
    print('Rows not model-ready:', int((final['source_status'] == 'REVIEW_NOT_MODEL_READY').sum()))
    print('Intermediate rows using early-pattern carry-forward:', int((final['method'] == 'CARRY_FORWARD_EARLY_PATTERN_TO_ZERO_LATER_ANCHOR').sum()))

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Scientific operations adapted from original share notebook, part 5
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    interp_problems = []
    for iso3, g in final.groupby('iso3'):
        g = g.set_index('year')
        if not all((y in g.index for y in [2000, 2005, 2010, 2015])):
            continue
        for year in [2005, 2010]:
            if g.loc[year, 'method'] != 'LINEAR_INTERPOLATION_BETWEEN_MODEL_ANCHORS':
                continue
            cols = ['surface_share', 'sprinkler_share', 'drip_share']
            if g.loc[[2000, 2015], cols].isna().any().any():
                continue
            fraction = (year - 2000) / (2015 - 2000)
            expected = g.loc[2000, cols].astype(float) + fraction * (g.loc[2015, cols].astype(float) - g.loc[2000, cols].astype(float))
            observed = g.loc[year, cols].astype(float)
            max_diff = np.max(np.abs(observed.values - expected.values))
            if max_diff > 1e-10:
                interp_problems.append({'iso3': iso3, 'country': g.loc[year, 'country'], 'year': year, 'max_abs_difference': max_diff})
    interp_problems = pd.DataFrame(interp_problems)
    print('Interpolation rows failing exact-anchor check:', len(interp_problems))
    if len(interp_problems) > 0:
        display(interp_problems)
    special_cases = final[final['method'] == 'CARRY_FORWARD_EARLY_PATTERN_TO_ZERO_LATER_ANCHOR'][['iso3', 'country', 'year', 'surface_share', 'sprinkler_share', 'drip_share', 'method', 'source_status']]
    print('\nIntermediate zero-later-anchor special-case rows:', len(special_cases))
    display(special_cases)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Scientific operations adapted from original share notebook, part 6
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    final_qc = final.copy()
    final_qc['share_sum'] = final_qc[['surface_share', 'sprinkler_share', 'drip_share']].sum(axis=1, min_count=1)
    final_qc['qc_duplicate_country_year'] = final_qc.duplicated(subset=['iso3', 'year'], keep=False)
    final_qc['qc_missing_system_share'] = final_qc[['surface_share', 'sprinkler_share', 'drip_share']].isna().any(axis=1)
    final_qc['qc_share_out_of_range'] = ~final_qc['qc_missing_system_share'] & ~(final_qc['surface_share'].between(0, 1) & final_qc['sprinkler_share'].between(0, 1) & final_qc['drip_share'].between(0, 1))
    final_qc['qc_share_sum_problem'] = ~final_qc['qc_missing_system_share'] & ~(np.isclose(final_qc['share_sum'], 1.0, atol=0.005) | np.isclose(final_qc['share_sum'], 0.0, atol=0.005))
    country_year_counts = final_qc.groupby('iso3')['year'].nunique()
    bad_country_years = country_year_counts[country_year_counts != len(TARGET_YEARS)]
    final_qc['qc_status'] = np.select([final_qc['qc_duplicate_country_year'] | final_qc['qc_share_out_of_range'] | final_qc['qc_share_sum_problem'], final_qc['qc_missing_system_share']], ['FAIL', 'REVIEW_SOURCE_GAP'], default='PASS')
    jag.to_csv(QC_DIR / '01_jagermeyr_source_QC.csv', index=False)
    roh.to_csv(QC_DIR / '02_rohwer_source_QC.csv', index=False)
    cross.to_csv(QC_DIR / '03_cross_source_QC.csv', index=False)
    final_qc.to_csv(QC_DIR / '04_final_global_dataset_QC.csv', index=False)
    jag.to_csv(OUTPUT_DIR / '01_jagermeyr_source_QC_READY.csv', index=False)
    roh_anchor.to_csv(OUTPUT_DIR / '02_rohwer_source_QC_READY.csv', index=False)
    FINAL_GLOBAL_FILE = OUTPUT_DIR / '03_FABLE_global_irrigation_system_shares_2000_2020.csv'
    final.to_csv(FINAL_GLOBAL_FILE, index=False)
    summary = pd.DataFrame({'metric': ['Jägermeyr raw rows', 'Rohwer raw rows', 'Final countries/entities', 'Final rows', 'Direct Rohwer early anchors', 'IFT-derived Rohwer early anchors', 'Jägermeyr back-cast early fallbacks', 'Jägermeyr missing-system rows', 'Later gaps resolved with Rohwer', 'Unresolved countries/entities', 'Cross-source large differences', 'Final FAIL rows', 'Final REVIEW_SOURCE_GAP rows'], 'value': [len(jag), len(roh), final['iso3'].nunique(), len(final), int((cross['anchor2000_method'] == 'ROHWER_DIRECT_ANNEX_A_NORMALIZED').sum()), int((cross['anchor2000_method'] == 'ROHWER_IFT_DERIVED').sum()), int((cross['anchor2000_method'] == 'JAGERMEYR_BACKCAST_FALLBACK').sum()), int(cross['jagermeyr_missing_system_breakdown'].sum()), int((cross['later_anchor_method'] == 'ROHWER_CARRY_FORWARD_FOR_MISSING_JAGERMEYR_BREAKDOWN').sum()), int((cross['later_anchor_method'] == 'UNRESOLVED_SOURCE_GAP').sum()), int((cross['cross_source_status'] == 'LARGE_DIFFERENCE').sum()), int((final_qc['qc_status'] == 'FAIL').sum()), int((final_qc['qc_status'] == 'REVIEW_SOURCE_GAP').sum())]})
    summary.to_csv(QC_DIR / '05_QC_summary.csv', index=False)
    display(summary)
    if (final_qc['qc_status'] == 'FAIL').any() or len(bad_country_years) > 0:
        raise ValueError('Critical final QC failed. Inspect outputs/QC.')
    overall_status = 'PASS_WITH_REVIEW' if (final_qc['qc_status'] == 'REVIEW_SOURCE_GAP').any() else 'PASS'
    print('\nFINAL STRUCTURAL QC:', overall_status)
    print('Global dataset saved to:')
    print(FINAL_GLOBAL_FILE)
    return FINAL_GLOBAL_FILE

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jagermeyr',type=Path,required=True)
    parser.add_argument('--rohwer',type=Path,required=True)
    parser.add_argument('--output-root',type=Path,required=True)
    args=parser.parse_args()
    result=rebuild(args.jagermeyr,args.rohwer,args.output_root)
    print('BASELINE_TECHNOLOGY_SOURCE_BUILT:',result)
    print('This is a source-share reconstruction, not the approved 824-row completion.')

if __name__=='__main__':main()
