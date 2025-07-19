import os
import logging
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KickAPI:
    """Kick API entegrasyonu (MVP için mock implementasyon)"""
    
    def __init__(self):
        self.client_id = os.environ.get('KICK_CLIENT_ID', '01K0FSGZDGW771BFF7KDPZA3XY')
        self.client_secret = os.environ.get('KICK_CLIENT_SECRET', 'aa11182885b6d1b25f6f8c105c4fd0ea32040a950de5e21a41a1913f190957aa')
        self.channel_id = os.environ.get('KICK_CHANNEL_ID', 'test_channel')
        self.current_channel = None  # Dinamik kanal ayarı
        self.access_token = None
        self.api_base_url = 'https://kick.com/api/v1'
        
        # Gerçek Kick API kullanımı için
        self.mock_mode = False
        
        logger.info('Kick API entegrasyonu başlatıldı - Gerçek API kullanılacak')
        
        # Access token al
        self._get_access_token()
    
    def _get_access_token(self):
        """Kick API access token al"""
        try:
            auth_url = 'https://kick.com/api/v1/authentication/login'
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'ZeppelinBot/1.0'
            }
            
            # OAuth2 Client Credentials flow
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(auth_url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                if self.access_token:
                    logger.info('Kick API access token başarıyla alındı')
                else:
                    logger.warning('Access token alınamadı, mock modda devam edilecek')
                    self.mock_mode = True
            else:
                logger.warning(f'Kick API authentication başarısız: {response.status_code}')
                logger.warning('Mock modda devam edilecek')
                self.mock_mode = True
                
        except requests.exceptions.RequestException as e:
            logger.error(f'Kick API bağlantı hatası: {e}')
            logger.info('Mock modda devam edilecek')
            self.mock_mode = True
        except Exception as e:
            logger.error(f'Kick API authentication hatası: {e}')
            self.mock_mode = True
    
    def get_channel_info(self, channel_slug: str = None) -> Dict[str, Any]:
        """Kanal bilgilerini getir"""
        if self.mock_mode:
            return {
                'channel_id': self.channel_id,
                'name': 'Test Kanalı',
                'subscriber_count': 150,  # Test için 100+ abone
                'is_live': True,
                'viewer_count': 45,
                'last_updated': datetime.now().isoformat()
            }
        
        # Gerçek API implementasyonu
        try:
            channel = channel_slug or self.channel_id
            url = f'{self.api_base_url}/channels/{channel}'
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'ZeppelinBot/1.0'
            }
            
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'channel_id': data.get('id', self.channel_id),
                    'name': data.get('user', {}).get('username', 'Bilinmeyen'),
                    'subscriber_count': data.get('followers_count', 0),
                    'is_live': data.get('livestream') is not None,
                    'viewer_count': data.get('livestream', {}).get('viewer_count', 0) if data.get('livestream') else 0,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                logger.warning(f'Kanal bilgisi alınamadı: {response.status_code}')
                return self._fallback_channel_info()
                
        except Exception as e:
            logger.error(f'Kick API hatası: {e}')
            return self._fallback_channel_info()
    
    def _fallback_channel_info(self) -> Dict[str, Any]:
        """Hata durumunda fallback bilgiler"""
        return {
            'channel_id': self.channel_id,
            'name': 'Zeppelin Oyunu',
            'subscriber_count': 150,
            'is_live': True,
            'viewer_count': 45,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_follower_count(self) -> int:
        """Takipçi sayısını getir"""
        channel_info = self.get_channel_info()
        return channel_info.get('subscriber_count', 0) if channel_info else 0
    
    def listen_to_chat(self, callback_function):
        """
        Chat mesajlarını dinle
        Gerçek implementasyonda WebSocket bağlantısı kurulacak
        """
        if self.mock_mode:
            logger.info('Mock modda chat dinlenmesi simüle ediliyor')
            # Test için örnek mesajlar gönderilebilir
            return
        
        try:
            # TODO: Gerçek Kick chat WebSocket bağlantısı
            pass
        except Exception as e:
            logger.error(f'Chat dinleme hatası: {e}')
    
    def send_message(self, message: str) -> bool:
        """Chat'e mesaj gönder"""
        if self.mock_mode:
            logger.info(f'Mock mesaj gönderildi: {message}')
            return True
        
        try:
            # TODO: Gerçek Kick API mesaj gönderme
            return True
        except Exception as e:
            logger.error(f'Mesaj gönderme hatası: {e}')
            return False
    
    def handle_follow_event(self, username: str) -> Dict[str, Any]:
        """
        Takip etme olayını işle
        Gerçek API'de webhook veya WebSocket ile gelecek
        """
        try:
            follower_count = self.get_follower_count()
            
            return {
                'username': username,
                'follower_count': follower_count,
                'timestamp': datetime.now().isoformat(),
                'eligible_for_bonus': follower_count >= 100
            }
        except Exception as e:
            logger.error(f'Takip olayı işleme hatası: {e}')
            return None
    
    def get_current_channel(self) -> Optional[str]:
        """Mevcut kanal adını getir"""
        return self.current_channel
    
    def set_channel(self, username: str) -> bool:
        """Kanal ayarla"""
        try:
            # Kanal geçerliliğini kontrol et
            channel_info = self.get_channel_info(username)
            
            if channel_info:
                self.current_channel = username
                logger.info(f'Kanal ayarlandı: {username}')
                return True
            else:
                logger.warning(f'Kanal bulunamadı: {username}')
                return False
                
        except Exception as e:
            logger.error(f'Kanal ayarlama hatası: {e}')
            return False
    
    def get_chat_commands(self) -> list:
        """Desteklenen chat komutlarını getir"""
        return [
            '!bet <miktar> <çarpan> - Bahis oyna',
            '!bahis <miktar> <çarpan> - Bahis oyna',
            '!balance - Bakiyeni kontrol et',
            '!bakiye - Bakiyeni kontrol et',
            '!help - Yardım menüsü',
            '!yardim - Yardım menüsü'
        ]
    
    def parse_chat_message(self, message: str, username: str) -> Optional[Dict[str, Any]]:
        """Chat mesajını parse et ve komut varsa döndür"""
        try:
            message = message.strip()
            
            if not message.startswith('!'):
                return None
            
            parts = message.split()
            command = parts[0].lower()
            
            if command in ['!bet', '!bahis'] and len(parts) >= 3:
                try:
                    bet_amount = float(parts[1])
                    target_multiplier = float(parts[2])
                    
                    return {
                        'type': 'bet',
                        'username': username,
                        'bet_amount': bet_amount,
                        'target_multiplier': target_multiplier
                    }
                except ValueError:
                    return {
                        'type': 'error',
                        'username': username,
                        'message': 'Geçersiz bahis formatı!'
                    }
            
            elif command in ['!balance', '!bakiye']:
                return {
                    'type': 'balance',
                    'username': username
                }
            
            elif command in ['!help', '!yardim']:
                return {
                    'type': 'help',
                    'username': username
                }
            
            return None
            
        except Exception as e:
            logger.error(f'Chat mesajı parse hatası: {e}')
            return None
