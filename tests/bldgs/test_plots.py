'''
Created on Apr. 24, 2024

@author: cef

test for plotters
'''


import pytest, os, shutil, pickle

import pandas as pd

from unittest.mock import patch 


from .conftest import find_single_file_by_extension, test_data_dir_master


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
# helpers-----
#===============================================================================
def write_fig(figure, ofp, write=True):
    if write:
        figure.savefig(ofp, format='svg')
        print(f'wrote figure to \n    {ofp}')


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
    assert os.path.exists(tdata_dir), tdata_dir
    
    fp = find_single_file_by_extension(tdata_dir, '.pkl')
    
    with open(fp, 'rb') as file:
        return pickle.load(file)
    

 
    
    
    


#===============================================================================
# tests---------
#===============================================================================
@pytest.mark.dev
@pytest.mark.parametrize('testPhase',['c00'], indirect=False)
@pytest.mark.parametrize('testCase',[
    'case1',
    'case2'
    ], indirect=False)
def test_plot_c00_costitems(action_result, tmp_path):
    ci_df, _, _ , _= action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c00_costitems as func
    
    figure = func(ci_df)
    
    write_fig(figure, os.path.join(tmp_path, 'plot_c00_costitems.svg'))
    

    
    
 
@pytest.mark.parametrize('testPhase',['c00'], indirect=False)
@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_plot_c00_DRF(action_result, tmp_path):
    _, drf_df, _, _ = action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c00_DRF as func
    
    figure = func(drf_df)
 
    write_fig(figure, os.path.join(tmp_path, 'plot_c00_DRF.svg'))
    
    

 
@pytest.mark.parametrize('testPhase',['c01'], indirect=False)
@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_plot_c01_depth_rcv(action_result, tmp_path):
    data = action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c01_depth_rcv as func
    
    figure = func(data)
    
    write_fig(figure, os.path.join(tmp_path, 'plot_c01_depth_rcv.svg'))
    
    

@pytest.mark.dev
@pytest.mark.parametrize('testPhase',['c02'], indirect=False)
@pytest.mark.parametrize('testCase',['case1'], indirect=False)
def test_plot_c02_ddf(action_result, tmp_path):
    data = action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c02_ddf as func
    
    figure = func(data)
    
    write_fig(figure, os.path.join(tmp_path, 'plot_c02_ddf.svg'))
    
    
    
    
    
    
    
    
    
    
    
    
    
    