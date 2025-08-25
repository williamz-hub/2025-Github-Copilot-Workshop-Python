#!/usr/bin/env python3
"""
ポモドーロタイマー ゲーミフィケーション機能デモンストレーション
"""

import time
import os
from pomodoro_timer import PomodoroTimer


def demo_gamification():
    """ゲーミフィケーション機能のデモ"""
    print("🍅" * 30)
    print("  ポモドーロタイマー ゲーミフィケーション機能デモ")
    print("🍅" * 30)
    print()
    
    # 既存の統計ファイルを削除してクリーンスタート
    if os.path.exists("pomodoro_stats.json"):
        os.remove("pomodoro_stats.json")
    
    # タイマー初期化
    timer = PomodoroTimer(work_duration=25*60, break_duration=5*60)
    
    print("📊 初期状態:")
    stats = timer.get_stats_summary()
    print(f"  レベル: {stats['level']}")
    print(f"  経験値: {stats['experience']}/{stats['next_level_xp']}")
    print(f"  総ポモドーロ: {stats['total_pomodoros']}")
    print(f"  ストリーク: {stats['current_streak']} 日")
    print(f"  実績: {stats['unlocked_achievements']}/{stats['total_achievements']}")
    print()
    
    input("Enterを押してポモドーロ完了をシミュレーション...")
    
    # 複数のポモドーロ完了をシミュレーション
    print("\n🎮 ゲーミフィケーション要素の動作確認:")
    print("=" * 50)
    
    for i in range(1, 8):
        print(f"\n--- ポモドーロ {i} 回目完了 ---")
        timer._complete_pomodoro()
        
        stats = timer.get_stats_summary()
        
        # XPバー表示
        xp_percentage = stats['experience'] / stats['next_level_xp']
        bar_length = 20
        filled_length = int(bar_length * xp_percentage)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"レベル: {stats['level']} | XP: [{bar}] {stats['experience']}/{stats['next_level_xp']}")
        print(f"総ポモドーロ: {stats['total_pomodoros']} | ストリーク: {stats['current_streak']}日")
        print(f"実績解除: {stats['unlocked_achievements']}/{stats['total_achievements']}")
        
        time.sleep(0.5)  # 視覚的な効果のための待機
    
    print("\n🏆 解除された実績一覧:")
    print("-" * 30)
    for achievement in timer.user_stats.achievements:
        if achievement.unlocked:
            print(f"✅ {achievement.name}: {achievement.description}")
    
    print("\n📈 週間統計:")
    print("-" * 20)
    from datetime import date, timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    days = ["月", "火", "水", "木", "金", "土", "日"]
    
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_sessions = timer.user_stats.daily_sessions.get(day_date.isoformat(), 0)
        bar = "█" * min(day_sessions, 10)  # 最大10文字
        print(f"{days[i]} {day_date.strftime('%m/%d')}: {bar} ({day_sessions}回)")
    
    print(f"\n📊 最終統計:")
    final_stats = timer.get_stats_summary()
    print(f"  レベル: {final_stats['level']}")
    print(f"  総ポモドーロ: {final_stats['total_pomodoros']} 回")
    print(f"  総集中時間: {final_stats['total_focus_time']}")
    print(f"  現在のストリーク: {final_stats['current_streak']} 日")
    print(f"  今週のセッション: {final_stats['weekly_sessions']} 回")
    print(f"  解除実績: {final_stats['unlocked_achievements']}/{final_stats['total_achievements']} 個")
    
    print("\n✨ デモ完了！ゲーミフィケーション機能が正常に動作しています。")
    print("実際の使用では、pomodoro_ui.py を実行してください。")


if __name__ == "__main__":
    demo_gamification()