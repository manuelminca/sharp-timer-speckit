"""Timer engine for Sharp Timer."""

import threading
import time
from typing import Callable, Optional
from constants import MODE_WORK, MODE_REST_EYES, MODE_LONG_REST


class TimerEngine:
    """High-performance timer engine with threading."""
    
    def __init__(self, completion_callback: Callable):
        """Initialize timer engine.
        
        Args:
            completion_callback: Function to call when timer completes
        """
        self.completion_callback = completion_callback
        self.duration = 0  # Total duration in seconds
        self.remaining = 0  # Remaining time in seconds
        self.running = False
        self.paused = False
        self.timer_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
    
    def start(self, duration_minutes: int):
        """Start the timer with specified duration in minutes.
        
        Args:
            duration_minutes: Duration in minutes
        """
        if duration_minutes <= 0:
            return
        
        # Stop any existing timer
        self.stop()
        
        # Set up new timer
        self.duration = duration_minutes * 60  # Convert to seconds
        self.remaining = self.duration
        self.running = True
        self.paused = False
        self.stop_event.clear()
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
    
    def start_with_seconds(self, duration_seconds: int):
        """Start the timer with specified duration in seconds.
        
        Args:
            duration_seconds: Duration in seconds
        """
        if duration_seconds <= 0:
            return
        
        # Stop any existing timer
        self.stop()
        
        # Set up new timer
        self.duration = duration_seconds
        self.remaining = duration_seconds
        self.running = True
        self.paused = False
        self.stop_event.clear()
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
    
    def pause(self):
        """Pause the timer."""
        if self.running and not self.paused:
            self.paused = True
    
    def resume(self):
        """Resume the timer."""
        if self.running and self.paused:
            self.paused = False
    
    def stop(self):
        """Stop the timer."""
        self.running = False
        self.paused = False
        self.stop_event.set()
        
        # Wait for timer thread to finish
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1.0)
    
    def reset(self):
        """Reset the timer to initial state."""
        self.stop()
        self.remaining = 0
    
    def get_remaining_time(self) -> tuple[int, int]:
        """Get remaining time as (minutes, seconds).
        
        Returns:
            Tuple of (minutes, seconds)
        """
        if not self.running or self.paused:
            return divmod(max(0, self.remaining), 60)
        return divmod(max(0, self.remaining), 60)
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0.0 to 1.0).
        
        Returns:
            Progress percentage
        """
        if self.duration == 0:
            return 0.0
        return max(0.0, min(1.0, (self.duration - self.remaining) / self.duration))
    
    def is_running(self) -> bool:
        """Check if timer is running.
        
        Returns:
            True if timer is running
        """
        return self.running and not self.paused
    
    def is_paused(self) -> bool:
        """Check if timer is paused.
        
        Returns:
            True if timer is paused
        """
        return self.paused
    
    def _timer_loop(self):
        """Main timer loop running in separate thread."""
        while self.running and not self.stop_event.is_set():
            if not self.paused:
                if self.remaining <= 0:
                    # Timer completed
                    self.running = False
                    # Call completion callback in main thread
                    self.completion_callback()
                    break
                
                # Decrement remaining time
                self.remaining -= 1
            
            # Sleep for 1 second (or less if paused for responsiveness)
            sleep_time = 0.1 if self.paused else 1.0
            time.sleep(sleep_time)
