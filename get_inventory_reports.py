import requests
import json
import time
import gzip
import base64
import pandas as pd
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ENDPOINT = "https://sellingpartnerapi-na.amazon.com"
API_VERSION = "2020-09-04"

def authorize(refresh_token, lwa_app_id, lwa_client_secret):
    """
    Handle authentication and obtain access token.
    """
    try:
        response = requests.post(
            "https://api.amazon.com/auth/o2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": lwa_app_id,
                "client_secret": lwa_client_secret,
            },
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.RequestException as e:
        logger.error(f"Authentication failed: {e}")
        raise

def request_report(access_token, report_type, marketplace_id):
    """
    Request a report and return the report_id.
    """
    try:
        response = requests.post(
            f"{ENDPOINT}/reports/{API_VERSION}/reports",
            headers={
                "x-amz-access-token": access_token,
                "Content-Type": "application/json",
            },
            json={
                "reportType": report_type,
                "marketplaceIds": [marketplace_id],
            },
        )
        response.raise_for_status()
        return response.json()["payload"]["reportId"]
    except requests.RequestException as e:
        logger.error(f"Failed to request report: {e}")
        raise

def create_inventory_reports(access_token, marketplace_ids):
    """
    Create inventory reports for multiple marketplaces.
    """
    report_ids = {}
    for marketplace_id in marketplace_ids:
        try:
            report_id = request_report(access_token, "GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT", marketplace_id)
            report_ids[marketplace_id] = report_id
            time.sleep(1)  # Delay to avoid rate limiting
        except Exception as e:
            logger.error(f"Failed to create report for marketplace {marketplace_id}: {e}")
    return report_ids

def check_report_status(access_token, report_ids):
    """
    Check the status of multiple reports and return report_document_ids when ready.
    """
    report_document_ids = {}
    while len(report_document_ids) < len(report_ids):
        for marketplace_id, report_id in report_ids.items():
            if marketplace_id not in report_document_ids:
                try:
                    response = requests.get(
                        f"{ENDPOINT}/reports/{API_VERSION}/reports/{report_id}",
                        headers={"x-amz-access-token": access_token},
                    )
                    response.raise_for_status()
                    report_status = response.json()["payload"]["processingStatus"]
                    if report_status == "DONE":
                        report_document_ids[marketplace_id] = response.json()["payload"]["reportDocumentId"]
                except requests.RequestException as e:
                    logger.error(f"Failed to check report status for marketplace {marketplace_id}: {e}")
        time.sleep(60)  # Wait before checking again
    return report_document_ids

def decompress_gzip(compressed_data):
    """
    Decompress GZIP data.
    """
    try:
        return gzip.decompress(compressed_data)
    except gzip.BadGzipFile as e:
        logger.error(f"Failed to decompress GZIP data: {e}")
        raise

def download_and_save_reports(access_token, report_document_ids):
    """
    Download, decompress, and save reports.
    """
    for marketplace_id, report_document_id in report_document_ids.items():
        try:
            # Get report document details
            response = requests.get(
                f"{ENDPOINT}/reports/{API_VERSION}/documents/{report_document_id}",
                headers={"x-amz-access-token": access_token},
            )
            response.raise_for_status()
            document_info = response.json()["payload"]

            # Download encrypted report
            encrypted_report = requests.get(document_info["url"]).content

            # Decrypt and decompress report
            key = base64.b64decode(document_info["encryptionDetails"]["key"])
            iv = base64.b64decode(document_info["encryptionDetails"]["initializationVector"])
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_report = decryptor.update(encrypted_report) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            unpadded_report = unpadder.update(decrypted_report) + unpadder.finalize()
            
            if document_info.get("compressionAlgorithm") == "GZIP":
                decompressed_report = decompress_gzip(unpadded_report)
            else:
                decompressed_report = unpadded_report

            # Save report
            filename = f"inventory_report_{marketplace_id}.txt"
            with open(filename, 'wb') as f:
                f.write(decompressed_report)
            
            logger.info(f"Report saved as {filename}")

            # Convert to Excel (optional)
            df = pd.read_csv(filename, sep="\t", encoding="ISO-8859-1", dtype=str)
            excel_filename = f"inventory_report_{marketplace_id}.xlsx"
            df.to_excel(excel_filename, index=False)
            logger.info(f"Excel report saved as {excel_filename}")

        except Exception as e:
            logger.error(f"Failed to process report for marketplace {marketplace_id}: {e}")

def main():
    load_dotenv()  # load environment variables from .env file

    # Get the keys from environment variables
    refresh_token = os.getenv('RESH_TOKEN')
    lwa_app_id = os.getenv('LWA_APP_ID')
    lwa_client_secret = os.getenv('LWA_CLIENT_SECRET')
    marketplace_ids = ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]  # US and CA marketplaces


    try:
        access_token = authorize(refresh_token, lwa_app_id, lwa_client_secret)
        report_ids = create_inventory_reports(access_token, marketplace_ids)
        report_document_ids = check_report_status(access_token, report_ids)
        download_and_save_reports(access_token, report_document_ids)
    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}")

if __name__ == "__main__":
    main()
