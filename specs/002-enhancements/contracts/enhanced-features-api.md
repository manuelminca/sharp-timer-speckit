# Enhanced Features API Contract

**Version**: 1.0  
**Date**: 2025-11-14  
**Components**: Audio Notifications & Auto Mode Switching

## Overview

This contract defines the API interfaces for enhanced audio notifications (5-second duration) and automatic mode switching between timer modes.

## Audio Notification Interface

### EnhancedNotificationManager

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

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

class EnhancedNotificationManager(ABC):
    """Abstract interface for enhanced audio notifications."""
    
    @abstractmethod
    def play_timer_completion_sound(self, mode_name: str, duration_minutes: int) -> bool:
        """Play 5-second sound for timer completion.
        
        Args:
            mode_name: Name of completed timer mode
            duration_minutes: Duration that was completed
            
        Returns:
            True if sound played successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def play_sound_with_duration(self, sound_file: SoundFile, duration_seconds: int) -> bool:
        """Play sound for specific duration.
        
        Args:
            sound_file: Sound file to play
            duration_seconds: Duration to play sound
            
        Returns:
            True if sound played successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def test_audio_configuration(self) -> bool:
        """Test current audio configuration.
        
        Returns:
            True if configuration is working, False otherwise
        """
        pass
    
    @abstractmethod
    def update_audio_config(self, config: AudioNotificationConfig) -> bool:
        """Update audio notification configuration.
        
        Args:
            config: New audio configuration
            
        Returns:
            True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_available_sounds(self) -> List[SoundFile]:
        """Get list of available sound files.
        
        Returns:
            List of available sound files
        """
        pass
```

## Automatic Mode Switching Interface

### ModeTransitionManager

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum

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

class ModeTransitionManager(ABC):
    """Abstract interface for automatic mode switching."""
    
    @abstractmethod
    def execute_auto_switch(self, completed_mode: TimerMode, current_timer_state: 'TimerState') -> Optional[TransitionResult]:
        """Execute automatic mode switch after timer completion.
        
        Args:
            completed_mode: Mode that just completed
            current_timer_state: Current timer state
            
        Returns:
            TransitionResult if switch executed, None if no switch configured
        """
        pass
    
    @abstractmethod
    def get_transition_config(self, from_mode: TimerMode, to_mode: TimerMode) -> Optional[ModeTransition]:
        """Get transition configuration for mode pair.
        
        Args:
            from_mode: Source mode
            to_mode: Target mode
            
        Returns:
            ModeTransition if configured, None otherwise
        """
        pass
    
    @abstractmethod
    def set_transition_config(self, transition: ModeTransition) -> bool:
        """Set transition configuration.
        
        Args:
            transition: Transition configuration to set
            
        Returns:
            True if set successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_auto_switch_enabled(self, from_mode: TimerMode) -> bool:
        """Check if auto-switch is enabled for mode.
        
        Args:
            from_mode: Mode to check
            
        Returns:
            True if auto-switch enabled, False otherwise
        """
        pass
    
    @abstractmethod
    def get_all_transitions(self) -> Dict[str, ModeTransition]:
        """Get all configured transitions.
        
        Returns:
            Dictionary of all transitions
        """
        pass
```

## Implementation Requirements

### Audio Notification Implementation

```python
class EnhancedNotificationManagerImpl(EnhancedNotificationManager):
    """Implementation of enhanced audio notifications."""
    
    def __init__(self, config: AudioNotificationConfig):
        self.config = config
        self._validate_sound_files()
    
    def play_timer_completion_sound(self, mode_name: str, duration_minutes: int) -> bool:
        """Play 5-second sound with fallback handling."""
        # Send visual notification first
        self._send_visual_notification(mode_name, duration_minutes)
        
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
            import subprocess
            import threading
            import time
            
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
            import subprocess
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
```

### Mode Switching Implementation

```python
class ModeTransitionManagerImpl(ModeTransitionManager):
    """Implementation of automatic mode switching."""
    
    def __init__(self):
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
    
    def execute_auto_switch(self, completed_mode: TimerMode, current_timer_state: 'TimerState') -> Optional[TransitionResult]:
        """Execute automatic mode switch with performance tracking."""
        import time
        
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
                    # Update timer state with new mode
                    current_timer_state.mode = new_mode.value
                    current_timer_state.is_paused = (transition.target_state == TransitionState.PAUSED)
                    current_timer_state.is_running = (transition.target_state == TransitionState.RUNNING)
                    
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
                        new_mode=completed_mode,  # No change
                        transition_time_ms=int((time.time() - start_time) * 1000),
                        error_message=str(e)
                    )
        
        return None  # No transition configured
