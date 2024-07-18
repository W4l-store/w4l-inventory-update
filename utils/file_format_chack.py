import os
import csv
import logging

logger = logging.getLogger(__name__)

def validate_stock_status_file(file_path):
    logger.info(f"Starting validation of file: {file_path}")

    # Check file extension
    if not file_path.lower().endswith('.txt'):
        logger.warning(f"File {file_path} does not have a .txt extension")
        return False, "File must have a .txt extension"

    # Check file name
    file_name = os.path.basename(file_path)
    if not file_name.startswith('STOCK-STATUS'):
        logger.warning(f"File name {file_name} does not start with 'STOCK-STATUS'")
        return False, "File name must start with 'STOCK-STATUS'"

    # Check file contents
    required_columns = ['Item No.', 'Description', 'Qty on Hand', 'Unit Cost', 'Retail']

    try:
        with open(file_path, 'r', newline='') as file:
            reader = csv.reader(file, delimiter='\t')
            
            # Check headers
            headers = next(reader, None)
            if not headers or not all(col in headers for col in required_columns):
                missing_columns = [col for col in required_columns if col not in headers]
                logger.warning(f"Missing required columns: {', '.join(missing_columns)}")
                return False, f"Missing required columns: {', '.join(missing_columns)}"

            # Check data
            for row_num, row in enumerate(reader, start=2):
                if len(row) != len(headers):
                    logger.warning(f"Incorrect number of columns in row {row_num}")
                    return False, f"Incorrect number of columns in row {row_num}"

    except csv.Error as e:
        logger.error(f"CSV error in file {file_path}: {str(e)}")
        return False, "File is not a valid tab-delimited table"
    except IOError as e:
        logger.error(f"IO error reading file {file_path}: {str(e)}")
        return False, "Error reading the file"

    logger.info(f"File {file_path} successfully validated")
    return True, "File matches the required format"