"""Main application entry point for Sharp Timer."""

import rumps
from timer import TimerEngine
from settings import SettingsManager
from notifications import NotificationManager
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
        """Initialize the Sharp Timer application."""
        super(SharpTimer, self).__init__("⏱️", quit_button=None)
        
        # Initialize components
        self.settings = SettingsManager()
        self.timer = TimerEngine(self._on_timer_complete)
        
        # Application state
        self.current_mode = self.settings.get_current_mode()
        self.update_timer_title()
        
        # Set up menu
        self._setup_menu()
        
        # Start update timer for UI
        rumps.Timer(self._update_ui, 1.0).start()
    
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
    
    def _update_ui(self, sender):
        """Update UI periodically (called by timer)."""
        if self.timer.is_running():
            self.update_timer_title()
    
    def _on_timer_complete(self):
        """Handle timer completion."""
        mode_name = MODE_NAMES.get(self.current_mode, "Session")
        duration = self.settings.get_duration(self.current_mode)
        
        # Send notification
        NotificationManager.notify_timer_complete(mode_name, duration)
        
        # Update UI
        self.update_timer_title()
        
        # Update menu to show Start again
        self.menu[MENU_START].title = MENU_START
    
    @rumps.clicked(MENU_START)
    def start_timer(self, sender):
        """Start or pause the timer."""
        if self.timer.is_running():
            # Pause the timer
            self.timer.pause()
            sender.title = MENU_START
        elif self.timer.is_paused():
            # Resume the timer
            self.timer.resume()
            sender.title = MENU_PAUSE
        else:
            # Start new timer
            duration = self.settings.get_duration(self.current_mode)
            self.timer.start(duration)
            sender.title = MENU_PAUSE
            self.update_timer_title()
    
    @rumps.clicked(MENU_RESET)
    def reset_timer(self, sender):
        """Reset the timer."""
        self.timer.reset()
        self.update_timer_title()
        self.menu[MENU_START].title = MENU_START
    
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
            # Ask user to confirm mode switch
            response = rumps.alert(
                title="Switch Mode?",
                message="Timer is running. Do you want to switch modes?",
                ok="Switch", cancel="Cancel"
            )
            if response == 0:  # User clicked Cancel
                return
        
        # Switch mode
        self.current_mode = mode
        self.settings.set_current_mode(mode)
        self.timer.reset()
        self.update_timer_title()
        self.menu[MENU_START].title = MENU_START
    
    @rumps.clicked(MENU_SETTINGS)
    def show_settings(self, sender):
        """Show settings dialog."""
        self._show_settings_dialog()
    
    def _show_settings_dialog(self):
        """Show settings dialog for customizing durations."""
        # Get current settings
        work_duration = self.settings.get_duration(MODE_WORK)
        rest_eyes_duration = self.settings.get_duration(MODE_REST_EYES)
        long_rest_duration = self.settings.get_duration(MODE_LONG_REST)
        
        # Create settings window
        window = rumps.Window(
            message="Configure timer durations (1-60 minutes):",
            title="Sharp Timer Settings",
            default_text=f"Work: {work_duration}\nRest Eyes: {rest_eyes_duration}\nLong Rest: {long_rest_duration}",
            ok="Save", cancel="Cancel"
        )
        
        response = window.run()
        
        if response.clicked:
            try:
                # Parse user input
                lines = response.text.strip().split('\n')
                new_values = {}
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = int(value.strip())
                        
                        if 'work' in key:
                            new_values[MODE_WORK] = value
                        elif 'rest' in key and 'eyes' in key:
                            new_values[MODE_REST_EYES] = value
                        elif 'long' in key:
                            new_values[MODE_LONG_REST] = value
                
                # Update settings
                for mode, duration in new_values.items():
                    if 1 <= duration <= 60:
                        self.settings.set_duration(mode, duration)
                
                # Update menu items and display
                self._update_menu_labels()
                self.update_timer_title()
                
                rumps.notification(
                    title="Settings Saved",
                    subtitle="Timer durations have been updated",
                    message="Your preferences have been saved.",
                    sound=False
                )
                
            except (ValueError, AttributeError):
                rumps.alert(
                    title="Invalid Input",
                    message="Please enter valid numbers between 1 and 60.",
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
        """Quit the application."""
        self.timer.stop()
        rumps.quit_application()


def main():
    """Main entry point for the application."""
    app = SharpTimer()
    app.run()


if __name__ == "__main__":
    main()
