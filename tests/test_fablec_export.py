"""Synthetic regression tests for the original September FABLE3 historical export route."""
import importlib.util
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / '08-export-fablec-historical.py'
spec = importlib.util.spec_from_file_location('fablec_export', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    keys = {
        'country_iso3': ['BGD','BGD','BGD'],
        'year': [2000, 2000, 2005],
        'fable_product': ['pineapple','wheat','wheat']
    }
    master = pd.DataFrame({**keys,
        'harvested_irrigated_ha':[100,0,200],
        'harvested_rainfed_ha':[300,400,500],
        'harvesting_intensity_irrigated':[1.0,np.nan,1.3],
        'harvesting_intensity_rainfed':[0.9,0.95,1.05]})
    overlay = pd.DataFrame({'country_iso3':['BGD'], 'year':[2000],
        'fable_product':['pineapple'], 'harvested_irrigated_ha':[120],
        'harvested_rainfed_ha':[np.nan],
        'harvesting_intensity_irrigated':[1.1],
        'harvesting_intensity_rainfed':[np.nan]})
    iwr = pd.DataFrame({'country_iso3':['BGD','BGD','BGD','IND'],
        'year':[2000,2000,2005,2000],
        'fable_product':['pinapple','wheat','wheat','rice'],
        'iwr_m3_ha_yr':[4000,np.nan,0,5000]})
    tech = pd.DataFrame({'country_iso3':['BGD','BGD'], 'year':[2000,2005],
        'surface_share':[0.5,1], 'sprinkler_share':[0.25,0],
        'drip_share':[0.25,0]})
    eff = pd.DataFrame({'technology':['surface','sprinkler','drip'],
        'final_delivery_efficiency':[0.42,0.7125,0.855]})
    return master,overlay,iwr,tech,eff


class FableCHistoricalExportTests(unittest.TestCase):
    def build(self, inputs=None):
        return m.build_fablec_tables(*(inputs or fixture()), require_global_products=False)

    def test_overlay_and_pinapple_and_key_universe(self):
        spam,iwr,gross,excluded,report=self.build()
        self.assertEqual(len(spam),3)
        self.assertEqual(spam.loc[0,'Crop'],'pinapple')
        self.assertAlmostEqual(spam.loc[0,'irrigated_harvested'],0.12)
        self.assertAlmostEqual(spam.loc[0,'rainfed_harvested'],0.3)
        self.assertAlmostEqual(spam.loc[0,'harvesting_intensity_irrigated'],1.1)
        self.assertEqual(len(excluded),1)
        self.assertEqual(excluded.iloc[0]['country_iso3'],'IND')
        self.assertTrue(spam[m.PUBLIC_KEYS].equals(iwr[m.PUBLIC_KEYS]))
        self.assertEqual(report['positive_area_missing_iwr'],0)

    def test_net_and_gross_per_hectare_without_area_double_count(self):
        spam,iwr,gross,excluded,report=self.build()
        net=float(iwr.loc[iwr.Crop.eq('pinapple'),'Requirement_ha'].iloc[0])
        self.assertEqual(net,4000)
        multiplier=0.5/.42+0.25/.7125+0.25/.855
        row=gross.loc[gross.Crop.eq('pinapple')].iloc[0]
        self.assertAlmostEqual(row['gross_multiplier'],multiplier)
        self.assertAlmostEqual(row['gross_requirement_m3_ha_yr'],4000*multiplier)
        self.assertEqual(report['efficiencies'],m.EFF)

    def test_blank_not_zero_and_valid_explicit_zero(self):
        spam,iwr,gross,excluded,report=self.build()
        wheat0=iwr[(iwr.Crop=='wheat')&(iwr.Year==2000)].iloc[0]
        wheat5=iwr[(iwr.Crop=='wheat')&(iwr.Year==2005)].iloc[0]
        self.assertTrue(pd.isna(wheat0.Requirement_ha))
        self.assertEqual(float(wheat5.Requirement_ha),0)
        self.assertEqual(report['blank_iwr_states_retained'],1)
        self.assertEqual(report['zero_iwr_states_retained'],1)

    def test_positive_area_without_net_is_rejected(self):
        x=list(fixture())
        x[2]=x[2].copy()
        x[2].loc[x[2].fable_product.eq('pinapple'),'iwr_m3_ha_yr']=np.nan
        with self.assertRaisesRegex(ValueError,'Positive irrigated'):
            self.build(x)

    def test_missing_shares_rejected_for_positive_area(self):
        x=list(fixture());x[3]=x[3].iloc[:1].copy()
        with self.assertRaisesRegex(ValueError,'Positive irrigated'):
            self.build(x)

    def test_share_sums_and_efficiency_freeze(self):
        x=list(fixture());x[3]=x[3].copy();x[3].loc[0,'surface_share']=0.6
        with self.assertRaisesRegex(ValueError,'sum to one'):
            self.build(x)
        y=list(fixture());y[4]=y[4].copy();y[4].loc[0,'final_delivery_efficiency']=0.5
        with self.assertRaisesRegex(ValueError,'scientific approval'):
            self.build(y)

    def test_no_blind_rcp_collapse_from_net_master(self):
        self.assertNotIn('pathway',m.KEYS)
        self.assertNotIn('RCP26',m.build_fablec_tables.__doc__)

    def test_numerical_reference_comparison_fails_mismatch(self):
        _,out,_,_,_=self.build()
        same=m.compare_export(out,out.copy(),'IWR')
        self.assertEqual(same['status'],'PASS_NUMERIC_REFERENCE_MATCH')
        modified=out.copy();modified.loc[0,'Requirement_ha']=999
        bad=m.compare_export(out,modified,'IWR')
        self.assertEqual(bad['status'],'FAIL_NUMERIC_REFERENCE_MISMATCH')
        self.assertEqual(bad['mismatch_counts']['Requirement_ha'],1)



# Additional, non-destructive exports for the operational Calculator input tables.
class CanonicalCalculatorInputTests(unittest.TestCase):
    def test_three_standalone_tables_and_units(self):
        _, historical, _, _, _ = m.build_fablec_tables(*fixture(), require_global_products=False)
        approved = m.build_calculator_inputs(historical, fixture()[3], fixture()[4])
        self.assertEqual(set(approved), {m.NET_CALC_NAME,m.SHARES_CALC_NAME,m.EFF_CALC_NAME})
        net=approved[m.NET_CALC_NAME]
        self.assertEqual(list(net),['country_iso3','year','fable_product','net_iwr_mm_yr','net_iwr_m3_ha_yr'])
        pinapple=net.loc[net.fable_product.eq('pinapple')].iloc[0]
        self.assertAlmostEqual(pinapple.net_iwr_m3_ha_yr,4000)
        self.assertAlmostEqual(pinapple.net_iwr_mm_yr,400)
        self.assertTrue(pd.isna(net.loc[net.year.eq(2000)&net.fable_product.eq('wheat'),'net_iwr_mm_yr'].iloc[0]))
        self.assertEqual(float(net.loc[net.year.eq(2005),'net_iwr_m3_ha_yr'].iloc[0]),0)
        tech=approved[m.SHARES_CALC_NAME]
        self.assertEqual(len(tech),2)
        self.assertEqual(list(tech), ['country_iso3','year']+m.SHARE_COLS)
        eff=approved[m.EFF_CALC_NAME]
        self.assertEqual(dict(zip(eff.technology,eff.final_delivery_efficiency)),m.EFF)

    def test_standalone_export_requires_complete_technology(self):
        _,historical,_,_,_=m.build_fablec_tables(*fixture(), require_global_products=False)
        shares=fixture()[3].copy()
        shares.loc[1,m.SHARE_COLS]=np.nan
        with self.assertRaisesRegex(ValueError,'blank shares'):
            m.build_calculator_inputs(historical,shares,fixture()[4])

    def test_extra_exports_do_not_change_original_fable3_schema(self):
        import tempfile
        _,iwr,gross,excluded,report=m.build_fablec_tables(*fixture(), require_global_products=False)
        spam=m.build_fablec_tables(*fixture(), require_global_products=False)[0]
        canonical=m.build_calculator_inputs(iwr,fixture()[3],fixture()[4])
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)
            m.save_output(dest,spam,iwr,gross,excluded,report,canonical)
            self.assertEqual(list(pd.read_csv(dest/m.IWR_NAME)),
                             ['CountryISO','Year','Crop','Requirement_ha','Sur_shr','Spin_shr','Drip_shr'])
            for fname in canonical:
                self.assertTrue((dest/fname).is_file())
            with self.assertRaisesRegex(FileExistsError,'already exists'):
                m.save_output(dest,spam,iwr,gross,excluded,report,canonical)

if __name__=='__main__':
    unittest.main()
