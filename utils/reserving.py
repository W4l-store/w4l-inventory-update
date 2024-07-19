
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
from .helpers import a_ph
import os
import json
import time
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .update_resources import get_workbook, get_worksheet_df_by_name
from .BS_sku_to_qtt_map_generator import stabilize_BS_df

def update_bluesistem_resources():
    update_all_BS_sku_reserve()


def update_all_BS_sku_reserve():

    bs_all_sku_reserve_local = pd.read_csv(a_ph('resources/reserve/blue_system/BS_all_sku_reserve.csv'))
    BS_export_df = stabilize_BS_df(pd.read_csv(a_ph('resources/user_uploads/BS_stock.TXT'), sep='\t', encoding='ascii', skiprows=2, dtype=str))
    BS_export_df = BS_export_df[['SKU', 'NAME', 'PROD TYPE' ]]
    # find rows in BS_export_df that are not in bs_all_sku_reserve_local
    new_rows = BS_export_df[~BS_export_df['SKU'].isin(bs_all_sku_reserve_local['SKU'])]

    if new_rows.empty:
        logger.info('No new BS sku found')
    else:
        logger.info(f'Found {len(new_rows)} new BS sku')
        # save to local file
        pd.concat([bs_all_sku_reserve_local, new_rows]).to_csv(a_ph('resources/reserve/blue_system/BS_all_sku_reserve.csv'), index=False)
        workbook = get_workbook()#'BS_all_sku_reserve'
        worksheet = get_worksheet_df_by_name(get_workbook(), 'BS_all_sku_reserve')
        
        
        update_sheet_in_chunks(worksheet, new_rows, continue_from_end=True, start_row= bs_all_sku_reserve_local.shape[0] + 1  )




def update_sheet_in_chunks(worksheet, df, chunk_size=2000, continue_from_end=False, start_row=0):
    try:
        logger.info(f'Updating google sheet "{worksheet }" in chunks')
        header = worksheet.row_values(1)
        df_coloumns_list = df.columns.values.tolist()

        if not continue_from_end:
            worksheet.clear()
            start_row = 0
        else:
            if header != df_coloumns_list:
                logger.error(f'updating google sheet "{worksheet}" Header mismatch: {header} != {df_coloumns_list}')
                raise Exception(f'updating google sheet "{worksheet}" Header mismatch: {header} != {df_coloumns_list}')
                
        worksheet_length = worksheet.row_count
        df_columns_length = len(df.columns)

        ensure_sheet_size(worksheet, worksheet_length + len(df),df_columns_length )

        df_list = df_to_sheet_list(df, header= not continue_from_end)
         
        for i in range(start_row, len(df_list) + start_row, chunk_size):
            chunk = df_list[i:i+chunk_size]
            range_name = f'A{i+1}:{column_number_to_letter(df_columns_length)}{i+len(chunk)}'
            logger.info(f'Updating chunk {range_name}')

            worksheet.update(chunk, range_name)
            # add timout to avoid google api rate limit
            time.sleep(0.3)
    except Exception as e:
        logger.error(f'Error updating sheet in chunks: {str(e)}')


def ensure_sheet_size(worksheet, required_rows, required_cols):
    current_rows = worksheet.row_count
    current_cols = worksheet.col_count

    if required_rows > current_rows or required_cols > current_cols:
        new_rows = max(required_rows, current_rows)
        new_cols = max(required_cols, current_cols)
        worksheet.resize(new_rows, new_cols)

def df_to_sheet_list(df, header=True):
    df =df.fillna('')
    df = df.replace({pd.NA: ''})
    df = df.replace({'nan': ''})
    if header:
        df = [df.columns.values.tolist()] + df.values.tolist()
    else:
        df = df.values.tolist()
    return df

def column_number_to_letter(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string