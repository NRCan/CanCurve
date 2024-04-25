'''
Created on Apr. 16, 2024

@author: cef

core join, group, and scaling source code
'''
#===============================================================================
# IMPORTS---------
#===============================================================================
import os, sys, platform
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

from .hp.logr import get_log_stream
from .hp.basic import view_web_df as view
from .hp.basic import convert_to_bool


from .parameters import drf_db_default_fp, colns_index, today_str, settings_default_d
from .assertions import assert_ci_df, assert_drf_db, assert_drf_df, assert_proj_db_fp, assert_proj_db
from cancurve import __version__
 
 
#===============================================================================
# helper funcs----------
#===============================================================================
 
def table_exists(conn, table_name):
    """Checks if a table exists in the SQLite3 database.

    Args:
        conn: The database connection object.
        table_name: The name of the table to check.

    Returns:
        True if the table exists, False otherwise.
    """

    cursor = conn.cursor()
    cursor.execute("""
        SELECT count(*)
        FROM sqlite_master 
        WHERE type='table' AND name=?
        """, (table_name,))

    if cursor.fetchone()[0] == 1:
        return True
    else:
        return False

def get_slog(name, log):
    if log is None:
        log = get_log_stream()
        
    return log.getChild(name)

def get_setting(conn, param, table_name="project_settings"):
    """Retrieve a setting from the settings table."""
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT val FROM {table_name} WHERE param = ?", (param,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    except Exception as e:
        raise IOError(f'failed to retrieve {param} FROM {table_name} w/ \n    {e}')
 

def load_ci_df(fp, log=None):
    
    
    
    
    assert os.path.exists(fp)
    assert fp.endswith('.csv')
    
    log = get_slog('load_ci_df', log)
    
    #load
    log.debug(f'loading costitem table from \n    {fp}')
    ci_df = pd.read_csv(fp, index_col=[0,1])
    
    try:
        assert_ci_df(ci_df)
    except Exception as e:
        log.error(f'the loaded costitem table failed failed some checks\n    {fp}\n    {e}')
        raise e
    
    log.info(f'loaded cost-item table {ci_df.shape}')
    
    return ci_df

def load_drf(fp, log=None):
    """load the DRF table from teh database
    
    TODO: load just the necessary rows (once the database is larger)
    
    """
    
    
    
    #===========================================================================
    # precheck
    #===========================================================================
    assert os.path.exists(fp), fp
    assert fp.endswith('.db')
    
    log = get_slog('load_drf', log)
    
    #===========================================================================
    # load
    #===========================================================================
    with sqlite3.connect(fp) as conn:
        assert_drf_db(conn)
        df_raw =  pd.read_sql('SELECT * FROM drf', conn, index_col=['cat', 'sel', 'bldg_layout'])
        
    #===========================================================================
    # post
    #===========================================================================
    df1 = df_raw.copy()

    df1.columns.name='meters'
    df1.columns = df1.columns.astype('float')
    
    try:
        assert_drf_df(df1)
    except Exception as e:
        log.error(f'the loaded drf table failed failed some checks\n    {fp}\n    {e}')
        raise e
    
    log.info(f'loaded DRF table {df1.shape}')
    
    return df1
    
    
    
    

def _get_proj_meta(log, 
                   #curve_name=None,
                   function_name=None,
                   misc=None):
    
 
    proj_meta_df = pd.DataFrame({
            #'curve_name':[curve_name], 
            #'date':[today_str],
            
            'function_name':function_name, 
            'script_name':[os.path.basename(__file__)],
            'script_path':[os.path.dirname(__file__)],
            'now':[datetime.now()], 
            'username':[os.getlogin()], 

            'cancurve_version':[__version__], 
            'python_version':[sys.version.split()[0]],
            'platform':f"{platform.system()} {platform.release()}"            
            
            })
    #add qgis
    try:
        from qgis.core import Qgis
        proj_meta_df['qgis_version'] = Qgis.QGIS_VERSION
    except Exception as e:
        log.warning(f'failed to retrieve QGIS version\n    {e}')
        
    #add misc
    if not misc is None:
        proj_meta_df['misc'] = misc
    return proj_meta_df

def _update_proj_meta(function_name, log, conn, **kwargs):
    proj_meta_df = _get_proj_meta(log,function_name=function_name, **kwargs)
    proj_meta_df.to_sql('project_meta', conn, if_exists='append', index=False)    
    log.debug(f'updated \'project_meta\' w/ {proj_meta_df.shape}')
    return proj_meta_df
    
#===============================================================================
# ACTIONS------------
#===============================================================================

