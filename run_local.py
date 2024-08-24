import os
import sys
import subprocess
import venv
import webbrowser
import time

def create_venv():
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
    return venv_path

def get_venv_python(venv_path):
    if sys.platform == 'win32':
        return os.path.join(venv_path, 'Scripts', 'python.exe')
    return os.path.join(venv_path, 'bin', 'python')

def start_server(venv_python):
    print("Starting server...")
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    return subprocess.Popen([venv_python, app_path])

def open_browser(url):
    print(f"Opening {url} in browser...")
    webbrowser.open(url)

def main():
    venv_path = create_venv()
    venv_python = get_venv_python(venv_path)
    
    server_process = start_server(venv_python)
    
    time.sleep(2)
    
    open_browser("http://127.0.0.1:8000")  
    
    try:
        # Ожидаем завершения сервера
        server_process.wait()
    except KeyboardInterrupt:
        print("Stopping server...")
        server_process.terminate()

if __name__ == "__main__":
    main()
