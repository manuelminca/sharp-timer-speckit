"""Unit tests for automatic mode switching."""

import pytest
import time
from unittest.mock import MagicMock
from sharp_timer.mode_transitions import (
    ModeTransitionManager, ModeTransition, TransitionResult, 
    TimerMode, TransitionState
)
from sharp_timer.timer_state import TimerState


class TestModeTransition:
    """Test ModeTransition class."""
    
    def test_default_transition(self):
        """Test default transition configuration."""
        transition = ModeTransition(
            from_mode=TimerMode.WORK,
            to_mode=TimerMode.REST_EYES
        )
        
        assert transition.from_mode == TimerMode.WORK
        assert transition.to_mode == TimerMode.REST_EYES
        assert transition.enabled is True
        assert transition.target_state == TransitionState.PAUSED
        assert transition.transition_delay_ms == 100
    
    def test_custom_transition(self):
        """Test custom transition configuration."""
        transition = ModeTransition(
            from_mode=TimerMode.WORK,
            to_mode=TimerMode.REST_EYES,
            enabled=False,
            target_state=TransitionState.RUNNING,
            transition_delay_ms=200
        )
        
        assert transition.enabled is False
        assert transition.target_state == TransitionState.RUNNING
        assert transition.transition_delay_ms == 200


class TestTransitionResult:
    """Test TransitionResult class."""
    
    def test_successful_transition(self):
        """Test successful transition result."""
        result = TransitionResult(
            success=True,
            previous_mode=TimerMode.WORK,
            new_mode=TimerMode.REST_EYES,
            transition_time_ms=50
        )
        
        assert result.success is True
        assert result.previous_mode == TimerMode.WORK
        assert result.new_mode == TimerMode.REST_EYES
        assert result.transition_time_ms == 50
        assert result.error_message is None
    
    def test_failed_transition(self):
        """Test failed transition result."""
        result = TransitionResult(
            success=False,
            previous_mode=TimerMode.WORK,
            new_mode=TimerMode.WORK,
            transition_time_ms=25,
            error_message="Test error"
        )
        
        assert result.success is False
        assert result.error_message == "Test error"


