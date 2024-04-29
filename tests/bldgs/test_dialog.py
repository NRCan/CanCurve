'''
Created on Apr. 26, 2024

@author: cef

tests dialogs
'''

import pytest, time, sys, inspect

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QApplication, QPoint
from PyQt5.QtWidgets import QAction, QFileDialog, QListWidget, QTableWidgetItem
from qgis.PyQt import QtWidgets

import pandas as pd

 
from cancurve.bldgs.parameters import drf_db_default_fp
from cancurve.bldgs.dialog import BldgsDialog
from cancurve.hp.qt import assert_string_in_combobox, enable_widget_and_parents
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
 
    dialog.show() #launch the window?
    
    
    return dialog

#===============================================================================
# populating dialog for tests
#===============================================================================
@pytest.fixture(scope='function') 
def set_all_tabs(set_tab2bldgDetils, set_tab3dataInput):
    """call all the fixtures"""
    
    return True
    
    
@pytest.fixture(scope='function')    
def set_tab2bldgDetils(dialog, bldg_meta_d):
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
        
    print('tab2bldgDetils setup')
    
    return True

@pytest.fixture(scope='function') 
def set_tab3dataInput(dialog, set_tableWidget_tab3dataInput_fixedCosts, 
                      testCase, ci_fp, scale_m2,
                      tmp_path):
    
    dialog.lineEdit_wdir.setText(str(tmp_path))
    dialog.lineEdit_tab3dataInput_curveName.setText(testCase)
    dialog.lineEdit_tab3dataInput_cifp.setText(ci_fp)
    
    if scale_m2: 
        dialog.radioButton_tab3dataInput_rcvm2.setChecked(True)
    else:
        dialog.radioButton_tab3dataInput_rcvm2.setChecked(False)
        
    """not needed... the default is set during connect_slots
    dialog.lineEdit_tab3dataInput_drfFp.setText(drf_db_default_fp)"""
    
    print('tab3dataInput setup')
    
    return True
    
@pytest.fixture(scope='function')    
def set_tableWidget_tab3dataInput_fixedCosts(dialog, fixed_costs_d):
    """assign the dictionary to the input table widget"""
    dialog._change_tab('tab3dataInput')
    
    tblW = dialog.tableWidget_tab3dataInput_fixedCosts #get the table widget
    
    ser = pd.Series(fixed_costs_d)
 
    tblW.setRowCount(len(ser)) #add this many rows
    for i, (eName, pval) in enumerate(ser.items()):
        tblW.setItem(i, 0, QTableWidgetItem(str(eName)))
        tblW.setItem(i, 1, QTableWidgetItem(str(pval)))
    
    return True
       

        


#===============================================================================
# tests------
#===============================================================================

def test_init(dialog):
    
  #=============================================================================
  #   """manual inspection only"""
  #   QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
  # 
  #   sys.exit(QApp.exec_()) #wrap
  #=============================================================================
 
 
    
    assert hasattr(dialog, 'logger')
 
    
#===============================================================================
# private tests-------
#===============================================================================
"""functions hidden from user"""


@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
def test_get_building_details(dialog, 
                         set_tab2bldgDetils, #calling this sets the values on the UI
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
                         set_tableWidget_tab3dataInput_fixedCosts, #calling this sets the values on the UI
                         fixed_costs_d 
                         ):
    
    result_d = dialog._get_fixed_costs()
 
    assert result_d==fixed_costs_d
    
    
#===============================================================================
# dialog logic tests--------
#===============================================================================
@pytest.mark.dev
def test_radioButton_tab4actions_runControl_all(dialog):
    
   #============================================================================
   #  QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
   # 
   #  sys.exit(QApp.exec_()) #wrap
   #============================================================================
    b1 = dialog.radioButton_tab4actions_runControl_all
    b2 = dialog.radioButton_tab4actions_runControl_individ
    
    button_l = [
        dialog.pushButton_tab4actions_step1,
        dialog.pushButton_tab4actions_step2,
        dialog.pushButton_tab4actions_step3,
        dialog.pushButton_tab4actions_step4        
        ]
 

    # Initial state (assuming buttons start disabled)
    for w in button_l:
        assert not w.isEnabled(), w.objectName()
    print('init state is good')
    
    
    assert b1.isChecked(), 'All should be selected by default'    
    assert not b2.isChecked()
    
    #===========================================================================
    # #click b2
    #===========================================================================
    QTest.mouseClick(b2, Qt.LeftButton)
    
    assert b2.isChecked()
    assert not b1.isChecked()
 
    
    #changed state
    for w in button_l:
        assert w.isEnabled(), w.objectName()
        
    #===========================================================================
    # click again
    #===========================================================================
    """not sure why these don't work"""
    #QTest.mouseClick(b1, Qt.LeftButton)
    #b2.toggle()
    b1.toggle()
    assert b1.isChecked() #thils fails
    assert not b2.isChecked()
    
    for w in button_l:
        assert not w.isEnabled(), w.objectName()
                     
                 
    
    
 
 
#===============================================================================
# action tests--------
#===============================================================================
"""simulate user interface"""


    

@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True], indirect=False)
def test_action_tab4actions_step1(dialog,
                                  set_all_tabs,
                                  ):
    w = dialog.pushButton_tab4actions_step1
    enable_widget_and_parents(w) #need to enable the button for it to work 
    QTest.mouseClick(w, Qt.LeftButton)  
    
    print('finished')
    
    
    


@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True, False], indirect=False)
def test_action_tab4actions_run(dialog, set_all_tabs): 
    QTest.mouseClick(dialog._get_child('pushButton_tab4actions_run'), Qt.LeftButton)  
    
    
    
    
    
    
    
    
    

    