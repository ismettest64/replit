# 🚀 ZEPPELİN BETTING GAME - HIZLI BAŞLATMA

Kendi bilgisayarınızda 5 dakikada oyunu çalıştırın!

## ⚡ Süper Hızlı Kurulum

### 1. Python Kurulumu
- **Windows**: https://python.org/downloads - Python 3.8+ indirin
- **macOS**: Terminal'de `brew install python` 
- **Linux**: `sudo apt install python3 python3-pip`

### 2. Proje Dosyalarını İndirin
- Bu projeyi ZIP olarak indirin
- Bir klasöre çıkartın
- Terminal/CMD ile o klasöre gidin

### 3. Tek Komutla Başlatın
```bash
python quick_start.py
```

Bu komut:
- ✅ Gerekli paketleri otomatik kurar
- ✅ Ayar dosyasını oluşturur
- ✅ SQLite veritabanını hazırlar
- ✅ Oyunu test eder

### 4. Oyunu Çalıştırın
```bash
python quick_start.py run
```

### 5. Tarayıcıda Açın
- **Ana Oyun**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin

## 🎯 Hızlı Test

Tarayıcı konsolunda (F12):
```javascript
// Kullanıcı simülasyonu
simulateFollow()

// Bahis simülasyonu  
placeBet()

// Chat komutu
simulateChat("!bet 100 2.5")
```

## 🔧 Sorun Çözümleri

### "Python bulunamadı" Hatası
```bash
# Windows'ta PATH'e Python ekleyin
# veya python yerine py kullanın:
py quick_start.py
```

### "Paket kurulumu başarısız" Hatası
```bash
# Manuel kurulum:
pip install flask flask-socketio flask-sqlalchemy requests sqlalchemy
```

### "Port kullanımda" Hatası
```bash
# Farklı port kullanın:
python quick_start.py run --port 8080
```

## 📋 Gelişmiş Kurulum

Daha fazla özellik için:
1. **PostgreSQL** kurulumu → `INSTALLATION.md`
2. **Kick API** entegrasyonu → `README.md`
3. **Prodüksiyon** dağıtımı → `README.md`

## 🎮 Oyun Özellikler

- **Gerçek Zamanlı**: Socket.IO ile canlı oyun
- **Türkçe Arayüz**: Tamamen Türkçe
- **Admin Panel**: Kanal ve ayar yönetimi
- **3D Efektler**: Streaming dostu görsel efektler
- **Chat Komutları**: !bet, !bakiye, !yardim

## 🚀 Başarılı Kurulum Sonrası

1. Admin panelden kanal ayarlayın
2. Oyun ayarlarını düzenleyin
3. Test kullanıcıları oluşturun
4. Canlı yayında test edin

**Hızlı başlatma başarısızsa → `INSTALLATION.md` dosyasını okuyun**