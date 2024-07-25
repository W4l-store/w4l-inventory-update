# utils/generate_inv_update_files.py

import pandas as pd
import logging
import os 
import zipfile
import time 
import glob

from .gen_amz_inv_update_by_region import gen_amz_inv_update_by_region
from .wayfair import gen_wayfair_inv_update_by_region
from .walmart import gen_walmart_inv_update_by_region
from .houzz import gen_houzz_inv_update
from .update_resources import update_resources
from .helpers import a_ph, set_processing_status

logger = logging.getLogger(__name__)

amazon_regions = ["PL", "FR", "SE", "US", "NL", "UK", "MX", "CA", "BE", "ES", "IT", "DE"]
wayfair_regions = ["US", "CA"]
walmart_regions = ["US", "CA"]

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
            
            # Generate update files for each Wayfair region
            for region in wayfair_regions:
                update_df = gen_wayfair_inv_update_by_region(BS_export_df, region)
                
                # Create the folder structure
                folder_path = f'Wayfair/'
                os.makedirs(folder_path, exist_ok=True)
                
                # Generate the filename
                filename = f'wayfair_inv_update_{region}.csv'
                file_path = os.path.join(folder_path, filename)
                
                # Save the update file
                update_df.to_csv(file_path, index=False)
                
                # Add the file to the ZIP archive
                zipf.write(file_path, os.path.join('Update files', file_path))
                
                # Remove the temporary file
                os.remove(file_path)
            
            # Generate update files for each Walmart region
            for region in walmart_regions:
                update_df = gen_walmart_inv_update_by_region(BS_export_df, region)
                
                # Create the folder structure
                folder_path = f'Walmart/'
                os.makedirs(folder_path, exist_ok=True)
                
                # Generate the filename
                filename = f'walmart_inv_update_{region}.csv'
                file_path = os.path.join(folder_path, filename)
                
                # Save the update file
                update_df.to_csv(file_path, index=False)
                
                # Add the file to the ZIP archive
                zipf.write(file_path, os.path.join('Update files', file_path))
                
                # Remove the temporary file
                os.remove(file_path)
            
            # Generate update file for Houzz
            update_df = gen_houzz_inv_update(BS_export_df)
            
            # Create the folder structure
            folder_path = f'Houzz/'
            os.makedirs(folder_path, exist_ok=True)
            
            # Generate the filename
            filename = f'houzz_inv_update.csv'
            file_path = os.path.join(folder_path, filename)
            
            # Save the update file
            update_df.to_csv(file_path, index=False)
            
            # Add the file to the ZIP archive
            zipf.write(file_path, os.path.join('Update files', file_path))
            
            # Remove the temporary file
            os.remove(file_path)
            
            os.rmdir('Amazon')
            os.rmdir('Wayfair')
            os.rmdir('Walmart')
            os.rmdir('Houzz')
        
        logger.info(f"Inventory update files generated and saved to {zip_filename}")

    
    except Exception as e:
        logger.error(f"Error generating inventory update files: {str(e)}")
        raise

#test this function in terminal
def test():
    BS_export_df = pd.read_csv('../preparing/data/STOCK-STATUS202407098.952568.TXT', sep='\t', encoding='ascii', skiprows=2, dtype=str)
    generate_inv_update_files(BS_export_df)
    
# test()
