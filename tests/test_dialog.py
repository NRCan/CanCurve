'''
Created on Apr. 26, 2024

@author: cef

tests dialogs
'''

import pytest

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt

 

from cancurve.dialog import CanCurveDialog
from tests.test_plugin import logger

#===============================================================================
# helpers-----
#===============================================================================
 

#===============================================================================
# fixtures------
#===============================================================================
@pytest.fixture(scope='function') 
def dialog(qgis_iface):
    return CanCurveDialog(parent=None, iface=qgis_iface,
                          debug_logger=logger, #connect python logger for rtests
                          )   


#===============================================================================
# tests------
#===============================================================================

def test_init(dialog):
    assert hasattr(dialog, 'logger')
    
@pytest.mark.dev 
def test_Tcc_run(dialog):
 
    QTest.mouseClick(dialog._get_child('pushButton_Tcc_run'), Qt.LeftButton)  

    