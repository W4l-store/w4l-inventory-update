# utils/generate_amazon_inv_update_files.py

import pandas as pd
import logging
import os 
import zipfile
import time 
import glob

from .gen_amz_inv_update_by_region import gen_amz_inv_update_by_region
from .update_resources import update_resources
from .helpers import a_ph

logger = logging.getLogger(__name__)

amazon_regions = ["PL", "FR", "SE", "US", "NL", "UK", "MX", "CA", "BE", "ES", "IT", "DE"]

def generate_inv_update_files(BS_export_df: pd.DataFrame) -> None:
    try:
        update_resources() 
        # delete old ZIP file
        zip_files = glob.glob(a_ph('/download/*.zip'))

        for zip_file in zip_files:
            os.remove(zip_file)
            logger.info(f"Deleted {zip_file}")

        # Create a ZIP file add time stamp
        today = time.strftime('%m_%d_%y')
        zip_filename = f'update_files_{ today }.zip'
        os.makedirs(a_ph('download'), exist_ok=True)
        with zipfile.ZipFile(os.path.join( a_ph('download'), zip_filename), 'w') as zipf:
            # Generate update files for each Amazon region
            for region in amazon_regions:
                update_df = gen_amz_inv_update_by_region(BS_export_df, region)
                
                # Create the folder structure
                folder_path = f'Amazon/'
                os.makedirs(folder_path, exist_ok=True)
                
                # Generate the filename
                filename = f'amz_inv_update_{region}.txt'
                file_path = os.path.join(folder_path, filename)
                
                # Save the update file
                update_df.to_csv(file_path, sep='\t', index=False)
                
                # Add the file to the ZIP archive
                zipf.write(file_path, os.path.join('Update files', file_path))
                
                # Remove the temporary file
                os.remove(file_path)
            
            
            os.rmdir('Amazon')
        
        logger.info(f"Inventory update files generated and saved to {zip_filename}")
    
    except Exception as e:
        logger.error(f"Error generating inventory update files: {str(e)}")
        raise

#test this function in terminal
def test():
    BS_export_df = pd.read_csv('../preparing/data/STOCK-STATUS202407098.952568.TXT', sep='\t', encoding='ascii', skiprows=2, dtype=str)
    generate_inv_update_files(BS_export_df)
    
# test()


