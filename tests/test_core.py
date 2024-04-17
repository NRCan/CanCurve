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
    
@pytest.fixture(scope='function')   
def proj_db_fp(tmp_path):
    fp = find_single_file_by_extension(test_data_dir_master, '.cancurve')
    return shutil.copy(fp, os.path.join(tmp_path, os.path.basename(fp)))


#===============================================================================
# tests---------
#===============================================================================

def test_c00_setup_project(tmp_path):
    from cancurve.core import c00_setup_project as func
    func(out_dir=tmp_path, bldg_meta={'mf_height_m':1.8, 'mf_area_m2':232.0}, curve_name='c00')
    
    
@pytest.mark.dev
@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_c01_join_drf(ci_fp, proj_db_fp, tmp_path):
    from cancurve.core import c01_join_drf as func   
    

    #get a copy of the project database
    proj_db_fp = shutil.copy(
        os.path.join(test_data_dir_master, 'c00_20240416.cancurve'), 
        os.path.join(tmp_path, 'c00.cancurve'))
    
    func(ci_fp, proj_db_fp, out_dir=tmp_path)