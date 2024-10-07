'''
Created on Apr. 15, 2024

@author: cef

script for porting MRB 'LineRules' to a SQLite
'''
#===============================================================================
# variables
#===============================================================================
raw_linerules_xls = r'l:\02_WORK\CEF\2403_CanCurve\02_INFO\davids_tool\linerules_20240415.xls'


sql_fp = r'l:\10_IO\CanCurve\misc\port_linerules\mrb_20241007.db'


#===============================================================================
# imports
#===============================================================================
import pandas as pd
from pandas import IndexSlice as idx
import numpy as np

import sqlite3

from cancurve.hp.basic import view_web_df as view
index_cols = ['cat', 'sel', 'bldg_layout']



"""
view(df1)
view(df_left)
"""
 

#===============================================================================
# # load
#===============================================================================
df_raw = pd.read_excel(raw_linerules_xls, sheet_name=0, header=[0,1,2])
df1 = df_raw.copy()


#===============================================================================
# indexing
#===============================================================================
#clean up index
df_left = df_raw.xs('meta1', level=1, axis=1).droplevel(0, axis=1).loc[:, ['Cat', 'Sel', 'StructGroup', 'Cat.Sel', 'Unit', 'Desc']]
df_left.columns = df_left.columns.str.lower()


    

# bldg_layout

"""looks like these had some suffix added to Cat.Sel
ie. wanting to use different DRF for the same cost-item (e.g., ductwork in a 1story vs. 2 story)
David manually added a suffix to the 'cat.sel' field for these
"""
    
    
#extract type from desc
bx =  df_left[['cat', 'sel']].duplicated(keep=False)
df_left = df_left.join(df_left[bx]['desc'].str.extract(r'\((.*?)\)').dropna().iloc[:,0].rename('bldg_layout'))
df_left['bldg_layout'].fillna('default', inplace=True)

df_left = df_left.loc[:, ['cat', 'sel', 'bldg_layout', 'unit', 'desc']]


#check for uniques
bx =  df_left[index_cols].duplicated(keep=False)
assert not bx.any()

df_left['unit'].fillna('EA', inplace=True)
cost_meta_df = df_left.set_index(index_cols)



#===============================================================================
# #DRF
#===============================================================================
drf_df = df_raw[~bx].xs('drf', level=0, axis=1).fillna(0.0).droplevel(0, axis=1)
drf_df.columns.name = 'meters'

#join index
drf_df = drf_df.join(df_left.loc[:, index_cols]).set_index(index_cols)

# Assuming drf_df.columns contains the meter values as strings or numbers
# Convert column names to floats if they aren't already
meters = drf_df.columns.astype(float)

# Convert meters to feet
feet = meters * 3.28084  # Conversion factor from meters to feet

# Initialize depth_idx array
depth_idx = np.zeros(len(meters), dtype=int)

# Identify indices for negative, zero, and positive meters
neg_indices = meters < 0
zero_indices = meters == 0
pos_indices = meters > 0

# For negative meters, assign depth_idx starting from -1, decreasing
# Sort negative meters in increasing order (from most negative to least negative)
neg_meters = meters[neg_indices]
neg_sorted_indices = np.argsort(neg_meters)
neg_depth_idx = -np.arange(1, len(neg_meters) + 1)  # -1, -2, -3, ...

# Map the negative depth indices back to their original positions
depth_idx_neg = np.empty(len(neg_meters), dtype=int)
depth_idx_neg[neg_sorted_indices] = neg_depth_idx
depth_idx[neg_indices] = depth_idx_neg

# For zero meters, depth_idx is already zero (initialized)

# For positive meters, assign depth_idx starting from 1, increasing
# Sort positive meters in increasing order
pos_meters = meters[pos_indices]
pos_sorted_indices = np.argsort(pos_meters)
pos_depth_idx = np.arange(1, len(pos_meters) + 1)  # 1, 2, 3, ...

# Map the positive depth indices back to their original positions
depth_idx_pos = np.empty(len(pos_meters), dtype=int)
depth_idx_pos[pos_sorted_indices] = pos_depth_idx
depth_idx[pos_indices] = depth_idx_pos

# Create the MultiIndex
multi_index = pd.MultiIndex.from_arrays(
    [depth_idx, meters, feet],
    names=['depth_idx', 'meters', 'feet']
)

# Assign the new MultiIndex to drf_df.columns
drf_df.columns = multi_index

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
    'mrb_sourcee':[r'l:\09_REPOS\04_TOOLS\DDFP\DDF_RuleBook_r0.xlsm'],
    'entries':[len(drf_df)],
    'index_cols':[str(index_cols)],
})

#===============================================================================
# port to SQLite-------
#===============================================================================
# Database connection
conn = sqlite3.connect(sql_fp)

# Add DataFrames to the database
cost_meta_df.to_sql('cost_items', conn, if_exists='replace', index=True)
metadata_df.to_sql('meta', conn, if_exists='replace', index=False)

#===============================================================================
# #write the DRF. split out the multi-index columns into a separate table
#===============================================================================
#and link the two tables using depth_idx
#write both tables to the sqlite database
# 1. Extract the MultiIndex columns information into a DataFrame
# Reset the MultiIndex columns to a DataFrame
drf_columns = drf_df.columns.to_frame(index=False)

# Write the columns DataFrame to SQLite as 'drf_columns' table
drf_columns.to_sql('depths', conn, if_exists='replace', index=False)

# 2. Prepare the data DataFrame by resetting the MultiIndex columns
# Transpose drf_df to swap rows and columns
drf_data = drf_df.transpose().reset_index()

# Now drf_data has columns: 'depth_idx', 'meters', 'feet', plus the index columns from drf_df

# Drop 'meters' and 'feet' as they're already in drf_columns
drf_data = drf_data.drop(columns=['meters', 'feet'])

# Optional: If you have index columns in drf_df, reset the index to include them
drf_data = drf_data.set_index('depth_idx').transpose().reset_index()


# Write drf_data to SQLite as 'drf_data' table
drf_data.to_sql('drf', conn, if_exists='replace', index=False)

#===============================================================================
# add keys
#===============================================================================
#add primary keys to drf_data
#index: cat, sel, bldg_layout

#add the same to cost_meta_df and link the keys together between the two tables
 

# Close the connection
conn.close()

print(f'finished and created database at \n    {sql_fp}')



 
 
