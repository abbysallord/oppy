import os
import json
from pathlib import Path

HOME = str(Path.home())
CONFIG_DIR = os.path.join(HOME, ".config", "oppy")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "remote_only": True,
    "paid_only": True,
    "selected_platforms": ["unstop", "devpost", "remoteok", "weworkremotely"],
    "export_path": os.path.join(HOME, "Documents", "obsidian", "Brain", "00 Inbox", "Opportunities.md"),
    "search_keywords": [],
    "custom_rss_feeds": []
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except Exception:
            pass
        return DEFAULT_CONFIG.copy()
        
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Merge missing default keys
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")
