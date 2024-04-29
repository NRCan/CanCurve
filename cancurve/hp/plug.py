'''
Created on Apr. 29, 2024

@author: cef

QGIS plugin helpers
'''

#===============================================================================
# imports-----
#===============================================================================
import os, datetime, sys

from qgis.core import Qgis, QgsLogger, QgsMessageLog

#===============================================================================
# classes------
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
                           log_nm=log_nm,
                           debug_logger=self.debug_logger)
        

        
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
    
        
      