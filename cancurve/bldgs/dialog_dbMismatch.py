'''
Created on Mar 4, 2025

@author: cef
'''

#===============================================================================
# Imports----------
#===============================================================================
import os, sys, sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QTableView
from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    )


from ..hp.qt import (
        DialogQtBasic, get_formLayout_data, get_gridLayout_data, get_tabelWidget_data,
        enable_widget_and_parents, enable_widget_and_children, set_tableWidget_data, set_tableView_data
        ,get_tableView_data)

from ..hp.plug import plugLogger

from .assertions import (
    assert_ci_df, assert_drf_db, assert_drf_df, assert_proj_db_fp, assert_proj_db,
    assert_bldg_meta_d, assert_CanFlood_ddf, assert_fixed_costs_d, assert_scale_factor
    )

FORM_CLASS2, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dbMismatch_dialog.ui'), resource_suffix='')           
class dbMismatchDialog(QtWidgets.QDialog, FORM_CLASS2, DialogQtBasic):
    def __init__(self, 
                 parent=None, #not sure what this is supposed to be... 
                 iface=None,
                 debug_logger=None, #testing only
                 pluginObject=None, #actual parent
                 proj_db_fp=None, #path to the project database
                 **kwargs):   

            super(dbMismatchDialog, self).__init__(parent)
            
            self.setupUi(self)
            self.pluginObject=pluginObject
            self.iface=iface
            
            self.proj_db_fp = proj_db_fp
            #assert_proj_db(proj_db_fp)
            
            if self.proj_db_fp:
                with sqlite3.connect(self.proj_db_fp) as conn:
                    assert_proj_db(conn)
 
            
            
            #setup logger
            self.logger = plugLogger(self.iface, parent=self, statusQlab=self.progressText,
                                     debug_logger=debug_logger)
        
        
            self.connect_slots(**kwargs)
            

    def _load_tables(self, proj_db_fp=None, log=None):
        """load the tables from the project database and update the ui"""
        #=======================================================================
        # Defaults
        #=======================================================================
        if proj_db_fp is None: proj_db_fp = self.proj_db_fp
        if log is None: log = self.logger.getChild('_load_tables')
                
        #load tables from the project database
        log.debug(f'openning database from {proj_db_fp}')
        with sqlite3.connect(proj_db_fp) as conn:
            #=======================================================================
            # retrieve-----------
            #=======================================================================
            ci_df = pd.read_sql('SELECT * FROM c00_cost_items', conn, index_col=['category', 'component'])
            drf_df = pd.read_sql('SELECT * FROM c00_drf', conn, index_col=['category', 'component'])
    #check the data
        assert_drf_df(drf_df)
        assert_ci_df(ci_df)
    #compute the differences
        bx = np.invert(ci_df.index.isin(drf_df.index))
        self.ci_df = ci_df.loc[bx, :].copy()
    #update metadata widgets
        self.label_CI_entries_total.setText(str(len(ci_df)))
        self.label_CI_entries_missing.setText(str(bx.sum()))
        self.label_DRF_entries_total.setText(str(len(drf_df)))
        return drf_df, bx

    def connect_slots(self,
                      proj_db_fp=None
                      ):
        """connect signals and slots
        
        Parameters
        ----------
 
        """
        #=======================================================================
        # setup
        #=======================================================================
        log = self.logger.getChild('connect_slots')
        if proj_db_fp is None: 
            proj_db_fp = self.proj_db_fp
        else: 
            self.proj_db_fp = proj_db_fp
        
        #=======================================================================
        # data tables
        #=======================================================================
        
        #attach the project database        
        self.lineEdit_projDB.setText(proj_db_fp)
        
        #load the tables
        drf_df, bx = self._load_tables(proj_db_fp=proj_db_fp, log=log)
 
        
        log.debug(f'found {bx.sum()} differences')
        
        #load the cost item data into the table widget
        set_tableView_data(self.tableView_costItems, self.ci_df.reset_index())
        
       
        #create an empty table in the DRF table widget (copy columns from drf_df)
        #set_tableView_data(self.tableView_drf, pd.DataFrame(columns=drf_df.columns))
        drf_df_reset = drf_df.reset_index()

        # Extract the list of columns, including 'category' and 'component'
        drf_columns = drf_df_reset.columns.tolist()

        # Create an empty DataFrame with these columns
        empty_drf_df = pd.DataFrame(columns=drf_columns)
        #empty_drf_df = pd.DataFrame(columns=drf_columns)
        set_tableView_data(self.tableView_drf, empty_drf_df)
        

        #=======================================================================
        # functions
        #=======================================================================
        #self.pushButton_copyCItoDRF.clicked.connect(self._copy_ci_to_drf)      
        self.pushButton_copyCItoDRF.clicked.connect(
    lambda: self._copy_ci_to_drf(self.ci_df, self.tableView_costItems, self.tableView_drf)
)
        #self.pushButton_DRFtoProjDB.clicked.connect(self._copy_drf_to_db)  
 
    
    def launch(self):   
        self.exec_() #block execution until user closes
        
    def _get_drf_df_from_widget(self):
        #return get_tabelWidget_data(self.tableView_drf)
        return get_tableView_data(self.tableView_drf)

                     
    # def _copy_ci_to_drf(self,  drf_df=None):
    #     """copy selected entries from the cost-items data to create new entries in the DRF table"""
    #
    #
    #     if drf_df is None: drf_df = self._get_drf_df_from_widget()
    #
    #
    #     #identify rows selected in the CostItem widget
    #     selected_rows = self.tableView_costItems.selectionModel().selectedRows()
    #
    #     #get the data from these rows
    #     ci_df_selected = self.ci_df.iloc[[r.row() for r in selected_rows]]
    #
    #     #add new rows to the DRF table (from ci_df.loc[['category', 'component'])
    #     drf_df = drf_df.append(ci_df_selected)
    #
    #
    #
    
    def _copy_ci_to_drf(self, ci_df: pd.DataFrame, tableView_costItems: QTableView, tableView_drf: QTableView):
        # Reset index to access 'category' and 'component' as columns
        ci_df_reset = ci_df.reset_index()
        # Get current DRF data to maintain column structure
        drf_df = self._get_drf_df_from_widget()
        # Get selected rows from cost-items table
        selected_rows = tableView_costItems.selectionModel().selectedRows()
        if not selected_rows:
            return
        # Fetch only 'category' and 'component' columns from selected rows
        selected_data = ci_df_reset.loc[[r.row() for r in selected_rows], ['category', 'component']].copy()
        # Initialize missing DRF columns (excluding 'category' and 'component') with empty strings
        for col in drf_df.columns:
            if col not in selected_data.columns:
                selected_data[col] = ""  # or np.nan if preferred
        # Ensure correct column order as per DRF
        selected_data = selected_data[drf_df.columns]
        # Append selected data to DRF DataFrame
        drf_df = pd.concat([drf_df, selected_data], ignore_index=True)
        # Update the DRF table view with the new data
        set_tableView_data(tableView_drf, drf_df)

        return drf_df


    def _write_drf_to_projdb(self,
                             proj_db_fp=None,
                             drf_df=None,
                             ):
        
        #=======================================================================
        # defaults
        #=======================================================================
        log = self.logger.getChild('_write_drf_to_projdb')
        if proj_db_fp is None: proj_db_fp = self.proj_db_fp
        if drf_df is None: drf_df = self._get_drf_df_from_widget()
        
        assert_drf_df(drf_df)
        
        
        #check that all of the cost item entries are present
        bx = np.invert(self.ci_df.index.isin(drf_df.index))
        assert not bx.any(), 'not all cost items have been copied to the DRF table'
        
        #write        
        with sqlite3.connect(proj_db_fp) as conn:
            drf_df.to_sql('c00_drf', conn, if_exists='append', index=True)
 
        
        log.push(f'wrote {len(drf_df)} entries to {proj_db_fp}')
        
        #update the ui with the new tables
        _ = self._load_tables(log=log)
        
        
        
        
        
        
        
        
        
 