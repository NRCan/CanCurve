'''
Created on Apr. 16, 2024

@author: cef

core join, group, and scaling source code
'''
#===============================================================================
# IMPORTS---------
#===============================================================================
import os, sys, platform, warnings
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

from ..hp.logr import get_log_stream
from ..hp.basic import view_web_df as view
from ..hp.basic import convert_to_bool


from .parameters import (
    drf_db_default_fp, colns_index, today_str, settings_default_d, bldg_meta_rqmt_df,
    bldg_layout_options_l,
    )
 
from .assertions import (
    assert_ci_df, assert_drf_db, assert_drf_df, assert_proj_db_fp, assert_proj_db,
    assert_bldg_meta_d, assert_CanFlood_ddf,
    )

from .. import __version__
 
 
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
    
def get_out_dir():
    out_dir = os.path.join(os.path.expanduser('~'), 'CanCurve')
    if not os.path.exists(out_dir):os.makedirs(out_dir)
    return out_dir
 

def load_ci_df(fp, log=None):
    
    
    
    
    assert os.path.exists(fp), f'cost-item datafile does not exist\n    {fp}'
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
    
    
    
    

def _get_proj_meta_d(log, 
                   #curve_name=None,
                   #function_name=None,
                   #misc=None,
                   ):
    """database metadata for tracking progress of core functions
    
    different from teh building metadata
    """
    
    d = {
            #'curve_name':[curve_name], 
            #'date':[today_str],
            
            #'function_name':function_name, 
            'script_name':[os.path.basename(__file__)],
            'script_path':[os.path.dirname(__file__)],
            'now':[datetime.now()], 
            'username':[os.getlogin()], 

            'cancurve_version':[__version__], 
            'python_version':[sys.version.split()[0]],
            'platform':f"{platform.system()} {platform.release()}"            
            
            }
    #add qgis
    try:
        from qgis.core import Qgis
        d['qgis_version'] = Qgis.QGIS_VERSION
    except Exception as e:
        log.warning(f'failed to retrieve QGIS version\n    {e}')
        
 
    return d

def _update_proj_meta(log, conn, meta_d=dict()):
    
    #retrieve data
    d = _get_proj_meta_d(log)
    d.update(meta_d) #overwrite/update
    
    #push to database
    proj_meta_df = pd.DataFrame(d)
    proj_meta_df.to_sql('project_meta', conn, if_exists='append', index=False)    
    log.debug(f'updated \'project_meta\' w/ {proj_meta_df.shape}')
    return proj_meta_df


def _get_building_layout_from_meta(d):
    """construct the DRF 'bldg_layout' key from granular metadata
    
    '1storeybase', '2storeybase','1storeycrawl', '2storeycrawl'
    
    legacy carry-over from DRF format
    would be better to have keys directly in DRF
    """
    from .parameters_ui import building_details_options_d
    
    #check expectations
    assert d['occupancyClassification']=='Residential'
    assert d['foundationType'] in building_details_options_d['foundationType']
    if not isinstance(d['storeys'], int):
        assert d['storeys']=='Split'
 
    
    
    """
    for k,v in bldg_meta_d.items():
        print(k,v)
    """
    #===========================================================================
    # construct from logic
    #===========================================================================
    bldg_layout='default'
    
    if d['foundationType']=='basement':        
        if d['storeys']==1:            
                bldg_layout='1storeybase'            
        elif d['storeys']==2:
            bldg_layout='2storeybase'
            
    elif d['foundationType']=='crawlspace':
        if d['storeys']==1:            
                bldg_layout='1storeycrawl'            
        elif d['storeys']==2:
            bldg_layout='2storeycrawl'
        
            
            
    return bldg_layout
        
            
    


