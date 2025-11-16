"""Main application entry point for Sharp Timer."""

import rumps
import time
import threading
from timer import TimerEngine
from settings import SettingsManager
from notifications import NotificationManager
from timer_state import TimerState
from quit_dialog import QuitDialogManager, QuitAction
from enhanced_notifications import EnhancedNotificationManager, AudioNotificationConfig
from mode_transitions import ModeTransitionManager, TimerMode
from system_events import SystemEventManager
from constants import (
    MODE_WORK, MODE_REST_EYES, MODE_LONG_REST,
    MODE_NAMES, MODE_ICONS,
    MENU_START, MENU_PAUSE, MENU_RESET, MENU_SEPARATOR,
    MENU_WORK_MODE, MENU_REST_EYES_MODE, MENU_LONG_REST_MODE,
    MENU_SETTINGS, MENU_QUIT
)


class SharpTimer(rumps.App):
    """Main Sharp Timer application running in macOS menu bar."""
    
    def __init__(self):
        """Initialize the Sharp Timer application with enhancements."""
        super(SharpTimer, self).__init__("⏱️", quit_button=None)
        
        # Initialize components
        self.settings = SettingsManager()
        self.timer = TimerEngine(self._on_timer_complete)
        
        # Initialize enhanced components
        self.quit_dialog_manager = QuitDialogManager(self.timer, self.settings)
        self.enhanced_notification_manager = EnhancedNotificationManager()
        self.mode_transition_manager = ModeTransitionManager(self.settings)
        self.system_event_manager = SystemEventManager(self.settings.timer_state_manager, self.timer)
        
        # Application state
        self.current_mode = self.settings.get_current_mode()
        self._backup_timer = None
        self._ui_update_active = True
        self._ui_lock = threading.Lock()
        self._stop_ui_updates = False
        
        # Set up menu first
        self._setup_menu()
        
        # Then restore timer state (this will update menu buttons if needed)
        self._restore_timer_state()
        
        # Start background UI update thread that runs independently
        self._start_ui_update_thread()
        
        # Start periodic backup timer
        self._start_backup_timer()
        
        # Setup system event callbacks
        self._setup_system_event_callbacks()
    
    def _setup_menu(self):
        """Set up the menu bar menu."""
        self.menu.clear()
        
        # Timer controls
        self.menu.add(MENU_START)
        self.menu.add(MENU_RESET)
        self.menu.add(MENU_SEPARATOR)
        
        # Mode selection
        self.menu.add(MENU_WORK_MODE)
        self.menu.add(MENU_REST_EYES_MODE)
        self.menu.add(MENU_LONG_REST_MODE)
        self.menu.add(MENU_SEPARATOR)
        
        # Settings and quit
        self.menu.add(MENU_SETTINGS)
        self.menu.add(MENU_QUIT)
    
    def update_timer_title(self):
        """Update the menu bar title with current timer display."""
        if self.timer.is_running():
            mins, secs = self.timer.get_remaining_time()
            mode_icon = MODE_ICONS.get(self.current_mode, "⏱️")
            self.title = f"{mode_icon} {mins:02d}:{secs:02d}"
        else:
            # Show default duration for current mode
            duration = self.settings.get_duration(self.current_mode)
            mode_icon = MODE_ICONS.get(self.current_mode, "⏱️")
            self.title = f"{mode_icon} {duration:02d}:00"
    
    def update_menu_button_state(self):
        """Update the start/pause menu button based on current timer state."""
        if hasattr(self, 'menu') and MENU_START in self.menu:
            if self.timer.is_running():
                self.menu[MENU_START].title = MENU_PAUSE
            else:
                self.menu[MENU_START].title = MENU_START
    
    def _start_ui_update_thread(self):
        """Start a background thread for UI updates that won't be blocked by dialogs."""
        def update_ui_continuously():
            while not self._stop_ui_updates:
                try:
                    if self.timer.is_running():
                        # Update title directly - this should work even when dialogs are open
                        self.update_timer_title()
                    time.sleep(0.5)  # Update every 500ms
                except Exception as e:
                    print(f"Error in UI update thread: {e}")
                    time.sleep(1)  # Wait longer on error
        
        ui_thread = threading.Thread(target=update_ui_continuously, daemon=True)
        ui_thread.start()
    
    def _update_ui(self, sender):
        """Update UI periodically (called by timer) - thread-safe and non-blocking."""
        # This method is kept for compatibility but the main work is done by the background thread
        pass
    
    def _safe_update_title(self, sender):
        """Safely update the title from the main thread."""
        try:
            if self.timer.is_running():
                self.update_timer_title()
        except Exception as e:
            print(f"Error updating title: {e}")
    
    def _on_timer_complete(self):
        """Enhanced timer completion handler."""
        # Get current state
        current_state = self._get_current_timer_state()
        mode_name = MODE_NAMES.get(self.current_mode, "Session")
        duration = self.settings.get_duration(self.current_mode)
        
        # Play enhanced audio notification
        self.enhanced_notification_manager.play_timer_completion_sound(mode_name, duration)
        
        # Execute automatic mode switching
        completed_mode = TimerMode(self.current_mode)
        transition_result = self.mode_transition_manager.execute_auto_switch(
            completed_mode, current_state
        )
        
        if transition_result and transition_result.success:
            # Update current mode
            self.current_mode = transition_result.new_mode.value
            self.settings.set_current_mode(self.current_mode)
            
            # Update UI
            self.update_timer_title()
            self._update_menu_labels()
            
            print(f"Auto-switched from {transition_result.previous_mode.value} to {transition_result.new_mode.value} in {transition_result.transition_time_ms}ms")
        
        # Update menu to show Start again
        self.update_menu_button_state()
        
        # Save state after completion
        self._save_current_state()
    
    @rumps.clicked(MENU_START)
    def start_timer(self, sender):
        """Start or pause the timer with state persistence."""
        if self.timer.is_running():
            # Pause the timer
            self.timer.pause()
            self.update_menu_button_state()
        elif self.timer.is_paused():
            # Resume the timer
            self.timer.resume()
            self.update_menu_button_state()
        else:
            # Start new timer
            duration = self.settings.get_duration(self.current_mode)
            self.timer.start(duration)
            self.update_menu_button_state()
            self.update_timer_title()
        
        # Save state after timer operation
        self._save_current_state()
    
    @rumps.clicked(MENU_RESET)
    def reset_timer(self, sender):
        """Reset the timer."""
        self.timer.reset()
        self.update_timer_title()
        self.update_menu_button_state()
        
        # Save state after reset
        self._save_current_state()
    
    @rumps.clicked(MENU_WORK_MODE)
    def switch_to_work_mode(self, sender):
        """Switch to Work mode."""
        self._switch_mode(MODE_WORK)
    
    @rumps.clicked(MENU_REST_EYES_MODE)
    def switch_to_rest_eyes_mode(self, sender):
        """Switch to Rest Your Eyes mode."""
        self._switch_mode(MODE_REST_EYES)
    
    @rumps.clicked(MENU_LONG_REST_MODE)
    def switch_to_long_rest_mode(self, sender):
        """Switch to Long Rest mode."""
        self._switch_mode(MODE_LONG_REST)
    
    def _switch_mode(self, mode):
        """Switch to a specific timer mode."""
        if self.timer.is_running():
            # Ask user to confirm mode switch in a non-blocking way
            def show_confirmation():
                try:
                    with self._ui_lock:
                        self._ui_update_active = False
                    
                    response = rumps.alert(
                        title="Switch Mode?",
                        message="Timer is running. Do you want to switch modes?",
                        ok="Switch", cancel="Cancel"
                    )
                    
                    if response == 1:  # User clicked Switch (1 = OK)
                        # Switch mode
                        self.current_mode = mode
                        self.settings.set_current_mode(mode)
                        self.timer.reset()
                        self.update_timer_title()
                        self.update_menu_button_state()
                        
                        # Save state after mode switch
                        self._save_current_state()
                finally:
                    with self._ui_lock:
                        self._ui_update_active = True
            
            # Run confirmation in separate thread
            confirmation_thread = threading.Thread(target=show_confirmation, daemon=True)
            confirmation_thread.start()
        else:
            # Switch mode immediately if timer is not running
            self.current_mode = mode
            self.settings.set_current_mode(mode)
            self.timer.reset()
            self.update_timer_title()
            self.update_menu_button_state()
            
            # Save state after mode switch
            self._save_current_state()
    
    @rumps.clicked(MENU_SETTINGS)
    def show_settings(self, sender):
        """Show settings dialog."""
        self._show_settings_dialog()
    
    def _show_settings_dialog(self):
        """Show user-friendly settings dialog with visual increment/decrement controls."""
        # Get current settings
        work_duration = self.settings.get_duration(MODE_WORK)
        rest_eyes_duration = self.settings.get_duration(MODE_REST_EYES)
        long_rest_duration = self.settings.get_duration(MODE_LONG_REST)
        
        # Create a visual settings dialog with increment/decrement controls
        settings_text = f"""
⏱️ TIMER DURATION SETTINGS ⏱️
────────────────────────────────

💼 Work interval duration:
      [-]  [ {work_duration:2d} ]  [+]

👁️ Short break duration:
      [-]  [ {rest_eyes_duration:2d} ]  [+]

🌟 Long break duration:
      [-]  [ {long_rest_duration:2d} ]  [+]

────────────────────────────────
• Click [-] to decrease a value
• Click [+] to increase a value
• Or type a number (1-60) directly in the brackets
• All values are in minutes
"""
        
        window = rumps.Window(
            message="Adjust timer durations using the controls below:",
            title="⏱️ Sharp Timer Settings",
            default_text=settings_text,
            ok="Save Settings", cancel="Cancel",
            dimensions=(450, 350)
        )
        
        response = window.run()
        
        if response.clicked:
            try:
                # Parse the user input
                lines = response.text.strip().split('\n')
                new_values = {}
                
                # Extract numbers from the brackets [ ## ]
                import re
                
                # Look for work duration
                work_lines = [line for line in lines if '💼' in line or 'Work' in line]
                if work_lines:
                    # Find the next line with brackets
                    for i, line in enumerate(lines):
                        if any(work in line for work in work_lines) or (i > 0 and any(work in lines[i-1] for work in work_lines)):
                            # Look for numbers in brackets
                            bracket_numbers = re.findall(r'\[\s*(\d{1,2})\s*\]', line)
                            if bracket_numbers:
                                new_values[MODE_WORK] = int(bracket_numbers[0])
                                break
                
                # Look for rest eyes duration
                rest_lines = [line for line in lines if '👁️' in line or 'Short break' in line]
                if rest_lines:
                    # Find the next line with brackets
                    for i, line in enumerate(lines):
                        if any(rest in line for rest in rest_lines) or (i > 0 and any(rest in lines[i-1] for rest in rest_lines)):
                            # Look for numbers in brackets
                            bracket_numbers = re.findall(r'\[\s*(\d{1,2})\s*\]', line)
                            if bracket_numbers:
                                new_values[MODE_REST_EYES] = int(bracket_numbers[0])
                                break
                
                # Look for long rest duration
                long_lines = [line for line in lines if '🌟' in line or 'Long break' in line]
                if long_lines:
                    # Find the next line with brackets
                    for i, line in enumerate(lines):
                        if any(long in line for long in long_lines) or (i > 0 and any(long in lines[i-1] for long in long_lines)):
                            # Look for numbers in brackets
                            bracket_numbers = re.findall(r'\[\s*(\d{1,2})\s*\]', line)
                            if bracket_numbers:
                                new_values[MODE_LONG_REST] = int(bracket_numbers[0])
                                break
                
                # Validate we have all three values
                if len(new_values) != 3:
                    rumps.alert(
                        title="Missing Values",
                        message="Please ensure all three timer durations are set:\n\n• Work interval (💼)\n• Short break (👁️)\n• Long break (🌟)\n\nEach must be a number between 1 and 60.",
                        ok="OK"
                    )
                    return
                
                # Validate each value
                for mode, duration in new_values.items():
                    if not 1 <= duration <= 60:
                        mode_names = {
                            MODE_WORK: "Work interval",
                            MODE_REST_EYES: "Short break",
                            MODE_LONG_REST: "Long break"
                        }
                        rumps.alert(
                            title="Invalid Duration",
                            message=f"{mode_names[mode]} duration must be between 1 and 60 minutes.\n\nYou entered: {duration}",
                            ok="OK"
                        )
                        return
                
                # All validations passed - update settings
                self.settings.set_duration(MODE_WORK, new_values[MODE_WORK])
                self.settings.set_duration(MODE_REST_EYES, new_values[MODE_REST_EYES])
                self.settings.set_duration(MODE_LONG_REST, new_values[MODE_LONG_REST])
                
                # Update menu items and display
                self._update_menu_labels()
                self.update_timer_title()
                
                # Show success notification
                rumps.notification(
                    title="✅ Settings Saved Successfully!",
                    subtitle=f"Work: {new_values[MODE_WORK]}m | Short break: {new_values[MODE_REST_EYES]}m | Long break: {new_values[MODE_LONG_REST]}m",
                    message="Your timer preferences have been updated.",
                    sound=False
                )
                
            except Exception as e:
                rumps.alert(
                    title="Error",
                    message=f"An error occurred while saving settings:\n\n{str(e)}\n\nPlease check your input and try again.",
                    ok="OK"
                )
    
    def _update_menu_labels(self):
        """Update menu labels with current durations."""
        work_duration = self.settings.get_duration(MODE_WORK)
        rest_eyes_duration = self.settings.get_duration(MODE_REST_EYES)
        long_rest_duration = self.settings.get_duration(MODE_LONG_REST)
        
        self.menu[MENU_WORK_MODE].title = f"{MODE_ICONS[MODE_WORK]} Work Mode ({work_duration}m)"
        self.menu[MENU_REST_EYES_MODE].title = f"{MODE_ICONS[MODE_REST_EYES]} Rest Your Eyes ({rest_eyes_duration}m)"
        self.menu[MENU_LONG_REST_MODE].title = f"{MODE_ICONS[MODE_LONG_REST]} Long Rest ({long_rest_duration}m)"
    
    @rumps.clicked(MENU_QUIT)
    def quit_app(self, sender):
        """Quit application with confirmation if needed."""
        # Check if we need to show quit dialog
        if not self.quit_dialog_manager.should_show_quit_dialog():
            # No timer running, quit immediately
            rumps.quit_application()
            return
        
        # Show quit dialog and handle response synchronously for quit action
        response = self.quit_dialog_manager.show_quit_confirmation()
        if response and response.action != QuitAction.CANCEL:
            # Execute quit action immediately
            self.quit_dialog_manager.execute_quit_action(response)
    
    def _restore_timer_state(self):
        """Restore timer state from previous session."""
        saved_state = self.settings.load_timer_state()
        if saved_state and saved_state.is_valid():
            print(f"Restored timer state: {saved_state.mode}, {saved_state.remaining_seconds}s, running={saved_state.is_running}")
            
            # Restore timer state
            self.current_mode = saved_state.mode
            self.settings.set_current_mode(saved_state.mode)
            
            if saved_state.is_running and not saved_state.is_paused:
                # Resume running timer with exact remaining seconds
                if saved_state.remaining_seconds > 0:
                    self.timer.start_with_seconds(saved_state.remaining_seconds)
                else:
                    # Fallback to 1 minute if somehow remaining seconds is 0 or negative
                    self.timer.start(1)
            elif saved_state.is_paused:
                # Set up paused timer
                self.timer.reset()
                # Timer will show remaining time when started
            
            # Update UI elements after restoration
            self.update_timer_title()
            self.update_menu_button_state()
        else:
            print("No valid timer state found, starting fresh")
    
    def _save_current_state(self):
        """Save current timer state."""
        try:
            current_state = self._get_current_timer_state()
            if current_state:
                self.settings.save_timer_state(current_state)
        except Exception as e:
            print(f"Error saving timer state: {e}")
    
    def _get_current_timer_state(self) -> TimerState:
        """Get current timer state."""
        try:
            remaining_time = self.timer.get_remaining_time()
            remaining_seconds = remaining_time[0] * 60 + remaining_time[1]
            
            return TimerState(
                mode=self.current_mode,
                remaining_seconds=remaining_seconds,
                is_running=self.timer.is_running(),
                is_paused=self.timer.is_paused(),
                session_id="",  # Will be generated
                start_timestamp=0,  # Will be set
                last_update_timestamp=time.time(),
                total_duration_seconds=self.settings.get_duration(self.current_mode) * 60
            )
        except Exception as e:
            print(f"Error getting current timer state: {e}")
            return None
    
    def _start_backup_timer(self):
        """Start periodic backup timer."""
        def backup_periodically():
            while True:
                time.sleep(30)  # Backup every 30 seconds
                if self.timer.is_running() or self.timer.is_paused():
                    self._save_current_state()
        
        backup_thread = threading.Thread(target=backup_periodically, daemon=True)
        backup_thread.start()
    
    def _setup_system_event_callbacks(self):
        """Setup system event callbacks."""
        def on_sleep():
            print("System sleep detected, saving timer state")
            self._save_current_state()
        
        def on_wake():
            print("System wake detected, checking timer state")
            # Timer state will be automatically handled by system_events.py
        
        self.system_event_manager.set_sleep_callback(on_sleep)
        self.system_event_manager.set_wake_callback(on_wake)


def main():
    """Main entry point for the application."""
    app = SharpTimer()
    app.run()


if __name__ == "__main__":
    main()
