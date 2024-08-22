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

#===============================================================================
# Imports----------
#===============================================================================
import os, sys, sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from PyQt5.QtTest import QTest
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    )

 

from ..config import dev_mode

from ..hp.basic import convert_to_number, force_open_dir
from ..hp.plug import plugLogger
from ..hp.qt import (
        DialogQtBasic, get_formLayout_data, get_gridLayout_data, get_tabelWidget_data,
        enable_widget_and_parents, enable_widget_and_children
        )

from .parameters import (
    drf_db_default_fp,home_dir, bldg_meta_rqmt_df
    )

from .parameters_ui import building_details_options_d
 


#===============================================================================
# helpers-------
#===============================================================================
 

#===============================================================================
# Main Dialog----------
#===============================================================================
#append the path (resources_rc workaround)
from ..parameters import plugin_dir
resources_module_fp = os.path.join(plugin_dir, 'resources.py')
assert os.path.exists(resources_module_fp), resources_module_fp 
if not os.path.dirname(resources_module_fp) in sys.path:
    sys.path.append(os.path.dirname(resources_module_fp))



# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
"""
help(uic)
help(uic.loadUiType)
print(sys.path)
"""
ui_fp = os.path.join(os.path.dirname(__file__), 'cc_bldgs_dialog.ui')
assert os.path.exists(ui_fp)
FORM_CLASS, _ = uic.loadUiType(ui_fp, resource_suffix='')

