#!/usr/bin/env python3
"""
高度なゲーミフィケーション機能テスト - より多くの実績解除
"""

import os
from datetime import date, timedelta
from pomodoro_timer import PomodoroTimer


def advanced_test():
    """高度なテスト - より多くの実績を解除"""
    print("🚀 高度なゲーミフィケーション機能テスト")
    print("=" * 50)
    
    # クリーンスタート
    if os.path.exists("pomodoro_stats.json"):
        os.remove("pomodoro_stats.json")
    
    timer = PomodoroTimer()
    
    # 週間10回実績を解除するため
    print("📅 週間10回実績のテスト...")
    for i in range(10):
        timer._complete_pomodoro()
        if i % 3 == 2:  # 3回ごとに統計表示
            stats = timer.get_stats_summary()
            print(f"  {i+1}回完了 - レベル: {stats['level']}, 今週: {stats['weekly_sessions']}回")
    
    print("\n🎯 レベル5実績のテスト...")
    # レベル5に到達するまで（500XP × 4 = 2000XP必要、つまり20回）
    while timer.user_stats.level < 5:
        timer._complete_pomodoro()
        if timer.user_stats.level > 1:  # レベルアップ時のみ表示
            break
    
    print(f"現在レベル: {timer.user_stats.level}")
    
    # 3日連続のシミュレーション（日付を手動で設定）
    print("\n📆 連続日数実績のテスト...")
    today = date.today()
    
    # 過去3日間のデータを設定
    for i in range(3):
        day = (today - timedelta(days=2-i)).isoformat()
        timer.user_stats.daily_sessions[day] = 1
    
    # ストリークを手動で設定
    timer.user_stats.current_streak = 3
    timer.user_stats.last_session_date = today.isoformat()
    
    # 実績チェック実行
    timer._check_achievements()
    
    print("\n🏆 解除された実績:")
    unlocked = [a for a in timer.user_stats.achievements if a.unlocked]
    for ach in unlocked:
        print(f"✅ {ach.name}")
    
    print(f"\n📊 最終統計:")
    stats = timer.get_stats_summary()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 統計保存
    timer._save_stats()
    print("\n💾 統計が保存されました")


if __name__ == "__main__":
    advanced_test()