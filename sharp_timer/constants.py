"""Application constants and default values."""

# App metadata
APP_NAME = "Sharp Timer"
APP_VERSION = "1.0.0"
APP_SUPPORT_DIR = "Library/Application Support/Sharp Timer"

# Default timer durations (in minutes)
DEFAULT_WORK_DURATION = 25
DEFAULT_REST_EYES_DURATION = 5
DEFAULT_LONG_REST_DURATION = 15

# Timer modes
MODE_WORK = "work"
MODE_REST_EYES = "rest_eyes"
MODE_LONG_REST = "long_rest"

# Mode display names
MODE_NAMES = {
    MODE_WORK: "Work",
    MODE_REST_EYES: "Rest Your Eyes",
    MODE_LONG_REST: "Long Rest"
}

# Mode icons
MODE_ICONS = {
    MODE_WORK: "💼",
    MODE_REST_EYES: "👁️",
    MODE_LONG_REST: "🌟"
}

# Settings file
SETTINGS_FILENAME = "settings.json"

# Menu items
MENU_START = "Start"
MENU_PAUSE = "Pause"
MENU_RESET = "Reset"
MENU_SEPARATOR = None
MENU_WORK_MODE = f"{MODE_ICONS[MODE_WORK]} Work Mode ({DEFAULT_WORK_DURATION}m)"
MENU_REST_EYES_MODE = f"{MODE_ICONS[MODE_REST_EYES]} Rest Your Eyes ({DEFAULT_REST_EYES_DURATION}m)"
MENU_LONG_REST_MODE = f"{MODE_ICONS[MODE_LONG_REST]} Long Rest ({DEFAULT_LONG_REST_DURATION}m)"
MENU_SETTINGS = "Settings..."
MENU_QUIT = "Quit"
