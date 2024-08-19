import os
import sys
import subprocess
import venv
from dotenv import load_dotenv


def init_git_repo():
    load_dotenv()  # Load environment variables from .env file
    repo_path = os.path.dirname(os.path.abspath(__file__))
    github_repo_url = os.getenv('GITHUB_REPO_URL')
    
    if not github_repo_url:
        print("Error: GITHUB_REPO_URL is not set in the .env file.")
        return False

    if not os.path.exists(os.path.join(repo_path, '.git')):
        print("Initializing Git repository...")
        try:
            subprocess.check_call(['git', 'init'], cwd=repo_path)
            subprocess.check_call(['git', 'remote', 'add', 'origin', github_repo_url], cwd=repo_path)
            subprocess.check_call(['git', 'fetch'], cwd=repo_path)
            subprocess.check_call(['git', 'checkout', '-b', 'main', '--track', 'origin/main'], cwd=repo_path)
            print("Git repository initialized successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Git repository: {e}")
            return False
    else:
        print("Git repository already initialized.")
        return True

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
    init_git_repo()
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
