# Quit Dialog API Contract

**Version**: 1.0  
**Date**: 2025-11-14  
**Component**: Quit Confirmation Workflow

## Overview

This contract defines the API interface for the quit confirmation dialog that appears when users attempt to quit the application while a timer is active.

## Interfaces

### QuitDialogManager

```python
from abc import ABC, abstractmethod
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

class QuitAction(Enum):
    """Available quit dialog actions."""
    STOP_AND_QUIT = "stop_and_quit"
    PRESERVE_AND_QUIT = "preserve_and_quit"
    CANCEL = "cancel"

@dataclass
class QuitDialogResponse:
    """Response from quit confirmation dialog."""
    action: QuitAction
    timer_state_at_decision: 'TimerState'
    timestamp: float
    user_choice_timestamp: float

class QuitDialogManager(ABC):
    """Abstract interface for quit dialog management."""
    
    @abstractmethod
    def should_show_quit_dialog(self, timer_state: 'TimerState') -> bool:
        """Determine if quit dialog should be shown.
        
        Args:
            timer_state: Current timer state
            
        Returns:
            True if dialog should be shown, False otherwise
        """
        pass
    
    @abstractmethod
    def show_quit_confirmation(self, timer_state: 'TimerState') -> Optional[QuitDialogResponse]:
        """Show quit confirmation dialog to user.
        
        Args:
            timer_state: Current timer state
            
        Returns:
            QuitDialogResponse if user made choice, None if dialog cancelled
        """
        pass
    
    @abstractmethod
    def execute_quit_action(self, response: QuitDialogResponse) -> bool:
        """Execute the chosen quit action.
        
        Args:
            response: User's quit dialog response
            
        Returns:
            True if action executed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def set_dialog_callback(self, callback: Callable[[QuitDialogResponse], None]) -> None:
        """Set callback for dialog response handling.
        
        Args:
            callback: Function to call when dialog response is received
        """
        pass
    
    @abstractmethod
    def get_dialog_history(self, limit: int = 10) -> list[QuitDialogResponse]:
        """Get history of quit dialog interactions.
        
        Args:
            limit: Maximum number of historical responses to return
            
        Returns:
            List of quit dialog responses
        """
        pass
```

## Dialog Specifications

### Visual Design

```
┌─────────────────────────────────────┐
│ ⏱️ Sharp Timer                      │
├─────────────────────────────────────┤
│ Timer is active now. Are you sure   │
│ you want to quit the app?           │
│                                     │
│ Choose how to handle the running    │
│ timer:                              │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ ⏹️  Stop timer and Quit         │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 💾  Quit and leave timer running│ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ ❌  Cancel                         │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Dialog Behavior

1. **Display Conditions**:
   - Timer is running (`is_running = True`)
   - Timer is paused with remaining time (`is_paused = True` and `remaining_seconds > 0`)
   - Quit confirmation is enabled in settings

2. **Button Actions**:
   - **Stop timer and Quit**: Stop timer, clear state, quit application
   - **Quit and leave timer running**: Save timer state, quit application
   - **Cancel**: Close dialog, continue running application

3. **Default Selection**:
   - No default button (requires explicit user choice)
   - Escape key maps to "Cancel"
   - Return key requires button focus

## Implementation Requirements

### State Integration

```python
class QuitDialogStateManager:
    """Manages quit dialog state persistence."""
    
    def save_dialog_response(self, response: QuitDialogResponse) -> bool:
        """Save quit dialog response to history."""
        pass
    
    def load_dialog_history(self) -> list[QuitDialogResponse]:
        """Load quit dialog interaction history."""
        pass
    
    def should_preserve_timer_state(self, action: QuitAction) -> bool:
        """Determine if timer state should be preserved."""
        return action == QuitAction.PRESERVE_AND_QUIT
