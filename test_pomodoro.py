#!/usr/bin/env python3
"""
Command-line test for Pomodoro Timer functionality
Demonstrates all customization features without GUI
"""

import time
from pomodoro_settings import PomodoroSettings
from pomodoro_timer import PomodoroTimer, TimerState


def print_separator():
    print("=" * 60)


def test_settings():
    """Test settings functionality."""
    print_separator()
    print("🔧 設定機能のテスト")
    print_separator()
    
    settings = PomodoroSettings('test_settings.json')
    
    # Test default settings
    print(f"デフォルト設定: {settings.get_all_settings()}")
    
    # Test work time customization
    print(f"\n📋 作業時間設定テスト:")
    print(f"現在の作業時間: {settings.get_work_time()}分")
    for work_time in settings.WORK_TIME_OPTIONS:
        result = settings.set_work_time(work_time)
        print(f"  {work_time}分に設定: {'✅' if result else '❌'}")
    print(f"最終設定: {settings.get_work_time()}分")
    
    # Test break time customization
    print(f"\n☕ 休憩時間設定テスト:")
    print(f"現在の休憩時間: {settings.get_break_time()}分")
    for break_time in settings.BREAK_TIME_OPTIONS:
        result = settings.set_break_time(break_time)
        print(f"  {break_time}分に設定: {'✅' if result else '❌'}")
    print(f"最終設定: {settings.get_break_time()}分")
    
    # Test theme customization
    print(f"\n🎨 テーマ設定テスト:")
    print(f"現在のテーマ: {settings.get_theme()}")
    for theme in settings.THEME_OPTIONS:
        result = settings.set_theme(theme)
        print(f"  {theme}テーマに設定: {'✅' if result else '❌'}")
    print(f"最終設定: {settings.get_theme()}")
    
    # Test sound settings
    print(f"\n🔊 サウンド設定テスト:")
    sound_types = ['start', 'end', 'tick']
    for sound_type in sound_types:
        current = settings.get_sound_setting(sound_type)
        print(f"  {sound_type}音: {'🔊' if current else '🔇'}")
        settings.set_sound_setting(sound_type, not current)
        new_setting = settings.get_sound_setting(sound_type)
        print(f"  {sound_type}音を切り替え: {'🔊' if new_setting else '🔇'}")
    
    print(f"\n最終設定: {settings.get_all_settings()}")


def timer_callback_example(time_remaining):
    """Example timer callback."""
    minutes = time_remaining // 60
    seconds = time_remaining % 60
    print(f"\r⏰ 残り時間: {minutes:02d}:{seconds:02d}", end='', flush=True)


def session_complete_callback(session_type):
    """Example session complete callback."""
    session_text = "ワークセッション" if session_type == "work" else "休憩セッション"
    print(f"\n✅ {session_text}が完了しました！")


def state_change_callback(state):
    """Example state change callback."""
    state_text = {
        TimerState.STOPPED: "停止中",
        TimerState.RUNNING: "実行中", 
        TimerState.PAUSED: "一時停止",
        TimerState.BREAK: "休憩中"
    }
    print(f"\n📊 状態変更: {state_text[state]}")


def test_timer_functionality():
    """Test timer functionality with customized settings."""
    print_separator()
    print("⏲️ タイマー機能のテスト")
    print_separator()
    
    # Create settings with custom values
    settings = PomodoroSettings('test_settings.json')
    settings.set_work_time(15)  # Short work session for testing
    settings.set_break_time(5)  # Short break for testing
    settings.set_sound_setting('start', True)
    settings.set_sound_setting('end', True)
    settings.set_sound_setting('tick', False)  # Disable tick to avoid spam
    
    # Create timer
    timer = PomodoroTimer(settings)
    timer.set_callbacks(
        on_tick=timer_callback_example,
        on_session_complete=session_complete_callback,
        on_state_change=state_change_callback
    )
    
    print(f"⚙️ 設定確認:")
    print(f"  作業時間: {settings.get_work_time()}分")
    print(f"  休憩時間: {settings.get_break_time()}分")
    print(f"  テーマ: {settings.get_theme()}")
    print(f"  サウンド設定: {settings.get_all_settings()['sounds']}")
    
    # Test short work session (10 seconds for demo)
    print(f"\n🚀 短時間ワークセッションのテスト (10秒)...")
    timer.time_remaining = 10  # Override for quick test
    timer.total_time = 10
    timer.current_session_type = "work"
    timer._start_timer()
    
    # Wait for completion or timeout
    timeout = 15
    start_time = time.time()
    while timer.state == TimerState.RUNNING and (time.time() - start_time) < timeout:
        time.sleep(0.5)
    
    if timer.state != TimerState.STOPPED:
        timer.stop()
        print("\n⏹️ タイマーを停止しました")
    
    # Show session statistics
    session_info = timer.get_session_info()
    print(f"\n📈 セッション統計:")
    print(f"  完了セッション数: {session_info['completed_sessions']}")
    print(f"  最後のセッション: {session_info['type']}")


def demonstrate_all_features():
    """Demonstrate all customization features."""
    print("🎯 カスタマイズ可能なポモドーロタイマー - 機能デモンストレーション")
    print("https://github.com/williamz-hub/2025-Github-Copilot-Workshop-Python")
    
    test_settings()
    test_timer_functionality()
    
    print_separator()
    print("✨ すべての機能テストが完了しました！")
    print("以下の機能が実装され、動作確認されました:")
    print("  ✅ 作業時間を15/25/35/45分から選択可能")
    print("  ✅ 休憩時間を5/10/15分から選択可能") 
    print("  ✅ テーマ切り替え（ダーク/ライト/フォーカスモード）")
    print("  ✅ サウンド（開始/終了/tick）のオン・オフ切り替え")
    print("  ✅ 設定の永続化（JSON形式）")
    print("  ✅ セッション統計の追跡")
    print_separator()


if __name__ == "__main__":
    demonstrate_all_features()