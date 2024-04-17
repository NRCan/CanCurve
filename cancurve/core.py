'''
Created on Apr. 16, 2024

@author: cef

core join, group, and scaling source code
'''
import os, sys
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

from .hp.logr import get_log_stream
from .hp.basic import view_web_df as view
from .parameters import drf_db_master_fp, colns_index, today_str
from .assertions import assert_ci_df, assert_drf_db, assert_drf_df, assert_proj_db_fp, assert_proj_db
from cancurve import __version__
 
def get_od(name):
    out_dir = os.path.join(out_base_dir, 'fines', name)
    if not os.path.exists(out_dir):os.makedirs(out_dir)
    return out_dir

def get_slog(name, log):
    if log is None:
        log = get_log_stream()
        
    return log.getChild(name)

def get_curve_name(conn):
    """
    Retrieves the first curve name from the 'project_meta' table.

    Args:
        conn: An open SQLite database connection.

    Returns:
        The first 'curve_name' value, or None if the table or column doesn't exist. 
    """
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT curve_name FROM project_meta LIMIT 1")
        result = cursor.fetchone()

        if result:
            return result[0]  # Extract the first item from the result tuple
        else:
            return None

    except sqlite3.Error as e:
        print(f"Error retrieving curve name: {e}")
        return None 

def load_ci_df(fp, log=None):
    
    
    
    
    assert os.path.exists(fp)
    assert fp.endswith('.csv')
    
    log = get_slog('load_ci_df', log)
    
    #load
    log.debug(f'loading costitem table from \n    {fp}')
    ci_df = pd.read_csv(fp, index_col=[0,1])
    
    try:
        assert_ci_df(ci_df)
    except Exception as e:
        log.error(f'the loaded costitem table failed failed some checks\n    {fp}\n    {e}')
        raise e
    
    log.info(f'loaded cost-item table {ci_df.shape}')
    
    return ci_df

def load_drf(fp, log=None):
    """load the DRF table from teh database
    
    TODO: load just the necessary rows (once the database is larger)
    
    """
    
    
    
    #===========================================================================
    # precheck
    #===========================================================================
    assert os.path.exists(fp), fp
    assert fp.endswith('.db')
    
    log = get_slog('load_drf', log)
    
    #===========================================================================
    # load
    #===========================================================================
    with sqlite3.connect(fp) as conn:
        assert_drf_db(conn)
        df_raw =  pd.read_sql('SELECT * FROM drf', conn, index_col=['cat', 'sel', 'bldg_layout'])
        
    #===========================================================================
    # post
    #===========================================================================
    df1 = df_raw.copy()

    df1.columns.name='meters'
    df1.columns = df1.columns.astype('float')
    
    try:
        assert_drf_df(df1)
    except Exception as e:
        log.error(f'the loaded drf table failed failed some checks\n    {fp}\n    {e}')
        raise e
    
    log.info(f'loaded DRF table {df1.shape}')
    
    return df1
    
    
    
    

def _get_proj_meta(log, curve_name=None,function_name=None):
    proj_meta_df = pd.DataFrame({
            'curve_name':[curve_name], 
            #'date':[today_str],
            'now':[datetime.now()], 
            'username':[os.getlogin()], 
            'script_name':[os.path.basename(__file__)],
            'function_name':function_name, 
            'cancurve_version':[__version__], 
            'python_version':[sys.version.split()[0]],
            
            })
    #add qgis
    try:
        from qgis.core import Qgis
        proj_meta_df['qgis_version'] = Qgis.QGIS_VERSION
    except Exception as e:
        log.warning(f'failed to retrieve QGIS version\n    {e}')
    return proj_meta_df

def _update_proj_meta(function_name, log, conn):
    curve_name = get_curve_name(conn)
    proj_meta_df = _get_proj_meta(log, curve_name=curve_name, function_name=function_name)
    proj_meta_df.to_sql('project_meta', conn, if_exists='append', index=False)
    
    log.debug(f'updated \'project_meta\' w/ {proj_meta_df.shape}')
    return proj_meta_df
    
