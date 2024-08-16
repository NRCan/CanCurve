'''
Created on May 20, 2024

@author: cef

compile and analyze DDFP example curves against CanCurve
'''

#===============================================================================
# INPUTS---------
#===============================================================================
import  os, logging, pprint, pickle
from datetime import datetime
import pandas as pd
import numpy as np

#import tqdm #not part of Q 

from misc.port_estimate import ddfp_inputs_to_ci, ddfp_inputs_to_fixedCosts
from cancurve.hp.logr import get_new_file_logger, get_log_stream
from cancurve.hp.basic import view_web_df as view
from cancurve.bldgs.assertions import assert_CanFlood_ddf

from misc.bldgs_script_example import bldgs_workflow
#===============================================================================
# DDFP data
#===============================================================================
ddfp_data_dir = r'l:\02_WORK\CEF\2403_CanCurve\01_MGMT\01_INOUT\2024 03 25 - David - NRCan_DDF_Transfer\OneDrive_2_3-25-2024\DDF_data'
ddfp_lib_fp_d = {
    'AB.Calgary':r'Alberta\Calgary\CanFlood_R_ABCA_09-2023.xls',
    'NB.Fredericton':r'NewBrunswick\Fredericton\CanFlood_R_NBFR_09-2023.xlsx'
    }
ddfp_lib_fp_d = {k:os.path.join(ddfp_data_dir, v) for k,v in ddfp_lib_fp_d.items()}


def _d_to_pick(d, filename):
    with open(filename, 'wb') as file:
        pickle.dump(d, file)
        
    print(f'wrote to file\n    {filename}')
    
    return filename
    
def _pick_to_d(filename):
    
    with open(filename, 'rb') as file:
        dictionary = pickle.load(file)
        
    print(f'loaded {len(dictionary)} from \n    {filename}')
    return dictionary


def _get_series_value_from_keys(s, labels):
    for label in labels:
        if label in s.index:
            v = s[label]
            
            if v=='na':
                v = np.nan
            
            return v
    raise KeyError(f'no match in \n    {labels}')



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
#     _d_to_pick(res_lib, os.path.join(out_dir, f'DDFP_to_cc_lib.pkl'))
#     
#     
#     print('finished')
#===============================================================================
    
def p01_build_ddfp_from_dir_noindex(ddfp_lib_fp_d,
                            log_level=logging.INFO,
                            out_dir = r'l:\10_IO\CanCurve\misc\DDFP_compare',
                            ):
    """convert DDFP to CanCurve format cost-item dataset for all curves in a directory"""
    #===========================================================================
    # defaults
    #===========================================================================
    
    log = get_log_stream(level=log_level)
    

        
    
    #===============================================================================
    # loop on case study region
    #===============================================================================
    cnt = 0
    res_lib, warn_lib, meta_lib, fixd_lib, crve_lib = dict(), dict(), dict(), dict(), dict()
    for study_name, ddfp_lib_fp in ddfp_lib_fp_d.items():
        log.info(f'\n\n{study_name}\n\n==================')
        res_lib[study_name] = dict()
        warn_lib[study_name] = dict()
        meta_lib[study_name] = dict()
        fixd_lib[study_name] = dict()
        crve_lib[study_name] = dict()
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
            
            
            #===================================================================
            # #build cost-information---------
            #===================================================================
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
            
            
            #===================================================================
            # fixed costs-------
            #===================================================================
            ddfp_workbook_fp = get_filename_by_prefix(curve_data_dir, 'DDFwork')
            fixd_lib[study_name][ddf_name] = ddfp_inputs_to_fixedCosts(ddfp_workbook_fp)
            
            #===================================================================
            # compiled curve------
            #===================================================================
            #need this for comparison later
            ddf = ddfp_lib_d[ddf_name+'_m2'].reset_index()
            
            #add depthLoc_key
            id_loc = ddf.index[ddf[0].str.lower().str.contains('function scale').fillna(False)].item()            
            ddf.loc[id_loc+1, 0] = 'exposure'
            
            #check
            assert_CanFlood_ddf(ddf)
            
            #store
            crve_lib[study_name][ddf_name] = ddf
            
            
            #===================================================================
            # extract metadata------
            #===================================================================
            #{'bldg_layout': 'default', 'basement_height_m': '1.8', 'scale_value_m2': '232.1'}
            #load resulting curve
            curve_ser = ddfp_lib_d[ddf_name+'_m2'].iloc[:,0]
            
            get_v = lambda x:float(_get_series_value_from_keys(curve_ser, x))
            
            try:
                meta_lib[study_name][ddf_name] = {
                    'bldg_layout':'default', 
                    'basement_height_m':get_v(['base to main height']),
                    'scale_value_m2':get_v(['estimate GFA (m2)']),
                    'curve_name':ddf_name,                
                    }
            except Exception as e:
                raise KeyError(f'failed on {ddf_name} w/\n    {e}')
            
            
            cnt+=1
            
 
        
        log.info(f'done w/ {study_name}')
        
    #===========================================================================
    # write
    #===========================================================================
    log.info(f'finished w/ {cnt}')
    
    _d_to_pick({'ci':res_lib, 'fixed':fixd_lib, 'meta':meta_lib, 'crve':crve_lib}, os.path.join(out_dir, f'DDFP_to_cc_lib.pkl'))
    
    #write warnings
    dx = pd.concat({k:pd.DataFrame.from_dict(v) for k,v in warn_lib.items()}, names=['study_name', 'warning']).T.stack(level=0).swaplevel()
 
    ofp = os.path.join(out_dir, f'DDFP_to_cc_warnings.csv')
    dx.to_csv(ofp)
    
    log.info(f'wrote warnings {dx.shape} to \n    {ofp}')
    
    return res_lib, meta_lib
    
 
    
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