class BldgsDialog(QtWidgets.QDialog, FORM_CLASS, DialogQtBasic):
    

    
    
    def __init__(self, 
                 parent=None, #not sure what this is supposed to be... 
                 iface=None,
                 debug_logger=None, #testing only
                 pluginObject=None, #actual parent
                 show_plots=True,
                 ):
        """Dialog constructor
        
        Params
        ------
        show_plots: bool, True
            whether to call plt.show()
            useful for tests
            
        """
        super(BldgsDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.pluginObject=pluginObject
        self.iface=iface
        self.show_plots=show_plots
        
        #setup logger
        self.logger = plugLogger(self.iface, parent=self, statusQlab=self.progressText,
                                 debug_logger=debug_logger)
        
        self.connect_slots()
        
        #=======================================================================
        # children
        #=======================================================================
        self.dialog_dbMismatch=None
        
        self.logger.debug('CanCurveDialog init finish')
        #self.logger.info('this woriks?')
        
 
        
    def connect_slots(self):
        """on launch of ui, populate and connect"""
 
        log = self.logger.getChild('connect_slots')
        log.debug('connecting slots')
 
        
        
        #=======================================================================
        # general----------------
        #=======================================================================
        def close_dialog():
            self.logger.push(f'dialog reset')
            if not self.pluginObject is None:
                self.pluginObject.dlg=None
                self.pluginObject.first_start=True #not ideal
            self.close()
        
        self.close_pushButton.clicked.connect(close_dialog) 
        self.cancel_pushButton.clicked.connect(self.action_cancel_process)
        
        from cancurve import __version__
        self.label_version.setText(f'v{__version__}')
        
        #=======================================================================
        # development-----
        #=======================================================================
        if dev_mode:
            
            #add the cases 
            from .dialog_test_scripts import (
                test_cases_l, fixed_costs_master_d, test_data_dir_master
                )
            
            from ..hp.basic import find_single_file_by_extension
            
            self.comboBox_dev.addItems(test_cases_l)
            
            #add the action
            from cancurve.bldgs.dialog_test_scripts import set_tab2bldgDetils, set_fixedCosts
            
            def populate_ui():
                self.clear_tab4actions()
                #get the case
                testCase = self.comboBox_dev.currentText()
                
                #populate with the test data
                set_tab2bldgDetils(self, testCase)                
                set_fixedCosts(self, fixed_costs_master_d[testCase])
                
                wdir = os.path.join(os.path.expanduser('~'), 'CanCurve', testCase, 
                                    datetime.now().strftime('%Y%m%d%H%M%S'))
                self.lineEdit_wdir.setText(wdir)
                self.lineEdit_tab3dataInput_curveName.setText(testCase)
                
                #cost information
                tdata_dir = os.path.join(test_data_dir_master, testCase)
                ci_fp = find_single_file_by_extension(tdata_dir, '.csv')
                self.lineEdit_tab3dataInput_cifp.setText(ci_fp)
                
                self.logger.push(f'ui populated for testCase \'{testCase}\'')
                
            self.pushButton_dev.clicked.connect(populate_ui)
                
                
             
            
            
            
        #=======================================================================
        # Tab: 02 Building Details-------
        #=======================================================================
        
        #=======================================================================
        # populate ui
        #=======================================================================
        #populate form options from parameters
        for k,v in building_details_options_d.items():
            #append empty
            options_l = v
            #retrieve the combo box matching the name
            #log.debug(f'setting \'{k}\':{options_l}')
            comboBox = self._get_child(f'{k}_ComboBox', childType=QtWidgets.QComboBox)
            comboBox.addItems([str(e) for e in options_l])
            comboBox.setCurrentIndex(-1)
            
        #add the current date to the LineEdit
        """this is added by the core functions... no need to let the user edit
        self.dateCurveCreated_LineEdit.setText(datetime.datetime.now().strftime('%Y %m %d %H:%M:%S'))
        """
        
        #username
        self.createdBy_LineEdit.setText(os.getlogin())
        
        
        #=======================================================================
        # Tab: 03 Data Input-----
        #=======================================================================
        
        #=======================================================================
        # shortcuts
        #=======================================================================
        #shortcut to retrieve fixed costs per-story
        #maybe this should go elsewhere?
        self.fixed_costs_widget_d = {
            -1:self.doubleSpinBox_tab3dataInput_sm1,
            0:self.doubleSpinBox_tab3dataInput_s0
            }
        
        #=======================================================================
        # populate ui
        #=======================================================================
        self.lineEdit_tab3dataInput_drfFp.setText(drf_db_default_fp) #DRF default
        self.lineEdit_wdir.setText(home_dir)
        
        self.pushButton_wd_open.clicked.connect(
            lambda: force_open_dir(self.lineEdit_wdir.text())
            )
        
        #working directory browse 
        def pushButton_wd_QFileDialog(): 
            filename = QFileDialog.getExistingDirectory(
                self,  # Parent widget (your dialog)
                "Select working directory",  # Dialog title
                home_dir,  # Initial directory (optional, use current working dir by default)
                #"tabular data files;;Comma Separated Values (*.csv)"  # Example file filters
                )
            
            if filename =='':
                self.logger.debug('user cancelled QFileDialog')
                return
            
            #needed so we can have a single test for both types of file dialogs
            if isinstance(filename, tuple):
                filename=filename[0]
 
            if filename:
                self.lineEdit_wdir.setText(filename)
                
        self.pushButton_wd.clicked.connect(pushButton_wd_QFileDialog)
        
        
        
        
        #cost item browse
        def pushButton_tab3dataInput_cifp_QFileDialog():
            filename, _ = QFileDialog.getOpenFileName(
                self,  # Parent widget (your dialog)
                "Open Cost-Item file",  # Dialog title
                home_dir,  # Initial directory (optional, use current working dir by default)
                "comma separated values (*.csv)"  # Example file filters
                )
            if filename:
                self.lineEdit_tab3dataInput_cifp.setText(filename) 
        
        self.pushButton_tab3dataInput_cifp.clicked.connect(pushButton_tab3dataInput_cifp_QFileDialog)
        
        
        #DRF browse
        def pushButton_tab3dataInput_drfFp_QFileDialog():
            filename, _ = QFileDialog.getOpenFileName(
                self,  # Parent widget (your dialog)
                "Open DRF file",  # Dialog title
                home_dir,  # Initial directory (optional, use current working dir by default)
                "sqlite database files (*.db)"  # Example file filters
                )
            if filename:
                self.lineEdit_tab3dataInput_drfFp.setText(filename) 
        
        self.pushButton_tab3dataInput_drfFp.clicked.connect(pushButton_tab3dataInput_drfFp_QFileDialog)
        
 
        
        #=======================================================================
        # Tab: 04 Create Curve---------
        #=======================================================================
        #=======================================================================
        # run buttons
        #=======================================================================
        self.pushButton_tab4actions_run.clicked.connect(self.action_tab4actions_run)
        
 
        """NOTE: these are disabled by default"""
        self.pushButton_tab4actions_step1.clicked.connect(self.action_tab4actions_step1)        
        self.pushButton_tab4actions_step2.clicked.connect(self.action_tab4actions_step2)
        self.pushButton_tab4actions_step3.clicked.connect(self.action_tab4actions_step3)
        self.pushButton_tab4actions_step4.clicked.connect(self.action_tab4actions_step4)
        
        #set up radio button to control whether the sub-actions are enabled
        
        #create a function to enable the four actions
        def toggle_actions_enabled(checked):
            """Enables or disables actions based on radioButton_tab4actions_runControl_all state"""
            enabled = checked  # 'checked' will be True if the radio button is checked 
            
            #toggle first step
            enable_widget_and_children(self.groupBox_step01, enabled)
            enable_widget_and_children(self.groupBox_01wd_2, enabled)
            
            if not enabled: #turnother setps off
                enable_widget_and_children(self.groupBox_step02, enabled)
                enable_widget_and_children(self.groupBox_step03, enabled)
                enable_widget_and_children(self.groupBox_step04, enabled)
                
            self.pushButton_tab4actions_run.setEnabled(not enabled)
            print('toggle_actions_enabled finished')
        
        #assign the function as an action to be enabled anytime the radio button is checked
        self.radioButton_tab4actions_runControl_individ.toggled.connect(toggle_actions_enabled)
        
        
        #=======================================================================
        # project database
        #=======================================================================
        def proj_db_browse_QFileDialog():
            filename, _ = QFileDialog.getOpenFileName(
                self,  # Parent widget (your dialog)
                "Open CanCurve project database file",  # Dialog title
                home_dir,  # Initial directory (optional, use current working dir by default)
                "CanCurve project files (*.cancurve);;database files (*.db)"  # Example file filters
                )
            if filename:
                self.lineEdit_tab4actions_projdb.setText(filename)
 
                
        self.pushButton_tab4actions_browse.clicked.connect(proj_db_browse_QFileDialog)
        
        #read button
        self.pushButton_tab4actions_read.clicked.connect(self.action_read_proj_db)
        
        #clear

        
        self.pushButton_tab4actions_clear.clicked.connect(self.clear_tab4actions)
        #=======================================================================
        # wrap
        #=======================================================================
        log.debug(f'slots connected')
        
    def clear_tab4actions(self):
        old_fp = self.lineEdit_tab4actions_projdb.text()
        try:
            os.remove(old_fp)
        except Exception as e:
            self.logger.warning(f'failed to remove the existing project database filepath w/ \n    {e}')
            #raise IOError(e)
        
        self.lineEdit_tab4actions_projdb.clear()
        
        #clear progress bars
        self.progressBar_tab4actions_step1.setValue(0)
        self.progressBar_tab4actions_step2.setValue(0)
        self.progressBar_tab4actions_step3.setValue(0)
        self.progressBar_tab4actions_step4.setValue(0)
        
    def action_read_proj_db(self):
        """pushButton_tab4actions_read
        
        load the project database and set some ui conditions
        """
 
        log = self.logger.getChild('_run')
        
        
        proj_db_fp = self._get_proj_db_fp() 
        
        log.push(f'reading project database from {os.path.basename(proj_db_fp)}')
        
        self._read_db(proj_db_fp, log)
        
    
    def _read_db(self, proj_db_fp, log):
        #=======================================================================
        # imports
        #=======================================================================
        
        from .assertions import assert_proj_db
        from ..hp.sql import get_table_names
        import sqlite3
        
        
 
        #=======================================================================
        # get table names
        #=======================================================================        
        
        with sqlite3.connect(proj_db_fp) as conn:
            assert_proj_db(conn)
            
            table_names_l =get_table_names(conn)
            
        log.debug(f'read {len(table_names_l)} tables')
        #=======================================================================
        # activate buttons based on table presence
        #=======================================================================
        
        for tableName, d in {
            'c00_cost_items':{'groupBox':'groupBox_step02','progressBar':'progressBar_tab4actions_step1'},
            'c01_depth_rcv':{'groupBox':'groupBox_step03','progressBar':'progressBar_tab4actions_step2'},
            'c02_ddf':{'groupBox':'groupBox_step04','progressBar':'progressBar_tab4actions_step3'}            
            }.items():
            
            enable = tableName in table_names_l
            #turn teh group on
            enable_widget_and_children(getattr(self, d['groupBox']), enable)
            
            #set the progress on teh previous
            pb = getattr(self, d['progressBar'])
            if enable:
                pb.setValue(100)
            else:
                pb.setValue(0)
                
            
            
 
        
        
        
    def action_tab4actions_run(self):
        """main ALL runner button
        
        pushButton_tab4actions_run
        
        TODO: implement QgsTask
        
        """
        log = self.logger.getChild('tab4actions_run')
        log.push(f'start')
        
        out_dir = self.lineEdit_wdir.text()

        
        step_log = lambda x:log.info(f'\n\n\nStep {x}\n----------------------\n\n')
        #=======================================================================
        # run actions-------
        #=======================================================================
        
        #=======================================================================
        # step 1
        #=======================================================================`
        step_log(1)
        _, _, _, err_msg = self._run_c00_setup_project(logger=log, out_dir=out_dir)
        
        if not err_msg is None:
            log.warning(err_msg)
            return
        
        #=======================================================================
        # step 2
        #=======================================================================
        step_log(2)
        self._run_c01_join_drf(logger=log)
        
        step_log(3)
        self._run_c02_group_story(logger=log)
        
        step_log(4)
        _, ofp = self._run_c03_export(logger=log)
        
        log.push(f'workflow complete and DDF output to\n    {ofp}')
        
        return
        

        
    def action_tab4actions_step1(self):
        """step1 run button
        
        pushButton_tab4actions_step1"""
        log = self.logger.getChild('tab4actions_run')
        log.push(f'start')
        
        self._run_c00_setup_project()
        
        self._read_db(self._get_proj_db_fp(), log)
        

    def _launch_dialog_dbMismatch(self, msg): 
        self.dialog_dbMismatch = dbMismatchDialog(message=msg)  
        self.dialog_dbMismatch.exec_() # Show modally

    def _run_c00_setup_project(self, 
                               logger=None, out_dir=None):
        """retrive and run project setup
        
        re-factored so we can call it from multiple push buttons
        """
        #=======================================================================
        # defaults
        #=======================================================================
        if logger is None: logger = self.logger
        log = logger.getChild('_run')
        
        if out_dir is None: out_dir = self.lineEdit_wdir.text()
        
        progress = self.progressBar_tab4actions_step1 #progress bar for this function
        
        progress.setValue(5)
        #=======================================================================
        # #retrieve info from UI----------
        #=======================================================================
        
        ci_fp =         self.lineEdit_tab3dataInput_cifp.text()
        drf_db_fp =     self.lineEdit_tab3dataInput_drfFp.text()        
        
        #curve_name = self.lineEdit_di_curveName.text() in settings_d
        bldg_meta =     self._get_building_details(logger=log)
        
        #fixed costs from table
        try:
            fixed_costs_d = self._get_fixed_costs(logger=log)
        except Exception as e:
            raise IOError(f'failed to retrieve fixed costs data w/ \n    {e}')
        
        settings_d =    self._get_settings(logger=log)
        
        ofp = self._get_proj_db_fp() #load the one provided by the user
        
        #get buidling layout
        """seems like only the 'default' entries are working
        from .core import _get_building_layout_from_meta
        bldg_layout = _get_building_layout_from_meta(bldg_meta)
        
        bldg_meta['bldg_layout'] = bldg_layout"""
        bldg_meta['bldg_layout']='default'
        
        progress.setValue(50)
        #=======================================================================
        # run action--------
        #=======================================================================
        from .core import c00_setup_project as func
        
        
        ci_df, drf_df, ofp, err_msg =  func(
            ci_fp, drf_db_fp=drf_db_fp, bldg_meta=bldg_meta, fixed_costs_d=fixed_costs_d,
            settings_d=settings_d, log=log, out_dir=out_dir, ofp=ofp
            )
        
        progress.setValue(70)
        
        #=======================================================================
        # plots-----
        #=======================================================================
        cbox_d = {
            'ci':{'cbox':self.checkBox_tab4actions_step1_ciPlot,'df':ci_df},
            'drf':{'cbox':self.checkBox_tab4actions_step1_drfPlot, 'df':drf_df},
            }
        
        #setup both
        show_plot=False
        for k,v in cbox_d.items():
            if v['cbox'].isChecked():
                plt.close('all')
                show_plot=True
                break
 
            
        if show_plot:
            #loop and plots
            for i, (k,d) in enumerate(cbox_d.items()):
                log.info(f'plotting \'{k}\'')
                if d['cbox'].isChecked():
                    
                    #load the function
                    if k=='ci':
                        from .plots import plot_c00_costitems as func
                    elif k=='drf':
                        from .plots import plot_c00_DRF as func
                    else:
                        raise KeyError()
                    
                    #call
                    func(d['df'], log=log, figure=plt.figure(10+i))
                    
            log.info(f'launching matplotlib plot dialog')
            if self.show_plots: plt.show()
                
        
                    
        progress.setValue(80)
        
        #=======================================================================
        # post ui actions-------
        #=======================================================================
        #missing entries
        bx = ci_df['drf_intersect']
        if not bx.all():
            log.warning(f'intersection incomplete')
            self._launch_dialog_dbMismatch(err_msg)
                    
        
        self.lineEdit_tab4actions_projdb.setText(ofp)
        
        progress.setValue(95)
        
        
        
        progress.setValue(100)
        
        log.info(f'Step 1 complete w/ {ci_df.shape}')
        
        return ci_df, drf_df, ofp, err_msg
        
        
        
    
    def action_tab4actions_step2(self):
        """step2 run button
        
        pushButton_tab4actions_step2"""
        self._run_c01_join_drf()
        
        self._read_db(self._get_proj_db_fp(), self.logger)

    def _run_c01_join_drf(self, logger=None):
        """retrive and run project setup
        
        re-factored so we can call it from multiple push buttons
        """
        if logger is None: logger = self.logger
        log = logger.getChild('_run')
        
        proj_db_fp = self._get_proj_db_fp() 
        
        progress = self.progressBar_tab4actions_step2 #progress bar for this function
        
        progress.setValue(5)
        #=======================================================================
        # run
        #=======================================================================
        from .core import c01_join_drf as func
        progress.setValue(10)
        depth_rcv_df =  func(proj_db_fp, log=log)
        
        progress.setValue(70)
        #=======================================================================
        # plot
        #=======================================================================
        if self.checkBox_tab4actions_step2_plot.isChecked():
            plt.close('all')
            log.info(f'plotting depth_rcv_df')
            from .plots import plot_c01_depth_rcv 
            plot_c01_depth_rcv(depth_rcv_df, figure=plt.figure(2), log=log)
            log.info(f'launching matplotlib plot dialog')
            if self.show_plots: plt.show()
        
        #=======================================================================
        # wrap
        #=======================================================================
        progress.setValue(90)
        #self._read_db(proj_db_fp, log)
        
        progress.setValue(100)
        log.info(f'Step 2 complete w/ {depth_rcv_df.shape}')
        return depth_rcv_df
        
    
    
    
    
        
    def action_tab4actions_step3(self):
        """step3 run button
    
        pushButton_tab4actions_step3"""
        self._run_c02_group_story()
        
        self._read_db(self._get_proj_db_fp(), self.logger)

    def _run_c02_group_story(self, logger=None):
        """retrieve and run group story (Step 3)
    
        re-factored so we can call it from multiple push buttons
        """
        if logger is None: logger = self.logger
        log = logger.getChild('_run')
        
        proj_db_fp = self._get_proj_db_fp() 
        
        progress = self.progressBar_tab4actions_step3 #progress bar for this function
        
        progress.setValue(5)
    
        #=======================================================================
        # run
        #=======================================================================
        from .core import c02_group_story as func
        progress.setValue(10)
        ddf =  func(proj_db_fp, log=log)
        
        progress.setValue(70)
        #=======================================================================
        # plot
        #=======================================================================
        if self.checkBox_tab4actions_step3_plot.isChecked():
            plt.close('all')
            log.info(f'plotting ddf')
            
            #retrieve meta
            with sqlite3.connect(proj_db_fp) as conn:
                bldg_meta_d = pd.read_sql('SELECT * FROM c00_bldg_meta', conn).iloc[0, :].to_dict()
                
            settings_d = self._get_settings()
                
            """
            for k,v in bldg_meta_d.items():
                print(k,v)
            """
                
            from .plots import plot_c02_ddf
            
            #build y-label
            if 'costBasis' in bldg_meta_d: #fancy
                ylabel='%s (%s)'%(bldg_meta_d['costBasis'], bldg_meta_d['currency'])
                
                if settings_d['scale_m2']:
                    ylabel +=' per ' + bldg_meta_d['sizeOrAreaUnits']
            else:
                ylabel = 'damage'
                if settings_d['scale_m2']:
                    ylabel +=' per area'
                
 
             
            plot_c02_ddf(ddf, figure=plt.figure(3), log=log,ylabel=ylabel)
            log.info(f'launching matplotlib plot dialog')
            if self.show_plots: plt.show() 
        
        #=======================================================================
        # wrap
        #=======================================================================
        progress.setValue(90)
        #self._read_db(proj_db_fp, log)
        
        progress.setValue(100)
        log.info(f'Step 3 complete w/ {ddf.shape}')
        
        return ddf
    
    
    
    
    
    
    def action_tab4actions_step4(self):
        """step4 run button
    
        pushButton_tab4actions_step4"""
        _, ofp = self._run_c03_export()
        
        self._read_db(self._get_proj_db_fp(), self.logger)
        
        self.logger.push(f'Step 4 complete and exported DDF to {ofp}')
    
    def _run_c03_export(self, logger=None):
        """retrieve and run export
    
        re-factored so we can call it from multiple push buttons
        """
        if logger is None: logger = self.logger
        log = logger.getChild('_run')
        
        proj_db_fp = self._get_proj_db_fp() 
        
        progress = self.progressBar_tab4actions_step4 #progress bar for this function
        
        progress.setValue(5)
    
        #=======================================================================
        # run
        #=======================================================================
    
        from .core import c03_export as func
        progress.setValue(10)
        
        res_df, ofp =  func(proj_db_fp, log=log)
        
        #=======================================================================
        # wrap
        #=======================================================================
        progress.setValue(90)
        #self._read_db(proj_db_fp, log)
        
        progress.setValue(100)
        log.info(f'Step 4 complete w/ {res_df.shape}')
        
        return res_df, ofp
        
        
        
        
    def action_cancel_process(self):
        """handle user cancel request
        
        may need to implement QgsTask for this to work
        
        cancel_pushButton
        
        
        """
        # 1. Set a flag to signal cancellation 
        self.process_should_cancel = True     
 
    
        # 3. Optionally provide feedback to the user and 
        self.logger.warning('user requested \'Cancel\'')
        #    (e.g., disable the cancel button, show a progress bar)
        
    
    def _get_proj_db_fp(self):
        """retrieve the project filedatabse"""
        proj_db_fp = self.lineEdit_tab4actions_projdb.text()
        #=======================================================================
        # if not os.path.exists(proj_db_fp):
        #     raise IOError(f'must specify a valid project database filepath. got \n    {proj_db_fp}')
        #=======================================================================
        if proj_db_fp =='':
            proj_db_fp=None
            
        return proj_db_fp
        
    def _get_building_details(self,
                              logger=None):
        """retrieve dataa from Building Details tab"""
        if logger is None: logger = self.logger
        log = logger.getChild('_get_building_details')
        
        #=======================================================================
        # extract from layouts----------
        #=======================================================================

        # #general  building details
        bldg_meta_d = get_formLayout_data(self.formLayout_t02_01)
        
        #foundation
        bldg_meta_d.update(get_formLayout_data(self.formLayout_t02_02a))

        # #size age materials (grid layout)
        bldg_meta_d.update(get_gridLayout_data(self.gridLayout_t02_02))
        
        #=======================================================================
        # location costs
        #=======================================================================
        bldg_meta_d.update(get_formLayout_data(self.formLayout_t02_03))
        
        #=======================================================================
        # misc
        #=======================================================================
        bldg_meta_d.update(get_formLayout_data(self.formLayout_t02_04))
        
        #=======================================================================
        # format conversions----
        #=======================================================================
        for k,v in bldg_meta_d.copy().items():
            new_v=None
            if isinstance(v, str):
                if '\u00B2' in v:
                    new_v = v.replace('\u00B2', '2')
                elif v=='':
                    new_v = np.nan
                else:
                    new_v = convert_to_number(v) 
                    
                    
            if not new_v is None:
                bldg_meta_d[k] = new_v
                
        
                
        
        #=======================================================================
        # #check all of the keys are present
        #=======================================================================
        """
        bldg_meta_d['locationCityTownRegionLineEdit']
        for k,v in bldg_meta_d.items():
            print(f'{k}\n    {v} ({type(v)})')
        """
        df = bldg_meta_rqmt_df.loc[:, ['varName_ui', 'widgetName', 'type', 'case1']].dropna(
            subset='varName_ui').set_index('varName_ui')
            
        miss_s = set(df.index).symmetric_difference(bldg_meta_d.keys())
        assert miss_s==set(), f'bldg_meta mismatch from expectations'
        
        #typeset
        for k, type_str in df['type'].to_dict().items():
            try:
                bldg_meta_d[k] = eval(type_str)(bldg_meta_d[k])
            except Exception as e:
                raise TypeError(f'failed to set type %s on \'%s\'=\'%s\' w/ \n    {e}'%(
                    type_str, k, bldg_meta_d[k]))
                
        log.debug(f'forced types onto {len(bldg_meta_d)} vars')
        
        #=======================================================================
        # set core VarNames
        #=======================================================================
        """seems better to keep the varnames in as well"""
        bldg_meta_d['bldg_layout'] = bldg_meta_d['buildingLayout']
        
        if bldg_meta_d['basementHeightUnits']=='m':
            bldg_meta_d['basement_height_m'] = bldg_meta_d['basementHeight']
        else:
            raise NotImplementedError(bldg_meta_d['basementHeightUnits'])
        
        if bldg_meta_d['sizeOrAreaUnits']=='m2':
            bldg_meta_d['scale_value_m2'] = bldg_meta_d['sizeOrAreaValue']
        else:
            raise NotImplementedError(bldg_meta_d['sizeOrAreaUnits'])
            
        #=======================================================================
        # check expectations
        #=======================================================================
        req_d = bldg_meta_rqmt_df.loc[:, ['varName_core', 'type']].dropna().set_index('varName_core').iloc[:, 0].to_dict()
        req_d = {k:eval(v) for k,v in req_d.items()}
        
        for k,type_class in req_d.items():
            assert isinstance(bldg_meta_d[k], type_class), f'bad type on {k}'
            
        
        log.debug(f'collected {len(bldg_meta_d)} entries from \'Building Details\' tab')
        
        
        return bldg_meta_d
        
    def _get_fixed_costs(self, logger=None):
        """retireve fixed costs from 'Data Input' tab"""
 
        d = {k:v.value() for k,v in self.fixed_costs_widget_d.items()}
        
        #check it
        for k,v in d.items():
            assert isinstance(k, int)
            if not isinstance(v, float):
                raise TypeError(f'got unexpected type on fixed Data Input > Fixed Costs (storey {k})')
            
        return d
 
            
 
        
    def _get_settings(self, logger=None):
        """retrieve project settings from Data Input  tab"""
        return {
            'curve_name':self.lineEdit_tab3dataInput_curveName.text(),
            'scale_m2':self.radioButton_tab3dataInput_rcvm2.isChecked(), #retrieve from radio buttons
            }



FORM_CLASS2, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dbMismatch_dialog.ui'), resource_suffix='')           
class dbMismatchDialog(QtWidgets.QDialog, FORM_CLASS2, DialogQtBasic):
    def __init__(self, message='Warning'):  # Accept message
            super().__init__()
            self.setupUi(self)
            self.textBrowser.append(message)  # Set the label if a message is given
            self.connect_slots()
            
    def connect_slots(self):
        
        self.pushButton.clicked.connect(self.close)
        
        
        
        
 
        

        
