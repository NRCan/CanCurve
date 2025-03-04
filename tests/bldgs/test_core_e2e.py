'''
Created on Mar 3, 2025

@author: cef
'''

import pytest, os, shutil, pickle
from .conftest import ci_fp, fixed_costs_d, bldg_meta_d
from tests.test_misc import ci_df
from cancurve.hp.basic import get_out_dir, convert_to_float

#===============================================================================
# file-based tests ------
#===============================================================================
from ..data.bldgs_data_scripts import load_tests_cases_from_file, test_cases_l
load_tests_cases_from_file() #setup file-based test cases



@pytest.mark.dev
@pytest.mark.parametrize('testCase',
    #['case4_R2']
     test_cases_l,    
    )
def test_bldgs_workflow(testCase, 
                        ci_df, bldg_meta_d,fixed_costs_d,  #from conftest based on testCase                       
                        tmpdir, logger):
    """end-to-end backend testing"""
    from misc.bldgs_script_example import bldgs_workflow as func
    
    if bldg_meta_d is None:
        
        #get meta from test cases
        from cancurve.bldgs.parameters import bldg_meta_rqmt_df
        """
        view(bldg_meta_rqmt_df)
        """
        d = bldg_meta_rqmt_df.loc[:, ['varName_core', 'case1']].dropna().set_index('varName_core').iloc[:, 0].to_dict()
        d = {k:convert_to_float(v) for k,v in d.items()}
        
        
    print(f'starting test for {testCase}\n===========================\n\n')
    func(ci_df, bldg_meta_d=bldg_meta_d, fixed_costs_d=fixed_costs_d, 
         #settings_d=settings_d, #use settings_default_d
          curve_name=f'{testCase}_c00',
         logger=logger, out_dir=tmpdir,
         plot=False,
         )