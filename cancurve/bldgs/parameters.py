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
drf_db_default_fp = os.path.join(src_dir, 'cancurve', 'db', 'mrb_20240416.db')

#===============================================================================
# params
#===============================================================================
colns_index = ['cat', 'sel', 'bldg_layout']

colns_dtypes = {'cat': 'object', 'sel': 'object', 'rcv': 'float64', 'desc': 'object', 'bldg_layout':'object',
                'group_code':'object', 'group_description':'object', 'story':'int64'}




floor_story_d = {'main':0, 'basement':-1}

#queried from mrb_20240416.db
bldg_layout_options_l = ['default', 
                         'mech-base', 'mech-main', #not sure what is going on with these... they are duplicated in default
                         '1storeybase', '2storeybase','1storeycrawl', '2storeycrawl']


settings_default_d = {'scale_m2':False, 'curve_name':'myCurveName'}

#===============================================================================
# params. building metadata
#===============================================================================
"""see also core.DFunc.crve_d

using a csv table to capture all of the info
"""
bldg_meta_rqmt_fp = os.path.join(os.path.dirname(__file__), 'bldg_meta_rqmts.csv')
bldg_meta_rqmt_df = pd.read_csv(bldg_meta_rqmt_fp)
#===============================================================================
# building_meta_rqmts_d = {
#     'location': {'type': str},
#     'date': {'type': datetime},
#     'source': {'type': str},
#     'impact_units': {'type': str},
#     'impact_var': {'type': str},
#     'exposure_units': {'type': str},
#     'exposure_var': {'type': str},
#     'scale_units': {'type': str},
#     'scale_var': {'type': str},
#     'bldg_layout': {'type': str},
# }
#===============================================================================
 


 


