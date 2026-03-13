# 🎬 YouTube Otomasyon Botu

Yüzünü göstermeden otomatik YouTube videoları üretip yayınlayan sistem.

## 🔄 Nasıl Çalışır?

```
Konu → Claude (Senaryo) → ElevenLabs (Ses) → Pexels (Görseller)
     → FFmpeg (Video) → Thumbnail → YouTube API (Yayın)
```

- **Türkçe video** → İngilizce altyazı otomatik eklenir
- **İngilizce video** → Türkçe altyazı otomatik eklenir
- **Haftada 3-4 video** otomatik olarak zamanlanır

---

## ⚙️ Kurulum (Adım Adım)

### 1. Python Kütüphanelerini Kur
```bash
pip install -r requirements.txt
```

### 2. FFmpeg Kur
```bash
# Windows: https://ffmpeg.org/download.html
# Mac:
brew install ffmpeg
# Linux:
sudo apt install ffmpeg
```

### 3. API Anahtarlarını Al

| Servis | Nereden? | Fiyat |
|--------|----------|-------|
| **Groq (Llama 3.3)** | console.groq.com | Tamamen ücretsiz ✅ |
| **ElevenLabs** | elevenlabs.io | Ücretsiz başlangıç |
| **Pexels** | pexels.com/api | Tamamen ücretsiz |
| **YouTube Data API** | console.cloud.google.com | Ücretsiz |

### 4. `.env` Dosyasını Oluştur
```bash
cp .env.example .env
```
Sonra `.env` dosyasını aç ve API anahtarlarını gir:
```
ANTHROPIC_API_KEY=sk-ant-gerçek_anahtarın
ELEVENLABS_API_KEY=gerçek_anahtarın
PEXELS_API_KEY=gerçek_anahtarın
```

> ⚠️ `.env` dosyası `.gitignore`'da zaten var — GitHub'a **asla** yüklenmez.

### 5. YouTube OAuth Kurulumu
1. [Google Cloud Console](https://console.cloud.google.com) → Yeni proje
2. "YouTube Data API v3" → Etkinleştir
3. OAuth 2.0 → Client ID oluştur (Desktop App)
4. JSON dosyasını indir → `config/client_secret.json` olarak kaydet
5. İlk çalıştırmada tarayıcı açılır, Google hesabını onayla

---

## 🚀 Kullanım

### Tek Video Üret (Manuel Konu)
```bash
python main.py "Yapay zeka nedir?"
```

### Otomatik Konu Seç
```bash
python main.py
```

### Zamanlayıcı Modunda Çalıştır (Haftada 3-4)
```bash
python main.py --schedule
```

---

## 📁 Proje Yapısı

```
youtube_bot/
├── main.py                    # Ana orkestratör
├── requirements.txt
├── config/
│   ├── settings.py            # Tüm ayarlar burada
│   ├── client_secret.json     # Google OAuth (sen ekleyeceksin)
│   └── token.pickle           # Otomatik oluşur
├── modules/
│   ├── content_generator.py   # Claude API → senaryo
│   ├── voice_synthesizer.py   # ElevenLabs → ses
│   ├── image_fetcher.py       # Pexels → görseller
│   ├── video_builder.py       # MoviePy → video
│   └── youtube_uploader.py    # YouTube API → yayın
├── output/                    # Üretilen dosyalar
└── logs/                      # İşlem kayıtları
```

---

## 🌍 Dil Ayarı

`config/settings.py` içinde:
```python
VIDEO_LANGUAGE = "tr"   # Türkçe video + İngilizce altyazı
VIDEO_LANGUAGE = "en"   # İngilizce video + Türkçe altyazı
```

---

## 📅 Zamanlama Ayarı

```python
SCHEDULE_DAYS = ["monday", "wednesday", "friday", "saturday"]
SCHEDULE_TIME = "10:00"
```

---

## 🐙 GitHub'a Atma (Güvenli)

```bash
git init
git add .
git commit -m "ilk commit"
git remote add origin https://github.com/KULLANICI_ADIN/youtube-bot.git
git push -u origin main
```

**GitHub'a gidecek dosyalar:** Tüm kod, `.env.example`, `README.md`
**GitHub'a GİTMEYECEK:** `.env`, `client_secret.json`, `token.pickle`, videolar

Başka birisi projeyi klonlarsa sadece şunu çalıştırır:
```bash
cp .env.example .env   # kendi anahtarlarını yazar
pip install -r requirements.txt
```

---

- **ElevenLabs ücretsiz limiti** aşılırsa sistem otomatik gTTS'e geçer
- **Pexels** tamamen ücretsiz ve sınırsız
- `TOPIC_LIST` listesini istediğin konularla doldur
- `YOUTUBE_PRIVACY = "private"` yaparak önce test edebilirsin
- Aylık maliyet tahmini: ~$5-10 (çoğunlukla Claude API)
