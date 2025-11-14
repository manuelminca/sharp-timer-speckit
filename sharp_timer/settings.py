"""Settings management for Sharp Timer."""

import json
import os
import shutil
from pathlib import Path
from constants import (
    APP_SUPPORT_DIR, SETTINGS_FILENAME, DEFAULT_WORK_DURATION,
    DEFAULT_REST_EYES_DURATION, DEFAULT_LONG_REST_DURATION,
    MODE_WORK, MODE_REST_EYES, MODE_LONG_REST
)


class SettingsManager:
    """Manages application settings with JSON persistence."""
    
    def __init__(self):
        """Initialize settings manager with default values."""
        self.app_support_dir = Path.home() / APP_SUPPORT_DIR
        self.settings_file = self.app_support_dir / SETTINGS_FILENAME
        
        # Default settings
        self.defaults = {
            "work_duration": DEFAULT_WORK_DURATION,
            "rest_eyes_duration": DEFAULT_REST_EYES_DURATION,
            "long_rest_duration": DEFAULT_LONG_REST_DURATION,
            "current_mode": MODE_WORK,
            "notifications_enabled": True,
            "sound_enabled": True,
            "auto_start_next": False
        }
        
        # Current settings (start with defaults)
        self.settings = self.defaults.copy()
        
        # Ensure directory exists and load settings
        self._ensure_directory_exists()
        self.load_settings()
    
    def _ensure_directory_exists(self):
        """Create application support directory if it doesn't exist."""
        try:
            self.app_support_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create settings directory: {e}")
    
    def load_settings(self):
        """Load settings from JSON file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Update only keys that exist in defaults
                    for key in self.defaults:
                        if key in loaded:
                            self.settings[key] = loaded[key]
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load settings, using defaults: {e}")
            self.settings = self.defaults.copy()
    
    def save_settings(self):
        """Save settings to JSON file with atomic write."""
        try:
            # Write to temporary file first
            temp_file = self.settings_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            # Move temporary file to final location (atomic operation)
            shutil.move(str(temp_file), str(self.settings_file))
        except (IOError, OSError) as e:
            print(f"Warning: Could not save settings: {e}")
    
    def get_duration(self, mode):
        """Get duration for a specific mode in minutes."""
        duration_key = f"{mode}_duration"
        return self.settings.get(duration_key, self.defaults.get(duration_key, 25))
    
    def set_duration(self, mode, duration):
        """Set duration for a specific mode in minutes."""
        if isinstance(duration, int) and 1 <= duration <= 60:
            duration_key = f"{mode}_duration"
            self.settings[duration_key] = duration
            self.save_settings()
            return True
        return False
    
    def get_current_mode(self):
        """Get the currently selected mode."""
        return self.settings.get("current_mode", MODE_WORK)
    
    def set_current_mode(self, mode):
        """Set the current mode."""
        if mode in [MODE_WORK, MODE_REST_EYES, MODE_LONG_REST]:
            self.settings["current_mode"] = mode
            self.save_settings()
            return True
        return False
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = self.defaults.copy()
        self.save_settings()
