import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import glob
import logging
import threading
from datetime import datetime
import time
import uuid
from threading import Lock
from flask_cors import CORS
from collections import deque
from utils.helpers import a_ph



from utils.reserving import update_all_BS_sku_reserve
from utils.generate_inv_update_files import generate_inv_update_files
from utils.helpers import get_processing_status, is_inv_updated_today, a_ph, set_processing_status, clear_processing_logs, append_to_processing_logs

from logger_config import setup_logger


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Setup logger
logger = setup_logger()


UPLOAD_FOLDER = '/resources/user_uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_directories():
    """Initialize all required directories with proper permissions"""
    required_dirs = [
        '/resources',
        '/resources/user_uploads',
        '/resources/amazon',
        '/resources/wayfair',
        '/resources/walmart',
        '/resources/houzz',
        '/resources/blue_system',
        '/resources/reserve',
        '/download'
    ]
    
    for dir_path in required_dirs:
        try:
            full_path = a_ph(dir_path)
            os.makedirs(full_path, mode=0o755, exist_ok=True)
            logger.info(f"Ensured directory exists: {dir_path}")
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {str(e)}")

# Initialize directories when app starts
init_directories()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def main_page():
    logger.info('Main page requested')
    is_updated_today = is_inv_updated_today()
    if not is_updated_today:
        set_processing_status('NO_TASK')
    elif get_processing_status()['state'] != 'PROCESSING':
        set_processing_status('NO_TASK')
    elif is_updated_today:
        set_processing_status('SUCCESS')
    
    if get_processing_status()['state'] == 'PROCESSING':
        is_processing = True
    else:
        is_processing = False
        
    return render_template('upload.html', is_updated_today=is_updated_today, is_processing=is_processing)

@app.route('/', methods=['POST'])
def upload_file():
    current_task = get_processing_status()
    logger.info('File upload request received')
    
    if current_task['state'] == 'PROCESSING':
        return jsonify({'error': 'A task is already in progress'})

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        try:
            # Get the upload directory path
            upload_dir = a_ph(app.config['UPLOAD_FOLDER'])
            
            # Ensure all parent directories exist with proper permissions
            os.makedirs(upload_dir, mode=0o755, exist_ok=True)
            
            # Clean up existing files
            try:
                files = glob.glob(os.path.join(upload_dir, '*'))
                for f in files:
                    if os.path.isfile(f):
                        os.remove(f)
            except Exception as e:
                logger.warning(f"Error cleaning up existing files: {str(e)}")
            
            # Save the new file
            file_path = a_ph(os.path.join(app.config['UPLOAD_FOLDER'], "BS_stock.TXT"))
            file.save(file_path)
            
            # Ensure the file was created successfully
            if not os.path.exists(file_path):
                raise Exception("File was not saved successfully")
                
            task_id = str(uuid.uuid4())
            threading.Thread(target=process_file_task, args=(file_path, task_id)).start()
            return jsonify({'message': 'File uploaded and processing started'})
            
        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}")
            return jsonify({'error': f'Error uploading file: {str(e)}'})
    
    return jsonify({'error': 'Invalid file type'})

def process_file_task(file_path, task_id):
    current_task = get_processing_status()
    set_processing_status('PROCESSING', result='File processing started')
    clear_processing_logs()
    try:
        logger.info('Starting file processing')
        BS_export_df = pd.read_csv(file_path, sep='\t', encoding='ascii', skiprows=2, dtype=str)
        generate_inv_update_files(BS_export_df)

        logger.info('File processing completed successfully')
       

        update_all_BS_sku_reserve()
        current_task['state'] = 'SUCCESS'
        current_task['result'] = 'File processed successfully'
        set_processing_status('SUCCESS', result='File processed successfully')
           
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        current_task['state'] = 'FAILURE'
        current_task['result'] = f'Error processing file: {str(e)}'
        set_processing_status('FAILURE', result=f'Error processing file: {str(e)}')

@app.route('/task_status')
def task_status():
    status_data = get_processing_status()
    return jsonify({
        'state': status_data['state'],
        'result': status_data.get('result', ''),
        'logs': status_data.get('logs', [])
    })

@app.route('/download')
def download_file():
    zip_files = glob.glob(a_ph('/download/*.zip'))
    if not zip_files or not is_inv_updated_today():
        return jsonify({'error': 'No update files available or file not created today'})
    file_name = zip_files[0]
    
    try:
        with open(file_name, 'rb') as f:
            f.read()
    except IOError:
        return jsonify({'error': 'File is not ready for download. Please try again in a few moments.'})
    
    return send_file(file_name, as_attachment=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True, use_reloader=False)
