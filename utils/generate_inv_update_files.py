# utils/generate_inv_update_files.py

import pandas as pd
import logging
import os 
import zipfile
import time 
import glob
import shutil

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
    temp_dir = 'temp_update_files'
    try:
        update_resources() 
        
        # Delete old ZIP files
        zip_files = glob.glob(a_ph('/download/*.zip'))
        for zip_file in zip_files:
            os.remove(zip_file)
            logger.info(f"Deleted {zip_file}")

        # Create a temporary directory for files
        os.makedirs(temp_dir, exist_ok=True)

        # Generate update files for each platform and region
        generate_amazon_files(BS_export_df, temp_dir)
        generate_wayfair_files(BS_export_df, temp_dir)
        generate_walmart_files(BS_export_df, temp_dir)
        generate_houzz_files(BS_export_df, temp_dir)

        # Create ZIP file
        today = time.strftime('%m_%d_%y')
        zip_filename = f'update_files_{today}.zip'
        os.makedirs(a_ph('download'), exist_ok=True)
        zip_path = os.path.join(a_ph('download'), zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('Update files', os.path.relpath(file_path, temp_dir))
                    zipf.write(file_path, arcname)

        # Verify ZIP file integrity
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            if zipf.testzip() is not None:
                raise Exception("ZIP file is corrupted")

        logger.info(f"Inventory update files generated and saved to {zip_filename}")

    except Exception as e:
        logger.error(f"Error generating inventory update files: {str(e)}")
        raise

    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def generate_amazon_files(BS_export_df, temp_dir):
    for region in amazon_regions:
        update_df = gen_amz_inv_update_by_region(BS_export_df, region)
        folder_path = os.path.join(temp_dir, 'Amazon')
        os.makedirs(folder_path, exist_ok=True)
        filename = f'amz_inv_update_{region}.txt'
        file_path = os.path.join(folder_path, filename)
        update_df.to_csv(file_path, sep='\t', index=False)

def generate_wayfair_files(BS_export_df, temp_dir):
    for region in wayfair_regions:
        update_df = gen_wayfair_inv_update_by_region(BS_export_df, region)
        folder_path = os.path.join(temp_dir, 'Wayfair')
        os.makedirs(folder_path, exist_ok=True)
        filename = f'wayfair_inv_update_{region}.csv'
        file_path = os.path.join(folder_path, filename)
        update_df.to_csv(file_path, index=False)

def generate_walmart_files(BS_export_df, temp_dir):
    for region in walmart_regions:
        update_df = gen_walmart_inv_update_by_region(BS_export_df, region)
        folder_path = os.path.join(temp_dir, 'Walmart')
        os.makedirs(folder_path, exist_ok=True)
        filename = f'walmart_inv_update_{region}.csv'
        file_path = os.path.join(folder_path, filename)
        update_df.to_csv(file_path, index=False)

def generate_houzz_files(BS_export_df, temp_dir):
    update_df = gen_houzz_inv_update(BS_export_df)
    folder_path = os.path.join(temp_dir, 'Houzz')
    os.makedirs(folder_path, exist_ok=True)
    filename = 'houzz_inv_update.csv'
    file_path = os.path.join(folder_path, filename)
    update_df.to_csv(file_path, index=False)

def test():
    BS_export_df = pd.read_csv('../preparing/data/STOCK-STATUS202407098.952568.TXT', sep='\t', encoding='ascii', skiprows=2, dtype=str)
    generate_inv_update_files(BS_export_df)

# test()
