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


from tests.test_plugin import logger

from cancurve.bldgs.dialog_dbMismatch import dbMismatchDialog


#===============================================================================
# FIXTURES------
#===============================================================================

@pytest.fixture(scope='function') 
def dialog(qgis_iface):
    """dialog fixture.
    for interactive tests, see 'test_init' (uncomment block)"""
    
    #indirect parameters
 
    
    dialog =  dbMismatchDialog(parent=None, iface=qgis_iface,
                          debug_logger=logger, #connect python logger for rtests
 
                          )
 
 
    
    
    return dialog



#===============================================================================
# TESTS----------
#===============================================================================
def test_00_dialog_init(dialog):
    
    """uncomment the below to use pytest to launch the dialog interactively"""
    dialog.show()
    QApp = QApplication(sys.argv) #initlize a QT appliaction (inplace of Qgis) to manually inspect    
    sys.exit(QApp.exec_()) #wrap
    assert hasattr(dialog, 'logger')
 
 