'''
Created on Apr. 16, 2024

@author: cef


tests for the core module
'''

import pytest, os, shutil, pickle

import pandas as pd


from tests.conftest import find_single_file_by_extension, src_dir, test_data_dir_master
 



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
@pytest.mark.parametrize('testCase',[
    #'case1',
    'case2',
    ], indirect=False)
def test_c00_setup_project(tmp_path, ci_fp, testCase):
    from cancurve.core import c00_setup_project as func
    
    result = func(ci_fp, 
         out_dir=tmp_path, 
         bldg_meta={'basement_height_m':1.8, 'mf_area_m2':232.0},
         #settings_d = {'scale_m2':True}, 
         curve_name=f'{testCase}_c00',
         ofp=os.path.join(tmp_path, f'{testCase}_c00.cancurve'))
    
    
    print(f'finished at\n    {tmp_path}')
    
    #write result pickle

    ofp = os.path.join(test_data_dir_master, testCase,'c00', 'c00_setup_project_result.pkl')
     
    if not os.path.exists(os.path.dirname(ofp)):os.makedirs(os.path.dirname(ofp))
     
    with open(ofp, 'wb') as file:
        pickle.dump(result, file)
    print(f'wrote result to \n    {ofp}')

    
    

@pytest.mark.parametrize('testCase',['case1'], indirect=False)
@pytest.mark.parametrize('testPhase',['c01'], indirect=False)
def test_c01_join_drf(proj_db_fp, tmp_path, testCase, testPhase):
    from cancurve.core import c01_join_drf as func   
 
    result = func(proj_db_fp)
    
    print(f'finished at\n    {tmp_path}')
    
    #===========================================================================
    # #write result
    # ofp = os.path.join(test_data_dir_master, testCase,testPhase, 'c01_join_drf_result.pkl')
    # with open(ofp, 'wb') as file:
    #     pickle.dump(result, file)
    # print(f'wrote result to \n    {ofp}')
    #===========================================================================
     
     
 

@pytest.mark.parametrize('testCase',['case1'], indirect=False)
@pytest.mark.parametrize('testPhase',['c02'], indirect=False)
@pytest.mark.parametrize('scale_m2',[None, 
                                     #True, False
                                     ], indirect=False)
def test_c02_group_story(proj_db_fp, scale_m2, testCase, testPhase):
    from cancurve.core import c02_group_story as func 
      
    result = func(proj_db_fp, scale_m2=scale_m2)
    
    
    #write result
    ofp = os.path.join(test_data_dir_master, testCase,testPhase, 'c02_group_story_result.pkl')
    with open(ofp, 'wb') as file:
        pickle.dump(result, file)
    print(f'wrote result to \n    {ofp}')
