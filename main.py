#!/usr/bin/env python3
"""
カスタマイズ可能なポモドーロタイマー
Customizable Pomodoro Timer

ユーザーごとに最適なポモドーロ体験を提供するため、設定のカスタマイズ性を強化したアプリケーション。

機能:
- 作業時間を15/25/35/45分から選択可能
- テーマ切り替え（ダーク/ライト/フォーカスモード）
- サウンド（開始/終了/tick）のオン・オフ切り替え
- 休憩時間を5/10/15分から選択可能
"""

from pomodoro_app import PomodoroApp


def main():
    """Main entry point for the Pomodoro Timer application."""
    try:
        app = PomodoroApp()
        app.run()
    except KeyboardInterrupt:
        print("\nアプリケーションを終了します...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()