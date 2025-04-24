'''
Created on Apr. 16, 2024

@author: cef
'''
from unittest.mock import Mock
import os, logging, sys
import pytest
#from unittest.mock import patch

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt 
from qgis.gui import QgisInterface

from cancurve.parameters import src_dir

#===============================================================================
# data
#===============================================================================
from definitions import test_data_dir as test_data_dir_master
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
#test_data_dir_master = os.path.join(src_dir, 'tests', 'data')

#===============================================================================
# pytest custom config-------
#===============================================================================
 

def pytest_runtest_teardown(item, nextitem):
    """custom teardown message"""
    test_name = item.name
    print(f"\n{'='*20} Test completed: {test_name} {'='*20}\n\n\n")
    
def pytest_report_header(config):
    """modifies the pytest header to show all of the arguments"""
    return f"pytest arguments: {' '.join(config.invocation_params.args)}"


#===============================================================================
# Pytest-qgis fixes--------
#===============================================================================

@pytest.fixture(scope="session")
def qgis_iface_stub(qgis_iface: QgisInterface):
    """
    stub message logger
    
    BACKGEROUND================
    some stub implementations are broken in the pytest-qgis package.
    need to over-write them here
    
    see issues:
    https://github.com/GispoCoding/pytest-qgis/issues/26
    
    USE/WARNING===================
    need to excplicitly import this into each test target (otherwise the stub will not be inherited)
    
    """
    
    # Create a new mock object to simulate the QgsMessageBar instance.
    message_bar_mock = Mock()
    # Provide a pushMessage mock that can be called with any combination of arguments.
    message_bar_mock.pushMessage = Mock()
     
    # Since the QGIS API expects iface.messageBar() to be called,
    # assign a callable (lambda) that returns our message_bar_mock.
    qgis_iface.messageBar = lambda: message_bar_mock

 

    return qgis_iface

#===============================================================================
# HELPERS----------
#===============================================================================
def click(widget):
    widgetname = widget.objectName() if widget.objectName() else str(widget)
    
    #check that the widget is enabled
    assert widget.isEnabled(), f'widget is not enabled: {widgetname}'
    sys.stdout.flush()
    print(f"\n\nclicking: \'{widgetname}\'\n{'=' * 80}\n\n")
    return QTest.mouseClick(widget, Qt.LeftButton)

#===============================================================================
# fixtrues--------
#===============================================================================



@pytest.fixture(scope='function')
def logger():
    logging.basicConfig(
                #filename='xCurve.log', #basicConfig can only do file or stream
                force=True, #overwrite root handlers
                stream=sys.stdout, #send to stdout (supports colors)
                level=logging.INFO, #lowest level to display
                format='%(asctime)s %(levelname)s %(name)s: %(message)s',  # Include timestamp
                datefmt='%H:%M:%S'  # Format for timestamp
                )
    
    #get a new logger and lower it to avoid messing with dependencies
    log = logging.getLogger(str(os.getpid()))
    log.setLevel(logging.DEBUG)
    
    
    return log



 