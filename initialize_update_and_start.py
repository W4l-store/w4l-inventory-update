import os
import sys
import subprocess
import venv
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    return os.getenv('GITHUB_REPO_URL')

def clone_or_pull_repo(repo_url):
    repo_path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(repo_path, '.git')):
        if os.listdir(repo_path):
            print("Destination directory is not empty. Pulling updates instead of cloning...")
            subprocess.check_call(['git', 'init'], cwd=repo_path)
            subprocess.check_call(['git', 'remote', 'add', 'origin', repo_url], cwd=repo_path)
            subprocess.check_call(['git', 'fetch'], cwd=repo_path)
            subprocess.check_call(['git', 'reset', '--hard', 'origin/master'], cwd=repo_path)  # Changed 'main' to 'master'
        else:
            print("Cloning repository...")
            subprocess.check_call(['git', 'clone', repo_url, repo_path])
    else:
        print("Repository already exists. Pulling updates...")
        subprocess.check_call(['git', 'pull'], cwd=repo_path)

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


def start_server(venv_python):
    print("Starting server...")
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    subprocess.check_call([venv_python, app_path])

def get_venv_python(venv_path):
    if sys.platform == 'win32':
        return os.path.join(venv_path, 'Scripts', 'python.exe')
    return os.path.join(venv_path, 'bin', 'python')

def main():
    repo_url = load_env()
    if not repo_url:
        print("Error: GITHUB_REPO_URL is not set in the .env file.")
        sys.exit(1)

    clone_or_pull_repo(repo_url)
    venv_path = create_venv()
    venv_python = get_venv_python(venv_path)
    install_dependencies(venv_python)
    print("Initialization and update completed successfully.")
    start_server(venv_python)



if __name__ == "__main__":
    main()
