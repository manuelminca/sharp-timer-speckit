"""Quit confirmation dialog for Sharp Timer."""

import time
import rumps
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
from timer_state import TimerState

# Import NSAlert for proper three-button dialog
try:
    from Cocoa import NSAlert, NSApplication, NSAlertFirstButtonReturn, NSAlertSecondButtonReturn, NSAlertThirdButtonReturn
    NSALERT_AVAILABLE = True
except ImportError:
    NSALERT_AVAILABLE = False
    print("Warning: NSAlert not available, falling back to basic dialog")


class QuitAction(Enum):
    """Available quit dialog actions."""
    STOP_AND_QUIT = "stop_and_quit"
    PRESERVE_AND_QUIT = "preserve_and_quit"
    CANCEL = "cancel"


@dataclass
class QuitDialogResponse:
    """Response from quit confirmation dialog."""
    action: QuitAction
    timer_state_at_decision: TimerState
    timestamp: float
    user_choice_timestamp: float


class QuitDialogManager:
    """Manages quit confirmation dialog."""
    
    def __init__(self, timer_engine, settings_manager):
        self.timer_engine = timer_engine
        self.settings_manager = settings_manager
        self.callback: Optional[Callable[[QuitDialogResponse], None]] = None
    
    def should_show_quit_dialog(self) -> bool:
        """Determine if quit dialog should be shown."""
        return (self.timer_engine.is_running() or 
                self.timer_engine.is_paused() and 
                self._has_remaining_time())
    
    def _has_remaining_time(self) -> bool:
        """Check if timer has remaining time."""
        try:
            remaining = self.timer_engine.get_remaining_time()
            return remaining[0] > 0 or remaining[1] > 0
        except:
            return False
    
    def show_quit_confirmation(self) -> Optional[QuitDialogResponse]:
        """Show quit confirmation dialog to user."""
        if not self.should_show_quit_dialog():
            return None
        
        # Get current timer state
        current_state = self._get_current_timer_state()
        if not current_state:
            return None
        
        # Show custom dialog
        response = self._show_custom_quit_dialog()
        if response:
            quit_response = QuitDialogResponse(
                action=response,
                timer_state_at_decision=current_state,
                timestamp=time.time(),
                user_choice_timestamp=time.time()
            )
            
            # Execute action
            self.execute_quit_action(quit_response)
            
            # Call callback if set
            if self.callback:
                self.callback(quit_response)
            
            return quit_response
        
        return None
    
    def _show_custom_quit_dialog(self) -> Optional[QuitAction]:
        """Show custom quit dialog with three options using NSAlert."""
        if NSALERT_AVAILABLE:
            return self._show_nsalert_dialog()
        else:
            return self._show_fallback_dialog()
    
    def _show_nsalert_dialog(self) -> Optional[QuitAction]:
        """Show proper three-button dialog using NSAlert."""
        try:
            alert = NSAlert.new()
            alert.setMessageText_("Timer is active now. Are you sure you want to quit the app?")
            alert.setInformativeText_("Choose how to handle the running timer:")
            
            # Add three buttons
            alert.addButtonWithTitle_("Stop timer and Quit")
            alert.addButtonWithTitle_("Quit and leave timer running")
            alert.addButtonWithTitle_("Cancel")
            
            # Set alert style
            alert.setAlertStyle_(1)  # Warning style
            
            # Show dialog and get response
            response = alert.runModal()
            
            if response == NSAlertFirstButtonReturn:
                return QuitAction.STOP_AND_QUIT
            elif response == NSAlertSecondButtonReturn:
                return QuitAction.PRESERVE_AND_QUIT
            elif response == NSAlertThirdButtonReturn:
                return QuitAction.CANCEL
            else:
                return QuitAction.CANCEL
                
        except Exception as e:
            print(f"Error showing NSAlert dialog: {e}")
            return self._show_fallback_dialog()
    
    def _show_fallback_dialog(self) -> Optional[QuitAction]:
        """Fallback dialog using rumps."""
        try:
            # Use rumps.Window for better UX
            window = rumps.Window(
                title="Timer is active now. Are you sure you want to quit the app?",
                message="Choose how to handle the running timer:\n\n" +
                       "1. Stop timer and Quit\n" +
                       "2. Quit and leave timer running\n" +
                       "3. Cancel\n\n" +
                       "Enter your choice (1, 2, or 3):",
                default_text="3",
                ok="Quit",
                cancel="Cancel"
            )
            
            response = window.run()
            
            if not response.clicked:  # User clicked Cancel
                return QuitAction.CANCEL
            
            user_input = response.text.strip()
            
            if user_input == "1":
                return QuitAction.STOP_AND_QUIT
            elif user_input == "2":
                return QuitAction.PRESERVE_AND_QUIT
            else:
                return QuitAction.CANCEL
                
        except Exception as e:
            print(f"Error showing fallback dialog: {e}")
            return QuitAction.CANCEL
    
    def execute_quit_action(self, response: QuitDialogResponse) -> bool:
        """Execute the chosen quit action."""
        try:
            if response.action == QuitAction.STOP_AND_QUIT:
                # Stop timer and quit
                self.timer_engine.stop()
                self.settings_manager.clear_timer_state()
                rumps.quit_application()
                return True
                
            elif response.action == QuitAction.PRESERVE_AND_QUIT:
                # Save timer state and quit
                self.settings_manager.save_timer_state(response.timer_state_at_decision)
                rumps.quit_application()
                return True
                
            elif response.action == QuitAction.CANCEL:
                # Cancel quit operation
                return True
                
        except Exception as e:
            print(f"Error executing quit action: {e}")
            return False
        
        return False
    
    def _get_current_timer_state(self) -> Optional[TimerState]:
        """Get current timer state."""
        try:
            remaining_time = self.timer_engine.get_remaining_time()
            remaining_seconds = remaining_time[0] * 60 + remaining_time[1]
            
            return TimerState(
                mode=self.settings_manager.get_current_mode(),
                remaining_seconds=remaining_seconds,
                is_running=self.timer_engine.is_running(),
                is_paused=self.timer_engine.is_paused(),
                session_id=str(uuid.uuid4()),
                start_timestamp=time.time(),
                last_update_timestamp=time.time(),
                total_duration_seconds=self.settings_manager.get_duration(
                    self.settings_manager.get_current_mode()
                ) * 60
            )
        except Exception as e:
            print(f"Error getting current timer state: {e}")
            return None
    
    def set_callback(self, callback: Callable[[QuitDialogResponse], None]):
        """Set callback for dialog response handling."""
        self.callback = callback
    
    def get_dialog_history(self, limit: int = 10) -> list[QuitDialogResponse]:
        """Get history of quit dialog interactions."""
        # This would be implemented with persistent storage if needed
        # For now, return empty list
        return []


