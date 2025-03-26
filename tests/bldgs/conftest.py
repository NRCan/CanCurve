'''
Created on Apr. 28, 2024

@author: cef
'''
import pytest, os, shutil, random, logging, sys

 
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
# helpers--------
#===============================================================================
def _get_bldg_meta_d(testCase, df=None):
    """retrieve the bldg_meta_d from the 'bldg_meta_rqmts.csv
    just those entries in 'varName_core' column
    """
    if testCase in df.columns:
        d = df.loc[:, ['varName_core', testCase]].dropna().set_index('varName_core').iloc[:, 0].to_dict()
    else:
        raise KeyError(f'failed to find \'{testCase}\' in bldg_meta_rqmt_df_test')
    d = {k:convert_to_float(v) for k, v in d.items()}
    assert_bldg_meta_d(d, msg=testCase)
    return d

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
def expo_units(bldg_meta_d):
    return bldg_meta_d['expo_units']


@pytest.fixture(scope='function')
def bldg_meta_d(testCase):
    """build a dict from the 'bldg_meta_rqmts.csv' for this case"""
    
    #get a copy of the 'bldg_meta_rqmts.csv' as a dataframe
    from tests.data.bldgs_data_scripts import bldg_meta_rqmt_df_test 
 
    #extract dictionary for this case
    return _get_bldg_meta_d(testCase, df=bldg_meta_rqmt_df_test)
  


if __name__=='__main__':
    print(f'finished running conftest.py')