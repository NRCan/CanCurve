'''
Created on Mar 3, 2025

@author: cef
'''

import pytest, os, shutil, pickle
from .conftest import ci_fp, fixed_costs_d, bldg_meta_d
from tests.test_misc import ci_df

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
    print(f'starting test for {testCase}\n===========================\n\n')
    func(ci_df, bldg_meta_d=bldg_meta_d, fixed_costs_d=fixed_costs_d,
         #settings_d=settings_d, #use settings_default_d
          curve_name=f'{testCase}_c00',
         logger=logger, out_dir=tmpdir,
         plot=False,
         )