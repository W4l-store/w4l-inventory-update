import os
from flask import current_app

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
