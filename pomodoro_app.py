"""
Pomodoro Timer GUI Application
Customizable Pomodoro timer with themes, settings, and sound controls.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pomodoro_settings import PomodoroSettings
from pomodoro_timer import PomodoroTimer, TimerState


class PomodoroApp:
    """Main GUI application for the customizable Pomodoro timer."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("カスタマイズ可能なポモドーロタイマー")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # Initialize settings and timer
        self.settings = PomodoroSettings()
        self.timer = PomodoroTimer(self.settings)
        
        # Set up timer callbacks
        self.timer.set_callbacks(
            on_tick=self._update_display,
            on_session_complete=self._on_session_complete,
            on_state_change=self._on_state_change
        )
        
        # Theme color schemes
        self.themes = {
            'light': {
                'bg': '#ffffff',
                'fg': '#333333',
                'button_bg': '#e1e1e1',
                'button_fg': '#333333',
                'timer_bg': '#f8f9fa',
                'accent': '#007bff'
            },
            'dark': {
                'bg': '#2b2b2b',
                'fg': '#ffffff',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'timer_bg': '#1e1e1e',
                'accent': '#4dabf7'
            },
            'focus': {
                'bg': '#1a1a2e',
                'fg': '#eee2dc',
                'button_bg': '#16213e',
                'button_fg': '#eee2dc',
                'timer_bg': '#0f0f23',
                'accent': '#ff6b6b'
            }
        }
        
        self._create_widgets()
        self._apply_theme()
        self._update_display(0)
        
        # Start GUI update loop
        self._start_gui_update_loop()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Timer display section
        timer_frame = tk.Frame(main_frame, relief=tk.RAISED, bd=2)
        timer_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        timer_frame.columnconfigure(0, weight=1)
        
        self.session_label = tk.Label(timer_frame, text="ワークセッション", font=("Arial", 16, "bold"))
        self.session_label.grid(row=0, column=0, pady=10)
        
        self.time_label = tk.Label(timer_frame, text="25:00", font=("Arial", 36, "bold"))
        self.time_label.grid(row=1, column=0, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(timer_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, pady=10, padx=20, sticky=(tk.W, tk.E))
        
        self.status_label = tk.Label(timer_frame, text="停止中", font=("Arial", 12))
        self.status_label.grid(row=3, column=0, pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        self.start_work_btn = tk.Button(button_frame, text="ワーク開始", command=self._start_work)
        self.start_work_btn.grid(row=0, column=0, padx=5)
        
        self.start_break_btn = tk.Button(button_frame, text="休憩開始", command=self._start_break)
        self.start_break_btn.grid(row=0, column=1, padx=5)
        
        self.pause_btn = tk.Button(button_frame, text="一時停止", command=self._pause_resume)
        self.pause_btn.grid(row=0, column=2, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="停止", command=self._stop)
        self.stop_btn.grid(row=0, column=3, padx=5)
        
        # Settings section
        settings_frame = tk.LabelFrame(main_frame, text="設定", font=("Arial", 12, "bold"))
        settings_frame.grid(row=2, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        settings_frame.columnconfigure(1, weight=1)
        
        # Work time setting
        tk.Label(settings_frame, text="ワーク時間:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.work_time_var = tk.IntVar(value=self.settings.get_work_time())
        work_time_combo = ttk.Combobox(settings_frame, textvariable=self.work_time_var, 
                                      values=self.settings.WORK_TIME_OPTIONS, state="readonly", width=10)
        work_time_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        work_time_combo.bind('<<ComboboxSelected>>', self._update_work_time)
        
        tk.Label(settings_frame, text="分").grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # Break time setting
        tk.Label(settings_frame, text="休憩時間:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.break_time_var = tk.IntVar(value=self.settings.get_break_time())
        break_time_combo = ttk.Combobox(settings_frame, textvariable=self.break_time_var,
                                       values=self.settings.BREAK_TIME_OPTIONS, state="readonly", width=10)
        break_time_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        break_time_combo.bind('<<ComboboxSelected>>', self._update_break_time)
        
        tk.Label(settings_frame, text="分").grid(row=1, column=2, sticky=tk.W, pady=5)
        
        # Theme setting
        tk.Label(settings_frame, text="テーマ:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.theme_var = tk.StringVar(value=self.settings.get_theme())
        theme_combo = ttk.Combobox(settings_frame, textvariable=self.theme_var,
                                  values=['light', 'dark', 'focus'], state="readonly", width=10)
        theme_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        theme_combo.bind('<<ComboboxSelected>>', self._update_theme)
        
        # Sound settings
        sound_frame = tk.LabelFrame(settings_frame, text="サウンド設定")
        sound_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=10)
        
        self.sound_start_var = tk.BooleanVar(value=self.settings.get_sound_setting('start'))
        tk.Checkbutton(sound_frame, text="開始音", variable=self.sound_start_var,
                      command=self._update_sound_start).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.sound_end_var = tk.BooleanVar(value=self.settings.get_sound_setting('end'))
        tk.Checkbutton(sound_frame, text="終了音", variable=self.sound_end_var,
                      command=self._update_sound_end).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.sound_tick_var = tk.BooleanVar(value=self.settings.get_sound_setting('tick'))
        tk.Checkbutton(sound_frame, text="刻み音", variable=self.sound_tick_var,
                      command=self._update_sound_tick).grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Statistics
        stats_frame = tk.LabelFrame(main_frame, text="統計", font=("Arial", 12, "bold"))
        stats_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.completed_sessions_label = tk.Label(stats_frame, text="完了セッション: 0", font=("Arial", 11))
        self.completed_sessions_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Store references to themed widgets
        self.themed_widgets = [
            self.root, timer_frame, self.session_label, self.time_label, self.status_label,
            button_frame, self.start_work_btn, self.start_break_btn, self.pause_btn, self.stop_btn,
            settings_frame, sound_frame, stats_frame, self.completed_sessions_label
        ]
    
    def _apply_theme(self):
        """Apply the current theme colors to all widgets."""
        current_theme = self.settings.get_theme()
        colors = self.themes[current_theme]
        
        # Apply to all themed widgets
        for widget in self.themed_widgets:
            if isinstance(widget, (tk.Tk, tk.Frame, tk.LabelFrame)):
                widget.configure(bg=colors['bg'])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=colors['timer_bg'] if 'timer' in str(widget) else colors['bg'], 
                               fg=colors['fg'])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=colors['button_bg'], fg=colors['button_fg'],
                               activebackground=colors['accent'])
    
    def _start_gui_update_loop(self):
        """Start the GUI update loop."""
        self._update_gui()
        self.root.after(1000, self._start_gui_update_loop)  # Update every second
    
    def _update_gui(self):
        """Update GUI elements."""
        session_info = self.timer.get_session_info()
        self.completed_sessions_label.configure(text=f"完了セッション: {session_info['completed_sessions']}")
    
    # Timer control methods
    def _start_work(self):
        """Start work session."""
        self.timer.start_work_session()
    
    def _start_break(self):
        """Start break session."""
        self.timer.start_break_session()
    
    def _pause_resume(self):
        """Toggle pause/resume."""
        if self.timer.state == TimerState.RUNNING:
            self.timer.pause()
        elif self.timer.state == TimerState.PAUSED:
            self.timer.resume()
    
    def _stop(self):
        """Stop timer."""
        self.timer.stop()
    
    # Timer callbacks
    def _update_display(self, time_remaining):
        """Update timer display."""
        session_info = self.timer.get_session_info()
        
        # Update labels
        session_text = "ワークセッション" if session_info['type'] == "work" else "休憩セッション"
        self.session_label.configure(text=session_text)
        self.time_label.configure(text=session_info['formatted_time'])
        self.progress_var.set(session_info['progress_percentage'])
    
    def _on_session_complete(self, session_type):
        """Handle session completion."""
        session_text = "ワークセッション" if session_type == "work" else "休憩セッション"
        messagebox.showinfo("セッション完了", f"{session_text}が完了しました！")
    
    def _on_state_change(self, state):
        """Handle timer state changes."""
        state_text = {
            TimerState.STOPPED: "停止中",
            TimerState.RUNNING: "実行中",
            TimerState.PAUSED: "一時停止",
            TimerState.BREAK: "休憩中"
        }
        self.status_label.configure(text=state_text[state])
        
        # Update button states
        if state == TimerState.RUNNING:
            self.pause_btn.configure(text="一時停止")
        elif state == TimerState.PAUSED:
            self.pause_btn.configure(text="再開")
        else:
            self.pause_btn.configure(text="一時停止")
    
    # Settings update methods
    def _update_work_time(self, event=None):
        """Update work time setting."""
        self.settings.set_work_time(self.work_time_var.get())
    
    def _update_break_time(self, event=None):
        """Update break time setting."""
        self.settings.set_break_time(self.break_time_var.get())
    
    def _update_theme(self, event=None):
        """Update theme setting."""
        self.settings.set_theme(self.theme_var.get())
        self._apply_theme()
    
    def _update_sound_start(self):
        """Update start sound setting."""
        self.settings.set_sound_setting('start', self.sound_start_var.get())
    
    def _update_sound_end(self):
        """Update end sound setting."""
        self.settings.set_sound_setting('end', self.sound_end_var.get())
    
    def _update_sound_tick(self):
        """Update tick sound setting."""
        self.settings.set_sound_setting('tick', self.sound_tick_var.get())
    
    def run(self):
        """Run the application."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle application closing."""
        self.timer.stop()
        self.root.destroy()


if __name__ == "__main__":
    app = PomodoroApp()
    app.run()