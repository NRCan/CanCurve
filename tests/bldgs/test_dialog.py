'''
Created on Apr. 26, 2024

@author: cef

tests dialogs
'''
#===============================================================================
# IMPORTS----------
#===============================================================================
import pytest, time, sys, inspect

from unittest.mock import patch

import matplotlib.pyplot as plt

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QApplication, QPoint
from PyQt5.QtWidgets import (
    QAction, QFileDialog, QListWidget, QTableWidgetItem,
    QComboBox,
    )
from qgis.PyQt import QtWidgets

import pandas as pd
import numpy as np

 
from cancurve.bldgs.parameters import bldg_meta_rqmt_df
from cancurve.bldgs.parameters_ui import building_details_options_d
from cancurve.bldgs.dialog import BldgsDialog
from cancurve.bldgs.assertions import assert_proj_db_fp, expected_tables_base
from cancurve.hp.qt import (
    assert_string_in_combobox, enable_widget_and_parents, set_widget_value
    )
from tests.test_plugin import logger

from cancurve.bldgs.dialog_test_scripts import test_cases_l, set_tab2bldgDetils, set_fixedCosts

 

#===============================================================================
# helpers-----
#===============================================================================
 

#===============================================================================
# FIXTURES------
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
    """dialog fixture.
    for interactive tests, see 'test_init' (uncomment block)"""
    
    #indirect parameters
 
    
    dialog =  BldgsDialog(parent=None, iface=qgis_iface,
                          debug_logger=logger, #connect python logger for rtests
 
                          )
 
    #disable launching of result
    dialog.checkBox_tab4actions_step4_launch.setChecked(False) #not nice for testing
    
    #disable launching of plots
    dialog.checkBox_tab4actions_launchPlot.setChecked(False)
    
    
    return dialog

#===============================================================================
# populating dialog for tests
#===============================================================================
@pytest.fixture(scope='function') 
def set_all_tabs(tab2bldgDetils, tab3dataInput, tab4createCurve):
    """call all the fixtures"""
    
    return True
    
    



@pytest.fixture(scope='function')    
def tab2bldgDetils(dialog, testCase, 
                   bldg_meta_d, #from conftest
                   ):
    """populate the 'Building Details' tab with test metadata"""
    
    dialog._change_tab('tab2bldgDetils')
    
    set_tab2bldgDetils(dialog, testCase) 
        
    #===========================================================================
    # check against core parmeters
    #===========================================================================
    assert bldg_meta_d['bldg_layout']==dialog.buildingLayout_ComboBox.currentText()
    
    #if dialog.basementHeightUnits_ComboBox.currentText()=='m':
    assert 'basement_height' in bldg_meta_d
    assert bldg_meta_d['basement_height']==dialog.basementHeight_DoubleSpinBox.value()
    
    if dialog.sizeOrAreaUnits_ComboBox.currentText()=='m²':
        assert bldg_meta_d['scale_value_m2']==dialog.sizeOrAreaValue_DoubleSpinBox.value()
 
 
        
    """
    bldg_meta_d_strict.keys()
    dialog.show()
    """
        
    print('tab2bldgDetils setup')
    
    return True

@pytest.fixture(scope='function') 
def tab3dataInput(dialog, tableWidget_tab3dataInput_fixedCosts, 
                      testCase, ci_fp, expo_units,
                      #scale_m2,
                      tmp_path):
    
    dialog.lineEdit_wdir.setText(str(tmp_path))
    dialog.lineEdit_tab3dataInput_curveName.setText(testCase)
    dialog.lineEdit_tab3dataInput_cifp.setText(ci_fp)
    
    #set the QComboBox to match the value of 'expo_units'
    dialog.comboBox_tab3dataInput_expoUnits.setCurrentText(expo_units)
    
    """changed this to a drop down on tab4
    if scale_m2: 
        dialog.radioButton_tab3dataInput_rcvm2.setChecked(True)
    else:
        dialog.radioButton_tab3dataInput_rcvm2.setChecked(False)
    """
        
    """not needed... the default is set during connect_slots
    dialog.lineEdit_tab3dataInput_drfFp.setText(drf_db_default_fp)"""
    
    print('tab3dataInput setup')
    
    return True
    

@pytest.fixture(scope='function') 
def tab4createCurve(dialog, scale_m2,
                      tmp_path):
    
    """
    
        scale_m2_index_d = {
        0:False, # Total ($/structure)
        1:True #Area-based ($/area)
        }
        
    """
    
    # Find the index corresponding to scale_m2 directly using dictionary comprehension
    index = next((k for k, v in dialog.scale_m2_index_d.items() if v == scale_m2), None)

    if index is not None:
        dialog.comboBox_tab4actions_costBasis.setCurrentIndex(index)
        
        assert dialog.scale_m2_index_d[dialog.comboBox_tab4actions_costBasis.currentIndex()]==scale_m2
        
 
    else:
        # Optionally, handle the case where scale_m2 is not found in the dictionary
        raise ValueError(f"Invalid scale_m2 value: {scale_m2}")
    
    #check
            
 
    
 
    


