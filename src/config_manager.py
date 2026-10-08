"""
Configuration and logging manager for Killer Sudoku.
"""

import json
import logging
import os
from typing import Any, Dict

LOG_FILE = "error.log"

# Setup logging to file
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


class ConfigManager:
    """
    Manages loading and retrieving configuration settings with fallback defaults.
    """
    DEFAULT_CONFIG = {
        "app_title": "Killer Sudoku",
        "settings": {
            "highlight_row": True,
            "highlight_column": True,
            "highlight_box": True,
            "highlight_same_numbers": True,
            "enable_notes": True,
            "enable_timer": True,
            "enable_autosave": True,
            "autosave_interval": 30
        },
        "appearance": {
            "window_width": 900,
            "window_height": 900,
            "cell_size": 70,
            "background": "#FFFFFF",
            "grid_color": "#CCCCCC",
            "box_line_color": "#000000",
            "cage_line_color": "#2A65A0",
            "selected_color": "#B3D8FF",
            "highlight_color": "#EAF2FC",
            "same_number_color": "#CCE5FF",
            "error_color": "#FFCCCC",
            "given_font_color": "#000000",
            "player_font_color": "#002288",
            "note_font_color": "#666666"
        }
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path: str = config_path
        self.config: Dict[str, Any] = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        cfg = self.DEFAULT_CONFIG.copy()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Merge settings and appearance
                        if "app_title" in data:
                            cfg["app_title"] = data["app_title"]
                        if "settings" in data and isinstance(data["settings"], dict):
                            cfg["settings"].update(data["settings"])
                        if "appearance" in data and isinstance(data["appearance"], dict):
                            cfg["appearance"].update(data["appearance"])
            except Exception as e:
                logging.error(f"Failed to load config file {self.config_path}: {e}")
        return cfg

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.config.get("settings", {}).get(key, default)

    def get_appearance(self, key: str, default: Any = None) -> Any:
        return self.config.get("appearance", {}).get(key, default)


def log_error(msg: str, exc: Exception = None):
    if exc:
        logging.error(f"{msg}: {exc}", exc_info=True)
    else:
        logging.error(msg)
