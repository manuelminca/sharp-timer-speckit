# Sharp Timer Project Brief

## Project Overview

Sharp Timer is a minimalist macOS timer application that runs exclusively in the menu bar, providing a distraction-free productivity tool with three customizable timer modes. The project has evolved from a basic MVP (001-mvp) to an enhanced version (002-enhancements) with advanced state management and workflow features.

## Core Product Vision

A lightweight, unobtrusive timer application that respects macOS design principles while enhancing user productivity through seamless timer state management and intelligent workflow automation.

## Architecture & Technology Stack

### Core Technologies
- **Language**: Python 3.8+
- **Framework**: rumps (macOS menu bar framework)
- **Storage**: JSON file-based persistence in `~/Library/Application Support/Sharp Timer/`
- **Testing**: pytest with pytest-mock and pytest-cov
- **System Integration**: pyobjc-framework-SystemConfiguration for sleep/wake events

### Performance Standards
- < 1% CPU usage during normal operation
- < 50MB memory footprint
- < 100ms response time for user interactions
- < 100ms automatic mode switching
- < 10ms timer state save/load operations

## Product Features

### Core Features (v1.0.0)
- **Menu Bar Exclusive**: Never appears in dock or application switcher
- **Three Timer Modes**:
  - Work Mode (default: 25 minutes)
  - Rest Your Eyes Mode (default: 5 minutes)
  - Long Rest Mode (default: 15 minutes)
- **Customizable Durations**: All modes fully configurable
- **Native Notifications**: macOS notifications on timer completion
- **Settings Persistence**: User preferences saved across restarts

### Enhanced Features (v1.1.0)
- **Timer State Persistence**: Automatic state saving every 30 seconds
- **Quit Confirmation Dialog**: Three-option dialog when quitting with active timer
- **5-Second Audio Notifications**: Extended alarm duration with fallback sounds
- **Automatic Mode Switching**: Seamless transitions between Work and Rest modes
- **System Sleep/Wake Handling**: State preservation across system sleep cycles
- **Backup & Recovery**: Automatic backups and crash recovery mechanisms

## Key User Workflows

### Basic Timer Usage
1. User starts timer from menu bar
2. Timer runs with MM:SS display in menu bar
3. On completion, visual notification appears with sound alert
4. User can manually switch modes or reset timer

### Enhanced Workflow (v1.1.0)
1. User starts Work timer
2. On completion, automatic switch to Rest Your Eyes (paused)
3. User clicks "Start" to begin Rest session
4. On completion, automatic switch back to Work (paused)
5. Seamless continuation without manual mode selection

### Safe Quitting Workflow
1. User attempts to quit while timer is active
2. Confirmation dialog appears with three options:
   - "Stop timer and Quit"
   - "Quit and leave timer running" (preserves state)
   - "Cancel" (continues running)
3. Next launch restores preserved timer state if selected

## Data Model & Persistence

### Core Entities
- **TimerState**: Complete timer session state with metadata
- **QuitDialogResponse**: User choice in quit confirmation
- **ModeTransition**: Configuration for automatic mode switching
- **AudioNotificationConfig**: Sound notification settings

### Persistence Strategy
- **Primary Storage**: `~/Library/Application Support/Sharp Timer/settings.json`
- **Backup Storage**: Automatic backups every 30 seconds during active timer
- **Atomic Operations**: Prevents corruption during writes
- **Validation**: Schema validation on load with fallback to defaults

## Development Standards

### Code Quality
- Modular architecture with clear component separation
- Comprehensive docstrings and type hints
- Unit and integration test coverage
- Performance monitoring and regression testing

### Testing Framework
- **Unit Tests**: pytest with mocking for macOS-specific APIs
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Verify <100ms mode switching requirements
- **Fixtures**: Sample data for consistent testing

### Constitutional Compliance
All development must comply with the Sharp Timer Constitution:
- Menu bar exclusive philosophy
- Minimal resource footprint
- Persistent state management
- Native macOS integration
- Distraction-free interface
- Enhanced user experience

## Project Structure

```
sharp_timer/
├── main.py                     # Enhanced main application
├── timer.py                    # Timer engine
├── settings.py                 # Enhanced settings manager
├── notifications.py            # Legacy notification manager
├── timer_state.py              # Timer state management
├── quit_dialog.py              # Quit confirmation dialog
├── enhanced_notifications.py   # 5-second audio notifications
├── mode_transitions.py         # Automatic mode switching
├── system_events.py            # System sleep/wake handling
├── constants.py                # Application constants
└── requirements.txt            # Dependencies

tests/                          # Test suite
├── unit/                       # Unit tests
├── fixtures/                   # Test data
└── conftest.py                 # Test configuration

specs/                          # Specification documents
├── 001-mvp/                    # Original MVP specifications
└── 002-enhancements/           # Enhanced feature specifications
```

## Current Implementation Status

### ✅ Completed Features
- All MVP features (v1.0.0) fully implemented
- All enhanced features (v1.1.0) fully implemented
- Comprehensive test suite with >90% coverage
- Complete documentation and user guides
- Performance requirements met and verified

### Key Deliverables
- **Timer State Management**: Complete persistence with backup/recovery
- **Quit Dialog**: Three-option confirmation with state preservation
- **Enhanced Audio**: 5-second notifications with fallback system
- **Auto-Switching**: Sub-100ms mode transitions
- **System Integration**: Sleep/wake event handling
- **Testing**: Comprehensive unit and integration tests

## Quality Metrics

### Performance
- ✅ Timer state operations: <10ms
- ✅ Mode switching: <100ms
- ✅ Memory usage: <50MB
- ✅ CPU usage: <1%

### Testing
- ✅ Unit test coverage: >90%
- ✅ Integration tests: All workflows covered
- ✅ Performance tests: All benchmarks met
- ✅ System tests: Sleep/wake scenarios verified

### Documentation
- ✅ User documentation: Complete with troubleshooting
- ✅ Developer documentation: API contracts and implementation guide
- ✅ Specification documents: Comprehensive feature specs
- ✅ Code documentation: Docstrings and type hints

## Future Considerations

### Potential Enhancements
- Custom sound file support
- Timer analytics and usage tracking
- Cloud synchronization (while maintaining local-first philosophy)
- Advanced notification scheduling
- Integration with calendar applications

### Technical Debt
- Monitor performance impact of enhanced features
- Regular testing on new macOS versions
- Dependency updates and security patches
- Code refactoring for maintainability

## Governance

This project follows the Sharp Timer Constitution as the primary guidance for all development decisions. All features must maintain:
- Menu bar exclusivity
- Minimal resource footprint
- Persistent state management
- Native macOS integration
- Distraction-free interface
- Enhanced user experience

Any amendments to the constitution require documentation, approval, and migration plan. Complexity must be justified with clear user value.

---

**Last Updated**: 2025-11-16  
**Version**: 1.1.0 (Enhanced)  
**Status**: Production Ready with Full Feature Implementation
