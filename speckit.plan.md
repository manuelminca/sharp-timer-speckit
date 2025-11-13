# Implementation Plan: Sharp Timer

**Branch**: `feature/sharp-timer` | **Date**: 2025-11-13 | **Spec**: `.specify.md`
**Input**: Feature specification from `.specify.md`

**Note**: This plan focuses on macOS development using Swift with minimal standard library usage.

## Summary

Build a simple macOS menu bar timer application that provides Pomodoro-style productivity timers with minimal resource usage. The app should integrate with macOS menu bar, provide accurate countdown functionality, and persist timer state across app restarts using only standard Swift libraries and frameworks.

## Technical Context

**Language/Version**: Swift 5.9+ (macOS 12.0+ compatible)  
**Primary Dependencies**: Foundation, SwiftUI, AppKit (standard Apple frameworks only)  
**Storage**: UserDefaults (built-in)  
**Testing**: XCTest (built-in)  
**Target Platform**: macOS 12.0+ (Monterey and later)  
**Project Type**: Single desktop application  
**Performance Goals**: <50MB RAM usage, 0% CPU when idle, <0.5s startup time  
**Constraints**: Offline-only, no external dependencies, App Store compliant  
**Scale/Scope**: Single developer, minimal feature set, lightweight application

## Constitution Check

✅ **PASS** - Minimal external dependencies (only Apple frameworks)  
✅ **PASS** - Performance requirements met (<50MB RAM, fast startup)  
✅ **PASS** - Offline functionality (no network required)  
✅ **PASS** - macOS Human Interface Guidelines compliance  
✅ **PASS** - App Sandbox and App Store readiness  
✅ **PASS** - Simple architecture (MVVM, minimal complexity)  

## Project Structure

### Source Code (repository root)

```text
SharpTimer/
├── SharpTimerApp.swift          # App entry point
├── ContentView.swift           # Main SwiftUI view
├── ViewModels/
│   ├── TimerViewModel.swift    # Timer business logic
│   └── MenuBarViewModel.swift  # Menu bar icon management
├── Models/
│   ├── Timer.swift            # Timer data model
│   └── TimerState.swift       # Persistent timer state
├── Services/
│   ├── TimerService.swift     # Core timer functionality
│   ├── PersistenceService.swift # UserDefaults management
│   └── NotificationService.swift # System notifications
├── Views/
│   ├── MenuBarIconView.swift  # Menu bar status icon
│   ├── TimerPopupView.swift   # Timer configuration popup
│   └── TimerDisplayView.swift # Timer countdown display
├── Resources/
│   └── Assets.xcassets        # App icons and images
├── SharpTimer.entitlements    # App sandbox entitlements
└── Info.plist                 # App metadata
```

**Structure Decision**: Single SwiftUI+AppKit application using minimal separation of concerns. Business logic isolated in ViewModels, core services separated for testability, and views kept simple and focused.

## Standard Library Usage Strategy

### Core Frameworks (Required)
- **SwiftUI**: Primary UI framework for popup windows
- **AppKit**: Menu bar integration and window management
- **Foundation**: Date/time handling, UserDefaults persistence

### Avoid Overuse Of:
- **Combine**: Use simple @State/@Published instead of complex reactive patterns
- **CoreData**: Use UserDefaults for simple persistence
- **AVFoundation**: Use simple System Sound services for audio feedback
- **Foundation.Networking**: No network usage required

### Standard Library Components Used:
- **Timer**: Foundation.Timer for countdown functionality
- **UserDefaults**: For persistence (max 4KB, perfect for simple state)
- **NotificationCenter**: For system notification integration
- **Date**: For accurate time calculations
- **TimeInterval**: For timer duration management

## Development Phases

### Phase 1: Foundation Setup (Day 1)
**Goal**: Basic app structure and menu bar integration

**Tasks**:
1. Create Xcode project with macOS App template
2. Configure App Sandbox entitlements
3. Implement basic menu bar icon using NSStatusItem
4. Create initial SwiftUI popup window structure
5. Set up project organization per structure above

**Dependencies**: None - pure setup
**Success Criteria**: App shows icon in menu bar, opens basic popup window

### Phase 2: Core Timer Implementation (Day 1-2)
**Goal**: Working countdown timer functionality

**Tasks**:
1. Implement Timer model with duration and state management
2. Create TimerService with Foundation.Timer integration
3. Build TimerViewModel with start/stop/pause logic
4. Implement timer accuracy verification (±1 second)
5. Add basic countdown display in popup

**Dependencies**: Foundation (Timer, Date)
**Success Criteria**: Timer starts, counts down accurately, stops at zero

