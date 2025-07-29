import os
import json

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".creative_writer_cli")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def _ensure_config_dir_exists():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    _ensure_config_dir_exists()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    _ensure_config_dir_exists()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_project_directory_from_config():
    config = load_config()
    return config.get("project_directory")

def set_project_directory_in_config(path):
    config = load_config()
    config["project_directory"] = path
    save_config(config)
