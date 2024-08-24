import os
import sys
import subprocess
import venv
import shutil
from dotenv import load_dotenv

def check_current_directory():
    current_dir = os.getcwd()
    if any(os.path.isdir(os.path.join(current_dir, item)) for item in os.listdir(current_dir)):
        print("Error: The current directory contains other folders. Please run this script in an empty directory.")
        sys.exit(1)

def check_env_file():
    if not os.path.isfile('.env'):
        print("Error: .env file not found in the current directory.")
        sys.exit(1)

def clone_repository(repo_url, target_dir):
    print(f"Cloning repository into {target_dir}...")
    subprocess.check_call(['git', 'clone', repo_url, target_dir])

def copy_env_file(target_dir):
    shutil.copy('.env', target_dir)
    print(".env file copied to the new directory.")

def create_venv(target_dir):
    venv_path = os.path.join(target_dir, 'venv')
    print("Creating virtual environment...")
    venv.create(venv_path, with_pip=True)
    return venv_path

def get_venv_python(venv_path):
    if sys.platform == 'win32':
        return os.path.join(venv_path, 'Scripts', 'python.exe')
    return os.path.join(venv_path, 'bin', 'python')

def install_dependencies(venv_python, target_dir):
    requirements_path = os.path.join(target_dir, 'requirements.txt')
    if os.path.exists(requirements_path):
        print("Installing dependencies...")
        subprocess.check_call([venv_python, '-m', 'pip', 'install', '-r', requirements_path])
    else:
        print("requirements.txt not found. Skipping dependency installation.")

def main():
    # Load environment variables
    check_env_file()
    load_dotenv()
    repo_url = os.getenv('GITHUB_REPO_URL')
    if not repo_url:
        print("Error: GITHUB_REPO_URL is not set in the .env file.")
        sys.exit(1)

    # Check current directory and .env file
    check_current_directory()
    

    # Clone repository

    # Extract the repository name from the URL
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    # Create the target directory path
    target_dir = os.path.join(os.getcwd(), repo_name)
    clone_repository(repo_url, target_dir)

    # Copy .env file
    copy_env_file(target_dir)

    # Create virtual environment and install dependencies
    venv_path = create_venv(target_dir)
    venv_python = get_venv_python(venv_path)
    install_dependencies(venv_python, target_dir)

    print("Initialization completed successfully.")

if __name__ == "__main__":
    main()
