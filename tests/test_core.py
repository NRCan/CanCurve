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
def proj_db_fp(testCase, testPhase, tmp_path):
    fp = find_single_file_by_extension(test_data_dir_master, '.cancurve')
    
    proj_db_fp = shutil.copy(
        os.path.join(test_data_dir_master, 'c00.cancurve'), 
        os.path.join(tmp_path, 'c01.cancurve'))
        
    return shutil.copy(fp, os.path.join(tmp_path, os.path.basename(fp)))


#===============================================================================
# tests---------
#===============================================================================

@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_c00_setup_project(tmp_path, ci_fp, testCase):
    from cancurve.core import c00_setup_project as func
    func(ci_fp, 
         out_dir=tmp_path, 
         bldg_meta={'mf_height_m':1.8, 'mf_area_m2':232.0}, 
         curve_name=f'{testCase}_c00',
         ofp=os.path.join(tmp_path, f'{testCase}_c00.cancurve'))
    
    
@pytest.mark.dev
@pytest.mark.parametrize('testCase',['case1'], indirect=False)
@pytest.mark.parametrize('testPhase',['c01'], indirect=False)
def test_c01_join_drf(tmp_path, proj_db_fp):
    from cancurve.core import c01_join_drf as func   
 
    func(ci_fp, proj_db_fp, out_dir=tmp_path)
     
     
 
 
def test_c02_group_story(tmp_path):
    from cancurve.core import c02_group_story as func     
  
    #get a copy of the project database
    proj_db_fp = shutil.copy(
        os.path.join(test_data_dir_master, 'c01.cancurve'), 
        os.path.join(tmp_path, 'c02.cancurve'))
      
    func(ci_fp, proj_db_fp, out_dir=tmp_path)
