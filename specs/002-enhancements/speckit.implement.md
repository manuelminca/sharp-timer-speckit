
# Implementation Guide: Sharp Timer Enhancements

**Feature Branch**: `002-enhancements`  
**Date**: 2025-11-14  
**Spec**: [speckit.specify.md](speckit.specify.md)  
**Plan**: [plan.md](plan.md)  
**Tasks**: [speckit.tasks.md](speckit.tasks.md)

## Overview

This implementation guide provides detailed instructions for implementing the Sharp Timer Enhancements feature, including code examples, file structure, and step-by-step implementation procedures.

## Implementation Strategy

### Development Approach
1. **Incremental Development**: Implement features incrementally with testing at each step
2. **Backward Compatibility**: Ensure existing functionality remains intact
3. **Performance First**: Monitor performance throughout development
4. **Test-Driven**: Write tests alongside implementation code
5. **Constitutional Compliance**: Verify all changes comply with Sharp Timer constitution

### Implementation Order
Follow the critical path defined in tasks.md:
1. Core Infrastructure (Tasks 1.1-1.5)
2. Timer State Persistence (Tasks 2.1-2.6)
3. Parallel Development: Quit Dialog, Enhanced Audio, Auto-Switching
4. Integration & System Testing
5. Documentation & Finalization

## File Structure Changes

### New Files to Create
```
sharp_timer/
├── timer_state.py              # NEW: Timer state management
├── quit_dialog.py              # NEW: Quit confirmation dialog
├── mode_transitions.py         # NEW: Automatic mode switching
├── system_events.py            # NEW: System sleep/wake handling
└── enhanced_notifications.py   # NEW: Enhanced audio notifications

tests/                          # NEW: Test directory
├── __init__.py
├── conftest.py                 # pytest configuration
├── unit/
│   ├── __init__.py
│   ├── test_timer_state.py
│   ├── test_quit_dialog.py
│   ├── test_mode_transitions.py
│   ├── test_system_events.py
│   ├── test_enhanced_notifications.py
│   └── test_integration.py
└── fixtures/
    └── sample_settings.json

requirements-dev.txt            # NEW: Development dependencies
```

### Modified Files
```
sharp_timer/
├── main.py                     # Enhanced with new features
├── timer.py                    # Enhanced with state persistence
├── settings.py                 # Enhanced with timer state support
├── notifications.py            # Enhanced with 5-second audio
├── constants.py                # Enhanced with new constants
└── requirements.txt            # Updated dependencies
```

## Detailed Implementation

### 1. Core Infrastructure

#### 1.1 Create TimerState Class

**File**: `sharp_timer/timer_state.py`

```python
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
```

#### 1.2 Enhanced Settings Manager

**File**: `sharp_timer/settings.py` (modifications)

```python
# Add to imports
from timer_state import TimerState, TimerStateManager

# Add to SettingsManager.__init__
def __init__(self):
    # ... existing code ...
    self.timer_state_manager = TimerStateManager()

# Add new methods
def save_timer_state(self, state: TimerState) -> bool:
    """Save timer state using timer state manager."""
    return self.timer_state_manager.save_timer_state(state)

def load_timer_state(self) -> Optional[TimerState]:
    """Load timer state using timer state manager."""
    return self.timer_state_manager.load_timer_state()

def create_timer_state_backup(self, state: TimerState) -> bool:
    """Create backup of timer state."""
    return self.timer_state_manager.create_backup(state)
```

### 2. Quit Confirmation Dialog

#### 2.1 Quit Dialog Manager

**File**: `sharp_timer/quit_dialog.py`

