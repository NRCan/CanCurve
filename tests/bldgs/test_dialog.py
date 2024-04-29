'''
Created on Apr. 26, 2024

@author: cef

tests dialogs
'''

import pytest, time, sys

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QApplication
from PyQt5.QtWidgets import QAction, QFileDialog, QListWidget, QTableWidgetItem
from qgis.PyQt import QtWidgets

import pandas as pd

 

from cancurve.bldgs.dialog import BldgsDialog
from cancurve.hp.qt import assert_string_in_combobox
from tests.test_plugin import logger

#===============================================================================
# helpers-----
#===============================================================================
 

#===============================================================================
# fixtures------
#===============================================================================

#===============================================================================
# dialog setup
#===============================================================================
"""need to handle:
    different scenarios for user inputs (e.g., paramerterize populated fields on UI)
    partial (for individual run) and complete (for full run) parameterization
    
use fixtures to parameterize in blocks
    load the dialog, assign some variables
    only need to call the fixture (and the dialog) in the test (don't need to use)
"""
    
@pytest.fixture(scope='function') 
def dialog(qgis_iface):
    
    dialog =  BldgsDialog(parent=None, iface=qgis_iface,
                          debug_logger=logger, #connect python logger for rtests
                          )
    dialog.setModal(False)
    dialog.show() #launch the window?
    
    
    return dialog
    
@pytest.fixture(scope='function')    
def tableWidget_di_fixedCosts(dialog, fixed_costs_d):
    """assign the dictionary to the input table widget"""
    dialog._change_tab('tab_03_dataInput')
    tblW = dialog.tableWidget_di_fixedCosts
    
    ser = pd.Series(fixed_costs_d)
 
    tblW.setRowCount(len(ser)) #add this many rows
    for i, (eName, pval) in enumerate(ser.items()):
        tblW.setItem(i, 0, QTableWidgetItem(str(eName)))
        tblW.setItem(i, 1, QTableWidgetItem(str(pval)))
    
       
@pytest.fixture(scope='function')    
def set_tab_02_bldgDetils(dialog, bldg_meta_d):
    """populate the 'Building Details' tab with test metadata"""
    
    dialog._change_tab('tab_02_bldgDetils')
    
    #loop through and change the combobox to match whats in the dictionary
    for k,v_raw in bldg_meta_d.items():
        v = str(v_raw)
        comboBox = dialog._get_child(f'{k}_ComboBox', childType=QtWidgets.QComboBox)
        
        #check if the requested value is one of the comboBox's options
        assert_string_in_combobox(comboBox, v)
        
        #set this value
        comboBox.setCurrentText(v)

#===============================================================================
# tests------
#===============================================================================

def test_init(dialog):
    
 #==============================================================================
 #    """manual inspection only"""
 #    QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
 # 
 #    sys.exit(QApp.exec_()) #wrap
 #==============================================================================
 
 
    
    assert hasattr(dialog, 'logger')
 
    
#===============================================================================
# private tests-------
#===============================================================================
"""functions hidden from user"""

@pytest.mark.dev
@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
def test_get_building_details(dialog, 
                         set_tab_02_bldgDetils, #calling this sets the values on the UI
                         bldg_meta_d
                         ):
    
    """manual inspection only"""
  #=============================================================================
  #   QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
  # 
  #   sys.exit(QApp.exec_()) #wrap
  #=============================================================================
    
    result = dialog._get_building_details()
    
    for k,v in bldg_meta_d.items():
        assert k in result, f'key \'{k}\' missing in result'
        if k.endswith('Units'): #skip m^2
            continue
        assert v==result[k], f'value for \'{k}\' mismatch'
 


@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
def test_get_fixed_costs(dialog, 
                         tableWidget_di_fixedCosts, #calling this sets the values on the UI
                         fixed_costs_d
                         ):
    
    result_d = dialog._get_fixed_costs()
 
    assert result_d==fixed_costs_d
    



 
 
    
    
    
    
#===============================================================================
# action tests--------
#===============================================================================
"""simulate user interface"""
 
def test_Tcc_run(dialog):
 
    QTest.mouseClick(dialog._get_child('pushButton_Tcc_run'), Qt.LeftButton)  

    