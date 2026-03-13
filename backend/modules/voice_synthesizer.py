"""
Modül: Seslendirme
Edge-TTS ile metni son derece gerçekçi sese dönüştürür.
"""

import os
import sys
import asyncio
import edge_tts

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import VIDEO_LANGUAGE

# Edge-TTS Ses Karakterleri
VOICE_TR = "tr-TR-AhmetNeural"  # veya tr-TR-EmelNeural
VOICE_EN = "en-US-ChristopherNeural"

def text_to_speech(text: str, output_path: str, language: str = None) -> str:
    """
    Edge-TTS kullanarak metni ses dosyasına kaydeder.
    """
    lang = language or VIDEO_LANGUAGE
    voice = VOICE_TR if lang == "tr" else VOICE_EN

    print(f"[SES] Edge-TTS başlatıldı. Ses: {voice}")
    
    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        await communicate.save(output_path)

    asyncio.run(_generate())
    print(f"[✓] Ses oluşturuldu (Edge-TTS): {output_path}")
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
        "Merhaba! Bu bir test seslendirmesidir. Edge-TTS çok daha doğal bir insan sesi sunar.",
        "output/test_audio.mp3",
        "tr"
    )
