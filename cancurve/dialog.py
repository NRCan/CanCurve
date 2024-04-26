# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CanCurveDialog
                                 A QGIS plugin
 Creating depth-damage functions
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-04-24
        git sha              : $Format:%H$
        copyright            : (C) 2024 by NRCan
        email                : heather.mcgrath@canada.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, datetime, sys
import pandas as pd
import numpy as np

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets


from PyQt5.QtWidgets import (
    QFormLayout, QWidgetItem, QLabel, QLineEdit, QComboBox,
    QTableWidget, QWidget,
    )
 

from qgis.core import Qgis, QgsLogger, QgsMessageLog

from .parameters import building_meta_dtypes


#===============================================================================
# helpers-------
#===============================================================================
class plugLogger(object): 
    """pythonic logging interface"""
    
    log_tabnm = 'CanCurve' # qgis logging panel tab name
    
    log_nm = 'cc' #logger name
    
    def __init__(self, 
                 iface,
                 statusQlab=None,                 
                 parent=None,
                 log_nm = None,
                 debug_logger=None,
                 ):
        """
        
        params
        ---------
        debug_logger: python logging class
            workaround to capture QgsLogger
        """
        
        self.iface=iface
        self.statusQlab = statusQlab
        self.parent=parent
        self.debug_logger=debug_logger
        
        if  log_nm is None: #normal calls
            self.log_nm = '%s.%s'%(self.log_nm, self.parent.__class__.__name__)
        else: #getChild calls
            self.log_nm = log_nm
        
        
    def getChild(self, new_childnm):
        
        if hasattr(self.parent, 'logger'):
            log_nm = '%s.%s'%(self.parent.logger.log_nm, new_childnm)
        else:
            log_nm = new_childnm
        
        #build a new logger
        child_log = plugLogger(self.parent, 
                           statusQlab=self.statusQlab,
                           log_nm=log_nm)
        

        
        return child_log
    
    def info(self, msg):
        self._loghlp(msg, Qgis.Info, push=False, status=True)


    def debug(self, msg):
        self._loghlp(msg, -1, push=False, status=False)
        
        if not self.debug_logger is None: 
            self.debug_logger.debug(msg)
 
    def warning(self, msg):
        self._loghlp(msg, Qgis.Warning, push=False)

    def push(self, msg):
        self._loghlp(msg, Qgis.Info, push=True)

    def error(self, msg):
        """similar behavior to raising a QError.. but without throwing the execption"""
        self._loghlp(msg, Qgis.Critical, push=True)
        
    def _loghlp(self, #helper function for generalized logging
                msg_raw, qlevel, 
                push=False, #treat as a push message on Qgis' bar
                status=False, #whether to send to the status widget
                ):
        """
        QgsMessageLog writes to the message panel
            optionally, users can enable file logging
            this file logger 
        """

        #=======================================================================
        # send message based on qlevel
        #=======================================================================
        msgDebug = '%s    %s: %s'%(datetime.datetime.now().strftime('%d-%H.%M.%S'), self.log_nm,  msg_raw)
        
        if qlevel < 0: #file logger only            
            QgsLogger.debug('D_%s'%msgDebug)            
            push, status = False, False #should never trip
            
        else:#console logger
            msg = '%s:   %s'%(self.log_nm, msg_raw)
            QgsMessageLog.logMessage(msg, self.log_tabnm, level=qlevel)
            QgsLogger.debug('%i_%s'%(qlevel, msgDebug)) #also send to file
            
        #Qgis bar
        if push:
            try:
                self.iface.messageBar().pushMessage(self.log_tabnm, msg_raw, level=qlevel)
            except:
                QgsLogger.debug('failed to push to interface') #used for standalone tests
        
        #Optional widget
        if status or push:
            if not self.statusQlab is None:
                self.statusQlab.setText(msg_raw)
    
        
        
        
        
        
        
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

    field_values = {}
    for row in range(form_layout.rowCount()):
        label = form_layout.labelForField(form_layout.itemAt(row, QFormLayout.LabelRole).widget())
        widget = form_layout.itemAt(row, QFormLayout.FieldRole).widget()

        if label:
            field_values[label.text()] = _get_widget_value(widget)

    return field_values

