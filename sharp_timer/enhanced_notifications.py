"""Enhanced audio notifications for Sharp Timer."""

import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from pathlib import Path
from constants import MODE_NAMES


class SoundFile(Enum):
    """Available sound files."""
    CUSTOM_ALARM = "sounds/alarm-327234.mp3"
    GLASS = "/System/Library/Sounds/Glass.aiff"
    PING = "/System/Library/Sounds/Ping.aiff"
    PURR = "/System/Library/Sounds/Purr.aiff"
    SOSUMI = "/System/Library/Sounds/Sosumi.aiff"
    BOTTLE = "/System/Library/Sounds/Bottle.aiff"
    FROG = "/System/Library/Sounds/Frog.aiff"
    POP = "/System/Library/Sounds/Pop.aiff"


@dataclass
class AudioNotificationConfig:
    """Configuration for audio notifications."""
    enabled: bool = True
    duration_seconds: int = 5
    primary_sound: SoundFile = SoundFile.CUSTOM_ALARM
    fallback_sounds: List[SoundFile] = None
    volume_level: float = 1.0
    
    def __post_init__(self):
        if self.fallback_sounds is None:
            self.fallback_sounds = [SoundFile.GLASS, SoundFile.PING, SoundFile.PURR]


class EnhancedNotificationManager:
    """Enhanced notification manager with 5-second audio."""
    
    def __init__(self, config: AudioNotificationConfig = None):
        self.config = config or AudioNotificationConfig()
        self._validate_sound_files()
        self._current_process = None
    
    def play_timer_completion_sound(self, mode_name: str, duration_minutes: int) -> bool:
        """Play 5-second sound for timer completion."""
        # Send visual notification first
        self._send_visual_notification(mode_name, duration_minutes)
        
        if not self.config.enabled:
            return False
        
        # Stop any currently playing sound
        self._stop_current_sound()
        
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
            # Get the correct path for the sound file
            sound_path = self._get_sound_path(sound_file)
            
            # Validate sound file exists
            if not Path(sound_path).exists():
                print(f"Warning: Sound file not found: {sound_path}")
                return False
            
            # Set volume
            self._set_system_volume(self.config.volume_level)
            
            # Start sound playback
            self._current_process = subprocess.Popen(
                ['afplay', sound_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Stop after specified duration
            def stop_sound():
                time.sleep(duration_seconds)
                if self._current_process and self._current_process.poll() is None:
                    self._current_process.terminate()
                    self._current_process = None
            
            stop_thread = threading.Thread(target=stop_sound, daemon=True)
            stop_thread.start()
            
            return True
            
        except (subprocess.SubprocessError, OSError) as e:
            print(f"Error playing sound {sound_file.value}: {e}")
            return False
    
    def _get_sound_path(self, sound_file: SoundFile) -> str:
        """Get the correct path for a sound file."""
        if sound_file == SoundFile.CUSTOM_ALARM:
            # For custom alarm, construct path relative to the script directory
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(script_dir, sound_file.value)
        else:
            # For system sounds, use the absolute path directly
            return sound_file.value
    
    def _stop_current_sound(self):
        """Stop any currently playing sound."""
        if self._current_process and self._current_process.poll() is None:
            self._current_process.terminate()
            self._current_process = None
    
    def _set_system_volume(self, volume_level: float) -> bool:
        """Set system alert volume."""
        try:
            if not 0.0 <= volume_level <= 1.0:
                volume_level = 1.0
            
            volume_percentage = int(volume_level * 100)
            script = f'''
            tell application "System Events"
                set volume alert volume {volume_percentage}
            end tell
            '''
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, timeout=2)
            return True
        except Exception as e:
            print(f"Error setting system volume: {e}")
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
        except Exception as e:
            print(f"Error sending visual notification: {e}")
    
    def _validate_sound_files(self):
        """Validate that sound files exist."""
        all_sounds = [self.config.primary_sound] + self.config.fallback_sounds
        for sound_file in all_sounds:
            sound_path = self._get_sound_path(sound_file)
            if not Path(sound_path).exists():
                print(f"Warning: Sound file not found: {sound_path}")
    
    def test_audio_configuration(self) -> bool:
        """Test current audio configuration."""
        if not self.config.enabled:
            print("Audio notifications are disabled")
            return True
        
        print("Testing audio configuration...")
        
        # Test primary sound
        if self.play_sound_with_duration(self.config.primary_sound, 1):
            print(f"✓ Primary sound works: {self.config.primary_sound.value}")
            return True
        
        # Test fallback sounds
        for i, fallback_sound in enumerate(self.config.fallback_sounds):
            if self.play_sound_with_duration(fallback_sound, 1):
                print(f"✓ Fallback sound {i+1} works: {fallback_sound.value}")
                return True
        
        print("✗ No audio files are working")
        return False
    
    def update_audio_config(self, config: AudioNotificationConfig) -> bool:
        """Update audio notification configuration."""
        if isinstance(config, AudioNotificationConfig):
            self.config = config
            self._validate_sound_files()
            return True
        return False
    
    def get_available_sounds(self) -> List[SoundFile]:
        """Get list of available sound files."""
        available = []
        for sound_file in SoundFile:
            sound_path = self._get_sound_path(sound_file)
            if Path(sound_path).exists():
                available.append(sound_file)
        return available
    
    def set_volume(self, volume_level: float) -> bool:
        """Set volume level for notifications."""
        if 0.0 <= volume_level <= 1.0:
            self.config.volume_level = volume_level
            return self._set_system_volume(volume_level)
        return False
    
    def enable_audio(self, enabled: bool):
        """Enable or disable audio notifications."""
        self.config.enabled = enabled
    
    def is_audio_enabled(self) -> bool:
        """Check if audio notifications are enabled."""
        return self.config.enabled


class NotificationManager:
    """Legacy notification manager with enhanced capabilities."""
    
    def __init__(self):
        self.enhanced_manager = EnhancedNotificationManager()
    
    def notify_timer_complete(self, mode_name: str, duration_minutes: int):
        """Send notification for timer completion (legacy method)."""
        self.enhanced_manager.play_timer_completion_sound(mode_name, duration_minutes)
    
    def send_notification(self, title: str, message: str, subtitle: Optional[str] = None):
        """Send a macOS notification using osascript (legacy method)."""
        try:
            # Build osascript command
            script_parts = ['display notification', f'"{message}"']
            
            if title:
                script_parts.append(f'with title "{title}"')
            
            if subtitle:
                script_parts.append(f'subtitle "{subtitle}"')
            
            script = ' '.join(script_parts)
            
            # Execute notification
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, text=True, timeout=5)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Silently fail if notification doesn't work
            pass
    
    def play_system_sound(self, sound_name: str = "Glass"):
        """Play a system sound (legacy method)."""
        try:
            script = f'''
            tell application "System Events"
                set volume alert volume 100
            end tell
            '''
            subprocess.run(['osascript', '-e', script], 
                         capture_output=True, text=True, timeout=2)
            
            # Play the sound
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], 
                         capture_output=True, timeout=3)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to simple beep
            try:
                subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'], 
                             capture_output=True, timeout=2)
            except:
                # Final fallback - simple beep
                print('\a')
