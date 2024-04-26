'''
Created on Apr. 26, 2024

@author: cef


testing QGIS plugin
    see test_dialog for dialog tests
'''
import pytest, logging
from qgis.core import QgsApplication, QgsProject, Qgis, QgsLogger, QgsMessageLog



from cancurve.hp.logr import get_log_stream

 


#===============================================================================
# configure QGIS loggers for testing
#===============================================================================
logger = get_log_stream(level = logging.DEBUG)

def log_to_python(message, tag, level):
    """build action to connect to QgsMessageLog"""
    # Map QgsMessageLog level to Python logging level
    level_map = {
        Qgis.Info: logging.INFO,
        Qgis.Warning: logging.WARNING,
        Qgis.Critical: logging.ERROR,
    } 

    # Log the message using Python's logging module
    logger.log(level_map.get(level, logging.DEBUG), "[%s] %s", tag, message)
 
# Connect the function to QgsMessageLog
QgsApplication.messageLog().messageReceived.connect(log_to_python)

"""not sure how to capture this
QgsLogger.messageReceived.connect(log_to_python)"""





#===============================================================================
# tests --------
#===============================================================================



@pytest.mark.parametrize('qlevel',[Qgis.Info], indirect=False) 
def test_logging(qlevel, qgis_app):
    #caplog.set_level(logging.DEBUG)
    
    msg='test_message'
    QgsMessageLog.logMessage(msg, 'tabName', level=qlevel)
    #QgsLogger.debug('%i_%s'%(qlevel, msg)) #also send to file
    
    #assert "Test message" in caplog.text
    
    #print(f'finished test for {msg}')
 

 

def test_plugin_loads(qgis_app, qgis_iface, mocker):
    """Tests if the plugin adds its button to the QGIS interface correctly."""
    
    import pytest_mock #required for overriding QGIS settings
    from cancurve.plugin import CanCurve
  
    mocker.patch('PyQt5.QtCore.QSettings.value', return_value='en_EN') # Corrected import path 
   
    plugin = CanCurve(iface=qgis_iface)
    print('plugin init') 
    plugin.initGui()
    
    assert len(plugin.actions) == 1  # Expecting one action 
    assert plugin.actions[0].text() == "CanCurve"  # Check the action's text
    
 