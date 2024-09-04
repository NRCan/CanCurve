'''
Created on Apr. 28, 2024

@author: cef
'''
import pytest, os, shutil, random, logging, sys

from cancurve.bldgs.core import _get_bldg_meta_d
from cancurve.hp.basic import find_single_file_by_extension, convert_to_number, convert_to_float

from cancurve.bldgs.parameters_ui import building_details_options_d
from cancurve.bldgs.assertions import assert_bldg_meta_d
#from cancurve.bldgs.parameters import bldg_meta_rqmt_df


 
#===============================================================================
# data
#===============================================================================
from tests.data.bldgs_data_scripts import fixed_costs_master_d, test_data_dir_master#, bldg_meta_rqmt_df_test


#these cases are setup for unit tests
#end-to-end test cases are in bldgs_data_scripts.test_cases_l
cases_l = [
    'case1',
    'case2',
    'case3',
    'AB-Calgary_R_1-L-C-ST_ABCA'
    ]


#===============================================================================
# fixtrues--------
#===============================================================================

 


@pytest.fixture(scope='function')   
def proj_db_fp(testCase, testPhase, tmp_path):
    """retrieve the approraite project database file for hte test case (and make a copy)"""
    
    #get the target directory
    tdata_dir = os.path.join(test_data_dir_master, testCase, testPhase)
    if not os.path.exists(tdata_dir):
        raise FileNotFoundError(tdata_dir)
    
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
    """retrieve fixed_costs_d from master
    
    normally, fixed_costs_master_d is hard-coded and kept in 
        bldgs.dialog_test_scripts.fixed_costs_master_d
       
    However, this can also be updated using pickels by calling
        tests.data.bldgs_data_scripts.load_tests_cases_from_file()
    """
    
    if not testCase in fixed_costs_master_d:
        raise AssertionError(f'test case \'{testCase}\' missing from fixed_costs_master_d')
    return fixed_costs_master_d[testCase]
        




@pytest.fixture(scope='function')
def bldg_meta_d(testCase):
    from tests.data.bldgs_data_scripts import bldg_meta_rqmt_df_test
    
    d = _get_bldg_meta_d(testCase, df=bldg_meta_rqmt_df_test)
    return d
  