@pytest.fixture(scope='function')    
def tableWidget_tab3dataInput_fixedCosts(dialog, fixed_costs_d):
    """assign the dictionary to the input table widget"""
    dialog._change_tab('tab3dataInput')
    
    set_fixedCosts(dialog, fixed_costs_d)
    
    return True
       
@pytest.fixture(scope='function')        
def set_projdb(dialog, proj_db_fp):
    """set the project database filepath onto the dialog"""
    dialog.lineEdit_tab4actions_projdb.setText(proj_db_fp)
    
        


#===============================================================================
# TESTS------
#===============================================================================

def test_parameters():
    df = bldg_meta_rqmt_df.loc[:, ['varName_ui', 'widgetName', 'type']].dropna(subset='varName_ui').set_index('varName_ui')
    assert set(building_details_options_d.keys()).difference(df.index)==set(), 'parameters_ui doesnt match paramter csv'
    

#@pytest.mark.dev
def test_init(dialog,):
    
    
    #===========================================================================
    # """manual inspection only"""
    # dialog.show()
    # QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect    
    # sys.exit(QApp.exec_()) #wrap
    #===========================================================================
 
 
    
    assert hasattr(dialog, 'logger')
    

#===============================================================================
# @pytest.mark.parametrize('testCase',[
#     'case1',
#     #'case2',
#     ], indirect=False)
# @pytest.mark.parametrize('scale_m2',[True], indirect=False)
# def test_init_prepopulate(dialog, set_all_tabs):
#     """init and pre-populate the inputs
#     useful for manual tests"""
#      
#     """manual inspection only"""
#     dialog._change_tab('tab4actions')
#      
#     QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
#     
#     sys.exit(QApp.exec_()) #wrap
#===============================================================================
 
    
#===============================================================================
# private tests-------
#===============================================================================
"""functions hidden from user"""


@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
def test_get_building_details(dialog, 
                         tab2bldgDetils, #calling this sets the values on the UI
                         bldg_meta_d, #from conftest
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
                         tableWidget_tab3dataInput_fixedCosts, #calling this sets the values on the UI
                         fixed_costs_d 
                         ):
    
    result_d = dialog._get_fixed_costs()
 
    assert result_d==fixed_costs_d
    
    
#===============================================================================
# Dialog tests--------
#===============================================================================

