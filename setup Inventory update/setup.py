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
        try:
            # Core packages that don't require compilation
            core_packages = [
                'Flask==3.0.3',
                'Flask-Cors==4.0.1',
                'Werkzeug==3.0.3',
                'waitress==2.1.2',
                'google-api-core==2.19.1',
                'google-api-python-client==2.137.0',
                'google-auth==2.32.0',
                'google-auth-httplib2==0.2.0',
                'google-auth-oauthlib==1.2.1',
                'gspread==6.1.2',
                'python-dotenv==1.0.1',
                'chardet==5.2.0',
                'openpyxl==3.1.5'
            ]
            
            for package in core_packages:
                try:
                    print(f"Installing {package}...")
                    subprocess.check_call([
                        venv_python, '-m', 'pip', 'install',
                        '--only-binary', ':all:',
                        package
                    ])
                except subprocess.CalledProcessError as e:
                    print(f"Warning: Failed to install {package} with --only-binary, trying without...")
                    try:
                        subprocess.check_call([
                            venv_python, '-m', 'pip', 'install',
                            package
                        ])
                    except subprocess.CalledProcessError as e:
                        print(f"Warning: Failed to install {package}: {str(e)}")
            
            # Install packages that might need compilation
            print("Installing pandas and numpy...")
            try:
                subprocess.check_call([
                    venv_python, '-m', 'pip', 'install',
                    '--only-binary', ':all:',
                    'pandas',  # Latest compatible version
                    'numpy'    # Latest compatible version
                ])
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to install pandas/numpy with --only-binary, trying without...")
                try:
                    subprocess.check_call([
                        venv_python, '-m', 'pip', 'install',
                        'pandas',
                        'numpy'
                    ])
                except subprocess.CalledProcessError as e:
                    print(f"Warning: Failed to install pandas/numpy: {str(e)}")
            
        except Exception as e:
            print("Warning: Some dependencies could not be installed.")
            print("The application may still work, but some features might be limited.")
            print(f"Error details: {str(e)}")
    else:
        print("requirements.txt not found. Skipping dependency installation.")

def main():
    try:
        # Load environment variables
        check_env_file()
        load_dotenv()
        repo_url = os.getenv('GITHUB_REPO_URL')
        if not repo_url:
            print("Error: GITHUB_REPO_URL is not set in the .env file.")
            sys.exit(1)

        # Check current directory
        check_current_directory()

        # Clone repository
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        target_dir = os.path.join(os.getcwd(), repo_name)
        clone_repository(repo_url, target_dir)

        # Copy .env file
        copy_env_file(target_dir)

        # Create virtual environment and install dependencies
        venv_path = create_venv(target_dir)
        venv_python = get_venv_python(venv_path)
        try:
            install_dependencies(venv_python, target_dir)
        except Exception as e:
            print(f"Warning: Error during dependency installation: {str(e)}")
            print("The application may still work with limited functionality.")
        
        print("Initialization completed successfully.")
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
