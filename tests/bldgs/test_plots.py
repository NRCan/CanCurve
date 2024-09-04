'''
Created on Apr. 24, 2024

@author: cef

test for plotters
'''


import pytest, os, shutil, pickle

import pandas as pd

from unittest.mock import patch 

import matplotlib.pyplot as plt

from .conftest import find_single_file_by_extension, test_data_dir_master


#===============================================================================
# data---------
#===============================================================================
from ..data.bldgs_data_scripts import load_tests_cases_from_file, test_cases_l
load_tests_cases_from_file(
    #===========================================================================
    # caseName_l = [ #only loading a few for unit tests
    #      'AB-Calgary_R_1-L-C-ST_ABCA' 
    #     ]
    #===========================================================================
    ) #setup file-based test cases


#===============================================================================
# helpers-----
#===============================================================================
def write_fig(figure, ofp, write=True, log=None):
    if write:
        figure.savefig(ofp, format='svg')
        if not log is None:
            log.info(f'wrote figure to \n    {ofp}')
        
    plt.close('all')


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
    if not os.path.exists(tdata_dir):
        raise FileNotFoundError(tdata_dir)
    
    fp = find_single_file_by_extension(tdata_dir, '.pkl')
    
    with open(fp, 'rb') as file:
        return pickle.load(file)
    

 
    
    
    


#===============================================================================
# tests---------
#===============================================================================
@pytest.mark.dev
@pytest.mark.parametrize('testPhase',['c00'], indirect=False)
@pytest.mark.parametrize('testCase',test_cases_l, indirect=False)
def test_plot_c00_costitems(action_result, tmp_path, logger):
    ci_df, _, _ , _= action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c00_costitems as func
    
    figure = func(ci_df, log=logger)
    
    write_fig(figure, os.path.join(tmp_path, 'plot_c00_costitems.svg'), log=logger)
    

    
    
 
@pytest.mark.parametrize('testPhase',['c00'], indirect=False)
@pytest.mark.parametrize('testCase',test_cases_l, indirect=False)
def test_plot_c00_DRF(action_result, tmp_path, logger):
    _, drf_df, _, _ = action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c00_DRF as func
    
    figure = func(drf_df, log=logger)
 
    write_fig(figure, os.path.join(tmp_path, 'plot_c00_DRF.svg'), log=logger)
    
    

 
@pytest.mark.parametrize('testPhase',['c01'], indirect=False)
@pytest.mark.parametrize('testCase',test_cases_l, indirect=False)
def test_plot_c01_depth_rcv(action_result, tmp_path, logger):
    data = action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c01_depth_rcv as func
    
    figure = func(data, log=logger)
    
    write_fig(figure, os.path.join(tmp_path, 'plot_c01_depth_rcv.svg'), log=logger)
    
    

@pytest.mark.dev
@pytest.mark.parametrize('testPhase',['c02'], indirect=False)
@pytest.mark.parametrize('testCase',test_cases_l, indirect=False)
def test_plot_c02_ddf(action_result, tmp_path, logger):
    data = action_result #c00 returns both of these
    
    from cancurve.bldgs.plots import plot_c02_ddf as func
    
    figure = func(data, log=logger)
    
    write_fig(figure, os.path.join(tmp_path, 'plot_c02_ddf.svg'), log=logger)
    
    
    
    
    
    
    
    
    
    
    
    
    
    