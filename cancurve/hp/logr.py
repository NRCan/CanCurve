'''
Created on Mar. 26, 2020

@author: cefect

usually best to call this before any standard imports
    some modules have auto loggers to the root loger
    calling 'logging.getLogger()' after these configure will erase these
'''
import os, logging, logging.config, pprint, sys
from cancurve import config
from cancurve.parameters import log_format_str





def get_log_stream(name=None, level=None):
    """get a logger with stream handler"""
    if name is None:
        name = str(os.getpid())
    if level is None:
        level = config.log_level
        #=======================================================================
        # if __debug__:
        #     level = logging.DEBUG
        # else:
        #=======================================================================
            

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # see if it has been configured
    if not logger.handlers:
        
        handler = logging.StreamHandler(
            stream=sys.stdout,  # send to stdout (supports colors)
        )  # Create a file handler at the passed filename
        formatter = logging.Formatter(log_format_str, datefmt="%H:%M:%S", validate=True)
        handler.setFormatter(formatter)
        handler.setLevel(level)
        
        logger.addHandler(handler)
    return logger
    
    
    
    
    
    
    