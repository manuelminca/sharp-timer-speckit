"""Timer state management for Sharp Timer enhancements."""

import json
import uuid
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any
from constants import APP_SUPPORT_DIR, SETTINGS_FILENAME


@dataclass
class TimerState:
    """Complete timer state for persistence and recovery."""
    mode: str
    remaining_seconds: int
    is_running: bool
    is_paused: bool
    session_id: str
    start_timestamp: float
    last_update_timestamp: float
    total_duration_seconds: int
    survived_sleep: bool = False
    unexpected_termination: bool = False
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.start_timestamp:
            self.start_timestamp = time.time()
        self.last_update_timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimerState':
        """Create from dictionary for JSON deserialization."""
        return cls(**data)
    
    def is_valid(self) -> bool:
        """Validate timer state data."""
        return (
            self.mode in ['work', 'rest_eyes', 'long_rest'] and
            self.remaining_seconds >= 0 and
            self.total_duration_seconds > 0 and
            self.remaining_seconds <= self.total_duration_seconds and
            not (self.is_running and self.is_paused) and
            self.session_id and
            self.start_timestamp > 0
        )


class TimerStateManager:
    """Manages timer state persistence and recovery."""
    
    def __init__(self):
        self.app_support_dir = Path.home() / APP_SUPPORT_DIR
        self.settings_file = self.app_support_dir / SETTINGS_FILENAME
        self.backup_dir = self.app_support_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def save_timer_state(self, state: TimerState) -> bool:
        """Save timer state to persistent storage."""
        try:
            # Load current settings
            settings = self._load_settings()
            
            # Update timer state
            settings['timer_state'] = state.to_dict()
            settings['metadata'] = {
                'app_version': '1.1.0',
                'last_saved': time.time(),
                'backup_count': len(list(self.backup_dir.glob('timer_state_backup_*.json')))
            }
            
            # Atomic write
            return self._atomic_save_settings(settings)
        except Exception as e:
            print(f"Error saving timer state: {e}")
            return False
    
    def load_timer_state(self) -> Optional[TimerState]:
        """Load timer state from persistent storage."""
        try:
            settings = self._load_settings()
            timer_state_data = settings.get('timer_state')
            
            if timer_state_data:
                state = TimerState.from_dict(timer_state_data)
                if state.is_valid():
                    return state
                else:
                    print("Invalid timer state found, using defaults")
                    return None
            return None
        except Exception as e:
            print(f"Error loading timer state: {e}")
            return None
    
    def create_backup(self, state: TimerState) -> bool:
        """Create backup of current timer state."""
        try:
            timestamp = int(time.time())
            backup_file = self.backup_dir / f"timer_state_backup_{timestamp}.json"
            
            backup_data = {
                'timer_state': state.to_dict(),
                'backup_timestamp': timestamp,
                'app_version': '1.1.0'
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            # Clean up old backups (keep last 5)
            self._cleanup_old_backups()
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_from_backup(self) -> Optional[TimerState]:
        """Restore timer state from most recent backup."""
        try:
            backup_files = sorted(self.backup_dir.glob('timer_state_backup_*.json'))
            if not backup_files:
                return None
            
            # Get most recent backup
            latest_backup = backup_files[-1]
            with open(latest_backup, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            timer_state_data = backup_data.get('timer_state')
            if timer_state_data:
                state = TimerState.from_dict(timer_state_data)
                if state.is_valid():
                    return state
            
            return None
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return None
    
    def clear_timer_state(self) -> bool:
        """Clear timer state from persistent storage."""
        try:
            settings = self._load_settings()
            if 'timer_state' in settings:
                del settings['timer_state']
            return self._atomic_save_settings(settings)
        except Exception as e:
            print(f"Error clearing timer state: {e}")
            return False
    
    def validate_timer_state(self, state: TimerState) -> bool:
        """Validate timer state data integrity."""
        return state.is_valid()
    
    def get_state_history(self, limit: int = 10) -> list[TimerState]:
        """Get historical timer states from backups."""
        try:
            backup_files = sorted(self.backup_dir.glob('timer_state_backup_*.json'))
            if not backup_files:
                return []
            
            states = []
            for backup_file in backup_files[-limit:]:
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    timer_state_data = backup_data.get('timer_state')
                    if timer_state_data:
                        state = TimerState.from_dict(timer_state_data)
                        if state.is_valid():
                            states.append(state)
                except:
                    continue  # Skip corrupted backup files
            
            return states
        except Exception as e:
            print(f"Error getting state history: {e}")
            return []
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        if self.settings_file.exists():
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _atomic_save_settings(self, settings: Dict[str, Any]) -> bool:
        """Atomically save settings to file."""
        try:
            temp_file = self.settings_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            temp_file.replace(self.settings_file)
            return True
        except Exception:
            return False
    
    def _cleanup_old_backups(self):
        """Keep only the last 5 backup files."""
        backup_files = sorted(self.backup_dir.glob('timer_state_backup_*.json'))
        if len(backup_files) > 5:
            for old_backup in backup_files[:-5]:
                old_backup.unlink()
