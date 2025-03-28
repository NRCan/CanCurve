'''
Created on Apr. 16, 2024

@author: cef
'''

import os, warnings
import sqlite3
import pandas as pd

from .parameters import colns_index, colns_dtypes, bldg_meta_rqmt_df
from ..hp.basic import view_web_df as view


expected_tables_base = ['project_meta','project_settings','c00_bldg_meta', 'c00_cost_items','c00_drf']



#===============================================================================
# helpers--------
#===============================================================================
def _assert_sqlite_table_exists(conn, table_name): 
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name, ))
    result = cursor.fetchone()
    if not result:
        raise AssertionError(f"Table '{table_name}' not found in database") # Check if DRF table exists


def assert_ci_df(df, msg=''):
    """
    Asserts that the provided DataFrame conforms to CI data expectations.

    Args:
        df: The DataFrame to check.

    Raises:
        TypeError: If the input is not a DataFrame.
        KeyError: If the DataFrame's index names are incorrect.
        IOError: If an unrecognized column name is found.
        AssertionError: If a column's data type is incorrect.
    """

    # Check if it's a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame")

    # Check index 
    if not set(df.index.names).difference(['category', 'component']) == set():
        raise KeyError(f"Incorrect index names in DataFrame\n    {df.index.names}")

    # Check data types
    for coln, dstr in df.dtypes.items():
        if coln not in colns_dtypes:
            print(f'Unrecognized column name in estimate data: \'{coln}\'')
        else:
            if dstr != colns_dtypes[coln]:  # More specific check
                raise AssertionError(f"Incorrect data type for column '{coln}'. Expected: {colns_dtypes[coln]}, Found: {dstr}")
    #check storys
    msg1 = f'\nCanCurve only supports basement (-1) and main floor (0) cost items\n  '+ msg
                             #f'remove cost items with these designations\n  '+\
 
    if not df['story'].max()<=0:
        warnings.warn(f'CostItem maximum story value exceeds expectation of \'0\'  '+msg1)

    if not df['story'].min()>=-1:
        warnings.warn(f'CostItem minimum story value exceeds expectation \'-1\'  '+msg1)
#===============================================================================
# Project database
#===============================================================================
def assert_proj_db_fp(fp, **kwargs):
    """full check of proj_db_fp"""
    
    assert os.path.exists(fp), fp
    assert fp.endswith('.cancurve')
    
    try:
        with sqlite3.connect(fp) as conn:
            assert_proj_db(conn, **kwargs)
    
    except Exception as e:
        raise ValueError(f'project DB connection failed w/\n    {e}')
        
        
    
 

def assert_proj_db(conn,
                   expected_tables=expected_tables_base):
    """
    Checks if the provided project database meets expectations by verifying expected tables exist.

    Args:
        conn: An open SQLite database connection.
        expected_tables: A list of expected table names.

    Raises:
        AssertionError: If any of the expected tables are missing.
    """
    cursor = conn.cursor()

    missing_tables = []
    for table_name in expected_tables:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            missing_tables.append(table_name)

    if missing_tables:
        raise AssertionError(f"Missing tables in project database: {', '.join(missing_tables)}")

 


#===============================================================================
# DRF database-------
#===============================================================================




def assert_drf_db(conn):
    """check the drf database meets expectations"""

    try:
        _assert_sqlite_table_exists(conn, 'drf') 
        _assert_sqlite_table_exists(conn, 'depths')
        
         
        
    except sqlite3.Error as e:
        raise AssertionError(f"MasterRuleBook failed expectation check\n    {e}")
    
    
def assert_drf_df(df):
    """
    Asserts that the provided DataFrame conforms to expected format for a DRF dataset.

    Args:
        df: The DataFrame to check.

    Raises:
        TypeError: If the input is not a DataFrame or columns have non-float types.
        KeyError: If the DataFrame's index names are incorrect.
        
    view(df)
    """

    # Check if it's a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame")

    # Check index 
    if not set(df.index.names).difference(['category', 'component', 'bldg_layout']) == set():
        raise KeyError("Incorrect index names in DataFrame")

    # Check the columns all conform to float depths
    # if not 'float' in df.columns.dtype.name:
    #     raise TypeError(f'DRF column headers expected as dtype float. instead got \'{df.columns.dtype.name}\'')
    
    # Check data types (more accurate)
 
    for i, col in enumerate(df.columns):
        if not 'float' in df[col].dtype.name:  # Assuming you want specifically float64
            raise TypeError(f'DRF column \'{col}\' ({i}) expected as dtype float. instead got \'{df[col].dtype}\'')
        
def assert_mrb_depths_df(df):
    
    # Check if it's a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame")

    # Check index 
    if not set(df.index.names).difference(['meters', 'feet']) == set():
        raise KeyError("Incorrect index names in DataFrame")
    
        
def assert_bldg_meta_d(bldg_meta, msg=''):
    """check the bldg_meta_d meets expectations"""
    
    #check the minumn key requirements        
    miss_s = set(bldg_meta_rqmt_df['varName_core'].dropna().values.tolist()).difference(bldg_meta.keys())
    if not miss_s==set():
        raise KeyError(f'bldg_meta missing keys \'{miss_s}\'' + '\n'+msg)
    
    #check types
    type_d = bldg_meta_rqmt_df.loc[:, ['varName_core', 'type']].dropna().set_index('varName_core').iloc[:, 0].to_dict()
    for k,v in type_d.items():
        if not v in type(bldg_meta[k]).__name__:
            raise TypeError(f'unrecognized type on \'{k}\' ({type(bldg_meta[k])})'+ '\n'+msg)
        
    #check values
    if 'scale_factor' in bldg_meta:
        assert_scale_factor(bldg_meta['scale_factor'], msg=msg)
        
def assert_fixed_costs_d(d, msg=''):
    """check the fixed_costs_d meets expectations
    
    decided to allow len(d)>2 and just removing excess data
    for backwards compatability
    """
    assert isinstance(d, dict)
    
    #ssert len(d)<=2
    for k,v in d.items():
        
        #key expectations
        assert isinstance(k, int)        
        assert k>=-1
        #assert k<=0
        
        #value exectations
        if not isinstance(v, float):
            raise TypeError(k)
        assert v>=0
        
#===============================================================================
# MISC-----------
#===============================================================================

def assert_CanFlood_ddf(df, msg=''):
    from cancurve.bldgs.core import DFunc
    from cancurve.hp.logr import get_log_stream
    
    
    log = get_log_stream()
    with DFunc(tabn=df.iloc[0, 1], logger=log) as wrkr: 
        try:            #build        
            wrkr.build(df, log)
        except Exception as e:
            raise AssertionError(f'DDF failed to build as a CanFlood.Dfunc w/ \n    {e}')
 

def assert_scale_factor(v, msg=''):
    assert isinstance(v, float)
    assert v>0.0
    assert v<9e9
 
