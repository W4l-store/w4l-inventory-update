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

from .retrieve_BS_sku_mapping import retrieve_BS_sku_mapping
from .sku_to_qtt_map_generator import sku_to_qtt_map_generator
from .helpers import a_ph


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gen_amz_inv_update_by_region( BS_export_df: pd.DataFrame, region: str,) -> pd.DataFrame:
    
    logger.info(f"Generating Amazon inventory update for region: {region}")


    # Validate the region
    allowed_regions = ['US', 'CA', 'MX']
    if region not in allowed_regions:
        logger.error(f"Invalid region: {region}")
        raise ValueError('Invalid region')

    # Generate required mappings
    BS_sku_to_qtt_map = sku_to_qtt_map_generator(BS_export_df) # {'BS_SKU': 'quantity'}
    BS_sku_mapping = retrieve_BS_sku_mapping(region) # {'seller_sku': 'BS_SKU'}

    # read resources/amazon/pack_of_map.json
    pack_of_map =  json.load(open(a_ph('/resources/amazon/pack_of_map.json'), 'r'))


    amz_sku_to_qtt_map: Dict[str, int] = {}
    BS_skus_not_found = set(BS_sku_mapping.values()) - set(BS_sku_to_qtt_map.keys())
    
    logger.warning(f"SKUs not found in Blue System export data: {len(BS_skus_not_found)}")


    for amz_sku, BS_sku in BS_sku_mapping.items():

        if BS_sku not in BS_sku_to_qtt_map:
            continue
        
        BS_qtt = BS_sku_to_qtt_map.get(BS_sku, 0)

        # Calculate quantity based on pack size
        if amz_sku in pack_of_map:
            qtt = BS_qtt // pack_of_map.get(amz_sku, 1)
        else:
            qtt = BS_qtt

        amz_sku_to_qtt_map[amz_sku] = qtt

    # Create a pandas DataFrame from the mapping
    amz_inv_update_df = pd.DataFrame(list(amz_sku_to_qtt_map.items()), columns=['sku', 'quantity'])
    
    logger.info(f"Generated inventory update data for {len(amz_inv_update_df)} SKUs")
    return amz_inv_update_df

def test ():
    BS_export_df = pd.read_csv('../resources/user_uploads/BS_stock.TXT', sep='\t', encoding='ascii', skiprows=2, dtype=str)
    region = 'US'
    result = gen_amz_inv_update_by_region(BS_export_df, region)
    print(result.head())



# test()