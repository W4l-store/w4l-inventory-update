"""
    Generate Amazon inventory update data for a specific region.

    Args:
        BS_export_df (pd.DataFrame): Blue System export data.
        region (str): The region code ('US', 'CA', or 'MX').
       

    Returns:
        pd.DataFrame: Amazon inventory update data with columns 'sku' and 'quantity'.

    Raises:
        ValueError: If an invalid region is provided.
    """

import pandas as pd
import logging
from typing import Dict
import json

from .BS_sku_to_qtt_map_generator import BS_sku_to_qtt_map_generator
from .helpers import a_ph, get_back_of_map_by_marketplace


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gen_amz_inv_update_by_region( BS_export_df: pd.DataFrame, region: str,) -> pd.DataFrame:
    
    logger.info(f"Generating Amazon inventory update for region: {region}")


    # Validate the region
    allowed_regions = ["PL", "FR", "SE", "US", "NL", "UK", "MX", "CA", "BE", "ES", "IT", "DE"]
    if region not in allowed_regions:
        logger.error(f"Invalid region: {region}")
        raise ValueError('Invalid region')

    # Generate required mappings
    BS_sku_to_qtt_map = BS_sku_to_qtt_map_generator(BS_export_df) # {'BS_SKU': 'quantity'}
    BS_sku_mapping = retrieve_BS_sku_mapping(region) # {'seller_sku': 'BS_SKU'}



    amz_sku_to_qtt_map: Dict[str, int] = {}
    BS_skus_not_found = set(BS_sku_mapping.values()) - set(BS_sku_to_qtt_map.keys())
    
    logger.warning(f"SKUs not found in Blue System export data: {len(BS_skus_not_found)}")


    for amz_sku, BS_sku in BS_sku_mapping.items():

        if BS_sku not in BS_sku_to_qtt_map:
            continue
        
        BS_qtt = BS_sku_to_qtt_map.get(BS_sku, 0)

        amz_sku_to_qtt_map[amz_sku] = BS_qtt
    
    # apply the pack of map to the amz_sku_to_qtt_map
    pack_of_map =  get_back_of_map_by_marketplace('amazon')
    for amz_sku, pack_of in pack_of_map.items():
        if amz_sku in amz_sku_to_qtt_map:
            amz_sku_to_qtt_map[amz_sku] = amz_sku_to_qtt_map[amz_sku] // pack_of


    # Create a pandas DataFrame from the mapping
    amz_inv_update_df = pd.DataFrame(list(amz_sku_to_qtt_map.items()), columns=['sku', 'quantity'])
    
    logger.info(f"Generated inventory update data for {len(amz_inv_update_df)} SKUs")
    return amz_inv_update_df

def test ():
    BS_export_df = pd.read_csv('../resources/user_uploads/BS_stock.TXT', sep='\t', encoding='ascii', skiprows=2, dtype=str)
    region = 'US'
    result = gen_amz_inv_update_by_region(BS_export_df, region)
    print(result.head())





def retrieve_BS_sku_mapping(region, statuses_allowed=['Active', 'Inactive','Incomplete']):

    allowed_values = ["PL", "FR", "SE", "US", "NL", "UK", "MX", "CA", "BE", "ES", "IT", "DE"]
    if region not in allowed_values:
        raise ValueError(f"Invalid region '{region}'. Allowed values are {allowed_values}.")
    
    status_column = f'status_{region}'
    fulfillment = f'fulfillment_{region}'



    source_df = pd.read_csv(a_ph('/resources/amazon/amz_sku_mapping.csv'), dtype=str)
    
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
