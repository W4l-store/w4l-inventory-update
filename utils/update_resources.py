
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
from .helpers import a_ph
import os
import json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_resources():
    update_from_google_sheet()

def update_from_google_sheet():
    amz_NA_mapping_worksheet_name = "final_NA_mapping"
    update_double_roles_map_worksheet_name = "double_roles_map"


 
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(a_ph("credentials/sheets_api_cred.json"), scopes=scopes)
    client = gspread.authorize(creds)

    sheet_id = "1ZMzIMn7CzV_tUJSfXguHYLh3fkkgHVh_0u2NBWCzEAQ"
    workbook = client.open_by_key(sheet_id)

    worksheet_list = map(lambda x: x.title, workbook.worksheets())
    
    if amz_NA_mapping_worksheet_name not in worksheet_list:
        logging.error(f"Worksheet {amz_NA_mapping_worksheet_name} not found in the google sheet")
        raise ValueError(f"Worksheet {amz_NA_mapping_worksheet_name} not found in the google sheet")
    # get the worksheet to df 
    amz_NA_mapping_df = pd.DataFrame(workbook.worksheet(amz_NA_mapping_worksheet_name).get_all_records())
    
    update_amz_NA_mapping(amz_NA_mapping_df)

    if update_double_roles_map_worksheet_name not in worksheet_list:
        logging.error(f"Worksheet {update_double_roles_map_worksheet_name} not found in the google sheet")
        raise ValueError(f"Worksheet {update_double_roles_map_worksheet_name} not found in the google sheet")

    update_double_roles_map_df = pd.DataFrame(workbook.worksheet(update_double_roles_map_worksheet_name).get_all_records())
    update_double_roles_map(update_double_roles_map_df)





def update_amz_NA_mapping(amz_NA_mapping_df: pd.DataFrame):
   
    amz_NA_mapping_df.to_csv(os.path.join(a_ph('/resources/amazon/BS_SKU_mapping/NA_mapping'), 'amz_NA_mapping.csv'), index=False)
    logger.info("Updated NA mapping")

def update_double_roles_map(update_double_roles_map_df):
    #resources/blue_sistem/double_roles_map.json
    double_roles_map = dict(zip(update_double_roles_map_df['NAME'].str.strip(), update_double_roles_map_df['delimiter'].astype(int)))
    with open(a_ph('/resources/blue_sistem/double_roles_map.json'), 'w') as f:
        json.dump(double_roles_map, f)
    logger.info("Updated double roles map")


# test run 
def test():
    update_resources()

# test()



