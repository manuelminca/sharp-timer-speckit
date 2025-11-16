"""System event handling for Sharp Timer."""

import time
import threading
from typing import Optional, Callable
from timer_state import TimerState


class SystemEventManager:
    """Handles system sleep/wake events."""
    
    def __init__(self, timer_state_manager, timer_engine):
        self.timer_state_manager = timer_state_manager
        self.timer_engine = timer_engine
        self.sleep_callback: Optional[Callable] = None
        self.wake_callback: Optional[Callable] = None
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Setup system event monitoring
        self._setup_system_event_monitoring()
    
    def _setup_system_event_monitoring(self):
        """Setup monitoring for system sleep/wake events."""
        try:
            # Try to use pyobjc-framework-SystemConfiguration if available
            self._setup_native_monitoring()
        except ImportError:
            print("Warning: pyobjc-framework-SystemConfiguration not available, using fallback")
            self._setup_fallback_monitoring()
        except Exception as e:
            print(f"Warning: Could not setup system event monitoring: {e}")
            self._setup_fallback_monitoring()
    
    def _setup_native_monitoring(self):
        """Setup native macOS system event monitoring."""
        try:
            from SystemConfiguration import SCDynamicStoreCopyValue, SCDynamicStoreCreate
            from CoreFoundation import CFRunLoopGetCurrent, CFRunLoopRun
            
            # This would be the ideal implementation using pyobjc
            # For now, we'll use the fallback approach
            print("Native system monitoring available but not fully implemented")
            self._setup_fallback_monitoring()
        except ImportError:
            raise ImportError("pyobjc-framework-SystemConfiguration not available")
    
    def _setup_fallback_monitoring(self):
        """Setup fallback monitoring using periodic checks."""
        self._monitoring_active = True
        self._last_check_time = time.time()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def _monitor_loop(self):
        """Monitor loop for fallback approach."""
        while self._monitoring_active:
            try:
                current_time = time.time()
                
                # Check for significant time gaps (indicating sleep/wake)
                time_diff = current_time - self._last_check_time
                
                if time_diff > 60:  # More than 1 minute gap suggests sleep
                    self._handle_potential_sleep_wake(time_diff)
                
                self._last_check_time = current_time
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(30)
    
    def _handle_potential_sleep_wake(self, time_gap: float):
        """Handle potential sleep/wake event."""
        try:
            print(f"Detected potential sleep/wake event (gap: {time_gap:.1f}s)")
            
            # Save current state before processing
            current_state = self._get_current_timer_state()
            if current_state:
                # Mark as survived sleep
                current_state.survived_sleep = True
                current_state.last_update_timestamp = time.time()
                
                # Adjust remaining time based on sleep duration
                self._adjust_for_sleep_duration(current_state, time_gap)
                
                # Save updated state
                self.timer_state_manager.save_timer_state(current_state)
                
                # Call wake callback
                if self.wake_callback:
                    self.wake_callback()
            
        except Exception as e:
            print(f"Error handling sleep/wake event: {e}")
    
    def on_system_sleep(self):
        """Handle system sleep event."""
        try:
            print("System sleep detected")
            
            # Save current state before sleep
            current_state = self._get_current_timer_state()
            if current_state:
                current_state.survived_sleep = True
                self.timer_state_manager.save_timer_state(current_state)
            
            # Call sleep callback
            if self.sleep_callback:
                self.sleep_callback()
                
        except Exception as e:
            print(f"Error handling system sleep: {e}")
    
    def on_system_wake(self):
        """Handle system wake event."""
        try:
            print("System wake detected")
            
            # Validate and restore state after wake
            restored_state = self.timer_state_manager.load_timer_state()
            if restored_state and restored_state.survived_sleep:
                # Adjust for sleep duration if needed
                self._adjust_for_sleep_duration(restored_state, 0)
                
                # Update timer engine if needed
                self._restore_timer_engine_state(restored_state)
            
            # Call wake callback
            if self.wake_callback:
                self.wake_callback()
                
        except Exception as e:
            print(f"Error handling system wake: {e}")
    
    def _get_current_timer_state(self) -> Optional[TimerState]:
        """Get current timer state."""
        try:
            if not self.timer_engine:
                return None
            
            remaining_time = self.timer_engine.get_remaining_time()
            remaining_seconds = remaining_time[0] * 60 + remaining_time[1]
            
            from settings import SettingsManager
            settings = SettingsManager()
            
            return TimerState(
                mode=settings.get_current_mode(),
                remaining_seconds=remaining_seconds,
                is_running=self.timer_engine.is_running(),
                is_paused=self.timer_engine.is_paused(),
                session_id="",  # Will be generated
                start_timestamp=0,  # Will be set
                last_update_timestamp=time.time(),
                total_duration_seconds=settings.get_duration(settings.get_current_mode()) * 60
            )
        except Exception as e:
            print(f"Error getting current timer state: {e}")
            return None
    
    def _adjust_for_sleep_duration(self, state: TimerState, sleep_duration: float):
        """Adjust timer state for sleep duration."""
        try:
            if state.is_running and not state.is_paused:
                # Timer was running during sleep, subtract sleep time
                state.remaining_seconds -= int(sleep_duration)
                
                # Ensure we don't go negative
                if state.remaining_seconds < 0:
                    state.remaining_seconds = 0
                    state.is_running = False
                    state.is_paused = False
                
                print(f"Adjusted remaining time after sleep: {state.remaining_seconds}s")
            
        except Exception as e:
            print(f"Error adjusting for sleep duration: {e}")
    
    def _restore_timer_engine_state(self, state: TimerState):
        """Restore timer engine state from saved state."""
        try:
            if not self.timer_engine:
                return
            
            # If timer was running, we might want to restart it
            # This depends on user preference - for now, we'll leave it paused
            if state.is_running and not state.is_paused:
                print("Timer was running before sleep, leaving paused for user to resume")
            
        except Exception as e:
            print(f"Error restoring timer engine state: {e}")
    
    def set_sleep_callback(self, callback: Callable):
        """Set callback for sleep events."""
        self.sleep_callback = callback
    
    def set_wake_callback(self, callback: Callable):
        """Set callback for wake events."""
        self.wake_callback = callback
    
    def start_monitoring(self):
        """Start system event monitoring."""
        if not self._monitoring_active:
            self._monitoring_active = True
            if not self._monitor_thread or not self._monitor_thread.is_alive():
                self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
                self._monitor_thread.start()
            print("System event monitoring started")
    
    def stop_monitoring(self):
        """Stop system event monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("System event monitoring stopped")
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active."""
        return self._monitoring_active
    
    def test_sleep_wake_handling(self):
        """Test sleep/wake handling functionality."""
        print("Testing sleep/wake handling...")
        
        # Simulate sleep event
        self.on_system_sleep()
        time.sleep(1)
        
        # Simulate wake event
        self.on_system_wake()
        
        print("Sleep/wake handling test completed")


class SystemEventSimulator:
    """Simulator for testing system events."""
    
    def __init__(self, system_event_manager: SystemEventManager):
        self.system_event_manager = system_event_manager
    
    def simulate_sleep(self, duration_seconds: int = 300):
        """Simulate system sleep for specified duration."""
        print(f"Simulating system sleep for {duration_seconds} seconds...")
        
        # Trigger sleep event
        self.system_event_manager.on_system_sleep()
        
        # Wait for specified duration
        time.sleep(2)  # Shortened for testing
        
        # Trigger wake event
        self.system_event_manager.on_system_wake()
        
        print(f"Simulated sleep completed")
    
    def simulate_time_gap(self, gap_seconds: int):
        """Simulate a time gap (like system sleep)."""
        print(f"Simulating time gap of {gap_seconds} seconds...")
        
        # Manually trigger the gap handling
        self.system_event_manager._handle_potential_sleep_wake(gap_seconds)
        
        print(f"Time gap simulation completed")
