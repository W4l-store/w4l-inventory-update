import pandas as pd
import logging

logger = logging.getLogger(__name__)
def BS_sku_to_qtt_map_generator(BS_export_df, use_prod_type=False):
    
    try:
        # Select only needed columns and rename them
        BS_export_df = BS_export_df[['CODE', 'NAME', 'AVAIL', 'PROD TYPE']].rename(
            columns={'CODE': 'SKU'}
        )
        
        # Strip whitespace from string columns
        BS_export_df = BS_export_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        # Clean 'PROD TYPE' by removing "     00"
        BS_export_df['PROD TYPE'] = BS_export_df['PROD TYPE'].str.replace(" 00", "", regex=False).str.strip()

        # Convert 'AVAIL' to numeric, replacing non-numeric values with NaN
        BS_export_df['AVAIL'] = pd.to_numeric(BS_export_df['AVAIL'], errors='coerce')
        
        # Replace NaN values with 0
        BS_export_df['AVAIL'] = BS_export_df['AVAIL'].fillna(0)

        # replace negative values with 0
        BS_export_df['AVAIL'] = BS_export_df['AVAIL'].apply(lambda x: 0 if x < 0 else x)
        
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
        
        logger.info(f"Successfully created SKU to quantity map with {len(sku_avail_map)} entries")
        return sku_avail_map
    
    except KeyError as e:
        logger.error(f"Required column missing from input DataFrame: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing the BS file: {e}")
        raise

