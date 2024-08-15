


'''
Created on May 20, 2024

@author: cef

compile and analyze DDFP example curves against CanCurve
'''
import  os, logging, pprint, pickle
from datetime import datetime
import pandas as pd
import numpy as np

#import tqdm #not part of Q 

from misc.port_estimate import ddfp_inputs_to_ci
from cancurve.hp.logr import get_new_file_logger, get_log_stream
from cancurve.hp.basic import view_web_df as view
#===============================================================================
# DDFP data
#===============================================================================
ddfp_data_dir = r'l:\02_WORK\CEF\2403_CanCurve\01_MGMT\01_INOUT\2024 03 25 - David - NRCan_DDF_Transfer\OneDrive_2_3-25-2024\DDF_data'
ddfp_lib_fp_d = {
    'AB.Calgary':r'Alberta\Calgary\CanFlood_R_ABCA_09-2023.xls',
    'NB.Fredericton':r'NewBrunswick\Fredericton\CanFlood_R_NBFR_09-2023.xlsx'
    }
ddfp_lib_fp_d = {k:os.path.join(ddfp_data_dir, v) for k,v in ddfp_lib_fp_d.items()}


def d_to_pick(d, filename):
    with open(filename, 'wb') as file:
        pickle.dump(d, file)
        
    print(f'wrote to file\n    {filename}')
    
def pick_to_d(filename):
    
    with open(filename, 'rb') as file:
        dictionary = pickle.load(file)
        
    print(f'loaded {len(dictionary)} from \n    {filename}')
    return dictionary



#===============================================================================
# def _01_build_ddfp_from_dir(ddfp_lib_fp_d,
#                             log_level=logging.INFO):
#     """convert DDFP to CanCurve format for all curves in a directory"""
#     #===========================================================================
#     # defaults
#     #===========================================================================
#     out_dir = r'l:\10_IO\CanCurve\misc\DDFP_compare'
#     log = get_log_stream(level=log_level)
#     
# 
#         
#     
#     #===============================================================================
#     # loop on case study region
#     #===============================================================================
#     cnt = 0
#     res_lib, warn_lib = dict(), dict()
#     for study_name, ddfp_lib_fp in ddfp_lib_fp_d.items():
#         log.info(f'\n\n{study_name}\n\n==================')
#         res_lib[study_name] = dict()
#         warn_lib[study_name] = dict()
#         #=======================================================================
#         # defaults
#         #=======================================================================
#         #===========================================================================
#         # load DDFP data
#         #===========================================================================
#         ddfp_lib_d = pd.read_excel(ddfp_lib_fp, sheet_name=None)
#         log.info(f'loaded {len(ddfp_lib_d)} tabs from \n    {ddfp_lib_fp}')
#         #log.debug(pprint.pformat(list(ddfp_lib_d.keys())))
#         #===========================================================================
#         # loop on index
#         #===========================================================================
#         ddfp_cnt = len(ddfp_lib_d['index']) - 1
#         log.info(f'computing for {ddfp_cnt}')
#         for i, row in ddfp_lib_d['index'].iterrows():
#             ddf_name = row['ddf_name']
#             odi = os.path.join(out_dir, study_name)
#             if not os.path.exists(odi):
#                 os.makedirs(odi)
#             #get data dir
#             curve_data_dir = os.path.join(os.path.dirname(ddfp_lib_fp), row['ddf_name'])
#             log.info(f'\non ({i}/{ddfp_cnt}) %s' % row['ddf_name'])
#             #load
#             try:
#                 res_lib[study_name][ddf_name], warn_lib[study_name][ddf_name] = ddfp_inputs_to_ci_from_dir(
#                     curve_data_dir, 
#                     out_dir=os.path.join(odi, ddf_name), 
#                     logger=get_new_file_logger(
#                         logger=log.getChild(ddf_name), 
#                         fp=os.path.join(odi, f'{ddf_name}_compare.log')))
#             except Exception as e:
#                 raise IOError(f'failed on {ddf_name} w/\n    {e}')
#             
#             cnt+=1
#             
#             if cnt>3:
#                 break
#         
#         log.info(f'done w/ {study_name}')
#         
#     #===========================================================================
#     # write
#     #===========================================================================
#     log.info(f'finished w/ {cnt}')
#     
#     d_to_pick(res_lib, os.path.join(out_dir, f'DDFP_to_cc_lib.pkl'))
#     
#     
#     print('finished')
#===============================================================================
    
