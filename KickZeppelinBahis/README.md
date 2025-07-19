# Zeppelin Betting Game

Kick streaming platformu ile entegre çalışan gerçek zamanlı bahis oyunu.

## Özellikler

- **Gerçek Zamanlı Oyun**: Socket.IO ile canlı oyun deneyimi
- **Kick API Entegrasyonu**: Gerçek Kick API desteği
- **Türkçe Arayüz**: Tamamen Türkçe dil desteği
- **Admin Panel**: Dinamik kanal yönetimi ve oyun ayarları
- **PostgreSQL Veritabanı**: Güvenli ve hızlı veri saklama
- **Streaming Odaklı**: 3D görsel efektler ve yayın dostu tasarım

## Gereksinimler

- Python 3.11+
- PostgreSQL
- Kick API kimlik bilgileri

## Kurulum

1. **Repoyu klonlayın**:
```bash
git clone <repo-url>
cd zeppelin-betting-game
```

2. **Sanal ortam oluşturun**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları yükleyin**:
```bash
pip install -r requirements.txt
```

4. **PostgreSQL kurulumu**:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

5. **Veritabanı oluşturun**:
```sql
CREATE DATABASE zeppelin_game;
CREATE USER zeppelin_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE zeppelin_game TO zeppelin_user;
```

6. **Çevre değişkenlerini ayarlayın**:
```bash
export DATABASE_URL="postgresql://zeppelin_user:your_password@localhost/zeppelin_game"
export SESSION_SECRET="your-secret-key-here"
export KICK_CLIENT_ID="your-kick-client-id"
export KICK_CLIENT_SECRET="your-kick-client-secret"
```

7. **Uygulamayı çalıştırın**:
```bash
# Geliştirme modu
python main.py

# Prodüksiyon modu
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Kullanım

1. **Ana Oyun**: `http://localhost:5000`
2. **Admin Panel**: `http://localhost:5000/admin`

### Chat Komutları

- `!bet <miktar> <çarpan>` - Bahis oyna
- `!bakiye` - Bakiye kontrol et
- `!yardim` - Yardım menüsü

### Admin Panel

- **Kanal Yönetimi**: Kick kanalını dinamik olarak değiştirme
- **Oyun Ayarları**: Kazanma oranı ve çarpan limitlerini ayarlama
- **İstatistikler**: Gerçek zamanlı kullanıcı ve oyun istatistikleri

## Kick API Kurulumu

1. [Kick Developer Portal](https://kick.com/developer) üzerinden uygulama oluşturun
2. Client ID ve Client Secret alın
3. Çevre değişkenlerini ayarlayın

## Proje Yapısı

```
├── app.py              # Ana Flask uygulaması
├── main.py             # Uygulama giriş noktası
├── models.py           # Veritabanı modelleri
├── database_manager.py # Veritabanı işlemleri
├── game_logic.py       # Oyun mekaniği
├── kick_api.py         # Kick API entegrasyonu
├── templates/          # HTML şablonları
│   ├── index.html      # Ana oyun sayfası
│   └── admin.html      # Admin panel
└── static/             # CSS ve JavaScript dosyaları
```

## Konfigürasyon

### Oyun Ayarları

- **Kazanma Oranı**: %35 (varsayılan)
- **Min Çarpan**: 1.0x
- **Max Çarpan**: 50.0x
- **Abone Bonusu**: 100+ abone için 1000 puan

### Veritabanı Ayarları

- **Connection Pool**: 300 saniye yaşam süresi
- **Pre-ping**: Bağlantı kontrolü aktif
- **Auto-commit**: Kapalı (manuel transaction yönetimi)

## Geliştirme

### Debug Modu

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python main.py
```

### Test Komutları

Tarayıcı konsolunda:
- `simulateFollow()` - Takip simülasyonu
- `placeBet()` - Bahis simülasyonu
- `simulateChat("!bet 100 2.5")` - Chat komutu testi

## Üretim Dağıtımı

### Nginx Konfigürasyonu

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /socket.io {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Servisi

```ini
[Unit]
Description=Zeppelin Betting Game
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/zeppelin-betting-game
Environment=DATABASE_URL=postgresql://...
Environment=SESSION_SECRET=...
Environment=KICK_CLIENT_ID=...
Environment=KICK_CLIENT_SECRET=...
ExecStart=/path/to/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Sorun Giderme

### Yaygın Sorunlar

1. **Veritabanı Bağlantısı**: DATABASE_URL formatını kontrol edin
2. **Socket.IO Hatası**: Firewall ayarlarını kontrol edin
3. **Kick API**: Client kimlik bilgilerini doğrulayın

### Loglar

```bash
# Uygulama logları
tail -f /var/log/zeppelin-game.log

# Nginx logları
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## Destek

Sorularınız için issue açabilirsiniz.