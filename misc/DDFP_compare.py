'''
Created on May 20, 2024

@author: cef

compile and analyze DDFP example curves against CanCurve
'''

#===============================================================================
# IMPORTS---------
#===============================================================================
import  os, logging, pprint, pickle
from datetime import datetime
import pandas as pd
import numpy as np
pd.set_option("display.max_rows", 10)

import scipy.integrate
from scipy.interpolate import interp1d
 

#===============================================================================
# setup matplotlib
#===============================================================================
import matplotlib
#matplotlib.use('Qt5Agg') #sets the backend (case sensitive)
matplotlib.set_loglevel("info") #reduce logging level
import matplotlib.pyplot as plt

from cancurve.parameters_matplotlib import font_size, cmap_default #set custom styles

#===============================================================================
# imports
#===============================================================================
 
 
import matplotlib.gridspec as gridspec

#import tqdm #not part of Q 

from misc.port_estimate import ddfp_inputs_to_ci, ddfp_inputs_to_fixedCosts, load_main_floor_area
from cancurve.hp.logr import get_new_file_logger, get_log_stream
from cancurve.hp.basic import view_web_df as view
from cancurve.bldgs.assertions import assert_CanFlood_ddf
from cancurve.bldgs.core import DFunc

from misc.bldgs_script_example import bldgs_workflow


#===============================================================================
# parameters-----
#===============================================================================
metric_label_d = {
    'abc':'area between curves (m*CAD)',
    'auc':'area under curves (m*CAD)',
 
    }

framework_label_d = {
    'CC':'CanCurve', 'DDFP':'DDFP'
    }
#===============================================================================
# DDFP data
#===============================================================================
ddfp_data_dir = r'l:\02_WORK\CEF\2403_CanCurve\01_MGMT\01_INOUT\2024 03 25 - David - NRCan_DDF_Transfer\OneDrive_2_3-25-2024\DDF_data'
ddfp_lib_fp_d = {
    'AB.Calgary':r'Alberta\Calgary\CanFlood_R_ABCA_09-2023.xls',
    'NB.Fredericton':r'NewBrunswick\Fredericton\CanFlood_R_NBFR_09-2023.xlsx'
    }
ddfp_lib_fp_d = {k:os.path.join(ddfp_data_dir, v) for k,v in ddfp_lib_fp_d.items()}


#===============================================================================
# helpers------
#===============================================================================
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
    
def p01_extract_DDFP(ddfp_lib_fp_d,
                            log_level=logging.INFO,
                            out_dir = r'l:\10_IO\CanCurve\misc\DDFP_compare',
                            write=True, 
                            ddf_name_l_subset=None,
                            ):
    """convert DDFP to CanCurve format cost-item dataset for all curves in a directory
    
    extract data into CanCurve format (CostItem csv, fixed costs, metadata)
    
    """
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
        #if not ddf_name_l is None:
        #without the index, we need to build the unique list from teh tab names
        l = [e for e in ddfp_lib_d.keys() if not 'index' in e] #extract keys
        l = ['_'.join(e.split('_')[:-1]) for e in l] #drop suffix
        ddf_name_l = list(set(l)) #get unique set
        
        if not ddf_name_l_subset is None:
            ddf_name_l = [e for e in ddf_name_l if e in ddf_name_l_subset]
            
        
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
                    write=write,
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
                    #'scale_value_m2':get_v(['estimate GFA (m2)']),
                    #scale values on ddf tabs are wrong. need to pull thsi from DDFwrk_grp2
                    'curve_name':ddf_name,
                    'storeys':curve_ser['storeys']                
                    }
            except Exception as e:
                raise KeyError(f'failed on {ddf_name} w/\n    {e}')
            
        
            #scale area
            scale_value_m2  = load_main_floor_area(ddfp_workbook_fp)
            meta_lib[study_name][ddf_name]['scale_value_m2'] = scale_value_m2
            
            
            cnt+=1
            
 
        
        log.info(f'done w/ {study_name}')
        
    #===========================================================================
    # write
    #===========================================================================
    log.info(f'finished w/ {cnt}')
    
    collected_res_lib = {'ci':res_lib, 'fixed':fixd_lib, 'meta':meta_lib, 'crve':crve_lib}
    
    _d_to_pick(collected_res_lib, os.path.join(out_dir, f'DDFP_to_cc_lib.pkl'))
    
    #write warnings
    dx = pd.concat({k:pd.DataFrame.from_dict(v) for k,v in warn_lib.items()}, names=['study_name', 'warning']).T.stack(level=0).swaplevel()
 
    ofp = os.path.join(out_dir, f'DDFP_to_cc_warnings.csv')
    dx.to_csv(ofp)
    
    log.info(f'wrote warnings {dx.shape} to \n    {ofp}')
    
    return collected_res_lib
    
 
    
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



