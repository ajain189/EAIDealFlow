import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "deal_heat": {
        "revenue_min": 2_000_000,
        "revenue_max": 10_000_000,
        "peer_threshold": 5,
        "margin_threshold": 15
    },
    "auto_archive_days": 90,
    "keyboard_shortcuts_enabled": False,
    "first_visit_complete": False
}

def load_config() -> dict:
    """Load config from file or return defaults."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    """Auto-save config to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def reset_to_defaults() -> dict:
    """Reset config to defaults and save."""
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()