```python
"""Quit confirmation dialog for Sharp Timer."""

import time
import rumps
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
from timer_state import TimerState

class QuitAction(Enum):
    """Available quit dialog actions."""
    STOP_AND_QUIT = "stop_and_quit"
    PRESERVE_AND_QUIT = "preserve_and_quit"
    CANCEL = "cancel"

@dataclass
class QuitDialogResponse:
    """Response from quit confirmation dialog."""
    action: QuitAction
    timer_state_at_decision: TimerState
    timestamp: float
    user_choice_timestamp: float

class QuitDialogManager:
    """Manages quit confirmation dialog."""
    
    def __init__(self, timer_engine, settings_manager):
        self.timer_engine = timer_engine
        self.settings_manager = settings_manager
        self.callback: Optional[Callable[[QuitDialogResponse], None]] = None
    
    def should_show_quit_dialog(self) -> bool:
        """Determine if quit dialog should be shown."""
        return self.timer_engine.is_running() or self.timer_engine.is_paused()
    
    def show_quit_confirmation(self) -> Optional[QuitDialogResponse]:
        """Show quit confirmation dialog to user."""
        if not self.should_show_quit_dialog():
            return None
        
        # Get current timer state
        current_state = self._get_current_timer_state()
        if not current_state:
            return None
        
        # Show custom dialog
        response = self._show_custom_quit_dialog()
        if response:
            quit_response = QuitDialogResponse(
                action=response,
                timer_state_at_decision=current_state,
                timestamp=time.time(),
                user_choice_timestamp=time.time()
            )
            
            # Execute action
            self.execute_quit_action(quit_response)
            
            # Call callback if set
            if self.callback:
                self.callback(quit_response)
            
            return quit_response
        
        return None
    
    def _show_custom_quit_dialog(self) -> Optional[QuitAction]:
        """Show custom quit dialog with three options."""
        # Create custom window with three buttons
        window = rumps.Window(
            title="Timer is active now. Are you sure you want to quit the app?",
            message="Choose how to handle the running timer:",
            default_text="",
            ok="Cancel",
            cancel="Cancel"
        )
        
        # Add custom buttons by modifying the window
        # This is a simplified version - actual implementation may need NSAlert
        response = window.run()
        
        if response.clicked == 1:  # Cancel
            return QuitAction.CANCEL
        
        # For now, return Cancel - actual implementation needs custom dialog
        return QuitAction.CANCEL
    
    def execute_quit_action(self, response: QuitDialogResponse) -> bool:
        """Execute the chosen quit action."""
        try:
            if response.action == QuitAction.STOP_AND_QUIT:
                # Stop timer and quit
                self.timer_engine.stop()
                self.settings_manager.clear_timer_state()
                rumps.quit_application()
                return True
                
            elif response.action == QuitAction.PRESERVE_AND_QUIT:
                # Save timer state and quit
                self.settings_manager.save_timer_state(response.timer_state_at_decision)
                rumps.quit_application()
                return True
                
            elif response.action == QuitAction.CANCEL:
                # Cancel quit operation
                return True
                
        except Exception as e:
            print(f"Error executing quit action: {e}")
            return False
        
        return False
    
    def _get_current_timer_state(self) -> Optional[TimerState]:
        """Get current timer state."""
        try:
            remaining_seconds = self.timer_engine.get_remaining_seconds()[0] * 60 + self.timer_engine.get_remaining_seconds()[1]
            return TimerState(
                mode=self.settings_manager.get_current_mode(),
                remaining_seconds=remaining_seconds,
                is_running=self.timer_engine.is_running(),
                is_paused=self.timer_engine.is_paused(),
                session_id=str(uuid.uuid4()),
                start_timestamp=time.time(),
                last_update_timestamp=time.time(),
                total_duration_seconds=self.settings_manager.get_duration(self.settings_manager.get_current_mode()) * 60
            )
        except Exception:
            return None
    
    def set_callback(self, callback: Callable[[QuitDialogResponse], None]):
        """Set callback for dialog response handling."""
        self.callback = callback
```

### 3. Enhanced Audio Notifications

#### 3.1 Enhanced Notification Manager

**File**: `sharp_timer/enhanced_notifications.py`

