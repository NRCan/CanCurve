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
    
    #get the target directory
    tdata_dir = os.path.join(test_data_dir_master, testCase, testPhase)
    assert os.path.exists(tdata_dir)
    
    #get the project db file
    fp = find_single_file_by_extension(tdata_dir, '.cancurve')
    
    #make a working copy        
    return shutil.copy(fp,os.path.join(tmp_path, 'copy_'+os.path.basename(fp)))


#===============================================================================
# tests---------
#===============================================================================
@pytest.mark.dev
@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_c00_setup_project(tmp_path, ci_fp, testCase):
    from cancurve.core import c00_setup_project as func
    func(ci_fp, 
         out_dir=tmp_path, 
         bldg_meta={'basement_height_m':1.8, 'mf_area_m2':232.0},
         #settings_d = {'scale_m2':True}, 
         curve_name=f'{testCase}_c00',
         ofp=os.path.join(tmp_path, f'{testCase}_c00.cancurve'))
    
    
    print(f'finished at\n    {tmp_path}')
    

@pytest.mark.parametrize('testCase',['case1'], indirect=False)
@pytest.mark.parametrize('testPhase',['c01'], indirect=False)
def test_c01_join_drf(proj_db_fp, tmp_path):
    from cancurve.core import c01_join_drf as func   
 
    func(proj_db_fp)
    
    print(f'finished at\n    {tmp_path}')
     
     
 

@pytest.mark.parametrize('testCase',['case1'], indirect=False)
@pytest.mark.parametrize('testPhase',['c02'], indirect=False)
@pytest.mark.parametrize('scale_m2',[None, True, False], indirect=False)
def test_c02_group_story(proj_db_fp, scale_m2):
    from cancurve.core import c02_group_story as func     
 
      
    func(proj_db_fp, scale_m2=scale_m2)
