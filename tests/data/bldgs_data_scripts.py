'''
Created on Aug. 22, 2024

@author: cef
'''
import os, pickle, copy, pytest
import pandas as pd
import numpy as np

from cancurve.hp.basic import view_web_df as view
from cancurve.bldgs.assertions import assert_bldg_meta_d, assert_fixed_costs_d
from cancurve.bldgs.core import _get_bldg_meta_d
#===============================================================================
# parametesr
#===============================================================================
#data directory
from tests.conftest import test_data_dir_master as parent_tdata_dir
test_data_dir_master = os.path.join(parent_tdata_dir, 'bldgs')


from cancurve.bldgs.dialog_test_scripts import fixed_costs_master_d #eventually copy this back

from cancurve.bldgs.parameters import bldg_meta_rqmt_df

bldg_meta_rqmt_df_test = bldg_meta_rqmt_df.copy()

#===============================================================================
# helpers
#===============================================================================

def _get_filename_by_ext(folder_path, ext):
 
    matching_files = [
        filename
        for filename in os.listdir(folder_path)
        if filename.endswith(ext)
    ]

    if not matching_files:
        raise FileNotFoundError(f"No file endswith with '{ext}' found in {folder_path}")

    if len(matching_files) > 1:
        raise ValueError(f"Multiple files endswith with '{ext}' found in {folder_path}")

    return os.path.join(folder_path, matching_files[0])

def _pick_to_d(filename):
    
    with open(filename, 'rb') as file:
        dictionary = pickle.load(file)
        
    #print(f'loaded {len(dictionary)} from \n    {filename}')
    return dictionary

#===============================================================================
# load case data from files
#===============================================================================
 

def load_tests_cases_from_file(
        #df=None,
        ):
    """appends fixed costs to fixed_costs_master_d and returns full list of cases"""
    
    global bldg_meta_rqmt_df_test
 
 
    
    for root, dirs, _ in os.walk(test_data_dir_master):
        for caseName in dirs:
            if not (caseName in fixed_costs_master_d.keys() or caseName.startswith('__')):
                #retrieve the filepath
                srch_dir = os.path.join(test_data_dir_master, caseName)
                
                #===============================================================
                # fixed costs
                #===============================================================
                try:
                    #fixed_d_fp = _get_filename_by_ext(srch_dir, 'pkl')
                    fixed_d = _pick_to_d(os.path.join(srch_dir, 'fixed_d.pkl'))
 
 
                        
                    assert_fixed_costs_d(fixed_d)
                    
                    #load and append
                    fixed_costs_master_d[caseName] = fixed_d
                except Exception as e:
                    print(e)
                    
                #===============================================================
                # metadata
                #===============================================================
                #load
                bldg_meta_d = _pick_to_d(os.path.join(srch_dir, 'bldg_meta_d.pkl'))
                assert_bldg_meta_d(bldg_meta_d, msg=caseName)
                
                #fill in blank.. probably a better way to do this
                if np.isnan(bldg_meta_d['basement_height_m']):
                    bldg_meta_d['basement_height_m'] = 2.7
                
                s = pd.Series(bldg_meta_d, name=caseName)
                
                #join as a new column
                bldg_meta_rqmt_df_test = bldg_meta_rqmt_df_test.join(s, on='varName_core')
                """
                view(bldg_meta_rqmt_df_test)
                """
                #check again
                #_get_bldg_meta_d(caseName, df=bldg_meta_rqmt_df_test)
                #view()
        
        
           
        break
    
    #fill in blanks in column 'basement_height_m' with adjacent values
    #no... too tricky to id the correct columns
    #loc = bldg_meta_rqmt_df_test.index[bldg_meta_rqmt_df_test.iloc[:,0]=='basement_height_m'][0]
    #bldg_meta_rqmt_df_test.iloc[loc, :]
    
    print(f'built bldg_meta_rqmt_df_test w/ {bldg_meta_rqmt_df_test.shape}')
    
    #===========================================================================
    # handle bad cases
    #===========================================================================
    #===========================================================================
    # l = list()
    # 
    # for k in list(fixed_costs_master_d.keys()):
    #     if k in ['case2']:
    #         l.append(
    #             pytest.param(k, marks=pytest.mark.xfail(raises=KeyError, reason="this case is missing some DRF entries"))
    #             )
    #     else:
    #         l.append(k)
    # 
    #===========================================================================
    # import pprint
    # pprint.pprint(l)
    #===========================================================================
    #===========================================================================
    return 
 
