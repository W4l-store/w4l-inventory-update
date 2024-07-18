
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_resources():
    update_amz_NA_mapping()



def update_amz_NA_mapping():
    logging.info('Starting update_amz_NA_mapping function')
    folder_path = '../resources/amazon/BS_SKU_mapping/NA_mapping'

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("../credentials/sheets_api_cred.json", scopes=scopes)
    client = gspread.authorize(creds)

    sheet_id = "1ZMzIMn7CzV_tUJSfXguHYLh3fkkgHVh_0u2NBWCzEAQ"
    workbook = client.open_by_key(sheet_id)

    worksheet_list = map(lambda x: x.title, workbook.worksheets())
    source_worksheet_name = "final_NA_mapping"
    
    if source_worksheet_name not in worksheet_list:
        logging.error(f"Worksheet {source_worksheet_name} not found in the google sheet")
        raise ValueError(f"Worksheet {source_worksheet_name} not found in the google sheet")
    # get the worksheet to df 
    source_worksheet = workbook.worksheet(source_worksheet_name)
    records = source_worksheet.get_all_records()
    source_df = pd.DataFrame(records, dtype=str)
    source_df.to_csv(f'{folder_path}/amz_NA_mapping.csv', index=False)
    logging.info('Finished update_amz_NA_mapping function')

# test run 
def test():
    update_resources()

test()