class DFunc(object): 
    """
    2024 04 26: copied from CanFlood dev
    
    used by DFunc objects
    also DFunc handlers:
        model.dmg2.Dmg2
        misc.curvePlot.CurvePlotr
        misc.rfda.convert
        
    """
    #===========================================================================
    # pars from data
    #===========================================================================
    """see crve_d below"""
    impact_units = '' #units of impact prediction (used in axis labelling)
    
    
    #==========================================================================
    # program pars
    #==========================================================================

    
    #dd_df = pd.DataFrame() #depth-damage data
    
    """lets just do columns by location
    exp_coln = []"""
    
    #default variables for building new curves
    """see also parameters.building_meta_dtypes
    
    2024-04-30: switched to import from csv
    """
    
    #===========================================================================
    # crve_d = {
    #         #function metadata
    #         'tag':'?','desc':'?','source':'?','location':'?','date':'?',
    #         #'file_conversion':'CanFlood',
    #         
    #         #function definitions
    #         'impact_units':'$CAD', 'impact_var':'damage',
    #         'exposure_units':'m', 'exposure_var':'flood depth above floor',
    #         'scale_units':'m2', 'scale_var':'building footprint',            
    #         
    #         #headers for DDF
    #         'exposure':'impact'}
    # 
    # cdf_chk_d = {'tag':str, #parameters expected in crv_d (read from xls tab)
    #              'exposure':str,
    #              'impact_units':str}
    #===========================================================================
    
    #==========================================================================
    # user pars
    #==========================================================================
    tag = 'dfunc'
    min_dep = None
    pars_d = {}
    #curves_fp=''
    curve_deviation= 'base' #0: take first curve. otherwise, label lookup of curve deviation 
    
    def __init__(self,
                 tabn='damage_func', #optional tab name for logging
                 #curves_fp = '', #filepath loaded from (for reporting)
                 curve_deviation = 'base', #which curve deviation to build
                 monot=True,
                 logger=None):
        
        #=======================================================================
        # attach
        #=======================================================================
        self.tabn= tabn
        
        """
        todo: reconcile tabn vs tag
        """
        #self.curves_fp = curves_fp
        self.monot=monot
        self.curve_deviation=curve_deviation
        self.logger=logger
        
        #extract teh default metadata from teh parameter table
        meta_df = bldg_meta_rqmt_df.loc[:, ['varName_canflood', 'required_canflood', 'default_canflood', 'type']
                                            ].dropna(subset='varName_canflood', how='all'
                                                     ).set_index('varName_canflood')
                                                     
        self.crve_d = meta_df['default_canflood'].to_dict()
        self.cdf_chk_d = {k:eval(v) for k,v in meta_df[meta_df['required_canflood']]['type'].to_dict().items()}
        
        #init the baseclass
        #super().__init__(**kwargs) #initilzie Model
        
    
    def build(self,
              df_raw, #raw parameters to build the DFunc w/ . dummy index
              logger,
              curve_deviation=None,
              ):
        """"
        Params
        ---------
        df_raw: pd.DataFrame
            >=2 column frame with
                first column (name '0') containing indexers (should loosen this)
                second column containing values
                additional columns used for 'curve_deviations'
                
                
        
        """
        
        
        #=======================================================================
        # defaults
        #=======================================================================
        log = logger.getChild('%s'%self.tabn)
        if curve_deviation is None: curve_deviation=self.curve_deviation
        log.debug('on %s'%(str(df_raw.shape)))
        
        self.df_raw = df_raw.copy() #useful for retrieving later
        #=======================================================================
        # precheck
        #=======================================================================
        try:
            assert self.check_cdf(df_raw)
        except Exception as e:
            """letting this pass for backwards compatability"""
            log.error('curve failed check w/ \n    %s'%e)
        

        #slice and clean
        """not sure why we require 0 and 1 in teh index... should loosen this"""
        df = df_raw.set_index(0, drop=True).dropna(how='all', axis=1)            
        
        #======================================================================
        # identify depth-damage data
        #======================================================================
 
        
        #get the value specifying the start of the dd
 
        depthLoc_key='exposure'
        assert depthLoc_key in df.index, f'missing depthLoc_key = \'{depthLoc_key}\''
        depth_loc = df.index.get_loc(depthLoc_key)
        
        boolidx = pd.Series(df.index.isin(df.iloc[depth_loc:len(df), :].index), index=df.index,
                            name='dd_vals')
        
        """
        this includes the 'exposure' row in the dd_df
        view(df.join(boolidx))
        """
 
        #======================================================================
        # attach other pars
        #======================================================================
        #get remainder of data
        mser = df.loc[~boolidx, :].iloc[:,0]
        mser.index =  mser.index.str.strip() #strip the whitespace
        pars_d = mser.to_dict()
        
        #=======================================================================
        # parameter value check
        #=======================================================================
        assert 'tag' in pars_d, '%s missing tag'%self.tabn
        assert isinstance(pars_d['tag'], str), 'bad tag parameter type: %s'%type(pars_d['tag'])
        
        if not  pars_d['tag']==self.tabn:
            warnings.warn('tag/tab mismatch (\'%s\', \'%s\')'%(pars_d['tag'], self.tabn))
        
        #handle curve deviation
        if not curve_deviation=='base':
            assert curve_deviation in df.loc['exposure', :].values, \
                'requested curve_deviation \'%s\' not found on \'%s\''%(
                    curve_deviation, self.tabn)
                
         
        
        for varnm, val in pars_d.items():  #loop and store on instance
            setattr(self, varnm, val)
            
        log.debug('attached %i parameters to Dfunc: \n    %s'%(len(pars_d), pars_d))
        self.pars_d = pars_d.copy()
        
        #======================================================================
        # extract depth-damage data
        #======================================================================
 
        #get just the dd rows
        ddf1 = df.loc[boolidx, :]
        ddf1.index.name=None
        
        #set headers from a row
        ddf1.columns = ddf1.loc[depthLoc_key]
        ddf1 = ddf1.drop(depthLoc_key)
        
        
        #select deviation
        if curve_deviation=='base':
            ddcol = ddf1.columns[0] #taking first
        else:
            ddcol = curve_deviation
            
        #reindex for this deviation
        ddf2 = ddf1.loc[:, ddcol].to_frame().reset_index().rename(columns={'index':depthLoc_key})
        
 
        #typeset it
        try:
            ddf2 = ddf2.astype(float)
        except Exception as e:
            raise IOError('failed to typsset the ddf for \'%s\' w/ \n    %s'%(self.tabn, e))
        
        """
        view(dd_df)
        """
        
        ar = ddf2.sort_values(depthLoc_key).T.values
        """NO! leave unsorted
        ar = np.sort(np.array([dd_df.iloc[:,0].tolist(), dd_df.iloc[:,1].tolist()]), axis=1)"""
        self.dd_ar = ar
        
        #=======================================================================
        # check
        #=======================================================================
        """This is a requirement of the interp function"""
        assert np.all(np.diff(ar[0])>0), 'exposure values must be increasing'
        
        #impact (y) vals
        if not np.all(np.diff(ar[1])>=0):
            msg = '\'%s\' impact values are decreasing'%self.tabn
            if self.monot:
                raise IOError(msg)
            else:
                log.debug(msg)
            

        #=======================================================================
        # get stats
        #=======================================================================
        self.min_dep = min(ar[0])
        self.max_dep = max(ar[0])
        #=======================================================================
        # wrap
        #=======================================================================
        log.debug('\'%s\' built w/ dep min/max %.2f/%.2f and dmg min/max %.2f/%.2f'%(
            self.tag, min(ar[0]), max(ar[0]), min(ar[1]), max(ar[1])
            ))
        
        return self
        
 
    def get_stats(self): #get basic stats from the dfunc
        deps = self.dd_ar[0]
        dmgs = self.dd_ar[1]
        
        
        np.all(np.diff(deps)>=0)
        
 
        return {**{'min_dep':min(deps), 'max_dep':max(deps), 
                'min_dmg':min(dmgs), 'max_dmg':max(dmgs), 'dcnt':len(deps),
                'dep_mono':np.all(np.diff(deps)>=0), 'dmg_mono':np.all(np.diff(dmgs)>=0)
                },
                   
                **self.pars_d}
        
 
    def _get_split(self,#split the raw df into function and metadata
                   df_raw=None, #dummy index
                   fmt='dict', #result format
                   ): 
        if df_raw is None: df_raw=self.df_raw.copy()
        df = df_raw.set_index(0, drop=True)
        
        #get dd
        assert 'exposure' in df.index
        
        dd_indx = df.index[df.index.get_loc('exposure')+1:] #get those after exposure
        ddf = df.loc[dd_indx, :]
        
        #get meta
        mdf = df.loc[~df.index.isin(dd_indx), :]
        
        if fmt=='df':
            return ddf, mdf
        elif fmt=='dict':
            return ddf.iloc[:,0].to_dict(), mdf.iloc[:,0].to_dict()
        
        
    def _get_ddf(self): #return a formatted dataframe of the dd_ar
        return pd.DataFrame(self.dd_ar.T, columns=['exposure', 'impact'])
        
        
 
    def check_cdf(self, #convenience for checking the df as loaded
                  df, 
 
                  **kwargs): 
        
        """
        converting to dict for most checks
        
        not constructing, just simple field and type checks
        
        view(df)
        """
 
        
        assert isinstance(df, pd.DataFrame)
 
 
        crv_d = df.set_index(0, drop=True).iloc[:, 0].dropna().to_dict()
        
        
        return self.check_crvd(crv_d, **kwargs)



    def check_crvd(self, #validate the passed curve_d  
                    crv_d,
                    logger=None):
        
        if logger is None: logger=self.logger
        log = logger.getChild('check_crvd')
        
        assert isinstance(crv_d, dict)
        
        #log.debug('on %i'%len(crv_d))
        
        #=======================================================================
        # #check key presence
        #=======================================================================
        miss_l = set(self.cdf_chk_d.keys()).difference(crv_d.keys())
        if not len(miss_l)==0:
            log.error('dfunc \'%s\' missing keys: %s \n    %s'%(self.tabn, miss_l, ''))
            return False
        
        #=======================================================================
        # value type
        #=======================================================================
        for k, v in self.cdf_chk_d.items():
            if not isinstance(crv_d[k], v):
                log.error( '%s got bad type on %s'%(self.tabn, k))
                return False
            
        #=======================================================================
        # order
        #=======================================================================
        """TODO: check order"""
        

        return True
    
    def __enter__(self):
        return self
    
    def __exit__(self,*args,**kwargs):
        pass

    
    
