"""pytest configuration for Sharp Timer tests."""

import pytest
import tempfile
import shutil
import sys
import os
from pathlib import Path

# Add the sharp_timer directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def temp_settings_dir():
    """Create temporary settings directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_settings_manager(temp_settings_dir):
    """Create test settings manager."""
    # Mock the settings directory
    from sharp_timer.settings import SettingsManager
    original_support_dir = SettingsManager.APP_SUPPORT_DIR
    SettingsManager.APP_SUPPORT_DIR = Path(temp_dir).name
    
    manager = SettingsManager()
    yield manager
    
    # Restore original
    SettingsManager.APP_SUPPORT_DIR = original_support_dir

@pytest.fixture
def sample_timer_state():
    """Create sample timer state for testing."""
    import time
    from sharp_timer.timer_state import TimerState
    
    return TimerState(
        mode="work",
        remaining_seconds=1500,
        is_running=True,
        is_paused=False,
        session_id="test-session-123",
        start_timestamp=1699999999.0,
        last_update_timestamp=1700000000.0,
        total_duration_seconds=1500
    )

@pytest.fixture
def timer_state_manager(temp_settings_dir):
    """Create timer state manager for testing."""
    from sharp_timer.timer_state import TimerStateManager
    
    # Mock the settings directory
    original_support_dir = "Library/Application Support/Sharp Timer"
    TimerStateManager.APP_SUPPORT_DIR = Path(temp_settings_dir).name
    
    manager = TimerStateManager()
    yield manager
    
    # Restore original
    TimerStateManager.APP_SUPPORT_DIR = original_support_dir