#===============================================================================
# ACTIONS------------
#===============================================================================

def c00_setup_project(
        log=None,
        ofp=None,
        out_dir=None,
        curve_name='curve_name',
        bldg_meta=None,
        
        ):
    """build project SQLite"""
    
    #===========================================================================
    # defaults
    #===========================================================================
 
    
    if out_dir is None: 
        out_dir = os.getcwd()
        
    if bldg_meta is None: bldg_meta=dict()
    assert isinstance(bldg_meta, dict)
        
    log = get_slog('c00', log)
    
    if ofp is None:
        ofp = os.path.join(out_dir, f'{curve_name}_{today_str}.cancurve')
        
    assert not os.path.exists(ofp)
 
    #===========================================================================
    # setup project meta
    #===========================================================================
    proj_meta_df = _get_proj_meta(log, curve_name=curve_name, function_name='c00_setup_project')
    
    #===========================================================================
    # start database
    #===========================================================================
    log.info(f'init project SQLite db at\n    {ofp}')
    with sqlite3.connect(ofp) as conn:
        
        #add project meta
        proj_meta_df.to_sql('project_meta', conn, if_exists='replace', index=False)
        
        #create a table 'bldg_meta' and populate it with the entries in bldg_meta
        pd.Series(bldg_meta, name='val').to_frame().to_sql('bldg_meta', conn, if_exists='replace', index=True)
        
    log.info(f'project SQLiite DB built at \n    {ofp}')
    
    assert_proj_db_fp(ofp)
    
    return ofp
 




def c01_join_drf(
        ci_fp,
        proj_db_fp,
        drf_db_fp=None,
        bldg_layout='default',
        log=None,
        out_dir=None,
        
        
        ):
    """Join DRF db to cost-item csv (creates a ddf for each cost item)
    
    
    Params
    ------------
    ci_fp: str
        filepath to cost-item csv data table
        
    drf_db_fp: str, optional
        filepath to DRF SQLite db
        defaults to drf_db_master_fp 
    """
    
    #===========================================================================
    # defaults
    #===========================================================================
    if drf_db_fp is None: drf_db_fp = drf_db_master_fp
    
    if out_dir is None: 
        out_dir = os.getcwd()
        
    log = get_slog('c01', log)
    
    log.info(f'on {os.path.basename(ci_fp)}')
    
    #===========================================================================
    # prechecks
    #===========================================================================
 
    
    #===========================================================================
    # load costitem table
    #===========================================================================
    ci_df = load_ci_df(ci_fp, log=log)
    
    #===========================================================================
    # load depth-replacement-factor database
    #===========================================================================
    drf_df = load_drf(drf_db_fp, log=log).xs(bldg_layout, level=2)
    
    #===========================================================================
    # check intersect
    #===========================================================================
    bx = np.invert(ci_df.index.isin(drf_df.index))
    if bx.any():
        """TODO: add some support for populating missing entries into the DRF"""
        log.warning(f'missing {bx.sum()}/{len(bx)} entries')
        raise KeyError()
    
    #===========================================================================
    # join
    #===========================================================================
    df1 = ci_df.loc[:, ['rcv', 'story']].join(drf_df)
    
    assert df1.notna().all().all()
    
    #===========================================================================
    # update proejct database
    #===========================================================================
    
    
    log.info(f'adding cost-item w/ DRF table to project database w/ {df1.shape}\n    {proj_db_fp}')
    with sqlite3.connect(proj_db_fp) as conn:
        
        assert_proj_db(conn)
        
        #add result table
        df1.to_sql('ci_drf', conn, if_exists='replace', index=True)
        
        #update project meta
        _update_proj_meta('c01_join_drf', log, conn)
 
        
    log.info(f'finished')
    
    return proj_db_fp
    
    
    """
    view(df1)
    """

    
    
 
    
    
