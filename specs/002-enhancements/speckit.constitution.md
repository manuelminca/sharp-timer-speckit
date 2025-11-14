<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.0 (initial constitution)
- List of modified principles: N/A (new constitution)
- Added sections: All sections
- Removed sections: N/A
- Templates requiring updates: 
  ✅ .specify/templates/plan-template.md (Constitution Check section)
  ✅ .specify/templates/spec-template.md (scope/requirements alignment)
  ✅ .specify/templates/tasks-template.md (task categorization)
  ⚠️ Command files may need review for principle references
- Follow-up TODOs: None
-->

# Sharp Timer Constitution

## Core Principles

### I. Menu Bar Exclusive Philosophy
The application exists exclusively in the macOS menu bar, never appearing in the dock or application switcher. Zero system tray presence beyond menu bar with single-click access to all core functionality. Clean, unobtrusive presence that respects screen real estate.

### II. Minimal Resource Footprint
Optimized for low CPU and memory usage, running as an efficient background daemon. Zero friction startup and operation with efficient event handling and state management.

### III. Persistent State Management
Timer state and configuration MUST persist across application restarts. When closing with active timer, users MUST be presented with clear options for handling the running timer. Session state recovery after system restart is non-negotiable.

### IV. Enhanced User Experience
Timer transitions MUST be seamless with automatic mode switching. Work timer completion MUST automatically set Rest Your Eyes mode in paused state. Rest Your Eyes completion MUST prefill Work mode in paused state. Improved audio alerts MUST sound for 5 seconds on completion.

### V. Native macOS Integration
Respect macOS design language and aesthetics with native notifications. Consistent with system UI patterns and behaviors. Graceful handling of system events and proper integration with macOS lifecycle.

## Technical Requirements

### Technology Stack
- Python 3.8+ compatibility requirement
- Preference for built-in macOS libraries (rumps framework)
- Minimal external dependencies
- Built exclusively for macOS platform

### Performance Standards
- < 1% CPU usage during normal operation
- < 50MB memory footprint
- < 2 second application startup time
- < 100ms response time for user interactions

## Development Workflow

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

## Governance

This constitution supersedes all other development practices. Amendments require documentation, approval, and migration plan. All development must verify compliance with these principles. Complexity must be justified with clear user value. Use this constitution as the primary guidance for runtime development decisions.

**Version**: 1.0.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-11-14
