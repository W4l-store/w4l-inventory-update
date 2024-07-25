import pandas as pd
import logging
from typing import Dict
import json

from .BS_sku_to_qtt_map_generator import BS_sku_to_qtt_map_generator
from .helpers import a_ph, apply_pack_of_map

# Set up logging

logger = logging.getLogger(__name__)

def gen_wayfair_inv_update_by_region(BS_export_df: pd.DataFrame, region: str) -> pd.DataFrame:
    
    logger.info(f"Generating Wayfair inventory update for region: {region}")

    # Validate the region
    allowed_regions = ["US", "CA"]
    if region not in allowed_regions:
        logger.error(f"Invalid region: {region}")
        raise ValueError('Invalid region')

    # Generate required mappings
    BS_sku_to_qtt_map = BS_sku_to_qtt_map_generator(BS_export_df) # {'BS_SKU': 'quantity'}
    BS_sku_mapping = retrieve_wayfair_sku_mapping(region) # {'seller_sku': 'BS_SKU'}


    wayfair_sku_to_qtt_map: Dict[str, int] = {}
    BS_skus_not_found = set(BS_sku_mapping.values()) - set(BS_sku_to_qtt_map.keys())
    
    logger.warning(f"SKUs not found in Blue System export data: {len(BS_skus_not_found)}")

    for wayfair_sku, BS_sku in BS_sku_mapping.items():
        if BS_sku not in BS_sku_to_qtt_map:
            continue
        
        BS_qtt = BS_sku_to_qtt_map.get(BS_sku, 0)

        wayfair_sku_to_qtt_map[wayfair_sku] = BS_qtt
    
    # apply the pack of map to the wayfair_sku_to_qtt_map
    
    wayfair_sku_to_qtt_map = apply_pack_of_map(wayfair_sku_to_qtt_map, 'wayfair')

    # Create a pandas DataFrame from the mapping
    wayfair_inv_update_df = pd.DataFrame(list(wayfair_sku_to_qtt_map.items()), columns=['Supplier Part#', 'In Stock'])

    if region == 'US':
        wayfair_inv_update_df['Supplier ID'] = '217667'
    elif region == 'CA':
        wayfair_inv_update_df['Supplier ID'] = '100778'
    wayfair_inv_update_df = wayfair_inv_update_df[['Supplier ID', 'Supplier Part#', 'In Stock']]
    
    logger.info(f"Generated inventory update data for {len(wayfair_inv_update_df)} SKUs")
    return wayfair_inv_update_df

def retrieve_wayfair_sku_mapping(region):
    allowed_values = ["US", "CA"]
    if region not in allowed_values:
        raise ValueError(f"Invalid region '{region}'. Allowed values are {allowed_values}.")
    
    supplier_id_column = f'Supplier_ID_{region}'

    source_df = pd.read_csv(a_ph('/resources/wayfair/wayfair_sku_mapping.csv'), dtype=str)
    
    # filter the empty Supplier_ID columns
    source_df = source_df[source_df[supplier_id_column].notna()]
    source_df = source_df[source_df[supplier_id_column] != '']
    # filter the BS_SKU columns from nan and empty values
    source_df = source_df[source_df['BS_SKU'].notna()]
    source_df = source_df[source_df['BS_SKU'] != '']

    # to dict map
    wayfair_sku_to_BS_sku = dict(zip(source_df['seller_sku'], source_df['BS_SKU']))
    
    return wayfair_sku_to_BS_sku

