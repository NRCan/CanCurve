'''
Created on Apr. 26, 2024

@author: cef


testing QGIS elements
'''
import pytest
from qgis.core import QgsApplication, QgsProject 
import pytest_mock #required for overriding QGIS settings
#from pytest_mock import MockerFixture
 

from cancurve.plugin import CanCurve
#from qgis.PyQt.QtCore import QSettings
from PyQt5.QtCore import QSettings

 
def test_plugin_loads(qgis_app, qgis_iface, mocker):
    """Tests if the plugin adds its button to the QGIS interface correctly."""
  
    mocker.patch('PyQt5.QtCore.QSettings.value', return_value='en_EN') # Corrected import path 
   
    plugin = CanCurve(iface=qgis_iface)
    print('plugin init') 
    plugin.initGui()
    
    assert len(plugin.actions) == 1  # Expecting one action 
    assert plugin.actions[0].text() == "CanCurve"  # Check the action's text

 


#===============================================================================
# @pytest.mark.parametrize('dialogClass',[BuildDialog], indirect=True)
# def test_01_build_scenario(session):
#     dial = session.Dialog
#     dial._change_tab('tab_setup')
#     #===========================================================================
#     # setup
#     #===========================================================================
#     dial.linEdit_ScenTag.setText('test_01')
#     dial.lineEdit_wdir.setText(str(session.out_dir)) #set the working directory
#     #===========================================================================
#     # execute
#     #===========================================================================
#     """BuildDialog.build_scenario()"""
#  
#     QTest.mouseClick(dial.pushButton_generate, Qt.LeftButton)
#  
#     #===========================================================================
#     # check
#     #===========================================================================
#     assert os.path.exists(dial.lineEdit_cf_fp.text())
#===============================================================================