# ============================================================
#  config/settings.py — Tüm ayarlar .env'den okunur
#  API anahtarlarını buraya YAZMA, .env dosyasına yaz!
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Proje kök dizinindeki .env dosyasını yükle
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _require(key: str) -> str:
    """Zorunlu env değişkenini okur, yoksa hata verir."""
    val = os.getenv(key)
    if not val or val.startswith("BURAYA_YAZ"):
        raise EnvironmentError(
            f"\n\n[!] '{key}' ayarlanmamış!\n"
            f"    .env.example dosyasını kopyala:\n"
            f"    cp .env.example .env\n"
            f"    Sonra .env içine gerçek değeri yaz.\n"
        )
    return val


# --- API ANAHTARLARI ---
GROQ_API_KEY = _require("GROQ_API_KEY")
ELEVENLABS_API_KEY         = _require("ELEVENLABS_API_KEY")
PEXELS_API_KEY             = _require("PEXELS_API_KEY")
YOUTUBE_CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "config/client_secret.json")

# --- DİL AYARLARI ---
VIDEO_LANGUAGE = os.getenv("VIDEO_LANGUAGE", "tr")   # "tr" veya "en"

# --- ELEVENLABS SES AYARLARI ---
VOICE_ID_TR         = os.getenv("VOICE_ID_TR", "pNInz6obpgDQGcFmaJgB")
VOICE_ID_EN         = os.getenv("VOICE_ID_EN", "21m00Tcm4TlvDq8ikWAM")
VOICE_STABILITY     = float(os.getenv("VOICE_STABILITY", "0.5"))
VOICE_SIMILARITY    = float(os.getenv("VOICE_SIMILARITY", "0.8"))

# --- VİDEO AYARLARI ---
VIDEO_WIDTH     = 1920
VIDEO_HEIGHT    = 1080
VIDEO_FPS       = 24
SLIDE_DURATION  = 6
FONT_PATH       = "C:\\Windows\\Fonts\\arialbd.ttf"

# --- YOUTUBE AYARLARI ---
YOUTUBE_CATEGORY_ID = "27"   # 27 = Education
YOUTUBE_PRIVACY     = os.getenv("YOUTUBE_PRIVACY", "public")
YOUTUBE_TAGS_TR     = ["eğitim", "bilgi", "öğren", "türkçe", "youtube"]
YOUTUBE_TAGS_EN     = ["education", "learn", "knowledge", "english", "youtube"]

# --- ZAMANLAMA ---
SCHEDULE_DAYS = ["monday", "wednesday", "friday", "saturday"]
SCHEDULE_TIME = "10:00"

# --- İÇERİK KONULARI ---
TOPIC_LIST = [
    "Yapay zeka nedir ve nasıl çalışır?",
    "Kuantum bilgisayarlar nasıl çalışır?",
    "Beyin nasıl öğrenir?",
    "İklim değişikliğinin nedenleri",
    "Uzay keşfinin geleceği",
    "DNA ve genetik mühendisliği",
    "Blockchain teknolojisi",
    "Nöroloji: Bellek nasıl oluşur?",
    "Güneş enerjisi nasıl çalışır?",
    "Derin denizlerin gizemleri",
]