def _get_widget_value(widget):
    """Handles common widget types to extract their value."""
    if isinstance(widget, QLineEdit):
        return widget.text()
    elif isinstance(widget, QComboBox):
        return widget.currentText() 
    # Add more cases for other widget types (QSpinBox, QCheckBox, etc.)
    else:
        return None  # Or raise an exception if unsupported

#===============================================================================
# Main Dialog----------
#===============================================================================
#append the path (resources_rc workaround)
sys.path.append(os.path.dirname(__file__))

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'cc_dialog.ui'), resource_suffix='')





class CanCurveDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, 
                 parent=None, #not sure what this is supposed to be... 
                 iface=None,
                 debug_logger=None, #testing only
                 ):
        """Constructor."""
        super(CanCurveDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        
        self.iface=iface
        
        #setup logger
        self.logger = plugLogger(self.iface, parent=self, statusQlab=self.progressText,
                                 debug_logger=debug_logger)
        
        self.connect_slots()
        
        self.logger.debug('CanCurveDialog init finish')
        #self.logger.info('this woriks?')
        
 
        
    def connect_slots(self):
        """
        using the cointaier (dict) self.launch_actions to store functions
            that should be called once the dialog is launched
            see self.launch()
        """
        log = self.logger.getChild('connect_slots')
        log.debug('connecting slots')
        
        
        #=======================================================================
        # general----------------
        #=======================================================================
        """are these needed?
        #ok/cancel buttons
        self.buttonBox.accepted.connect(self.reject) #back out of the dialog
        self.buttonBox.rejected.connect(self.reject)
        """
        
        
        #=======================================================================
        # Tab: Create Curve---------
        #=======================================================================
        self.pushButton_Tcc_run.clicked.connect(self.action_Tcc_run)
        
        
        
        
        
    def action_Tcc_run(self):
        """pushButton_Tcc_run"""
        log = self.logger.getChild('action_Tcc_run')
        log.push(f'start')
        
        #=======================================================================
        # #retrieve info from UI----------
        #=======================================================================
        ci_fp = self.lineEdit_di_cifp.text()
        drf_db_fp = self.lineEdit_di_drf_db_fp.text()
        
        out_dir = self.lineEdit_wdir.text()
        #curve_name = self.lineEdit_di_curveName.text() in settings_d
        bldg_meta = self.get_building_details()
        fixed_costs_d = self.get_fixed_costs()
        settings_d = self.get_settings()
        
        
        #=======================================================================
        # run actions-------
        #=======================================================================
        from cancurve.core import c00_setup_project, c01_join_drf, c02_group_story, c03_export
        
        c00_setup_project(
            ci_fp, drf_db_fp=drf_db_fp, bldg_meta=bldg_meta, fixed_costs_d=fixed_costs_d,
            settings_d=settings_d,

            
            )
        
    def _get_building_details(self):
        """retrieve dataa from Building Details tab"""
        
        get_formLayout_data(self.formLayout_t02_01)
        
        #check all of the keys are present
        building_meta_dtypes
        
    def _get_fixed_costs(self):
        """retireve fixed costs from 'Data Input' tab"""
        df_raw =  tableWidget_to_dataframe(self.tableWidget_di_fixedCosts)
        
        return df_raw.astype(float).set_index(df_raw.columns[0]).iloc[:, 0].to_dict()
 
 
        
    def _get_settings(self):
        """retrieve project settings from Data Input  tab"""
        return {
            'curve_name':self.lineEdit_di_curveName.text(),
            'scale_m2':self.radioButton_di_rcvm2.isChecked(), #retrieve from radio buttons
            }

        
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
        
        
        
        
 
        

        
