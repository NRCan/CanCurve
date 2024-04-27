'''
Created on Apr. 26, 2024

@author: cef

tests dialogs
'''

import pytest, time, sys

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QApplication
from PyQt5.QtWidgets import QAction, QFileDialog, QListWidget, QTableWidgetItem

import pandas as pd

 

from cancurve.dialog import CanCurveDialog
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
    
    dialog =  CanCurveDialog(parent=None, iface=qgis_iface,
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
    
       


#===============================================================================
# tests------
#===============================================================================
@pytest.mark.dev
def test_init(dialog):
    QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
    #qtbot.addWidget(dialog)
    #qtbot.stopForInteraction()
    sys.exit(QApp.exec_()) #wrap
 
    #time.sleep(60)  # keep the dialog open for 60 seconds
    
    assert hasattr(dialog, 'logger')
 
    
#===============================================================================
# private tests-------
#===============================================================================
"""function shidden from user"""


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
    


@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
def test_get_building_details(dialog, 
                         tableWidget_di_fixedCosts, #calling this sets the values on the UI
                         bldg_meta
                         ):
    
    result = dialog._get_building_details()
 
 
    
    
    
    
#===============================================================================
# action tests--------
#===============================================================================
"""simulate user interface"""
 
def test_Tcc_run(dialog):
 
    QTest.mouseClick(dialog._get_child('pushButton_Tcc_run'), Qt.LeftButton)  

    