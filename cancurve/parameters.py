'''
Created on Apr. 16, 2024

@author: cef
'''
import os
from datetime import datetime

#===============================================================================
# directories and files
#===============================================================================
src_dir = os.path.dirname(os.path.dirname(__file__))

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
    }

floor_story_d = {'main':0, 'basement':-1}

log_format_str =  "%(levelname)s.%(name)s.%(asctime)s:  %(message)s"


settings_default_d = {'scale_m2':False}


 

#===============================================================================
# autos
#===============================================================================
today_str = datetime.now().strftime("%Y%m%d")

