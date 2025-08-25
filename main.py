#!/usr/bin/env python3
"""
Pomodoro Timer with Visual Feedback
ポモドーロタイマーの視覚的フィードバック強化版

Features:
- 円形プログレスバーのアニメーション
- 残り時間に応じた色変化（青→黄→赤）
- 集中時間中の背景エフェクト（パーティクルアニメーション）
"""

import http.server
import socketserver
import threading
import time
import json
import urllib.parse
from datetime import datetime
import webbrowser
import os


class PomodoroTimerServer:
    """ポモドーロタイマーWebサーバー"""
    
    def __init__(self, port=8000):
        self.port = port
        self.work_duration = 25 * 60  # 25分
        self.break_duration = 5 * 60  # 5分
        self.long_break_duration = 15 * 60  # 15分
        
        # 現在の状態
        self.current_time = self.work_duration
        self.total_time = self.work_duration
        self.is_running = False
        self.is_work_time = True
        self.session_count = 0
        self.start_time = None
        
    def get_html_page(self):
        """HTMLページを生成"""
        return '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pomodoro Timer - ポモドーロタイマー</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        
        .container {
            text-align: center;
            position: relative;
            z-index: 10;
        }
        
        .title {
            font-size: 2.5rem;
            margin-bottom: 30px;
            font-weight: 300;
            color: #ffffff;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .timer-container {
            position: relative;
            width: 400px;
            height: 400px;
            margin: 0 auto 30px;
        }
        
        .progress-ring {
            transform: rotate(-90deg);
        }
        
        .progress-background {
            stroke: #333;
            stroke-width: 12;
            fill: none;
        }
        
        .progress-bar {
            stroke: #2196F3;
            stroke-width: 12;
            fill: none;
            stroke-linecap: round;
            transition: stroke-dasharray 0.3s ease, stroke 0.3s ease;
        }
        
        .time-display {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3.5rem;
            font-weight: 300;
            color: white;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        
        .status {
            font-size: 1.5rem;
            margin-bottom: 30px;
            opacity: 0.8;
        }
        
        .controls {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .btn {
            padding: 15px 30px;
            font-size: 1.1rem;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        
        .btn-start {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        
        .btn-pause {
            background: linear-gradient(45deg, #FF9800, #f57c00);
            color: white;
        }
        
        .btn-reset {
            background: linear-gradient(45deg, #f44336, #d32f2f);
            color: white;
        }
        
        .session-count {
            font-size: 1rem;
            opacity: 0.7;
        }
        
        /* パーティクルアニメーション */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        
        .particle {
            position: absolute;
            background: radial-gradient(circle, rgba(33, 150, 243, 0.8) 0%, rgba(33, 150, 243, 0) 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        
        /* 波紋エフェクト */
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0) 70%);
            pointer-events: none;
            animation: ripple-animation 4s linear infinite;
        }
        
        @keyframes ripple-animation {
            0% {
                transform: scale(0);
                opacity: 1;
            }
            100% {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        /* 色の変化 */
        .focus-time {
            --primary-color: #4CAF50;
        }
        
        .break-time {
            --primary-color: #FF9800;
        }
        
        .long-break-time {
            --primary-color: #9C27B0;
        }
        
        /* レスポンシブデザイン */
        @media (max-width: 768px) {
            .timer-container {
                width: 300px;
                height: 300px;
            }
            .time-display {
                font-size: 2.5rem;
            }
            .title {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="particles" id="particles"></div>
    
    <div class="container">
        <h1 class="title">Pomodoro Timer</h1>
        
        <div class="timer-container">
            <svg width="400" height="400" class="progress-ring">
                <circle cx="200" cy="200" r="180" class="progress-background"></circle>
                <circle cx="200" cy="200" r="180" class="progress-bar" id="progressBar"></circle>
            </svg>
            <div class="time-display" id="timeDisplay">25:00</div>
        </div>
        
        <div class="status" id="status">集中時間 - Focus Time</div>
        
        <div class="controls">
            <button class="btn btn-start" id="startBtn" onclick="toggleTimer()">開始 / Start</button>
            <button class="btn btn-reset" onclick="resetTimer()">リセット / Reset</button>
        </div>
        
        <div class="session-count" id="sessionCount">Session: 0</div>
    </div>

    <script>
        let timerState = {
            currentTime: 1500, // 25分 = 1500秒
            totalTime: 1500,
            isRunning: false,
            isWorkTime: true,
            sessionCount: 0
        };
        
        let particles = [];
        let animationId;
        let lastTime = 0;
        
        // DOM要素
        const timeDisplay = document.getElementById('timeDisplay');
        const status = document.getElementById('status');
        const startBtn = document.getElementById('startBtn');
        const progressBar = document.getElementById('progressBar');
        const sessionCount = document.getElementById('sessionCount');
        const particlesContainer = document.getElementById('particles');
        
        // 円周の計算
        const radius = 180;
        const circumference = 2 * Math.PI * radius;
        progressBar.style.strokeDasharray = circumference;
        
        // パーティクルクラス
        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 60;
                this.vy = Math.random() * -80 - 20;
                this.life = Math.random() * 3 + 2;
                this.maxLife = this.life;
                this.size = Math.random() * 4 + 2;
                this.element = document.createElement('div');
                this.element.className = 'particle';
                this.element.style.width = this.size + 'px';
                this.element.style.height = this.size + 'px';
                particlesContainer.appendChild(this.element);
            }
            
            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.life -= dt;
                
                const alpha = this.life / this.maxLife;
                this.element.style.left = this.x + 'px';
                this.element.style.top = this.y + 'px';
                this.element.style.opacity = alpha;
                
                return this.life > 0;
            }
            
            destroy() {
                particlesContainer.removeChild(this.element);
            }
        }
        
        // 時間フォーマット
        function formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        // 進行度に応じた色を取得
        function getProgressColor(progress) {
            if (progress > 0.66) {
                return '#2196F3'; // 青
            } else if (progress > 0.33) {
                // 青から黄色へ
                const ratio = (progress - 0.33) / 0.33;
                const r = Math.floor(33 + (255 - 33) * (1 - ratio));
                const g = Math.floor(150 + (255 - 150) * (1 - ratio));
                const b = Math.floor(243 * ratio);
                return `rgb(${r}, ${g}, ${b})`;
            } else {
                // 黄色から赤へ
                const ratio = progress / 0.33;
                const r = 255;
                const g = Math.floor(255 * ratio);
                const b = 0;
                return `rgb(${r}, ${g}, ${b})`;
            }
        }
        
        // UI更新
        function updateUI() {
            timeDisplay.textContent = formatTime(Math.max(0, Math.floor(timerState.currentTime)));
            
            const progress = timerState.currentTime / timerState.totalTime;
            const strokeDashoffset = circumference * (1 - progress);
            progressBar.style.strokeDashoffset = strokeDashoffset;
            progressBar.style.stroke = getProgressColor(progress);
            
            sessionCount.textContent = `Session: ${timerState.sessionCount}`;
        }
        
        // パーティクル作成
        function createParticle() {
            if (timerState.isRunning && timerState.isWorkTime && Math.random() < 0.05) {
                const x = Math.random() * window.innerWidth;
                const y = window.innerHeight + 10;
                particles.push(new Particle(x, y));
            }
        }
        
        // パーティクル更新
        function updateParticles(dt) {
            createParticle();
            
            particles = particles.filter(particle => {
                if (particle.update(dt)) {
                    return true;
                } else {
                    particle.destroy();
                    return false;
                }
            });
        }
        
        // メインアニメーションループ
        function animate(currentTime) {
            const dt = (currentTime - lastTime) / 1000;
            lastTime = currentTime;
            
            if (timerState.isRunning) {
                timerState.currentTime -= dt;
                if (timerState.currentTime <= 0) {
                    timerFinished();
                }
            }
            
            updateParticles(dt);
            updateUI();
            
            animationId = requestAnimationFrame(animate);
        }
        
        // タイマー開始/停止
        function toggleTimer() {
            timerState.isRunning = !timerState.isRunning;
            
            if (timerState.isRunning) {
                startBtn.textContent = '一時停止 / Pause';
                startBtn.className = 'btn btn-pause';
            } else {
                startBtn.textContent = '開始 / Start';
                startBtn.className = 'btn btn-start';
            }
        }
        
        // タイマーリセット
        function resetTimer() {
            timerState.isRunning = false;
            timerState.currentTime = timerState.totalTime;
            
            startBtn.textContent = '開始 / Start';
            startBtn.className = 'btn btn-start';
            
            // パーティクルをクリア
            particles.forEach(particle => particle.destroy());
            particles = [];
            
            updateUI();
        }
        
        // タイマー終了
        function timerFinished() {
            timerState.isRunning = false;
            
            if (timerState.isWorkTime) {
                timerState.sessionCount++;
                
                if (timerState.sessionCount % 4 === 0) {
                    // 長い休憩
                    timerState.currentTime = 900; // 15分
                    timerState.totalTime = 900;
                    status.textContent = '長い休憩 - Long Break';
                    status.style.color = '#9C27B0';
                } else {
                    // 短い休憩
                    timerState.currentTime = 300; // 5分
                    timerState.totalTime = 300;
                    status.textContent = '休憩時間 - Break Time';
                    status.style.color = '#FF9800';
                }
                timerState.isWorkTime = false;
            } else {
                // 作業時間
                timerState.currentTime = 1500; // 25分
                timerState.totalTime = 1500;
                timerState.isWorkTime = true;
                status.textContent = '集中時間 - Focus Time';
                status.style.color = '#4CAF50';
            }
            
            startBtn.textContent = '開始 / Start';
            startBtn.className = 'btn btn-start';
            
            // 通知音
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAcBzyJz/LNeCsFJYHM8tyMOQgZZ7nr6KJSDQxUnOLztG');
        }
        
        // 初期化
        function init() {
            updateUI();
            lastTime = performance.now();
            animate(lastTime);
            
            // 波紋エフェクトを追加
            setInterval(() => {
                if (timerState.isRunning && timerState.isWorkTime) {
                    const ripple = document.createElement('div');
                    ripple.className = 'ripple';
                    ripple.style.width = '100px';
                    ripple.style.height = '100px';
                    ripple.style.left = (Math.random() * window.innerWidth - 50) + 'px';
                    ripple.style.top = (Math.random() * window.innerHeight - 50) + 'px';
                    document.body.appendChild(ripple);
                    
                    setTimeout(() => {
                        document.body.removeChild(ripple);
                    }, 4000);
                }
            }, 2000);
        }
        
        // ページ読み込み時に初期化
        window.addEventListener('load', init);
    </script>
</body>
</html>'''
    
    def create_handler(self):
        """HTTPハンドラーを作成"""
        timer_server = self
        
        class PomodoroHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(timer_server.get_html_page().encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
                    
            def log_message(self, format, *args):
                # ログを無効化
                pass
                
        return PomodoroHandler
    
    def run(self):
        """サーバーを起動"""
        handler = self.create_handler()
        
        try:
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                print(f"ポモドーロタイマーサーバーを起動しました")
                print(f"ブラウザで http://localhost:{self.port} にアクセスしてください")
                print("サーバーを停止するには Ctrl+C を押してください")
                
                # ブラウザを自動で開く（可能な場合）
                try:
                    webbrowser.open(f'http://localhost:{self.port}')
                except:
                    pass
                
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nサーバーを停止しました")
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"ポート {self.port} は既に使用されています。別のポートを試してください。")
                self.port += 1
                self.run()
            else:
                raise


if __name__ == "__main__":
    server = PomodoroTimerServer()
    server.run()
