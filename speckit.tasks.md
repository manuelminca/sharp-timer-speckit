# Sharp Timer Implementation Tasks

## Phase 1: Core Setup & Basic Functionality

### Environment Setup
- [ ] Create project directory structure
- [ ] Set up virtual environment
- [ ] Install minimal dependencies (`rumps`)
- [ ] Create basic README.md with project description

### Core Timer Engine
- [ ] Implement `TimerEngine` class
- [ ] Create timer start/pause/resume/reset functionality
- [ ] Implement time tracking and countdown logic
- [ ] Add mode switching capability (Work/Rest Your Eyes/Long Rest)
- [ ] Create timer event callbacks

### Settings Management
- [ ] Implement `SettingsManager` class
- [ ] Create default settings configuration
- [ ] Implement JSON file persistence
- [ ] Add settings validation
- [ ] Create atomic file writing for settings
- [ ] Implement settings migration capability

### Menu Bar Integration
- [ ] Set up basic `rumps` application
- [ ] Create menu structure
- [ ] Implement timer display in menu bar
- [ ] Add mode indicators
- [ ] Implement basic menu actions

## Phase 2: Feature Implementation

### Mode System
- [ ] Implement Work mode (25 min)
- [ ] Implement Rest Your Eyes mode (5 min)
- [ ] Implement Long Rest mode (15 min)
- [ ] Create mode switching UI
- [ ] Add mode duration customization

### Notification System
- [ ] Implement macOS native notifications
- [ ] Add sound alerts
- [ ] Create notification preferences
- [ ] Implement notification handling for mode completion

### Settings UI
- [ ] Create settings dialog
- [ ] Implement duration adjustment controls
- [ ] Add notification preferences toggles
- [ ] Create reset to defaults functionality

### State Management
- [ ] Implement application state persistence
- [ ] Add session tracking
- [ ] Create graceful shutdown handling
- [ ] Implement startup state restoration

## Phase 3: Optimization & Polish

### Performance Optimization
- [ ] Profile application for CPU usage
- [ ] Optimize memory footprint
- [ ] Improve startup time
- [ ] Reduce UI update frequency

### Error Handling
- [ ] Implement comprehensive error logging
- [ ] Add graceful error recovery
- [ ] Create user-friendly error messages
- [ ] Implement crash prevention mechanisms

### UI Polish
- [ ] Refine menu bar appearance
- [ ] Improve mode indicators
- [ ] Enhance settings dialog
- [ ] Add subtle animations for state changes

### Testing
- [ ] Write unit tests for timer logic
- [ ] Create integration tests for settings persistence
- [ ] Implement UI interaction tests
- [ ] Perform performance benchmarking

## Phase 4: Packaging & Distribution

### Application Packaging
- [ ] Configure PyInstaller
- [ ] Create standalone macOS application
- [ ] Set up code signing
- [ ] Prepare for notarization

### Documentation
- [ ] Complete inline code documentation
- [ ] Create user guide
- [ ] Add installation instructions
- [ ] Document customization options

### Distribution
- [ ] Create DMG installer
- [ ] Prepare for Mac App Store submission
- [ ] Set up GitHub repository
- [ ] Create release notes

### Final Testing
- [ ] Perform clean installation testing
- [ ] Test on multiple macOS versions
- [ ] Validate all features
- [ ] Conduct long-running stability tests

## Specific Implementation Tasks

### Task 1: Create Basic Menu Bar App
```python
# main.py
import rumps

class SharpTimer(rumps.App):
    def __init__(self):
        super(SharpTimer, self).__init__("⏱️", quit_button=None)
        self.menu = ["Start", "Reset", None, "Work (25m)", "Rest Eyes (5m)", "Long Rest (15m)", None, "Quit"]
        
    @rumps.clicked("Start")
    def start_timer(self, _):
        # Implement timer start logic
        pass
        
    @rumps.clicked("Reset")
    def reset_timer(self, _):
        # Implement timer reset logic
        pass
        
    @rumps.clicked("Quit")
    def quit_app(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    SharpTimer().run()
```

### Task 2: Implement Timer Engine
```python
# timer.py
import threading
import time

class TimerEngine:
    def __init__(self, callback):
        self.callback = callback
        self.duration = 0
        self.remaining = 0
        self.running = False
        self.timer = None
        
    def start(self, duration):
        self.duration = duration * 60  # Convert to seconds
        self.remaining = self.duration
        self.running = True
        self._schedule_tick()
        
    def _schedule_tick(self):
        if self.running:
            self.timer = threading.Timer(1.0, self._tick)
            self.timer.daemon = True
            self.timer.start()
            
    def _tick(self):
        if self.running:
            self.remaining -= 1
            if self.remaining <= 0:
                self.running = False
                self.callback()
            else:
                self._schedule_tick()
```

