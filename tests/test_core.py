'''
Created on Apr. 16, 2024

@author: cef


tests for the core module
'''

import pytest, os, shutil, pickle

import pandas as pd


from tests.conftest import find_single_file_by_extension, src_dir, test_data_dir_master
 



#===============================================================================
# helpers
#===============================================================================
def write_pick(result, ofp, write=False):
    if write:
        if not os.path.exists(os.path.dirname(ofp)):
            os.makedirs(os.path.dirname(ofp))
        with open(ofp, 'wb') as file:
            pickle.dump(result, file)
        print(f'wrote result to \n    {ofp}')
        
        
def copy_sqlite(proj_db_fp, testCase, destinationPhase, write=False):
    
    if write:
        dest_fp = os.path.join(test_data_dir_master, testCase, destinationPhase, os.path.basename(proj_db_fp))
        
        if not os.path.exists(os.path.dirname(dest_fp)):os.makedirs(os.path.dirname(dest_fp))
        
        shutil.copy(proj_db_fp, dest_fp)
        
        print(f'coipied sqlite database to \n    {dest_fp}')

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




@pytest.mark.parametrize('testCase',[
    'case1',
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
    
    #write results 
    write_pick(result, os.path.join(test_data_dir_master, testCase,'c00', 'c00_setup_project_result.pkl'))
    copy_sqlite(result[2], testCase, 'c01')

    
    
@pytest.mark.dev
@pytest.mark.parametrize('testCase',[
    'case1',
    pytest.param('case2', marks=pytest.mark.xfail(raises=KeyError, reason="this case is missing some DRF entries")), 
    ], indirect=False)
@pytest.mark.parametrize('testPhase',['c01'], indirect=False)
def test_c01_join_drf(proj_db_fp, tmp_path, testCase, testPhase):
    from cancurve.core import c01_join_drf as func   
 
    result = func(proj_db_fp)
    
    print(f'finished at\n    {tmp_path}')
    
    write_pick(result, os.path.join(test_data_dir_master, testCase,testPhase, 'c01_join_drf.pkl'))
    copy_sqlite(proj_db_fp, testCase, 'c02')
     
     
 

@pytest.mark.parametrize('testCase',['case1'], indirect=False)
@pytest.mark.parametrize('testPhase',['c02'], indirect=False)
@pytest.mark.parametrize('scale_m2',[None, 
                                     #True, False
                                     ], indirect=False)
def test_c02_group_story(proj_db_fp, scale_m2, testCase, testPhase, tmp_path):
    from cancurve.core import c02_group_story as func 
      
    result = func(proj_db_fp, scale_m2=scale_m2)
    
    print(f'finished at\n    {tmp_path}')
    
    write_pick(result, os.path.join(test_data_dir_master, testCase,testPhase, 'c02_group_story.pkl'))
    copy_sqlite(proj_db_fp, testCase, 'c03')
    
    
    
    
    
