'''
Created on Apr. 30, 2024

@author: cef

testing functions for use in pytests and manual QGIS tests (ie no pytest dependency)
'''
import os

import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (
    QAction, QFileDialog, QListWidget, QTableWidgetItem,
    QComboBox,
    )

from ..hp.qt import (
    assert_string_in_combobox, set_widget_value
    )

from ..parameters import src_dir, plugin_dir

from .parameters_ui import building_details_options_d
from .parameters import bldg_meta_rqmt_df


#===============================================================================
# params-----
#===============================================================================
test_data_dir_master = os.path.join(plugin_dir, 'dev_test_data') #needs to live in plugin directory for dev ui to work

#test_data_dir_master = os.path.join(parent_tdata_dir, 'bldgs')

test_cases_l = ['case1', 'case2']

fixed_costs_master_d = {
        'case1':{0:10000, -1:8000},
        'case2':None,        
        }


#===============================================================================
# helpers------
#===============================================================================

def set_fixedCosts(dialog, fixed_costs_d):
    tblW = dialog.tableWidget_tab3dataInput_fixedCosts #get the table widget
    ser = pd.Series(fixed_costs_d)
    tblW.setRowCount(len(ser)) #add this many rows
    for i, (eName, pval) in enumerate(ser.items()):
        tblW.setItem(i, 0, QTableWidgetItem(str(eName)))
        tblW.setItem(i, 1, QTableWidgetItem(str(pval)))
        
        
def set_tab2bldgDetils(dialog, testCase):
    
    df = bldg_meta_rqmt_df.loc[:, ['varName_ui', 'widgetName', 'type'] + test_cases_l].dropna(subset='varName_ui').set_index('varName_ui')
    #loop through and change the combobox to match whats in the dictionary
    for k, row in df.iterrows():
        if not pd.isnull(row[testCase]):
            v = row[testCase]
        elif k in building_details_options_d:
            v = building_details_options_d[k][0] #just take first
        else:
            #print('continue')
            continue #skip this one
        #v = str(v_raw)
        #comboBox = dialog._get_child(f'{k}_ComboBox', childType=QtWidgets.QComboBox)
        widget = getattr(dialog, row['widgetName'])
        #check if the requested value is one of the comboBox's options
        if isinstance(widget, QComboBox):
            assert_string_in_combobox(widget, v)
        set_widget_value(widget, v)