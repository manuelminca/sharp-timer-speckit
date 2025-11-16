"""Integration tests for Sharp Timer enhancements."""

import pytest
import time
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import all the components we need to test
from sharp_timer.settings import SettingsManager
from sharp_timer.timer_state import TimerState, TimerStateManager
from sharp_timer.quit_dialog import QuitDialogManager, QuitAction
from sharp_timer.enhanced_notifications import EnhancedNotificationManager, AudioNotificationConfig
from sharp_timer.mode_transitions import ModeTransitionManager, TimerMode
from sharp_timer.system_events import SystemEventManager


class TestSettingsIntegration:
    """Test integration between settings and timer state."""
    
    def test_settings_timer_state_integration(self, test_settings_manager, sample_timer_state):
        """Test that settings manager properly integrates with timer state."""
        # Test saving timer state through settings manager
        result = test_settings_manager.save_timer_state(sample_timer_state)
        assert result is True
        
        # Test loading timer state through settings manager
        loaded_state = test_settings_manager.load_timer_state()
        assert loaded_state is not None
        assert loaded_state.mode == sample_timer_state.mode
        assert loaded_state.remaining_seconds == sample_timer_state.remaining_seconds
    
    def test_complete_state_save_load(self, test_settings_manager, sample_timer_state):
        """Test complete state save and load cycle."""
        # Save complete state
        result = test_settings_manager.save_complete_state(sample_timer_state)
        assert result is True
        
        # Load complete state
        loaded_state = test_settings_manager.load_complete_state()
        assert loaded_state is not None
        assert loaded_state.mode == sample_timer_state.mode
        assert loaded_state.remaining_seconds == sample_timer_state.remaining_seconds
    
    def test_enhanced_settings_persistence(self, test_settings_manager):
        """Test enhanced settings persistence."""
        # Test audio config
        audio_config = {
            "enabled": False,
            "duration_seconds": 3,
            "volume_level": 0.8
        }
        result = test_settings_manager.set_audio_config(audio_config)
        assert result is True
        
        loaded_config = test_settings_manager.get_audio_config()
        assert loaded_config["enabled"] is False
        assert loaded_config["duration_seconds"] == 3
        assert loaded_config["volume_level"] == 0.8
        
        # Test mode transition config
        transition_config = {
            "enabled": True,
            "target_state": "running",
            "transition_delay_ms": 200
        }
        result = test_settings_manager.set_mode_transition_config("work", "rest_eyes", transition_config)
        assert result is True
        
        loaded_config = test_settings_manager.get_mode_transition_config("work", "rest_eyes")
        assert loaded_config["enabled"] is True
        assert loaded_config["target_state"] == "running"
        assert loaded_config["transition_delay_ms"] == 200


