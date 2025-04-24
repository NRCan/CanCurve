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

 

 
from cancurve.bldgs.parameters import bldg_meta_rqmt_df
from cancurve.bldgs.parameters_ui import building_details_options_d
from cancurve.bldgs.dialog import BldgsDialog
from cancurve.bldgs.assertions import assert_proj_db_fp, expected_tables_base
from cancurve.hp.qt import (
    assert_string_in_combobox, enable_widget_and_parents, set_widget_value
    )
from tests.test_plugin import logger
from tests.conftest import click, qgis_iface_stub


from cancurve.bldgs.dialog_test_scripts import test_cases_l, set_tab2bldgDetils, set_fixedCosts

from tests.bldgs.conftest import bldg_meta_d, fixed_costs_d, ci_fp, expo_units
 

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
def dialog_fixt(qgis_iface_stub):
    """dialog fixture.
    for interactive tests, see 'test_init' (uncomment block)"""
    
    #indirect parameters
 
    
    dialog =  BldgsDialog(parent=None, iface=qgis_iface_stub,
                          debug_logger=logger, #connect python logger for rtests
 
                          )
    
    dialog.logger.push('BldgsDialog.inited')
 
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
def tab2bldgDetils(dialog_fixt, testCase, 
                   bldg_meta_d, #from conftest
                   ):
    """populate the 'Building Details' tab with test metadata"""
    
    dialog_fixt._change_tab('tab2bldgDetils')
    
    set_tab2bldgDetils(dialog_fixt, testCase) 
        
    #===========================================================================
    # check against core parmeters
    #===========================================================================
    assert bldg_meta_d['bldg_layout']==dialog_fixt.buildingLayout_ComboBox.currentText()
    
    #if dialog.basementHeightUnits_ComboBox.currentText()=='m':
    assert 'basement_height' in bldg_meta_d
    assert bldg_meta_d['basement_height']==dialog_fixt.basementHeight_DoubleSpinBox.value()
    
    if dialog_fixt.sizeOrAreaUnits_ComboBox.currentText()=='m²':
        assert bldg_meta_d['scale_value_m2']==dialog_fixt.sizeOrAreaValue_DoubleSpinBox.value()
 
 
        
    """
    bldg_meta_d_strict.keys()
    dialog.show()
    """
        
    print('tab2bldgDetils setup')
    
    return True

@pytest.fixture(scope='function') 
def tab3dataInput(dialog_fixt, tableWidget_tab3dataInput_fixedCosts, 
                      testCase, ci_fp, expo_units,
                      #scale_m2,
                      tmp_path):
    
    dialog_fixt.lineEdit_wdir.setText(str(tmp_path))
    dialog_fixt.lineEdit_tab3dataInput_curveName.setText(testCase)
    dialog_fixt.lineEdit_tab3dataInput_cifp.setText(ci_fp)
    
    #set the QComboBox to match the value of 'expo_units'
    dialog_fixt.comboBox_tab3dataInput_expoUnits.setCurrentText(expo_units)
    
    """changed this to a drop down on tab4
    if scale_m2: 
        dialog_fixt.radioButton_tab3dataInput_rcvm2.setChecked(True)
    else:
        dialog_fixt.radioButton_tab3dataInput_rcvm2.setChecked(False)
    """
        
    """not needed... the default is set during connect_slots
    dialog_fixt.lineEdit_tab3dataInput_drfFp.setText(drf_db_default_fp)"""
    
    print('tab3dataInput setup')
    
    return True
    

@pytest.fixture(scope='function') 
def tab4createCurve(dialog_fixt, scale_m2,
                      tmp_path):
    
    """
    
        scale_m2_index_d = {
        0:False, # Total ($/structure)
        1:True #Area-based ($/area)
        }
        
    """
    print('tab4createCurve start')
    # Find the index corresponding to scale_m2 directly using dictionary comprehension
    index = next((k for k, v in dialog_fixt.scale_m2_index_d.items() if v == scale_m2), None)

    if index is not None:
        dialog_fixt.comboBox_tab4actions_costBasis.setCurrentIndex(index)
        
        assert dialog_fixt.scale_m2_index_d[dialog_fixt.comboBox_tab4actions_costBasis.currentIndex()]==scale_m2
        
 
    else:
        # Optionally, handle the case where scale_m2 is not found in the dictionary
        raise ValueError(f"Invalid scale_m2 value: {scale_m2}")
    
    #check
    print('tab4createCurve finish')
            
 
    
 
    


