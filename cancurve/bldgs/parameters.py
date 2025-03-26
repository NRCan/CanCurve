'''
Created on Apr. 16, 2024

@author: cef

buildings module parameters
'''
import os
from datetime import datetime
import pandas as pd

from ..parameters import src_dir, home_dir, today_str

#===============================================================================
# directories and files
#===============================================================================
drf_db_default_fp = os.path.join(src_dir, 'cancurve', 'db', 'mrb_20250226.db')

#===============================================================================
# params
#===============================================================================

column_rename_d = {
    'cat':'category',
    'sel':'component',
    }


colns_index = ['category', 'component', 'bldg_layout']

colns_dtypes = {'category': 'object', 'component': 'object', 'rcv': 'float64', 'desc': 'object', 'bldg_layout':'object',
                'group_code':'object', 'group_description':'object', 'story':'int64'}




floor_story_d = {'main':0, 'basement':-1, 'upper':1}

#queried from mrb_20240416.db
bldg_layout_options_l = ['default', 
                         'mech-base', 'mech-main', #not sure what is going on with these... they are duplicated in default
                         '1storybase', '2storybase','1storycrawl', '2storycrawl']


"""for testing these, usually hard code as a paramter (dont use buidling metadata)"""
settings_default_d = {'scale_m2':False, 'curve_name':'myCurveName', 'expo_units':'meters'}

#===============================================================================
# params. building metadata
#===============================================================================
"""see also core.DFunc.crve_d

using a csv table to capture all of the info
"""
bldg_meta_rqmt_fp = os.path.join(os.path.dirname(__file__), 'bldg_meta_rqmts.csv')
bldg_meta_rqmt_df = pd.read_csv(bldg_meta_rqmt_fp)

#check the requirements data
assert isinstance(bldg_meta_rqmt_df, pd.DataFrame)
assert len(bldg_meta_rqmt_df)>0
assert all([x in bldg_meta_rqmt_df.columns for x in ['varName_core', 'varName_ui', 'varName_canflood', 'type', 'required_core', 'required_canflood', 'default_canflood', 'widgetName']])
 
 


