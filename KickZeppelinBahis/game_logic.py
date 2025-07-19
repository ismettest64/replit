import random
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ZeppelinGame:
    """Zeppelin oyun mantığı"""
    
    def __init__(self):
        self.win_rate = 0.35  # %35 kazanma oranı
        self.min_multiplier = 1.0
        self.max_multiplier = 50.0
    
    def play_game(self, username: str, bet_amount: float, target_multiplier: float) -> Dict[str, Any]:
        """
        Zeppelin oyununu oyna
        
        Args:
            username: Oyuncu adı
            bet_amount: Bahis miktarı
            target_multiplier: Hedef çarpan
        
        Returns:
            Oyun sonucu dict'i
        """
        try:
            # Rastgele bir çarpan üret
            actual_multiplier = self._generate_multiplier()
            
            # Kazanma durumunu kontrol et
            won = self._check_win(target_multiplier, actual_multiplier)
            
            result = {
                'username': username,
                'bet_amount': bet_amount,
                'target_multiplier': target_multiplier,
                'actual_multiplier': actual_multiplier,
                'won': won
            }
            
            if won:
                # Kazanç hesapla
                winnings = bet_amount * target_multiplier
                result['winnings'] = winnings
                logger.info(f'{username} kazandı: {bet_amount} -> {winnings} ({target_multiplier}x)')
            else:
                result['winnings'] = 0
                logger.info(f'{username} kaybetti: {actual_multiplier:.2f}x < {target_multiplier}x')
            
            return result
            
        except Exception as e:
            logger.error(f'Oyun hatası: {e}')
            return {
                'username': username,
                'bet_amount': bet_amount,
                'target_multiplier': target_multiplier,
                'actual_multiplier': 0,
                'won': False,
                'winnings': 0,
                'error': str(e)
            }
    
    def _generate_multiplier(self) -> float:
        """
        Rastgele bir çarpan üret
        Dağılım: Düşük çarpanlar daha sık, yüksek çarpanlar daha nadir
        """
        # %35 kazanma şansı için özel dağılım
        rand = random.random()
        
        if rand < 0.65:  # %65 kayıp - düşük çarpanlar
            # 0.1x ile 2.0x arası
            multiplier = random.uniform(0.1, 2.0)
        else:  # %35 kazanma şansı - yüksek çarpanlar
            # Logaritmik dağılım ile yüksek çarpanlar
            # Düşük çarpanlar daha sık, yüksek çarpanlar daha nadir
            base = random.random()
            if base < 0.7:  # %70 - orta çarpanlar (1-5x)
                multiplier = random.uniform(1.0, 5.0)
            elif base < 0.9:  # %20 - yüksek çarpanlar (5-20x)
                multiplier = random.uniform(5.0, 20.0)
            else:  # %10 - çok yüksek çarpanlar (20-50x)
                multiplier = random.uniform(20.0, 50.0)
        
        return round(multiplier, 2)
    
    def _check_win(self, target_multiplier: float, actual_multiplier: float) -> bool:
        """
        Kazanma durumunu kontrol et
        Hedef çarpana ulaşırsa kazanır
        """
        return actual_multiplier >= target_multiplier
    
    def get_win_probability(self, target_multiplier: float) -> float:
        """
        Belirli bir çarpan için kazanma olasılığını hesapla (yaklaşık)
        """
        # Basit yaklaşım - gerçek dağılım daha karmaşık
        if target_multiplier <= 1.0:
            return 1.0
        elif target_multiplier <= 2.0:
            return 0.35
        elif target_multiplier <= 5.0:
            return 0.25
        elif target_multiplier <= 10.0:
            return 0.15
        elif target_multiplier <= 20.0:
            return 0.07
        else:
            return 0.035
    
    def update_settings(self, win_rate: float, min_multiplier: float, max_multiplier: float):
        """Oyun ayarlarını güncelle"""
        self.win_rate = win_rate
        self.min_multiplier = min_multiplier
        self.max_multiplier = max_multiplier
        logger.info(f'Oyun ayarları güncellendi - Win Rate: {win_rate:.2%}, Min: {min_multiplier}x, Max: {max_multiplier}x')
