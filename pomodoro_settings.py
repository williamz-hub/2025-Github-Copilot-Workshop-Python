"""
Pomodoro Timer Settings Management
Handles user preferences for work time, break time, themes, and sound settings.
"""
import json
import os
from typing import Dict, Any


class PomodoroSettings:
    """Manages user settings for the Pomodoro timer application."""
    
    DEFAULT_SETTINGS = {
        'work_time': 25,  # minutes - options: 15, 25, 35, 45
        'break_time': 5,  # minutes - options: 5, 10, 15
        'theme': 'light',  # options: 'light', 'dark', 'focus'
        'sounds': {
            'start': True,
            'end': True,
            'tick': False
        }
    }
    
    WORK_TIME_OPTIONS = [15, 25, 35, 45]
    BREAK_TIME_OPTIONS = [5, 10, 15]
    THEME_OPTIONS = ['light', 'dark', 'focus']
    
    def __init__(self, settings_file: str = 'pomodoro_settings.json'):
        """Initialize settings manager with optional custom settings file."""
        self.settings_file = settings_file
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults if file doesn't exist."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = self.DEFAULT_SETTINGS.copy()
                settings.update(loaded_settings)
                return settings
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, return defaults
                return self.DEFAULT_SETTINGS.copy()
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> None:
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError:
            # Handle permission errors gracefully
            pass
    
    def get_work_time(self) -> int:
        """Get work time in minutes."""
        return self.settings['work_time']
    
    def set_work_time(self, minutes: int) -> bool:
        """Set work time if it's a valid option."""
        if minutes in self.WORK_TIME_OPTIONS:
            self.settings['work_time'] = minutes
            self.save_settings()
            return True
        return False
    
    def get_break_time(self) -> int:
        """Get break time in minutes."""
        return self.settings['break_time']
    
    def set_break_time(self, minutes: int) -> bool:
        """Set break time if it's a valid option."""
        if minutes in self.BREAK_TIME_OPTIONS:
            self.settings['break_time'] = minutes
            self.save_settings()
            return True
        return False
    
    def get_theme(self) -> str:
        """Get current theme."""
        return self.settings['theme']
    
    def set_theme(self, theme: str) -> bool:
        """Set theme if it's a valid option."""
        if theme in self.THEME_OPTIONS:
            self.settings['theme'] = theme
            self.save_settings()
            return True
        return False
    
    def get_sound_setting(self, sound_type: str) -> bool:
        """Get sound setting for specific type (start, end, tick)."""
        return self.settings['sounds'].get(sound_type, False)
    
    def set_sound_setting(self, sound_type: str, enabled: bool) -> bool:
        """Set sound setting for specific type."""
        if sound_type in ['start', 'end', 'tick']:
            self.settings['sounds'][sound_type] = enabled
            self.save_settings()
            return True
        return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get a copy of all current settings."""
        return self.settings.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()