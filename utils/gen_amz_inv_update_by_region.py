# this function accepts regions, blue system df, and generates a pandas object what contains amazon inventory update data with colomns: 'sku','quantity'

# import necessary libraries
import pandas as pd
import sku_to_qtt_map_generator as sku_to_qtt_map_generator
import retrieve_BS_sku_mapping as retrieve_BS_sku_mapping
import retrieve_pack_of_map as retrieve_pack_of_map
import logging

def gen_amz_inv_update_by_region(region, BS_export_df):
    logger = logging.getLogger(__name__)

    allowed_regions = ['US', 'CA', 'MX']
    if region not in allowed_regions:
        raise ValueError('Invalid region')
    BS_sku_to_qtt_map = sku_to_qtt_map_generator(BS_export_df)
    BS_sku_mapping = retrieve_BS_sku_mapping(region)
    pack_of_map = retrieve_pack_of_map(region)

    amz_sku_to_qtt_map = {}
    for amz_sku , BS_sku in BS_sku_mapping.items():
        qtt = 0
        if BS_sku not in amz_sku_to_qtt_map:
            logging.warn(f"SKU {BS_sku} not found in BS export file")
            continue
            
        BS_qtt = BS_sku_to_qtt_map.get(BS_sku)

        if amz_sku in pack_of_map:
            qtt = BS_qtt // pack_of_map.get(amz_sku)
        else:
            qtt = BS_qtt
        amz_sku_to_qtt_map[amz_sku] = qtt
    # create a pandas object 
    amz_inv_update_df = pd.DataFrame(list(amz_sku_to_qtt_map.items()), columns=['sku', 'quantity'])
    return amz_inv_update_df
        

          