def c00_setup_project(
        ci_fp,
        drf_db_fp=None,
        
        bldg_meta=None,
        fixed_costs_d=None,
        
        bldg_layout='default',
        
        curve_name='curve_name',
        settings_d=None,
        
        log=None,ofp=None,out_dir=None,

        
        ):
    """build project SQLite. load data into it
    
    
    Params
    ---------------
    ci_fp: str
        filepath to cost-item dataset
        
    drf_db_fp: str, optional
        filepath to depth-replacement-fraction dataset
        defaults to drf_db_default_fp (from params)
        
    bldg_layout: str
        building layout used to slice the DRF
    
        
    bldg_meta: dict
        building metadata to be added to 'c00_bldg_meta'
        
    fixed_costs_d: dict
        fixed costs per story
        
        
    settings_d: dict, optional
        conatiner for settings values to apply to 'c00_settings'
        defaults to settings_default_d (from params)
    
    """
    
    #===========================================================================
    # defaults
    #===========================================================================
 
    
    if out_dir is None: 
        out_dir = os.getcwd()
        
    if bldg_meta is None: bldg_meta=dict()
    assert isinstance(bldg_meta, dict)
        
    log = get_slog('c00', log)
    
    if ofp is None:
        ofp = os.path.join(out_dir, f'{curve_name}_{today_str}.cancurve')
        
    assert not os.path.exists(ofp)
    
    if drf_db_fp is None: 
        log.info(f'using default depth-replacement-fraction dataset')
        drf_db_fp = drf_db_default_fp
    else:
        log.info(f'using user-provided depth-replacement-fraction dataset')
        
        
    if settings_d is None:
        settings_d = settings_default_d
        
    assert isinstance(settings_d, dict)
    assert isinstance(bldg_meta, dict)
 

    
    #===========================================================================
    # load datasets---------
    #===========================================================================
    #===========================================================================
    # load costitem table
    #=========================================================================== 
    ci_df = load_ci_df(ci_fp, log=log)
    
    #===========================================================================
    # load depth-replacement-factor database
    #===========================================================================
    drf_df_raw = load_drf(drf_db_fp, log=log)
    
    
    #slice by building layout
    drf_df1 = drf_df_raw.xs(bldg_layout, level=2)
    log.debug(f'sliced DRF w/ bldg_layout={bldg_layout} to get {drf_df1.shape}')
    
    #slice by keys intersect
    bx = drf_df1.index.isin(ci_df.index)
    drf_df2 = drf_df1[bx]
    log.debug(f'sliced DRF w/ CI keys to get {drf_df2.shape}')

    
    #===========================================================================
    # check intersect
    #===========================================================================
 
    log.debug(f'checking datasets')
    bx = np.invert(ci_df.index.isin(drf_df2.index))
    if bx.any():
        """TODO: add some support for populating missing entries into the DRF"""
        msg = f'DRF ({os.path.basename(drf_db_fp)}) is missing {bx.sum()}/{len(bx)} entries from the cost-items'
        
        ofp1 = os.path.join(out_dir, f'missing_DRF.csv')
        ci_df[bx].to_csv(ofp1)
        
        msg+=f'\noutput missing entries {ci_df[bx].shape} to {ofp1}'
        
        msg+=f'\nupdate the DRF and re-run this step before proceeding'
        
 
        
        log.warning(msg)
        
        
        """
        view(ci_df)
        """
 
    else:
        log.debug(f'all keys intersect')
    
        
    #add column
    ci_df['drf_intersect'] = ~bx #note this wriites as 0=False; 1=True
    
    #===========================================================================
    # setup project meta----------
    #===========================================================================
    log.debug(f'setting up project metadata')
    proj_meta_df = _get_proj_meta(log, function_name='c00_setup_project')
    
    #set specials
    proj_meta_df['misc'] = str({'ci_fp':ci_fp, 'drf_db_fp':drf_db_fp})
    #proj_meta_df['scale_m2'] = str(scale_m2)
    
    #===========================================================================
    # building metadata------
    #===========================================================================
    bldg_meta['bldg_layout'] = bldg_layout
    
    #create a table 'bldg_meta' and populate it with the entries in bldg_meta
    """using single row to preserve dtypes"""
    meta_df = pd.DataFrame.from_dict({'attn':bldg_meta}, orient='index')
    
    #===========================================================================
    # fixed costs------
    #===========================================================================
    if not fixed_costs_d is None:
        fc_ser = pd.Series(fixed_costs_d, name='rcv', dtype=float)
        fc_ser.index.name='story'
        log.debug(f'loaded {len(fc_ser)} fixed costs')
        
        #check intersect
        if not set(fc_ser.index).difference(ci_df['story'].unique())==set():
            raise KeyError(f'fixed cost stories do not match CostItems')
        
    else:
        fc_ser=None
        log.warning(f'no fixed costs provided')
    
    #===========================================================================
    # project settings------
    #===========================================================================
    settings_d.update({'curve_name':curve_name})
    
    for k , v in settings_d.copy().items():
        if isinstance(v, bool):
            log.debug(f'converting \'{k}\' to string')
            settings_d[k] = str(v)
    
    settings_df = pd.Series(settings_d, name='val').to_frame()
    settings_df.index.name='param'
    
    
    #===========================================================================
    # start database
    #===========================================================================
    log.info(f'init project SQLite db at\n    {ofp}')
    with sqlite3.connect(ofp) as conn:
        
        #add tables
        proj_meta_df.to_sql('project_meta', conn, if_exists='replace', index=False)
        settings_df.to_sql('project_settings', conn, if_exists='replace', index=True)
        meta_df.to_sql('c00_bldg_meta', conn, if_exists='replace', index=False)        
        ci_df.to_sql('c00_cost_items', conn, if_exists='replace', index=True)        
        drf_df2.to_sql('c00_drf', conn, if_exists='replace', index=True)
        
        if not fc_ser is None:
            fc_ser.to_frame().to_sql('c00_fixed_costs', conn, if_exists='replace', index=True)
        
        
    log.info(f'project SQLiite DB built at \n    {ofp}')
    
    assert_proj_db_fp(ofp)
    
    return ci_df, drf_df2, ofp
 