```

## Integration with Main Application

### Enhanced Timer Engine

```python
class EnhancedTimerEngine(TimerEngine):
    """Timer engine with enhanced features."""
    
    def __init__(self, completion_callback, 
                 notification_manager: EnhancedNotificationManager,
                 mode_transition_manager: ModeTransitionManager):
        super().__init__(completion_callback)
        self.notification_manager = notification_manager
        self.mode_transition_manager = mode_transition_manager
    
    def _on_timer_complete(self):
        """Enhanced timer completion handler."""
        # Get current state
        current_state = self.get_current_timer_state()
        mode_name = MODE_NAMES.get(current_state.mode, "Session")
        
        # Play enhanced audio notification
        self.notification_manager.play_timer_completion_sound(
            mode_name, 
            current_state.total_duration_seconds // 60
        )
        
        # Execute automatic mode switching
        completed_mode = TimerMode(current_state.mode)
        transition_result = self.mode_transition_manager.execute_auto_switch(
            completed_mode, current_state
        )
        
        if transition_result and transition_result.success:
            # Update UI with new mode
            self._update_mode_display(transition_result.new_mode)
        
        # Call original completion callback
        self.completion_callback()
```

## Performance Requirements

### Audio Notifications
- **Sound Initiation**: < 50ms from trigger to sound start
- **Duration Accuracy**: ±100ms for 5-second duration
- **Volume Setting**: < 20ms for volume adjustment
- **Fallback Switching**: < 200ms between sound attempts

### Mode Switching
- **Transition Execution**: < 100ms total (including delay)
- **State Update**: < 10ms for timer state modification
- **UI Update**: < 50ms for mode display update
- **Configuration Lookup**: < 1ms for transition retrieval

## Testing Requirements

### Audio Notification Tests
- `test_play_5second_sound_success`
- `test_play_5second_sound_fallback`
- `test_volume_adjustment`
- `test_sound_file_validation`
- `test_audio_configuration_update`
- `test_visual_notification_with_audio`

### Mode Switching Tests
- `test_auto_switch_work_to_rest_eyes`
- `test_auto_switch_rest_eyes_to_work`
- `test_auto_switch_long_rest_to_work`
- `test_disabled_auto_switch`
- `test_transition_delay_accuracy`
- `test_transition_performance_requirements`

### Integration Tests
- `test_timer_completion_with_enhanced_features`
- `test_mode_switching_with_state_persistence`
- `test_audio_notification_during_mode_switch`
- `test_system_integration_performance`
- `test_error_handling_and_recovery`

## Error Handling

### Audio Notification Errors
- **Sound File Missing**: Automatic fallback to next sound
- **Audio System Unavailable**: Visual notification only
- **Permission Denied**: Log error, continue with visual notification
- **Volume Control Failure**: Play at current system volume

### Mode Switching Errors
- **Invalid Transition**: Log error, continue without switching
- **State Update Failure**: Retry once, then log error
- **UI Update Failure**: Log error, state still updated
- **Configuration Corruption**: Reload defaults, log error

## Configuration Schema

```json
{
  "audio_notifications": {
    "enabled": true,
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
      "enabled": true,
      "target_state": "paused",
      "transition_delay_ms": 100
    },
    "rest_eyes_to_work": {
      "enabled": true,
      "target_state": "paused",
      "transition_delay_ms": 100
    },
    "long_rest_to_work": {
      "enabled": true,
      "target_state": "paused",
      "transition_delay_ms": 100
    }
  }
}
