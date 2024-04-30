'''
Created on Apr. 26, 2024

@author: cef

tests dialogs
'''

import pytest, time, sys, inspect

from unittest.mock import patch

import matplotlib.pyplot as plt

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QApplication, QPoint
from PyQt5.QtWidgets import QAction, QFileDialog, QListWidget, QTableWidgetItem
from qgis.PyQt import QtWidgets

import pandas as pd

 
from cancurve.bldgs.parameters import drf_db_default_fp
from cancurve.bldgs.dialog import BldgsDialog
from cancurve.bldgs.assertions import assert_proj_db_fp, expected_tables_base
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
def dialog(qgis_iface, request):
    
    #indirect parameters
    show_plots = request.param if hasattr(request, 'param') else False
    
    dialog =  BldgsDialog(parent=None, iface=qgis_iface,
                          debug_logger=logger, #connect python logger for rtests
                          show_plots=show_plots,
                          )
 
    #dialog.show() #launch the window?
    
    
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
    
    dialog._change_tab('tab2bldgDetils')
    
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
       
@pytest.fixture(scope='function')        
def set_projdb(dialog, proj_db_fp):
    """set the project database filepath onto the dialog"""
    dialog.lineEdit_tab4actions_projdb.setText(proj_db_fp)
    
        


#===============================================================================
# tests------
#===============================================================================
 
def test_init(dialog,):
    
   #============================================================================
   #  """manual inspection only"""
   #  QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
   # 
   #  sys.exit(QApp.exec_()) #wrap
   #============================================================================
 
 
    
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
# Dialog tests--------
#===============================================================================

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
                     
                 
    

def test_pushButton_tab4actions_browse(dialog):
    enable_widget_and_parents(dialog.pushButton_tab4actions_browse)
 
    
    # Mock QFileDialog.getOpenFileName to return a predetermined filename
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('test_filename', '')):
        # Simulate a mouse click on the browse button
        print('clicking browse from within mock')
        QTest.mouseClick(dialog.pushButton_tab4actions_browse, Qt.LeftButton)

        # Check that the line edit's text is the expected filename
        assert dialog.lineEdit_tab4actions_projdb.text() == 'test_filename'
 
#===============================================================================
# Dialog Action tests--------
#===============================================================================
"""simulate user interface"""


    

@pytest.mark.parametrize('testCase',[
    #'case1',
    'case2',
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True], indirect=False)
@pytest.mark.parametrize('ciPlot',[True], indirect=False)
@pytest.mark.parametrize('drfPlot',[True], indirect=False)
def test_action_tab4actions_step1(dialog,
                                  set_all_tabs, ciPlot, drfPlot
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
    
 
 

#@patch('matplotlib.pyplot.show')  #breaks enable_widget for some reason...
@pytest.mark.parametrize('testCase', ['case1'])
@pytest.mark.parametrize('button, testPhase, expected_tables', [
    ##('pushButton_tab4actions_step1', expected_tables_base), #this test is sufficnetly different... see above
    ('pushButton_tab4actions_step2', 'c01', expected_tables_base+['c01_depth_rcv']),
    ('pushButton_tab4actions_step3', 'c02', expected_tables_base+['c01_depth_rcv', 'c02_ddf']),
    ('pushButton_tab4actions_step4', 'c03', expected_tables_base+['c01_depth_rcv', 'c02_ddf']), #export step doesnt write
])
@pytest.mark.parametrize('run_plot', [True])
@pytest.mark.parametrize('show_plots', [False], indirect=True) #whether to call plt.show
@pytest.mark.parametrize('scale_m2',[True], indirect=False)
def test_action_tab4actions(dialog, set_all_tabs, set_projdb, button, expected_tables, 
                            run_plot, testPhase, show_plots):
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
            

    #===========================================================================
    # execute
    #===========================================================================
    # Simulate a mouse click on the button
    print('QTest.mouseClick')
    QTest.mouseClick(w, Qt.LeftButton)

    # Check the result
    assert_proj_db_fp(dialog._get_proj_db_fp(), expected_tables=expected_tables)
    
 

    print('finished')

    
@pytest.mark.dev
@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True, False], indirect=False)
def test_action_tab4actions_runAll(dialog, set_all_tabs): 
    """test combined
    
    no need to test plots here
    """
    dialog._change_tab('tab4actions')
    QTest.mouseClick(dialog._get_child('pushButton_tab4actions_run'), Qt.LeftButton)  
    
    
    
    
    
    
    
    
    

    