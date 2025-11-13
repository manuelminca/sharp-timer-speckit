# Sharp Timer ⏱️

A simple, efficient macOS menu bar timer application built with Swift and SwiftUI. Perfect for Pomodoro technique, focus sessions, and break management.

## ✨ Features

### 🎯 Core Timer Functionality
- **Accurate Countdown**: Precise timer with ±1 second accuracy
- **Start/Stop/Pause/Resume**: Full timer control with intuitive buttons
- **Visual Progress**: Beautiful progress bar and countdown display
- **Timer Completion**: macOS notifications when timer finishes

### 🔄 State Persistence
- **Auto-Save**: Timer state automatically saved every 30 seconds
- **App Restart Recovery**: Resume timers after app quit/restart
- **Data Validation**: Automatic cleanup of corrupted saved data
- **Edge Case Handling**: Works with force quit, system restart, time changes

### ⚙️ Timer Types & Presets
- **Focus Timer**: 25-minute default (Pomodoro technique)
- **Break Timer**: 5-minute short break timer
- **Custom Timer**: Set any duration from 1 minute to 8 hours
- **User Preferences**: Custom durations are saved automatically

### 🍎 macOS Integration
- **Menu Bar Icon**: Clean, system-integrated timer icon
- **Popup Window**: Click icon to open timer controls
- **macOS Notifications**: Native notification center integration
- **Accessibility**: VoiceOver support and keyboard navigation

## 🚀 Quick Start

### Prerequisites
- **macOS 12.0** or later
- **Xcode 14.0** or later
- **Apple Developer Account** (for building and running)

### Build Instructions

1. **Clone or Download the Project**
   ```bash
   # Download the SharpTimer project files
   # Ensure all files are in the SharpTimer/ directory
   ```

2. **Open in Xcode**
   ```bash
   open SharpTimer.xcodeproj
   ```

3. **Configure Project**
   - Select the `SharpTimer` project in the navigator
   - Go to **Signing & Capabilities** tab
   - Select your Apple Developer account
   - Ensure **Team** is set to your developer account

4. **Build the Project**
   - Press `Cmd+B` or select **Product → Build**
   - Wait for compilation to complete

5. **Run the Application**
   - Press `Cmd+R` or select **Product → Run**
   - The app will appear in your menu bar

## 📱 How to Use

### Starting Your First Timer

1. **Launch the App**
   - Run from Xcode or double-click the built app
   - Look for the ⏱️ timer icon in your menu bar

2. **Open Timer Controls**
   - Click the timer icon in the menu bar
   - A popup window will appear with timer options

3. **Choose a Timer Type**
   - **Focus**: 25-minute productivity timer
   - **Break**: 5-minute break timer
   - **Custom**: Enter your own duration (1-480 minutes)

4. **Start Timing**
   - Click **Start Timer** button
   - The popup shows a beautiful countdown interface
   - Progress bar updates in real-time

5. **Timer Controls**
   - **Pause/Resume**: Pause and resume active timers
   - **Stop**: Stop and reset the timer
   - **Close**: Close popup (timer continues running)

### Persistent State Testing

1. **Start a Timer**
   - Begin any timer (try a 30-second timer for quick testing)

2. **Quit the App**
   - Close the app completely

3. **Restart the App**
   - Launch the app again
   - The timer should continue from where it left off

4. **Verify State**
   - Timer state is automatically saved every 30 seconds
   - Check menu bar icon changes when timer is active

## 🏗️ Project Structure

```
SharpTimer/
├── SharpTimerApp.swift              # Main app entry point
├── Info.plist                       # App metadata and permissions
├── SharpTimer.entitlements         # App sandbox configuration
├── Models/
│   ├── Timer.swift                 # Core timer data model
│   └── TimerState.swift           # Persistent state management
├── ViewModels/
│   └── TimerViewModel.swift       # Timer business logic coordinator
├── Services/
│   ├── TimerService.swift         # Foundation.Timer integration
│   ├── NotificationService.swift # macOS notifications
│   └── PersistenceService.swift  # UserDefaults persistence
└── Views/
    ├── MenuBarIconView.swift      # Menu bar display
    ├── TimerDisplayView.swift     # Countdown interface
    └── TimerPopupView.swift       # Main control interface
```

