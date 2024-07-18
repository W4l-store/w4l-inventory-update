
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging


def retrieve_BS_sku_mapping(region, use_local=False, statuses_allowed=['Active', 'Inactive','Incomplete']):

    allowed_values = ['US', 'CA', 'MX']
    if region not in allowed_values:
        raise ValueError(f"Invalid region '{region}'. Allowed values are {allowed_values}.")
    
    status_column = f'status_{region}'


    if use_local:
        source_df = pd.read_csv('preparing/data/all_listings_mapping_NA.csv', dtype=str)
    else:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("../credentials/sheets_api_cred.json", scopes=scopes)
        client = gspread.authorize(creds)

        sheet_id = "1ZMzIMn7CzV_tUJSfXguHYLh3fkkgHVh_0u2NBWCzEAQ"
        workbook = client.open_by_key(sheet_id)

        worksheet_list = map(lambda x: x.title, workbook.worksheets())
        source_worksheet_name = "final_NA_mapping"
        
        if source_worksheet_name not in worksheet_list:
            raise ValueError(f"Worksheet {source_worksheet_name} not found in the google sheet")
        # get the worksheet to df 
        source_worksheet = workbook.worksheet(source_worksheet_name)
        records = source_worksheet.get_all_records()
        # print(records)
        source_df = pd.DataFrame(records, dtype=str)
    # filter the empty status columns
    source_df = source_df[source_df[status_column].notna()]
    source_df = source_df[source_df[status_column] != '']
    source_df = source_df[source_df[status_column].isin(statuses_allowed)]
    # filter the BS_SKU columns from nan and empty values
    source_df = source_df[source_df['BS_SKU'].notna()]
    source_df = source_df[source_df['BS_SKU'] != '']
    # to dict map
    amazon_sku_to_BS_sku = dict(zip(source_df['seller_sku'], source_df['BS_SKU']))
    
    return amazon_sku_to_BS_sku

