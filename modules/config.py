"""
Configuration management for EAI DealFlow Terminal.
Handles admin settings with auto-save and reset to defaults.
"""

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
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_CONFIG, **saved}
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Auto-save config to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def reset_to_defaults() -> dict:
    """Reset config to defaults and save."""
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()


def get_deal_heat_config(config: dict = None) -> dict:
    """Get deal heat thresholds from config."""
    if config is None:
        config = load_config()
    return config.get('deal_heat', DEFAULT_CONFIG['deal_heat'])
