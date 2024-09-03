import os
from flask import current_app
import time
import glob
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)


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
    


def get_back_of_map_by_marketplace(marketplace: str) -> dict:
    #amazon_sku	amazon_delimiter	walmart_sku	walmart_delimiter	wayfair_sku	wayfair_delimiter	houzz_sku	houzz_delimiter
    supported_marketplaces = ['amazon', 'walmart', 'wayfair', 'houzz']
    if marketplace not in supported_marketplaces:
        raise ValueError(f"Invalid marketplace: {marketplace}")
    # resources/pack_of_map.csv
    pack_of_map = pd.read_csv(a_ph('/resources/pack_of_map.csv'),dtype=str )
    pack_of_map = pack_of_map[[f'{marketplace}_sku', f'{marketplace}_delimiter']]
    # drop na values
    pack_of_map = pack_of_map.dropna()

    pack_of_map[f'{marketplace}_delimiter'] = pack_of_map[f'{marketplace}_delimiter'].astype(int)
    pack_of_map_dict = pack_of_map.set_index(f'{marketplace}_sku').to_dict()[f'{marketplace}_delimiter']
    return pack_of_map_dict

# приминить pack_of_map by marketplace
def apply_pack_of_map(sku_to_qtt_map, marketplace):
    pack_of_map = get_back_of_map_by_marketplace(marketplace)
    for amz_sku, pack_of in pack_of_map.items():
        if amz_sku in sku_to_qtt_map:
            sku_to_qtt_map[amz_sku] = sku_to_qtt_map[amz_sku] // pack_of
    return sku_to_qtt_map

def set_processing_status(status, logs=None, result=None):
    try:
        with open(a_ph('processing_status.json'), 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {}  # If file is empty or corrupt, start with empty dict
    
    data["state"] = status
    if result:
        data["result"] = result
    if logs:
        if "logs" not in data:
            data["logs"] = []
        data["logs"].extend(logs)  # Append new logs instead of overwriting
    
    with open(a_ph('processing_status.json'), 'w') as f:
        json.dump(data, f, ensure_ascii=False, default=str)

def get_processing_status():
    with open(a_ph('processing_status.json'), 'r') as f:
        data = json.load(f)
    return data

def clear_processing_logs():
    with open(a_ph('processing_status.json'), 'r') as f:
        data = json.load(f)
    data["logs"] = []
    with open(a_ph('processing_status.json'), 'w') as f:
        json.dump(data, f)

def append_to_processing_logs(log_entry):
    with open(a_ph('processing_status.json'), 'r') as f:
        data = json.load(f)
    if "logs" not in data:
        data["logs"] = []
    data["logs"].append(log_entry)
    with open(a_ph('processing_status.json'), 'w') as f:
        json.dump(data, f, ensure_ascii=False, default=str)