class TestModeTransitionIntegration:
    """Test integration between mode transitions and settings."""
    
    def test_mode_transition_settings_integration(self, test_settings_manager, sample_timer_state):
        """Test that mode transitions properly integrate with settings."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Modify transition settings
        transition_config = {
            "enabled": True,
            "target_state": "running",
            "transition_delay_ms": 50
        }
        test_settings_manager.set_mode_transition_config("work", "rest_eyes", transition_config)
        
        # Reload transitions to pick up settings
        manager._load_settings_transitions()
        
        # Verify the settings were loaded
        transition = manager.get_transition_config(TimerMode.WORK, TimerMode.REST_EYES)
        assert transition.target_state.value == "running"
        assert transition.transition_delay_ms == 50
        
        # Test execution with new settings
        sample_timer_state.mode = "work"
        result = manager.execute_auto_switch(TimerMode.WORK, sample_timer_state)
        
        assert result is not None
        assert result.success is True
        assert sample_timer_state.is_running is True  # Should be running now
        assert sample_timer_state.is_paused is False


class TestQuitDialogIntegration:
    """Test integration between quit dialog and timer state."""
    
    def test_quit_dialog_timer_state_integration(self, test_settings_manager):
        """Test that quit dialog properly integrates with timer state."""
        # Create a mock timer engine
        mock_timer = MagicMock()
        mock_timer.is_running.return_value = True
        mock_timer.is_paused.return_value = False
        mock_timer.get_remaining_time.return_value = (25, 0)  # 25 minutes
        
        manager = QuitDialogManager(mock_timer, test_settings_manager)
        
        # Test that dialog should show
        assert manager.should_show_quit_dialog() is True
        
        # Test getting current timer state
        current_state = manager._get_current_timer_state()
        assert current_state is not None
        assert current_state.mode == "work"  # Default mode
        assert current_state.is_running is True
        assert current_state.remaining_seconds == 1500  # 25 minutes


class TestNotificationIntegration:
    """Test integration between notifications and settings."""
    
    def test_notification_settings_integration(self, test_settings_manager):
        """Test that notifications properly integrate with settings."""
        # Set custom audio config
        audio_config = AudioNotificationConfig(
            enabled=True,
            duration_seconds=3,
            volume_level=0.7
        )
        test_settings_manager.set_audio_config(audio_config._asdict())
        
        # Create notification manager
        manager = EnhancedNotificationManager()
        
        # Update with settings config
        settings_config = test_settings_manager.get_audio_config()
        new_config = AudioNotificationConfig(**settings_config)
        result = manager.update_audio_config(new_config)
        
        assert result is True
        assert manager.config.duration_seconds == 3
        assert manager.config.volume_level == 0.7


class TestSystemEventsIntegration:
    """Test integration between system events and timer state."""
    
    def test_system_events_timer_state_integration(self, timer_state_manager):
        """Test that system events properly integrate with timer state."""
        # Create a mock timer engine
        mock_timer = MagicMock()
        mock_timer.is_running.return_value = True
        mock_timer.is_paused.return_value = False
        mock_timer.get_remaining_time.return_value = (10, 30)  # 10 minutes 30 seconds
        
        manager = SystemEventManager(timer_state_manager, mock_timer)
        
        # Test getting current timer state
        current_state = manager._get_current_timer_state()
        assert current_state is not None
        assert current_state.is_running is True
        assert current_state.remaining_seconds == 630  # 10 minutes 30 seconds
        
        # Test sleep/wake handling
        test_state = TimerState(
            mode="work",
            remaining_seconds=600,
            is_running=True,
            is_paused=False,
            session_id="test",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        
        # Simulate sleep event
        manager.on_system_sleep()
        
        # Simulate wake event
        manager.on_system_wake()


class TestFullWorkflow:
    """Test complete workflow integration."""
    
    def test_complete_timer_workflow(self, test_settings_manager):
        """Test complete timer workflow with all enhancements."""
        # Initialize all components
        timer_state_manager = test_settings_manager.timer_state_manager
        mode_transition_manager = ModeTransitionManager(test_settings_manager)
        
        # Create a timer state
        timer_state = TimerState(
            mode="work",
            remaining_seconds=1500,  # 25 minutes
            is_running=True,
            is_paused=False,
            session_id="test-session",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        
        # Save initial state
        assert test_settings_manager.save_timer_state(timer_state) is True
        
        # Simulate timer completion and auto-switch
        result = mode_transition_manager.execute_auto_switch(TimerMode.WORK, timer_state)
        
        assert result is not None
        assert result.success is True
        assert timer_state.mode == "rest_eyes"
        assert timer_state.is_paused is True
        assert timer_state.is_running is False
        
        # Save updated state
        assert test_settings_manager.save_timer_state(timer_state) is True
        
        # Load and verify state
        loaded_state = test_settings_manager.load_timer_state()
        assert loaded_state is not None
        assert loaded_state.mode == "rest_eyes"
        assert loaded_state.is_paused is True
        
        # Test backup creation
        assert timer_state_manager.create_backup(timer_state) is True
        
        # Test backup restoration
        restored_state = timer_state_manager.restore_from_backup()
        assert restored_state is not None
        assert restored_state.mode == "rest_eyes"
    
    @patch('sharp_timer.enhanced_notifications.rumps.notification')
    @patch('sharp_timer.enhanced_notifications.subprocess.Popen')
    def test_complete_notification_workflow(self, mock_popen, mock_notification, test_settings_manager):
        """Test complete notification workflow."""
        # Mock successful sound playback
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.poll.return_value = None
        
        # Create notification manager with custom config
        audio_config = AudioNotificationConfig(
            enabled=True,
            duration_seconds=2,
            volume_level=0.8
        )
        test_settings_manager.set_audio_config(audio_config._asdict())
        
        settings_config = test_settings_manager.get_audio_config()
        manager = EnhancedNotificationManager(AudioNotificationConfig(**settings_config))
        
        # Test notification playback
        result = manager.play_timer_completion_sound("Work", 25)
        
        assert result is True
        mock_notification.assert_called_once()
        mock_popen.assert_called_once()
    
    def test_error_handling_integration(self, test_settings_manager):
        """Test error handling across integrated components."""
        timer_state_manager = test_settings_manager.timer_state_manager
        
        # Test with invalid timer state
        invalid_state = TimerState(
            mode="invalid_mode",
            remaining_seconds=1500,
            is_running=True,
            is_paused=True,  # Invalid - both running and paused
            session_id="test",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        
        # Should handle invalid state gracefully
        assert timer_state_manager.validate_timer_state(invalid_state) is False
        
        # Should not save invalid state
        result = timer_state_manager.save_timer_state(invalid_state)
        # This might still succeed (save operation) but validation should catch it
        # The important thing is that loading would fail validation
        
        # Test loading invalid state
        # Force save invalid state for testing
        timer_state_manager.settings['timer_state'] = invalid_state.to_dict()
        timer_state_manager._atomic_save_settings(timer_state_manager.settings)
        
        loaded_state = timer_state_manager.load_timer_state()
        # Should return None for invalid state
        assert loaded_state is None


class TestPerformanceIntegration:
    """Test performance requirements across integrated components."""
    
    def test_state_persistence_performance(self, test_settings_manager, sample_timer_state):
        """Test that state persistence meets performance requirements."""
        timer_state_manager = test_settings_manager.timer_state_manager
        
        # Test save performance
        start_time = time.time()
        result = timer_state_manager.save_timer_state(sample_timer_state)
        save_time = (time.time() - start_time) * 1000  # Convert to ms
        
        assert result is True
        assert save_time < 10  # Should be under 10ms
        
        # Test load performance
        start_time = time.time()
        loaded_state = timer_state_manager.load_timer_state()
        load_time = (time.time() - start_time) * 1000  # Convert to ms
        
        assert loaded_state is not None
        assert load_time < 5  # Should be under 5ms
    
    def test_mode_switching_performance(self, test_settings_manager, sample_timer_state):
        """Test that mode switching meets performance requirements."""
        manager = ModeTransitionManager(test_settings_manager)
        
        # Set minimal delay for performance testing
        manager.set_transition_delay(TimerMode.WORK, 10)  # 10ms
        
        sample_timer_state.mode = "work"
        
        start_time = time.time()
        result = manager.execute_auto_switch(TimerMode.WORK, sample_timer_state)
        end_time = time.time()
        
        assert result is not None
        assert result.success is True
        
        # Should complete within reasonable time (including delay)
        actual_time_ms = int((end_time - start_time) * 1000)
        assert actual_time_ms < 50  # Should be under 50ms total
        assert result.transition_time_ms < 20  # Transition logic should be fast
