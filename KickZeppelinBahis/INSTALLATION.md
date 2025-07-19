# Kendi Bilgisayarınızda Kurulum Rehberi

Bu rehber size Zeppelin Betting Game'i kendi bilgisayarınızda nasıl kuracağınızı gösterir.

## 1. Ön Gereksinimler

### Python Kurulumu
- **Windows**: [python.org](https://www.python.org/downloads/) üzerinden Python 3.11+ indirin
- **macOS**: `brew install python@3.11` veya App Store'dan
- **Ubuntu/Debian**: `sudo apt-get install python3.11 python3.11-pip`

### PostgreSQL Kurulumu

#### Windows
1. [PostgreSQL resmi sitesi](https://www.postgresql.org/download/windows/)nden indirin
2. Kurulum sırasında şifre belirleyin (unutmayın!)
3. Port 5432'yi kullanın (varsayılan)

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## 2. Proje Dosyalarını İndirin

### GitHub'dan İndirme
1. Replit projesini GitHub'a aktar
2. Terminal açın ve şu komutu çalıştırın:

```bash
git clone https://github.com/YOUR_USERNAME/zeppelin-betting-game.git
cd zeppelin-betting-game
```

### Zip Dosyası İle
1. Projeyi zip olarak indirin
2. Bir klasöre çıkarın
3. Terminal/CMD ile o klasöre gidin

## 3. Sanal Ortam Oluşturun

```bash
# Sanal ortam oluşturun
python -m venv zeppelin_env

# Sanal ortamı aktifleştirin
# Windows:
zeppelin_env\Scripts\activate

# macOS/Linux:
source zeppelin_env/bin/activate
```

## 4. Bağımlılıkları Yükleyin

```bash
# Temel paketleri yükleyin
pip install flask flask-socketio flask-sqlalchemy gunicorn psycopg2-binary requests sqlalchemy trafilatura email-validator
```

Veya setup.py kullanarak:
```bash
pip install -e .
```

## 5. Veritabanını Hazırlayın

### PostgreSQL Veritabanı Oluşturun

```bash
# PostgreSQL'e bağlanın
psql -U postgres

# Veritabanı ve kullanıcı oluşturun
CREATE DATABASE zeppelin_game;
CREATE USER zeppelin_user WITH ENCRYPTED PASSWORD 'güçlü_şifre_123';
GRANT ALL PRIVILEGES ON DATABASE zeppelin_game TO zeppelin_user;
\q
```

## 6. Çevre Değişkenlerini Ayarlayın

### Windows (.env dosyası oluşturun)
```bash
echo DATABASE_URL=postgresql://zeppelin_user:güçlü_şifre_123@localhost:5432/zeppelin_game > .env
echo SESSION_SECRET=çok-güçlü-gizli-anahtar-burada >> .env
echo KICK_CLIENT_ID=your-kick-client-id >> .env  
echo KICK_CLIENT_SECRET=your-kick-client-secret >> .env
```

### macOS/Linux
```bash
export DATABASE_URL="postgresql://zeppelin_user:güçlü_şifre_123@localhost:5432/zeppelin_game"
export SESSION_SECRET="çok-güçlü-gizli-anahtar-burada"
export KICK_CLIENT_ID="your-kick-client-id"
export KICK_CLIENT_SECRET="your-kick-client-secret"
```

### .env Dosyası Kullanımı (Önerilen)
Proje klasörünüzde `.env` dosyası oluşturun:

```env
DATABASE_URL=postgresql://zeppelin_user:güçlü_şifre_123@localhost:5432/zeppelin_game
SESSION_SECRET=çok-güçlü-gizli-anahtar-burada-12345
KICK_CLIENT_ID=your-kick-client-id
KICK_CLIENT_SECRET=your-kick-client-secret
```

## 7. Kick API Ayarları

### Kick Developer Hesabı
1. [Kick Developer Portal](https://kick.com/developer)a gidin
2. Yeni uygulama oluşturun
3. Client ID ve Client Secret alın
4. Bu bilgileri `.env` dosyasına ekleyin

**Not**: Kick API erişimi yoksa mock modda çalışır.

## 8. Uygulamayı Çalıştırın

### Geliştirme Modu
```bash
python main.py
```

### Prodüksiyon Modu (Daha Hızlı)
```bash
gunicorn --bind 127.0.0.1:5000 --workers 2 main:app
```

## 9. Tarayıcıda Açın

- **Ana Oyun**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin

## Sorun Giderme

### Hata: "psycopg2 kurulumu başarısız"
**Windows**:
```bash
pip install psycopg2-binary
```

**macOS**: 
```bash
brew install libpq
pip install psycopg2-binary
```

**Linux**:
```bash
sudo apt-get install libpq-dev python3-dev
pip install psycopg2-binary
```

### Hata: "PostgreSQL bağlantısı başarısız"
1. PostgreSQL servisinin çalıştığını kontrol edin:
   - Windows: Services.msc > PostgreSQL
   - macOS: `brew services list | grep postgres`
   - Linux: `sudo systemctl status postgresql`

2. Bağlantı URL'sini kontrol edin
3. Şifre ve kullanıcı adını doğrulayın

### Hata: "Port 5000 kullanımda"
Farklı port kullanın:
```bash
python main.py --port 8080
# veya
gunicorn --bind 127.0.0.1:8080 main:app
```

### Performans İyileştirmeleri

1. **Worker sayısını artırın**:
```bash
gunicorn --bind 127.0.0.1:5000 --workers 4 main:app
```

2. **Redis kurarak Socket.IO performansını artırın**:
```bash
# Redis kurulumu
# Windows: https://github.com/microsoftarchive/redis/releases
# macOS: brew install redis
# Linux: sudo apt-get install redis-server
```

3. **PostgreSQL ayarlarını optimize edin**:
PostgreSQL konfigürasyonunda:
```sql
-- postgresql.conf dosyasında
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
```

## Güvenlik

1. **.env dosyasını git'e eklemeyin**:
```bash
echo ".env" >> .gitignore
```

2. **Güçlü şifreler kullanın**
3. **Firewall ayarlarını kontrol edin**

## Otomatik Başlatma

### Windows (Startup)
1. Win+R > `shell:startup`
2. Batch dosyası oluşturun:
```batch
@echo off
cd /d "C:\path\to\zeppelin-betting-game"
call zeppelin_env\Scripts\activate
python main.py
pause
```

### macOS/Linux (systemd)
```ini
# /etc/systemd/system/zeppelin-game.service
[Unit]
Description=Zeppelin Betting Game
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/zeppelin-betting-game
Environment=DATABASE_URL=postgresql://...
ExecStart=/home/your-username/zeppelin-betting-game/zeppelin_env/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Servisi aktifleştirin:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zeppelin-game
sudo systemctl start zeppelin-game
```

## Yedekleme

```bash
# Veritabanı yedekleme
pg_dump -U zeppelin_user -h localhost zeppelin_game > backup.sql

# Geri yükleme
psql -U zeppelin_user -h localhost -d zeppelin_game -f backup.sql
```

Bu rehberi takip ederek Zeppelin Betting Game'i kendi bilgisayarınızda başarıyla çalıştırabilirsiniz!