@pytest.fixture(scope='function')    
def tableWidget_tab3dataInput_fixedCosts(dialog_fixt, fixed_costs_d):
    """assign the dictionary to the input table widget"""
    dialog_fixt._change_tab('tab3dataInput')
    
    set_fixedCosts(dialog_fixt, fixed_costs_d)
    
    return True
       
@pytest.fixture(scope='function')        
def set_projdb(dialog_fixt, proj_db_fp):
    """set the project database filepath onto the dialog"""
    dialog_fixt.lineEdit_tab4actions_projdb.setText(proj_db_fp)
    
        


#===============================================================================
# TESTS------
#===============================================================================

def test_01_parameters():
    df = bldg_meta_rqmt_df.loc[:, ['varName_ui', 'widgetName', 'type']].dropna(subset='varName_ui').set_index('varName_ui')
    assert set(building_details_options_d.keys()).difference(df.index)==set(), 'parameters_ui doesnt match paramter csv'
    

 
def test_02_init(dialog_fixt,):
    
    
    """uncomment the below to use pytest to launch the dialog interactively"""
    #===========================================================================
    # dialog.show()
    # QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect    
    # sys.exit(QApp.exec_()) #wrap
    #===========================================================================
 
 
    
    assert hasattr(dialog_fixt, 'logger')
    

#===============================================================================
# @pytest.mark.parametrize('testCase',[
#     'case1',
#     #'case2',
#     ], indirect=False)
# @pytest.mark.parametrize('scale_m2',[True], indirect=False)
# def test_init_prepopulate(dialog_fixt, set_all_tabs):
#     """init and pre-populate the inputs
#     useful for manual tests"""
#      
#     """manual inspection only"""
#     dialog_fixt._change_tab('tab4actions')
#      
#     QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect
#     
#     sys.exit(QApp.exec_()) #wrap
#===============================================================================
 
    
#===============================================================================
# TESTS: PRIVATE-------
#===============================================================================
"""functions hidden from user"""


@pytest.mark.parametrize('testCase',[
    'case1',
    '01',
    '02',
    #'case2',
    ], indirect=False)
def test_03_get_building_details(dialog_fixt, 
                         tab2bldgDetils, #calling this sets the values on the UI
                         bldg_meta_d, #from conftest
                         ):
    
 
    
    result = dialog_fixt._get_building_details()
    
    for k,v in bldg_meta_d.items():
        assert k in result, f'key \'{k}\' missing in result'
        if k.endswith('Units'): #skip m^2
            continue
        assert v==result[k], f'value for \'{k}\' mismatch'
 


@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
def test_04_get_fixed_costs(dialog_fixt, 
                         tableWidget_tab3dataInput_fixedCosts, #calling this sets the values on the UI
                         fixed_costs_d 
                         ):
    
    result_d = dialog_fixt._get_fixed_costs()
 
    assert result_d==fixed_costs_d
    
    
#===============================================================================
# TESTS: DIALOG FUNCTIONALITY--------
#===============================================================================

