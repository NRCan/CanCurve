'''
Created on Apr. 27, 2024

@author: cef
'''
 
 
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (
    QFormLayout, QWidgetItem, QLabel, QLineEdit, QComboBox,
    QTableWidget, QWidget,
    )

from qgis.PyQt import QtWidgets

def assert_string_in_combobox(combo_box: QComboBox, target_string: str):
    """
    Asserts that the given string is present as an item in the specified ComboBox.

    Args:
        combo_box: The QComboBox to check.
        target_string: The string to search for within the ComboBox items.
    """

    for index in range(combo_box.count()):
        if combo_box.itemText(index) == target_string:
            return  # Assertion passes if the string is found

    raise AssertionError(f"String '{target_string}' not found in ComboBox items")


def tableWidget_to_dataframe(tableWidget: QTableWidget):
    """Converts the contents of a QTableWidget to a pandas DataFrame.

    Args:
        tableWidget: The QTableWidget instance to convert.

    Returns:
        A pandas DataFrame containing the data from the table.
    """

    headers = []
    for column in range(tableWidget.columnCount()):
        header_item = tableWidget.horizontalHeaderItem(column)
        headers.append(header_item.text() if header_item else '')

    data = []
    for row in range(tableWidget.rowCount()):
        row_data = []
        for column in range(tableWidget.columnCount()):
            item = tableWidget.item(row, column)
            row_data.append(item.text() if item else '')
        data.append(row_data)

    return pd.DataFrame(data, columns=headers)


def get_formLayout_data(form_layout: QFormLayout) -> dict:
    """Retrieves field (label) and value pairs from a QFormLayout.

    Args:
        form_layout: The QFormLayout instance to extract data from.

    Returns:
        A dictionary where keys are field labels and values are the
        corresponding widget values.
    """

    assert form_layout.rowCount()>0
    
    field_values = {}
    for row in range(form_layout.rowCount()):
        #retrieve widgets
        labelWidget = form_layout.itemAt(row, QFormLayout.LabelRole).widget() 
        valueWidget = form_layout.itemAt(row, QFormLayout.FieldRole).widget()
        
        #retrieve values
        field_values[labelWidget.objectName() ] = _get_widget_value(valueWidget)

    assert len(field_values)==form_layout.rowCount(), f'failed to retrieve all values'
    return field_values

def get_gridLayout_data(grid_layout):
    
    num_rows = grid_layout.rowCount()
    num_columns = grid_layout.columnCount()

    res_lib = dict()
    for row in range(num_rows):
        res_lib[row] = dict()
        for col in range(num_columns):
            grid_item = grid_layout.itemAtPosition(row, col)
            if grid_item is not None:
                v = _get_widget_value(grid_item.widget())
            else:
                v=None
            
            res_lib[row][col] = v
            

    return res_lib

def _get_widget_value(widget):
    """Handles common widget types to extract their value."""
    if isinstance(widget, QLineEdit):
        return widget.text()
    elif isinstance(widget, QComboBox):
        return widget.currentText() 
    elif isinstance(widget, QLabel):
        return widget.text()
    # Add more cases for other widget types (QSpinBox, QCheckBox, etc.)
    else:
        return None  # Or raise an exception if unsupported


class DialogQtBasic():
    """generic dialog methods"""
    
            
    def _get_child(self, childName, childType=QtWidgets.QPushButton):
        child = self.findChild(childType, childName)
        assert not child is None, f'failed to get {childName} of type \'{childType}\''
        return child
    
    def _change_tab(self, tabObjectName): #try to switch the tab on the gui
        try:
            tabw = self.tabWidget
            index = tabw.indexOf(tabw.findChild(QWidget, tabObjectName))
            assert index > 0, 'failed to find index?'
            tabw.setCurrentIndex(index)
        except Exception as e:
            self.logger.error(f'failed to change to {tabObjectName} tab w/ \n    %s' % e)