def p02_build_CanCurve_batch(ci_df_lib, meta_lib, fixd_lib,
                             
                             out_dir=None,log_level=logging.INFO,
                             ):
    """build a batch of CanCurve ddfs from extracted data"""
    #===========================================================================
    # defaults
    #===========================================================================
    log = get_log_stream(level=log_level)
    
    #===========================================================================
    # loop and build each
    #===========================================================================
    res_lib=dict()
    cnt=0
    
    for study_name, d0 in ci_df_lib.items():
        res_lib[study_name] = dict()
        log.info(f'\n\n==========================\n{study_name}\n=====================\n\n')
        
        for ddf_name, ci_df in d0.items():
            log.info(f'\n\n{ddf_name}\n--------------------------')
            
            #===================================================================
            # #pre-process
            #===================================================================
            #building meta
            bldg_meta_d=meta_lib[study_name][ddf_name].copy()
            
            if pd.isnull(bldg_meta_d['basement_height_m']):
                bldg_meta_d['basement_height_m'] = 2.7
                
                
            #cost items
            bx = ci_df['story']>0
            if bx.any():
                
                log.warning(f'dropping {bx.sum()}/{len(bx)} multi-story')
                ci_df = ci_df.loc[~bx, :]
 
            
            
            #===================================================================
            # run workflow
            #===================================================================
            try:
                res_lib[study_name][ddf_name] = bldgs_workflow(ci_df, 
                    curve_name=ddf_name, 
                    bldg_meta_d=bldg_meta_d, 
                    fixed_costs_d=fixd_lib[study_name][ddf_name],
                    logger=log, 
                    out_dir = os.path.join(out_dir, study_name, ddf_name))
                
            except Exception as e:
                raise IOError(f'failed on \'{ddf_name}\'\n    {e}')
            
            cnt+=1
            
    #===========================================================================
    # wrap
    #===========================================================================
    log.info(f'finuished on {cnt}')
    
    ofp = _d_to_pick(res_lib, os.path.join(out_dir, 'DDFP_CanCurve_batch.pkl'))
    
    return res_lib

def p03_compare(DDFP_lib, CanCurve_lib,
                             
                             out_dir=None,log_level=logging.INFO,
                             ):
    """compare the curves compiled from teh two platforms"""
    
    #===========================================================================
    # defaults
    #===========================================================================
    log = get_log_stream(level=log_level)
    
    #===========================================================================
    # precheck
    #===========================================================================
    assert set(DDFP_lib.keys()).symmetric_difference(CanCurve_lib.keys())==set()
    
    #zip together
    ddf_zip = [(key, DDFP_lib[key], CanCurve_lib[key]) for key in DDFP_lib.keys()]
    #===========================================================================
    # loop on study area
    #==========================================================================
    for study_name, DDFP_d, CC_d in ddf_zip:
    
        log.info(f'on {len(DDFP_d)} curves')
        
        assert set(DDFP_d.keys()).symmetric_difference(CC_d.keys())==set()
        
        #=======================================================================
        # loop on each curver
        #=======================================================================
         
    
    
 
    
if __name__=='__main__':
    
    out_dir = r'l:\10_IO\CanCurve\misc\DDFP_compare'
    
    
    #===========================================================================
    # #build pickle of compiled DDFPs
    #===========================================================================
    #ddfp_lib = p01_build_ddfp_from_dir_noindex(ddfp_lib_fp_d, out_dir=out_dir)
    
    
    ddfp_lib = _pick_to_d(r'l:\10_IO\CanCurve\misc\DDFP_compare\DDFP_to_cc_lib.pkl')
      
    ci_df_lib = ddfp_lib.pop('ci')
    meta_lib = ddfp_lib.pop('meta')
    fixd_lib = ddfp_lib.pop('fixed')
       
       
     
    #===========================================================================
    # build curves using CanCurve   
    #===========================================================================
    #CanCurve_ddfs_lib = p02_build_CanCurve_batch(ci_df_lib, meta_lib, fixd_lib, out_dir=out_dir)
    
    CanCurve_ddfs_lib = _pick_to_d(r'l:\10_IO\CanCurve\misc\DDFP_compare\DDFP_CanCurve_batch.pkl')
    
    
    #===========================================================================
    # compare
    #===========================================================================
    p03_compare(ddfp_lib.pop('crve'), CanCurve_ddfs_lib)
    
    
    
    
    
    
    
    print('finished')
    
    
    
    
    
    
    
    
    
    
    
