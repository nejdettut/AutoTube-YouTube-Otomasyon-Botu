"""
Modül: Seslendirme
ElevenLabs API ile metni sese dönüştürür.
gTTS (ücretsiz) yedek olarak kullanılır.
"""

import os
import sys
import requests
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    ELEVENLABS_API_KEY, VOICE_ID_TR, VOICE_ID_EN,
    VOICE_STABILITY, VOICE_SIMILARITY, VIDEO_LANGUAGE
)


def text_to_speech(text: str, output_path: str, language: str = None) -> str:
    """
    Metni sese çevirir. ElevenLabs başarısız olursa gTTS'e geçer.
    Döndürür: ses dosyasının yolu
    """
    lang = language or VIDEO_LANGUAGE
    voice_id = VOICE_ID_TR if lang == "tr" else VOICE_ID_EN

    try:
        return _elevenlabs_tts(text, output_path, voice_id)
    except Exception as e:
        print(f"[UYARI] ElevenLabs başarısız: {e}. gTTS'e geçiliyor...")
        return _gtts_tts(text, output_path, lang)


def _elevenlabs_tts(text: str, output_path: str, voice_id: str) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": VOICE_STABILITY,
            "similarity_boost": VOICE_SIMILARITY
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"[✓] Ses oluşturuldu (ElevenLabs): {output_path}")
    return output_path


def _gtts_tts(text: str, output_path: str, language: str) -> str:
    """Ücretsiz Google TTS yedek"""
    from gtts import gTTS
    lang_code = "tr" if language == "tr" else "en"
    tts = gTTS(text=text, lang=lang_code, slow=False)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tts.save(output_path)
    print(f"[✓] Ses oluşturuldu (gTTS): {output_path}")
    return output_path


def get_audio_duration(audio_path: str) -> float:
    """Ses dosyasının süresini saniye olarak döndürür"""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
    except Exception:
        return 180.0  # Varsayılan 3 dakika


if __name__ == "__main__":
    text_to_speech(
        "Merhaba! Bu bir test seslendirmesidir.",
        "output/test_audio.mp3",
        "tr"
    )
