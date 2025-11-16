"""Unit tests for enhanced audio notifications."""

import pytest
import time
from unittest.mock import patch, MagicMock
from sharp_timer.enhanced_notifications import (
    EnhancedNotificationManager, AudioNotificationConfig, SoundFile
)


class TestAudioNotificationConfig:
    """Test AudioNotificationConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = AudioNotificationConfig()
        
        assert config.enabled is True
        assert config.duration_seconds == 5
        assert config.primary_sound == SoundFile.GLASS
        assert len(config.fallback_sounds) == 3
        assert config.volume_level == 1.0
    
    def test_custom_config(self):
        """Test custom configuration."""
        fallback_sounds = [SoundFile.PING, SoundFile.PURR]
        config = AudioNotificationConfig(
            enabled=False,
            duration_seconds=3,
            primary_sound=SoundFile.PING,
            fallback_sounds=fallback_sounds,
            volume_level=0.8
        )
        
        assert config.enabled is False
        assert config.duration_seconds == 3
        assert config.primary_sound == SoundFile.PING
        assert config.fallback_sounds == fallback_sounds
        assert config.volume_level == 0.8


class TestEnhancedNotificationManager:
    """Test EnhancedNotificationManager class."""
    
    def test_initialization(self):
        """Test manager initialization."""
        config = AudioNotificationConfig(enabled=True)
        manager = EnhancedNotificationManager(config)
        
        assert manager.config.enabled is True
        assert manager.config.duration_seconds == 5
    
    def test_initialization_with_default_config(self):
        """Test manager initialization with default config."""
        manager = EnhancedNotificationManager()
        
        assert manager.config.enabled is True
        assert manager.config.duration_seconds == 5
        assert manager.config.primary_sound == SoundFile.GLASS
    
    @patch('sharp_timer.enhanced_notifications.rumps.notification')
    def test_play_timer_completion_sound_disabled(self, mock_notification):
        """Test playing sound when disabled."""
        config = AudioNotificationConfig(enabled=False)
        manager = EnhancedNotificationManager(config)
        
        result = manager.play_timer_completion_sound("Work", 25)
        
        assert result is False
        mock_notification.assert_called_once()
    
    @patch('sharp_timer.enhanced_notifications.subprocess.Popen')
    @patch('sharp_timer.enhanced_notifications.Path.exists')
    @patch('sharp_timer.enhanced_notifications.rumps.notification')
    def test_play_timer_completion_sound_success(self, mock_notification, mock_exists, mock_popen):
        """Test successful sound playback."""
        mock_exists.return_value = True
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.poll.return_value = None
        
        manager = EnhancedNotificationManager()
        result = manager.play_timer_completion_sound("Work", 25)
        
        assert result is True
        mock_notification.assert_called_once()
        mock_popen.assert_called_once()
    
    @patch('sharp_timer.enhanced_notifications.subprocess.Popen')
    @patch('sharp_timer.enhanced_notifications.Path.exists')
    @patch('sharp_timer.enhanced_notifications.rumps.notification')
    def test_play_timer_completion_sound_fallback(self, mock_notification, mock_exists, mock_popen):
        """Test fallback sound when primary fails."""
        # Primary sound doesn't exist
        mock_exists.side_effect = [False, True, True]  # GLASS fails, PING succeeds
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.poll.return_value = None
        
        manager = EnhancedNotificationManager()
        result = manager.play_timer_completion_sound("Work", 25)
        
        assert result is True
        mock_notification.assert_called_once()
        # Should try fallback
        assert mock_popen.call_count == 1
    
    @patch('sharp_timer.enhanced_notifications.subprocess.Popen')
    @patch('sharp_timer.enhanced_notifications.Path.exists')
    @patch('sharp_timer.enhanced_notifications.rumps.notification')
    def test_play_timer_completion_sound_all_fail(self, mock_notification, mock_exists, mock_popen):
        """Test when all sounds fail."""
        mock_exists.return_value = False  # All sounds don't exist
        
        manager = EnhancedNotificationManager()
        result = manager.play_timer_completion_sound("Work", 25)
        
        assert result is False
        mock_notification.assert_called_once()
        mock_popen.assert_not_called()
    
    @patch('sharp_timer.enhanced_notifications.subprocess.run')
    def test_set_system_volume(self, mock_run):
        """Test setting system volume."""
        mock_run.return_value = MagicMock()
        manager = EnhancedNotificationManager()
        
        result = manager.set_volume(0.8)
        
        assert result is True
        mock_run.assert_called_once()
        
        # Check that the script contains the correct volume
        call_args = mock_run.call_args[0][1]
        assert '80' in call_args  # 80% volume
    
    def test_set_volume_invalid(self):
        """Test setting invalid volume."""
        manager = EnhancedNotificationManager()
        
        # Test invalid volumes
        assert manager.set_volume(-0.1) is False
        assert manager.set_volume(1.1) is False
    
    def test_enable_disable_audio(self):
        """Test enabling and disabling audio."""
        manager = EnhancedNotificationManager()
        
        # Test disable
        manager.enable_audio(False)
        assert manager.is_audio_enabled() is False
        
        # Test enable
        manager.enable_audio(True)
        assert manager.is_audio_enabled() is True
    
    def test_update_audio_config(self):
        """Test updating audio configuration."""
        manager = EnhancedNotificationManager()
        new_config = AudioNotificationConfig(enabled=False, duration_seconds=3)
        
        result = manager.update_audio_config(new_config)
        
        assert result is True
        assert manager.config.enabled is False
        assert manager.config.duration_seconds == 3
    
    def test_update_audio_config_invalid(self):
        """Test updating with invalid config."""
        manager = EnhancedNotificationManager()
        
        result = manager.update_audio_config("invalid")
        
        assert result is False
    
    @patch('sharp_timer.enhanced_notifications.Path.exists')
    def test_get_available_sounds(self, mock_exists):
        """Test getting available sounds."""
        # Mock some sounds as existing
        def exists_side_effect(path):
            return "Glass.aiff" in path or "Ping.aiff" in path
        
        mock_exists.side_effect = exists_side_effect
        
        manager = EnhancedNotificationManager()
        available = manager.get_available_sounds()
        
        assert len(available) == 2
        assert SoundFile.GLASS in available
        assert SoundFile.PING in available
        assert SoundFile.PURR not in available
    
    @patch('sharp_timer.enhanced_notifications.subprocess.Popen')
    @patch('sharp_timer.enhanced_notifications.Path.exists')
    def test_stop_current_sound(self, mock_exists, mock_popen):
        """Test stopping currently playing sound."""
        mock_exists.return_value = True
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.poll.return_value = None
        
        manager = EnhancedNotificationManager()
        
        # Start a sound
        manager.play_sound_with_duration(SoundFile.GLASS, 5)
        
        # Stop it
        manager._stop_current_sound()
        
        mock_process.terminate.assert_called_once()
    
    def test_test_audio_configuration(self):
        """Test testing audio configuration."""
        manager = EnhancedNotificationManager()
        
        # Test with disabled audio
        manager.config.enabled = False
        result = manager.test_audio_configuration()
        assert result is True
        
        # Test with enabled audio (will try to play sound)
        manager.config.enabled = True
        # This will fail in test environment, but should not crash
        result = manager.test_audio_configuration()
        # Result depends on system sound availability


class TestNotificationManager:
    """Test legacy NotificationManager integration."""
    
    @patch('sharp_timer.enhanced_notifications.EnhancedNotificationManager.play_timer_completion_sound')
    def test_notify_timer_complete(self, mock_play_sound):
        """Test legacy notify_timer_complete method."""
        from sharp_timer.enhanced_notifications import NotificationManager
        
        manager = NotificationManager()
        manager.notify_timer_complete("Work", 25)
        
        mock_play_sound.assert_called_once_with("Work", 25)
    
    @patch('sharp_timer.enhanced_notifications.subprocess.run')
    def test_send_notification(self, mock_run):
        """Test legacy send_notification method."""
        from sharp_timer.enhanced_notifications import NotificationManager
        
        manager = NotificationManager()
        manager.send_notification("Test Title", "Test Message", "Test Subtitle")
        
        mock_run.assert_called_once()
    
    @patch('sharp_timer.enhanced_notifications.subprocess.run')
    def test_play_system_sound(self, mock_run):
        """Test legacy play_system_sound method."""
        from sharp_timer.enhanced_notifications import NotificationManager
        
        manager = NotificationManager()
        manager.play_system_sound("Glass")
        
        # Should be called twice - once for volume, once for sound
        assert mock_run.call_count == 2
