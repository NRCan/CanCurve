'''
Created on Apr. 15, 2024

@author: cef
'''

import os
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
    assert os.path.exists(directory)
    matching_files = [f for f in os.listdir(directory) if f.endswith(extension)]

    if len(matching_files) == 0:
        raise FileNotFoundError(f"No files with extension '{extension}' found in '{directory}'")
    elif len(matching_files) > 1:
        raise ValueError(f"Multiple files with extension '{extension}' found in '{directory}'")

    return os.path.join(directory, matching_files[0])