class TestModeTransitionManager:
    """Test ModeTransitionManager class."""
    
    def test_initialization(self, test_settings_manager):
        """Test manager initialization."""
        manager = ModeTransitionManager(test_settings_manager)
        
        assert len(manager.transitions) == 3
        assert "work_to_rest_eyes" in manager.transitions
        assert "rest_eyes_to_work" in manager.transitions
        assert "long_rest_to_work" in manager.transitions
    
    def test_get_transition_config(self, test_settings_manager):
        """Test getting transition configuration."""
        manager = ModeTransitionManager(test_settings_manager)
        
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        assert transition is not None
        assert transition.from_mode == TimerMode.WORK
        assert transition.to_mode == TimerMode.REST_EYES
        assert transition.enabled is True
        
        # Test non-existent transition
        transition = manager.get_transition_config(TimerMode.REST_EYES, TimerMode.LONG_REST)
        assert transition is None
    
    def test_set_transition_config(self, test_settings_manager):
        """Test setting transition configuration."""
        manager = ModeTransitionManager(test_settings_manager)
        
        new_transition = ModeTransition(
            from_mode=TimerMode.WORK,
            to_mode=TimerMode.REST_EYES,
            enabled=False,
            target_state=TransitionState.RUNNING,
            transition_delay_ms=300
        )
        
        result = manager.set_transition_config(new_transition)
        assert result is True
        
        # Verify the change
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        assert transition.enabled is False
        assert transition.target_state == TransitionState.RUNNING
        assert transition.transition_delay_ms == 300
    
    def test_execute_auto_switch_success(self, test_settings_manager, sample_timer_state):
        """Test successful automatic mode switch."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Set up sample state for work mode
        sample_timer_state.mode = "work"
        
        result = manager.execute_auto_switch(TimerMode.WORK, sample_timer_state)
        
        assert result is not None
        assert result.success is True
        assert result.previous_mode == TimerMode.WORK
        assert result.new_mode == TimerMode.REST_EYES
        assert result.transition_time_ms >= 0
        
        # Verify state was updated
        assert sample_timer_state.mode == "rest_eyes"
        assert sample_timer_state.is_paused is True
        assert sample_timer_state.is_running is False
    
    def test_execute_auto_switch_disabled(self, test_settings_manager, sample_timer_state):
        """Test auto switch when disabled."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Disable the transition
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        transition.enabled = False
        manager.set_transition_config(transition)
        
        sample_timer_state.mode = "work"
        
        result = manager.execute_auto_switch(TimerMode.WORK, sample_timer_state)
        
        assert result is None  # No transition executed
        
        # Verify state was not changed
        assert sample_timer_state.mode == "work"
    
    def test_execute_auto_switch_no_config(self, test_settings_manager, sample_timer_state):
        """Test auto switch with no configuration."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Try a transition that doesn't exist
        result = manager.execute_auto_switch(TimerMode.REST_EYES, TimerMode.LONG_REST, sample_timer_state)
        
        assert result is None
    
    def test_is_auto_switch_enabled(self, test_settings_manager):
        """Test checking if auto-switch is enabled."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Should be enabled by default
        assert manager.is_auto_switch_enabled(TimerMode.WORK) is True
        assert manager.is_auto_switch_enabled(TimerMode.REST_EYES) is True
        assert manager.is_auto_switch_enabled(TimerMode.LONG_REST) is True
    
    def test_enable_auto_switch(self, test_settings_manager):
        """Test enabling/disabling auto-switch."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Disable auto-switch for work mode
        result = manager.enable_auto_switch(TimerMode.WORK, False)
        assert result is True
        assert manager.is_auto_switch_enabled(TimerMode.WORK) is False
        
        # Re-enable
        result = manager.enable_auto_switch(TimerMode.WORK, True)
        assert result is True
        assert manager.is_auto_switch_enabled(TimerMode.WORK) is True
    
    def test_set_transition_delay(self, test_settings_manager):
        """Test setting transition delay."""
        manager = ModeTransitionManager(test_settings_manager)
        
        result = manager.set_transition_delay(TimerMode.WORK, 200)
        assert result is True
        
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        assert transition.transition_delay_ms == 200
        
        # Test invalid delay
        result = manager.set_transition_delay(TimerMode.WORK, -10)
        assert result is False
        
        result = manager.set_transition_delay(TimerMode.WORK, 10000)
        assert result is False
    
    def test_set_target_state(self, test_settings_manager):
        """Test setting target state."""
        manager = ModeTransitionManager(test_settings_manager)
        
        result = manager.set_target_state(TimerMode.WORK, TransitionState.RUNNING)
        assert result is True
        
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        assert transition.target_state == TransitionState.RUNNING
    
    def test_get_next_mode(self, test_settings_manager):
        """Test getting next mode."""
        manager = ModeTransitionManager(test_settings_manager)
        
        next_mode = manager.get_next_mode(TimerMode.WORK)
        assert next_mode == TimerMode.REST_EYES
        
        next_mode = manager.get_next_mode(TimerMode.REST_EYES)
        assert next_mode == TimerMode.WORK
        
        next_mode = manager.get_next_mode(TimerMode.LONG_REST)
        assert next_mode == TimerMode.WORK
    
    def test_get_next_mode_disabled(self, test_settings_manager):
        """Test getting next mode when disabled."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Disable work transitions
        manager.enable_auto_switch(TimerMode.WORK, False)
        
        next_mode = manager.get_next_mode(TimerMode.WORK)
        assert next_mode is None
    
    def test_get_all_transitions(self, test_settings_manager):
        """Test getting all transitions."""
        manager = ModeTransitionManager(test_settings_manager)
        
        all_transitions = manager.get_all_transitions()
        
        assert len(all_transitions) == 3
        assert "work_to_rest_eyes" in all_transitions
        assert "rest_eyes_to_work" in all_transitions
        assert "long_rest_to_work" in all_transitions
        
        # Verify it's a copy (changes to returned dict don't affect original)
        all_transitions["test"] = "test"
        assert "test" not in manager.transitions
    
    def test_reset_to_defaults(self, test_settings_manager):
        """Test resetting to defaults."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Modify a transition
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        transition.enabled = False
        transition.transition_delay_ms = 500
        manager.set_transition_config(transition)
        
        # Reset to defaults
        manager.reset_to_defaults()
        
        # Verify reset
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        assert transition.enabled is True
        assert transition.transition_delay_ms == 100
    
    def test_transition_performance(self, test_settings_manager, sample_timer_state):
        """Test transition performance requirements."""
        manager = ModeTransitionManager(test_settings_manager)
        
        sample_timer_state.mode = "work"
        
        start_time = time.time()
        result = manager.execute_auto_switch(TimerMode.WORK, sample_timer_state)
        end_time = time.time()
        
        # Should complete quickly (under 100ms including delay)
        actual_time_ms = int((end_time - start_time) * 1000)
        expected_time_ms = 100  # Default delay
        
        # Allow some tolerance for test environment
        assert actual_time_ms >= expected_time_ms
        assert actual_time_ms < expected_time_ms + 50  # 50ms tolerance
        
        if result:
            assert result.transition_time_ms < 150  # Should be fast
    
    def test_multiple_transitions(self, test_settings_manager, sample_timer_state):
        """Test multiple consecutive transitions."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Work -> Rest Eyes
        sample_timer_state.mode = "work"
        result1 = manager.execute_auto_switch(TimerMode.WORK, sample_timer_state)
        
        assert result1 is not None
        assert result1.success is True
        assert sample_timer_state.mode == "rest_eyes"
        
        # Rest Eyes -> Work
        result2 = manager.execute_auto_switch(TimerMode.REST_EYES, sample_timer_state)
        
        assert result2 is not None
        assert result2.success is True
        assert sample_timer_state.mode == "work"
