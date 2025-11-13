# Speckit Constitution
## Principles for a Simple macOS Menu Bar Timer App in Swift

*Last Updated: 2025-11-13*  
*Version: 2.0*  
*Target Platform: macOS*  
*App Type: Simple Menu Bar Timer (similar to "Be Focused")*

---

## 1. CODE QUALITY PRINCIPLES

### 1.1 Swift Language Standards
- **Swift Version**: Target Swift 5.9+ for latest stability
- **Simplicity First**: Write clear, simple code over clever code
- **Value Semantics**: Use structs for models, classes for views
- **Optionals**: Handle optionals safely, avoid force unwrapping
- **Memory Efficiency**: Use weak references to prevent retain cycles

### 1.2 Architecture
- **Simple MVVM**: Basic Model-View-ViewModel pattern
- **Single Responsibility**: Each class/view should have one clear job
- **Dependency Injection**: Simple initializer injection for testability
- **Protocols**: Use lightweight protocols for simple abstractions
- **No External Dependencies**: Prefer built-in frameworks over third-party libraries

### 1.3 Code Organization
- **Minimal File Structure**: Keep project simple with few files
- **Access Control**: Use `private` and `fileprivate` to limit scope
- **Clear Naming**: Use descriptive but concise names
- **Comments**: Comment only when code isn't self-explanatory

### 1.4 SwiftUI for Menu Bar
- **Lightweight Views**: Create simple, focused views
- **State Management**: Use `@State` and `@Binding` only when needed
- **Window Management**: Properly manage popup window lifecycle

---

## 2. TESTING STANDARDS

### 2.1 Minimal Testing Approach
- **Unit Tests**: Test timer logic and business rules (80% coverage minimum)
- **Integration Tests**: Test end-to-end timer workflows
- **No UI Tests**: Skip complex UI testing for simple interface
- **XCTest**: Use Apple's built-in testing framework

### 2.2 Timer-Specific Testing
- **Timer Accuracy**: Test timer precision and drift
- **State Persistence**: Test that timer state persists across app restarts
- **Interrupt Handling**: Test behavior when app is quit/launched
- **Memory Management**: Ensure no memory leaks in timer callbacks

### 2.3 Performance Testing
- **Memory Usage**: App should use less than 50MB RAM
- **CPU Usage**: Should be idle when no timer is running
- **Startup Time**: App should launch instantly (under 0.5 seconds)

---

## 3. USER EXPERIENCE FOR MENU BAR APPS

### 3.1 Menu Bar Design
- **System Integration**: Follow macOS Human Interface Guidelines for menu bar apps
- **Icon Consistency**: Use system-appropriate icon style (SF Symbols preferred)
- **Status Indication**: Clear visual indication of timer state (running/stopped/paused)
- **Right-click Support**: Provide context menu options

### 3.2 Timer Interface
- **Quick Access**: Timer should be usable with minimal clicks
- **Visual Feedback**: Clear indication when timer starts/stops/completes
- **Customization**: Allow basic timer length customization
- **Notification**: Sound or notification when timer completes

### 3.3 Minimal UI Design
- **Simple Layout**: Clean, uncluttered popup window
- **macOS Styling**: Use system fonts and colors
- **Responsive**: Window should resize naturally with content
- **Keyboard Shortcuts**: Support spacebar to start/stop timer

### 3.4 Accessibility
- **VoiceOver**: All controls should have accessibility labels
- **Keyboard Navigation**: Tab navigation through all controls
- **Color Accessibility**: Ensure sufficient contrast for timer display

---

## 4. PERFORMANCE & RESOURCE REQUIREMENTS

### 4.1 Memory Management
- **Low Memory Footprint**: Target <50MB RAM usage
- **Efficient Timers**: Use `Timer` class efficiently, avoid multiple timer instances
- **Cleanup**: Properly invalidate timers when not needed
- **Background Mode**: Minimal resource usage when app is not active

