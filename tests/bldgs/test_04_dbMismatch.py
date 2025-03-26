'''
Created on Mar 4, 2025

@author: cef

testing the dbmismatch module
'''


#===============================================================================
# IMPORTS----------
#===============================================================================
import pytest, time, sys, inspect


from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt, QApplication, QPoint
from qgis.PyQt import QtWidgets


from tests.test_plugin import logger

from cancurve.bldgs.dialog_dbMismatch import dbMismatchDialog

#===============================================================================
# HELPERS------
#===============================================================================
class BldgsDialog_emulator(QtWidgets.QDialog):
    """emulate teh building dialog"""
    def __init__(self):
        super(BldgsDialog_emulator, self).__init__(None)
        return 
    def _get_settings(self, logger=None):
        """retrieve project settings from Data Input tab"""
        return {
            'curve_name':'some curve name', 
            'scale_m2':'some cost basis', #retrieve from radio buttons
            'expo_units':'meters',
            }

#===============================================================================
# FIXTURES------
#===============================================================================

@pytest.fixture(scope='function') 
def dialog(qgis_iface, proj_db_fp):
    """dialog fixture.
    for interactive tests, see 'test_init' (uncomment block)"""
    
    #indirect parameters
    
    parent = BldgsDialog_emulator()
 
    
    dialog =  dbMismatchDialog(parent=parent, iface=qgis_iface,
                          logger=logger, #connect python logger for rtests
                          proj_db_fp=proj_db_fp,
 
                          )
 
 
    
    
    return dialog



#===============================================================================
# TESTS----------
#===============================================================================
@pytest.mark.parametrize('testCase', [
    'case2', 
    ])
@pytest.mark.parametrize('testPhase', ['c01'])
def test_00_dialog_init(dialog):
    
    """uncomment the below to use pytest to launch the dialog interactively"""
    #===========================================================================
    # dialog.launch()
    # QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect    
    # sys.exit(QApp.exec_()) #wrap
    #===========================================================================
    assert hasattr(dialog, 'logger')
 
 