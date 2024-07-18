
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging


def retrieve_BS_sku_mapping(region, statuses_allowed=['Active', 'Inactive','Incomplete']):

    allowed_values = ['US', 'CA', 'MX']
    if region not in allowed_values:
        raise ValueError(f"Invalid region '{region}'. Allowed values are {allowed_values}.")
    
    status_column = f'status_{region}'
    fulfillment = f'fulfillment_{region}'



    source_df = pd.read_csv('../resources/amazon/BS_SKU_mapping/NA_mapping/amz_NA_mapping.csv', dtype=str)
    
    # filter the empty status columns
    source_df = source_df[source_df[status_column].notna()]
    source_df = source_df[source_df[status_column] != '']
    source_df = source_df[source_df[status_column].isin(statuses_allowed)]
    # filter the BS_SKU columns from nan and empty values
    source_df = source_df[source_df['BS_SKU'].notna()]
    source_df = source_df[source_df['BS_SKU'] != '']
    # filter the fulfillment column to only "DEFAULT" values
    source_df = source_df[source_df[fulfillment] == 'DEFAULT']

    # to dict map
    amazon_sku_to_BS_sku = dict(zip(source_df['seller_sku'], source_df['BS_SKU']))
    
    return amazon_sku_to_BS_sku

