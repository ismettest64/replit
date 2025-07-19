import os
import logging
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

# Import database models
from models import db, User, GameResult
from database_manager import DatabaseManager
from game_logic import ZeppelinGame
from kick_api import KickAPI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "zeppelin-game-secret-key")

# Configure PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize game components
db_manager = DatabaseManager()
zeppelin_game = ZeppelinGame()
kick_api = KickAPI()

# Initialize database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")

# Global game state
current_game = None

@app.route('/')
def index():
    """Ana oyun sayfası"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin panel"""
    try:
        # İstatistikleri al
        total_users = db_manager.get_total_users()
        active_users = db_manager.get_active_users()
        total_games = db_manager.get_total_games()
        total_winnings = db_manager.get_total_winnings()
        
        # Son aktiviteler
        recent_activities = db_manager.get_recent_activities(20)
        
        # Mevcut kanal ayarlarını al
        current_channel = getattr(kick_api, 'current_channel', None)
        channel_info = None
        api_status = False
        api_message = "Henüz kanal ayarlanmamış"
        
        if current_channel:
            try:
                channel_info = kick_api.get_channel_info(current_channel)
                api_status = True
                api_message = f"{current_channel} kanalına bağlı"
            except Exception as e:
                api_message = f"Kanal bilgisi alınamadı: {str(e)}"
        
        return render_template('admin.html', 
                             user_stats={
                                 'total_users': total_users,
                                 'active_users': active_users,
                                 'total_games': total_games,
                                 'total_winnings': total_winnings
                             },
                             recent_activities=recent_activities,
                             current_channel=current_channel,
                             channel_info=channel_info,
                             api_status=api_status,
                             api_message=api_message)
    except Exception as e:
        logger.error(f"Admin panel error: {e}")
        return render_template('admin.html', 
                             user_stats={
                                 'total_users': 0,
                                 'active_users': 0,
                                 'total_games': 0,
                                 'total_winnings': 0
                             },
                             recent_activities=[],
                             current_channel=None,
                             channel_info=None,
                             api_status=False,
                             api_message="Sistem hatası")

@app.route('/api/user/<username>')
def get_user(username):
    """Kullanıcı bilgilerini getir"""
    user = db_manager.get_user(username)
    if user:
        return jsonify(user)
    return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

@app.route('/api/stats')
def get_stats():
    """Oyun istatistiklerini getir"""
    stats = db_manager.get_game_stats()
    return jsonify(stats)

@app.route('/api/simulate_follow', methods=['POST'])
def simulate_follow():
    """Test için takip simülasyonu"""
    data = request.get_json()
    username = data.get('username')
    subscriber_count = data.get('subscriber_count', 50)
    
    if not username:
        return jsonify({'error': 'Kullanıcı adı gerekli'}), 400
    
    result = db_manager.register_user(username, subscriber_count)
    
    # Sonucu tüm istemcilere gönder
    socketio.emit('user_registered', {
        'username': username,
        'message': result['message'],
        'balance': result.get('balance', 0),
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })
    
    return jsonify(result)

@app.route('/api/migrate_from_json', methods=['POST'])
def migrate_from_json():
    """JSON verilerini PostgreSQL'e migrate et"""
    try:
        # Mevcut JSON dosyasını oku
        import os
        if os.path.exists('kullanicilar.json'):
            with open('kullanicilar.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Migration işlemini gerçekleştir
            success = db_manager.migrate_from_json(json_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'JSON verileri başarıyla PostgreSQL\'e aktarıldı!'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Migration sırasında hata oluştu!'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'kullanicilar.json dosyası bulunamadı!'
            })
    
    except Exception as e:
        logger.error(f'Migration hatası: {e}')
        return jsonify({
            'success': False,
            'message': f'Migration hatası: {str(e)}'
        })