def p02_CanCurve_workflow(ci_df_lib, meta_lib, fixd_lib,
                          out_dir=None,log_level=logging.INFO,
                          plot=True,
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
                res_lib[study_name][ddf_name], _ = bldgs_workflow(ci_df, 
                    curve_name=ddf_name, 
                    bldg_meta_d=bldg_meta_d, 
                    fixed_costs_d=fixd_lib[study_name][ddf_name],
                    logger=log, plot=plot,
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

def p03_compare(DDFP_lib, CanCurve_lib, meta_lib,
                out_dir=None,log_level=logging.INFO,
                ddf_name_l=None,
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
    ddf_zip = [(key, DDFP_lib[key], CanCurve_lib[key], meta_lib[key]) for key in DDFP_lib.keys()]
    
    
    #===========================================================================
    # loop on study area
    #==========================================================================
    res_d = dict()
    #metric_lib = {k:dict() for k in DDFP_lib.keys().keys()}
    for study_name, DDFP_d, CC_d, meta_d0 in ddf_zip:
    
        log.info(f'on {len(DDFP_d)} curves')
        
        #pprint.pprint(list(DDFP_d.keys()))
        
        assert set(DDFP_d.keys()).symmetric_difference(CC_d.keys())==set()
        
 
        metric_lib = dict()
        
        #=======================================================================
        # plot and calc each curve
        #=======================================================================
        for ddf_name, DDFP_df in DDFP_d.items():
            
            #selection
            if not ddf_name_l is None:
                if not ddf_name in ddf_name_l:continue
            
            
            log.info(ddf_name)
            CC_df = CC_d[ddf_name]
            meta_d = meta_d0[ddf_name]
            
            """
            write test data
            
            od = os.path.join(r'l:\09_REPOS\04_TOOLS\CanCurve\tests\data\misc', study_name, ddf_name)
            os.makedirs(od, exist_ok='OK')
            
            DDFP_df.to_pickle(os.path.join(od, 'DDFP.pkl'))
            
            CC_df.to_pickle(os.path.join(od, 'CC.pkl'))
            """
            
            
            metric_lib[ddf_name] = plot_and_eval_ddfs({'DDFP':DDFP_df, 'CC':CC_df},
                               out_dir = os.path.join(out_dir, study_name),
                               title=f'{study_name} {ddf_name}',
                               meta_d=meta_d,
                               )
            
            
        #=======================================================================
        # summary
        #=======================================================================
        res_d[study_name] = pd.concat(metric_lib, names=['ddf_name'])
        
    #===========================================================================
    # write
    #===========================================================================
    _d_to_pick(res_d, os.path.join(out_dir, 'metric_dx.pkl'))
    
    return res_d
            
 
            
 
            
            

def _calc_metric_df(serx):
    metric_d = dict()
    #basic impact
    metric_d['impact_max'] = serx.groupby(level=0).max().rename(None)
    metric_d['impact_min'] = serx.groupby(level=0).min().rename(None)
    #basic exposure
    expo_df = serx.index.to_frame().reset_index(drop=True)
    metric_d['exposure_max'] = expo_df.groupby('framework_name').max().iloc[:, 0].rename(None)
    metric_d['exposure_min'] = expo_df.groupby('framework_name').min().iloc[:, 0].rename(None)
    """
    
    view(dx)
    
    """
    #area
    #for each level=0 group, compute the area under the exposure-impact curve (to x=0)
    metric_d['auc'] = serx.groupby(level=0).apply(_area_under_curve).rename(None)
    metric_dx = pd.concat(metric_d, names=['metric']).unstack()
    metric_dx.loc['abc', :] = _area_between_curves(serx) #single value
    
    return metric_dx

def plot_and_eval_ddfs(ddf_d,
                   log=None, out_dir=None,
                   title=None,
                   meta_d=dict(),
                   ):
    """plot and evaluate a list of similar ddfs"""
    
    #===========================================================================
    # defaults
    #===========================================================================
    if log is None: log = get_log_stream(level=logging.DEBUG)
    os.makedirs(out_dir, exist_ok=True)
    #===========================================================================
    # init DFuncs
    #===========================================================================
    DFunc_d=dict()
    for framework_name, df_raw in ddf_d.items():
        log.debug(f'init on {framework_name}')
        with DFunc(logger=log, tabn=df_raw.iloc[0,1]) as wrkr:
            DFunc_d[framework_name] = wrkr.build(df_raw, log)
    
    ddf_name = wrkr.tag
    #===========================================================================
    # compute metrics
    #===========================================================================
    #data prep
    dx = pd.concat({k:w._get_ddf() for k,w in DFunc_d.items()}, names=['framework_name', 'index'])
    serx = dx.set_index(['exposure'], append=True).droplevel(1).iloc[:,0]
 
    
    metric_df = _calc_metric_df(serx)
 
    
    #===========================================================================
    # plot-------
    #===========================================================================
    # Create a figure with custom dimensions and GridSpec layout
    fig = plt.figure(figsize=(10,10))
    gs = gridspec.GridSpec(3, 1, figure=fig)  # Define a grid with 3 rows and 1 column
    
    #add lines to the top subplot
    ax = fig.add_subplot(gs[:2, 0])  # This adds a subplot in the first two rows
    ax = plot_DFuncs(DFunc_d, log=log, ax=ax)
    
    if not title is None:
        ax.set_title(title)
        
    #===========================================================================
    # add meta text
    #===========================================================================
    # Convert dictionary to string with one entry per row
    info_str = '\n'.join([f'{key}: {value}' for key, value in meta_d.items()])
    
    # Add the string to the bottom right of the axis
    # Use transform=ax.transAxes to position text relative to the axis (0, 0 is bottom-left, 1, 1 is top-right)
    ax.text(
        0.9, 0.1, info_str,
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes,
        #fontsize=10,
        bbox=dict(facecolor='white', alpha=0.1)
    )
    
    #===========================================================================
    # add a table
    #===========================================================================
    
    
    #add the metric_df as text or a table in the lower right of the ax
    
    # Assign the bottom 1/3 for the metrics table
    ax_table = fig.add_subplot(gs[2, 0])  # This adds a subplot in the third row
    ax_table.axis('tight')
    ax_table.axis('off')  # Hide the axes

    # Create the table in the specified subplot
    table = ax_table.table(cellText=metric_df.values.astype(np.float32).round(2),
                           colWidths=[0.1] * len(metric_df.columns),
                           rowLabels=metric_df.index,
                           colLabels=metric_df.columns,
                           cellLoc='center', rowLoc='center',
                           loc='center')  # Center the table within the subplot
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(2, 2)  # Scale the table to better fit the subplot, adjust as necessary
    
    #===========================================================================
    # write figure
    #===========================================================================
    ofp = os.path.join(out_dir, f'ddf_comparison_{ddf_name}.svg')
    fig.savefig(ofp, dpi=300, transparent=True)
    
    log.info(f'wrote figure to \n    {ofp}')
    
    return metric_df
    
    
 
    
def _area_under_curve(group):
    # Sort the group by exposure to ensure proper order
    group = group.sort_index(level='exposure')
    exposure = group.index.get_level_values('exposure')
    impact = group.values
    # Use the trapezoidal rule to compute the area
    return scipy.integrate.trapezoid(impact, exposure)


def _area_between_curves(series):
    # Identify the two groups in the level=0 index
    groups = series.index.get_level_values(0).unique()
    
    if len(groups) != 2:
        raise ValueError("The series must contain exactly two level=0 groups to compute the area between curves.")
    
    # Split the series into two based on the first level
    series1 = series.xs(groups[0], level=0)
    series2 = series.xs(groups[1], level=0)
    
    """
    plt.plot(series1)
    plt.plot(series2)
    
    """
    
    # Determine the union of all exposure points (the x-axis values)
    common_exposure = np.union1d(series1.index, series2.index)
    
    # Interpolate both series to this common exposure grid
    interp_func1 = interp1d(series1.index, series1.values, kind='linear', bounds_error=False, fill_value=0)
    interp_func2 = interp1d(series2.index, series2.values, kind='linear', bounds_error=False, fill_value=0)
    
    interpolated_series1 = interp_func1(common_exposure)
    interpolated_series2 = interp_func2(common_exposure)
    
 
    # Compute the area between the curves using the trapezoidal rule
 
    return scipy.integrate.trapezoid(interpolated_series1 - interpolated_series2, x=common_exposure)
 
    
def plot_DFuncs(DFunc_d, 
                figure=None, ax=None,
                fig_kwargs=dict(
                    #figsize=(10,10),
                    tight_layout=True,
                    ),
                cmap=None,
                log=None,
                ):
    
    #===========================================================================
    # setup figure
    #===========================================================================
    if cmap is None:
        cmap = cmap_default
 
    #figure default
    if ax is None:
        if figure is None:
            figure = plt.figure(**fig_kwargs)
            
        ax = figure.subplots()
    
    #===========================================================================
    # dataprep
    #===========================================================================
    log.debug(f'prepping {len(DFunc_d)} dfuncs')
    #df_d = {k:wrkr._get_ddf() for k, wrkr in DFunc_d.items()}
    
    #===========================================================================
    # loop and plot
    #===========================================================================
    for framework_name, wrkr in DFunc_d.items():
        
        #data prep
        df = wrkr._get_ddf()
        xar, yar = df['impact'].values, df['exposure'].values
        
        #plot
        ax.plot(xar, yar, label=framework_name)
        
    #===========================================================================
    # plost
    #===========================================================================
    ax.grid()
    ax.legend()
    
        
    """
    plt.show()
    """
    
    return ax
        
        
 
        
    
    
    
    
def convert_CanFlood_to_CanCurve_ddf(df_raw, log=None):
    """CanFlood includes metatdata while CanCurve just has the stories as columns
    
    usually, we only go the other way"""
    
    #===========================================================================
    # defaults
    #===========================================================================
    if log is None: log = get_log_stream(level=logging.DEBUG)
    
    
    #===========================================================================
    # compile with CanFlood DFunc
    #===========================================================================
    with DFunc(logger=log, tabn=df_raw.iloc[0,1]) as wrkr:
        wrkr.build(df_raw, log)
        
        ddf_cf_clean = wrkr._get_ddf()
        
    #===========================================================================
    # clean
    #===========================================================================
    return ddf_cf_clean.rename(columns={'exposure':'depths_m', 'impact':'combined'}).set_index('depths_m')

def p04_summary_plot(dx,
                     out_dir=None,log_level=logging.INFO,
                     title='summary_plot',
                     
                     ):
    """summary plots on metrics
    
    
    
    
    
    >>> dx
    framework_name                          CC         DDFP
    ddf_name         metric                                
    R_2-S-BU-EC_ABCA impact_max    1340.210000  1362.730805

                     auc           3367.945800  4170.284578
    ...                                    ...          ...
    R_2-M-C-ST_ABCA  impact_min     178.860000     0.000000

                     abc            529.911675   529.911675
    
    [174 rows x 2 columns]
    
    
    
    
    
    """
 
    #===========================================================================
    # defaults
    #===========================================================================
    log = get_log_stream(level=log_level)
    
    """
    view(dx)
    """
    
    #===========================================================================
    # setup figutre
    #===========================================================================
    metric_l = dx.index.unique('metric')
    
    
    # Create a figure with custom dimensions and GridSpec layout
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 10), sharey=False, sharex=False)
    
    
 
    # Initialize a dictionary to map each metric to its corresponding axis
    ax_d = {metric: ax for metric, ax in zip(metric_l, axes.flatten())}
    
    # Turn off unused axes
    for ax in axes[len(metric_l):]:
        ax.axis('off')

    #===========================================================================
    # populate figure
    #===========================================================================
    for metric, gdf in dx.groupby(level='metric'):
        # Retrieve axis
        ax = ax_d[metric]
        
        xar, yar = gdf.iloc[:,0].values, gdf.iloc[:,1].values
        
        
        #=======================================================================
        # plot data-----
        #=======================================================================
        ax.plot(xar, yar, marker='x', color='black', linestyle='none')
        
        #1:1 line
        
        # Determine the range for both axes
        min_val = min(min(xar), min(yar))
        max_val = max(max(xar), max(yar))
        
        
        linspace_ar = np.linspace(min_val, max_val, 2)
        ax.plot(linspace_ar, linspace_ar, linewidth=0.5, label='1:1', color='red')
        
        #=======================================================================
        # post-----
        #=======================================================================
        



        #adjust axis
        # Calculate the expansion factor (e.g., 1% of the range)
        expansion = (max_val - min_val) * 0.01
        
        # Set identical limits for both axes, applying the expansion factor
        ax.set_xlim(min_val - expansion, max_val + expansion)
        ax.set_ylim(min_val - expansion, max_val + expansion)
        
        
        # Set square aspect ratio
        ax.set_aspect('equal', 'box')
        
        #add meta
 
        meta_d = {
            'rmse': np.sqrt(np.mean((xar - yar) ** 2)),
            }
        info_str = '\n'.join([f'{key}: {value:.2f}' for key, value in meta_d.items()])
    
        # Add the string to the bottom right of the axis
        # Use transform=ax.transAxes to position text relative to the axis (0, 0 is bottom-left, 1, 1 is top-right)
        ax.text(
            0.9, 0.1, info_str,
            verticalalignment='bottom', horizontalalignment='right',
            transform=ax.transAxes,
            #fontsize=10,
            bbox=dict(facecolor='white', alpha=0.1)
        )
        
        
        
 
        # Set the title for the subplot
        if metric in metric_label_d:
            ax_lab = metric_label_d[metric]
        else:
            ax_lab= metric
        ax.set_title(ax_lab)
        
        
        #set labels
        xlab = gdf.columns[0]
        if xlab in framework_label_d:
            xlab = framework_label_d[xlab]
        ax.set_xlabel(xlab)
        
        # For y-axis label
        ylab = gdf.columns[1]  # Example column name for y-axis
        if ylab in framework_label_d:
            ylab = framework_label_d[ylab]
        ax.set_ylabel(ylab)
        
    #===========================================================================
    # post 
    #===========================================================================
    
 
    
    # Adjust layout to avoid overlap
    #plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust rect to accommodate the main title
    fig.suptitle(title)
    
    #===========================================================================
    # write
    #===========================================================================
    ofp =os.path.join(out_dir, f'p04_summary_plot_{title}.svg')
    fig.savefig(ofp)
    
    log.info(f'wrote figure to \n    {ofp}')
    
    return ofp
    
 
    
 
    
 
    
if __name__=='__main__':
    
    out_dir = r'l:\10_IO\CanCurve\misc\DDFP_compare'
    def god(sfx):
        od = os.path.join(out_dir, sfx)
        os.makedirs(od, exist_ok=True)
        return od
    
    #ddf_name_l = ['R_2-L-BD-CU_ABCA']
    ddf_name_l=None
    #===========================================================================
    # #===========================================================================
    # # #build pickle of compiled DDFPs
    # #===========================================================================
    #ddfp_lib = p01_extract_DDFP(ddfp_lib_fp_d,out_dir=god('p01'),ddf_name_l_subset=ddf_name_l)
    # 
    # 
    ddfp_lib = _pick_to_d(r'l:\10_IO\CanCurve\misc\DDFP_compare\p01\DDFP_to_cc_lib.pkl')
        
    ci_df_lib = ddfp_lib.pop('ci')
    meta_lib = ddfp_lib.pop('meta')
    fixd_lib = ddfp_lib.pop('fixed')
    #     
    #     
    #   
    # #===========================================================================
    # # build curves using CanCurve   
    # #===========================================================================
    #CanCurve_ddfs_lib = p02_CanCurve_workflow(ci_df_lib, meta_lib, fixd_lib, out_dir=god('p02'))
    #  
    CanCurve_ddfs_lib = _pick_to_d(r'l:\10_IO\CanCurve\misc\DDFP_compare\p02\DDFP_CanCurve_batch.pkl')
     
     
    #===========================================================================
    # compare
    #===========================================================================
    #metric_dx_d = p03_compare(ddfp_lib.pop('crve'), CanCurve_ddfs_lib, meta_lib, out_dir=god('p03'),ddf_name_l = ddf_name_l)
    
    metric_dx_d = _pick_to_d(r'l:\10_IO\CanCurve\misc\DDFP_compare\p03\metric_dx.pkl')
    
    for k,dx in metric_dx_d.items():
        p04_summary_plot(dx, out_dir = god(f'p03'), title=k)
        
    
    
    
    
    
    
    
    print('finished')
    
    
    
    
    
    
    
    
    
    
    
