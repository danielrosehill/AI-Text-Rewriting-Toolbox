"""
Configuration module for the AI Text Transformer Toolbox.
Handles user preferences and application settings.
"""

import os
import json
from appdirs import user_config_dir

# Define app name for config directory
APP_NAME = "ai-text-transformer-toolbox"

# Get the user's config directory
CONFIG_DIR = user_config_dir(APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "preferences.json")

# Default configuration
DEFAULT_CONFIG = {
    "model": "llama3",
    "download_path": os.path.expanduser("~/Desktop"),
    "last_used_transformations": ["basic_cleanup"]
}


def ensure_config_dir():
    """Ensure the config directory exists."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)


def load_preferences():
    """Load user preferences from the config file."""
    ensure_config_dir()
    
    if not os.path.exists(CONFIG_FILE):
        save_preferences(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If the file is corrupted or missing, reset to defaults
        save_preferences(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_preferences(preferences):
    """Save user preferences to the config file."""
    ensure_config_dir()
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(preferences, f, indent=2)


def update_preference(key, value):
    """Update a specific preference."""
    preferences = load_preferences()
    preferences[key] = value
    save_preferences(preferences)


def get_preference(key, default=None):
    """Get a specific preference."""
    preferences = load_preferences()
    return preferences.get(key, default)
