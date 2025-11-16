"""Automatic mode switching for Sharp Timer."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from constants import MODE_WORK, MODE_REST_EYES, MODE_LONG_REST
from timer_state import TimerState


class TimerMode(Enum):
    """Timer mode enumeration."""
    WORK = MODE_WORK
    REST_EYES = MODE_REST_EYES
    LONG_REST = MODE_LONG_REST


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
        self._load_settings_transitions()
    
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
    
    def _load_settings_transitions(self):
        """Load transition configurations from settings."""
        try:
            config = self.settings_manager.get_mode_transition_config("work", "rest_eyes")
            if config:
                self.transitions["work_to_rest_eyes"].enabled = config.get("enabled", True)
                self.transitions["work_to_rest_eyes"].target_state = TransitionState(
                    config.get("target_state", "paused")
                )
                self.transitions["work_to_rest_eyes"].transition_delay_ms = config.get(
                    "transition_delay_ms", 100
                )
            
            config = self.settings_manager.get_mode_transition_config("rest_eyes", "work")
            if config:
                self.transitions["rest_eyes_to_work"].enabled = config.get("enabled", True)
                self.transitions["rest_eyes_to_work"].target_state = TransitionState(
                    config.get("target_state", "paused")
                )
                self.transitions["rest_eyes_to_work"].transition_delay_ms = config.get(
                    "transition_delay_ms", 100
                )
            
            config = self.settings_manager.get_mode_transition_config("long_rest", "work")
            if config:
                self.transitions["long_rest_to_work"].enabled = config.get("enabled", True)
                self.transitions["long_rest_to_work"].target_state = TransitionState(
                    config.get("target_state", "paused")
                )
                self.transitions["long_rest_to_work"].transition_delay_ms = config.get(
                    "transition_delay_ms", 100
                )
        except Exception as e:
            print(f"Error loading settings transitions: {e}")
    
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
    
    def get_transition_config(self, from_mode: TimerMode, to_mode: TimerMode) -> Optional[ModeTransition]:
        """Get transition configuration for mode pair."""
        transition_key = f"{from_mode.value}_to_{to_mode.value}"
        return self.transitions.get(transition_key)
    
    def set_transition_config(self, transition: ModeTransition) -> bool:
        """Set transition configuration."""
        try:
            transition_key = f"{transition.from_mode.value}_to_{transition.to_mode.value}"
            self.transitions[transition_key] = transition
            
            # Save to settings
            config = {
                "enabled": transition.enabled,
                "target_state": transition.target_state.value,
                "transition_delay_ms": transition.transition_delay_ms
            }
            self.settings_manager.set_mode_transition_config(
                transition.from_mode.value, 
                transition.to_mode.value, 
                config
            )
            
            return True
        except Exception as e:
            print(f"Error setting transition config: {e}")
            return False
    
    def is_auto_switch_enabled(self, from_mode: TimerMode) -> bool:
        """Check if auto-switch is enabled for mode."""
        transition_key = f"{from_mode.value}_to_"
        for key, transition in self.transitions.items():
            if key.startswith(transition_key):
                return transition.enabled
        return False
    
    def get_all_transitions(self) -> Dict[str, ModeTransition]:
        """Get all configured transitions."""
        return self.transitions.copy()
    
    def enable_auto_switch(self, from_mode: TimerMode, enabled: bool) -> bool:
        """Enable or disable auto-switch for a specific mode."""
        transition_key = f"{from_mode.value}_to_"
        updated = False
        
        for key, transition in self.transitions.items():
            if key.startswith(transition_key):
                transition.enabled = enabled
                updated = True
                
                # Save to settings
                config = {
                    "enabled": enabled,
                    "target_state": transition.target_state.value,
                    "transition_delay_ms": transition.transition_delay_ms
                }
                self.settings_manager.set_mode_transition_config(
                    transition.from_mode.value,
                    transition.to_mode.value,
                    config
                )
        
        return updated
    
    def set_transition_delay(self, from_mode: TimerMode, delay_ms: int) -> bool:
        """Set transition delay for a specific mode."""
        if delay_ms < 0 or delay_ms > 5000:  # Reasonable limits
            return False
        
        transition_key = f"{from_mode.value}_to_"
        updated = False
        
        for key, transition in self.transitions.items():
            if key.startswith(transition_key):
                transition.transition_delay_ms = delay_ms
                updated = True
                
                # Save to settings
                config = {
                    "enabled": transition.enabled,
                    "target_state": transition.target_state.value,
                    "transition_delay_ms": delay_ms
                }
                self.settings_manager.set_mode_transition_config(
                    transition.from_mode.value,
                    transition.to_mode.value,
                    config
                )
        
        return updated
    
    def set_target_state(self, from_mode: TimerMode, target_state: TransitionState) -> bool:
        """Set target state for transitions from a specific mode."""
        transition_key = f"{from_mode.value}_to_"
        updated = False
        
        for key, transition in self.transitions.items():
            if key.startswith(transition_key):
                transition.target_state = target_state
                updated = True
                
                # Save to settings
                config = {
                    "enabled": transition.enabled,
                    "target_state": target_state.value,
                    "transition_delay_ms": transition.transition_delay_ms
                }
                self.settings_manager.set_mode_transition_config(
                    transition.from_mode.value,
                    transition.to_mode.value,
                    config
                )
        
        return updated
    
    def get_next_mode(self, current_mode: TimerMode) -> Optional[TimerMode]:
        """Get the next mode that will be switched to."""
        transition_key = f"{current_mode.value}_to_"
        for key, transition in self.transitions.items():
            if key.startswith(transition_key) and transition.enabled:
                return transition.to_mode
        return None
    
    def reset_to_defaults(self):
        """Reset all transitions to default configurations."""
        self.transitions = self._load_default_transitions()
        
        # Save defaults to settings
        for transition in self.transitions.values():
            config = {
                "enabled": transition.enabled,
                "target_state": transition.target_state.value,
                "transition_delay_ms": transition.transition_delay_ms
            }
            self.settings_manager.set_mode_transition_config(
                transition.from_mode.value,
                transition.to_mode.value,
                config
            )
