let timer = 1500;
let interval = null;
let isRunning = false;
const timerDisplay = document.getElementById('timer');
const startBtn = document.getElementById('start');
const resetBtn = document.getElementById('reset');

// ゲーミフィケーション関連の要素
const levelDisplay = document.getElementById('level');
const experienceDisplay = document.getElementById('experience');
const totalCompletedDisplay = document.getElementById('total-completed');
const currentStreakDisplay = document.getElementById('current-streak');
const todayCompletionsDisplay = document.getElementById('today-completions');
const weekCompletionsDisplay = document.getElementById('week-completions');
const xpProgressBar = document.getElementById('xp-progress');
const xpText = document.getElementById('xp-text');
const badgesContainer = document.getElementById('badges-container');
const weekChart = document.getElementById('week-chart');
const completionNotification = document.getElementById('completion-notification');

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadWeeklyStats();
    loadBadges();
});

function updateDisplay() {
    const min = String(Math.floor(timer / 60)).padStart(2, '0');
    const sec = String(timer % 60).padStart(2, '0');
    timerDisplay.textContent = `${min}:${sec}`;
}

startBtn.onclick = function() {
    if (interval) return;
    
    isRunning = true;
    startBtn.textContent = '実行中';
    startBtn.disabled = true;
    
    interval = setInterval(() => {
        if (timer > 0) {
            timer--;
            updateDisplay();
        } else {
            clearInterval(interval);
            interval = null;
            isRunning = false;
            startBtn.textContent = '開始';
            startBtn.disabled = false;
            
            // ポモドーロ完了処理
            onPomodoroComplete();
        }
    }, 1000);
};

resetBtn.onclick = function() {
    clearInterval(interval);
    interval = null;
    isRunning = false;
    timer = 1500;
    startBtn.textContent = '開始';
    startBtn.disabled = false;
    updateDisplay();
};

// ポモドーロ完了時の処理
async function onPomodoroComplete() {
    try {
        const response = await fetch('/api/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ xp_gain: 100 })
        });
        
        if (response.ok) {
            const result = await response.json();
            showCompletionNotification(result);
            
            // 統計情報を更新
            await loadStats();
            await loadWeeklyStats();
            await loadBadges();
        } else {
            console.error('Failed to complete pomodoro');
        }
    } catch (error) {
        console.error('Error completing pomodoro:', error);
    }
    
    // タイマーをリセット
    timer = 1500;
    updateDisplay();
}

