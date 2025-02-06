'''
Created on Aug. 15, 2024

@author: cef
'''



import pytest, os, shutil, pickle

import pandas as pd
from .conftest import test_data_dir_master
from .bldgs.conftest import ci_fp, fixed_costs_d, bldg_meta_d

from definitions import test_data_dir as test_data_dir_master
test_data_dir_master = os.path.join(test_data_dir_master, 'misc')
#===============================================================================
# test data
#===============================================================================
from misc.DDFP_compare import ddfp_lib_fp_d


#===============================================================================
# helpers----
#===============================================================================
def _get_ddf(study_name, ddf_name, framework_name):
    fp = os.path.join(test_data_dir_master, study_name, ddf_name, framework_name+'.pkl')
    assert os.path.exists(fp), fp
    print(f'loading from \n    {fp}')
    
    return pd.read_pickle(fp)

#===============================================================================
# fixtures-------
#===============================================================================
@pytest.fixture(scope='function')
def curve_data_dir(study_name, ddf_name):
    curve_path = os.path.join(os.path.dirname(ddfp_lib_fp_d[study_name]), ddf_name)
    assert os.path.exists(curve_path), f'failed to get a real path for \'{study_name}\' and \'{ddf_name}\''
    return curve_path

@pytest.fixture(scope='function')
def ddf_d(study_name, ddf_name):
    CC_df = _get_ddf(study_name, ddf_name, 'CC')
    DDFP_df = _get_ddf(study_name, ddf_name, 'DDFP')
    
    return {'DDFP':DDFP_df, 'CC':CC_df}
    

@pytest.fixture(scope='function')
def ci_df(ci_fp):
    
    from cancurve.bldgs.core import load_ci_df 
    
    return load_ci_df(ci_fp)
#===============================================================================
# tests---------
#===============================================================================




@pytest.mark.parametrize('study_name, ddf_name',[
    ('AB.Calgary', 'R_2-L-BD-CU_ABCA'),
    ])
def test_ddfp_inputs_to_ci_from_dir(curve_data_dir, tmpdir, logger):
    from misc.DDFP_compare import ddfp_inputs_to_ci_from_dir as func
    
    result = func(curve_data_dir, logger=logger, out_dir=tmpdir)

 
@pytest.mark.parametrize('study_name, ddf_name',[
    ('AB.Calgary', 'R_2-M-BU-ST_ABCA'),
    ])
def test_plot_and_eval_ddfs(ddf_d, tmpdir, logger):
    from misc.DDFP_compare import plot_and_eval_ddfs as func
    
    func(ddf_d, log=logger, out_dir=tmpdir)
    
    
#===============================================================================
# file-based tests ------
#===============================================================================
from .data.bldgs_data_scripts import load_tests_cases_from_file, test_cases_l
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
    
    func(ci_df, bldg_meta_d=bldg_meta_d, fixed_costs_d=fixed_costs_d,
         #settings_d=settings_d, #use default 
          curve_name=f'{testCase}_c00',
         logger=logger, out_dir=tmpdir,
         plot=False,
         )
    
    
    
    
    
    
    
    
    
