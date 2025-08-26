let timer = 1500;
let initialTimer = 1500;
let interval = null;
const timerDisplay = document.getElementById('timer');
const startBtn = document.getElementById('start');
const resetBtn = document.getElementById('reset');
const progressCircle = document.querySelector('.progress-ring-circle');

// 背景エフェクト用のキャンバス設定
const canvas = document.getElementById('background-canvas');
const ctx = canvas.getContext('2d');
let particles = [];

// キャンバスサイズ設定
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

// パーティクルクラス
class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 3 + 1;
        this.speedX = (Math.random() - 0.5) * 0.5;
        this.speedY = (Math.random() - 0.5) * 0.5;
        this.opacity = Math.random() * 0.5 + 0.2;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
        if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
    }

    draw() {
        ctx.save();
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = getCurrentThemeColor();
        ctx.fill();
        ctx.restore();
    }
}

// 現在のテーマ色を取得
function getCurrentThemeColor() {
    const progress = (initialTimer - timer) / initialTimer;
    
    if (progress < 0.5) {
        return '#4285f4'; // 青
    } else if (progress < 0.8) {
        return '#fbbc04'; // 黄
    } else {
        return '#ea4335'; // 赤
    }
}

// パーティクルシステム初期化
function initParticles() {
    particles = [];
    for (let i = 0; i < 50; i++) {
        particles.push(new Particle());
    }
}

// アニメーションループ
function animateBackground() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });

    // パーティクル間の線を描画
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
                ctx.beginPath();
                ctx.strokeStyle = getCurrentThemeColor();
                ctx.globalAlpha = (100 - distance) / 100 * 0.2;
                ctx.lineWidth = 0.5;
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }

    requestAnimationFrame(animateBackground);
}

// プログレスバーの更新
function updateProgressBar() {
    const progress = (initialTimer - timer) / initialTimer;
    const circumference = 2 * Math.PI * 120; // r=120の円周
    const strokeDashoffset = circumference - (progress * circumference);
    
    progressCircle.style.strokeDashoffset = strokeDashoffset;
    
    // 色の変化
    progressCircle.classList.remove('progress-warning', 'progress-danger');
    if (progress >= 0.8) {
        progressCircle.classList.add('progress-danger');
        timerDisplay.classList.add('timer-urgent');
    } else if (progress >= 0.5) {
        progressCircle.classList.add('progress-warning');
        timerDisplay.classList.remove('timer-urgent');
    } else {
        timerDisplay.classList.remove('timer-urgent');
    }
}

// 時間表示の更新
function updateDisplay() {
    const min = String(Math.floor(timer / 60)).padStart(2, '0');
    const sec = String(timer % 60).padStart(2, '0');
    timerDisplay.textContent = `${min}:${sec}`;
    updateProgressBar();
}

// 完了アニメーション
function triggerCompletionAnimation() {
    const container = document.querySelector('.timer-container');
    container.classList.add('completed');
    
    setTimeout(() => {
        container.classList.remove('completed');
    }, 1000);
}

// タイマー開始
startBtn.onclick = function() {
    if (interval) return;
    
    startBtn.textContent = '実行中...';
    startBtn.disabled = true;
    
    interval = setInterval(() => {
        if (timer > 0) {
            timer--;
            updateDisplay();
        } else {
            clearInterval(interval);
            interval = null;
            startBtn.textContent = '開始';
            startBtn.disabled = false;
            triggerCompletionAnimation();
            
            // 完了通知
            if (Notification.permission === 'granted') {
                new Notification('ポモドーロ完了！', {
                    body: '25分間お疲れ様でした！',
                    icon: '/static/favicon.ico'
                });
            }
        }
    }, 1000);
};

// タイマーリセット
resetBtn.onclick = function() {
    clearInterval(interval);
    interval = null;
    timer = initialTimer;
    startBtn.textContent = '開始';
    startBtn.disabled = false;
    timerDisplay.classList.remove('timer-urgent');
    updateDisplay();
};

// 初期化
window.addEventListener('resize', resizeCanvas);
document.addEventListener('DOMContentLoaded', () => {
    resizeCanvas();
    initParticles();
    animateBackground();
    updateDisplay();
    
    // 通知許可の要求
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});
