# Sharp Timer

A minimalist macOS timer app that runs exclusively in the menu bar with enhanced productivity features.

## Features

### Core Features
- **Menu Bar Only**: Never appears in the dock
- **Three Modes**: Work (25min), Rest Your Eyes (5min), Long Rest (15min)
- **Customizable**: Adjust duration for each mode
- **Native Notifications**: macOS notifications when timer completes
- **Sound Alerts**: Enhanced audio notifications when sessions complete
- **Persistent Settings**: Your preferences are saved automatically

### Enhanced Features (v1.1.0)
- **Timer State Persistence**: Timer automatically saves state every 30 seconds
- **Quit Confirmation Dialog**: Protects against accidental timer loss when quitting
- **5-Second Audio Notifications**: Extended audio alerts for better awareness
- **Automatic Mode Switching**: Seamless transitions between Work and Rest modes
- **System Sleep/Wake Handling**: Timer state preserved across system sleep
- **Backup & Recovery**: Automatic backup creation and crash recovery

## Installation

1. Clone or download this repository
2. Install Python 3.8 or later
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python main.py
   ```

## Usage

### Basic Usage
1. **Start Timer**: Click "Start" in the menu bar
2. **Switch Modes**: Select from Work, Rest Your Eyes, or Long Rest
3. **Customize**: Choose "Settings..." to adjust durations
4. **Pause/Resume**: Click "Start" again to pause or resume

### Enhanced Workflow
1. **Automatic Mode Switching**: When Work timer completes, Rest Your Eyes mode is automatically selected and paused
2. **Seamless Continuation**: Click "Start" to begin the next session without manual mode selection
3. **State Persistence**: Timer state is automatically saved and restored if the app is restarted
4. **Safe Quitting**: When quitting with an active timer, choose how to handle the running timer

### Quit Options
When quitting with an active timer, you can choose from:
- **Stop timer and Quit**: Ends current session and quits
- **Quit and leave timer running**: Preserves timer state for next launch
- **Cancel**: Returns to the application with timer running

## Customization

### Timer Durations
All timer modes are fully customizable:

- Work Mode: Default 25 minutes
- Rest Your Eyes Mode: Default 5 minutes
- Long Rest Mode: Default 15 minutes

Access Settings from the menu bar to adjust any duration between 1-60 minutes.

### Enhanced Settings
The enhanced version includes additional customization options stored in `~/Library/Application Support/Sharp Timer/settings.json`:

- **Audio Notifications**: Configure 5-second alert duration and volume
- **Mode Transitions**: Enable/disable automatic mode switching
- **System Integration**: Configure sleep/wake handling and quit confirmation

## System Requirements

- macOS 10.14 or later
- Python 3.8 or later
- Dependencies: `rumps` and `pyobjc-framework-SystemConfiguration`

## Development

### Running Tests
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=sharp_timer
```

### Project Structure
```
sharp_timer/
├── main.py                     # Enhanced main application
├── timer.py                    # Timer engine
├── settings.py                 # Enhanced settings with timer state support
├── notifications.py            # Legacy notification manager
├── timer_state.py              # NEW: Timer state management
├── quit_dialog.py              # NEW: Quit confirmation dialog
├── enhanced_notifications.py   # NEW: 5-second audio notifications
├── mode_transitions.py         # NEW: Automatic mode switching
├── system_events.py            # NEW: System sleep/wake handling
├── constants.py                # Application constants
└── requirements.txt            # Dependencies

tests/                          # NEW: Test suite
├── unit/                       # Unit tests
├── fixtures/                   # Test data
└── conftest.py                 # Test configuration
```

## Troubleshooting

### Timer State Not Preserved
- Check file permissions: `~/Library/Application Support/Sharp Timer/`
- Verify settings.json is not corrupted
- Ensure application has write permissions

### Audio Notifications Not Working
- Check system volume and mute settings
- Verify sound files exist in `/System/Library/Sounds/`
- Test with different sound files in settings

### Auto Mode Switching Not Working
- Verify auto-switch is enabled in settings
- Check transition configuration for specific modes
- Ensure timer completion event is firing

### System Sleep Issues
- Timer state is automatically saved before sleep
- State is restored and adjusted after wake
- No manual intervention required

## Version History

### v1.1.0 (Current)
- Added timer state persistence across application restarts
- Implemented quit confirmation dialog with three options
- Enhanced audio notifications to 5-second duration
- Added automatic mode switching between Work and Rest modes
- Implemented system sleep/wake event handling
- Added comprehensive backup and recovery system

### v1.0.0
- Initial release with basic timer functionality
- Three timer modes with customizable durations
- Native macOS notifications and sound alerts
- Menu bar exclusive interface

## License

MIT License