```python
"""Enhanced audio notifications for Sharp Timer."""

import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import List
from constants import MODE_NAMES

class SoundFile(Enum):
    """Available system sound files."""
    GLASS = "/System/Library/Sounds/Glass.aiff"
    PING = "/System/Library/Sounds/Ping.aiff"
    PURR = "/System/Library/Sounds/Purr.aiff"
    SOSUMI = "/System/Library/Sounds/Sosumi.aiff"

@dataclass
class AudioNotificationConfig:
    """Configuration for audio notifications."""
    enabled: bool = True
    duration_seconds: int = 5
    primary_sound: SoundFile = SoundFile.GLASS
    fallback_sounds: List[SoundFile] = None
    volume_level: float = 1.0
    
    def __post_init__(self):
        if self.fallback_sounds is None:
            self.fallback_sounds = [SoundFile.PING, SoundFile.PURR]

class EnhancedNotificationManager:
    """Enhanced notification manager with 5-second audio."""
    
    def __init__(self, config: AudioNotificationConfig = None):
        self.config = config or AudioNotificationConfig()
        self._validate_sound_files()
    
    def play_timer_completion_sound(self, mode_name: str, duration_minutes: int) -> bool:
        """Play 5-second sound for timer completion."""
        # Send visual notification first
        self._send_visual_notification(mode_name, duration_minutes)
        
        if not self.config.enabled:
            return False
        
        # Try primary sound
        if self.play_sound_with_duration(self.config.primary_sound, self.config.duration_seconds):
            return True
        
        # Try fallback sounds
        for fallback_sound in self.config.fallback_sounds:
            if self.play_sound_with_duration(fallback_sound, self.config.duration_seconds):
                return True
        
        # Final fallback: system beep
        print('\a')
        return False
    
    def play_sound_with_duration(self, sound_file: SoundFile, duration_seconds: int) -> bool:
        """Play sound for exact duration using subprocess."""
        try:
            # Set volume
            self._set_system_volume(self.config.volume_level)
            
            # Start sound playback
            process = subprocess.Popen(
                ['afplay', sound_file.value],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Stop after specified duration
            def stop_sound():
                time.sleep(duration_seconds)
                if process.poll() is None:
                    process.terminate()
            
            stop_thread = threading.Thread(target=stop_sound, daemon=True)
            stop_thread.start()
            
            return True
            
        except (subprocess.SubprocessError, OSError):
            return False
    
    def _set_system_volume(self, volume_level: float) -> bool:
        """Set system alert volume."""
        try:
            volume_percentage = int(volume_level * 100)
            script = f'''
            tell application "System Events"
                set volume alert volume {volume_percentage}
            end tell
            '''
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def _send_visual_notification(self, mode_name: str, duration_minutes: int):
        """Send visual notification."""
        try:
            rumps.notification(
                title="Sharp Timer",
                subtitle=f"{mode_name} session completed!",
                message=f"You focused for {duration_minutes} minutes",
                sound=False
            )
        except:
            pass  # Silently fail if notification doesn't work
    
    def _validate_sound_files(self):
        """Validate that sound files exist."""
        for sound_file in [self.config.primary_sound] + self.config.fallback_sounds:
            if not Path(sound_file.value).exists():
                print(f"Warning: Sound file not found: {sound_file.value}")
```

### 4. Automatic Mode Switching

#### 4.1 Mode Transition Manager

**File**: `sharp_timer/mode_transitions.py`

```python
"""Automatic mode switching for Sharp Timer."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from timer_state import TimerState

class TimerMode(Enum):
    """Timer mode enumeration."""
    WORK = "work"
    REST_EYES = "rest_eyes"
    LONG_REST = "long_rest"

class TransitionState(Enum):
    """Target state after mode transition."""
    PAUSED = "paused"
    RUNNING = "running"

@dataclass
class ModeTransition:
    """Configuration for mode transition."""
    from_mode: TimerMode
    to_mode: TimerMode
    enabled: bool = True
    target_state: TransitionState = TransitionState.PAUSED
    transition_delay_ms: int = 100

@dataclass
class TransitionResult:
    """Result of mode transition operation."""
    success: bool
    previous_mode: TimerMode
    new_mode: TimerMode
    transition_time_ms: int
    error_message: Optional[str] = None

class ModeTransitionManager:
    """Manages automatic mode switching."""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.transitions = self._load_default_transitions()
    
    def _load_default_transitions(self) -> Dict[str, ModeTransition]:
        """Load default transition configurations."""
        return {
            "work_to_rest_eyes": ModeTransition(
                from_mode=TimerMode.WORK,
                to_mode=TimerMode.REST_EYES,
                enabled=True,
                target_state=TransitionState.PAUSED,
                transition_delay_ms=100
            ),
            "rest_eyes_to_work": ModeTransition(
                from_mode=TimerMode.REST_EYES,
                to_mode=TimerMode.WORK,
                enabled=True,
                target_state=TransitionState.PAUSED,
                transition_delay_ms=100
            ),
            "long_rest_to_work": ModeTransition(
                from_mode=TimerMode.LONG_REST,
                to_mode=TimerMode.WORK,
                enabled=True,
                target_state=TransitionState.PAUSED,
                transition_delay_ms=100
            )
        }
    
    def execute_auto_switch(self, completed_mode: TimerMode, current_timer_state: TimerState) -> Optional[TransitionResult]:
        """Execute automatic mode switch with performance tracking."""
        start_time = time.time()
        
        # Find transition for completed mode
        transition_key = f"{completed_mode.value}_to_"
        for key, transition in self.transitions.items():
            if key.startswith(transition_key) and transition.enabled:
                try:
                    # Apply transition delay
                    if transition.transition_delay_ms > 0:
                        time.sleep(transition.transition_delay_ms / 1000.0)
                    
                    # Execute mode switch
                    new_mode = transition.to_mode
                    current_timer_state.mode = new_mode.value
                    current_timer_state.is_paused = (transition.target_state == TransitionState.PAUSED)
                    current_timer_state.is_running = (transition.target_state == TransitionState.RUNNING)
                    
                    # Update settings
                    self.settings_manager.set_current_mode(new_mode.value)
                    
                    transition_time = int((time.time() - start_time) * 1000)
                    
                    return TransitionResult(
                        success=True,
                        previous_mode=completed_mode,
                        new_mode=new_mode,
                        transition_time_ms=transition_time
                    )
                    
                except Exception as e:
                    return TransitionResult(
                        success=False,
                        previous_mode=completed_mode,
                        new_mode=completed_mode,
                        transition_time_ms=int((time.time() - start_time) * 1000),
                        error_message=str(e)
                    )
        
        return None  # No transition configured
```

