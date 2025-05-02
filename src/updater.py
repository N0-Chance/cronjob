import requests, subprocess, os, shutil, zipfile
from src.settings import config

REPO = "N0-Chance/cronjob"
VERSION_URL = f"https://raw.githubusercontent.com/{REPO}/main/version.txt"
RELEASE_URL = f"https://github.com/{REPO}/releases/latest/download/cronjob.zip"
VERSION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.txt")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backup")

# Directories and files that should be preserved (not updated)
PRESERVE_DIRS = ['db', 'config', 'output']
PRESERVE_FILES = []  # Add any specific files to preserve here

def compare_versions(version1, version2):
    """
    Compare two version strings in format x.y.z
    Returns:
        -1 if version1 < version2
        0 if version1 == version2
        1 if version1 > version2
    """
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 < v2:
            return -1
        if v1 > v2:
            return 1
    return 0

def get_local_version():
    try:
        with open(VERSION_FILE) as f:
            return f.read().strip()
    except:
        return "0.0.0"

def get_latest_version():
    try:
        r = requests.get(VERSION_URL, timeout=5)
        return r.text.strip() if r.status_code == 200 else None
    except:
        return None

def is_update_available():
    local = get_local_version()
    latest = get_latest_version()
    if not latest:
        return (local, latest, False)
    comparison = compare_versions(local, latest)
    return (local, latest, comparison < 0)

def backup_current_version():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        for filename in os.listdir(os.path.dirname(__file__)):
            file_path = os.path.join(os.path.dirname(__file__), filename)
            if os.path.isfile(file_path):
                shutil.copy(file_path, BACKUP_DIR)
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

def download_latest_release():
    try:
        version = get_latest_version()
        if not version:
            print("Failed to retrieve the latest version.")
            return False
        filename = f"cronjob-v{version}.zip"
        r = requests.get(RELEASE_URL, stream=True)
        if r.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def extract_and_replace():
    try:
        version = get_latest_version()
        if not version:
            print("Failed to retrieve the latest version.")
            return False
        filename = f"cronjob-v{version}.zip"
        
        # Create a temporary directory for extraction
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_update")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        # Extract to temporary directory
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Get the root directory of the application
        root_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Update src directory
        src_dir = os.path.join(root_dir, "src")
        temp_src_dir = os.path.join(temp_dir, "src")
        if os.path.exists(src_dir):
            shutil.rmtree(src_dir)
        shutil.copytree(temp_src_dir, src_dir)
        
        # Update top-level files
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isfile(item_path) and item not in PRESERVE_FILES:
                shutil.copy2(item_path, root_dir)
        
        # Clean up
        shutil.rmtree(temp_dir)
        os.remove(filename)
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return False

def perform_update():
    if not backup_current_version():
        return "Backup failed. Update aborted."
    if not download_latest_release():
        return "Download failed. Update aborted."
    if not extract_and_replace():
        return "Extraction failed. Update aborted."
    return "Update successful." 