'''
Created on Aug. 15, 2024

@author: cef
'''



import pytest, os, shutil, pickle

import pandas as pd
from .conftest import test_data_dir_master
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
    return os.path.join(os.path.dirname(ddfp_lib_fp_d[study_name]), ddf_name)

@pytest.fixture(scope='function')
def ddf_d(study_name, ddf_name):
    CC_df = _get_ddf(study_name, ddf_name, 'CC')
    DDFP_df = _get_ddf(study_name, ddf_name, 'DDFP')
    
    return {'DDFP':DDFP_df, 'CC':CC_df}
    


#===============================================================================
# tests---------
#===============================================================================




@pytest.mark.parametrize('study_name, ddf_name',[
    ('AB.Calgary', 'R_2-L-BD-CU_ABCA'),
    ])
def test_ddfp_inputs_to_ci_from_dir(curve_data_dir, tmpdir, logger):
    from misc.DDFP_compare import ddfp_inputs_to_ci_from_dir as func
    
    result = func(curve_data_dir, logger=logger, out_dir=tmpdir)

@pytest.mark.dev
@pytest.mark.parametrize('study_name, ddf_name',[
    ('AB.Calgary', 'R_2-M-BU-ST_ABCA'),
    ])
def test_plot_and_eval_ddfs(ddf_d, tmpdir, logger):
    from misc.DDFP_compare import plot_and_eval_ddfs as func
    
    func(ddf_d, log=logger, out_dir=tmpdir)
    
    
    
    
    
    
    
    
    