### 5. System Events Handling

#### 5.1 System Event Manager

**File**: `sharp_timer/system_events.py`

```python
"""System event handling for Sharp Timer."""

from typing import Optional, Callable
from timer_state import TimerState

class SystemEventManager:
    """Handles system sleep/wake events."""
    
    def __init__(self, timer_state_manager, timer_engine):
        self.timer_state_manager = timer_state_manager
        self.timer_engine = timer_engine
        self.sleep_callback: Optional[Callable] = None
        self.wake_callback: Optional[Callable] = None
        
        # Setup system event monitoring
        self._setup_system_event_monitoring()
    
    def _setup_system_event_monitoring(self):
        """Setup monitoring for system sleep/wake events."""
        try:
            # This is a simplified version
            # Actual implementation would use pyobjc-framework-SystemConfiguration
            from SystemConfiguration import SCDynamicStoreCopyValue, SCDynamicStoreCreate
            from CoreFoundation import CFRunLoopGetCurrent, CFRunLoopRun
            
            # Register for power state changes
            # Implementation details would go here
            pass
        except ImportError:
            print("Warning: System event monitoring not available")
    
    def on_system_sleep(self):
        """Handle system sleep event."""
        try:
            # Save current state before sleep
            current_state = self._get_current_timer_state()
            if current_state:
                current_state.survived_sleep = True
                self.timer_state_manager.save_timer_state(current_state)
            
            if self.sleep_callback:
                self.sleep_callback()
        except Exception as e:
            print(f"Error handling system sleep: {e}")
    
    def on_system_wake(self):
        """Handle system wake event."""
        try:
            # Validate and restore state after wake
            restored_state = self.timer_state_manager.load_timer_state()
            if restored_state and restored_state.survived_sleep:
                # Adjust for sleep duration if needed
                self._adjust_for_sleep_duration(restored_state)
            
            if self.wake_callback:
                self.wake_callback()
        except Exception as e:
            print(f"Error handling system wake: {e}")
    
    def _get_current_timer_state(self) -> Optional[TimerState]:
        """Get current timer state."""
        # Implementation would get current state from timer engine
        pass
    
    def _adjust_for_sleep_duration(self, state: TimerState):
        """Adjust timer state for sleep duration."""
        # Implementation would calculate sleep duration and adjust remaining time
        pass
```

### 6. Enhanced Main Application

#### 6.1 Updated Main Application

**File**: `sharp_timer/main.py` (modifications)

