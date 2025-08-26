#!/usr/bin/env python3
"""
ポモドーロタイマー with ゲーミフィケーション
コンソールベースのシンプルなUI
"""

import time
import os
import sys
from pomodoro_timer import PomodoroTimer, TimerState


class PomodoroUI:
    """ポモドーロタイマーのコンソールUI"""
    
    def __init__(self):
        self.timer = PomodoroTimer()
        self.running = True
    
    def clear_screen(self):
        """画面クリア"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """ヘッダー表示"""
        print("🍅" * 20)
        print("   ポモドーロタイマー with ゲーミフィケーション")
        print("🍅" * 20)
        print()
    
    def display_timer(self):
        """タイマー表示"""
        status_emoji = {
            TimerState.STOPPED: "⏹️",
            TimerState.RUNNING: "▶️",
            TimerState.PAUSED: "⏸️",
            TimerState.BREAK: "☕"
        }
        
        mode = "作業時間" if self.timer.current_duration == self.timer.work_duration else "休憩時間"
        
        print(f"{status_emoji[self.timer.state]} {mode}")
        print(f"残り時間: {self.timer.get_remaining_time_formatted()}")
        print()
    
    def display_stats(self):
        """統計表示"""
        stats = self.timer.get_stats_summary()
        
        print("📊 統計情報")
        print(f"レベル: {stats['level']} (XP: {stats['experience']}/{stats['next_level_xp']})")
        
        # XPバーの表示
        xp_percentage = stats['experience'] / stats['next_level_xp']
        bar_length = 20
        filled_length = int(bar_length * xp_percentage)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"XP: [{bar}] {int(xp_percentage * 100)}%")
        
        print(f"総ポモドーロ: {stats['total_pomodoros']} 回")
        print(f"総集中時間: {stats['total_focus_time']}")
        print(f"現在のストリーク: {stats['current_streak']} 日")
        print(f"最長ストリーク: {stats['longest_streak']} 日")
        print(f"今週のセッション: {stats['weekly_sessions']} 回")
        print(f"実績: {stats['unlocked_achievements']}/{stats['total_achievements']} 個解除")
        print()
    
    def display_achievements(self):
        """実績表示"""
        print("🏆 実績一覧")
        unlocked_count = 0
        for achievement in self.timer.user_stats.achievements:
            status = "✅" if achievement.unlocked else "🔒"
            print(f"{status} {achievement.name}: {achievement.description}")
            if achievement.unlocked:
                unlocked_count += 1
        
        if unlocked_count == 0:
            print("まだ実績が解除されていません。ポモドーロを完了して実績を獲得しましょう！")
        print()
    
    def display_weekly_stats(self):
        """週間統計表示"""
        print("📈 週間統計")
        from datetime import date, timedelta
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        days = ["月", "火", "水", "木", "金", "土", "日"]
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_sessions = self.timer.user_stats.daily_sessions.get(day_date.isoformat(), 0)
            bar = "█" * day_sessions if day_sessions > 0 else "░"
            print(f"{days[i]} {day_date.strftime('%m/%d')}: {bar} ({day_sessions}回)")
        print()
    
    def display_menu(self):
        """メニュー表示"""
        print("操作メニュー:")
        if self.timer.state == TimerState.STOPPED:
            print("1. タイマー開始")
        elif self.timer.state == TimerState.RUNNING:
            print("2. タイマー一時停止")
        elif self.timer.state == TimerState.PAUSED:
            print("1. タイマー再開")
        
        if self.timer.state != TimerState.STOPPED:
            print("3. タイマー停止")
        
        print("4. 実績確認")
        print("5. 週間統計")
        print("6. 統計リセット")
        print("0. 終了")
        print()
    
    def handle_input(self):
        """ユーザー入力処理"""
        try:
            choice = input("選択してください: ").strip()
            
            if choice == "1":
                if self.timer.state in [TimerState.STOPPED, TimerState.PAUSED]:
                    self.timer.start_timer()
            elif choice == "2" and self.timer.state == TimerState.RUNNING:
                self.timer.pause_timer()
            elif choice == "3" and self.timer.state != TimerState.STOPPED:
                self.timer.stop_timer()
            elif choice == "4":
                self.show_achievements_screen()
            elif choice == "5":
                self.show_weekly_stats_screen()
            elif choice == "6":
                self.reset_stats()
            elif choice == "0":
                self.running = False
                print("ポモドーロタイマーを終了します。お疲れ様でした！")
        except KeyboardInterrupt:
            self.running = False
            print("\nポモドーロタイマーを終了します。")
    
    def show_achievements_screen(self):
        """実績画面表示"""
        self.clear_screen()
        self.display_header()
        self.display_achievements()
        input("Enterキーで戻る...")
    
    def show_weekly_stats_screen(self):
        """週間統計画面表示"""
        self.clear_screen()
        self.display_header()
        self.display_weekly_stats()
        input("Enterキーで戻る...")
    
    def reset_stats(self):
        """統計リセット"""
        confirm = input("統計をリセットしますか？ (y/N): ").strip().lower()
        if confirm == 'y':
            if os.path.exists(self.timer.stats_file):
                os.remove(self.timer.stats_file)
            self.timer = PomodoroTimer()  # 新しいインスタンスを作成
            print("統計をリセットしました。")
            time.sleep(1)
    
    def run(self):
        """メインループ"""
        print("ポモドーロタイマーを開始します...")
        time.sleep(1)
        
        while self.running:
            # タイマー更新
            self.timer.update()
            
            # 画面更新
            self.clear_screen()
            self.display_header()
            self.display_timer()
            self.display_stats()
            self.display_menu()
            
            # ユーザー入力処理（タイムアウト付き）
            if self.timer.state == TimerState.RUNNING:
                print("(タイマー動作中 - 1秒後に自動更新)")
                # 実際のアプリケーションでは非同期入力処理が必要
                time.sleep(1)
            else:
                self.handle_input()


def main():
    """メイン関数"""
    try:
        ui = PomodoroUI()
        ui.run()
    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()