def _01_build_ddfp_from_dir_noindex(ddfp_lib_fp_d,
                            log_level=logging.INFO):
    """convert DDFP to CanCurve format cost-item dataset for all curves in a directory"""
    #===========================================================================
    # defaults
    #===========================================================================
    out_dir = r'l:\10_IO\CanCurve\misc\DDFP_compare'
    log = get_log_stream(level=log_level)
    

        
    
    #===============================================================================
    # loop on case study region
    #===============================================================================
    cnt = 0
    res_lib, warn_lib = dict(), dict()
    for study_name, ddfp_lib_fp in ddfp_lib_fp_d.items():
        log.info(f'\n\n{study_name}\n\n==================')
        res_lib[study_name] = dict()
        warn_lib[study_name] = dict()
        #=======================================================================
        # defaults
        #=======================================================================
        
        odi = os.path.join(out_dir, study_name)
        if not os.path.exists(odi):
            os.makedirs(odi)
                
        #===========================================================================
        # load DDFP data
        #===========================================================================
        ddfp_lib_d = pd.read_excel(ddfp_lib_fp, sheet_name=None, index_col=0, header=None )
        log.info(f'loaded {len(ddfp_lib_d)} tabs from \n    {ddfp_lib_fp}')
        #log.debug(pprint.pformat(list(ddfp_lib_d.keys())))
        
        
        #=======================================================================
        # collect names
        #=======================================================================
        #without the index, we need to build the unique list from teh tab names
        l = [e for e in ddfp_lib_d.keys() if not 'index' in e] #extract keys
        l = ['_'.join(e.split('_')[:-1]) for e in l] #drop suffix
        ddf_name_l = list(set(l)) #get unique set
        
        #===========================================================================
        # loop on index
        #===========================================================================
        ddfp_cnt = len(ddf_name_l)
        log.info(f'computing for {ddfp_cnt}')
        #for i, (tab_name, tab_df_raw) in enumerate(ddfp_lib_d.items()):
        for i, ddf_name in enumerate(ddf_name_l):
 
                
            #get data dir
            curve_data_dir = os.path.join(os.path.dirname(ddfp_lib_fp), ddf_name)
            assert os.path.exists(curve_data_dir)
            log.info(f'\non ({i}/{ddfp_cnt}) %s' % ddf_name)
            
            
            #load
            try:
                res_lib[study_name][ddf_name], warn_lib[study_name][ddf_name] = ddfp_inputs_to_ci_from_dir(
                    curve_data_dir, 
                    out_dir=os.path.join(odi, ddf_name), 
                    logger=get_new_file_logger(
                        logger=log.getChild(ddf_name), 
                        fp=os.path.join(odi, f'{ddf_name}_compare.log')),
                    write=False,
                    )
            except Exception as e:
                raise IOError(f'failed on {ddf_name} w/\n    {e}')
            
            cnt+=1
            
            #if cnt>3:break
        
        log.info(f'done w/ {study_name}')
        
    #===========================================================================
    # write
    #===========================================================================
    log.info(f'finished w/ {cnt}')
    
    d_to_pick(res_lib, os.path.join(out_dir, f'DDFP_to_cc_lib.pkl'))
    
    #write warnings
    dx = pd.concat({k:pd.DataFrame.from_dict(v) for k,v in warn_lib.items()}, names=['study_name', 'warning']).T.stack(level=0).swaplevel()
 
    ofp = os.path.join(out_dir, f'DDFP_to_cc_warnings.csv')
    dx.to_csv(ofp)
    
    log.info(f'wrote warnings {dx.shape} to \n    {ofp}')
    
    return res_lib
    
 
    
def ddfp_inputs_to_ci_from_dir(
        curve_data_dir, logger=None, **kwargs):
    """wrapper to call def ddfp_inputs_to_ci from a directory"""
    
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
    log.debug(f'for \'{ddfp_name}\' retrieved both files')
    
    return ddfp_inputs_to_ci(estimate_xls_fp, ddfp_workbook_fp, logger=logger,**kwargs)
    
    
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
    
    #build pickle of compiled DDFPs
    #ddfp_lib = _01_build_ddfp_from_dir_noindex(ddfp_lib_fp_d)
    
    
    ddfp_lib = pick_to_d(r'l:\10_IO\CanCurve\misc\DDFP_compare\DDFP_to_cc_lib.pkl')
    
    
    
    for study_name, d0 in ddfp_lib.items():
        for ddf_name, df in d0.items():
            """
            view(df)
            """
            print(ci_df)
    
    
    
    
    
    
    
    print('finished')
    
    
    
    
    
    
    
    
    
    
    
