#!/usr/bin/env python3
"""
Zeppelin Betting Game - Local Development Runner
Bu dosya oyunu kendi bilgisayarınızda çalıştırmak için kullanılır.
"""

import os
import sys
from pathlib import Path

# .env dosyasını yükle
def load_env():
    """Load environment variables from .env file"""
    env_path = Path('.') / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Tırnak işaretlerini temizle
                    value = value.strip('"\'')
                    os.environ[key] = value
        print("✅ .env dosyası yüklendi")
    else:
        print("⚠️  .env dosyası bulunamadı")
        # Otomatik .env dosyası oluştur
        create_default_env()

def create_default_env():
    """Create default .env file"""
    print("🔧 Otomatik .env dosyası oluşturuluyor...")
    
    default_env_content = """# Zeppelin Betting Game - Environment Variables
# Bu dosyayı düzenleyin ve kendi değerlerinizi girin

# Veritabanı Bağlantısı (PostgreSQL kurulduktan sonra düzenleyin)
DATABASE_URL=postgresql://zeppelin_user:your_password@localhost:5432/zeppelin_game

# Flask Session Security (güvenli bir değer girin)
SESSION_SECRET=zeppelin-game-secret-key-123456789

# Kick API Credentials (Opsiyonel - yoksa mock modda çalışır)
KICK_CLIENT_ID=your-kick-client-id
KICK_CLIENT_SECRET=your-kick-client-secret

# Debug Mode
FLASK_ENV=development
FLASK_DEBUG=1
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(default_env_content)
    
    print("✅ .env dosyası oluşturuldu")
    print("📝 Lütfen .env dosyasını açın ve veritabanı bilgilerinizi düzenleyin")
    
    # Varsayılan değerleri yükle
    os.environ['DATABASE_URL'] = 'postgresql://zeppelin_user:your_password@localhost:5432/zeppelin_game'
    os.environ['SESSION_SECRET'] = 'zeppelin-game-secret-key-123456789'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'

# Gerekli paketleri kontrol et
def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'flask_socketio', 'flask_sqlalchemy', 
        'psycopg2', 'requests', 'sqlalchemy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Eksik paketler: {', '.join(missing_packages)}")
        print("Şu komutu çalıştırın:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)
    else:
        print("✅ Tüm gerekli paketler mevcut")

# Veritabanı bağlantısını kontrol et
def check_database():
    """Check database connection"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL çevre değişkeni bulunamadı")
        print("Örnek: DATABASE_URL=postgresql://user:password@localhost:5432/dbname")
        return False
    
    # PostgreSQL bağlantısını dene
    if database_url.startswith('postgresql://'):
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            conn.close()
            print("✅ PostgreSQL veritabanı bağlantısı başarılı")
            return True
        except ImportError:
            print("❌ psycopg2 paketi bulunamadı")
            print("Kurulum: pip install psycopg2-binary")
            return False
        except Exception as e:
            print(f"❌ PostgreSQL bağlantısı başarısız: {e}")
            print("🔄 SQLite ile devam edilecek (geliştirme modu)")
            # SQLite fallback
            os.environ['DATABASE_URL'] = 'sqlite:///zeppelin_game.db'
            return True
    
    # SQLite için kontrol
    elif database_url.startswith('sqlite://'):
        print("✅ SQLite veritabanı kullanılacak (geliştirme modu)")
        return True
    
    else:
        print(f"❌ Desteklenmeyen veritabanı türü: {database_url}")
        return False

# Yapılandırma kontrolü
def check_configuration():
    """Check configuration"""
    required_vars = ['DATABASE_URL', 'SESSION_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Eksik çevre değişkenleri: {', '.join(missing_vars)}")
        print("Lütfen .env dosyasını oluşturun veya çevre değişkenlerini ayarlayın")
        return False
    
    print("✅ Yapılandırma tamam")
    return True

def main():
    """Main function to run the application"""
    print("🚀 Zeppelin Betting Game - Local Development")
    print("=" * 50)
    
    # .env dosyasını yükle
    load_env()
    
    # Gereksinimleri kontrol et
    check_requirements()
    
    # Yapılandırmayı kontrol et
    if not check_configuration():
        sys.exit(1)
    
    # Veritabanını kontrol et
    if not check_database():
        print("\n💡 Veritabanı kurulumu için INSTALLATION.md dosyasını okuyun")
        sys.exit(1)
    
    print("\n🎮 Oyun başlatılıyor...")
    print("🌐 Tarayıcıda açın: http://localhost:5000")
    print("⚙️  Admin panel: http://localhost:5000/admin")
    print("🛑 Durdurmak için Ctrl+C")
    print("=" * 50)
    
    # Uygulamayı başlat
    try:
        from main import app, socketio
        socketio.run(app, host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n👋 Oyun kapatılıyor...")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("Detaylar için INSTALLATION.md dosyasını kontrol edin")
        sys.exit(1)

if __name__ == '__main__':
    main()