## 🔧 Architecture Overview

### **MVVM Pattern**
- **Model**: Timer and TimerState data structures
- **View**: SwiftUI views (TimerDisplayView, TimerPopupView)
- **ViewModel**: TimerViewModel coordinating business logic

### **Service Layer**
- **TimerService**: Core timer functionality with Foundation.Timer
- **NotificationService**: macOS notification center integration
- **PersistenceService**: UserDefaults for state management

### **Key Design Principles**
- **Protocol-Oriented**: Clean interfaces for testability
- **Memory Management**: Weak references to prevent retain cycles
- **Error Handling**: Comprehensive validation and cleanup
- **Performance**: Optimized for minimal resource usage

## 🧪 Testing Features

### Manual Testing Checklist

#### ✅ Basic Timer Functionality
- [ ] Start Focus timer (25 minutes)
- [ ] Start Break timer (5 minutes)
- [ ] Start Custom timer (test different durations)
- [ ] Pause active timer
- [ ] Resume paused timer
- [ ] Stop timer completely
- [ ] Verify countdown accuracy

#### ✅ Persistence Testing
- [ ] Start timer, quit app, restart - timer continues
- [ ] Auto-save every 30 seconds during operation
- [ ] Force quit and restart - state recovery
- [ ] Test with different timer durations
- [ ] Verify custom durations are saved

#### ✅ macOS Integration
- [ ] Menu bar icon appears after launch
- [ ] Click icon opens/closes popup
- [ ] Timer completion notifications
- [ ] App runs in background without dock icon

#### ✅ User Interface
- [ ] Beautiful countdown display with progress bar
- [ ] Smooth animations and transitions
- [ ] Responsive popup window sizing
- [ ] Clear timer status indicators

### Performance Expectations
- **Memory Usage**: < 50MB RAM during operation
- **Startup Time**: < 0.5 seconds to full functionality
- **CPU Usage**: 0% when idle, minimal when timer running
- **Battery Impact**: Minimal due to efficient timer implementation

## 🔧 Troubleshooting

### Common Issues

**App doesn't appear in menu bar**
- Check that the app built successfully
- Look for any compilation errors in Xcode
- Verify LSUIElement is set to true in Info.plist

**Notifications not working**
- Grant notification permissions when prompted
- Check System Preferences → Notifications for Sharp Timer
- Ensure UNUserNotificationCenter is properly configured

**Timer state not persisting**
- Check UserDefaults permissions in sandbox
- Verify PersistenceService is saving state
- Look for console logs showing save/load operations

**Popup window positioning issues**
- Ensure menu bar icon button is properly configured
- Check window positioning calculations in SharpTimerApp.swift
- Verify screen detection logic

### Debug Mode
Add this to any ViewModel for debug output:
```swift
// Enable debug logging
let debugService = PersistenceService()
debugService.printDebugInfo()
```

## 📋 Development Notes

### Key Implementation Details

1. **Timer Accuracy**
   - Foundation.Timer with 1-second updates
   - Drift tracking and correction
   - System time change handling

2. **State Management**
   - Automatic state saving on all timer operations
   - Data validation and corruption recovery
   - Cleanup of expired states (>7 days)

3. **UI/UX Design**
   - macOS design language compliance
   - Smooth animations and transitions
   - Accessibility support throughout

4. **Performance Optimization**
   - Lazy loading of services
   - Efficient memory management
   - Background operation support

### Future Enhancements
- Menu bar status display enhancements
- Keyboard shortcuts for quick actions
- Multiple timer support
- Statistics and history tracking
- Sound customization options

## 📄 License

This project is created for educational and demonstration purposes.

---

**Sharp Timer** - Simple, efficient, and reliable timing for macOS users.
