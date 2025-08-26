from datetime import datetime, date
import json
import os
from typing import Dict, List, Optional


class GameStats:
    """ゲーミフィケーション統計を管理するクラス"""
    
    def __init__(self, data_file='game_stats.json'):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """データファイルから統計データを読み込み"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self._create_default_data()
    
    def _create_default_data(self) -> Dict:
        """デフォルトの統計データを作成"""
        return {
            'level': 1,
            'experience': 0,
            'total_completed': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'last_completion_date': None,
            'badges': [],
            'completion_history': [],  # [{'date': 'YYYY-MM-DD', 'count': int}]
            'daily_completions': {}    # {'YYYY-MM-DD': count}
        }
    
    def _save_data(self):
        """データをファイルに保存"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def complete_pomodoro(self, xp_gain: int = 100) -> Dict:
        """ポモドーロ完了時の処理"""
        today = date.today().isoformat()
        
        # 経験値とレベルアップ処理
        old_level = self.data['level']
        self.data['experience'] += xp_gain
        new_level = self._calculate_level(self.data['experience'])
        self.data['level'] = new_level
        
        # 完了数更新
        self.data['total_completed'] += 1
        
        # 日次完了数更新
        if today not in self.data['daily_completions']:
            self.data['daily_completions'][today] = 0
        self.data['daily_completions'][today] += 1
        
        # ストリーク更新
        self._update_streak(today)
        
        # バッジチェック
        new_badges = self._check_new_badges()
        
        # 履歴更新
        self._update_completion_history(today)
        
        self._save_data()
        
        return {
            'level_up': new_level > old_level,
            'old_level': old_level,
            'new_level': new_level,
            'experience': self.data['experience'],
            'xp_gained': xp_gain,
            'new_badges': new_badges,
            'current_streak': self.data['current_streak']
        }
    
    def _calculate_level(self, experience: int) -> int:
        """経験値からレベルを計算"""
        # レベル1: 0-199XP, レベル2: 200-499XP, レベル3: 500-899XP...
        # 各レベルに必要なXP = 200 + (level-1) * 300
        level = 1
        required_xp = 0
        
        while experience >= required_xp:
            next_level_xp = 200 + (level - 1) * 300
            if experience >= required_xp + next_level_xp:
                required_xp += next_level_xp
                level += 1
            else:
                break
        
        return level
    
    def _update_streak(self, today: str):
        """ストリーク情報を更新"""
        last_date = self.data['last_completion_date']
        
        if last_date is None:
            # 初回完了
            self.data['current_streak'] = 1
        else:
            last_datetime = datetime.fromisoformat(last_date).date()
            today_datetime = datetime.fromisoformat(today).date()
            diff = (today_datetime - last_datetime).days
            
            if diff == 0:
                # 同じ日の完了（ストリークは変わらず）
                pass
            elif diff == 1:
                # 連続日
                self.data['current_streak'] += 1
            else:
                # ストリーク途切れ
                self.data['current_streak'] = 1
        
        # 最長ストリーク更新
        if self.data['current_streak'] > self.data['longest_streak']:
            self.data['longest_streak'] = self.data['current_streak']
        
        self.data['last_completion_date'] = today
    
    def _update_completion_history(self, today: str):
        """完了履歴を更新"""
        # 日次完了数履歴を更新
        existing_entry = None
        for entry in self.data['completion_history']:
            if entry['date'] == today:
                existing_entry = entry
                break
        
        if existing_entry:
            existing_entry['count'] = self.data['daily_completions'][today]
        else:
            self.data['completion_history'].append({
                'date': today,
                'count': self.data['daily_completions'][today]
            })
        
        # 履歴は直近90日分のみ保持
        self.data['completion_history'].sort(key=lambda x: x['date'], reverse=True)
        self.data['completion_history'] = self.data['completion_history'][:90]
    
    def _check_new_badges(self) -> List[str]:
        """新しく獲得したバッジをチェック"""
        new_badges = []
        existing_badges = set(self.data['badges'])
        
        # 完了数バッジ
        total = self.data['total_completed']
        completion_badges = {
            1: "first_completion",
            5: "five_completions", 
            10: "ten_completions",
            25: "twenty_five_completions",
            50: "fifty_completions",
            100: "hundred_completions"
        }
        
        for threshold, badge in completion_badges.items():
            if total >= threshold and badge not in existing_badges:
                new_badges.append(badge)
                self.data['badges'].append(badge)
        
        # ストリークバッジ
        streak = self.data['current_streak']
        streak_badges = {
            3: "three_day_streak",
            7: "week_streak", 
            14: "two_week_streak",
            30: "month_streak"
        }
        
        for threshold, badge in streak_badges.items():
            if streak >= threshold and badge not in existing_badges:
                new_badges.append(badge)
                self.data['badges'].append(badge)
        
        # レベルバッジ
        level = self.data['level']
        level_badges = {
            5: "level_five",
            10: "level_ten",
            20: "level_twenty"
        }
        
        for threshold, badge in level_badges.items():
            if level >= threshold and badge not in existing_badges:
                new_badges.append(badge)
                self.data['badges'].append(badge)
        
        return new_badges
    
    def get_stats(self) -> Dict:
        """現在の統計情報を取得"""
        # 次のレベルまでに必要なXP計算
        current_level = self.data['level']
        current_xp = self.data['experience']
        
        # 現在のレベルの開始XP
        level_start_xp = 0
        for i in range(1, current_level):
            level_start_xp += 200 + (i - 1) * 300
        
        # 次のレベルまでに必要なXP
        next_level_xp = 200 + (current_level - 1) * 300
        xp_progress = current_xp - level_start_xp
        
        return {
            'level': self.data['level'],
            'experience': self.data['experience'],
            'xp_progress': xp_progress,
            'xp_to_next_level': next_level_xp - xp_progress,
            'total_completed': self.data['total_completed'],
            'current_streak': self.data['current_streak'],
            'longest_streak': self.data['longest_streak'],
            'badges': self.data['badges'],
            'completion_history': self.data['completion_history'][-30:],  # 直近30日
            'today_completions': self.data['daily_completions'].get(date.today().isoformat(), 0)
        }
    
    def get_weekly_stats(self) -> Dict:
        """週間統計を取得"""
        from datetime import timedelta
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        week_completions = 0
        for i in range(7):
            check_date = (week_start + timedelta(days=i)).isoformat()
            week_completions += self.data['daily_completions'].get(check_date, 0)
        
        return {
            'week_completions': week_completions,
            'week_start': week_start.isoformat(),
            'daily_breakdown': [
                {
                    'date': (week_start + timedelta(days=i)).isoformat(),
                    'count': self.data['daily_completions'].get((week_start + timedelta(days=i)).isoformat(), 0)
                }
                for i in range(7)
            ]
        }