class EnhancedQuitDialogManager(QuitDialogManager):
    """Enhanced quit dialog manager with better UI."""
    
    def _show_custom_quit_dialog(self) -> Optional[QuitAction]:
        """Show enhanced quit dialog with better UI using NSAlert."""
        # Use the same NSAlert implementation as the parent class
        if NSALERT_AVAILABLE:
            return self._show_nsalert_dialog()
        else:
            return self._show_enhanced_fallback_dialog()
    
    def _show_enhanced_fallback_dialog(self) -> Optional[QuitAction]:
        """Show enhanced fallback dialog with better UX."""
        try:
            window = rumps.Window(
                title="Timer is active now. Are you sure you want to quit the app?",
                message="Choose how to handle the running timer:\n\n" +
                       "1. Stop timer and Quit\n" +
                       "2. Quit and leave timer running\n" +
                       "3. Cancel\n\n" +
                       "Enter your choice (1, 2, or 3):",
                default_text="3",
                dimensions=(400, 250),
                ok="Execute",
                cancel="Cancel"
            )
            
            response = window.run()
            
            if not response.clicked:  # User clicked Cancel
                return QuitAction.CANCEL
            
            user_input = response.text.strip()
            
            if user_input == "1":
                return QuitAction.STOP_AND_QUIT
            elif user_input == "2":
                return QuitAction.PRESERVE_AND_QUIT
            else:
                return QuitAction.CANCEL
                
        except Exception as e:
            print(f"Error showing enhanced fallback dialog: {e}")
            return QuitAction.CANCEL