// 統計情報の読み込み
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        if (response.ok) {
            const stats = await response.json();
            updateStatsDisplay(stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// 週間統計の読み込み
async function loadWeeklyStats() {
    try {
        const response = await fetch('/api/stats/weekly');
        if (response.ok) {
            const weeklyStats = await response.json();
            updateWeeklyDisplay(weeklyStats);
        }
    } catch (error) {
        console.error('Error loading weekly stats:', error);
    }
}

// バッジ情報の読み込み
async function loadBadges() {
    try {
        const response = await fetch('/api/badges');
        if (response.ok) {
            const badgesInfo = await response.json();
            updateBadgesDisplay(badgesInfo);
        }
    } catch (error) {
        console.error('Error loading badges:', error);
    }
}

// 統計表示の更新
function updateStatsDisplay(stats) {
    levelDisplay.textContent = stats.level;
    experienceDisplay.textContent = stats.experience;
    totalCompletedDisplay.textContent = stats.total_completed;
    currentStreakDisplay.textContent = stats.current_streak;
    todayCompletionsDisplay.textContent = stats.today_completions;
    
    // XPプログレスバーの更新
    const progressPercentage = (stats.xp_progress / (stats.xp_progress + stats.xp_to_next_level)) * 100;
    xpProgressBar.style.width = `${progressPercentage}%`;
    xpText.textContent = `${stats.xp_progress} / ${stats.xp_progress + stats.xp_to_next_level} XP`;
}

// 週間統計表示の更新
function updateWeeklyDisplay(weeklyStats) {
    weekCompletionsDisplay.textContent = weeklyStats.week_completions;
    
    // 週間チャートの更新
    weekChart.innerHTML = '';
    const maxCount = Math.max(...weeklyStats.daily_breakdown.map(d => d.count), 1);
    
    weeklyStats.daily_breakdown.forEach(day => {
        const dayBar = document.createElement('div');
        dayBar.className = 'day-bar';
        
        const dayCount = document.createElement('div');
        dayCount.className = 'day-count';
        dayCount.textContent = day.count;
        
        const dayBarFill = document.createElement('div');
        dayBarFill.className = 'day-bar-fill';
        const height = (day.count / maxCount) * 80;
        dayBarFill.style.height = `${height}px`;
        
        const dayLabel = document.createElement('div');
        dayLabel.className = 'day-label';
        const dayNames = ['月', '火', '水', '木', '金', '土', '日'];
        const date = new Date(day.date);
        dayLabel.textContent = dayNames[date.getDay()];
        
        dayBar.appendChild(dayCount);
        dayBar.appendChild(dayBarFill);
        dayBar.appendChild(dayLabel);
        weekChart.appendChild(dayBar);
    });
}

// バッジ表示の更新
function updateBadgesDisplay(badgesInfo) {
    badgesContainer.innerHTML = '';
    
    if (badgesInfo.earned.length === 0) {
        badgesContainer.innerHTML = '<p style="text-align: center; color: #666;">まだバッジがありません</p>';
        return;
    }
    
    badgesInfo.earned.forEach(badgeId => {
        const badgeInfo = badgesInfo.available[badgeId];
        if (badgeInfo) {
            const badge = document.createElement('div');
            badge.className = 'badge';
            badge.title = badgeInfo.description;
            badge.textContent = badgeInfo.name;
            badgesContainer.appendChild(badge);
        }
    });
}

// 完了通知の表示
function showCompletionNotification(result) {
    const message = document.getElementById('completion-message');
    const achievementList = document.getElementById('achievement-list');
    
    let messageText = `+${result.xp_gained} XP 獲得！`;
    if (result.level_up) {
        messageText += ` レベル ${result.new_level} にアップ！`;
    }
    message.textContent = messageText;
    
    // 新しいバッジがある場合
    achievementList.innerHTML = '';
    if (result.new_badges && result.new_badges.length > 0) {
        const badgesTitle = document.createElement('p');
        badgesTitle.textContent = '新しいバッジを獲得:';
        badgesTitle.style.fontWeight = 'bold';
        achievementList.appendChild(badgesTitle);
        
        result.new_badges.forEach(badgeId => {
            const achievement = document.createElement('div');
            achievement.className = 'achievement-item';
            achievement.textContent = getBadgeName(badgeId);
            achievementList.appendChild(achievement);
        });
    }
    
    // ストリーク情報
    if (result.current_streak > 1) {
        const streakInfo = document.createElement('p');
        streakInfo.textContent = `${result.current_streak}日連続！`;
        streakInfo.style.color = '#7b6fdc';
        streakInfo.style.fontWeight = 'bold';
        achievementList.appendChild(streakInfo);
    }
    
    completionNotification.style.display = 'flex';
}

// 通知を閉じる
function closeNotification() {
    completionNotification.style.display = 'none';
}

// バッジ名の取得（ヘルパー関数）
function getBadgeName(badgeId) {
    const badgeNames = {
        'first_completion': '初回完了',
        'five_completions': '5回完了',
        'ten_completions': '10回完了',
        'twenty_five_completions': '25回完了',
        'fifty_completions': '50回完了',
        'hundred_completions': '100回完了',
        'three_day_streak': '3日連続',
        'week_streak': '1週間連続',
        'two_week_streak': '2週間連続',
        'month_streak': '1ヶ月連続',
        'level_five': 'レベル5到達',
        'level_ten': 'レベル10到達',
        'level_twenty': 'レベル20到達'
    };
    return badgeNames[badgeId] || badgeId;
}

// 初期表示更新
updateDisplay();
