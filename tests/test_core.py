'''
Created on Apr. 16, 2024

@author: cef


tests for the core module
'''

import pytest, os, shutil

import pandas as pd

from cancurve.hp.basic import find_single_file_by_extension
from cancurve.parameters import src_dir

 

#===============================================================================
# data
#===============================================================================
test_data_dir_master = os.path.join(src_dir, 'tests', 'data')

#===============================================================================
# fixtures-------
#===============================================================================
 

@pytest.fixture(scope='function')
def ci_fp(testCase):
    """cost item filepath retrival by testCase name"""
    tdata_dir = os.path.join(test_data_dir_master, testCase)    
    return find_single_file_by_extension(tdata_dir, '.csv')
    
    
    


#===============================================================================
# tests---------
#===============================================================================
@pytest.mark.dev
def test_c00_setup_project( tmp_path):
    from cancurve.core import c00_setup_project as func
    func(out_dir=tmp_path, bldg_meta={'testFeat1':'v1', 'testFeat2':'v2'})
    
    

@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_c01_join_drf(ci_fp, tmp_path):
    from cancurve.core import c01_join_drf as func
    func(ci_fp, out_dir=tmp_path)