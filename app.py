# app.py

import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
from logging.handlers import SocketHandler

import glob
import csv
import logging
import zipfile
import time
import threading
from utils.generate_inv_update_files import generate_inv_update_files
from utils.helpers import is_inv_updated_today
from utils.helpers import a_ph

app = Flask(__name__)
socketio = SocketIO(app)


# Configure logging
class SocketIOHandler(SocketHandler):
    def emit(self, record):
        socketio.emit('log_message', {"text": record.getMessage(), "type": record.levelname.lower()})

# Configure root logger
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(SocketIOHandler('localhost', 9000))

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'resources/user_uploads/'
ALLOWED_EXTENSIONS = {'txt'}
PIN_CODE = "{{1234}}"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def main_page():
    is_updated_today = is_inv_updated_today()
    
    return render_template('upload.html', is_updated_today= is_updated_today)

@app.route('/', methods=['POST'])
def upload_file():

    logger.info('File upload request received')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        #delete old files
        files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
        for f in files:
            os.remove(f)
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], "BS_stock.TXT")
        file.save(file_path)
        return process_file(file_path)




def process_file(file_path):

    try:
        BS_export_df = pd.read_csv(file_path, sep='\t', encoding='ascii', skiprows=2, dtype=str)
        generate_inv_update_files(BS_export_df)
        return jsonify({'message': 'File processed successfully'})

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'})

@app.route('/download')
def download_file():
    zip_files = glob.glob(a_ph('/download/*.zip'))
    if not zip_files:
        return jsonify({'error': 'No update files available'})
    else:
        file_name = zip_files[0]

    return send_file(file_name, as_attachment=True)

@app.route('/update_api', methods=['POST'])
def update_api():
    pin = request.json.get('pin')
    if pin != PIN_CODE:
        return jsonify({'error': 'Incorrect PIN'})
    
    # Simulating API update process
    time.sleep(5)
    
    return jsonify({'message': 'API update successful'})

@socketio.on('connect')
def test_connect():
    print('Client connected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
