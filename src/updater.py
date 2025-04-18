import requests, subprocess, os, shutil, zipfile
from src.settings import config

REPO = "N0-Chance/cronjob"
VERSION_URL = f"https://raw.githubusercontent.com/{REPO}/main/version.txt"
RELEASE_URL = f"https://github.com/{REPO}/releases/latest/download/cronjob.zip"
VERSION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.txt")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backup")

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
    return (local, latest, latest and latest != local)

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
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(os.path.dirname(os.path.dirname(__file__)))
        os.remove(filename)
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def perform_update():
    if not backup_current_version():
        return "Backup failed. Update aborted."
    if not download_latest_release():
        return "Download failed. Update aborted."
    if not extract_and_replace():
        return "Extraction failed. Update aborted."
    return "Update successful." 