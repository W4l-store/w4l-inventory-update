
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
from .helpers import a_ph
import os
import json


logger = logging.getLogger(__name__)

from dotenv import load_dotenv

amz_sku_mapping_worksheet_name = "amazon_sku_mapping"
update_double_roles_map_worksheet_name = "double_roles_map"
wayfair_sku_mapping_worksheet_name = "wayfair_sku_mapping"
walmart_sku_mapping_worksheet_name = "walmart_sku_mapping"
houzz_sku_mapping_worksheet_name = "houzz_sku_mapping"
BS_qty_overwrite_map = "BS_qty_overwrite_map"


def update_resources():
    logger.info("Updating resources")
    update_from_google_sheet()
    logger.info("Resources updated ")

def update_from_google_sheet():
   
    try:
        workbook = get_workbook()    
        
        update_amz_sku_mapping(workbook)
        update_double_roles_map(workbook)
        update_wayfair_sku_mapping(workbook)
        update_walmart_sku_mapping(workbook)
        update_houzz_sku_mapping(workbook)
        update_pack_of_map(workbook)
        update_BS_qty_overwrite_map(workbook)
    except Exception as e: 
        logger.error(f"Error in updating resources from google sheet {e}")
        raise e




def update_amz_sku_mapping(workbook):
    mapping_df = pd.DataFrame(get_worksheet_df_by_name(workbook, amz_sku_mapping_worksheet_name).get_all_records())
    mapping_df.to_csv(os.path.join(a_ph('/resources/amazon'), 'amz_sku_mapping.csv'), index=False)
    logger.info("Updated amazon - blue system mapping")

def update_wayfair_sku_mapping(workbook):
    mapping_df = pd.DataFrame(get_worksheet_df_by_name(workbook, wayfair_sku_mapping_worksheet_name).get_all_records())
    mapping_df.to_csv(os.path.join(a_ph('/resources/wayfair'), 'wayfair_sku_mapping.csv'), index=False)
    logger.info("Updated wayfair - blue system mapping")

def update_walmart_sku_mapping(workbook):
    mapping_df = pd.DataFrame(get_worksheet_df_by_name(workbook, walmart_sku_mapping_worksheet_name).get_all_records())
    mapping_df.to_csv(os.path.join(a_ph('/resources/walmart'), 'walmart_sku_mapping.csv'), index=False)
    logger.info("Updated walmart - blue system mapping")

def update_houzz_sku_mapping(workbook):
    mapping_df = pd.DataFrame(get_worksheet_df_by_name(workbook, houzz_sku_mapping_worksheet_name).get_all_records())
    mapping_df.to_csv(os.path.join(a_ph('/resources/houzz'), 'houzz_sku_mapping.csv'), index=False)
    logger.info("Updated houzz - blue system mapping")

def update_pack_of_map(workbook):
    pack_of_map_df = pd.DataFrame(get_worksheet_df_by_name(workbook, "pack_of_map").get_all_records())
    pack_of_map_df.to_csv(os.path.join(a_ph('/resources/'), 'pack_of_map.csv'), index=False)
    logger.info("Updated pack of map")

def update_double_roles_map(workbook):
    update_double_roles_map_df = pd.DataFrame(get_worksheet_df_by_name(workbook, update_double_roles_map_worksheet_name).get_all_records())
    double_roles_map = dict(zip(update_double_roles_map_df['NAME'].str.strip(), update_double_roles_map_df['delimiter'].astype(int)))
    with open(a_ph('/resources/blue_system/double_roles_map.json'), 'w') as f:
        json.dump(double_roles_map, f)
    logger.info("Updated double roles map")

def update_BS_qty_overwrite_map(workbook):
    mapping_df = pd.DataFrame(get_worksheet_df_by_name(workbook, BS_qty_overwrite_map).get_all_records())
    overwrite_dict = dict(zip(mapping_df['BS_SKU'], mapping_df['Overwrite_Quantity']))
    with open(a_ph('/resources/blue_system/BS_qty_overwrite_map.json'), 'w') as f:
        json.dump(overwrite_dict, f)
    logger.info("Updated BS qty overwrite map")


def get_workbook(sheet_id = "1ZMzIMn7CzV_tUJSfXguHYLh3fkkgHVh_0u2NBWCzEAQ"):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = get_sheets_api_credentials()
    client = gspread.authorize(creds)
    workbook = client.open_by_key(sheet_id)
    return workbook


def get_sheets_api_credentials():
    # Load environment variables
    load_dotenv(override=True)
    logger.info("Getting google sheets api credentials")
    # Create a dictionary with the credentials
    cred_dict = {
        "type": "service_account",
        "project_id": "w4l-inventory-update",
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY"),   
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        "universe_domain": "googleapis.com"
    }

    # Create a temporary file to store the credentials
    temp_cred_file = a_ph('temp_credentials.json')
    # if temp_cred_file is exist delate it first 
    if os.path.exists(temp_cred_file):
        os.remove(temp_cred_file)
        logger.info("Deleted the existing temp_cred_file")

    with open(temp_cred_file, 'w') as f:
        json.dump(cred_dict, f)
        logger.info("Created the temp_cred_file")


    # Get the credentials from the temporary file
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    
    creds = Credentials.from_service_account_file(temp_cred_file, scopes=scopes)

    # Remove the temporary file
    os.remove(temp_cred_file)

    return creds




def get_worksheet_df_by_name(workbook,worksheet_name):

    worksheet_list = map(lambda x: x.title, workbook.worksheets())
    if worksheet_name not in worksheet_list:
        logging.error(f"Worksheet {worksheet_name} not found in the google sheet")
        raise ValueError(f"Worksheet {worksheet_name} not found in the google sheet")
    # get the worksheet to df 
    return workbook.worksheet(worksheet_name)



def update_BS_all_sku_reserve_local():
    BS_all_sku_reserve = "BS_all_sku_reserve"
    workbook = get_workbook()
    mapping_df = pd.DataFrame(get_worksheet_df_by_name(workbook, BS_all_sku_reserve).get_all_records())
    mapping_df.to_csv(os.path.join(a_ph('resources/reserve/blue_system/BS_all_sku_reserve.csv'), 'BS_all_sku_reserve.csv'), index=False)



# test run 
def test():
    update_resources()

# test()



