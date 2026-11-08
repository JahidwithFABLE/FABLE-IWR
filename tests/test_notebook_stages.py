"""Synthetic regression tests for the new scientific notebooks, not release data."""
from pathlib import Path
import json
import unittest
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def load_code(name, index=2):
    nb=json.loads((ROOT/'notebooks'/name).read_text(encoding='utf-8'))
    ns={'__name__':'__notebook_test__'}
    for cell in nb['cells'][1:index+1]:
        if cell['cell_type']=='code':
            exec(compile(''.join(cell['source']),name,'exec'),ns)
    return ns

class NotebookStageTests(unittest.TestCase):
    def test_spam_weighting_conserves_harvested_area(self):
        ns=load_code('03-spam-weights.ipynb')
        h=pd.DataFrame([{'country_iso3':'BGD','year':2000,'fable_product':'corn',
                         'harvested_irrigated_ha':100.0}])
        s=pd.DataFrame([{'country_iso3':'BGD','fable_product':'corn','lon':90.01,
                         'lat':23.01,'harvested_irrigated_ha':2.0,'harvested_total_ha':3.0},
                        {'country_iso3':'BGD','fable_product':'corn','lon':90.10,
                         'lat':23.10,'harvested_irrigated_ha':3.0,'harvested_total_ha':4.0}])
        grid,plan=ns['prepare_weights'](h,s,2000)
        self.assertAlmostEqual(grid.corrected_irrigated_ha.sum(),100.0)
        self.assertEqual(plan.method.iloc[0],'IRRIGATED_PATTERN_SCALED_TO_CALCULATOR')
        s['harvested_irrigated_ha']=0.0
        grid,plan=ns['prepare_weights'](h,s,2000)
        self.assertAlmostEqual(grid.corrected_irrigated_ha.sum(),100.0)
        self.assertEqual(plan.method.iloc[0],'TOTAL_HARVESTED_PATTERN_SAME_YEAR')
        s['harvested_total_ha']=0.0
        with self.assertRaises(ValueError):ns['prepare_weights'](h,s,2000)

    def test_lpjml_pixel_weighting_and_coverage(self):
        ns=load_code('04-isimip-lpjml.ipynb')
        import xarray as xr
        weights=pd.DataFrame([{'country_iso3':'BGD','year':2000,'fable_product_norm':'corn',
            'lpjml_crop_code':'mai','lpjml_lat':23.25,'lpjml_lon':90.25,'corrected_irrigated_ha':10.0}])
        da=xr.DataArray([[20.0]],coords={'lat':[23.25],'lon':[90.25]},dims=('lat','lon'))
        out=ns['country_weighted'](da,weights,{'impact_model':'LPJmL'})
        self.assertAlmostEqual(out.weighted_pirrww_mm_yr.iloc[0],20.0)
        self.assertAlmostEqual(out.represented_water_km3.iloc[0],20*10*10/1e9)
        self.assertEqual(out.qc_status.iloc[0],'PASS')

    def test_four_forcing_median_and_reject_three(self):
        ns=load_code('05-isimip-model-qc.ipynb')
        base=dict(country_iso3='BGD',year=2000,climate_scenario='HISTORICAL',
                  fable_product_norm='corn',lpjml_crop_code='mai',
                  spatial_coverage_fraction=1)
        raw=pd.DataFrame([{**base,'climate_forcing':str(i),'weighted_pirrww_mm_yr':i*10} for i in range(4)])
        res=ns['model_median'](raw)
        self.assertEqual(len(res),1)
        self.assertAlmostEqual(res.median_pirrww_mm_yr.iloc[0],15)
        with self.assertRaises(ValueError):ns['model_median'](raw.iloc[:3])

    def test_technology_same_country_and_predefined_peers(self):
        ns=load_code('10-complete-shares.ipynb',1)
        src=pd.DataFrame([{'iso3':'BGD','year':2000,'surface_share':.6,'sprinkler_share':.3,'drip_share':.1},
                          {'iso3':'BGD','year':2010,'surface_share':.8,'sprinkler_share':.1,'drip_share':.1},
                          {'iso3':'ATG','year':2005,'surface_share':.5,'sprinkler_share':.3,'drip_share':.2},
                          {'iso3':'CUB','year':2005,'surface_share':.7,'sprinkler_share':.2,'drip_share':.1}])
        needed=pd.DataFrame([{'country_iso3':'BGD','year':2005},
                             {'country_iso3':'BHS','year':2005}])
        peer=pd.read_csv(ROOT/'config'/'technology-peers.csv')
        result=ns['complete'](needed,src,peer)
        b=result[result.country_iso3.eq('BGD')].iloc[0]
        h=result[result.country_iso3.eq('BHS')].iloc[0]
        self.assertAlmostEqual(b.surface_share,.7)
        self.assertEqual(b.technology_resolution_route,'R1_SAME_COUNTRY_NEAREST_VALID_YEAR')
        self.assertAlmostEqual(h.surface_share,.6)
        self.assertEqual(h.technology_resolution_route,'R2_SAME_YEAR_REGIONAL_PEER_MEAN')
        with self.assertRaises(ValueError):
            ns['complete'](needed,src[src.iso3.ne('CUB')],peer)

    def test_aquastat_missing_not_assumed_zero(self):
        ns=load_code('15-aquastat-qc.ipynb')
        g=pd.DataFrame([{'country_iso3':'UZB','year':2015,'pathway':'RCP26',
                         'gross_withdrawal_Mm3':37449.0},
                        {'country_iso3':'UZB','year':2010,'pathway':'RCP26',
                         'gross_withdrawal_Mm3':34958.0}])
        a=pd.DataFrame([{'country_iso3':'UZB','year':2015,'withdrawal_km3':49.97}])
        result=ns['compare_aquastat'](g,a)
        self.assertAlmostEqual(result.loc[result.year.eq(2015),'relative_difference'].iloc[0],
            37449/49970-1)
        self.assertTrue(np.isnan(result.loc[result.year.eq(2010),'relative_difference'].iloc[0]))

if __name__=='__main__':unittest.main()
