import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
from logging.handlers import SocketHandler
import glob
import csv
import logging
import threading
from datetime import datetime
import uuid
from threading import Lock

from utils.reserving import update_all_BS_sku_reserve
from utils.generate_inv_update_files import generate_inv_update_files
from utils.helpers import get_processing_status, is_inv_updated_today, a_ph, set_processing_status
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, ping_timeout=60, ping_interval=25)

eventlet.monkey_patch()

# Configure logging
class SocketIOHandler(SocketHandler):
    def emit(self, record):
        socketio.emit('log_message', {"text": record.getMessage(), "type": record.levelname.lower()})

logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(SocketIOHandler('', 0))

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'resources/user_uploads/'
ALLOWED_EXTENSIONS = {'txt'}
PIN_CODE = "{{1234}}"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables
current_task_lock = Lock()
current_task = {'status': 'NO_TASK', 'result': ''}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def main_page():
    is_updated_today = is_inv_updated_today()
    logger.info(f'/////////////////processing status: {get_processing_status()}')
    if is_updated_today and get_processing_status() != 'PROCESSING':
        set_processing_status('SUCCESS')
    elif get_processing_status() != 'PROCESSING':
        set_processing_status('NO_TASK')
    
    if get_processing_status() == 'PROCESSING':
        is_processing = True
    else:
        is_processing = False
        
    return render_template('upload.html', is_updated_today=is_updated_today, is_processing=is_processing)

@app.route('/', methods=['POST'])
def upload_file():
    global current_task
    logger.info('File upload request received')
    
    with current_task_lock:
        if current_task['status'] == 'PROCESSING':
            return jsonify({'error': 'A task is already in progress'})
    
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*'))
            for f in files:
                os.remove(f)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], "BS_stock.TXT")
            file.save(file_path)
            task_id = str(uuid.uuid4())
            current_task = {'task_id': task_id, 'start_time': datetime.now().isoformat(), 'status': 'PROCESSING'}
    
    threading.Thread(target=process_file_task, args=(file_path, task_id)).start()
    return jsonify({'message': 'File uploaded and processing started'})

def process_file_task(file_path, task_id):
    global current_task
    set_processing_status('PROCESSING')
    try:
        BS_export_df = pd.read_csv(file_path, sep='\t', encoding='ascii', skiprows=2, dtype=str)
        generate_inv_update_files(BS_export_df)

        set_processing_status('SUCCESS')

        update_all_BS_sku_reserve()
        with current_task_lock:
            current_task['status'] = 'SUCCESS'
            current_task['result'] = 'File processed successfully'
           
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        with current_task_lock:
            current_task['status'] = 'FAILURE'
            current_task['result'] = f'Error processing file: {str(e)}'
            set_processing_status('FAILURE')

@app.route('/task_status')
def task_status():
    with current_task_lock:
        status = get_processing_status()
        return jsonify({
            'state': status,
            'result': current_task.get('result', '')
        })

@app.route('/download')
def download_file():
    zip_files = glob.glob(a_ph('/download/*.zip'))
    if not zip_files or not is_inv_updated_today():
        return jsonify({'error': 'No update files available or file not created today'})
    file_name = zip_files[0]
    return send_file(file_name, as_attachment=True)

@socketio.on_error_default
def default_error_handler(e):
    print(f'An error occurred: {e}')
    socketio.emit('error', {'message': 'An error occurred on the server'})

@socketio.on('connect')
def handle_connect():
    socketio.server.eio.generate_id = lambda: uuid.uuid4().hex

def clean_sessions():
    while True:
        socketio.sleep(3600)  # Очистка каждый час
        socketio.server.eio.clean_timers()

socketio.start_background_task(clean_sessions)

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid} from {request.remote_addr}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid} from {request.remote_addr}')

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8000, debug=True, use_reloader=False)