```python
# Add to imports
from timer_state import TimerState
from quit_dialog import QuitDialogManager
from enhanced_notifications import EnhancedNotificationManager, AudioNotificationConfig
from mode_transitions import ModeTransitionManager, TimerMode
from system_events import SystemEventManager

# Modify SharpTimer.__init__
def __init__(self):
    """Initialize the Sharp Timer application with enhancements."""
    super(SharpTimer, self).__init__("⏱️", quit_button=None)
    
    # Initialize components
    self.settings = SettingsManager()
    self.timer = TimerEngine(self._on_timer_complete)
    
    # Initialize enhanced components
    self.quit_dialog_manager = QuitDialogManager(self.timer, self.settings)
    self.notification_manager = EnhancedNotificationManager()
    self.mode_transition_manager = ModeTransitionManager(self.settings)
    self.system_event_manager = SystemEventManager(self.settings, self.timer)
    
    # Application state
    self.current_mode = self.settings.get_current_mode()
    
    # Try to restore timer state
    self._restore_timer_state()
    
    # Set up menu
    self._setup_menu()
    
    # Start update timer for UI
    rumps.Timer(self._update_ui, 1.0).start()

def _restore_timer_state(self):
    """Restore timer state from previous session."""
    saved_state = self.settings.load_timer_state()
    if saved_state and saved_state.is_valid():
        # Restore timer state
        self.current_mode = saved_state.mode
        self.settings.set_current_mode(saved_state.mode)
        
        if saved_state.is_running and not saved_state.is_paused:
            # Resume running timer
            self.timer.start(saved_state.remaining_seconds // 60)
        elif saved_state.is_paused:
            # Set up paused timer
            self.timer.reset()
            # Timer will show remaining time when started
        
        self.update_timer_title()

def _on_timer_complete(self):
    """Enhanced timer completion handler."""
    # Get current state
    current_state = self._get_current_timer_state()
    mode_name = MODE_NAMES.get(self.current_mode, "Session")
    duration = self.settings.get_duration(self.current_mode)
    
    # Play enhanced audio notification
    self.notification_manager.play_timer_completion_sound(mode_name, duration)
    
    # Execute automatic mode switching
    completed_mode = TimerMode(self.current_mode)
    transition_result = self.mode_transition_manager.execute_auto_switch(
        completed_mode, current_state
    )
    
    if transition_result and transition_result.success:
        # Update current mode
        self.current_mode = transition_result.new_mode.value
        self.settings.set_current_mode(self.current_mode)
        
        # Update UI
        self.update_timer_title()
        self._update_menu_labels()
    
    # Update menu to show Start again
    self.menu[MENU_START].title = MENU_START

@rumps.clicked(MENU_QUIT)
def quit_app(self, sender):
    """Quit application with confirmation if needed."""
    response = self.quit_dialog_manager.show_quit_confirmation()
    if response and response.action != QuitAction.CANCEL:
        # Quit action will be executed by the dialog manager
        pass
    # If no response or cancel, do nothing

def _get_current_timer_state(self) -> TimerState:
    """Get current timer state."""
    remaining_seconds = self.timer.get_remaining_time()[0] * 60 + self.timer.get_remaining_time()[1]
    return TimerState(
        mode=self.current_mode,
        remaining_seconds=remaining_seconds,
        is_running=self.timer.is_running(),
        is_paused=self.timer.is_paused(),
        session_id="",  # Will be generated
        start_timestamp=0,  # Will be set
        last_update_timestamp=0,  # Will be set
        total_duration_seconds=self.settings.get_duration(self.current_mode) * 60
    )
```

### 7. Testing Implementation

#### 7.1 Test Configuration

**File**: `tests/conftest.py`

```python
"""pytest configuration for Sharp Timer tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from sharp_timer.settings import SettingsManager
from sharp_timer.timer_state import TimerState, TimerStateManager

@pytest.fixture
def temp_settings_dir():
    """Create temporary settings directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_settings_manager(temp_settings_dir):
    """Create test settings manager."""
    # Mock the settings directory
    original_support_dir = SettingsManager.APP_SUPPORT_DIR
    SettingsManager.APP_SUPPORT_DIR = Path(temp_dir).name
    
    manager = SettingsManager()
    yield manager
    
    # Restore original
    SettingsManager.APP_SUPPORT_DIR = original_support_dir

@pytest.fixture
def sample_timer_state():
    """Create sample timer state for testing."""
    return TimerState(
        mode="work",
        remaining_seconds=1500,
        is_running=True,
        is_paused=False,
        session_id="test-session-123",
        start_timestamp=1699999999.0,
        last_update_timestamp=1700000000.0,
        total_duration_seconds=1500
    )
```

#### 7.2 Unit Tests Example

**File**: `tests/unit/test_timer_state.py`

