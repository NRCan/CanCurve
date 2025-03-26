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
from PyQt5.QtWidgets import QTableView, QAbstractItemView
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


from ..parameters import plugin_dir
resources_module_fp = os.path.join(plugin_dir, 'resources.py')
assert os.path.exists(resources_module_fp), resources_module_fp 
if not os.path.dirname(resources_module_fp) in sys.path:
    sys.path.append(os.path.dirname(resources_module_fp))
    

FORM_CLASS2, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dbMismatch_dialog.ui'), resource_suffix='')           
class dbMismatchDialog(QtWidgets.QDialog, FORM_CLASS2, DialogQtBasic):
    def __init__(self, 
                 parent=None, #not sure what this is supposed to be... 
                 iface=None,
                 logger=None, #testing only
                 #pluginObject=None, #actual parent
                 proj_db_fp=None, #path to the project database
                 ):   

            super(dbMismatchDialog, self).__init__(parent)
            
            self.setupUi(self)
            #self.pluginObject=pluginObject
            self.iface=iface
            
            self.proj_db_fp = proj_db_fp
            
            #assert_proj_db(proj_db_fp)
            #===================================================================
            # if self.proj_db_fp:
            #     with sqlite3.connect(self.proj_db_fp) as conn:
            #         assert_proj_db(conn)
            #===================================================================
 
            
            
            #setup logger
            self.logger = logger
        
            #retrieve some data from the parent
            self.settings_d = parent._get_settings()
            self.connect_slots(proj_db_fp=proj_db_fp)
            
            
            
    def __enter__(self):
        """Support the with-statement by returning self."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the dialog on exit:
          - Close and delete the dialog to remove it from the Qt event loop.
          - Clear internal data.
          - Return False to propagate any exceptions.
        """
        self.close()
        self.deleteLater()  # Schedule deletion from Qt's event loop.
        self._clear_data()
        return False

    def _clear_data(self):
        """
        Clear internal data and references to help with garbage collection.
        Adjust as needed for your application.
        """
        self.proj_db_fp = None
        self.settings_d = {}
        self.ci_df = None
        # Clear table views by setting their models to None.
        if hasattr(self, 'tableView_costItems'):
            self.tableView_costItems.setModel(None)
        if hasattr(self, 'tableView_drf'):
            self.tableView_drf.setModel(None)
        self.logger = None


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
        
        drf_df_reset = drf_df.reset_index()
        # Extract the list of columns, including 'category' and 'component'
        drf_columns = drf_df_reset.columns.tolist()
        # Create an empty DataFrame with these columns
        empty_drf_df = pd.DataFrame(columns=drf_columns)
        set_tableView_data(self.tableView_drf, empty_drf_df)
        
        for col in range(2, 19): 
            self.tableView_drf.setColumnWidth(col, 9)
            
        #=======================================================================
        # exposure units
        #=======================================================================
 
        self.label_Depth_Units.setText(self.settings_d['expo_units'])
        #=======================================================================
        # functions
        #=======================================================================    
        self.pushButton_copyCItoDRF.clicked.connect(
        lambda: self._copy_ci_to_drf(self.ci_df, self.tableView_costItems, self.tableView_drf))
        
        
        self.pushButton_DRFtoProjDB.clicked.connect(
        lambda: self._write_drf_to_projdb(self.proj_db_fp)) 
        
        def close_dialog():
            self.close()
    
        self.pushButton_close.clicked.connect(close_dialog) 
        
        self.progressBar.setValue(0)
        
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
        
        
        #=======================================================================
        # populate the cost item table
        #=======================================================================
        ci_df = ci_df.reset_index()
        set_tableView_data(self.tableView_costItems, ci_df,
                           #freeze_columns_l=range(len(ci_df.columns)), #freeze all columns
                           )
        
        self.tableView_costItems.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #=======================================================================
        # populate the DRF table template
        #=======================================================================
        drf_df_reset = drf_df.reset_index()
        # Extract the list of columns, including 'category' and 'component'
        drf_columns = drf_df_reset.columns.tolist()
        # Create an empty DataFrame with these columns
        empty_drf_df = pd.DataFrame(columns=drf_columns)
        set_tableView_data(self.tableView_drf, empty_drf_df,
                           freeze_columns_l=[0, 1],
                           )
        #self.progressBar.setValue(30)
        return drf_df, bx
        
    
    def launch(self):   
        self.exec_() #block execution until user closes
        
    def _get_drf_df_from_widget(self):
        return get_tableView_data(self.tableView_drf)

                     
    def _copy_ci_to_drf(self, ci_df: pd.DataFrame, tableView_costItems: QTableView, tableView_drf: QTableView):
        log = self.logger.getChild('_copy_ci_to_drf')
        
        log.info(f"Copying selected cost items ({ci_df.shape} to DRF table.")
        self.progressBar.setValue(5) 
        # Reset index to access 'category' and 'component' as columns
        ci_df_reset = ci_df.reset_index()
        # Get current DRF data to maintain column structure
        drf_df = self._get_drf_df_from_widget()
        # Get selected rows from cost-items table
        selected_rows = tableView_costItems.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        # Fetch only 'category' and 'component' columns from selected rows
        selected_indices = [r.row() for r in selected_rows]
        selected_data = ci_df_reset.iloc[selected_indices][['category', 'component']].copy()
        
        self.progressBar.setValue(50) 
        # Initialize missing DRF columns (excluding 'category' and 'component') with empty strings
        for col in drf_df.columns:
            if col not in selected_data.columns:
                selected_data[col] = np.nan  # or np.nan if preferred
        # Ensure correct column order as per DRF
        selected_data = selected_data[drf_df.columns]
        
        #filter out any ['category', 'component'] matches from selected_data that exist in the DRF
        #keep these as columns, but treat them as a 2 level multindex (i.e., combinations)
        merged_df = selected_data.merge(
                    drf_df[['category', 'component']], 
                    on=['category', 'component'], 
                    how='left', 
                    indicator=True
                )
        
        new_data = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
        self.progressBar.setValue(60)
        
        # Append only the new rows (if any) to the current DRF DataFrame.
        if not new_data.empty:
            drf_df = pd.concat([drf_df, new_data], ignore_index=True)
        else:
            log.info("No new rows to add; all selected items already exist in DRF.")
        
        
        # Update the DRF table view with the new data
        set_tableView_data(tableView_drf, drf_df.fillna(0.0),
                           freeze_columns_l=[0, 1],
                           )
        
        self.progressBar.setValue(100)
        for col in range(2, 19):  # 19 is exclusive, so it covers 2 to 18
            self.tableView_drf.setColumnWidth(col, 9)
        
        
        self.progressBar.setValue(0)    
        return drf_df


    def _write_drf_to_projdb(self, proj_db_fp=None, drf_df=None):
        #=======================================================================
        # Setup and defaults
        #=======================================================================
        self.progressBar.setValue(5)
        log = self.logger.getChild('_write_drf_to_projdb')
        if proj_db_fp is None:
            proj_db_fp = self.proj_db_fp
        log.push(f'Writing project db: {proj_db_fp}')
    
        if drf_df is None:
            drf_df = self._get_drf_df_from_widget()
    
        if drf_df.empty:
            log.push("The DataFrame is empty, nothing to write.")
            return 
        
        #=======================================================================
        # Add 'bldg_layout' to satisfy the assert 
        #=======================================================================
        self.progressBar.setValue(10)
    # Ensure 'category' and 'component' are set as the index
        if 'category' in drf_df.columns and 'component' in drf_df.columns:
        # Convert 'category' and 'component' back to index if they're columns
            if not isinstance(drf_df.index, pd.MultiIndex):
                drf_df = drf_df.set_index(['category', 'component'])
    
        if 'bldg_layout' not in drf_df.index.names:
        # Add default 'bldg_layout' as a new index level
            drf_df['bldg_layout'] = 'default'
            drf_df.set_index('bldg_layout', append=True, inplace=True)
            drf_df = drf_df.reorder_levels(['category', 'component', 'bldg_layout'])
        
        # Convert only the data columns (not the index) to float
        self.progressBar.setValue(20)
        data_columns = drf_df.columns.difference(drf_df.index.names)

        # Convert the numeric columns to float (non-numeric values will become NaN)
        drf_df[data_columns] = drf_df[data_columns].apply(pd.to_numeric, errors='coerce')
        drf_df[data_columns] = drf_df[data_columns].astype(float)
    
        missing_mask = drf_df[data_columns].isna()

        if missing_mask.any().any():
            missing_rows = drf_df[missing_mask.any(axis=1)]
            log.push(f"ERROR: Missing column values detected. Aborting write to database.\n{missing_rows.to_string()}")
            return
        
        self.progressBar.setValue(50)
        log.push("All data columns have valid values.")
        #=======================================================================
        # Validation
        #=======================================================================
        assert_drf_df(drf_df)
        self.progressBar.setValue(60)
    
        #=======================================================================
        # Drop 'bldg_layout' before writing to database (if not needed in DB)
        #=======================================================================
        drf_df = drf_df.reset_index('bldg_layout', drop=True)
        self.progressBar.setValue(70)
        #=======================================================================
        # Write to Database
        #=======================================================================
        with sqlite3.connect(proj_db_fp) as conn:
            drf_df.to_sql('c00_drf', conn, if_exists='append', index=True)
            conn.commit()
    
            log.push(f'Wrote {len(drf_df)} entries to {proj_db_fp}')
            
            drf_df = drf_df.reset_index(level=['category', 'component'], drop=False)
            
        self.progressBar.setValue(90)
           
        #=======================================================================
        # Refresh UI with the new tables
        #=======================================================================
        _ = self._load_tables(log=log)
        self.progressBar.setValue(100)
        
        
        
        
        
        
        
        
 