#===============================================================================
# ACTIONS------------
#===============================================================================

def c00_setup_project(
        ci_fp=None, ci_df=None,
        drf_db_fp=None,
        
        bldg_meta=None,
        #bldg_layout=None,
        
        fixed_costs_d=None,        
        
        curve_name=None,
        settings_d=None,
        
        log=None,ofp=None,out_dir=None,overwrite=True,

        
        ):
    """build project SQLite. load data into it
    
    
    Params
    ---------------
    ci_fp: str
        filepath to cost-item dataset
        
    drf_db_fp: str, optional
        filepath to depth-replacement-factor dataset
        defaults to drf_db_default_fp (from params)
        
    bldg_layout: str, optional
        building layout used to slice the DRF
        derfaults to value in bldg_meta
        
    curve_name: str, optional
        filename base
        defaults to value in settings_d
        
    settings_d: dict, optional
        project settings values to apply to 'project_settings' table
        defaults to settings_default_d (from params)
        
    
        
    bldg_meta: dict
        building metadata to be added to 'c00_bldg_meta'
        
    fixed_costs_d: dict
        fixed costs per story
        
        

    
    """
    
    #===========================================================================
    # defaults---------
    #===========================================================================
 
    
    log = get_slog('c00', log)
    
    #===========================================================================
    # buildg metadata
    #===========================================================================
    if bldg_meta is None: bldg_meta=dict()
    assert_bldg_meta_d(bldg_meta)

    
    if settings_d is None:
        settings_d = settings_default_d
        
    assert isinstance(settings_d, dict)
    assert isinstance(bldg_meta, dict)
        
 
    
    #===========================================================================
    # from containers
    #===========================================================================
    #building layout
    #if bldg_layout is None:
    bldg_layout = bldg_meta['bldg_layout']
    assert isinstance(bldg_layout, str)
    assert bldg_layout in bldg_layout_options_l
 
        
    
    if curve_name is None:
        curve_name = settings_d['curve_name']
    assert isinstance(curve_name, str) 
    
    #===========================================================================
    # filepaths------
    #===========================================================================
    if out_dir is None: 
        out_dir = os.getcwd()
        
    if ofp is None:
        ofp = os.path.join(out_dir, f'{curve_name}_{today_str}.cancurve')
        
    if os.path.exists(ofp):
        if overwrite:
            log.warning(f'project database file exists... overwriting')
            try:
                os.remove(ofp)
            except Exception as e:
                log.warning(f'failed to remove the exisiting filepath w/ \n    {e}')
                
        else:
            raise IOError('project database file exists and overwrite=False')
        
    
    """letting this pass   
    assert not os.path.exists(ofp)"""
    
    if not os.path.exists(os.path.dirname(ofp)):os.makedirs(os.path.dirname(ofp))
        
    
    if drf_db_fp is None: 
        log.info(f'using default depth-replacement-fraction dataset')
        drf_db_fp = drf_db_default_fp
    else:
        log.info(f'using user-provided depth-replacement-fraction dataset')
        
 
    log.debug(f'function defaults set as \n    %s'%
              dict(curve_name=curve_name, bldg_layout=bldg_layout, 
                   drf_db_fp=drf_db_fp, settings_d=settings_d, ofp=ofp))
    #===========================================================================
    # load datasets---------
    #===========================================================================
    #===========================================================================
    # load costitem table
    #===========================================================================
    if ci_df is None: 
        ci_df = load_ci_df(ci_fp, log=log)
    else:
        assert ci_fp is None
        ci_df = ci_df.copy()
    
    #===========================================================================
    # load depth-replacement-factor database
    #===========================================================================
    drf_df_raw = load_drf(drf_db_fp, log=log)
    
    """
    drf_df_raw.index.unique('bldg_layout')
    """
    
    
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
        
        msg+=f'\noutput missing entries {ci_df[bx].shape} to:\n    {ofp1}'
        
        msg+=f'\nupdate the DRF and re-run this step before proceeding'
 
        log.warning(msg)
 
    else:
        log.debug(f'all keys intersect')
        msg=None
    
        
    #add column
    ci_df.loc[:, 'drf_intersect'] = ~bx #note this wriites as 0=False; 1=True
    
    #===========================================================================
    # setup project meta----------
    #===========================================================================
    log.debug(f'setting up project metadata')
    
    d = _get_proj_meta_d(log)
    d.update(dict(
        function_name='c00_setup_project', misc=str({'ci_fp':ci_fp, 'drf_db_fp':drf_db_fp}),
        #scale_m2 = str(scale_m2),
        ))
    proj_meta_df = pd.DataFrame(d)
    
 
    
    #===========================================================================
    # building metadata------
    #===========================================================================

    
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
        miss = set(ci_df['story'].unique()).difference(fc_ser.index.values)
        if not miss==set():
            raise KeyError(f'\'Storey\' values specified in the Fixed Costs table do not match those in the Cost Item Dataset'+\
                           '\n    ensure fixed costs are provided for each storey')
            
        fc_ser = fc_ser.loc[fc_ser.index.isin(ci_df['story'].unique())]
        
    else:
        fc_ser=None
        log.warning(f'no fixed costs provided')
    
    #===========================================================================
    # project settings------
    #===========================================================================
    #settings_d.update({'curve_name':curve_name})
    
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
    
    return ci_df, drf_df2, ofp, msg
 




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
        # update proejct database---------
        #===========================================================================    
        
        log.info(f'adding \'depth_rcv_df\' project database w/ {depth_rcv_df.shape}\n    {proj_db_fp}')
    
 
        #add result table
        depth_rcv_df.to_sql('c01_depth_rcv', conn, if_exists='replace', index=True)
        
        #update project meta
        _update_proj_meta(log, conn, meta_d =dict(function_name='c01_join_drf'))
        
 
 
        
    log.info(f'finished and added \'c01_depth_rcv\' to project database')
    
    return depth_rcv_df
    
    
