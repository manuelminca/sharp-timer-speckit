# Quickstart Guide: Sharp Timer Enhancements

**Version**: 1.0  
**Date**: 2025-11-14  
**Feature**: 002-enhancements

## Overview

This guide provides a quick introduction to the enhanced Sharp Timer features, including timer state persistence, quit confirmation dialog, 5-second audio notifications, and automatic mode switching.

## New Features Summary

### 1. Timer State Persistence
- Timer state is automatically saved every 30 seconds
- Timer state is preserved across application restarts
- Recovery after unexpected application termination
- System sleep/wake event handling

### 2. Quit Confirmation Dialog
- Appears when attempting to quit with an active timer
- Three options: Stop timer and Quit, Quit and leave timer running, Cancel
- Timer state preservation option for seamless workflow continuation

### 3. Enhanced Audio Notifications
- 5-second alarm sound duration (increased from ~1 second)
- Multiple fallback sound files for reliability
- Volume control integration
- Visual notifications always appear even if audio fails

### 4. Automatic Mode Switching
- Work → Rest Your Eyes (paused) after Work timer completion
- Rest Your Eyes → Work (paused) after Rest Eyes timer completion
- Long Rest → Work (paused) after Long Rest timer completion
- Single-click start to begin the pre-filled timer

## User Workflow

### Basic Timer Usage (Enhanced)

1. **Start Timer**: Click "Start" to begin your Work session
2. **Timer Completion**: 
   - 5-second audio notification plays
   - Visual notification appears
   - Mode automatically switches to Rest Your Eyes (paused)
3. **Continue Workflow**: Click "Start" to begin Rest Your Eyes session
4. **Repeat**: Automatic switching continues between Work and Rest modes

### Quitting with Active Timer

1. **Attempt to Quit**: Click "Quit" while timer is running
2. **Confirmation Dialog**: Choose your preferred option:
   - **Stop timer and Quit**: Ends current session and quits
   - **Quit and leave timer running**: Preserves timer state for next launch
   - **Cancel**: Returns to application with timer running
3. **Next Launch**: If preserved, timer resumes with remaining time

### System Integration

1. **System Sleep**: Timer state is automatically saved before sleep
2. **System Wake**: Timer state is restored and validated after wake
3. **Application Crash**: Timer state can be recovered on next launch
4. **Settings Migration**: Existing settings are preserved and enhanced

## Installation & Setup

### Prerequisites
- macOS 10.14 or later
- Python 3.8 or later
- Existing Sharp Timer installation

### Upgrade Process
```bash
# Navigate to Sharp Timer directory
cd sharp_timer

# Install new dependencies
pip install -r requirements.txt

# Run enhanced version
python main.py
```

### New Dependencies
```bash
# Testing framework (for development)
pip install pytest pytest-mock pytest-cov

# System event monitoring (for sleep/wake handling)
pip install pyobjc-framework-SystemConfiguration
```

## Configuration

### Enhanced Settings Structure

Settings are now stored in `~/Library/Application Support/Sharp Timer/settings.json` with enhanced structure:

```json
{
  "work_duration": 25,
  "rest_eyes_duration": 5,
  "long_rest_duration": 15,
  "current_mode": "work",
  
  "timer_state": {
    "mode": "work",
    "remaining_seconds": 1500,
    "is_running": true,
    "is_paused": false,
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  
  "audio_config": {
    "enabled": true,
    "duration_seconds": 5,
    "volume_level": 1.0
  },
  
  "mode_transitions": {
    "work_to_rest_eyes": {
      "enabled": true,
      "target_state": "paused"
    }
  },
  
  "system_integration": {
    "handle_sleep_events": true,
    "preserve_state_across_restarts": true,
    "quit_confirmation_enabled": true
  }
}
```

### Customizing Audio Notifications

1. **Access Settings**: Click "Settings..." in menu
2. **Audio Configuration**: Modify duration and volume preferences
3. **Sound Selection**: Choose from system sounds or custom files
4. **Test Configuration**: Use test button to verify audio setup

### Configuring Mode Switching

1. **Auto-Switch Toggle**: Enable/disable automatic mode switching
2. **Target State**: Choose paused or running state after switch
3. **Transition Delay**: Adjust delay between timer completion and mode switch
4. **Per-Mode Configuration**: Configure behavior for each timer mode

## Troubleshooting

### Common Issues

