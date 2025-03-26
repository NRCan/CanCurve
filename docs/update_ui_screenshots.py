"""auto update tab figures using pytest

could integreate this into the sphinx builder conf.py at some point.. but that seems overkill

This is a per-project script that should be shared with git tracking

needs to be run from the project pygis venv. eg:

    start cmd.exe /k python -m pytest --maxfail=10 %TEST_DIR% -c %SRC_DIR%\tests\pytest.ini

"""


import pytest
import os
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt

from tests.bldgs.test_02_dialog import (
    dialog, set_all_tabs, bldg_meta_d, tab2bldgDetils, tab3dataInput, tab4createCurve, 
    tableWidget_tab3dataInput_fixedCosts,fixed_costs_d, ci_fp, expo_units
    )

from cancurve.parameters import src_dir


def _write_tab_figure(dialog, output_image, tab_widget_name):
    tab_widget = dialog.findChild(QTabWidget)
    if not tab_widget:
        raise AssertionError("QTabWidget not found in the dialog.")
# Find the desired tab by its widget's objectName
    target_index = None
    for i in range(tab_widget.count()):
        child_widget = tab_widget.widget(i)
        if child_widget.objectName() == tab_widget_name:
            target_index = i
            tab_widget.setCurrentIndex(i)
            break
 
    if target_index is None:
        raise AssertionError(f"Tab with objectName '{tab_widget_name}' not found in the QTabWidget.")
# Adjust the dialog size to fit contents and render it to a QPixmap
    dialog.adjustSize()
    pixmap = QPixmap(dialog.size())
    dialog.render(pixmap)
# Save the rendered screenshot as a PNG
    output_dir = os.path.join(src_dir, 'docs', 'source', 'assets') # Directory for saving images
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_image)
    pixmap.save(output_path)
    print(f"Screenshot of tab '{tab_widget_name}' saved to {output_path}")
# Close the dialog after taking the screenshot
    dialog.close()
    
    
    

@pytest.mark.parametrize('output_image, tab_widget_name', [
    ('01-dialog-welcome.png', 'tab1welcome'),
    ('02-dialog-metadata.PNG', 'tab2bldgDetils'),
    ('02-dialog-dataInput.PNG', 'tab3dataInput'),
    ('02-dialog-createCurve.PNG', 'tab4actions'),
    # Add more cases here if needed
], indirect=False)
def test_capture_tab_screenshot(dialog, output_image, tab_widget_name):
    """
    Capture a screenshot of a specific tab in a PyQt5 QDialog and save it as a PNG.

    Parameters:
        dialog (QDialog): The dialog object provided by pytest-qgis.
        output_image (str): Name of the output PNG file.
        tab_widget_name (str): Object name of the tab to capture.
    """

    # Ensure the dialog is loaded and find the QTabWidget
    _write_tab_figure(dialog, output_image, tab_widget_name)


 
@pytest.mark.parametrize('output_image, tab_widget_name, testCase', [
    ('03_01_meta01.PNG', 'tab2bldgDetils', 'case1'), #TODO: allow tutorial names rather than case names
    ('03_01_dataInput.PNG', 'tab3dataInput', 'case1'),
 
    # Add more cases here if needed
], indirect=False)
def test_capture_tab_screenshot_populated(dialog, output_image, tab_widget_name, tab2bldgDetils, tab3dataInput):
    """
    Capture a screenshot of a specific tab in a PyQt5 QDialog, populate,
    """

    # Ensure the dialog is loaded and find the QTabWidget
    _write_tab_figure(dialog, output_image, tab_widget_name)
    
    
    
@pytest.mark.dev
@pytest.mark.parametrize('scale_m2', [True]) #TODO: clean up so this isn't needed
@pytest.mark.parametrize('output_image, tab_widget_name, testCase', [
    ('03_01_cc.PNG', 'tab4actions', 'case1'),
], indirect=False)
def test_capture_tab_screenshot_populated_tag4(dialog, output_image, tab_widget_name, set_all_tabs):
    """
    Capture a screenshot of a specific tab in a PyQt5 QDialog, populate,
    """

    #plot over-rides
    dialog.checkBox_tab4actions_step3_plot.setChecked(True)
    
    QTest.mouseClick(dialog._get_child('pushButton_tab4actions_run'), Qt.LeftButton)  
    
    # Ensure the dialog is loaded and find the QTabWidget
    _write_tab_figure(dialog, output_image, tab_widget_name)
    
    
    
    
    
    