def c02_group_story(proj_db_fp,
            log=None,
            scale_m2=None,
            
            basement_height_m=None, scale_value_m2=None,
            
            
 
            ):
    """group by story and assemble DDF
    
    NOTE: depth values come from the depth-replacement-factor database
    
    
    Params
    ---------------
    scale_m2: bool, optional
        whether curves are $/m2 or $
        None: retrieve from project_settings
        
    basement_height_m: float, optional
        vertical distance with which to shift the basement curve in meters
        defaults to value in c00_bldg_meta
        
    scale_value_m2: float, optional
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
            if scale_value_m2 is None:
                assert 'scale_value_m2' in bldg_meta_d, f'passed scale_m2=True but no \'scale_value_m2\' provided'
                scale_value_m2 = float(bldg_meta_d['scale_value_m2'])
            assert isinstance(scale_value_m2, float)
        
        params_d = dict(scale_m2=scale_m2, basement_height_m=basement_height_m, scale_value_m2=scale_value_m2)

            
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
        #single story
        if len(ddf1.columns)==1:
            ddf2 = ddf1.copy()
        
        elif len(ddf1.columns)==2:
 
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
            #DDFP seems to have some 2 story curves...
            #but this doesnt really make sense as the DRF only goes up to 2.7
            raise NotImplementedError(f'cost-item data sets with {len(ddf1.columns)} stories are not supported')
            
 
        log.info(f'curves harmonized to {ddf2.shape}')
        #=======================================================================
        # scale
        #=======================================================================
        if scale_m2:

            log.info(f'scaling by {scale_value_m2:.2f} m2')
            
            ddf3 = (ddf2/scale_value_m2).round(2)
            
        else:
            ddf3=ddf2.round(2)
            
        #get_setting(conn, table_name='bldg_meta', attn="scale_value_m2")
        
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
        _update_proj_meta(log, conn, 
                          meta_d = dict(function_name='c02_group_story', misc=str(params_d))
                                        )
 
        
    log.info(f'finished adding \'{tabnm}\'')
    
    return ddf3


def c03_export(
        proj_db_fp,
        output_format='CanFlood',
        ofp=None, out_dir=None, 
        log=None,
            ):
    """export the DDF in CanFlood format"""
    
    #===========================================================================
    # defaults
    #===========================================================================
   
    log = get_slog('c03', log)
 
        
 
    #===========================================================================
    # prechecks
    #===========================================================================
    assert_proj_db_fp(proj_db_fp)

    log.debug(f'openning database from \n    {proj_db_fp}')
    with sqlite3.connect(proj_db_fp) as conn:
        
        #=======================================================================
        # load from project database
        #=======================================================================
        #depth-damage
        ddf = pd.read_sql('SELECT * FROM c02_ddf', conn)
 
        log.debug(f'loaded DDF w/ {ddf.shape}')
        
        #building meta
        bldg_meta_d = pd.read_sql('SELECT * FROM c00_bldg_meta', conn).iloc[0, :].to_dict()
        log.debug(f'loaded c00_bldg_meta w/ \n    {bldg_meta_d}')
        
        #project settings
        settings_d = pd.read_sql('SELECT * FROM project_settings', conn, index_col=['param']).iloc[:, 0].to_dict()
                
 
    if not output_format=='CanFlood':
        raise NotImplementedError(output_format)
    
    #=======================================================================
    # compose into CanFlood format-------
    #=======================================================================
    with DFunc(tabn=settings_d['curve_name'], logger=log) as wrkr:
        
        #=======================================================================
        # build metadata
        #=======================================================================
        crve_d = wrkr.crve_d.copy() #start with a copy of the template        
        
        #update with user supplied metadata
        crve_d['tag'] = settings_d['curve_name']
        crve_d.update(bldg_meta_d) #preserves order
        
        #force exposure to the end
        if not list(crve_d.keys())[-1]=='exposure': 
            v1 = crve_d.pop('exposure')
            crve_d = {**crve_d, **{'exposure':v1}}
            
        #scaling
        scale_m2 = convert_to_bool(settings_d['scale_m2'])
        if scale_m2:
            crve_d['impact_units'] = '%s/%s'%(crve_d['impact_units'], crve_d['scale_units'])
            assert not crve_d['scale_var']  is None
        else:
            crve_d['scale_var']='none'
            
        #=======================================================================
        # #extract depth-damage
        #=======================================================================
        dd_d = ddf.loc[:, ['depths_m', 'combined']].astype(float).round(3).set_index('depths_m').iloc[:,0].to_dict()
        
        #=======================================================================
        # #assemble
        #=======================================================================
        dcurve_d = {**crve_d, **dd_d}
        
        #check
        assert wrkr.check_crvd(dcurve_d)
        
        #convert to frame
        res_df = pd.Series(dcurve_d).to_frame().reset_index()
        
        #=======================================================================
        # test
        #=======================================================================
    #maniuplate frame to match CanFlood expectations
    df1 = res_df.copy()
    df1.columns = [0, 1]
        
    assert_CanFlood_ddf(df1)

        
    #===========================================================================
    # output
    #===========================================================================
    """TODO: let user specify xls library?"""
    tabnm = settings_d['curve_name']
    
    #default paths
    if ofp is None:
        if out_dir is None: out_dir=get_out_dir()
        ofp = os.path.join(out_dir, f'CanCurve_{tabnm}.xls')
        
    
    
    with pd.ExcelWriter(ofp, engine='openpyxl') as writer: 
            
        if len(tabnm)>30:
            log.warning('tabName exceeds excel limits... truncating')
            tabnm = tabnm[:29] 
            
        res_df.to_excel(writer, sheet_name=tabnm, index=False, header=False)
    log.info(f'wrote {res_df.shape} to \n    {ofp}')
    
    return res_df, ofp
    
            
        
        
 
        
        
        
        
    