# Timer State API Contract

**Version**: 1.0  
**Date**: 2025-11-14  
**Component**: Timer State Management

## Overview

This contract defines the API interface for timer state persistence, recovery, and management in the Sharp Timer enhancements.

## Interfaces

### TimerStateManager

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json
import uuid
from pathlib import Path

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

class TimerStateManager(ABC):
    """Abstract interface for timer state management."""
    
    @abstractmethod
    def save_timer_state(self, state: TimerState) -> bool:
        """Save timer state to persistent storage.
        
        Args:
            state: Timer state to save
            
        Returns:
            True if save successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load_timer_state(self) -> Optional[TimerState]:
        """Load timer state from persistent storage.
        
        Returns:
            TimerState if found and valid, None otherwise
        """
        pass
    
    @abstractmethod
    def create_backup(self, state: TimerState) -> bool:
        """Create backup of current timer state.
        
        Args:
            state: Timer state to backup
            
        Returns:
            True if backup successful, False otherwise
        """
        pass
    
    @abstractmethod
    def restore_from_backup(self) -> Optional[TimerState]:
        """Restore timer state from backup.
        
        Returns:
            TimerState if backup found and valid, None otherwise
        """
        pass
    
    @abstractmethod
    def clear_timer_state(self) -> bool:
        """Clear timer state from persistent storage.
        
        Returns:
            True if clear successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_timer_state(self, state: TimerState) -> bool:
        """Validate timer state data integrity.
        
        Args:
            state: Timer state to validate
            
        Returns:
            True if state is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_state_history(self, limit: int = 10) -> list[TimerState]:
        """Get historical timer states.
        
        Args:
            limit: Maximum number of historical states to return
            
        Returns:
            List of historical timer states
        """
        pass
```

## Implementation Requirements

### File Storage Schema

```json
{
  "version": "1.0",
  "timer_state": {
    "mode": "work|rest_eyes|long_rest",
    "remaining_seconds": 1500,
    "is_running": true,
    "is_paused": false,
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "start_timestamp": 1699999999.0,
    "last_update_timestamp": 1700000000.0,
    "total_duration_seconds": 1500,
    "survived_sleep": false,
    "unexpected_termination": false
  },
  "metadata": {
    "app_version": "1.1.0",
    "last_saved": "2025-11-14T17:20:00Z",
    "backup_count": 3
  }
}
```

### Error Handling

```python
class TimerStateError(Exception):
    """Base exception for timer state operations."""
    pass

class TimerStateCorruptionError(TimerStateError):
    """Raised when timer state data is corrupted."""
    pass

class TimerStateValidationError(TimerStateError):
    """Raised when timer state validation fails."""
    pass

class TimerStatePersistenceError(TimerStateError):
    """Raised when timer state persistence fails."""
    pass
```

### Performance Requirements

- **Save Operations**: < 10ms for normal state, < 50ms for backup creation
- **Load Operations**: < 5ms for state loading, < 20ms for backup restoration
- **Validation**: < 1ms for state validation
- **File Size**: < 1KB for state file, < 10KB for backup files

### Atomic Operations

All write operations must be atomic:
1. Write to temporary file with `.tmp` extension
2. Validate written data
3. Atomic move to final destination
4. Clean up temporary files

### Backup Strategy

- **Frequency**: Every 30 seconds during active timer
- **Retention**: Keep last 5 backup files
- **Naming**: `timer_state_backup_YYYYMMDD_HHMMSS.json`
- **Cleanup**: Remove old backups on successful save

## Integration Points

### SettingsManager Integration

```python
class EnhancedSettingsManager(SettingsManager):
    """Extended settings manager with timer state support."""
    
    def __init__(self):
        super().__init__()
        self.timer_state_manager = TimerStateManagerImpl()
    
    def save_complete_state(self, timer_state: TimerState) -> bool:
        """Save both settings and timer state atomically."""
        # Save timer state first
        if not self.timer_state_manager.save_timer_state(timer_state):
            return False
        
        # Then save settings (includes current_mode reference)
        self.set_current_mode(timer_state.mode)
        return True
    
    def load_complete_state(self) -> Optional[TimerState]:
        """Load complete application state."""
        return self.timer_state_manager.load_timer_state()
```

### SystemEventManager Integration

```python
class SystemEventManager:
    """Handles system sleep/wake events."""
    
    def __init__(self, timer_state_manager: TimerStateManager):
        self.timer_state_manager = timer_state_manager
        self.setup_system_event_monitoring()
    
    def on_system_sleep(self):
        """Handle system sleep event."""
        # Save current state before sleep
        current_state = self.get_current_timer_state()
        if current_state:
            current_state.survived_sleep = True
            self.timer_state_manager.save_timer_state(current_state)
    
    def on_system_wake(self):
        """Handle system wake event."""
        # Validate and restore state after wake
        restored_state = self.timer_state_manager.load_timer_state()
        if restored_state and restored_state.survived_sleep:
            # Adjust for sleep duration if needed
            self.adjust_for_sleep_duration(restored_state)
```

## Testing Requirements

### Unit Tests

- `test_save_timer_state_success`
- `test_save_timer_state_failure`
- `test_load_timer_state_success`
- `test_load_timer_state_not_found`
- `test_load_timer_state_corrupted`
- `test_create_backup_success`
- `test_restore_from_backup_success`
- `test_validate_timer_state_valid`
- `test_validate_timer_state_invalid`
- `test_clear_timer_state_success`

### Integration Tests

- `test_persistence_across_restarts`
- `test_backup_creation_during_active_timer`
- `test_state_recovery_after_crash`
- `test_concurrent_state_access`
- `test_file_corruption_handling`

### Performance Tests

- `test_save_performance_under_load`
- `test_load_performance_with_large_history`
- `test_backup_creation_performance`
- `test_atomic_operation_performance`

## Security Considerations

- File permissions: 600 (user read/write only)
- Directory permissions: 700 (user read/write/execute only)
- Input validation for all timer state fields
- Path traversal prevention in file operations
- Safe JSON parsing with error handling

## Monitoring and Logging

### Log Events

- Timer state save success/failure
- Timer state load success/failure
- Backup creation success/failure
- State validation failures
- File corruption detection
- Performance warnings (>50ms operations)

### Metrics

- Save operation latency
- Load operation latency
- Backup file count and size
- State validation error rate
- File corruption incidents
