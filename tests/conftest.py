'''
Created on Apr. 16, 2024

@author: cef
'''
import pytest, os, shutil


from cancurve.hp.basic import find_single_file_by_extension
from cancurve.parameters import src_dir

#===============================================================================
# data
#===============================================================================
test_data_dir_master = os.path.join(src_dir, 'tests', 'data')


#===============================================================================
# fixtrues--------
#===============================================================================
@pytest.fixture(scope='function')   
def proj_db_fp(testCase, testPhase, tmp_path):
    """retrieve the approraite project database file for hte test case (and make a copy)"""
    
    #get the target directory
    tdata_dir = os.path.join(test_data_dir_master, testCase, testPhase)
    assert os.path.exists(tdata_dir)
    
    #get the project db file
    fp = find_single_file_by_extension(tdata_dir, '.cancurve')
    
    #make a working copy        
    return shutil.copy(fp,os.path.join(tmp_path, 'copy_'+os.path.basename(fp)))