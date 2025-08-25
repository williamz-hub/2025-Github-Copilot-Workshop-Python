import time
import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TimerState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"


@dataclass
class Achievement:
    """実績データクラス"""
    id: str
    name: str
    description: str
    unlocked: bool = False
    unlock_date: Optional[str] = None


@dataclass
class UserStats:
    """ユーザー統計データクラス"""
    total_pomodoros: int = 0
    total_focus_time: int = 0  # 秒単位
    current_streak: int = 0
    longest_streak: int = 0
    level: int = 1
    experience: int = 0
    last_session_date: Optional[str] = None
    daily_sessions: Dict[str, int] = None  # 日付をキーとした日別セッション数
    achievements: List[Achievement] = None

    def __post_init__(self):
        if self.daily_sessions is None:
            self.daily_sessions = {}
        if self.achievements is None:
            self.achievements = []


class PomodoroTimer:
    """ポモドーロタイマーとゲーミフィケーション機能"""
    
    def __init__(self, work_duration: int = 25 * 60, break_duration: int = 5 * 60):
        self.work_duration = work_duration
        self.break_duration = break_duration
        self.current_duration = work_duration
        self.remaining_time = work_duration
        self.state = TimerState.STOPPED
        self.start_time = None
        self.pause_time = 0
        
        # ゲーミフィケーション要素
        self.stats_file = "pomodoro_stats.json"
        self.user_stats = self._load_stats()
        self._initialize_achievements()
    
    def _load_stats(self) -> UserStats:
        """統計データを読み込み"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Achievementオブジェクトに変換
                    achievements = [Achievement(**ach) for ach in data.get('achievements', [])]
                    data['achievements'] = achievements
                    return UserStats(**data)
            except Exception as e:
                print(f"統計データの読み込みに失敗: {e}")
        return UserStats()
    
    def _save_stats(self):
        """統計データを保存"""
        try:
            # Achievementオブジェクトを辞書に変換
            data = asdict(self.user_stats)
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"統計データの保存に失敗: {e}")
    
    def _initialize_achievements(self):
        """実績システムの初期化"""
        predefined_achievements = [
            Achievement("first_pomodoro", "初回完走", "初めてポモドーロを完了しました"),
            Achievement("streak_3", "3日連続", "3日連続でポモドーロを実行しました"),
            Achievement("streak_7", "1週間連続", "7日連続でポモドーロを実行しました"),
            Achievement("weekly_10", "週間10回", "1週間で10回のポモドーロを完了しました"),
            Achievement("level_5", "レベル5達成", "レベル5に到達しました"),
            Achievement("level_10", "レベル10達成", "レベル10に到達しました"),
            Achievement("total_50", "累計50回", "累計50回のポモドーロを完了しました"),
            Achievement("total_100", "累計100回", "累計100回のポモドーロを完了しました"),
        ]
        
        # 既存の実績IDセット
        existing_ids = {ach.id for ach in self.user_stats.achievements}
        
        # 新しい実績を追加
        for new_ach in predefined_achievements:
            if new_ach.id not in existing_ids:
                self.user_stats.achievements.append(new_ach)
    
    def start_timer(self):
        """タイマー開始"""
        if self.state == TimerState.STOPPED:
            self.remaining_time = self.current_duration
        elif self.state == TimerState.PAUSED:
            self.remaining_time -= self.pause_time
        
        self.state = TimerState.RUNNING
        self.start_time = time.time()
        print(f"タイマー開始: {self.remaining_time // 60}分{self.remaining_time % 60}秒")
    
    def pause_timer(self):
        """タイマー一時停止"""
        if self.state == TimerState.RUNNING:
            self.pause_time = time.time() - self.start_time
            self.state = TimerState.PAUSED
            print("タイマー一時停止")
    
    def stop_timer(self):
        """タイマー停止"""
        self.state = TimerState.STOPPED
        self.remaining_time = self.current_duration
        self.pause_time = 0
        print("タイマー停止")
    
    def update(self):
        """タイマー更新（定期的に呼び出し）"""
        if self.state == TimerState.RUNNING:
            elapsed = time.time() - self.start_time
            self.remaining_time = max(0, self.current_duration - elapsed)
            
            if self.remaining_time <= 0:
                self._timer_completed()
    
    def _timer_completed(self):
        """タイマー完了時の処理"""
        if self.current_duration == self.work_duration:
            # ワークセッション完了
            print("🍅 ポモドーロ完了！お疲れ様でした！")
            self._complete_pomodoro()
            self.current_duration = self.break_duration
            self.state = TimerState.BREAK
        else:
            # 休憩完了
            print("☕ 休憩終了！次のポモドーロを始めましょう")
            self.current_duration = self.work_duration
            self.state = TimerState.STOPPED
        
        self.remaining_time = self.current_duration
    
    def _complete_pomodoro(self):
        """ポモドーロ完了時のゲーミフィケーション処理"""
        today = date.today().isoformat()
        
        # 統計更新
        self.user_stats.total_pomodoros += 1
        self.user_stats.total_focus_time += self.work_duration
        
        # 日別セッション数更新
        if today not in self.user_stats.daily_sessions:
            self.user_stats.daily_sessions[today] = 0
        self.user_stats.daily_sessions[today] += 1
        
        # ストリーク更新
        self._update_streak(today)
        
        # 経験値とレベル更新
        self._add_experience(100)  # ポモドーロ完了で100XP
        
        # 実績チェック
        self._check_achievements()
        
        # 統計保存
        self._save_stats()
        
        print(f"📊 統計更新: 総回数{self.user_stats.total_pomodoros}, レベル{self.user_stats.level}, ストリーク{self.user_stats.current_streak}日")
    
    def _update_streak(self, today: str):
        """ストリーク更新"""
        if self.user_stats.last_session_date:
            last_date = datetime.fromisoformat(self.user_stats.last_session_date).date()
            current_date = datetime.fromisoformat(today).date()
            days_diff = (current_date - last_date).days
            
            if days_diff == 1:
                # 連続日
                self.user_stats.current_streak += 1
            elif days_diff > 1:
                # ストリーク途切れ
                self.user_stats.current_streak = 1
            # days_diff == 0 の場合（同日）はストリーク値を維持
        else:
            # 初回
            self.user_stats.current_streak = 1
        
        self.user_stats.longest_streak = max(self.user_stats.longest_streak, self.user_stats.current_streak)
        self.user_stats.last_session_date = today
    
    def _add_experience(self, xp: int):
        """経験値追加とレベルアップ処理"""
        self.user_stats.experience += xp
        
        # レベルアップ計算（必要XP = レベル * 500）
        required_xp = self.user_stats.level * 500
        while self.user_stats.experience >= required_xp:
            self.user_stats.experience -= required_xp
            self.user_stats.level += 1
            print(f"🎉 レベルアップ！ レベル {self.user_stats.level} になりました！")
            required_xp = self.user_stats.level * 500
    
    def _check_achievements(self):
        """実績チェック"""
        newly_unlocked = []
        
        for achievement in self.user_stats.achievements:
            if achievement.unlocked:
                continue
                
            unlock_condition = False
            
            if achievement.id == "first_pomodoro" and self.user_stats.total_pomodoros >= 1:
                unlock_condition = True
            elif achievement.id == "streak_3" and self.user_stats.current_streak >= 3:
                unlock_condition = True
            elif achievement.id == "streak_7" and self.user_stats.current_streak >= 7:
                unlock_condition = True
            elif achievement.id == "weekly_10" and self._get_weekly_sessions() >= 10:
                unlock_condition = True
            elif achievement.id == "level_5" and self.user_stats.level >= 5:
                unlock_condition = True
            elif achievement.id == "level_10" and self.user_stats.level >= 10:
                unlock_condition = True
            elif achievement.id == "total_50" and self.user_stats.total_pomodoros >= 50:
                unlock_condition = True
            elif achievement.id == "total_100" and self.user_stats.total_pomodoros >= 100:
                unlock_condition = True
            
            if unlock_condition:
                achievement.unlocked = True
                achievement.unlock_date = date.today().isoformat()
                newly_unlocked.append(achievement)
        
        # 新規実績の通知
        for achievement in newly_unlocked:
            print(f"🏆 実績解除: {achievement.name} - {achievement.description}")
    
    def _get_weekly_sessions(self) -> int:
        """今週のセッション数を取得"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        weekly_count = 0
        for i in range(7):
            day = (week_start + timedelta(days=i)).isoformat()
            weekly_count += self.user_stats.daily_sessions.get(day, 0)
        
        return weekly_count
    
    def get_remaining_time_formatted(self) -> str:
        """残り時間を文字列で取得"""
        minutes = int(self.remaining_time // 60)
        seconds = int(self.remaining_time % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_stats_summary(self) -> Dict:
        """統計サマリーを取得"""
        total_hours = self.user_stats.total_focus_time // 3600
        total_minutes = (self.user_stats.total_focus_time % 3600) // 60
        
        return {
            "level": self.user_stats.level,
            "experience": self.user_stats.experience,
            "next_level_xp": self.user_stats.level * 500,
            "total_pomodoros": self.user_stats.total_pomodoros,
            "total_focus_time": f"{total_hours}時間{total_minutes}分",
            "current_streak": self.user_stats.current_streak,
            "longest_streak": self.user_stats.longest_streak,
            "weekly_sessions": self._get_weekly_sessions(),
            "unlocked_achievements": len([a for a in self.user_stats.achievements if a.unlocked]),
            "total_achievements": len(self.user_stats.achievements)
        }