"""macOS notifications and sound alerts for Sharp Timer."""

import subprocess
from typing import Optional


class NotificationManager:
    """Manages macOS notifications and sound alerts."""
    
    @staticmethod
    def send_notification(title: str, message: str, subtitle: Optional[str] = None):
        """Send a macOS notification using osascript.
        
        Args:
            title: Notification title
            message: Notification message
            subtitle: Optional subtitle
        """
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
    
    @staticmethod
    def play_system_sound(sound_name: str = "Glass"):
        """Play a system sound.
        
        Args:
            sound_name: Name of the system sound to play
        """
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
    
    @staticmethod
    def notify_timer_complete(mode_name: str, duration_minutes: int):
        """Send notification for timer completion.
        
        Args:
            mode_name: Name of the completed mode
            duration_minutes: Duration that was completed
        """
        title = "Sharp Timer"
        message = f"{mode_name} session completed!"
        subtitle = f"You focused for {duration_minutes} minutes"
        
        NotificationManager.send_notification(title, message, subtitle)
        NotificationManager.play_system_sound()
