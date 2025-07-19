#!/usr/bin/env python3
"""
Zeppelin Betting Game - Hızlı Başlatma
Bu script tüm kurulum adımlarını otomatik yapar.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_step(step, message):
    """Print formatted step"""
    print(f"\n🔥 ADIM {step}: {message}")
    print("=" * 50)

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"▶️  {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Başarılı: {description}")
            return True
        else:
            print(f"❌ Hata: {description}")
            print(f"   {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return False

def create_env_file():
    """Create .env file with defaults"""
    env_content = """# Zeppelin Betting Game - Otomatik Oluşturulmuş Ayarlar
DATABASE_URL=sqlite:///zeppelin_game.db
SESSION_SECRET=zeppelin-game-secret-key-12345
KICK_CLIENT_ID=mock-client-id
KICK_CLIENT_SECRET=mock-client-secret
FLASK_ENV=development
FLASK_DEBUG=1
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env dosyası oluşturuldu (SQLite ile)")

def main():
    """Main installation process"""
    print("🚀 ZEPPELİN BETTING GAME - OTOMATIK KURULUM")
    print("Bu script oyunu otomatik olarak kurup başlatacak")
    print("=" * 50)
    
    # Python version check
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ gerekli. Lütfen Python'ı güncelleyin.")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} - OK")
    
    print_step(1, "Gerekli Python paketlerini kurma")
    packages = [
        "flask", "flask-socketio", "flask-sqlalchemy", 
        "requests", "sqlalchemy", "trafilatura", "email-validator"
    ]
    
    for package in packages:
        success = run_command(f"pip install {package}", f"{package} kurulumu")
        if not success:
            print(f"⚠️  {package} kurulamadı, devam ediliyor...")
    
    print_step(2, "Yapılandırma dosyası oluşturma")
    create_env_file()
    
    print_step(3, "Oyunu test etme")
    
    # Test imports
    try:
        import flask
        import flask_socketio
        import flask_sqlalchemy
        print("✅ Flask paketleri hazır")
    except ImportError as e:
        print(f"❌ Paket import hatası: {e}")
        print("Manuel kurulum gerekli")
        sys.exit(1)
    
    print_step(4, "Oyunu başlatma")
    
    print("""
🎮 OYUN HAZIR!

▶️  Oyunu başlatmak için:
   python quick_start.py run

🌐 Tarayıcıda açılacak adresler:
   Ana sayfa: http://localhost:5000
   Admin panel: http://localhost:5000/admin

📝 Not: 
   - SQLite kullanılıyor (hızlı başlatma için)
   - PostgreSQL için INSTALLATION.md'yi okuyun
   - Kick API mock modda çalışıyor

🎯 Test komutları (tarayıcı konsolunda):
   simulateFollow() - Takip simülasyonu
   placeBet() - Bahis simülasyonu
""")

def run_game():
    """Run the game"""
    print("🚀 Oyun başlatılıyor...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///zeppelin_game.db'
    os.environ['SESSION_SECRET'] = 'zeppelin-game-secret-key-12345'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        # Import and run the app
        sys.path.append('.')
        from main import app, socketio
        
        print("🌐 Oyun başladı: http://localhost:5000")
        print("⚙️  Admin panel: http://localhost:5000/admin")
        print("🛑 Durdurmak için Ctrl+C")
        
        socketio.run(app, host='127.0.0.1', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 Oyun kapatıldı")
    except Exception as e:
        print(f"\n❌ Oyun başlatma hatası: {e}")
        print("Detaylar için INSTALLATION.md dosyasını kontrol edin")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        run_game()
    else:
        main()