def test_radioButton_tab4actions_runControl(dialog):
    
   #============================================================================
   #  QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
   # 
   #  sys.exit(QApp.exec_()) #wrap
   #============================================================================
    b1 = dialog.radioButton_tab4actions_runControl_all
    b2 = dialog.radioButton_tab4actions_runControl_individ
    
    button_l = [
        dialog.pushButton_tab4actions_step1,
        #dialog.pushButton_tab4actions_step2,
        #dialog.pushButton_tab4actions_step3,
        #dialog.pushButton_tab4actions_step4        
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
    #QTest.mouseClick(b2, Qt.LeftButton)
    b2.toggle()
    
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
# def test_pushButton_tab4actions_browse(dialog):
#     enable_widget_and_parents(dialog.pushButton_tab4actions_browse)
#  
#     
#     # Mock QFileDialog.getOpenFileName to return a predetermined filename
#     with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('test_filename', '')):
#         # Simulate a mouse click on the browse button
#         print('clicking browse from within mock')
#         QTest.mouseClick(dialog.pushButton_tab4actions_browse, Qt.LeftButton)
# 
#         # Check that the line edit's text is the expected filename
#         assert dialog.lineEdit_tab4actions_projdb.text() == 'test_filename'
#===============================================================================
   
        
 
@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
@pytest.mark.parametrize('testPhase', ['c03'])
def test_pushButton_tab4actions_read(dialog, set_projdb):
    
    w = dialog.pushButton_tab4actions_read
    
    enable_widget_and_parents(w) #need to enable the button for it to work
    
    
    QTest.mouseClick(w, Qt.LeftButton)
    
    
    #===========================================================================
    # """manual inspection only"""
    # dialog.show()
    # QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect    
    # sys.exit(QApp.exec_()) #wrap
    #===========================================================================

#@pytest.mark.dev
@pytest.mark.parametrize('buttonName, lineName, QFileDialogTypeName',[
     ('pushButton_wd','lineEdit_wdir','getExistingDirectory'),
     ('pushButton_tab3dataInput_cifp','lineEdit_tab3dataInput_cifp', 'getOpenFileName'),
     ('pushButton_tab3dataInput_drfFp','lineEdit_tab3dataInput_drfFp', 'getOpenFileName'),
     ('pushButton_tab4actions_browse', 'lineEdit_tab4actions_projdb', 'getOpenFileName'),
     ])  
def test_file_buttons(dialog, buttonName, lineName, QFileDialogTypeName):
    
    #retrieve button widget
    assert hasattr(dialog, buttonName), buttonName
    w = getattr(dialog, buttonName)    
    enable_widget_and_parents(w)
    
    #lineEdit widget
    assert hasattr(dialog, lineName)
    lineWidget = getattr(dialog, lineName)
    
    #PyQt5.QtWidgets.QFileDialog.
    
    with patch('PyQt5.QtWidgets.QFileDialog.' + QFileDialogTypeName, return_value=('test_string', '')):
        # Simulate a mouse click on the browse button
        print(f'clicking {buttonName} from within mock')
        QTest.mouseClick(w, Qt.LeftButton)

        # Check that the line edit's text is the expected filename
        assert lineWidget.text() == 'test_string', f'test string failed to set on {lineName}'
    
    
 
#===============================================================================
# Dialog Action tests--------
#===============================================================================
"""simulate user interface"""


    
#@pytest.mark.dev
@pytest.mark.parametrize('testCase',[
    'case1',
    'case2',
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True], indirect=False)
@pytest.mark.parametrize('ciPlot',[True], indirect=False)
@pytest.mark.parametrize('drfPlot',[True], indirect=False)
 
def test_action_tab4actions_step1(dialog,
                                  set_all_tabs, ciPlot, drfPlot, 
                                  ):
    
    
    
    
    #===========================================================================
    # settup diablog
    #===========================================================================

    dialog._change_tab('tab4actions')
    
    w = dialog.pushButton_tab4actions_step1
    
    enable_widget_and_parents(w) #need to enable the button for it to work
    
    if ciPlot:
        cbox = dialog.checkBox_tab4actions_step1_ciPlot
        enable_widget_and_parents(cbox)
        cbox.setChecked(True)
        
    if drfPlot:
        cbox = dialog.checkBox_tab4actions_step1_drfPlot
        enable_widget_and_parents(cbox)
        cbox.setChecked(True)
        
    
    #===========================================================================
    # execute test
    #===========================================================================
     
    QTest.mouseClick(w, Qt.LeftButton)  
    
    
    #===========================================================================
    # QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
    # sys.exit(QApp.exec_()) #wrap
    #===========================================================================
    #===========================================================================
    # check
    #===========================================================================
    assert_proj_db_fp(dialog._get_proj_db_fp())
     
    print('finished')
    
 
 
@pytest.mark.dev
#@patch('matplotlib.pyplot.show')  #breaks enable_widget for some reason...
@pytest.mark.parametrize('testCase', ['case4_R2'])
@pytest.mark.parametrize('button, testPhase, expected_tables', [
    #('pushButton_tab4actions_step1', expected_tables_base), #this test is sufficnetly different... see above
    ('pushButton_tab4actions_step2', 'c01', expected_tables_base+['c01_depth_rcv']),
    ('pushButton_tab4actions_step3', 'c02', expected_tables_base+['c01_depth_rcv', 'c02_ddf']),
    ('pushButton_tab4actions_step4', 'c03', expected_tables_base+['c01_depth_rcv', 'c02_ddf']), #export step doesnt write
])
@pytest.mark.parametrize('run_plot', [True])
@pytest.mark.parametrize('scale_m2',[True,
                                     #False,
                                     ], indirect=False)
def test_action_tab4actions(dialog, set_all_tabs, set_projdb, button, expected_tables, 
                            run_plot, testPhase):
    """run test on actions 2, 3, and 4 (see above for action 1)"""
    print('starting test')
    #===========================================================================
    # setup dialog
    #===========================================================================
    dialog._change_tab('tab4actions')
    # Get the button to test
    w = getattr(dialog, button)
    # Enable the button
    enable_widget_and_parents(w) #doesn't enable check boxes
    
    if run_plot:
        cbox_name = {
            'c01':'checkBox_tab4actions_step2_plot',
            'c02':'checkBox_tab4actions_step3_plot',
            'c03':None
            }[testPhase]
        
        if not cbox_name is None:            
            print(f'enabling plot checkBox \'{cbox_name}\'')
            cbox = getattr(dialog, cbox_name)
            enable_widget_and_parents(cbox)
            cbox.setChecked(True)
            
        dialog.checkBox_tab4actions_saveFig.setChecked(True)
            

    #===========================================================================
    # execute
    #===========================================================================
    # Simulate a mouse click on the button
    print('QTest.mouseClick')
    QTest.mouseClick(w, Qt.LeftButton)

    # Check the result
    assert_proj_db_fp(dialog._get_proj_db_fp(), expected_tables=expected_tables)
    
 

    print('finished')

    
#@pytest.mark.dev
@pytest.mark.parametrize('testCase',[
    #'case1',
    #pytest.param('case2', marks=pytest.mark.xfail(raises=(ValueError), reason="this case is missing some DRF entries")),
    #'case3',
    'case4_R2'
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True, False], indirect=False)
def test_action_tab4actions_runAll(dialog, set_all_tabs): 
    """test combined
    
    no need to test plots here
    """
    dialog._change_tab('tab4actions')
    
    #plot over-rides
    dialog.checkBox_tab4actions_step3_plot.setChecked(True)
    
    QTest.mouseClick(dialog._get_child('pushButton_tab4actions_run'), Qt.LeftButton)  
    
    #check
    assert_proj_db_fp(dialog._get_proj_db_fp(), expected_tables=expected_tables_base+['c01_depth_rcv', 'c02_ddf'])
    
    
    
    
    
    
    
    
    

    