```python
"""Unit tests for timer state management."""

import pytest
import time
from sharp_timer.timer_state import TimerState, TimerStateManager

class TestTimerState:
    """Test TimerState class."""
    
    def test_timer_state_creation(self):
        """Test creating a timer state."""
        state = TimerState(
            mode="work",
            remaining_seconds=1500,
            is_running=True,
            is_paused=False,
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        
        assert state.mode == "work"
        assert state.remaining_seconds == 1500
        assert state.is_running is True
        assert state.is_paused is False
        assert state.is_valid()
    
    def test_timer_state_validation(self):
        """Test timer state validation."""
        # Valid state
        valid_state = TimerState(
            mode="work",
            remaining_seconds=1500,
            is_running=True,
            is_paused=False,
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        assert valid_state.is_valid()
        
        # Invalid state - running and paused
        invalid_state = TimerState(
            mode="work",
            remaining_seconds=1500,
            is_running=True,
            is_paused=True,  # Both True - invalid
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        assert not invalid_state.is_valid()

class TestTimerStateManager:
    """Test TimerStateManager class."""
    
    def test_save_and_load_timer_state(self, test_settings_manager, sample_timer_state):
        """Test saving and loading timer state."""
        manager = TimerStateManager()
        
        # Save state
        assert manager.save_timer_state(sample_timer_state) is True
        
        # Load state
        loaded_state = manager.load_timer_state()
        assert loaded_state is not None
        assert loaded_state.mode == sample_timer_state.mode
        assert loaded_state.remaining_seconds == sample_timer_state.remaining_seconds
        assert loaded_state.is_valid()
    
    def test_backup_creation(self, test_settings_manager, sample_timer_state):
        """Test creating timer state backup."""
        manager = TimerStateManager()
        
        # Create backup
        assert manager.create_backup(sample_timer_state) is True
        
        # Check backup files exist
        backup_files = list(manager.backup_dir.glob('timer_state_backup_*.json'))
        assert len(backup_files) > 0
```

### 8. Development Dependencies

#### 8.1 Requirements File

**File**: `requirements-dev.txt`

```txt
# Development dependencies for Sharp Timer
pytest>=7.0.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0

# System integration
pyobjc-framework-SystemConfiguration>=8.0

# Code quality
black>=22.0.0
ruff>=0.0.280
mypy>=1.0.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.2.0
```

#### 8.2 Updated Main Requirements

**File**: `sharp_timer/requirements.txt` (additions)

```txt
# Existing dependencies...
rumps>=0.3.0

# New dependencies for enhancements
pyobjc-framework-SystemConfiguration>=8.0
```

## Implementation Checklist

### Pre-Implementation
- [ ] Set up development environment with new dependencies
- [ ] Create backup of existing codebase
- [ ] Set up testing framework
- [ ] Review and understand all contract specifications

### Core Infrastructure
- [ ] Implement TimerState and TimerStateManager
- [ ] Enhance SettingsManager with timer state support
- [ ] Set up atomic file operations
- [ ] Implement backup and recovery mechanism
- [ ] Add system event monitoring

### Feature Implementation
- [ ] Implement quit confirmation dialog
- [ ] Implement enhanced audio notifications
- [ ] Implement automatic mode switching
- [ ] Integrate all features with main application
- [ ] Update UI and menu interactions

### Testing & Quality
- [ ] Write comprehensive unit tests
- [ ] Write integration tests
- [ ] Perform performance testing
- [ ] Test system sleep/wake scenarios
- [ ] Test unexpected termination recovery

### Documentation & Finalization
- [ ] Update user documentation
- [ ] Update API documentation
- [ ] Create release notes
- [ ] Perform final code review
- [ ] Verify constitutional compliance

## Performance Monitoring

### Key Metrics to Monitor
- Timer state save/load performance
- Mode switching latency (<100ms target)
- Audio notification initiation time
- Memory usage during operation
- CPU usage during active timer

### Monitoring Tools
- Python's `time` module for performance measurement
- `memory_profiler` for memory usage
- Custom logging for operation timing
- pytest-benchmark for performance regression testing

## Troubleshooting Guide

### Common Implementation Issues

#### Timer State Persistence Issues
- **Problem**: State not saving correctly
- **Solution**: Check file permissions, verify atomic operations, add logging

#### Audio Notification Issues
- **Problem**: Sound not playing
- **Solution**: Verify sound file paths, check system volume, test fallback mechanism

#### Mode Switching Issues
- **Problem**: Auto-switch not working
- **Solution**: Check transition configuration, verify timer completion events, add debugging

#### System Event Issues
- **Problem**: Sleep/wake not detected
- **Solution**: Verify pyobjc installation, check system permissions, test with manual triggers

This implementation guide provides a comprehensive roadmap for implementing the Sharp Timer enhancements with detailed code examples, testing strategies, and troubleshooting guidance.
   