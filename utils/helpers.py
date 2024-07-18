import os
from flask import current_app
import time
import glob

def a_ph(relative_path):
    """
    Creates an absolute path based on the relative path from the project root.
    
    :param relative_path: Relative path from the project root
    :return: Absolute path
    """
    if current_app:
        # If the function is called within the context of a Flask application
        root_path = current_app.root_path
    else:
        # If the function is called outside the context of a Flask application
        # Get the parent directory of the directory containing this file
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Join the root path with the relative path, removing any leading '/'
    return os.path.join(root_path, relative_path.lstrip('/'))

# Example usage:
# print(a_ph('config/settings.json'))
# print(a_ph('/static/images/logo.png'))

def is_inv_updated_today():
    # gen name of the download/update_files_07_18_24.zip 
    # extract the date from the name
    # check if the date is today
    # return True or False

    zip_files = glob.glob(a_ph('/download/*.zip'))
    if not zip_files:
        return False
    else:
        zip_file = os.path.basename(zip_files[0])
        date_str = zip_file.replace('update_files_', '').replace('.zip', '')
        today = time.strftime('%m_%d_%y')
        return date_str == today
    

def test ():
    print(is_inv_updated_today())
    
# test()
    
    