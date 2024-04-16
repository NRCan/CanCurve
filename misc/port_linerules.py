'''
Created on Apr. 15, 2024

@author: cef

script for porting MRB 'LineRules' to a SQLite
'''
#===============================================================================
# variables
#===============================================================================
raw_linerules_xls = r'l:\02_WORK\CEF\2403_CanCurve\02_INFO\davids_tool\linerules_20240415.xls'
index_cols = ['cat', 'sel']

sql_fp = r'l:\10_IO\CanCurve\misc\port_linerules\mrb_20240415.db'


#===============================================================================
# imports
#===============================================================================
import pandas as pd
from pandas import IndexSlice as idx

import sqlite3

from cancurve.hp.basic import view_web_df as view



"""
view(df1)
view(df_left)
"""
 

# load
df_raw = pd.read_excel(raw_linerules_xls, sheet_name=0, header=[0,1,2])
df1 = df_raw.copy()


#clean up index
df_left = df_raw.xs('meta1', level=1, axis=1).droplevel(0, axis=1).loc[:, ['Cat', 'Sel', 'Unit', 'Desc']]
df_left.columns = df_left.columns.str.lower()

#check for uniques
bx =  df_left[index_cols].duplicated(keep='first')
if bx.any():
    """looks like these had some suffix added to Cat.Sel
    ie. wanting to use different DRF for the same cost-item (e.g., ductwork in a 1storey vs. 2 storey)
    just dropping these for now
    """
    print(f'WARNING: got {bx.sum()}/{len(bx)} duplicated {index_cols} entries')
    
    #take just the first occurence of each duplicated entry
    df_left = df_left.loc[~bx]
    
    #view(df_left.loc[bx, index_cols])

df_left['unit'].fillna('EA', inplace=True)
cost_meta_df = df_left.set_index(index_cols)



#DRF
drf_df = df_raw[~bx].xs('drf', level=0, axis=1).fillna(0.0).droplevel(0, axis=1)
drf_df.columns.name = 'meters'

#join index
drf_df = drf_df.join(df_left.loc[:, ['cat', 'sel']]).set_index(['cat', 'sel'])

#===============================================================================
# # Create metadata DataFrame
#===============================================================================
import datetime
import os
current_date = datetime.date.today().strftime('%Y-%m-%d')
username = os.getlogin()  # Or a relevant way to get the username
script_name = os.path.basename(__file__)  # Assumes script name is the file name
output_filename = os.path.basename(sql_fp)  
metadata_df = pd.DataFrame({
    'date': [current_date],
    'username': [username],
    'script_name': [script_name],
    'output_filename': [output_filename],
    'raw_linerules_xls':[raw_linerules_xls],
    'entries':[len(drf_df)]
})

#===============================================================================
# port to SQLite
#===============================================================================
# Database connection
conn = sqlite3.connect(sql_fp)

# Add DataFrames to the database
cost_meta_df.to_sql('cost_item_meta', conn, if_exists='replace', index=True)
drf_df.to_sql('drf', conn, if_exists='replace', index=True)
metadata_df.to_sql('meta', conn, if_exists='replace', index=False)

# Close the connection
conn.close()

print(f'finished and created database at \n    {sql_fp}')



 
 
