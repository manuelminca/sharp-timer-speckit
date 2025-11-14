# Sharp Timer Implementation Plan

## Technology Stack

### Core Requirements
- **Language**: Python 3.8+
- **Philosophy**: Minimal libraries, maximum performance
- **Target**: macOS exclusive
- **Architecture**: Simple but effective

### Minimal Library Approach
- **Standard Library Only**: Prefer built-in Python modules
- **macOS Integration**: Use `rumps` for menu bar functionality (single, well-maintained dependency)
- **Persistence**: JSON file storage using Python's `json` module
- **Timer**: `threading.Timer` or `asyncio` for lightweight timing
- **Notifications**: `osascript` via subprocess for native macOS notifications

## Architecture Design

### Core Components

#### 1. Timer Engine (`timer.py`)
```python
class TimerEngine:
    - start(mode, duration)
    - pause()
    - resume()
    - reset()
    - get_remaining_time()
    - is_running()
```

#### 2. Settings Manager (`settings.py`)
```python
class SettingsManager:
    - load_settings()
    - save_settings()
    - get_mode_duration(mode)
    - set_mode_duration(mode, duration)
    - reset_to_defaults()
```

#### 3. Menu Bar Interface (`menu.py`)
```python
class MenuBarApp:
    - create_menu()
    - update_display()
    - show_notification()
    - handle_menu_actions()
```

#### 4. Main Application (`main.py`)
```python
class SharpTimer:
    - initialize_components()
    - setup_menu_bar()
    - handle_mode_switching()
    - run()
```

## Persistence Strategy

### Simple JSON Storage
- **Location**: `~/Library/Application Support/Sharp Timer/settings.json`
- **Format**: Simple key-value structure
- **Backup**: Auto-backup on settings change

```json
{
    "work_duration": 25,
    "rest_eyes_duration": 5,
    "long_rest_duration": 15,
    "current_mode": "work",
    "auto_start_next": false,
    "sound_enabled": true,
    "notifications_enabled": true
}
```

### Settings Manager Implementation
- **Atomic Writes**: Write to temp file, then move to prevent corruption
- **Validation**: Ensure values are within reasonable bounds
- **Defaults**: Fallback to defaults if file is corrupted
- **Migration**: Handle future setting additions gracefully

## Performance Optimization

### Minimal Resource Usage
- **Event-Driven**: Use callbacks instead of polling
- **Lazy Loading**: Initialize components only when needed
- **Memory Efficient**: Avoid object creation in timer loops
- **CPU Friendly**: Sleep intervals in timer updates

### Timer Implementation
```python
import threading
import time

class PerformanceTimer:
    def __init__(self, callback, interval=1.0):
        self.callback = callback
        self.interval = interval
        self.timer = None
        self.running = False
    
    def start(self):
        if not self.running:
            self.running = True
            self._schedule_next()
    
    def _schedule_next(self):
        if self.running:
            self.timer = threading.Timer(self.interval, self._tick)
            self.timer.start()
    
    def _tick(self):
        if self.running:
            self.callback()
            self._schedule_next()
```

## Menu Bar Integration

### Using rumps Library
- **Single Dependency**: `rumps` for macOS menu bar integration
- **Native Feel**: Uses native macOS menu bar APIs
- **Lightweight**: Minimal overhead, pure Python wrapper

### Menu Structure
```
Sharp Timer
├── 25:00 (Work Mode)
├── ─────────────────
├── Start/Pause
├── Reset
├── ─────────────────
├── Work Mode (25m)
├── Rest Eyes (5m)
├── Long Rest (15m)
├── ─────────────────
├── Settings...
└── Quit
```

## File Structure

```
sharp_timer/
├── main.py              # Application entry point
├── timer.py             # Timer engine
├── settings.py          # Settings management
├── menu.py              # Menu bar interface
├── notifications.py     # macOS notifications
├── constants.py         # App constants and defaults
├── requirements.txt     # Minimal dependencies
└── README.md           # Setup and usage
```

## Development Phases

### Phase 1: Core Timer (Week 1)
- Basic timer functionality
- Three-mode system
- Menu bar integration
- Settings persistence

### Phase 2: Polish (Week 2)
- Notifications
- Settings UI
- Performance optimization
- Error handling

### Phase 3: Refinement (Week 3)
- Testing
- Documentation
- Packaging
- Distribution

## Code Quality Standards

### Simplicity First
- **Clear Naming**: Descriptive variable and function names
- **Single Responsibility**: Each function does one thing well
- **Minimal Complexity**: Avoid over-engineering
- **Documentation**: Essential docstrings only

### Performance Guidelines
- **No Blocking Operations**: Keep UI responsive
- **Efficient Updates**: Update menu only when necessary
- **Memory Management**: Clean up resources properly
- **Fast Startup**: App ready in under 2 seconds

## Testing Strategy

### Unit Tests
- Timer logic accuracy
- Settings persistence
- Mode switching
- Edge cases

### Integration Tests
- Menu bar functionality
- macOS notifications
- Settings file handling
- Performance benchmarks

### Manual Testing
- User workflow validation
- Menu interaction testing
- Long-running stability
- Resource usage monitoring

## Distribution Plan

### Packaging
- **PyInstaller**: Create standalone macOS app
- **Code Signing**: Ensure macOS compatibility
- **Notarization**: Pass Apple's security checks
- **DMG Creation**: Easy installation package

### Minimal Dependencies
```
rumps>=0.3.0
```

### Installation
```bash
pip install rumps
python main.py
```

## Success Metrics

### Performance Targets
- **Startup Time**: < 2 seconds
- **Memory Usage**: < 30MB
- **CPU Usage**: < 0.5% during operation
- **Menu Response**: < 100ms

### User Experience
- **Zero Configuration**: Works out of the box
- **Intuitive Interface**: Obvious controls
- **Reliable Operation**: No crashes or data loss
- **Fast Performance**: No lag or delays

This plan prioritizes simplicity, performance, and minimal dependencies while delivering a fully functional macOS menu bar timer.
