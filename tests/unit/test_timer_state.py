"""Unit tests for timer state management."""

import pytest
import time
from sharp_timer.timer_state import TimerState, TimerStateManager


class TestTimerState:
    """Test TimerState class."""
    
    def test_timer_state_creation(self):
        """Test creating a timer state."""
        state = TimerState(
            mode="work",
            remaining_seconds=1500,
            is_running=True,
            is_paused=False,
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        
        assert state.mode == "work"
        assert state.remaining_seconds == 1500
        assert state.is_running is True
        assert state.is_paused is False
        assert state.is_valid()
    
    def test_timer_state_validation(self):
        """Test timer state validation."""
        # Valid state
        valid_state = TimerState(
            mode="work",
            remaining_seconds=1500,
            is_running=True,
            is_paused=False,
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        assert valid_state.is_valid()
        
        # Invalid state - running and paused
        invalid_state = TimerState(
            mode="work",
            remaining_seconds=1500,
            is_running=True,
            is_paused=True,  # Both True - invalid
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        assert not invalid_state.is_valid()
        
        # Invalid state - negative remaining time
        invalid_state2 = TimerState(
            mode="work",
            remaining_seconds=-1,
            is_running=True,
            is_paused=False,
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        assert not invalid_state2.is_valid()
        
        # Invalid state - invalid mode
        invalid_state3 = TimerState(
            mode="invalid_mode",
            remaining_seconds=1500,
            is_running=True,
            is_paused=False,
            session_id="test-123",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        assert not invalid_state3.is_valid()
    
    def test_timer_state_serialization(self):
        """Test timer state serialization and deserialization."""
        original_state = TimerState(
            mode="rest_eyes",
            remaining_seconds=300,
            is_running=False,
            is_paused=True,
            session_id="test-456",
            start_timestamp=1699999999.0,
            last_update_timestamp=1700000000.0,
            total_duration_seconds=300
        )
        
        # Serialize to dict
        state_dict = original_state.to_dict()
        assert isinstance(state_dict, dict)
        assert state_dict['mode'] == "rest_eyes"
        assert state_dict['remaining_seconds'] == 300
        
        # Deserialize from dict
        restored_state = TimerState.from_dict(state_dict)
        assert restored_state.mode == original_state.mode
        assert restored_state.remaining_seconds == original_state.remaining_seconds
        assert restored_state.is_running == original_state.is_running
        assert restored_state.is_paused == original_state.is_paused
    
    def test_timer_state_auto_generation(self):
        """Test automatic generation of session_id and timestamps."""
        state = TimerState(
            mode="work",
            remaining_seconds=1500,
            is_running=True,
            is_paused=False,
            session_id="",  # Empty - should be auto-generated
            start_timestamp=0,  # Zero - should be auto-generated
            last_update_timestamp=0,  # Zero - should be auto-generated
            total_duration_seconds=1500
        )
        
        assert state.session_id != ""
        assert len(state.session_id) > 0
        assert state.start_timestamp > 0
        assert state.last_update_timestamp > 0


class TestTimerStateManager:
    """Test TimerStateManager class."""
    
    def test_save_and_load_timer_state(self, test_settings_manager, sample_timer_state):
        """Test saving and loading timer state."""
        manager = TimerStateManager()
        
        # Save state
        assert manager.save_timer_state(sample_timer_state) is True
        
        # Load state
        loaded_state = manager.load_timer_state()
        assert loaded_state is not None
        assert loaded_state.mode == sample_timer_state.mode
        assert loaded_state.remaining_seconds == sample_timer_state.remaining_seconds
        assert loaded_state.is_valid()
    
    def test_backup_creation(self, test_settings_manager, sample_timer_state):
        """Test creating timer state backup."""
        manager = TimerStateManager()
        
        # Create backup
        assert manager.create_backup(sample_timer_state) is True
        
        # Check backup files exist
        backup_files = list(manager.backup_dir.glob('timer_state_backup_*.json'))
        assert len(backup_files) > 0
    
    def test_restore_from_backup(self, test_settings_manager, sample_timer_state):
        """Test restoring timer state from backup."""
        manager = TimerStateManager()
        
        # Create backup first
        assert manager.create_backup(sample_timer_state) is True
        
        # Restore from backup
        restored_state = manager.restore_from_backup()
        assert restored_state is not None
        assert restored_state.mode == sample_timer_state.mode
        assert restored_state.remaining_seconds == sample_timer_state.remaining_seconds
        assert restored_state.is_valid()
    
    def test_clear_timer_state(self, test_settings_manager, sample_timer_state):
        """Test clearing timer state."""
        manager = TimerStateManager()
        
        # Save state first
        assert manager.save_timer_state(sample_timer_state) is True
        
        # Clear state
        assert manager.clear_timer_state() is True
        
        # Try to load - should return None
        loaded_state = manager.load_timer_state()
        assert loaded_state is None
    
    def test_validate_timer_state(self, test_settings_manager, sample_timer_state):
        """Test timer state validation."""
        manager = TimerStateManager()
        
        # Valid state
        assert manager.validate_timer_state(sample_timer_state) is True
        
        # Invalid state
        invalid_state = TimerState(
            mode="invalid",
            remaining_seconds=1500,
            is_running=True,
            is_paused=True,  # Invalid - both running and paused
            session_id="test",
            start_timestamp=time.time(),
            last_update_timestamp=time.time(),
            total_duration_seconds=1500
        )
        assert manager.validate_timer_state(invalid_state) is False
    
    def test_get_state_history(self, test_settings_manager, sample_timer_state):
        """Test getting state history from backups."""
        manager = TimerStateManager()
        
        # Create multiple backups
        for i in range(3):
            sample_timer_state.session_id = f"test-{i}"
            assert manager.create_backup(sample_timer_state) is True
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Get history
        history = manager.get_state_history(limit=5)
        assert len(history) == 3
        assert all(state.is_valid() for state in history)
    
    def test_backup_cleanup(self, test_settings_manager, sample_timer_state):
        """Test that old backups are cleaned up."""
        manager = TimerStateManager()
        
        # Create more than 5 backups
        for i in range(7):
            sample_timer_state.session_id = f"test-{i}"
            assert manager.create_backup(sample_timer_state) is True
            time.sleep(0.1)
        
        # Check that only 5 backups remain
        backup_files = list(manager.backup_dir.glob('timer_state_backup_*.json'))
        assert len(backup_files) == 5
