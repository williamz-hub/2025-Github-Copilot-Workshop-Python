import unittest
import json
import os
from datetime import date
from models import GameStats


class TestGameStats(unittest.TestCase):
    
    def setUp(self):
        """テスト前にテスト用データファイルを設定"""
        self.test_file = 'test_game_stats.json'
        self.game_stats = GameStats(self.test_file)
    
    def tearDown(self):
        """テスト後にテストファイルを削除"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_initial_state(self):
        """初期状態のテスト"""
        stats = self.game_stats.get_stats()
        self.assertEqual(stats['level'], 1)
        self.assertEqual(stats['experience'], 0)
        self.assertEqual(stats['total_completed'], 0)
        self.assertEqual(stats['current_streak'], 0)
        self.assertEqual(len(stats['badges']), 0)
    
    def test_complete_pomodoro(self):
        """ポモドーロ完了のテスト"""
        result = self.game_stats.complete_pomodoro(100)
        
        # 結果の確認
        self.assertEqual(result['xp_gained'], 100)
        self.assertEqual(result['new_level'], 1)
        self.assertFalse(result['level_up'])
        self.assertEqual(result['current_streak'], 1)
        self.assertIn('first_completion', result['new_badges'])
        
        # 統計の確認
        stats = self.game_stats.get_stats()
        self.assertEqual(stats['level'], 1)
        self.assertEqual(stats['experience'], 100)
        self.assertEqual(stats['total_completed'], 1)
        self.assertEqual(stats['current_streak'], 1)
        self.assertIn('first_completion', stats['badges'])
    
    def test_level_up(self):
        """レベルアップのテスト"""
        # 2回完了してレベルアップ
        self.game_stats.complete_pomodoro(100)
        result = self.game_stats.complete_pomodoro(100)
        
        # レベルアップの確認
        self.assertTrue(result['level_up'])
        self.assertEqual(result['old_level'], 1)
        self.assertEqual(result['new_level'], 2)
        
        stats = self.game_stats.get_stats()
        self.assertEqual(stats['level'], 2)
        self.assertEqual(stats['experience'], 200)
    
    def test_multiple_badges(self):
        """複数バッジ獲得のテスト"""
        # 5回完了して複数バッジ獲得
        for i in range(5):
            result = self.game_stats.complete_pomodoro(100)
        
        stats = self.game_stats.get_stats()
        self.assertIn('first_completion', stats['badges'])
        self.assertIn('five_completions', stats['badges'])
        self.assertEqual(stats['total_completed'], 5)
    
    def test_streak_calculation(self):
        """ストリーク計算のテスト"""
        # 同じ日に複数回完了
        self.game_stats.complete_pomodoro(100)
        self.game_stats.complete_pomodoro(100)
        
        stats = self.game_stats.get_stats()
        self.assertEqual(stats['current_streak'], 1)  # 同じ日なので1のまま
        self.assertEqual(stats['longest_streak'], 1)
    
    def test_weekly_stats(self):
        """週間統計のテスト"""
        # ポモドーロを完了
        self.game_stats.complete_pomodoro(100)
        
        weekly = self.game_stats.get_weekly_stats()
        self.assertEqual(weekly['week_completions'], 1)
        self.assertEqual(len(weekly['daily_breakdown']), 7)
        
        # 今日の完了数を確認
        today = date.today().isoformat()
        today_data = next((d for d in weekly['daily_breakdown'] if d['date'] == today), None)
        self.assertIsNotNone(today_data)
        self.assertEqual(today_data['count'], 1)
    
    def test_data_persistence(self):
        """データ永続化のテスト"""
        # データを保存
        self.game_stats.complete_pomodoro(100)
        
        # 新しいインスタンスを作成して読み込み
        new_game_stats = GameStats(self.test_file)
        stats = new_game_stats.get_stats()
        
        # データが正しく読み込まれていることを確認
        self.assertEqual(stats['experience'], 100)
        self.assertEqual(stats['total_completed'], 1)
        self.assertIn('first_completion', stats['badges'])


if __name__ == '__main__':
    unittest.main()