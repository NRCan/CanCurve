'''
Created on Apr. 28, 2024

@author: cef
'''
import pytest, os, shutil, random

from cancurve.hp.basic import find_single_file_by_extension

from cancurve.bldgs.parameters_ui import building_details_options_d


#===============================================================================
# data
#===============================================================================
from tests.conftest import test_data_dir_master as parent_tdata_dir
test_data_dir_master = os.path.join(parent_tdata_dir, 'bldgs')

#===============================================================================
# fixtrues--------
#===============================================================================
@pytest.fixture(scope='function')   
def proj_db_fp(testCase, testPhase, tmp_path):
    """retrieve the approraite project database file for hte test case (and make a copy)"""
    
    #get the target directory
    tdata_dir = os.path.join(test_data_dir_master, testCase, testPhase)
    assert os.path.exists(tdata_dir)
    
    #get the project db file
    fp = find_single_file_by_extension(tdata_dir, '.cancurve')
    
    #make a working copy        
    return shutil.copy(fp,os.path.join(tmp_path, 'copy_'+os.path.basename(fp)))


@pytest.fixture(scope='function')
def ci_fp(testCase):
    """cost item filepath retrival by testCase name"""
    tdata_dir = os.path.join(test_data_dir_master, testCase)    
    return find_single_file_by_extension(tdata_dir, '.csv')


@pytest.fixture(scope='function')
def fixed_costs_d(testCase):
    return {
        'case1':{0:10000, -1:8000},
        'case2':None,        
        }[testCase]
        
        
@pytest.fixture(scope='function')
def bldg_meta_d(testCase):
    
    #just take first from parameters
    case1_d = {k:v[0] for k,v in building_details_options_d.items()}
    
    #random choice
    case2_d = {k: random.choice(v) for k, v in building_details_options_d.items()}
    
    return {
        'case1':case1_d,
        'case2':case2_d,        
        }[testCase]