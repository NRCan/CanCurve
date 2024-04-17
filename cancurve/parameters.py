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

drf_db_master_fp = os.path.join(src_dir, 'cancurve', 'db', 'mrb_20240416.db')

#===============================================================================
# params
#===============================================================================
colns_index = ['cat', 'sel', 'bldg_layout']

colns_dtypes = {'cat': 'object', 'sel': 'object', 'rcv': 'float64', 'desc': 'object', 'bldg_layout':'object',
                'group_code':'object', 'group_description':'object', 'story':'int64'}

floor_story_d = {'main':0, 'basement':-1}

log_format_str =  "%(levelname)s.%(name)s.%(asctime)s:  %(message)s" 

#===============================================================================
# autos
#===============================================================================
today_str = datetime.now().strftime("%Y%m%d")