```

### Timer Engine Integration

```python
class TimerEngineWithQuitSupport(TimerEngine):
    """Enhanced timer engine with quit dialog support."""
    
    def __init__(self, completion_callback, quit_dialog_manager: QuitDialogManager):
        super().__init__(completion_callback)
        self.quit_dialog_manager = quit_dialog_manager
        self._quit_requested = False
    
    def request_quit(self) -> bool:
        """Handle quit request with dialog confirmation."""
        if self.quit_dialog_manager.should_show_quit_dialog(self.get_current_state()):
            response = self.quit_dialog_manager.show_quit_confirmation(self.get_current_state())
            if response:
                return self.quit_dialog_manager.execute_quit_action(response)
            return False  # Dialog cancelled
        return True  # No dialog needed, can quit directly
    
    def get_current_state(self) -> 'TimerState':
        """Get current timer state for dialog."""
        pass
```

### Application Lifecycle Integration

```python
class SharpTimerWithQuitSupport(SharpTimer):
    """Enhanced Sharp Timer with quit confirmation."""
    
    def __init__(self):
        super().__init__()
        self.quit_dialog_manager = QuitDialogManagerImpl()
        self._setup_quit_handlers()
    
    def _setup_quit_handlers(self):
        """Set up quit event handlers."""
        # Override default quit behavior
        self.quit_button = None  # Remove default quit button
        self.menu.add("Quit", callback=self._handle_quit_request)
    
    def _handle_quit_request(self, sender):
        """Handle quit request with confirmation dialog."""
        if self.timer.request_quit():
            rumps.quit_application()
    
    @rumps.clicked("Quit")
    def quit_app(self, sender):
        """Quit application with confirmation if needed."""
        self._handle_quit_request(sender)
```

## Error Handling

### Exception Types

```python
class QuitDialogError(Exception):
    """Base exception for quit dialog operations."""
    pass

class QuitDialogCancelledError(QuitDialogError):
    """Raised when user cancels quit dialog."""
    pass

class QuitDialogExecutionError(QuitDialogError):
    """Raised when quit action execution fails."""
    pass

class QuitDialogStateError(QuitDialogError):
    """Raised when quit dialog state is invalid."""
    pass
```

### Error Recovery

- **Dialog Display Failure**: Show simple alert as fallback
- **State Persistence Failure**: Continue with quit operation, log error
- **Timer Stop Failure**: Force quit application, log error
- **Application Quit Failure**: Show error message, retry operation

## Performance Requirements

- **Dialog Display**: < 100ms from request to visible
- **Response Handling**: < 50ms from user action to execution
- **State Capture**: < 10ms for timer state snapshot
- **History Storage**: < 20ms for response persistence

## Testing Requirements

### Unit Tests

- `test_should_show_quit_dialog_running_timer`
- `test_should_show_quit_dialog_paused_timer`
- `test_should_not_show_quit_dialog_no_timer`
- `test_show_quit_confirmation_success`
- `test_show_quit_confirmation_cancelled`
- `test_execute_quit_action_stop_and_quit`
- `test_execute_quit_action_preserve_and_quit`
- `test_execute_quit_action_cancel`
- `test_dialog_callback_handling`
- `test_dialog_history_persistence`

### Integration Tests

- `test_quit_dialog_with_active_timer`
- `test_quit_dialog_with_paused_timer`
- `test_quit_dialog_timer_state_preservation`
- `test_quit_dialog_application_quit`
- `test_quit_dialog_cancellation_flow`
- `test_quit_dialog_system_integration`

### UI Tests

- `test_quit_dialog_display_correctness`
- `test_quit_dialog_button_functionality`
- `test_quit_dialog_keyboard_navigation`
- `test_quit_dialog_accessibility`
- `test_quit_dialog_visual_appearance`

## Security Considerations

- Timer state validation before preservation
- Safe dialog response handling
- Prevention of dialog spoofing
- Secure state storage with proper permissions
- Input validation for all user interactions

## Accessibility Requirements

- VoiceOver support for all dialog elements
- Keyboard navigation support
- High contrast mode compatibility
- Screen reader announcements
- Focus management for dialog controls

## Localization Support

- Dialog text externalization
- Button text localization
- Timer mode name localization
- Right-to-left language support
- Font size and type considerations
