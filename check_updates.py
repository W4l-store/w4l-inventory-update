import os
import subprocess
import sys

def check_and_update():
    repo_path = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Fetch the latest changes
        subprocess.check_call(['git', 'fetch'], cwd=repo_path)
        
        # Get the hash of the current local commit
        local_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo_path).decode('utf-8').strip()
        
        # Get the hash of the latest remote commit
        remote_hash = subprocess.check_output(['git', 'rev-parse', 'origin/master'], cwd=repo_path).decode('utf-8').strip()
        
        if local_hash != remote_hash:
            print("Updates available. Downloading...")
            subprocess.check_call(['git', 'pull'], cwd=repo_path)
            print("Update completed.")
        else:
            print("No updates required.")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking/downloading updates: {e}")
        return False


if __name__ == "__main__":
    if check_and_update():
        print("Update check completed successfully.")
    else:
        print("Failed to check/download updates. Exiting.")
        sys.exit(1)
