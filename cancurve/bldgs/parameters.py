'''
Created on Apr. 16, 2024

@author: cef

buildings module parameters
'''
import os
from datetime import datetime

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

"""see also core.DFunc.crve_d"""
building_meta_dtypes = {
     'location':str,'date':datetime, 'source':str,
     
    'impact_units':str,'impact_var':str, #e.g., replacement costs
    'exposure_units':str, 'exposure_var':str, #e.g., flood depth above main floor
    'scale_units':str,'scale_var':str, #e.g., usable floor space
    
    'bldg_layout':str, #building layout used to slice the DRF
    
    }

floor_story_d = {'main':0, 'basement':-1}

#queried from mrb_20240416.db
bldg_layout_options_l = ['default', 
                         'mech-base', 'mech-main', #not sure what is going on with these... they are duplicated in default
                         '1storeybase', '2storeybase','1storeycrawl', '2storeycrawl']


settings_default_d = {'scale_m2':False, 'curve_name':'myCurveName'}

 


 


