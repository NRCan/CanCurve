'''
Created on Apr. 16, 2024

@author: cef
'''

import os
import sqlite3
import pandas as pd

from cancurve.parameters import colns_index, colns_dtypes





def assert_ci_df(df):
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
    if not set(df.index.names).difference(['cat', 'sel']) == set():
        raise KeyError("Incorrect index names in DataFrame")

    # Check data types
    for coln, dstr in df.dtypes.items():
        if coln not in colns_dtypes:
            raise IOError(f'Unrecognized column name in estimate data: \'{coln}\'')
        if dstr != colns_dtypes[coln]:  # More specific check
            raise AssertionError(f"Incorrect data type for column '{coln}'. Expected: {colns_dtypes[coln]}, Found: {dstr}")

 
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
        raise AssertionError(f'project DB connection failed w/\n    {e}')
        
        
    
 

def assert_proj_db(conn,
                   expected_tables=['project_meta','project_settings', 
                                    'c00_bldg_meta', 'c00_cost_items','c00_drf']):
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
# DRF database
#===============================================================================
def assert_drf_db(conn, table_name='drf'):
    """check the drf database meets expectations"""

    try:
        # Check if the table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()

        if not result:
            raise AssertionError(f"Table '{table_name}' not found in database")

    except sqlite3.Error as e:
        raise AssertionError(f"Error checking database': {e}") 
    
    
def assert_drf_df(df):
    """
    Asserts that the provided DataFrame conforms to expected format for a DRF dataset.

    Args:
        df: The DataFrame to check.

    Raises:
        TypeError: If the input is not a DataFrame or columns have non-float types.
        KeyError: If the DataFrame's index names are incorrect.
    """

    # Check if it's a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame")

    # Check index 
    if not set(df.index.names).difference(['cat', 'sel', 'bldg_layout']) == set():
        raise KeyError("Incorrect index names in DataFrame")

    # Check data types
    if not 'float' in df.columns.dtype.name:
        raise TypeError('bad type on columns')
    
    # Check data types (more accurate)
    for col in df.columns:
        if df[col].dtype != 'float64':  # Assuming you want specifically float64
            raise TypeError(f"Column '{col}' is not a float type")
 
 

 