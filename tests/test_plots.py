'''
Created on Apr. 24, 2024

@author: cef

test for plotters
'''


import pytest, os, shutil, pickle

import pandas as pd

from tests.conftest import find_single_file_by_extension, src_dir, test_data_dir_master


#===============================================================================
# data
#===============================================================================
#===============================================================================
# test_data_dir_master = os.path.join(src_dir, 'tests', 'data')
# 
# def get_sqlite_table(proj_db_fp, table_name, **kwargs):
#     with sqlite3.connect(proj_db_fp) as conn:
#         return pd.read_sql(f'SELECT * FROM {table_name}', conn, **kwargs)
#===============================================================================

#===============================================================================
# fixtures-------
#===============================================================================
#===============================================================================
# @pytest.fixture(scope='function')
# def c00_cost_items_df(proj_db_fp):
#     return get_sqlite_table(proj_db_fp, 'c00_cost_items', index_col=['cat', 'sel'])
#===============================================================================
@pytest.fixture(scope='function')
def action_result(testCase, testPhase):
    """intelligently retrieve result for this case and phase from test_core"""
    
    tdata_dir = os.path.join(test_data_dir_master, testCase, testPhase)
    assert os.path.exists(tdata_dir)
    
    fp = find_single_file_by_extension(tdata_dir, '.pkl')
    
    with open(fp, 'rb') as file:
        return pickle.load(file)
    
    
    


#===============================================================================
# tests---------
#===============================================================================
@pytest.mark.dev
@pytest.mark.parametrize('testPhase',['c00'], indirect=False)
@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_plot_c00_costitems(action_result, tmp_path):
    ci_df, drf_df = action_result #c00 returns both of these
    
    from cancurve.plots import plot_c00_costitems as func
    
    fig = func(ci_df)