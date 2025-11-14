# Sharp Timer Specification

## Overview

Sharp Timer is a minimalist macOS timer app that runs exclusively in the menu bar, never appearing in the dock. It provides a distraction-free timer experience with three customizable modes: Work, Rest Your Eyes, and Long Rest.

## Core Requirements

### Menu Bar Exclusivity
- Application exists only in the macOS menu bar
- Never appears in the dock or application switcher
- Zero system tray presence beyond menu bar
- Clean, unobtrusive presence that respects screen real estate

### Three-Mode Timer System

#### Work Mode
- **Default Duration**: 25 minutes
- **Purpose**: Focused work sessions
- **Customizable**: Yes (user can set any duration)

#### Rest Your Eyes Mode
- **Default Duration**: 5 minutes
- **Purpose**: Short eye rest breaks
- **Customizable**: Yes (user can set any duration)

#### Long Rest Mode
- **Default Duration**: 15 minutes
- **Purpose**: Extended rest periods
- **Customizable**: Yes (user can set any duration)

### Customization Features
- All three modes must be fully customizable
- Users can modify duration for each mode independently
- Settings should persist across app restarts
- Real-time configuration updates without timer restart

### User Interface Requirements
- Minimalist design in menu bar
- Timer display in MM:SS format
- Current mode indicator
- Single-click access to all controls
- Settings accessible from menu bar

### Technical Requirements
- Built exclusively for macOS
- Python 3.8+ compatibility
- Minimal resource footprint
- Native macOS notifications
- No external dependencies where possible

### Default Configuration
- Work: 25 minutes
- Rest Your Eyes: 5 minutes
- Long Rest: 15 minutes
- Ready to use immediately without configuration

## Success Criteria

1. **Menu Bar Only**: App must never appear in dock
2. **Three Modes**: Clear distinction between Work, Rest Your Eyes, and Long Rest
3. **Customizable**: All durations must be user-configurable
4. **Minimalist**: Clean, distraction-free interface
5. **Persistent**: Settings survive app restarts
