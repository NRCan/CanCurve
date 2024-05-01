'''
Created on Apr. 16, 2024

@author: cef

porting Xactimate 'raw estimate' to Archetype Cost-item dataset
'''
import  os
from datetime import datetime
import pandas as pd
import numpy as np

from cancurve.hp.basic import view_web_df as view
from cancurve.parameters import colns_index, colns_dtypes, floor_story_d

import sys
#print(f'    {sys.executable}\n  {sys.version_info}')



def xls_to_csv(estimate_xls_fp, info_fp, out_dir=None, out_fp=None):
    """Converts the first sheet of an XLS file to CSV.

    Args:
        estimate_xls_fp (str): Filepath of the XLS input file.
        out_fp (str): Filepath of the CSV output file.
    """

 
    #=======================================================================
    # load raw data
    #=======================================================================
    print(f"Loading XLS file \n    {estimate_xls_fp}")
    df_raw = pd.read_excel(estimate_xls_fp, sheet_name=0)  # Load the first sheet
    df1 = df_raw.copy().loc[:, ['Cat', 'Sel', 'Group Code', 'RCV', 'Desc']]
    df1.columns = df1.columns.str.strip().str.lower().str.replace(' ', '_') 
    

    #=======================================================================
    # formatting and checks
    #=======================================================================
    #check data types
    for coln, dstr in df1.dtypes.items():
        if not coln in colns_dtypes:
            raise IOError(f'unrecognized column name in estimate data: \'{coln}\'')
        assert dstr==colns_dtypes[coln], coln
        
    #check keys are unique
    keys = ['cat', 'sel', 'group_code']
    bx = df1.loc[:, keys].duplicated(keep=False)
    if bx.any():
        """this is normal.. often have duplicate items here (e.g., 2x countertops in the kitchen)"""
        print(f'got {bx.sum()}/{len(bx)} duplicated {keys} keys\n%s'%df1[bx].sort_values(keys))
 
    
    
    #check description
    assert not df1['desc'].str.contains(r"[\n]").any(), 'contains some newlines'
    if df1['desc'].str.contains(r"[,]").any():
        print('descriptions contains some commas')
        
    #replace double quotes with in
    df1['desc'] = df1['desc'].str.replace('"', 'in')
    
    #replace commas with periods
    df1['desc'] = df1['desc'].str.replace(',', '.')
    
    #change group codes to lower
    df1.loc[:, 'group_code'] = df1['group_code'].str.lower()
    
    print(f'loaded estimate data {df1.shape} w/ the following groups:\n%s'%df1['group_code'].value_counts())
    
    #=======================================================================
    # load rooms info
    #=======================================================================
    rooms_df_raw = load_info_tab(info_fp, 'Rooms')
    
    
    
    """
    view(df_raw)
    
    """
    #clean up
    rooms_df = rooms_df_raw.rename(columns={'Floor (all lower case!)':'Floor'}
                               ).loc[:, ['Name', 'Floor', 'Type']]
                               
                               
    assert not rooms_df.isnull().any().any(), 'got some nulls in the Rooms info'
    rooms_df.columns = rooms_df.columns.str.lower()
    rooms_df.rename(columns={'name':'group_code'}, inplace=True)
    
    #add story
    rooms_df['story'] = rooms_df['floor'].apply(lambda x: floor_story_d.get(x, float('nan')))
    
    
    
    #===========================================================================
    # handle missing rooms
    #===========================================================================
    #check union
    gcodes_ser = pd.Series(df1['group_code'].str.lower().unique(), name='group_code')
    gcodes_df = gcodes_ser.to_frame().join(gcodes_ser.isin(rooms_df['group_code'].str.lower()).rename('match'))
    
 
    if not gcodes_df['match'].all():
        print(f'the following group codes failed to match\nsetting these to story=1:\n%s'%gcodes_df[~gcodes_df['match']])
        
        
        miss_df = gcodes_df[~gcodes_df['match']].loc[:, 'group_code'].reset_index(drop=True).to_frame()
        miss_df['floor']='main'
        miss_df['type'] = 'missing from info'
        miss_df['story']=0
        miss_df.columns.name=rooms_df.columns.name
        
        rooms_df = pd.concat([rooms_df, miss_df]).sort_values('story').reset_index(drop=True)
        
    else:
        miss_df=None
        
    rooms_df.loc[:, 'group_code'] = rooms_df['group_code'].str.lower()
    
    """
    view(rooms_df)
    view(miss_df)
    """
    
    #===========================================================================
    # join story
    #===========================================================================
    df1 = df1.join(rooms_df.loc[:, ['group_code', 'story']].set_index('group_code'), on='group_code')
    
    assert df1.notna().all().all()
    
    #===========================================================================
    # post
    #===========================================================================
    assert len(df1)==len(df_raw)
    
    df1 = df1.set_index(keys).sort_index().loc[:, ['rcv', 'story', 'desc']]
    
    #=======================================================================
    # write
    #=======================================================================
    if out_fp is None:
        out_fp= os.path.join(out_dir, os.path.splitext(os.path.basename(estimate_xls_fp))[0]+'.csv')
    
    """
    view(df1)
    df1.columns
    """
    print(f"Saving data to CSV\n    {out_fp}")
    df1.to_csv(out_fp, index=True)  # Save without row indices
    
    print("Conversion complete!")
    
    #=======================================================================
    # metadata
    #=======================================================================
    print("Creating metadata file...")
    
    # Get username (replace with your logic to get username)

    
    # Create metadata dictionary
    metadata = {
        "username": os.getenv('USERNAME'),
        "date": datetime.now().strftime("%Y-%m-%d"),  # Get current date
        "script_name": os.path.basename(__file__),  # Assuming script name
        "xls_filepath": estimate_xls_fp,
        "output_filepath": out_fp,
        "dataset_shape": df1.shape,  # Get data frame shape (rows, columns)
    }
    
    if not miss_df is None:
        metadata['missing_group_codes'] = str(miss_df['group_code'].tolist())
    
    # Write metadata to text file
    meta_ofp = os.path.join(os.path.dirname(out_fp), 'metadata.txt')
    with open(meta_ofp, "w") as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    print(f'wrote metadata to \n    {meta_ofp}')
    
    print('finished')
    
    return df1

 

