<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0 (minor version for feature additions)
- List of modified principles: 
  - Enhanced Principle 3: "Distraction-Free Interface" → "Persistent State Management"
  - Added Principle 6: "Enhanced User Experience"
- Added sections: Enhanced notification requirements, Quit confirmation workflow
- Removed sections: N/A
- Templates requiring updates: 
  ✅ .specify/templates/plan-template.md (Constitution Check section)
  ✅ .specify/templates/spec-template.md (scope/requirements alignment)
  ✅ .specify/templates/tasks-template.md (task categorization)
  ⚠️ Command files may need review for principle references
- Follow-up TODOs: None
-->

# Sharp Timer Constitution

## Vision Statement

Sharp Timer is a minimalist macOS timer app that runs exclusively in the menu bar, never appearing in the dock. It provides a distraction-free timer experience with three customizable modes: Work, Rest Your Eyes, and Long Rest, designed to enhance productivity while maintaining minimal system impact and seamless user experience.

## Core Design Principles

### 1. Menu Bar Exclusive Philosophy
The application exists exclusively in the macOS menu bar, never appearing in the dock or application switcher. Zero system tray presence beyond menu bar with single-click access to all core functionality. Clean, unobtrusive presence that respects screen real estate.

### 2. Minimal Resource Footprint
Optimized for low CPU and memory usage, running as an efficient background daemon. Zero friction startup and operation with efficient event handling and state management.

### 3. Persistent State Management
Timer state and configuration MUST persist across application restarts. When closing with active timer, users MUST be presented with clear options for handling the running timer. Session state recovery after system restart is non-negotiable. Configuration persistence in user preferences with current session state recovery after restart.

### 4. Native macOS Integration
Respect macOS design language and aesthetics with native notifications. Consistent with system UI patterns and behaviors. Graceful handling of system events and proper integration with macOS lifecycle.

### 5. Distraction-Free Interface
Display only essential information at all times. Timer display in MM:SS format with current session status indicator (Work/Rest Your Eyes/Long Rest). No unnecessary visual elements or animations. Clean, unobtrusive presence that respects screen real estate.

### 6. Enhanced User Experience
Timer transitions MUST be seamless with automatic mode switching. Work timer completion MUST automatically set Rest Your Eyes mode in paused state. Rest Your Eyes completion MUST prefill Work mode in paused state. Improved audio alerts MUST sound for 5 seconds on completion.

## Functional Requirements

### Timer Management
- **Work Mode**: Default 25-minute focused work periods
- **Rest Your Eyes Mode**: Default 5-minute eye rest periods
- **Long Rest Mode**: Default 15-minute extended rest periods
- **Three-Mode System**: Clear distinction between Work, Rest Your Eyes, and Long Rest
- **Manual Control**: Start, pause, resume, and reset functionality

### Configurable Intervals
- Customizable Work mode duration (default: 25 minutes)
- Customizable Rest Your Eyes mode duration (default: 5 minutes)
- Customizable Long Rest mode duration (default: 15 minutes)
- Settings persistence across app restarts
- Real-time configuration updates without timer restart

### Session Tracking
- Current session progress indicator with automatic mode switching
- Work timer completion MUST automatically set Rest Your Eyes mode in paused state
- Rest Your Eyes completion MUST prefill Work mode in paused state
- Long Rest completion MUST prefill Work mode in paused state

### Enhanced Notification System
- Audio alerts for session completion MUST play for exactly 5 seconds
- macOS native notifications with session type
- Configurable notification preferences
- Graceful handling of missed notifications
- Visual notification must appear even if audio is not heard

### Quit Confirmation Workflow
- When timer is active and user attempts to quit, MUST display confirmation dialog
- Dialog message: "Timer is active now. Are you sure you want to quit the app?"
- Three options MUST be provided:
  - "Stop timer and Quit" - stops timer and quits application
  - "Quit and leave timer running" - preserves timer state for next launch
  - "Cancel" - closes dialog and continues running with timer active

## Technical Quality Standards

### Lightweight Architecture
- Minimal dependency footprint
- Efficient Python libraries for macOS integration
- Optimized timer implementation with minimal CPU usage
- Memory-efficient state management

### Graceful Degradation
- Robust error handling for timer interruptions
- State recovery after system sleep/wake
- System MUST recover timer state after unexpected application termination
- System MUST handle system sleep/wake events without losing timer state

### Lazy Loading Strategy
- Initialize components only when required
- Deferred loading of non-critical features
- Memory-efficient resource management
- Fast application startup times

## User Experience Guidelines

### Intuitive Defaults
- Work: 25 minutes, Rest Your Eyes: 5 minutes, Long Rest: 15 minutes
- Three-mode system ready immediately
- Sensible default settings for new users
- Progressive disclosure of advanced features
- Zero-configuration initial experience

### Visual Feedback
- Clear MM:SS timer display in menu bar
- Mode indicators (💼 Work, 👁️ Rest Your Eyes, 🌟 Long Rest)
- Progress visualization through menu bar icon
- Subtle animations for mode changes

### One-Click Interactions
- Primary actions accessible via single menu click
- Contextual menu options based on timer state
- Quick settings access without deep navigation
- Users MUST be able to start pre-filled timer with single click after automatic switching

## Development Constraints

### Technology Stack
- Python 3.8+ compatibility requirement
- Preference for built-in macOS libraries (rumps framework)
- Minimal external dependencies
- Built exclusively for macOS platform

### Code Quality Standards
- Clean, documented code structure with comprehensive docstrings and type hints
- Modular architecture for maintainability
- Consistent coding style and conventions
- Unit tests for core timer logic
- Integration tests for macOS integration

### Testing Requirements
- Unit tests for core timer logic
- Integration tests for macOS integration
- Performance testing for resource usage
- User acceptance testing for workflows

### Performance Benchmarks
- < 1% CPU usage during normal operation
- < 50MB memory footprint
- < 2 second application startup time
- < 100ms response time for user interactions
- Automatic mode switching MUST occur within 100ms of timer completion

## Architecture Principles

### Component Separation
- Timer engine separate from UI components
- Configuration management isolated from core logic
- Notification system as independent module
- Timer state management as independent module

### Event-Driven Design
- Reactive architecture for timer events
- Loose coupling between components
- Observable state management
- Efficient event propagation

### Error Handling Strategy
- Fail-safe operation for timer continuity
- Graceful degradation for non-critical features
- Comprehensive logging for debugging
- User-friendly error messages

## Security and Privacy

### Data Protection
- Local storage only (no cloud synchronization)
- Minimal data collection and storage
- Secure configuration storage
- Timer state stored locally with user consent

### System Integration
- Minimal system permissions required
- Respect user privacy and system boundaries
- No unnecessary network access
- Transparent resource usage

## Governance

This constitution supersedes all other development practices. Amendments require documentation, approval, and migration plan. All development must verify compliance with these principles. Complexity must be justified with clear user value. Use this constitution as the primary guidance for runtime development decisions.

**Version**: 1.1.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-11-14
