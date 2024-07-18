# app.py

import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
from logging.handlers import SocketHandler


import csv
import logging
import zipfile
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)


# Configure logging
class SocketIOHandler(SocketHandler):
    def emit(self, record):
        socketio.emit('log_message', record.getMessage())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(SocketIOHandler('localhost', 9000))

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
PIN_CODE = "{{1234}}"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    
    if request.method == 'POST':
        logger.info('File upload request received')
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return process_file(file_path)
    else:
        return render_template('upload.html')




def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
           
        return jsonify({'message': 'File processed successfully'})
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'})


@app.route('/download')
def download_file():
    return send_file('update_files.zip', as_attachment=True)

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
