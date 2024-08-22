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


#===============================================================================
# fixtrues--------
#===============================================================================

 


@pytest.fixture(scope='function')   
def proj_db_fp(testCase, testPhase, tmp_path):
    """retrieve the approraite project database file for hte test case (and make a copy)"""
    
    #get the target directory
    tdata_dir = os.path.join(test_data_dir_master, testCase, testPhase)
    assert os.path.exists(tdata_dir), tdata_dir
    
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
    if not testCase in fixed_costs_master_d:
        raise AssertionError(f'test case \'{testCase}\' missing from fixed_costs_master_d')
    return fixed_costs_master_d[testCase]
        




@pytest.fixture(scope='function')
def bldg_meta_d(testCase):
    from tests.data.bldgs_data_scripts import bldg_meta_rqmt_df_test
    
    d = _get_bldg_meta_d(testCase, df=bldg_meta_rqmt_df_test)
    return d
  
#===============================================================================
# @pytest.fixture(scope='function')
# def bldg_meta_d_ui(testCase):
#     """full set of parameters for the UI"""    
#     
#     if testCase=='case1':
#         #just take first from parameters
#         d = {k:v[0] for k,v in building_details_options_d.items()}
#     
#     elif testCase=='case2':
#     
#         #random choice
#         d = {k: random.choice(v) for k, v in building_details_options_d.items()}
#     
#     """
#     for k,v in d.items():
#         print(f'{k}\n    {v} ({type(v)})')
#     """
#     return d
# 
#  
# @pytest.fixture(scope='function')
# def bldg_meta_d_strict(testCase):
#     """strict building meta parameters needed by core"""
#     return {'basement_height_m':1.8, 'scale_value_m2':232.0, 'bldg_layout':'default'}
#===============================================================================