def load_info_tab(fp, sectionName):

    df_raw = load_xls_with_pattern(fp)
    
    # Find start row of the section
    bx = df_raw.iloc[:, 0].str.lower() == sectionName.lower()
    assert bx.sum()==1, f'failed to get unique section name match for \'{sectionName}\''
    start_row = df_raw[bx].index[0] + 1 
    
    # Find end row (revised)
    next_section_rows = df_raw[start_row:][df_raw.iloc[:, 0].notna() & df_raw.iloc[:, 0].str.contains('^[A-Z]')].index
    end_row = next_section_rows.min() - 1 if next_section_rows.any() else df_raw.shape[0]

    # Extract section data (revised with dropna)
    df_section = df_raw.iloc[start_row:end_row, 1:].dropna(axis=1, how='all')
    
    # Promote first row to column names
    df_section.columns = df_section.iloc[0]
    df_section = df_section[1:].reset_index(drop=True)  # Drop the old header row
    df_section.columns.name = sectionName
    
    print(f'for \'Info\' section \'{sectionName}\' extracted {df_section.shape}')
    
    return df_section
    
    """
    view(df_section)
    """

 


def load_xls_with_pattern(xls_filepath, pattern="_info"):
    """Loads a sheet from an XLS file where the sheet name matches a pattern.

    Args:
        xls_filepath (str): The path to the XLS file.
        pattern (str, optional): The pattern to match sheet names. 
                                 Defaults to "*_info".

    Returns:
        pandas.DataFrame: The DataFrame containing the data from the matching sheet,
                          or None if no matching sheet is found.
    """

    excel_file = pd.ExcelFile(xls_filepath)
    
    for sheet_name in excel_file.sheet_names:
        if pattern in sheet_name:  # You might want a regex here for stricter matching
            df = pd.read_excel(xls_filepath, sheet_name=sheet_name)
            return df

    raise IOError(f"No sheet found matching the pattern '{pattern}'")



          

 



if __name__=="__main__":
    
    xls_to_csv(
        r'l:\09_REPOS\04_TOOLS\DDFP\example\R_1-L-BD-CU_ABCA\R_1-L-BD-CU_ABCA.xlsx',
        r'l:\09_REPOS\04_TOOLS\DDFP\example\R_1-L-BD-CU_ABCA\DDFwork_R_1-L-BD-CU_ABCA.xlsm',
        out_dir=r'l:\10_IO\CanCurve\misc\port_estimate'
        )
    