@socketio.on('connect')
def handle_connect():
    """İstemci bağlantısı"""
    logger.info(f'İstemci bağlandı: {request.sid}')
    join_room('game_room')
    
    # Mevcut oyun durumunu gönder
    if current_game:
        emit('game_state', current_game)

@socketio.on('disconnect')
def handle_disconnect():
    """İstemci bağlantısı kesildi"""
    logger.info(f'İstemci ayrıldı: {request.sid}')
    leave_room('game_room')

@socketio.on('place_bet')
def handle_bet(data):
    """Bahis yerleştirme"""
    try:
        username = data.get('username')
        bet_amount = float(data.get('bet_amount', 0))
        target_multiplier = float(data.get('target_multiplier', 2.0))
        
        logger.info(f'Bahis: {username} - {bet_amount} - {target_multiplier}x')
        
        # Kullanıcı kontrolü
        user = db_manager.get_user(username)
        if not user:
            emit('bet_error', {
                'message': f'❌ {username}, önce takip etmelisin!',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            return
        
        # Bakiye kontrolü
        if user['balance'] < bet_amount:
            emit('bet_error', {
                'message': f'❌ {username}, yeterli bakiyen yok! Mevcut: {user["balance"]:.0f}',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            return
        
        # Bahis limitlerini kontrol et
        if bet_amount < 1:
            emit('bet_error', {
                'message': f'❌ {username}, minimum bahis miktarı 1 puandır!',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            return
        
        if target_multiplier < 1.0 or target_multiplier > 50.0:
            emit('bet_error', {
                'message': f'❌ {username}, çarpan 1.0x ile 50.0x arasında olmalı!',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            return
        
        # Oyunu oyna
        result = zeppelin_game.play_game(username, bet_amount, target_multiplier)
        
        # Kullanıcı bakiyesini güncelle ve oyun sonucunu kaydet
        if result['won']:
            new_balance = db_manager.add_balance(username, result['winnings'])
            message = f'🎉 {username}, {result["actual_multiplier"]:.2f}x ile kazandın! +{result["winnings"]:.0f} puan. Yeni bakiye: {new_balance:.0f}'
        else:
            new_balance = db_manager.subtract_balance(username, bet_amount)
            if result['actual_multiplier'] < target_multiplier:
                message = f'💥 {username}, {result["actual_multiplier"]:.2f}x\'de patladı! Kaybettin. Yeni bakiye: {new_balance:.0f}'
            else:
                message = f'💥 {username}, hiç havalanamadı. Kaybettin. Yeni bakiye: {new_balance:.0f}'
        
        # Oyun sonucunu veritabanına kaydet
        db_manager.save_game_result(
            username, bet_amount, target_multiplier, 
            result['actual_multiplier'], result['won'], 
            result.get('winnings', 0)
        )
        
        # Sonucu tüm istemcilere gönder
        socketio.emit('game_result', {
            'username': username,
            'bet_amount': bet_amount,
            'target_multiplier': target_multiplier,
            'actual_multiplier': result['actual_multiplier'],
            'won': result['won'],
            'winnings': result.get('winnings', 0),
            'new_balance': new_balance,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }, room='game_room')
        
    except Exception as e:
        logger.error(f'Bahis hatası: {e}')
        emit('bet_error', {
            'message': f'❌ {username}, bahis işlenirken hata oluştu!',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

@socketio.on('chat_command')
def handle_chat_command(data):
    """Chat komutlarını işle"""
    try:
        username = data.get('username')
        message = data.get('message', '').strip()
        
        # Bahis komutu kontrolü (!bet miktar çarpan)
        if message.startswith('!bet') or message.startswith('!bahis'):
            parts = message.split()
            if len(parts) >= 3:
                try:
                    bet_amount = float(parts[1])
                    target_multiplier = float(parts[2])
                    
                    # Bahis yerleştir
                    handle_bet({
                        'username': username,
                        'bet_amount': bet_amount,
                        'target_multiplier': target_multiplier
                    })
                except ValueError:
                    emit('chat_error', {
                        'message': f'❌ {username}, geçersiz bahis formatı! Örnek: !bet 100 2.5',
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
            else:
                emit('chat_error', {
                    'message': f'❌ {username}, bahis formatı: !bet <miktar> <çarpan>',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        # Bakiye sorgulama
        elif message.startswith('!balance') or message.startswith('!bakiye'):
            user = db_manager.get_user(username)
            if user:
                emit('chat_info', {
                    'message': f'💰 {username}, bakiyen: {user["balance"]:.0f} puan',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            else:
                emit('chat_error', {
                    'message': f'❌ {username}, önce takip etmelisin!',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        # Yardım komutu
        elif message.startswith('!help') or message.startswith('!yardim'):
            emit('chat_info', {
                'message': f'ℹ️ Komutlar: !bet <miktar> <çarpan>, !bakiye, !yardim',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
    except Exception as e:
        logger.error(f'Chat komutu hatası: {e}')

# Admin Panel Routes

@app.route('/admin/set-channel', methods=['POST'])
def set_channel():
    """Kick kanal ayarla"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': 'Kullanıcı adı gerekli'})
        
        # Kanalı ayarla
        success = kick_api.set_channel(username)
        
        if success:
            # Socket.IO ile güncelleme bildir
            socketio.emit('channel_updated', {'channel': username})
            return jsonify({'success': True, 'message': f'{username} kanalı başarıyla ayarlandı'})
        else:
            return jsonify({'success': False, 'message': 'Kanal ayarlanırken hata oluştu'})
            
    except Exception as e:
        logger.error(f"Set channel error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/test-connection', methods=['POST'])
def test_connection():
    """Kanal bağlantısını test et"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': 'Kullanıcı adı gerekli'})
        
        # Kanal bilgilerini test et
        channel_info = kick_api.get_channel_info(username)
        
        if channel_info:
            return jsonify({
                'success': True, 
                'message': f'✅ {username} kanalına başarıyla bağlandı!\nTakipçi: {channel_info.get("followers_count", 0)}\nDurum: {"Canlı" if channel_info.get("is_live") else "Offline"}'
            })
        else:
            return jsonify({'success': False, 'message': f'❌ {username} kanalı bulunamadı veya erişilemiyor'})
            
    except Exception as e:
        logger.error(f"Test connection error: {e}")
        return jsonify({'success': False, 'message': f'Bağlantı hatası: {str(e)}'})

@app.route('/admin/update-settings', methods=['POST'])
def update_settings():
    """Oyun ayarlarını güncelle"""
    try:
        data = request.get_json()
        
        win_rate = float(data.get('win_rate', 35))
        min_multiplier = float(data.get('min_multiplier', 1.0))
        max_multiplier = float(data.get('max_multiplier', 50.0))
        
        # Geçerlilik kontrolü
        if not (10 <= win_rate <= 60):
            return jsonify({'success': False, 'message': 'Kazanma oranı %10-60 arasında olmalı'})
        
        if not (1.0 <= min_multiplier <= 5.0):
            return jsonify({'success': False, 'message': 'Min çarpan 1.0-5.0 arasında olmalı'})
        
        if not (10.0 <= max_multiplier <= 100.0):
            return jsonify({'success': False, 'message': 'Max çarpan 10.0-100.0 arasında olmalı'})
        
        if min_multiplier >= max_multiplier:
            return jsonify({'success': False, 'message': 'Min çarpan max çarpandan küçük olmalı'})
        
        # Oyun ayarlarını güncelle
        zeppelin_game.update_settings(
            win_rate=win_rate / 100,
            min_multiplier=min_multiplier,
            max_multiplier=max_multiplier
        )
        
        return jsonify({'success': True, 'message': 'Oyun ayarları güncellendi'})
        
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        return jsonify({'success': False, 'message': f'Ayar güncellenirken hata: {str(e)}'})

if __name__ == '__main__':
    logger.info('Zeppelin oyunu başlatılıyor...')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
