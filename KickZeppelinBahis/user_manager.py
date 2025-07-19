import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class UserManager:
    """Kullanıcı yönetimi ve bakiye sistemi"""
    
    def __init__(self, data_file: str = 'kullanicilar.json'):
        self.data_file = data_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, Any]:
        """Kullanıcı verilerini dosyadan yükle"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f'{len(data)} kullanıcı yüklendi')
                    return data
            else:
                logger.info('Kullanıcı dosyası bulunamadı, yeni dosya oluşturulacak')
                return {}
        except Exception as e:
            logger.error(f'Kullanıcı verisi yüklenirken hata: {e}')
            return {}
    
    def _save_users(self) -> bool:
        """Kullanıcı verilerini dosyaya kaydet"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            logger.debug(f'Kullanıcı verileri {self.data_file} dosyasına kaydedildi')
            return True
        except Exception as e:
            logger.error(f'Kullanıcı verisi kaydedilirken hata: {e}')
            return False
    
    def register_user(self, username: str, subscriber_count: int = 0) -> Dict[str, Any]:
        """
        Yeni kullanıcı kaydet veya mevcut kullanıcıyı güncelle
        
        Args:
            username: Kullanıcı adı
            subscriber_count: Kanal abone sayısı
        
        Returns:
            İşlem sonucu
        """
        try:
            username = username.lower().strip()
            
            if username in self.users:
                return {
                    'success': True,
                    'message': f'🔄 {username} zaten kayıtlı! Mevcut bakiye: {self.users[username]["balance"]:.0f}',
                    'balance': self.users[username]['balance'],
                    'existing': True
                }
            
            # Yeni kullanıcı oluştur
            initial_balance = 1000 if subscriber_count >= 100 else 0
            
            user_data = {
                'username': username,
                'balance': initial_balance,
                'total_bets': 0,
                'total_winnings': 0,
                'games_played': 0,
                'registration_date': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'subscriber_count_at_registration': subscriber_count
            }
            
            self.users[username] = user_data
            self._save_users()
            
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
            logger.error(f'Kullanıcı kaydı hatası: {e}')
            return {
                'success': False,
                'message': f'❌ {username} kaydedilirken hata oluştu!',
                'error': str(e)
            }
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini getir"""
        username = username.lower().strip()
        return self.users.get(username)
    
    def update_user_activity(self, username: str):
        """Kullanıcı aktivitesini güncelle"""
        username = username.lower().strip()
        if username in self.users:
            self.users[username]['last_activity'] = datetime.now().isoformat()
            self._save_users()
    
    def add_balance(self, username: str, amount: float) -> float:
        """Kullanıcı bakiyesine puan ekle"""
        username = username.lower().strip()
        if username in self.users:
            self.users[username]['balance'] += amount
            self.users[username]['total_winnings'] += amount
            self.update_user_activity(username)
            self._save_users()
            logger.debug(f'{username} bakiyesine {amount} eklendi')
            return self.users[username]['balance']
        return 0
    
    def subtract_balance(self, username: str, amount: float) -> float:
        """Kullanıcı bakiyesinden puan düş"""
        username = username.lower().strip()
        if username in self.users:
            self.users[username]['balance'] -= amount
            self.users[username]['total_bets'] += amount
            self.users[username]['games_played'] += 1
            self.update_user_activity(username)
            self._save_users()
            logger.debug(f'{username} bakiyesinden {amount} düşüldü')
            return self.users[username]['balance']
        return 0
    
    def set_balance(self, username: str, amount: float) -> float:
        """Kullanıcı bakiyesini belirle (admin fonksiyonu)"""
        username = username.lower().strip()
        if username in self.users:
            old_balance = self.users[username]['balance']
            self.users[username]['balance'] = amount
            self.update_user_activity(username)
            self._save_users()
            logger.info(f'{username} bakiyesi {old_balance} -> {amount} olarak değiştirildi')
            return amount
        return 0
    
    def get_all_users(self) -> Dict[str, Any]:
        """Tüm kullanıcıları getir"""
        return self.users.copy()
    
    def get_top_users(self, limit: int = 10) -> list:
        """En yüksek bakiyeli kullanıcıları getir"""
        sorted_users = sorted(
            self.users.items(),
            key=lambda x: x[1]['balance'],
            reverse=True
        )
        return sorted_users[:limit]
    
    def get_user_count(self) -> int:
        """Toplam kullanıcı sayısını getir"""
        return len(self.users)
    
    def delete_user(self, username: str) -> bool:
        """Kullanıcıyı sil (admin fonksiyonu)"""
        username = username.lower().strip()
        if username in self.users:
            del self.users[username]
            self._save_users()
            logger.info(f'Kullanıcı silindi: {username}')
            return True
        return False
