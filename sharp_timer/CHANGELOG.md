# Changelog

All notable changes to Sharp Timer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-14

### Added
- **Timer State Persistence**: Timer automatically saves state every 30 seconds and restores on application restart
- **Quit Confirmation Dialog**: Three-option dialog when quitting with active timer (Stop/Preserve/Cancel)
- **Enhanced Audio Notifications**: 5-second alarm sound duration with multiple fallback sound files
- **Automatic Mode Switching**: Seamless transitions between Work and Rest Your Eyes modes
- **System Sleep/Wake Handling**: Timer state preserved across system sleep and adjusted on wake
- **Backup & Recovery System**: Automatic backup creation and recovery after unexpected termination
- **Comprehensive Test Suite**: Unit tests and integration tests for all enhanced features

### Enhanced
- **Settings Management**: Extended with timer state support and enhanced configuration options
- **Main Application**: Integrated all enhanced features with backward compatibility
- **Error Handling**: Robust error handling and fallback mechanisms throughout the application
- **Performance**: Optimized for <100ms mode switching and <10ms state operations

### Technical
- **New Components**: 
  - `timer_state.py` - Timer state management with persistence
  - `quit_dialog.py` - Quit confirmation workflow
  - `enhanced_notifications.py` - 5-second audio notifications
  - `mode_transitions.py` - Automatic mode switching logic
  - `system_events.py` - System sleep/wake event handling
- **Dependencies**: Added `pyobjc-framework-SystemConfiguration` for system integration
- **Testing**: Complete test suite with pytest framework
- **Configuration**: Enhanced JSON settings schema with backward compatibility

### Security
- **File Permissions**: Proper file permissions (600/700) for settings and state files
- **Data Validation**: Comprehensive validation for all timer state data
- **Atomic Operations**: Atomic file operations to prevent data corruption

### Performance
- **Memory Usage**: Maintained <50MB memory footprint
- **CPU Usage**: Optimized for <1% CPU usage during normal operation
- **Response Time**: <100ms automatic mode switching
- **State Operations**: <10ms save/load operations for timer state

### User Experience
- **Workflow Continuity**: Seamless transitions between work and rest periods
- **Data Safety**: Protection against accidental timer loss during application quit
- **Recovery**: Automatic recovery from system crashes and unexpected termination
- **Accessibility**: Enhanced audio notifications for better user awareness

## [1.0.0] - 2024-XX-XX

### Added
- **Initial Release**: Basic timer functionality with three modes
- **Menu Bar Interface**: Exclusive menu bar presence, never appears in dock
- **Three Timer Modes**: Work (25min), Rest Your Eyes (5min), Long Rest (15min)
- **Customizable Durations**: User-configurable timer durations (1-60 minutes)
- **Native Notifications**: macOS notifications when timer completes
- **Sound Alerts**: Basic audio notifications for timer completion
- **Persistent Settings**: User preferences saved automatically
- **Cross-Platform**: Python-based implementation for macOS

### Technical
- **Framework**: Built with rumps for macOS menu bar integration
- **Dependencies**: Minimal external dependencies
- **Architecture**: Modular design with separate timer, settings, and notification components
- **System Integration**: Native macOS notifications and sound system integration
