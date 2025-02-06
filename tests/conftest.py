'''
Created on Apr. 16, 2024

@author: cef
'''
import os, logging, sys
import pytest
from unittest.mock import patch



from cancurve.parameters import src_dir

#===============================================================================
# data
#===============================================================================
from definitions import test_data_dir as test_data_dir_master
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
#test_data_dir_master = os.path.join(src_dir, 'tests', 'data')


#===============================================================================
# fixtrues--------
#===============================================================================



@pytest.fixture(scope='function')
def logger():
    logging.basicConfig(
                #filename='xCurve.log', #basicConfig can only do file or stream
                force=True, #overwrite root handlers
                stream=sys.stdout, #send to stdout (supports colors)
                level=logging.INFO, #lowest level to display
                format='%(asctime)s %(levelname)s %(name)s: %(message)s',  # Include timestamp
                datefmt='%H:%M:%S'  # Format for timestamp
                )
    
    #get a new logger and lower it to avoid messing with dependencies
    log = logging.getLogger(str(os.getpid()))
    log.setLevel(logging.DEBUG)
    
    
    return log


 