import pandas as pd
import logging
from typing import Dict

from .BS_sku_to_qtt_map_generator import BS_sku_to_qtt_map_generator
from .helpers import a_ph, apply_pack_of_map

logger = logging.getLogger(__name__)

def gen_houzz_inv_update(BS_export_df: pd.DataFrame) -> pd.DataFrame:
    
    logger.info("Generating Houzz inventory update")

    # Generate required mappings
    BS_sku_to_qtt_map = BS_sku_to_qtt_map_generator(BS_export_df) # {'BS_SKU': 'quantity'}
    houzz_sku_mapping = retrieve_houzz_sku_mapping() # {'seller_sku': 'BS_SKU'}

    houzz_sku_to_qtt_map: Dict[str, int] = {}
    BS_skus_not_found = set(houzz_sku_mapping.values()) - set(BS_sku_to_qtt_map.keys())
    
    logger.warning(f"SKUs not found in Blue System export data: {len(BS_skus_not_found)}")

    for houzz_sku, BS_sku in houzz_sku_mapping.items():
        if BS_sku not in BS_sku_to_qtt_map:
            continue
        
        BS_qtt = BS_sku_to_qtt_map.get(BS_sku, 0)

        houzz_sku_to_qtt_map[houzz_sku] = BS_qtt
    
    # apply the pack of map to the houzz_sku_to_qtt_map
    
    houzz_sku_to_qtt_map = apply_pack_of_map(houzz_sku_to_qtt_map, 'houzz')

    # Create a pandas DataFrame from the mapping
    houzz_inv_update_df = pd.DataFrame(list(houzz_sku_to_qtt_map.items()), columns=['SKU', 'Quantity'])

    logger.info(f"Generated inventory update data for {len(houzz_inv_update_df)} SKUs")
    return houzz_inv_update_df

def retrieve_houzz_sku_mapping():
    source_df = pd.read_csv(a_ph('/resources/houzz/houzz_sku_mapping.csv'), dtype=str)
    
    # filter the empty BS_SKU columns
    source_df = source_df[source_df['BS_SKU'].notna()]
    source_df = source_df[source_df['BS_SKU'] != '']

    # to dict map
    houzz_sku_to_BS_sku = dict(zip(source_df['seller_sku'], source_df['BS_SKU']))
    
    return houzz_sku_to_BS_sku