def c01_join_drf(
        
        proj_db_fp,
        
        
        log=None,
 
        ):
    """Join DRF to CI then multiply through to create 'depth_rcv' table
    
    
    Params
    ------------
    proj_db_fp: str
        filepath to project database

    """
    
    #===========================================================================
    # defaults
    #===========================================================================
   
    log = get_slog('c01', log)
 
    #===========================================================================
    # prechecks
    #===========================================================================
    assert_proj_db_fp(proj_db_fp)

    log.debug(f'openning database from {proj_db_fp}')
    with sqlite3.connect(proj_db_fp) as conn:
        
        #=======================================================================
        # retrieve-----------
        #=======================================================================
        ci_df =  pd.read_sql('SELECT * FROM c00_cost_items', conn, index_col=['cat', 'sel'])
        drf_df = pd.read_sql('SELECT * FROM c00_drf', conn, index_col=['cat', 'sel'])
        
        #check
        bx = ~ci_df['drf_intersect'].astype(bool)
        if bx.any():
            msg = f'missing {bx.sum()}/{len(bx)} cost-item keys in DRF... update your DRF and re-run step 1'
            log.error(msg)
            raise KeyError(msg)
        
        #===========================================================================
        # join
        #===========================================================================
        log.debug(f'left join drf {drf_df.shape} to cost-item {ci_df.shape}')
        df1 = ci_df.loc[:, ['rcv', 'story']].join(drf_df).set_index('story', append=True)
        
        assert df1.notna().all().all()
        
        #=======================================================================
        # multiply through rcv
        #=======================================================================
        rcv_df = df1.pop('rcv')
        
        depth_rcv_df = df1.multiply(rcv_df.values, axis=0)
        
        #===========================================================================
        # update proejct database
        #===========================================================================    
        
        log.info(f'adding \'depth_rcv_df\' project database w/ {depth_rcv_df.shape}\n    {proj_db_fp}')
    
 
        #add result table
        depth_rcv_df.to_sql('c01_depth_rcv', conn, if_exists='replace', index=True)
        
        #update project meta
        _update_proj_meta('c01_join_drf', log, conn)
 
        
    log.info(f'finished')
    
    return depth_rcv_df
    
    
