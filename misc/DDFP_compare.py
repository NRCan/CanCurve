'''
Created on May 20, 2024

@author: cef

compile and analyze DDFP example curves against CanCurve
'''
import  os, logging
from datetime import datetime
import pandas as pd
import numpy as np

from misc.port_estimate import ddfp_inputs_to_ci
from cancurve.hp.logr import get_new_file_logger, get_log_stream
#===============================================================================
# DDFP data
#===============================================================================
ddfp_data_dir = r'l:\02_WORK\CEF\2403_CanCurve\01_MGMT\01_INOUT\2024 03 25 - David - NRCan_DDF_Transfer\OneDrive_2_3-25-2024\DDF_data'
ddfp_lib_fp_d = {
    'AB.Calgary':r'Alberta\Calgary\CanFlood_R_ABCA_09-2023.xls',
    'NB.Fredericton':r'NewBrunswick\Fredericton\CanFlood_R_NBFR_09-2023.xlsx'
    }
ddfp_lib_fp_d = {k:os.path.join(ddfp_data_dir, v) for k,v in ddfp_lib_fp_d.items()}



        

def ddfp_inputs_to_ci_from_dir(
        curve_data_dir, logger=None, **kwargs):
    """wrapper to load from directory"""
    
    log = logger
    
    assert os.path.exists(curve_data_dir)
    
    ddfp_name = os.path.basename(curve_data_dir)
    
    #search for estimate fp
    estimate_xls_fp = os.path.join(curve_data_dir,ddfp_name+'.xlsx')
    assert os.path.exists(estimate_xls_fp), estimate_xls_fp
    
    #DDFP workbok
    ddfp_workbook_fp = get_filename_by_prefix(curve_data_dir, 'DDFwork')
    assert os.path.exists(ddfp_workbook_fp)
    #===========================================================================
    # convert
    #===========================================================================
    log.info(f'for \'{ddfp_name}\' retrieved both files')
    
    return ddfp_inputs_to_ci(estimate_xls_fp, ddfp_workbook_fp, logger=logger,
                             **kwargs)
    
    
def get_filename_by_prefix(folder_path, prefix):
    """Retrieves the name of a single file within a folder that begins with 'DDFPwork_'.

    Args:
        folder_path (str): The path to the folder to search.

    Returns:
        str: The name of the matching file.

    Raises:
        FileNotFoundError: If no matching file is found.
        ValueError: If more than one matching file is found.
    """
    matching_files = [
        filename
        for filename in os.listdir(folder_path)
        if filename.startswith(prefix)
    ]

    if not matching_files:
        raise FileNotFoundError(f"No file starting with '{prefix}' found in {folder_path}")

    if len(matching_files) > 1:
        raise ValueError(f"Multiple files starting with '{prefix}' found in {folder_path}")

    return os.path.join(folder_path, matching_files[0])
    
    
if __name__=='__main__':
    #===========================================================================
    # defaults
    #===========================================================================
    out_dir = r'l:\10_IO\CanCurve\misc\DDFP_compare'
    
    log = get_log_stream(level=logging.INFO)
    
    #===============================================================================
    # loop on case study region
    #===============================================================================
    res_lib = dict()
    for study_name, ddfp_lib_fp in ddfp_lib_fp_d.items():
        log.info(f'\n\n{study_name}\n\n==================')
        res_lib[study_name]=dict()
        #=======================================================================
        # defaults
        #=======================================================================

        #===========================================================================
        # load DDFP data
        #===========================================================================
        ddfp_lib_d = pd.read_excel(ddfp_lib_fp, sheet_name=None)
        log.info(f'loaded {len(ddfp_lib_d)} tabs')
        
        #===========================================================================
        # loop on index
        #===========================================================================
        ddfp_cnt = len(ddfp_lib_d['index'])
        for i, row in ddfp_lib_d['index'].iterrows():
            
            ddf_name=row['ddf_name']
            
            odi = os.path.join(out_dir, study_name)
            if not os.path.exists(odi):os.makedirs(odi)
            
            #get data dir
            curve_data_dir = os.path.join(os.path.dirname(ddfp_lib_fp), row['ddf_name'])
            
            log.info(f'\non ({i}/{ddfp_cnt-1}) %s from \n    {curve_data_dir}'%row['ddf_name'])
            
            try:
                res_lib[study_name][ddf_name] = ddfp_inputs_to_ci_from_dir(
                    curve_data_dir,
                    out_dir=os.path.join(odi, ddf_name),
                    logger=get_new_file_logger(
                        logger=log.getChild(ddf_name),
                        fp=os.path.join(odi, f'{ddf_name}_compare.log')
                                               ))
            except Exception as e:
                raise IOError(f'failed on {ddf_name} w/\n    {e}')
            
        log.info(f'done w/ {study_name}')
        
    print('finished')
