#!/usr/bin/env python3
"""
ポモドーロタイマー ゲーミフィケーション機能 テスト
"""

import unittest
import os
import tempfile
from pomodoro_timer import PomodoroTimer, TimerState


class TestPomodoroGamification(unittest.TestCase):
    """ポモドーロタイマーのゲーミフィケーション機能テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # 一時ファイル名を使用
        self.test_file = tempfile.mktemp(suffix='.json')
        self.timer = PomodoroTimer()
        self.timer.stats_file = self.test_file
        # 新しい統計データで初期化
        from pomodoro_timer import UserStats
        self.timer.user_stats = UserStats()
        self.timer._initialize_achievements()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_initial_state(self):
        """初期状態のテスト"""
        stats = self.timer.get_stats_summary()
        self.assertEqual(stats['level'], 1)
        self.assertEqual(stats['experience'], 0)
        self.assertEqual(stats['total_pomodoros'], 0)
        self.assertEqual(stats['current_streak'], 0)
        self.assertEqual(stats['unlocked_achievements'], 0)
    
    def test_xp_and_level_system(self):
        """XPとレベルシステムのテスト"""
        # 初期レベル確認
        self.assertEqual(self.timer.user_stats.level, 1)
        self.assertEqual(self.timer.user_stats.experience, 0)
        
        # XP追加
        self.timer._add_experience(300)
        self.assertEqual(self.timer.user_stats.experience, 300)
        self.assertEqual(self.timer.user_stats.level, 1)
        
        # レベルアップ
        self.timer._add_experience(200)  # 合計500XP
        self.assertEqual(self.timer.user_stats.level, 2)
        self.assertEqual(self.timer.user_stats.experience, 0)
    
    def test_pomodoro_completion(self):
        """ポモドーロ完了時の処理テスト"""
        initial_count = self.timer.user_stats.total_pomodoros
        
        self.timer._complete_pomodoro()
        
        # 統計が更新されているか確認
        self.assertEqual(self.timer.user_stats.total_pomodoros, initial_count + 1)
        self.assertEqual(self.timer.user_stats.experience, 100)  # 100XP獲得
        self.assertEqual(self.timer.user_stats.current_streak, 1)
    
    def test_achievement_system(self):
        """実績システムのテスト"""
        # 初期状態で実績は未解除
        unlocked = [a for a in self.timer.user_stats.achievements if a.unlocked]
        self.assertEqual(len(unlocked), 0)
        
        # 1回完了で「初回完走」実績解除
        self.timer._complete_pomodoro()
        unlocked = [a for a in self.timer.user_stats.achievements if a.unlocked]
        self.assertEqual(len(unlocked), 1)
        
        # 初回完走実績が解除されているか
        first_achievement = next(a for a in self.timer.user_stats.achievements if a.id == "first_pomodoro")
        self.assertTrue(first_achievement.unlocked)
    
    def test_streak_system(self):
        """ストリークシステムのテスト"""
        from datetime import date
        
        today = date.today().isoformat()
        
        # 初回実行
        self.timer._update_streak(today)
        self.assertEqual(self.timer.user_stats.current_streak, 1)
        
        # 同日実行（ストリーク維持）
        self.timer._update_streak(today)
        self.assertEqual(self.timer.user_stats.current_streak, 1)
    
    def test_timer_functionality(self):
        """タイマー機能のテスト"""
        # 初期状態
        self.assertEqual(self.timer.state, TimerState.STOPPED)
        
        # タイマー開始
        self.timer.start_timer()
        self.assertEqual(self.timer.state, TimerState.RUNNING)
        
        # タイマー一時停止
        self.timer.pause_timer()
        self.assertEqual(self.timer.state, TimerState.PAUSED)
        
        # タイマー停止
        self.timer.stop_timer()
        self.assertEqual(self.timer.state, TimerState.STOPPED)
    
    def test_data_persistence(self):
        """データ永続化のテスト"""
        # データ変更
        self.timer._complete_pomodoro()
        original_count = self.timer.user_stats.total_pomodoros
        
        # 保存
        self.timer._save_stats()
        
        # 新しいインスタンス作成
        new_timer = PomodoroTimer()
        new_timer.stats_file = self.test_file
        new_timer.user_stats = new_timer._load_stats()
        
        # データが保持されているか確認
        self.assertEqual(new_timer.user_stats.total_pomodoros, original_count)


if __name__ == '__main__':
    unittest.main()