"""Small, synthetic regression tests for calculation and QC; no original IWR data."""
from pathlib import Path
import importlib.util
import unittest
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parents[1]

def load(path):
    spec=importlib.util.spec_from_file_location(path.stem.replace('-','_'),path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

water=load(HERE/'scripts'/'05-build-withdrawal.py')
sharescheck=load(HERE/'scripts'/'04-check-shares.py')
routes=load(HERE/'tools'/'rebuild-net-routes.py')
compare=load(HERE/'scripts'/'06-compare-release.py')

class ScientificTests(unittest.TestCase):
    def setUp(self):
        self.net=pd.DataFrame([
          {'country_iso3':'BGD','year':2000,'fable_product':'rice','pathway':'RCP26',
           'water_requirement_mm_yr':100.0,'water_requirement_m3_ha_yr':1000.0,
           'SPAM_irrigated_area_ha':10.0},
          {'country_iso3':'BGD','year':2000,'fable_product':'rice','pathway':'RCP60',
           'water_requirement_mm_yr':100.0,'water_requirement_m3_ha_yr':1000.0,
           'SPAM_irrigated_area_ha':10.0},
        ])
        self.shares=pd.DataFrame([{'country_iso3':'BGD','year':2000,
            'surface_share':0.5,'sprinkler_share':0.25,'drip_share':0.25}])
        self.eff={'surface':0.42,'sprinkler':0.7125,'drip':0.855}
    def test_gross_component_identity(self):
        out=water.compute(self.net,self.shares,self.eff,expected=False)
        expected=100*(0.5/0.42+0.25/0.7125+0.25/0.855)
        self.assertTrue(np.allclose(out.gross_withdrawal_mm_yr,expected))
        self.assertTrue(np.allclose(out.gross_withdrawal_m3,expected*10*10))
        self.assertTrue(np.allclose(out.additional_delivery_requirement_mm_yr, expected-100))
        self.assertTrue(np.all(out['observed_withdrawal']==False))
    def test_missing_share_fails(self):
        with self.assertRaises(ValueError):
            water.compute(self.net,self.shares.iloc[0:0],self.eff,expected=False)
    def test_share_sum_fails(self):
        bad=self.shares.copy();bad['drip_share']=0.5
        with self.assertRaises(ValueError):
            water.compute(self.net,bad,self.eff,expected=False)
    def test_reference_mismatch_detected(self):
        out=water.compute(self.net,self.shares,self.eff,expected=False)
        self.assertEqual(compare.compare(out,out)['status'],'PASS_SHARED_NUMERIC_REFERENCE_MATCH')
        changed=out.copy(); changed.loc[0,'gross_withdrawal_mm_yr']+=1
        self.assertEqual(compare.compare(out,changed)['status'],'FAIL_NUMERIC_REFERENCE_MISMATCH')
    def test_route_rebuild(self):
        frame=pd.DataFrame([{'target_crop':'rice','country_iso3':'BGD','year':2000,'pathway':'RCP26',
          'SPAM_irrigated_area_ha':10.0,'route_value_mm_yr':100.0,
          'route_group':'DIRECT_LPJML','route_type':'direct','confidence':'HIGH',
          'semantic_status':'OK','final_value_available':True}])
        result=routes.rebuild(frame)
        self.assertEqual(result.loc[0,'water_requirement_m3_ha_yr'],1000.0)
        self.assertEqual(result.loc[0,'total_requirement_m3_before_system_losses'],10000.0)

if __name__=='__main__':unittest.main()
