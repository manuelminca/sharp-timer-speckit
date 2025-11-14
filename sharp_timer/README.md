# Sharp Timer

A minimalist macOS timer app that runs exclusively in the menu bar.

## Features

- **Menu Bar Only**: Never appears in the dock
- **Three Modes**: Work (25min), Rest Your Eyes (5min), Long Rest (15min)
- **Customizable**: Adjust duration for each mode
- **Native Notifications**: macOS notifications when timer completes
- **Sound Alerts**: Audio notification when sessions complete
- **Persistent Settings**: Your preferences are saved automatically

## Installation

1. Clone or download this repository
2. Install Python 3.8 or later
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python main.py
   ```

## Usage

1. **Start Timer**: Click "Start" in the menu bar
2. **Switch Modes**: Select from Work, Rest Your Eyes, or Long Rest
3. **Customize**: Choose "Settings..." to adjust durations
4. **Pause/Resume**: Click "Start" again to pause or resume

## Customization

All timer modes are fully customizable:

- Work Mode: Default 25 minutes
- Rest Your Eyes Mode: Default 5 minutes  
- Long Rest Mode: Default 15 minutes

Access Settings from the menu bar to adjust any duration between 1-60 minutes.

## System Requirements

- macOS 10.10 or later
- Python 3.8 or later
- Only one external dependency: `rumps`

## License

MIT License
