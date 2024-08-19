import os
import sys
import subprocess
import venv

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

def install_dependencies(venv_python):
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    if os.path.exists(requirements_path):
        print("Installing dependencies...")
        subprocess.check_call([venv_python, '-m', 'pip', 'install', '-r', requirements_path])
    else:
        print("requirements.txt not found. Skipping dependency installation.")

def check_updates(venv_python):
    print("Checking for updates...")
    update_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'check_updates.py')
    subprocess.check_call([venv_python, update_script])


def start_server(venv_python):
    print("Starting server...")
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    subprocess.check_call([venv_python, app_path])


if __name__ == "__main__":
    venv_path = create_venv()
    venv_python = get_venv_python(venv_path)
    install_dependencies(venv_python)
    check_updates(venv_python)
    start_server(venv_python)