def test_05_radioButton_tab4actions_runControl(dialog_fixt):
    """check radio button logic"""

    b1 = dialog_fixt.radioButton_tab4actions_runControl_all
    b2 = dialog_fixt.radioButton_tab4actions_runControl_individ
    
    button_l = [
        dialog_fixt.pushButton_tab4actions_step1,
        #dialog_fixt.pushButton_tab4actions_step2,
        #dialog_fixt.pushButton_tab4actions_step3,
        #dialog_fixt.pushButton_tab4actions_step4        
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
                     
                 

        
 
@pytest.mark.parametrize('testCase',[
    'case1',
    #'case2',
    ], indirect=False)
@pytest.mark.parametrize('testPhase', ['c03'])
def test_06_pushButton_tab4actions_read(dialog_fixt, set_projdb):
    """test read project database button"""
    
    w = dialog_fixt.pushButton_tab4actions_read
    
    enable_widget_and_parents(w) #need to enable the button for it to work    
    
    QTest.mouseClick(w, Qt.LeftButton) #dialog_fixt.Bldgsdialog_fixt.action_read_proj_db()
    

 
 
@pytest.mark.parametrize('buttonName, lineName, QFileDialogTypeName',[
     ('pushButton_wd','lineEdit_wdir','getExistingDirectory'),
     ('pushButton_tab3dataInput_cifp','lineEdit_tab3dataInput_cifp', 'getOpenFileName'),
     ('pushButton_tab3dataInput_drfFp','lineEdit_tab3dataInput_drfFp', 'getOpenFileName'),
     ('pushButton_tab4actions_browse', 'lineEdit_tab4actions_projdb', 'getOpenFileName'),
     ])  
def test_07_file_buttons(dialog_fixt, buttonName, lineName, QFileDialogTypeName):
    """check all the load file buttons"""
    
    #retrieve button widget
    assert hasattr(dialog_fixt, buttonName), buttonName
    w = getattr(dialog_fixt, buttonName)    
    enable_widget_and_parents(w)
    
    #lineEdit widget
    assert hasattr(dialog_fixt, lineName)
    lineWidget = getattr(dialog_fixt, lineName)
    
    #PyQt5.QtWidgets.QFileDialog.
    
    with patch('PyQt5.QtWidgets.QFileDialog.' + QFileDialogTypeName, return_value=('test_string', '')):
        # Simulate a mouse click on the browse button
        print(f'clicking {buttonName} from within mock')
        QTest.mouseClick(w, Qt.LeftButton)

        # Check that the line edit's text is the expected filename
        assert lineWidget.text() == 'test_string', f'test string failed to set on {lineName}'
    
    
 
#===============================================================================
# TESTS: Dialog Actions--------
#===============================================================================
"""simulate user interface"""


    
 
@pytest.mark.parametrize('testCase',[
    'case1',
    'case2', #db mismatch case
    'case4_R2'
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True], indirect=False)
@pytest.mark.parametrize('ciPlot',[True], indirect=False)
@pytest.mark.parametrize('drfPlot',[True], indirect=False) 
def test_08_action_tab4actions_step1(dialog_fixt,
                                  set_all_tabs, ciPlot, drfPlot, 
                                  ):
    """test the step 1 button for _run_c00_setup_project'"""
    
    
    
    
    #===========================================================================
    # settup diablog
    #===========================================================================

    dialog_fixt._change_tab('tab4actions')
    
    w = dialog_fixt.pushButton_tab4actions_step1
    
    enable_widget_and_parents(w) #need to enable the button for it to work
    
    if ciPlot:
        cbox = dialog_fixt.checkBox_tab4actions_step1_ciPlot
        enable_widget_and_parents(cbox)
        cbox.setChecked(True)
        
    if drfPlot:
        cbox = dialog_fixt.checkBox_tab4actions_step1_drfPlot
        enable_widget_and_parents(cbox)
        cbox.setChecked(True)
        
    
    #===========================================================================
    # execute test
    #===========================================================================
     
    QTest.mouseClick(w, Qt.LeftButton)  #BldgsDialog.action_tab4actions_step1()
    
 
    #===========================================================================
    # check
    #===========================================================================
    assert_proj_db_fp(dialog_fixt._get_proj_db_fp())
     
    print('finished')
    
 
 
def _run_tab4actions_setup(dialog_fixt, button_name, checkbox_names=None):
    """
    Common setup and execution for tab4actions tests.
 
    """
    # Switch to the appropriate tab and enable the target button.
    dialog_fixt._change_tab('tab4actions')
    button = getattr(dialog_fixt, button_name)
    enable_widget_and_parents(button)
    
    # Always enable the figure saving checkbox.
    dialog_fixt.checkBox_tab4actions_saveFig.setChecked(True)
    
    # Enable and check each provided checkbox.
    if checkbox_names:
        for cb_name in checkbox_names:
            cb = getattr(dialog_fixt, cb_name)
            enable_widget_and_parents(cb)
            cb.setChecked(True)
    
    # Execute: simulate a mouse click on the button.
    click(button)
    #QTest.mouseClick(button, Qt.LeftButton)
    
    
    

 
 


@pytest.mark.dev
@pytest.mark.parametrize('testCase', [
    #'case1',
    'case2',
    #===========================================================================
    # pytest.param('case2', marks=pytest.mark.xfail(
    #                             raises=(KeyError,), 
    #                             reason="missing DRF entries")),
    #===========================================================================
    #'case4_R2'
    ])
@pytest.mark.parametrize('testPhase', ['c01'])
@pytest.mark.parametrize('scale_m2', [True], indirect=False)
def test_09_action_tab4actions_step2(dialog_fixt, set_all_tabs, set_projdb, testCase, testPhase, scale_m2, monkeypatch):
    """
    Test for Step2 c01_join_drf

    """
    expected_tables = expected_tables_base + ['c01_depth_rcv']
    
    run_test = lambda: _run_tab4actions_setup(
                dialog_fixt,
                button_name='pushButton_tab4actions_step2', #_run_c01_join_drf()
                checkbox_names=['checkBox_tab4actions_step2_plot']
            )


    if testCase=='case2':
        def patch_dbMisMatch(*args, **kwargs):
            """tried to throw an error here and catch it with pytest.raises
            spent 30 m and couldnt figure it out
            some problem with an error in the tear down
            """
            print('patch_dbMisMatch')
  
        #patch teh dbMisMatch dialog_fixt
        monkeypatch.setattr(dialog_fixt, "_launch_dialog_dbMismatch", patch_dbMisMatch)
    
        """for dev"""
        #with pytest.raises(KeyError, match="launch_dialog_dbMismatch"):
        #run_test()
        
    else:
        run_test()
        # Verification: check the project DB for the expected tables.
        assert_proj_db_fp(dialog_fixt._get_proj_db_fp(), expected_tables=expected_tables)




 
@pytest.mark.parametrize('testCase', ['case4_R2'])
@pytest.mark.parametrize('testPhase', ['c02'])
@pytest.mark.parametrize('scale_m2', [True], indirect=False)
def test_10_action_tab4actions_step3(dialog_fixt, set_all_tabs, set_projdb, testCase, testPhase, scale_m2):
    """
    Test for Step3 
    """
    expected_tables = expected_tables_base + ['c01_depth_rcv', 'c02_ddf']
    _run_tab4actions_setup(
        dialog_fixt,
        button_name='pushButton_tab4actions_step3',
        checkbox_names=['checkBox_tab4actions_step3_plot']
    )
    # Verification: check the project DB for the expected tables.
    assert_proj_db_fp(dialog_fixt._get_proj_db_fp(), expected_tables=expected_tables)


# Test for action step4
 
@pytest.mark.parametrize('testCase', ['case4_R2'])
@pytest.mark.parametrize('testPhase', ['c03'])
@pytest.mark.parametrize('scale_m2', [True], indirect=False)
def test_11_action_tab4actions_step4(dialog_fixt, set_all_tabs, set_projdb, testCase, testPhase, scale_m2):
    """
     Test for Step4
    """
    expected_tables = expected_tables_base + ['c01_depth_rcv', 'c02_ddf']
    _run_tab4actions_setup(
        dialog_fixt,
        button_name='pushButton_tab4actions_step4',
        checkbox_names=[]
    )
    # Verification: check the project DB for the expected tables.
    assert_proj_db_fp(dialog_fixt._get_proj_db_fp(), expected_tables=expected_tables)
    
    
    

    
#
@pytest.mark.parametrize('testCase',[
    #'case1',
    #pytest.param('case2', marks=pytest.mark.xfail(raises=(ValueError), reason="this case is missing some DRF entries")),
    #'case3',
    'case4_R2'
    ], indirect=False)
@pytest.mark.parametrize('scale_m2',[True, False], indirect=False)
def test_12_action_tab4actions_runAll(dialog_fixt, set_all_tabs): 
    """test combined
    
    no need to test plots here
    """
    dialog_fixt._change_tab('tab4actions')
    
    #plot over-rides
    dialog_fixt.checkBox_tab4actions_step3_plot.setChecked(True)
    
    QTest.mouseClick(dialog_fixt._get_child('pushButton_tab4actions_run'), Qt.LeftButton)  
    
    #check
    assert_proj_db_fp(dialog_fixt._get_proj_db_fp(), expected_tables=expected_tables_base+['c01_depth_rcv', 'c02_ddf'])
    
    
    
    
    
    
    
    
    

    