### Phase 3: Timer Presets and Customization (Day 2)
**Goal**: User-friendly timer configuration

**Tasks**:
1. Define TimerPreset enum (Focus: 25min, Break: 5min, Custom)
2. Update UI to show preset selection buttons
3. Implement custom duration input (text field with validation)
4. Add preset-specific color coding or icons
5. Test all preset types for correct behavior

**Dependencies**: SwiftUI (Form, TextField, Button)
**Success Criteria**: Users can select presets and create custom timers

### Phase 4: State Persistence (Day 2-3)
**Goal**: Timer continues after app restart

**Tasks**:
1. Implement PersistenceService using UserDefaults
2. Save timer state on app quit and every minute during operation
3. Load and restore timer state on app launch
4. Handle edge cases (system sleep, time changes)
5. Test persistence across multiple app restarts

**Dependencies**: Foundation (UserDefaults)
**Success Criteria**: Timer survives app restarts with accurate remaining time

### Phase 5: Menu Bar Integration (Day 3)
**Goal**: Visual status and quick actions in menu bar

**Tasks**:
1. Update menu bar icon to show timer status (default/running/paused)
2. Add tooltip with current timer information
3. Implement right-click context menu (start/stop options)
4. Add keyboard shortcut support (spacebar)
5. Test icon responsiveness and visual feedback

**Dependencies**: AppKit (NSStatusItem, NSMenu)
**Success Criteria**: Menu bar clearly shows timer state and provides quick access

### Phase 6: Notifications (Day 3)
**Goal**: User notification when timer completes

**Tasks**:
1. Implement NotificationService using UserNotificationCenter
2. Request notification permissions on first run
3. Send notification when timer reaches zero
4. Add optional sound feedback using System Sound
5. Handle notification click actions (focus app, stop timer)

**Dependencies**: Foundation (NotificationCenter, UserNotification)
**Success Criteria**: Users receive clear notification when timer completes

### Phase 7: Testing and Optimization (Day 4)
**Goal**: Ensure quality and performance requirements

**Tasks**:
1. Implement unit tests for TimerService accuracy
2. Add integration tests for timer state persistence
3. Profile memory usage and optimize if needed
4. Test on multiple macOS versions (12.0+)
5. Validate App Store compliance and sandbox settings

**Dependencies**: XCTest (built-in)
**Success Criteria**: All tests pass, memory usage <50MB, performance goals met

### Phase 8: Final Polish (Day 4)
**Goal**: Production-ready application

**Tasks**:
1. Add app icon and proper Info.plist metadata
2. Implement proper app lifecycle handling
3. Add error handling and edge case coverage
4. Create minimal README and setup instructions
5. Prepare for App Store submission

**Dependencies**: None - final polish
**Success Criteria**: App ready for distribution and user testing

## Implementation Guidelines

### Code Organization Principles
- **Simple MVVM**: Views handle presentation, ViewModels handle logic
- **Protocol-Oriented**: Define interfaces for testable services
- **Value Semantics**: Use structs for models, classes for services
- **Minimal State**: Only persist necessary timer state

### Performance Guidelines
- **Lazy Loading**: Initialize services only when needed
- **Memory Management**: Use weak references, avoid retain cycles
- **CPU Efficiency**: Update UI only when timer value changes
- **Battery Friendly**: Stop all timers when app becomes inactive

### Testing Strategy
- **Unit Tests**: Focus on timer logic and persistence accuracy
- **Integration Tests**: Verify app restart scenarios
- **Manual Testing**: Test user workflows and edge cases
- **Performance Testing**: Measure resource usage with Instruments

### Deployment Preparation
- **Code Signing**: Set up developer certificate and provisioning profile
- **App Sandbox**: Configure entitlements for minimal required permissions
- **App Store Assets**: Create app icon, screenshots, description
- **Privacy Policy**: Simple privacy statement for offline-only app

## Complexity Justification

**Simple Architecture Choice**: Using basic MVVM with SwiftUI provides sufficient separation of concerns without over-engineering. The timer functionality is straightforward and doesn't require complex dependency injection or architectural patterns.

**Standard Library Focus**: Sticking to Foundation, SwiftUI, and AppKit ensures maximum compatibility, minimal bundle size, and reduced maintenance burden. No external dependencies means no version conflicts or security vulnerabilities.

**Minimal Persistence**: UserDefaults provides adequate storage for timer state without requiring database setup or migration strategies. The simple key-value approach matches the app's simple requirements.

This plan prioritizes simplicity, performance, and maintainability over feature richness, creating a focused tool that excels at its core purpose of providing reliable timer functionality with minimal system impact.
