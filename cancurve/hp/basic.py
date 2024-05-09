'''
Created on Apr. 15, 2024

@author: cef
'''

import os, logging
import pandas as pd

def view_web_df(df):
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)
    import webbrowser
    #import pandas as pd
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(delete=False, suffix='.html', mode='w') as f:
        #type(f)
        df.to_html(buf=f)
        
    webbrowser.open(f.name)
    
    

def find_single_file_by_extension(directory, extension):
    """
    Searches a directory for a single file matching the provided extension.

    Args:
        directory: The directory to search in.
        extension: The file extension to search for (e.g., '.txt').

    Returns:
        The full path of the matching file.

    Raises:
        FileNotFoundError: If no matching file is found.
        ValueError: If multiple matching files are found.
    """
    assert os.path.exists(directory), directory
    matching_files = [f for f in os.listdir(directory) if f.endswith(extension)]

    if len(matching_files) == 0:
        raise FileNotFoundError(f"No files with extension '{extension}' found in '{directory}'")
    elif len(matching_files) > 1:
        raise ValueError(f"Multiple files with extension '{extension}' found in '{directory}'")

    return os.path.join(directory, matching_files[0])



def convert_to_bool(value):
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
    return value  # Keep other values as they are



def convert_to_number(text):
    """
    Attempts to convert a string to a number (int or float) if possible.
    
    Args:
        text: The string to convert.
    
    Returns:
        The converted number (int or float) if successful, original otherwise.
    """
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text
        

def convert_to_float(text): 
    try:
        return float(text)
    except ValueError:
        return text
        
def force_open_dir(folder_path_raw, logger=None): #force explorer to open a folder
    
    if logger is None: logger= logging.getLogger()
 
    
    if not os.path.exists(folder_path_raw):
        logger.error('passed directory does not exist: \n    %s'%folder_path_raw)
        return False
        
    import subprocess
    
    #===========================================================================
    # convert directory to raw string literal for windows
    #===========================================================================
    try:
        #convert forward to backslashes
        folder_path=  folder_path_raw.replace('/', '\\')
    except:
        logger.error('failed during string conversion')
        return False
    
    try:

        args = r'explorer "' + str(folder_path) + '"'
        with subprocess.Popen(args) as p: #spawn process in explorer
            pass
 
        logger.info('forced open folder: \n    %s'%folder_path)
        return True
    except:
        logger.error('unable to open directory: \n %s'%dir)
        return False