### 4.2 CPU Optimization
- **Idle CPU Usage**: 0% CPU usage when no timer is running
- **Efficient Updates**: Update UI only when necessary (once per second for timer)
- **Thread Management**: Use main thread for UI, background threads for non-UI work
- **Timer Precision**: Use `Timer` with reasonable tolerance for simplicity

### 4.3 Battery Life
- **Minimal Background Processing**: No background polling or updates
- **Efficient Notifications**: Use system notification center efficiently
- **App Nap Friendly**: Don't prevent system app nap when idle

### 4.4 Storage
- **User Defaults**: Use `UserDefaults` for simple preference storage
- **No Database**: Avoid complex storage solutions
- **Minimal Disk Usage**: App bundle under 10MB
- **State Persistence**: Store current timer state for quick restore

---

## 5. APP SPECIFIC REQUIREMENTS

### 5.1 Timer Functionality
- **Core Timer**: Accurate countdown timer (25 minutes default like Pomodoro)
- **Multiple Timers**: Support for multiple concurrent timers (3-5 max)
- **Timer Types**: Basic timer types (focus, break, custom)
- **Persistence**: Save timer state across app restarts

### 5.2 Menu Bar Integration
- **Status Display**: Show current timer remaining in menu bar
- **Quick Actions**: Start/stop/restart from menu bar
- **Popup Window**: Clean, focused timer management window
- **System Tray**: Integrate properly with macOS menu bar behavior

### 5.3 Notifications
- **Completion Alert**: Sound or visual notification when timer completes
- **System Integration**: Use `UserNotificationCenter` for alerts
- **Non-intrusive**: Notifications shouldn't interrupt user's workflow

---

## 6. DEVELOPMENT WORKFLOW

### 6.1 Simple Development Process
- **Single Developer**: Optimized for solo development
- **Git**: Simple git workflow with feature branches
- **Build System**: Use Xcode build system, no complex CI/CD needed
- **Documentation**: Minimal but clear README and inline comments

### 6.2 Code Quality Tools
- **SwiftLint**: Basic linting rules for consistent style
- **SwiftFormat**: Automatic code formatting
- **Xcode Warnings**: Address all compiler warnings
- **Build Settings**: Optimize for release builds

### 6.3 Deployment
- **App Store**: Prepare for Mac App Store distribution
- **Code Signing**: Proper certificate and provisioning profiles
- **Sandbox**: macOS App Sandbox compliance
- **Notarization**: Apple notarization for distribution

---

## 7. SECURITY & PRIVACY

### 7.1 Minimal Security
- **No Network**: App should work completely offline
- **No Personal Data**: Don't collect any user data
- **Local Storage Only**: All data stays on user's device
- **Keychain**: Use for any future settings if needed

### 7.2 Privacy
- **No Analytics**: Don't track user behavior
- **No Internet**: No network permissions needed
- **Local-Only**: All functionality works offline
- **Privacy Policy**: Simple, transparent privacy policy

---

## 8. SIMPLICITY PRINCIPLES

### 8.1 Design Philosophy
- **Less is More**: Every feature should earn its place
- **User-Focused**: Solve the specific problem of tracking time
- **Fast**: Prioritize speed over features
- **Reliable**: Focus on correctness over complexity

### 8.2 Feature Constraints
- **Core Features Only**: Timer functionality and basic management
- **No Over-engineering**: Avoid abstractions that aren't needed
- **Simple Defaults**: Sane defaults that work for most users
- **Incremental Development**: Build simple, then add features gradually

### 8.3 Maintenance
- **Future-Proof**: Code should be easy to understand and modify
- **Documentation**: Keep docs simple and current
- **Updates**: Minimal, focused updates rather than large rewrites

---

*This constitution emphasizes simplicity and efficiency for a focused menu bar timer application. The goal is to create a lightweight, reliable tool that uses minimal system resources while providing essential timer functionality.*
