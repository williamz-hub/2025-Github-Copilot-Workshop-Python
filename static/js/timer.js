// Timer state
let timer = 1500; // default 25 minutes
let interval = null;
let isWorkSession = true; // true for work, false for break
let settings = {
    workTime: 25,
    breakTime: 5,
    theme: 'default',
    startSound: true,
    endSound: true,
    tickSound: false
};

// DOM elements
const timerDisplay = document.getElementById('timer');
const sessionType = document.getElementById('session-type');
const startBtn = document.getElementById('start');
const resetBtn = document.getElementById('reset');
const settingsBtn = document.getElementById('settings-btn');
const settingsPanel = document.getElementById('settings-panel');
const closeSettingsBtn = document.getElementById('close-settings');

// Settings elements
const workTimeSelect = document.getElementById('work-time');
const breakTimeSelect = document.getElementById('break-time');
const themeSelect = document.getElementById('theme');
const startSoundCheck = document.getElementById('start-sound');
const endSoundCheck = document.getElementById('end-sound');
const tickSoundCheck = document.getElementById('tick-sound');

// Load settings from localStorage
function loadSettings() {
    const saved = localStorage.getItem('pomodoroSettings');
    if (saved) {
        settings = { ...settings, ...JSON.parse(saved) };
    }
    
    // Apply loaded settings to UI
    workTimeSelect.value = settings.workTime;
    breakTimeSelect.value = settings.breakTime;
    themeSelect.value = settings.theme;
    startSoundCheck.checked = settings.startSound;
    endSoundCheck.checked = settings.endSound;
    tickSoundCheck.checked = settings.tickSound;
    
    applyTheme();
    resetTimer();
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem('pomodoroSettings', JSON.stringify(settings));
}

// Apply theme
function applyTheme() {
    document.body.className = settings.theme === 'default' ? '' : `theme-${settings.theme}`;
}

// Update timer display
function updateDisplay() {
    const min = String(Math.floor(timer / 60)).padStart(2, '0');
    const sec = String(timer % 60).padStart(2, '0');
    timerDisplay.textContent = `${min}:${sec}`;
    
    // Update session type display
    sessionType.textContent = isWorkSession ? '作業時間' : '休憩時間';
}

// Play sound (basic implementation)
function playSound(type) {
    if (!settings[type + 'Sound']) return;
    
    // Create a simple beep sound using Web Audio API
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Different frequencies for different sound types
        if (type === 'start') {
            oscillator.frequency.value = 800;
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        } else if (type === 'end') {
            oscillator.frequency.value = 400;
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        } else if (type === 'tick') {
            oscillator.frequency.value = 1000;
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        }
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + (type === 'end' ? 0.5 : 0.2));
    } catch (e) {
        console.log('Audio not supported');
    }
}

// Reset timer to current session's duration
function resetTimer() {
    clearInterval(interval);
    interval = null;
    timer = isWorkSession ? settings.workTime * 60 : settings.breakTime * 60;
    updateDisplay();
    startBtn.textContent = '開始';
}

// Switch between work and break sessions
function switchSession() {
    isWorkSession = !isWorkSession;
    resetTimer();
}

// Start/pause timer
startBtn.onclick = function() {
    if (interval) {
        // Pause timer
        clearInterval(interval);
        interval = null;
        startBtn.textContent = '開始';
    } else {
        // Start timer
        playSound('start');
        startBtn.textContent = '一時停止';
        
        interval = setInterval(() => {
            if (timer > 0) {
                timer--;
                updateDisplay();
                
                // Play tick sound
                if (settings.tickSound) {
                    playSound('tick');
                }
            } else {
                // Timer finished
                clearInterval(interval);
                interval = null;
                startBtn.textContent = '開始';
                
                playSound('end');
                
                // Auto-switch to break/work session
                switchSession();
                
                // Show notification
                if (isWorkSession) {
                    alert('休憩時間が終了しました！作業時間を開始しましょう。');
                } else {
                    alert('作業時間が終了しました！休憩時間です。');
                }
            }
        }, 1000);
    }
};

// Reset timer
resetBtn.onclick = function() {
    resetTimer();
};

// Settings panel toggle
settingsBtn.onclick = function() {
    settingsPanel.classList.remove('hidden');
};

closeSettingsBtn.onclick = function() {
    settingsPanel.classList.add('hidden');
};

// Settings change handlers
workTimeSelect.onchange = function() {
    settings.workTime = parseInt(this.value);
    saveSettings();
    if (isWorkSession) resetTimer();
};

breakTimeSelect.onchange = function() {
    settings.breakTime = parseInt(this.value);
    saveSettings();
    if (!isWorkSession) resetTimer();
};

themeSelect.onchange = function() {
    settings.theme = this.value;
    saveSettings();
    applyTheme();
};

startSoundCheck.onchange = function() {
    settings.startSound = this.checked;
    saveSettings();
};

endSoundCheck.onchange = function() {
    settings.endSound = this.checked;
    saveSettings();
};

tickSoundCheck.onchange = function() {
    settings.tickSound = this.checked;
    saveSettings();
};

// Close settings panel when clicking outside
window.onclick = function(event) {
    if (event.target === settingsPanel) {
        settingsPanel.classList.add('hidden');
    }
};

// Initialize
loadSettings();
updateDisplay();
