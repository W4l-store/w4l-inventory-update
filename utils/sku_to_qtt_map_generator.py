import pandas as pd
import logging

def BS_file_to_QT_map(BS_export_df, use_prod_type=False):
    # Select only needed columns and rename them
    BS_export_df = BS_export_df[['CODE', 'NAME', 'AVAIL', 'PROD TYPE']].rename(
        columns={'CODE': 'SKU'}
    )
    
    # Strip whitespace from string columns
    BS_export_df = BS_export_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Clean 'PROD TYPE' by removing "     00"
    BS_export_df['PROD TYPE'] = BS_export_df['PROD TYPE'].str.replace(" 00", "", regex=False).str.strip()


    # Convert 'AVAIL' to numeric, replacing non-numeric values with NaN
    BS_export_df['AVAIL'] = BS_export_df['AVAIL'].astype(int)
    
    # Replace NaN values with 0
    BS_export_df['AVAIL'] = BS_export_df['AVAIL'].fillna(0)
    
    
    # Create base dictionary mapping SKU to AVAIL
    sku_avail_map = dict(zip(BS_export_df['SKU'], BS_export_df['AVAIL']))
    
    if use_prod_type:
            # Filter DataFrame for related products
            mask = (BS_export_df['PROD TYPE'] != '') & (BS_export_df['AVAIL'] > 0)
            related_df = BS_export_df.loc[mask, ['SKU', 'AVAIL', 'PROD TYPE']]
            
            # Drop rows where 'PROD TYPE' is NaN
            related_df = related_df.dropna(subset=['PROD TYPE'])

            # Create dictionary mapping PROD TYPE to AVAIL
            prod_type_avail_map = dict(zip(related_df['PROD TYPE'], related_df['AVAIL']))


        
            
            # Update sku_avail_map for items with zero availability
            skus_for_update = [sku for sku, avail in sku_avail_map.items() if avail <= 0]
            
            # filter skus for update in prod_type_avail_map
            skus_for_update = [sku for sku in skus_for_update if sku in prod_type_avail_map.keys()]

            for sku in skus_for_update:
                sku_avail_map[sku] = prod_type_avail_map[sku]

    return sku_avail_map

