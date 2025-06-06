'''
Created on Apr. 30, 2024

@author: cef

testing functions for use in pytests and manual QGIS tests (ie no pytest dependency)

for pytest data handlers, see tests.data.bldgs_data_scripts
'''
import os, warnings, copy

import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (
    QAction, QFileDialog, QListWidget, QTableWidgetItem,
    QComboBox,
    )

from ..hp.qt import (
    assert_string_in_combobox, set_widget_value
    )

from ..hp.basic import view_web_df as view

from ..parameters import src_dir, plugin_dir

from .parameters_ui import building_details_options_d
from .parameters import bldg_meta_rqmt_df


#===============================================================================
# params-----
#===============================================================================
test_data_dir_master = os.path.join(plugin_dir, 'tutorial') #needs to live in plugin directory for dev ui to work

 

"""this needs to live here so it is accessible by tests after deployment
note the underlying data needs to be duplicated in ./dev_test_data and ./tests/data/bldgs
"""
fixed_costs_master_d = {
        '01':{0:10000.0, -1:8000.0}, #case1 for UI display
        '02':{0:10000.0, -1:8000.0}, #case1_ci_header_case'
        'case1':{0:10000.0, -1:8000.0},
        'case1_ci_header_case':{0:10000.0, -1:8000.0},
        'case2':None,
        'case3':{-1:0.0, 0:25000.0},
        'case4_R2':{-1:19361.0, 0:24879.0, 
                    #1:22484.0,
                    },
        'case5_crawl':{0:10000.0}
                
        }

#see tests.data.bldgs.misc for file-based test cases
test_cases_l = copy.copy(list(fixed_costs_master_d.keys()))

 

#===============================================================================
# helpers------
#===============================================================================

def set_fixedCosts(dialog, fixed_costs_d):
 
    if isinstance(fixed_costs_d, dict):
        for k,v in fixed_costs_d.items():
            #retrieve widget for this story
            qds_widget = dialog.fixed_costs_widget_d[k]
            qds_widget.setValue(v)
    else:
        warnings.warn(f'got no fixed costs')
 
    
        
        
def set_tab2bldgDetils(dialog, testCase):
    """configure the building details tab based on the test"""
    
    #read from bldg_meta_rqmts.csv
    #slice down and index by the ui element (varName_ui)
    cols_bx = bldg_meta_rqmt_df.columns.isin(['varName_ui', 'widgetName', 'type'] + test_cases_l)
    df = bldg_meta_rqmt_df.loc[:,cols_bx].dropna(subset='varName_ui').set_index('varName_ui')
    
    """
    view(df)
    """
    
    #loop through and change the combobox to match whats in the dictionary
    for k, row in df.iterrows():
        
        

        
        try:
            #retrieve the value from the test case
            if not pd.isnull(row[testCase]):
                v = row[testCase]
            elif k in building_details_options_d:
                v = building_details_options_d[k][0] #just take first
            else:
                #print('continue')
                continue #skip this one
            #v = str(v_raw)
            
            #retrieve the widget
            assert hasattr(dialog, row['widgetName']), f'bad widgetname: %s'%row['widgetName']
            widget = getattr(dialog, row['widgetName'])
            
            
            if k == 'subClassification': #add exception for the subClassifcation
                continue
            
            
            #check if the requested value is one of the comboBox's options
            if isinstance(widget, QComboBox):
                assert_string_in_combobox(widget, v)
            
            #set the value 
            set_widget_value(widget, v)
            
            
        except Exception as e:
            raise IOError(f'failed to set element \'{k}\' on the building details tab w/\n    {e}')
        
        
        
        
        
        
        
        
        
        