#### Timer State Not Preserved
**Symptoms**: Timer resets to default after restart
**Solutions**:
1. Check file permissions: `~/Library/Application Support/Sharp Timer/`
2. Verify settings.json is not corrupted
3. Ensure application has write permissions
4. Check disk space availability

#### Audio Notifications Not Working
**Symptoms**: No sound on timer completion
**Solutions**:
1. Check system volume and mute settings
2. Verify sound files exist in `/System/Library/Sounds/`
3. Test with different sound files
4. Check audio permissions in System Preferences

#### Auto Mode Switching Not Working
**Symptoms**: Mode doesn't change after timer completion
**Solutions**:
1. Verify auto-switch is enabled in settings
2. Check transition configuration for specific modes
3. Ensure timer completion event is firing
4. Review mode transition logs

#### Quit Dialog Not Appearing
**Symptoms**: Application quits immediately without confirmation
**Solutions**:
1. Verify quit confirmation is enabled in settings
2. Check if timer is actually running/paused
3. Review quit dialog configuration
4. Test with active timer session

### Debug Information

#### Enable Debug Logging
```python
# In main.py, add debug mode
DEBUG = True

# Debug logs will appear in:
# ~/Library/Logs/Sharp Timer/debug.log
```

#### Check Timer State
```python
# Timer state file location
TIMER_STATE_FILE = "~/Library/Application Support/Sharp Timer/timer_state.json"

# Backup files location
BACKUP_DIR = "~/Library/Application Support/Sharp Timer/backups/"
```

#### System Event Monitoring
```python
# Check if sleep/wake events are being handled
# Look for logs in Console.app with "Sharp Timer" filter
```

## Development Guide

### Project Structure
```
sharp_timer/
├── main.py              # Enhanced with quit dialog and auto-switching
├── timer.py             # Timer engine with state persistence
├── settings.py          # Enhanced settings manager
├── notifications.py     # 5-second audio notifications
├── constants.py         # Application constants
├── timer_state.py       # NEW: Timer state management
├── quit_dialog.py       # NEW: Quit confirmation dialog
├── mode_transitions.py  # NEW: Automatic mode switching
└── system_events.py     # NEW: System sleep/wake handling

tests/                  # NEW: Test suite
├── unit/
├── integration/
└── fixtures/
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sharp_timer

# Run specific test file
pytest tests/unit/test_timer_state.py
```

### Development Workflow
1. **Feature Development**: Implement in feature branch
2. **Unit Testing**: Write comprehensive unit tests
3. **Integration Testing**: Test feature interactions
4. **Performance Testing**: Verify <100ms mode switching
5. **User Acceptance Testing**: Verify workflow improvements

## Performance Metrics

### Target Performance
- **Timer State Save**: < 10ms
- **Timer State Load**: < 5ms
- **Mode Switching**: < 100ms
- **Audio Initiation**: < 50ms
- **Quit Dialog Display**: < 100ms

### Monitoring
- CPU usage should remain < 1%
- Memory usage should remain < 50MB
- File operations should be atomic
- No memory leaks during extended use

## Migration from Previous Version

### Automatic Migration
- Existing settings are preserved
- New configuration sections added with defaults
- Timer state history starts fresh
- No user action required

### Manual Configuration (Optional)
- Enable/disable new features as preferred
- Customize audio notification settings
- Configure mode switching behavior
- Set up quit confirmation preferences

## Support & Feedback

### Issue Reporting
1. Check troubleshooting section first
2. Collect debug logs and system information
3. Document reproduction steps
4. Report through GitHub issues or support channel

### Feature Requests
1. Review existing feature requests
2. Provide detailed use case description
3. Consider constitutional compliance
4. Submit through appropriate channels

## FAQ

**Q: Will my existing timer settings be preserved?**
A: Yes, all existing settings are automatically preserved during upgrade.

**Q: Can I disable the quit confirmation dialog?**
A: Yes, it can be disabled in settings, but keeping it enabled is recommended for data safety.

**Q: What happens if the system crashes during a timer?**
A: Timer state is automatically backed up every 30 seconds and can be recovered on next launch.

**Q: Can I customize the 5-second audio duration?**
A: Yes, the duration can be customized in audio settings from 1-10 seconds.

**Q: Will automatic mode switching work with custom timer durations?**
A: Yes, mode switching works with any timer duration configuration.

**Q: How much additional disk space is used for state persistence?**
A: Less than 1MB for all state files and backups combined.

**Q: Is the enhanced version compatible with older macOS versions?**
A: The enhanced version requires macOS 10.14 or later for system event integration.
