"""
Pomodoro Timer Core Logic
Handles timer state, countdown functionality, and session management.
"""
import time
import threading
from enum import Enum
from typing import Callable, Optional
from pomodoro_settings import PomodoroSettings


class TimerState(Enum):
    """Enum for timer states."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"


class PomodoroTimer:
    """Core Pomodoro timer logic with customizable settings."""
    
    def __init__(self, settings: PomodoroSettings):
        """Initialize timer with settings manager."""
        self.settings = settings
        self.state = TimerState.STOPPED
        self.current_session_type = "work"  # "work" or "break"
        self.time_remaining = 0  # seconds
        self.total_time = 0  # seconds
        self.completed_sessions = 0
        
        # Callbacks for UI updates
        self.on_tick: Optional[Callable[[int], None]] = None
        self.on_session_complete: Optional[Callable[[str], None]] = None
        self.on_state_change: Optional[Callable[[TimerState], None]] = None
        
        # Timer thread
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def set_callbacks(self, 
                     on_tick: Optional[Callable[[int], None]] = None,
                     on_session_complete: Optional[Callable[[str], None]] = None,
                     on_state_change: Optional[Callable[[TimerState], None]] = None) -> None:
        """Set callback functions for timer events."""
        if on_tick:
            self.on_tick = on_tick
        if on_session_complete:
            self.on_session_complete = on_session_complete
        if on_state_change:
            self.on_state_change = on_state_change
    
    def start_work_session(self) -> None:
        """Start a new work session."""
        if self.state == TimerState.RUNNING:
            return
        
        self.current_session_type = "work"
        self.time_remaining = self.settings.get_work_time() * 60  # convert to seconds
        self.total_time = self.time_remaining
        self._start_timer()
        
        # Play start sound if enabled
        if self.settings.get_sound_setting('start'):
            self._play_sound('start')
    
    def start_break_session(self) -> None:
        """Start a new break session."""
        if self.state == TimerState.RUNNING:
            return
        
        self.current_session_type = "break"
        self.time_remaining = self.settings.get_break_time() * 60  # convert to seconds
        self.total_time = self.time_remaining
        self._start_timer()
        
        # Play start sound if enabled
        if self.settings.get_sound_setting('start'):
            self._play_sound('start')
    
    def pause(self) -> None:
        """Pause the current timer."""
        if self.state == TimerState.RUNNING:
            self._stop_event.set()
            self.state = TimerState.PAUSED
            if self.on_state_change:
                self.on_state_change(self.state)
    
    def resume(self) -> None:
        """Resume a paused timer."""
        if self.state == TimerState.PAUSED:
            self._start_timer()
    
    def stop(self) -> None:
        """Stop the current timer and reset."""
        self._stop_event.set()
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join()
        
        self.state = TimerState.STOPPED
        self.time_remaining = 0
        self.total_time = 0
        
        if self.on_state_change:
            self.on_state_change(self.state)
        if self.on_tick:
            self.on_tick(0)
    
    def get_progress_percentage(self) -> float:
        """Get current progress as percentage (0-100)."""
        if self.total_time == 0:
            return 0.0
        return ((self.total_time - self.time_remaining) / self.total_time) * 100
    
    def get_formatted_time(self) -> str:
        """Get formatted time string (MM:SS)."""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_session_info(self) -> dict:
        """Get current session information."""
        return {
            'type': self.current_session_type,
            'state': self.state.value,
            'time_remaining': self.time_remaining,
            'formatted_time': self.get_formatted_time(),
            'progress_percentage': self.get_progress_percentage(),
            'completed_sessions': self.completed_sessions
        }
    
    def _start_timer(self) -> None:
        """Start the timer thread."""
        self._stop_event.clear()
        self.state = TimerState.RUNNING
        if self.on_state_change:
            self.on_state_change(self.state)
        
        self._timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self._timer_thread.start()
    
    def _timer_loop(self) -> None:
        """Main timer loop running in separate thread."""
        last_tick_time = time.time()
        
        while not self._stop_event.is_set() and self.time_remaining > 0:
            current_time = time.time()
            
            # Only update if at least 1 second has passed
            if current_time - last_tick_time >= 1.0:
                self.time_remaining -= 1
                last_tick_time = current_time
                
                # Play tick sound if enabled
                if self.settings.get_sound_setting('tick'):
                    self._play_sound('tick')
                
                # Update UI
                if self.on_tick:
                    self.on_tick(self.time_remaining)
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
        
        # Timer completed
        if not self._stop_event.is_set() and self.time_remaining <= 0:
            self._session_complete()
    
    def _session_complete(self) -> None:
        """Handle session completion."""
        self.state = TimerState.STOPPED
        
        # Play end sound if enabled
        if self.settings.get_sound_setting('end'):
            self._play_sound('end')
        
        # Increment completed sessions counter
        if self.current_session_type == "work":
            self.completed_sessions += 1
        
        # Notify UI
        if self.on_session_complete:
            self.on_session_complete(self.current_session_type)
        if self.on_state_change:
            self.on_state_change(self.state)
    
    def _play_sound(self, sound_type: str) -> None:
        """Play sound (placeholder - would use actual sound library in production)."""
        # In a real implementation, this would play actual sound files
        # For now, just print to console for demonstration
        sound_messages = {
            'start': "🔔 セッション開始!",
            'end': "✅ セッション完了!",
            'tick': "⏰"
        }
        print(sound_messages.get(sound_type, f"Sound: {sound_type}"))