def c02_group_story(proj_db_fp,
            log=None,
            scale_m2=None,
            
            basement_height_m=None, mf_area_m2=None,
            
            
 
            ):
    """group by story and assemble DDF
    
    
    Params
    ---------------
    scale_m2: bool, optional
        whether curves are $/m2 or $
        None: retrieve from project_settings
        
    basement_height_m: float, optional
        vertical distance with which to shift the basement curve in meters
        defaults to value in c00_bldg_meta
        
    mf_area_m2: float, optional
        area with which to scare replacement values (e.g., floor area in m2)
        defaults to value in c00_bldg_meta
        
    """
    
        #===========================================================================
    # defaults
    #===========================================================================
   
    log = get_slog('c02', log)
 
    #===========================================================================
    # prechecks
    #===========================================================================
    assert_proj_db_fp(proj_db_fp)

    log.debug(f'openning database from \n    {proj_db_fp}')
    with sqlite3.connect(proj_db_fp) as conn:
        
        #=======================================================================
        # retrieve
        #=======================================================================
        #cost information
        cid_df = pd.read_sql('SELECT * FROM c01_depth_rcv', conn, index_col=['cat', 'sel', 'story'])
        cid_df.columns = cid_df.columns.astype(float)
        cid_df.columns.name = 'depths_m'
        
        #fixed costs
        if table_exists(conn, 'c00_fixed_costs'):
            fc_ser = pd.read_sql('SELECT * FROM c00_fixed_costs', conn, index_col=['story']).iloc[:, 0]
        else:
            fc_ser=None
            log.warning(f'no fixed costs found in the database')
        
        #project settings
        if scale_m2 is None:
            scale_m2 = convert_to_bool(get_setting(conn, 'scale_m2'))
        assert isinstance(scale_m2, bool)
        
        #building metadata defaults
        bldg_meta_d = pd.read_sql('SELECT * FROM c00_bldg_meta', conn).iloc[0, :].to_dict()
        if basement_height_m is None:
            basement_height_m = float(bldg_meta_d['basement_height_m'])
            
        
        if scale_m2:
            if mf_area_m2 is None:
                assert 'mf_area_m2' in bldg_meta_d, f'passed scale_m2=True but no \'mf_area_m2\' provided'
                mf_area_m2 = float(bldg_meta_d['mf_area_m2'])
            assert isinstance(mf_area_m2, float)
        
        params_d = dict(scale_m2=scale_m2, basement_height_m=basement_height_m, mf_area_m2=mf_area_m2)

            
        log.debug(f'extracted data from proj_db w/ f\n    {params_d}')
        """
        view(cid_df)
        """
        
        #=======================================================================
        # group
        #=======================================================================
        #sum on story
        ddf1 = cid_df.groupby(level='story').sum().T.sort_index()
        
        #add fixed costs
        if not fc_ser is None:
            log.debug(f'adding fixed costs\n    {fc_ser.to_dict()}')
            ddf1 = ddf1.add(fc_ser)
 
 
        
        #check
        for coln, col in ddf1.items():
            assert np.all(np.diff(col.values)>=0), f'{coln} values non-monotonic'
 
        
        #=======================================================================
        # concat on story
        #=======================================================================
        if len(ddf1.columns)==2:
 
            assert isinstance(basement_height_m, float), f'multi-story requires \'basement_height_m\' value'
          
            log.info(f'concating stories together w/ basement_height_m={basement_height_m} ')
 
            
            #===================================================================
            # #basement
            #===================================================================
            #drop negatives
            bx = ddf1.index<0
            """not useful anymore because of how we added fixed costs
            assert ddf1.iloc[bx, 0].sum()<=0, f'got some negative basement damages'"""
            bsmt_s = ddf1.iloc[~bx, 0]
            
            #shift down
            bsmt_s1 = pd.Series(bsmt_s.values, index = bsmt_s.index.values - basement_height_m, name='base')
            bsmt_s1.index.name=ddf1.index.name
            
            #===================================================================
            # harmonize and concat
            #===================================================================
            ddf2 = ddf1.iloc[:, 1].rename('main').to_frame().join(bsmt_s1, how='outer').sort_index()          
 
            ddf2 = ddf2.interpolate(method='index', limit_direction='both')
            
            """
            view(ddf1)
 
            import matplotlib.pyplot as plt
            ddf2.plot()
            plt.show()
            """
            
        else:
            raise NotImplementedError('only 2 story curves are implemented')
            
 
        log.info(f'curves harmonized to {ddf2.shape}')
        #=======================================================================
        # scale
        #=======================================================================
        if scale_m2:

            log.info(f'scaling by {mf_area_m2:.2f} m2')
            
            ddf3 = (ddf2/mf_area_m2).round(2)
            
        else:
            ddf3=ddf2.round(2)
            
        #get_setting(conn, table_name='bldg_meta', attn="mf_area_m2")
        
        #=======================================================================
        # sum stores
        #=======================================================================
        ddf3['combined'] = ddf3.sum(axis=1)
        
        """
        view(ddf3)
        import matplotlib.pyplot as plt
        ddf3.plot()
        plt.show()
        """
        
        
        #===========================================================================
        # update proejct database
        #===========================================================================    
        tabnm='c02_ddf'
        log.info(f'adding \'{tabnm}\' {ddf3.shape} table to project database \n    {proj_db_fp}')
    
 
        #add result table
        ddf3.to_sql(tabnm, conn, if_exists='replace', index=True)
        
        #update project meta
        _update_proj_meta('c02_group_story', log, conn, misc=str(params_d))
 
        
    log.info(f'finished')
    
    return ddf3
        
 
        
        
        

    
    
 
    
    
3