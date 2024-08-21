'''
Created on Aug. 15, 2024

@author: cef

An example of using the bldgs.core functions in a script
'''


import  os, logging, pprint, pickle
from datetime import datetime
import pandas as pd
import numpy as np

from cancurve.hp.logr import get_new_file_logger, get_log_stream
from cancurve.hp.basic import view_web_df as view
from cancurve.hp.basic import get_out_dir, convert_to_float

from cancurve.bldgs.core import c00_setup_project, c01_join_drf, c02_group_story, c03_export


def bldgs_workflow(
        ci_df,
        bldg_meta_d=None,fixed_costs_d=None,
        curve_name=None,
        settings_d=None,
        logger=None, out_dir=None,
        plot=True,
        
        ):
    """run CanCurve buildings 4 step workflow (as a script)
    
    see also bldgs.dialog.BldgsDialog.action_tab4actions_run() for gui implementation
    
    """
    
    
    #===========================================================================
    # defaults
    #===========================================================================
    if logger is None: get_log_stream(level=logging.INFO)
    
    if bldg_meta_d is None:
        
        #get meta from test cases
        from cancurve.bldgs.parameters import bldg_meta_rqmt_df
        """
        view(bldg_meta_rqmt_df)
        """
        d = bldg_meta_rqmt_df.loc[:, ['varName_core', 'case1']].dropna().set_index('varName_core').iloc[:, 0].to_dict()
        d = {k:convert_to_float(v) for k,v in d.items()}
        
    if curve_name is None: curve_name = bldg_meta_d['curve_name']
    
    if out_dir is None: out_dir = get_out_dir(fr'workflow\{curve_name}')
        
    skwargs = dict(out_dir=out_dir, log=logger, overwrite=True)
    #===========================================================================
    # setup project
    #===========================================================================
    
    _, _, proj_db_fp, _ = c00_setup_project(ci_df=ci_df,
        bldg_meta=bldg_meta_d, curve_name=curve_name, 
        fixed_costs_d=fixed_costs_d, settings_d=settings_d,
        **skwargs)
    
    
    #===========================================================================
    # join DRF
    #===========================================================================
    depth_rcv_df = c01_join_drf(proj_db_fp, log=logger)
    
    if plot:
        from cancurve.bldgs.plots import plot_c01_depth_rcv
        fig = plot_c01_depth_rcv(depth_rcv_df, log=logger, fig_kwargs=dict(figsize=(10,10)))
        fig.savefig(os.path.join(out_dir, 'plot_c01_depth_rcv.svg'))
    
    #===========================================================================
    # group story
    #===========================================================================
    ddf3 = c02_group_story(proj_db_fp, log=logger, 
                    scale_m2=True,  #$/m2 curves
                    )
    
    #plot
    if plot:
        from cancurve.bldgs.plots import plot_c02_ddf
        fig = plot_c02_ddf(ddf3, log=logger)
        fig.savefig(os.path.join(out_dir, 'plot_c02_ddf.svg'))
    
    #===========================================================================
    # export
    #===========================================================================
    res_df, ofp = c03_export(proj_db_fp, log=logger, out_dir=out_dir)
    
    #===========================================================================
    # wrap
    #===========================================================================
    return res_df, ofp