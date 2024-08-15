'''
Created on Aug. 15, 2024

@author: cef
'''



import pytest, os, shutil, pickle

import pandas as pd

#===============================================================================
# test data
#===============================================================================
from misc.DDFP_compare import ddfp_lib_fp_d

#===============================================================================
# fixtures-------
#===============================================================================
@pytest.fixture(scope='function')
def curve_data_dir(study_name, ddf_name):
    return os.path.join(os.path.dirname(ddfp_lib_fp_d[study_name]), ddf_name)
#===============================================================================
# tests---------
#===============================================================================



@pytest.mark.dev
@pytest.mark.parametrize('study_name, ddf_name',[
    ('AB.Calgary', 'R_2-L-BD-CU_ABCA'),
    ])
#===============================================================================
# @pytest.mark.parametrize('fixed_costs_d',[
#     {0:10000, -1:8000},
#     None,
#     #pytest.param({0:10000, -2:8000}, marks=pytest.mark.xfail(raises=KeyError, reason="bad story")), 
#     ])
#===============================================================================
def test_ddfp_inputs_to_ci_from_dir(curve_data_dir, tmpdir, logger):
    from misc.DDFP_compare import ddfp_inputs_to_ci_from_dir as func
    
    result = func(curve_data_dir, logger=logger, out_dir=tmpdir)