#test cases from file... built from load_tests_cases_from_file
#best to have it hard-coded for pytest behavior

test_cases_l = [
    'case1',
 pytest.param('case2', marks=pytest.mark.xfail(raises=KeyError, reason="this case is missing some DRF entries")),
 'case3',
 'case4_R2',
 'AB-Calgary_R_1-L-BD-CU_ABCA',
 'AB-Calgary_R_1-L-BD-ST_ABCA',
 'AB-Calgary_R_1-L-BU-ST_ABCA',
 'AB-Calgary_R_1-L-C-CU_ABCA',
 'AB-Calgary_R_1-L-C-ST_ABCA',
 'AB-Calgary_R_1-M-BD-CU_ABCA',
 'AB-Calgary_R_1-M-BD-ST_ABCA',
 'AB-Calgary_R_1-M-BU-ST_ABCA',
 'AB-Calgary_R_1-M-C-CU_ABCA',
 'AB-Calgary_R_1-S-BD-AA_ABCA',
 'AB-Calgary_R_1-S-BD-EC_ABCA',
 'AB-Calgary_R_1-S-BU-EC_ABCA',
 'AB-Calgary_R_1-S-C-AA_ABCA',
 'AB-Calgary_R_1-S-C-EC_ABCA',
 'AB-Calgary_R_2-L-BD-CU_ABCA',
 'AB-Calgary_R_2-L-BD-ST_ABCA',
 'AB-Calgary_R_2-L-BU-ST_ABCA',
 'AB-Calgary_R_2-L-C-CU_ABCA',
 'AB-Calgary_R_2-L-C-ST_ABCA',
 'AB-Calgary_R_2-M-BD-CU_ABCA',
 'AB-Calgary_R_2-M-BD-ST_ABCA',
 'AB-Calgary_R_2-M-BU-ST_ABCA',
 'AB-Calgary_R_2-M-C-CU_ABCA',
 'AB-Calgary_R_2-M-C-ST_ABCA',
 'AB-Calgary_R_2-S-BD-AA_ABCA',
 'AB-Calgary_R_2-S-BD-EC_ABCA',
 'AB-Calgary_R_2-S-BU-EC_ABCA',
 'AB-Calgary_R_2-S-C-AA_ABCA',
 'AB-Calgary_R_2-S-C-EC_ABCA',
 'NB-Fredericton_R_1-L-BD-CU_NBFR',
 'NB-Fredericton_R_1-L-BD-ST_NBFR',
 'NB-Fredericton_R_1-L-BU-ST_NBFR',
 'NB-Fredericton_R_1-L-C-CU_NBFR',
 'NB-Fredericton_R_1-L-C-ST_NBFR',
 'NB-Fredericton_R_1-M-BD-CU_NBFR',
 'NB-Fredericton_R_1-M-BD-ST_NBFR',
 'NB-Fredericton_R_1-M-BU-ST_NBFR',
 'NB-Fredericton_R_1-M-C-CU_NBFR',
 'NB-Fredericton_R_1-M-C-ST_NBFR',
 'NB-Fredericton_R_1-S-BD-AA_NBFR',
 'NB-Fredericton_R_1-S-BD-EC_NBFR',
 'NB-Fredericton_R_1-S-BU-EC_NBFR',
 'NB-Fredericton_R_1-S-C-AA_NBFR',
 'NB-Fredericton_R_1-S-C-EC_NBFR',
 'NB-Fredericton_R_2-L-BD-CU_NBFR',
 'NB-Fredericton_R_2-L-BD-ST_NBFR',
 'NB-Fredericton_R_2-L-BU-ST_NBFR',
 'NB-Fredericton_R_2-L-C-CU_NBFR',
 'NB-Fredericton_R_2-L-C-ST_NBFR',
 'NB-Fredericton_R_2-M-BD-CU_NBFR',
 'NB-Fredericton_R_2-M-BD-ST_NBFR',
 'NB-Fredericton_R_2-M-BU-ST_NBFR',
 'NB-Fredericton_R_2-M-C-CU_NBFR',
 'NB-Fredericton_R_2-M-C-ST_NBFR',
 'NB-Fredericton_R_2-S-BD-AA_NBFR',
 'NB-Fredericton_R_2-S-BD-EC_NBFR',
 'NB-Fredericton_R_2-S-BU-EC_NBFR',
 'NB-Fredericton_R_2-S-C-AA_NBFR',
 'NB-Fredericton_R_2-S-C-EC_NBFR']





