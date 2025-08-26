from flask import Flask, render_template, jsonify, request
from models import GameStats

app = Flask(__name__)
game_stats = GameStats()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """現在の統計情報を取得"""
    try:
        stats = game_stats.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/weekly', methods=['GET'])
def get_weekly_stats():
    """週間統計を取得"""
    try:
        stats = game_stats.get_weekly_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete', methods=['POST'])
def complete_pomodoro():
    """ポモドーロ完了時の処理"""
    try:
        # XP獲得量をリクエストから取得（デフォルト100）
        data = request.get_json() or {}
        xp_gain = data.get('xp_gain', 100)
        
        result = game_stats.complete_pomodoro(xp_gain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/badges', methods=['GET'])
def get_badges():
    """バッジ情報を取得"""
    try:
        badges_info = {
            'earned': game_stats.data['badges'],
            'available': {
                # 完了数バッジ
                'first_completion': {'name': '初回完了', 'description': '初めてのポモドーロ完了'},
                'five_completions': {'name': '5回完了', 'description': '5回のポモドーロ完了'},
                'ten_completions': {'name': '10回完了', 'description': '10回のポモドーロ完了'},
                'twenty_five_completions': {'name': '25回完了', 'description': '25回のポモドーロ完了'},
                'fifty_completions': {'name': '50回完了', 'description': '50回のポモドーロ完了'},
                'hundred_completions': {'name': '100回完了', 'description': '100回のポモドーロ完了'},
                
                # ストリークバッジ
                'three_day_streak': {'name': '3日連続', 'description': '3日連続でポモドーロ完了'},
                'week_streak': {'name': '1週間連続', 'description': '7日連続でポモドーロ完了'},
                'two_week_streak': {'name': '2週間連続', 'description': '14日連続でポモドーロ完了'},
                'month_streak': {'name': '1ヶ月連続', 'description': '30日連続でポモドーロ完了'},
                
                # レベルバッジ
                'level_five': {'name': 'レベル5到達', 'description': 'レベル5に到達'},
                'level_ten': {'name': 'レベル10到達', 'description': 'レベル10に到達'},
                'level_twenty': {'name': 'レベル20到達', 'description': 'レベル20に到達'}
            }
        }
        return jsonify(badges_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
