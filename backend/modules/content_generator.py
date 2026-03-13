"""
Modül: İçerik Üretici
Groq API (ücretsiz) kullanarak video senaryosu, başlık, açıklama ve altyazı üretir.
Model: llama-3.3-70b-versatile — Türkçe desteği güçlü, çok hızlı
"""

import json
import sys
import os
from groq import Groq
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import GROQ_API_KEY, VIDEO_LANGUAGE


client = Groq(api_key=GROQ_API_KEY)

# Groq model seçenekleri:
#   llama-3.3-70b-versatile  → En iyi kalite, Türkçe güçlü (önerilen)
#   llama-3.1-8b-instant     → Daha hızlı, biraz daha düşük kalite
#   mixtral-8x7b-32768       → Uzun metinler için iyi
GROQ_MODEL = "llama-3.3-70b-versatile"


def generate_script(topic: str) -> dict:
    """
    Verilen konuya göre tam video içeriği üretir.
    Döndürür: title, description, script, slides, subtitle_translation, tags
    """
    lang = VIDEO_LANGUAGE
    is_tr = lang == "tr"

    video_lang   = "Türkçe" if is_tr else "İngilizce"
    sub_lang     = "İngilizce" if is_tr else "Türkçe"

    prompt = (
        f'Sen bir YouTube eğitim kanalı için içerik üreticisisin.\n'
        f'Konu: "{topic}"\n'
        f'Video dili: {video_lang}\n\n'
        f'Aşağıdaki JSON formatında içerik üret. SADECE JSON döndür, '
        f'başka hiçbir şey yazma, kod bloğu kullanma:\n\n'
        '{\n'
        f'  "title": "{video_lang} video başlığı (max 70 karakter, SEO uyumlu)",\n'
        f'  "description": "{video_lang} video açıklaması (300-500 karakter)",\n'
        '  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],\n'
        f'  "script": "Tam anlatım metni ({video_lang}, doğal ve akıcı, ~500 kelime)",\n'
        '  "slides": [\n'
        '    {\n'
        '      "title": "Slayt başlığı",\n'
        '      "text": "Kısa açıklama (max 2 cümle)",\n'
        '      "image_query": "Pexels için İngilizce arama terimi"\n'
        '    }\n'
        '  ],\n'
        f'  "subtitle_translation": "Senaryonun {sub_lang} çevirisi (altyazı için)"\n'
        '}\n\n'
        'Slides: 6-8 slayt olsun. Script: slaytlarla uyumlu, eğitici olsun.'
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Sen bir YouTube içerik üreticisisin. "
                    "Her zaman geçerli JSON formatında yanıt verirsin. "
                    "Kod bloğu, açıklama veya ek metin kullanmazsın."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()

    # Model yine de kod bloğu kullandıysa temizle
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    data["language"] = lang
    data["topic"] = topic
    return data


def generate_srt(script: str, language: str, duration_per_line: float = 4.0) -> str:
    """Senaryo metninden SRT altyazı dosyası oluşturur."""
    sentences = [s.strip() for s in script.replace("\n", " ").split(".") if len(s.strip()) > 10]

    srt_lines = []
    current_time = 0.0

    for i, sentence in enumerate(sentences, 1):
        start = current_time
        end = current_time + duration_per_line
        srt_lines.append(f"{i}")
        srt_lines.append(f"{_seconds_to_srt_time(start)} --> {_seconds_to_srt_time(end)}")
        srt_lines.append(sentence + ".")
        srt_lines.append("")
        current_time = end

    return "\n".join(srt_lines)


def _seconds_to_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


if __name__ == "__main__":
    result = generate_script("Yapay zeka nedir?")
    print(json.dumps(result, ensure_ascii=False, indent=2))
