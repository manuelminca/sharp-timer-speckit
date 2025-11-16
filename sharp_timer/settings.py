"""Settings management for Sharp Timer."""

import json
import os
import shutil
from pathlib import Path
from typing import Optional
from constants import (
    APP_SUPPORT_DIR, SETTINGS_FILENAME, DEFAULT_WORK_DURATION,
    DEFAULT_REST_EYES_DURATION, DEFAULT_LONG_REST_DURATION,
    MODE_WORK, MODE_REST_EYES, MODE_LONG_REST
)
from timer_state import TimerState, TimerStateManager


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
            "auto_start_next": False,
            # Enhanced settings for 002-enhancements
            "audio_config": {
                "enabled": True,
                "duration_seconds": 5,
                "primary_sound": "/System/Library/Sounds/Glass.aiff",
                "fallback_sounds": [
                    "/System/Library/Sounds/Ping.aiff",
                    "/System/Library/Sounds/Purr.aiff"
                ],
                "volume_level": 1.0
            },
            "mode_transitions": {
                "work_to_rest_eyes": {
                    "enabled": True,
                    "target_state": "paused",
                    "transition_delay_ms": 100
                },
                "rest_eyes_to_work": {
                    "enabled": True,
                    "target_state": "paused",
                    "transition_delay_ms": 100
                },
                "long_rest_to_work": {
                    "enabled": True,
                    "target_state": "paused",
                    "transition_delay_ms": 100
                }
            },
            "system_integration": {
                "handle_sleep_events": True,
                "preserve_state_across_restarts": True,
                "quit_confirmation_enabled": True
            }
        }
        
        # Current settings (start with defaults)
        self.settings = self.defaults.copy()
        
        # Initialize timer state manager
        self.timer_state_manager = TimerStateManager()
        
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
    
    # Timer state management methods
    def save_timer_state(self, state: TimerState) -> bool:
        """Save timer state using timer state manager."""
        return self.timer_state_manager.save_timer_state(state)
    
    def load_timer_state(self) -> Optional[TimerState]:
        """Load timer state using timer state manager."""
        return self.timer_state_manager.load_timer_state()
    
    def create_timer_state_backup(self, state: TimerState) -> bool:
        """Create backup of timer state."""
        return self.timer_state_manager.create_backup(state)
    
    def restore_timer_state_from_backup(self) -> Optional[TimerState]:
        """Restore timer state from backup."""
        return self.timer_state_manager.restore_from_backup()
    
    def clear_timer_state(self) -> bool:
        """Clear timer state from persistent storage."""
        return self.timer_state_manager.clear_timer_state()
    
    def validate_timer_state(self, state: TimerState) -> bool:
        """Validate timer state data integrity."""
        return self.timer_state_manager.validate_timer_state(state)
    
    # Enhanced settings methods
    def get_audio_config(self) -> dict:
        """Get audio notification configuration."""
        return self.settings.get("audio_config", self.defaults["audio_config"])
    
    def set_audio_config(self, config: dict) -> bool:
        """Set audio notification configuration."""
        if isinstance(config, dict):
            self.settings["audio_config"] = config
            self.save_settings()
            return True
        return False
    
    def get_mode_transition_config(self, from_mode: str, to_mode: str) -> dict:
        """Get mode transition configuration."""
        transition_key = f"{from_mode}_to_{to_mode}"
        transitions = self.settings.get("mode_transitions", {})
        return transitions.get(transition_key, {})
    
    def set_mode_transition_config(self, from_mode: str, to_mode: str, config: dict) -> bool:
        """Set mode transition configuration."""
        if isinstance(config, dict) and from_mode in [MODE_WORK, MODE_REST_EYES, MODE_LONG_REST]:
            transition_key = f"{from_mode}_to_{to_mode}"
            if "mode_transitions" not in self.settings:
                self.settings["mode_transitions"] = {}
            self.settings["mode_transitions"][transition_key] = config
            self.save_settings()
            return True
        return False
    
    def get_system_integration_config(self) -> dict:
        """Get system integration configuration."""
        return self.settings.get("system_integration", self.defaults["system_integration"])
    
    def set_system_integration_config(self, config: dict) -> bool:
        """Set system integration configuration."""
        if isinstance(config, dict):
            self.settings["system_integration"] = config
            self.save_settings()
            return True
        return False
    
    def save_complete_state(self, timer_state: TimerState) -> bool:
        """Save both settings and timer state atomically."""
        # Save timer state first
        if not self.save_timer_state(timer_state):
            return False
        
        # Then save settings (includes current_mode reference)
        self.set_current_mode(timer_state.mode)
        return True
    
    def load_complete_state(self) -> Optional[TimerState]:
        """Load complete application state."""
        return self.load_timer_state()