### Task 3: Implement Settings Manager
```python
# settings.py
import json
import os
import shutil

class SettingsManager:
    def __init__(self):
        self.app_support_dir = os.path.expanduser("~/Library/Application Support/Sharp Timer")
        self.settings_file = os.path.join(self.app_support_dir, "settings.json")
        self.defaults = {
            "work_duration": 25,
            "rest_eyes_duration": 5,
            "long_rest_duration": 15,
            "current_mode": "work",
            "notifications_enabled": True,
            "sound_enabled": True
        }
        self.settings = self.defaults.copy()
        self._ensure_dir_exists()
        self.load_settings()
        
    def _ensure_dir_exists(self):
        if not os.path.exists(self.app_support_dir):
            os.makedirs(self.app_support_dir)
            
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Update only keys that exist in defaults
                    for key in self.defaults:
                        if key in loaded:
                            self.settings[key] = loaded[key]
        except Exception:
            # If loading fails, use defaults
            self.settings = self.defaults.copy()
            
    def save_settings(self):
        try:
            # Write to temp file first
            temp_file = self.settings_file + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            # Then move to replace the original
            shutil.move(temp_file, self.settings_file)
        except Exception:
            # If saving fails, just continue with current settings
            pass
```

### Task 4: Implement Notification System
```python
# notifications.py
import subprocess

def send_notification(title, message):
    """Send a macOS notification using osascript"""
    script = f'''
    display notification "{message}" with title "{title}"
    '''
    subprocess.run(["osascript", "-e", script])
    
def play_sound():
    """Play a system sound"""
    script = '''
    beep
    '''
    subprocess.run(["osascript", "-e", script])
```

### Task 5: Integrate Components
```python
# Integration of timer, settings, and menu bar
import rumps
from timer import TimerEngine
from settings import SettingsManager
from notifications import send_notification, play_sound

class SharpTimer(rumps.App):
    def __init__(self):
        super(SharpTimer, self).__init__("⏱️", quit_button=None)
        
        # Initialize components
        self.settings = SettingsManager()
        self.timer = TimerEngine(self.timer_completed)
        
        # Set up menu
        self.menu = [
            "Start",
            "Reset",
            None,
            "Work Mode",
            "Rest Your Eyes Mode",
            "Long Rest Mode",
            None,
            "Settings...",
            "Quit"
        ]
        
        # Set current mode
        self.current_mode = self.settings.settings["current_mode"]
        self.update_title()
        
    def update_title(self):
        """Update the menu bar title with current time"""
        if self.timer.running:
            mins, secs = divmod(self.timer.remaining, 60)
            self.title = f"{mins:02d}:{secs:02d}"
        else:
            mode_durations = {
                "work": self.settings.settings["work_duration"],
                "rest_eyes": self.settings.settings["rest_eyes_duration"],
                "long_rest": self.settings.settings["long_rest_duration"]
            }
            duration = mode_durations.get(self.current_mode, 25)
            self.title = f"{duration:02d}:00"
    
    def timer_completed(self):
        """Handle timer completion"""
        mode_names = {
            "work": "Work",
            "rest_eyes": "Rest Your Eyes",
            "long_rest": "Long Rest"
        }
        
        # Send notification
        if self.settings.settings["notifications_enabled"]:
            send_notification(
                "Sharp Timer", 
                f"{mode_names.get(self.current_mode, 'Session')} completed!"
            )
            
        # Play sound
        if self.settings.settings["sound_enabled"]:
            play_sound()
            
        # Update UI
        self.update_title()
```

## Testing Tasks

### Unit Testing
- [ ] Test timer accuracy
- [ ] Validate settings persistence
- [ ] Verify mode switching logic
- [ ] Test notification system

### Integration Testing
- [ ] Test full application workflow
- [ ] Verify settings UI functionality
- [ ] Test menu bar interactions
- [ ] Validate notification delivery

### Performance Testing
- [ ] Measure startup time
- [ ] Monitor memory usage
- [ ] Track CPU utilization
- [ ] Test long-running stability

## Documentation Tasks

- [ ] Create installation guide
- [ ] Document configuration options
- [ ] Create user manual
- [ ] Add developer documentation

## Milestone Checklist

### Milestone 1: Basic Functionality
- [ ] App runs in menu bar only
- [ ] Timer counts down correctly
- [ ] Three modes are implemented
- [ ] Settings persist between sessions

### Milestone 2: Complete Feature Set
- [ ] All modes function correctly
- [ ] Notifications work properly
- [ ] Settings UI is complete
- [ ] Performance is optimized

### Milestone 3: Release Ready
- [ ] Packaging is complete
- [ ] Documentation is finished
- [ ] All tests pass
- [ ] App is stable and reliable
