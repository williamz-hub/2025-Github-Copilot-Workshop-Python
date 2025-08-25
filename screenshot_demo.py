#!/usr/bin/env python3
"""
ポモドーロタイマー ゲーミフィケーション機能 スクリーンショット用デモ
"""

import os
from pomodoro_timer import PomodoroTimer


def create_demo_screenshots():
    """スクリーンショット用のデモデータ作成"""
    
    # クリーンスタート
    if os.path.exists("pomodoro_stats.json"):
        os.remove("pomodoro_stats.json")
    
    timer = PomodoroTimer()
    
    # 複数回のポモドーロを完了してデモデータ作成
    for i in range(15):
        timer._complete_pomodoro()
    
    # 連続3日のシミュレーション
    from datetime import date, timedelta
    today = date.today()
    for i in range(3):
        day = (today - timedelta(days=2-i)).isoformat()
        timer.user_stats.daily_sessions[day] = 3 + i
    
    timer.user_stats.current_streak = 3
    timer.user_stats.longest_streak = 5
    timer._check_achievements()
    timer._save_stats()
    
    print("✅ デモデータを作成しました")
    
    # 統計表示
    print("\n🍅" * 25)
    print("   ポモドーロタイマー with ゲーミフィケーション")
    print("🍅" * 25)
    print()
    
    stats = timer.get_stats_summary()
    print("📊 統計情報")
    print(f"レベル: {stats['level']} (XP: {stats['experience']}/{stats['next_level_xp']})")
    
    # XPバー
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
    
    print("🏆 実績一覧")
    for achievement in timer.user_stats.achievements:
        status = "✅" if achievement.unlocked else "🔒"
        print(f"{status} {achievement.name}: {achievement.description}")
    print()
    
    print("📈 週間統計")
    days = ["月", "火", "水", "木", "金", "土", "日"]
    week_start = today - timedelta(days=today.weekday())
    
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_sessions = timer.user_stats.daily_sessions.get(day_date.isoformat(), 0)
        bar = "█" * min(day_sessions, 10)
        print(f"{days[i]} {day_date.strftime('%m/%d')}: {bar} ({day_sessions}回)")
    print()
    
    print("🎮 実装されたゲーミフィケーション機能:")
    print("✅ 経験値（XP）とレベルアップ機能（ポモドーロ完了ごとにXP付与）")
    print("✅ 達成バッジ／実績システム（3日連続、週間10回など）")
    print("✅ 週間・月間統計の詳細グラフ表示（完了率、平均集中時間など）")
    print("✅ ストリーク表示（連続日数のカウント）")
    print("✅ データ永続化とユーザー進捗保存")
    print()
    print("🚀 実行方法:")
    print("  python3 main.py        # フル機能のUIで起動")
    print("  python3 demo_gamification.py  # 基本デモ")
    print("  python3 test_pomodoro.py      # テスト実行")


if __name__ == "__main__":
    create_demo_screenshots()