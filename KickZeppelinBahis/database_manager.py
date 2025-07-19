import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from models import db, User, GameResult, GameStats, get_or_create_daily_stats

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Veritabanı yönetimi sınıfı - JSON UserManager'ın yerine geçer"""
    
    def __init__(self):
        """Database manager başlat"""
        logger.info("Database manager başlatıldı")
    
    def register_user(self, username: str, subscriber_count: int = 0) -> Dict[str, Any]:
        """
        Yeni kullanıcı kaydet veya mevcut kullanıcıyı döndür
        
        Args:
            username: Kullanıcı adı
            subscriber_count: Kanal abone sayısı
        
        Returns:
            İşlem sonucu
        """
        try:
            username = username.lower().strip()
            
            # Mevcut kullanıcıyı kontrol et
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                return {
                    'success': True,
                    'message': f'🔄 {username} zaten kayıtlı! Mevcut bakiye: {existing_user.balance:.0f}',
                    'balance': existing_user.balance,
                    'existing': True
                }
            
            # Yeni kullanıcı oluştur
            initial_balance = 1000 if subscriber_count >= 100 else 0
            
            new_user = User(
                username=username,
                balance=initial_balance,
                subscriber_count_at_registration=subscriber_count,
                registration_date=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            if initial_balance > 0:
                message = f'🎉 {username} 100+ abone ile katıldı! {initial_balance} puan verildi.'
            else:
                message = f'👋 {username} oyuna katıldı! Abone sayısı artırılınca puan alacak.'
            
            logger.info(f'Yeni kullanıcı kaydedildi: {username} (bakiye: {initial_balance})')
            
            return {
                'success': True,
                'message': message,
                'balance': initial_balance,
                'existing': False
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Kullanıcı kaydı hatası: {e}')
            return {
                'success': False,
                'message': f'❌ {username} kaydedilirken hata oluştu!',
                'error': str(e)
            }
    
    def get_total_users(self):
        """Toplam kullanıcı sayısını al"""
        try:
            return User.query.count()
        except Exception as e:
            logger.error(f"Get total users error: {e}")
            return 0
    
    def get_active_users(self):
        """Aktif kullanıcı sayısını al (bakiyesi > 0)"""
        try:
            return User.query.filter(User.balance > 0).count()
        except Exception as e:
            logger.error(f"Get active users error: {e}")
            return 0
    
    def get_total_games(self):
        """Toplam oyun sayısını al"""
        try:
            return GameResult.query.count()
        except Exception as e:
            logger.error(f"Get total games error: {e}")
            return 0
    
    def get_total_winnings(self):
        """Toplam kazancı al"""
        try:
            result = db.session.query(db.func.sum(GameResult.winnings)).filter_by(won=True).scalar()
            return result if result else 0
        except Exception as e:
            logger.error(f"Get total winnings error: {e}")
            return 0
    
    def get_recent_activities(self, limit=20):
        """Son aktiviteleri al"""
        try:
            results = GameResult.query.order_by(GameResult.game_date.desc()).limit(limit).all()
            activities = []
            
            for result in results:
                activities.append({
                    'username': result.player.username if result.player else 'Unknown',
                    'bet_amount': result.bet_amount,
                    'multiplier': result.actual_multiplier,
                    'result': 'win' if result.won else 'lose',
                    'timestamp': result.game_date
                })
            
            return activities
        except Exception as e:
            logger.error(f"Get recent activities error: {e}")
            return []
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini getir"""
        try:
            username = username.lower().strip()
            user = User.query.filter_by(username=username).first()
            return user.to_dict() if user else None
        except Exception as e:
            logger.error(f'Kullanıcı getirme hatası: {e}')
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """ID ile kullanıcı getir"""
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f'Kullanıcı ID getirme hatası: {e}')
            return None
    
    def update_user_activity(self, username: str) -> bool:
        """Kullanıcı aktivitesini güncelle"""
        try:
            username = username.lower().strip()
            user = User.query.filter_by(username=username).first()
            
            if user:
                user.update_activity()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f'Aktivite güncelleme hatası: {e}')
            return False
    
    def add_balance(self, username: str, amount: float) -> float:
        """Kullanıcı bakiyesine puan ekle"""
        try:
            username = username.lower().strip()
            user = User.query.filter_by(username=username).first()
            
            if user:
                user.balance += amount
                user.total_winnings += amount
                user.update_activity()
                db.session.commit()
                logger.debug(f'{username} bakiyesine {amount} eklendi')
                return user.balance
            return 0
        except Exception as e:
            db.session.rollback()
            logger.error(f'Bakiye ekleme hatası: {e}')
            return 0
    
    def subtract_balance(self, username: str, amount: float) -> float:
        """Kullanıcı bakiyesinden puan düş"""
        try:
            username = username.lower().strip()
            user = User.query.filter_by(username=username).first()
            
            if user:
                user.balance -= amount
                user.total_bets += amount
                user.games_played += 1
                user.update_activity()
                db.session.commit()
                logger.debug(f'{username} bakiyesinden {amount} düşüldü')
                return user.balance
            return 0
        except Exception as e:
            db.session.rollback()
            logger.error(f'Bakiye düşme hatası: {e}')
            return 0
    
    def set_balance(self, username: str, amount: float) -> float:
        """Kullanıcı bakiyesini belirle (admin fonksiyonu)"""
        try:
            username = username.lower().strip()
            user = User.query.filter_by(username=username).first()
            
            if user:
                old_balance = user.balance
                user.balance = amount
                user.update_activity()
                db.session.commit()
                logger.info(f'{username} bakiyesi {old_balance} -> {amount} olarak değiştirildi')
                return amount
            return 0
        except Exception as e:
            db.session.rollback()
            logger.error(f'Bakiye belirleme hatası: {e}')
            return 0
    
    def get_all_users(self) -> Dict[str, Any]:
        """Tüm kullanıcıları getir"""
        try:
            users = User.query.all()
            return {user.username: user.to_dict() for user in users}
        except Exception as e:
            logger.error(f'Tüm kullanıcıları getirme hatası: {e}')
            return {}
    
    def get_top_users(self, limit: int = 10) -> List[tuple]:
        """En yüksek bakiyeli kullanıcıları getir"""
        try:
            users = User.query.order_by(User.balance.desc()).limit(limit).all()
            return [(user.username, user.to_dict()) for user in users]
        except Exception as e:
            logger.error(f'Top kullanıcıları getirme hatası: {e}')
            return []
    
    def get_user_count(self) -> int:
        """Toplam kullanıcı sayısını getir"""
        try:
            return User.query.count()
        except Exception as e:
            logger.error(f'Kullanıcı sayısı getirme hatası: {e}')
            return 0
    
    def delete_user(self, username: str) -> bool:
        """Kullanıcıyı sil (admin fonksiyonu)"""
        try:
            username = username.lower().strip()
            user = User.query.filter_by(username=username).first()
            
            if user:
                db.session.delete(user)
                db.session.commit()
                logger.info(f'Kullanıcı silindi: {username}')
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f'Kullanıcı silme hatası: {e}')
            return False
    
    def save_game_result(self, username: str, bet_amount: float, target_multiplier: float, 
                        actual_multiplier: float, won: bool, winnings: float = 0) -> bool:
        """Oyun sonucunu veritabanına kaydet"""
        try:
            user = User.query.filter_by(username=username.lower().strip()).first()
            
            if not user:
                logger.error(f'Oyun sonucu kaydı için kullanıcı bulunamadı: {username}')
                return False
            
            game_result = GameResult(
                user_id=user.id,
                bet_amount=bet_amount,
                target_multiplier=target_multiplier,
                actual_multiplier=actual_multiplier,
                won=won,
                winnings=winnings,
                game_date=datetime.utcnow()
            )
            
            db.session.add(game_result)
            db.session.commit()
            
            # Günlük istatistikleri güncelle
            self.update_daily_stats(bet_amount, winnings)
            
            logger.debug(f'Oyun sonucu kaydedildi: {username} - {bet_amount} -> {winnings}')
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Oyun sonucu kaydetme hatası: {e}')
            return False
    
    def update_daily_stats(self, bet_amount: float, winnings: float):
        """Günlük istatistikleri güncelle"""
        try:
            stats = get_or_create_daily_stats()
            
            stats.total_games += 1
            stats.total_bets += bet_amount
            stats.total_winnings += winnings
            stats.active_users = User.query.count()
            stats.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Günlük istatistik güncelleme hatası: {e}')
    
    def get_game_stats(self) -> Dict[str, Any]:
        """Oyun istatistiklerini getir"""
        try:
            # Bugünkü istatistikler
            today_stats = get_or_create_daily_stats()
            
            # Tüm zamanların istatistikleri
            all_time_games = db.session.query(db.func.sum(GameStats.total_games)).scalar() or 0
            all_time_bets = db.session.query(db.func.sum(GameStats.total_bets)).scalar() or 0
            all_time_winnings = db.session.query(db.func.sum(GameStats.total_winnings)).scalar() or 0
            
            # Toplam bakiye
            total_balance = db.session.query(db.func.sum(User.balance)).scalar() or 0
            
            return {
                'total_games': int(all_time_games),
                'total_bets': float(all_time_bets),
                'total_winnings': float(all_time_winnings),
                'active_users': User.query.count(),
                'total_balance': float(total_balance),
                'today_games': today_stats.total_games,
                'today_bets': today_stats.total_bets,
                'today_winnings': today_stats.total_winnings
            }
            
        except Exception as e:
            logger.error(f'İstatistik getirme hatası: {e}')
            return {
                'total_games': 0,
                'total_bets': 0,
                'total_winnings': 0,
                'active_users': 0,
                'total_balance': 0,
                'today_games': 0,
                'today_bets': 0,
                'today_winnings': 0
            }
    
    def get_recent_games(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Son oyunları getir"""
        try:
            results = GameResult.query.order_by(GameResult.game_date.desc()).limit(limit).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            logger.error(f'Son oyunları getirme hatası: {e}')
            return []
    
    def migrate_from_json(self, json_users: Dict[str, Any]) -> bool:
        """JSON verilerini PostgreSQL'e migrate et"""
        try:
            migrated_count = 0
            
            for username, user_data in json_users.items():
                if username == "_metadata":
                    continue
                
                # Kullanıcı zaten var mı kontrol et
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    continue
                
                # JSON'dan kullanıcı oluştur
                new_user = User(
                    username=username,
                    balance=user_data.get('balance', 0),
                    total_bets=user_data.get('total_bets', 0),
                    total_winnings=user_data.get('total_winnings', 0),
                    games_played=user_data.get('games_played', 0),
                    registration_date=datetime.fromisoformat(user_data.get('registration_date', datetime.utcnow().isoformat())),
                    last_activity=datetime.fromisoformat(user_data.get('last_activity', datetime.utcnow().isoformat())),
                    subscriber_count_at_registration=user_data.get('subscriber_count_at_registration', 0)
                )
                
                db.session.add(new_user)
                migrated_count += 1
            
            db.session.commit()
            logger.info(f'{migrated_count} kullanıcı JSON\'dan PostgreSQL\'e migrate edildi')
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'JSON migration hatası: {e}')
            return False