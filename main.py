"""
ANA ORKESTRATÖR
Tüm modülleri sırayla çalıştırarak bir videoyu baştan sona üretir ve yayınlar.

Kullanım:
  python main.py                          # Otomatik konu seçer
  python main.py "Kuantum fiziği nedir?"  # Manuel konu
  python main.py --schedule               # Zamanlayıcı modunda çalıştır
"""

import os
import sys
import json
import argparse
import random
import datetime
import traceback

# Modülleri import et
from config.settings import TOPIC_LIST, VIDEO_LANGUAGE, SCHEDULE_DAYS, SCHEDULE_TIME
from modules.content_generator import generate_script, generate_srt
from modules.voice_synthesizer import text_to_speech, get_audio_duration
from modules.image_fetcher import fetch_images
from modules.video_builder import build_video, create_thumbnail
from modules.youtube_uploader import upload_video


def run_pipeline(topic: str = None) -> dict:
    """
    Verilen konuya göre tam pipeline'ı çalıştırır.
    """
    if not topic:
        topic = random.choice(TOPIC_LIST)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = f"output/{timestamp}"
    os.makedirs(work_dir, exist_ok=True)

    log = {"topic": topic, "timestamp": timestamp, "steps": {}}

    print(f"\n{'='*60}")
    print(f"  YouTube Otomasyon Botu Başladı")
    print(f"  Konu: {topic}")
    print(f"  Dil: {VIDEO_LANGUAGE}")
    print(f"{'='*60}\n")

    # ─── ADIM 1: İçerik Üret ────────────────────────────────
    print("[1/6] Senaryo ve içerik üretiliyor...")
    try:
        content = generate_script(topic)
        with open(f"{work_dir}/content.json", "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        log["steps"]["content"] = "✓"
        print(f"      Başlık: {content['title']}")
    except Exception as e:
        _fail("İçerik üretimi", e, log)
        return log

    # ─── ADIM 2: Seslendirme ────────────────────────────────
    print("[2/6] Seslendirme oluşturuluyor...")
    audio_path = f"{work_dir}/audio.mp3"
    try:
        text_to_speech(content["script"], audio_path, VIDEO_LANGUAGE)
        duration = get_audio_duration(audio_path)
        log["steps"]["audio"] = f"✓ ({duration:.0f}s)"
        print(f"      Ses süresi: {duration:.0f} saniye")
    except Exception as e:
        _fail("Seslendirme", e, log)
        return log

    # ─── ADIM 3: Altyazı ────────────────────────────────────
    print("[3/6] Altyazı oluşturuluyor...")
    subtitle_lang = "en" if VIDEO_LANGUAGE == "tr" else "tr"
    subtitle_text = content.get("subtitle_translation", "")
    srt_path = f"{work_dir}/subtitle_{subtitle_lang}.srt"
    try:
        srt_content = generate_srt(subtitle_text, subtitle_lang)
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        log["steps"]["subtitle"] = f"✓ ({subtitle_lang.upper()})"
        print(f"      Altyazı dili: {subtitle_lang.upper()}")
    except Exception as e:
        print(f"[UYARI] Altyazı oluşturulamadı: {e}")
        subtitle_text = ""

    # ─── ADIM 4: Görseller ──────────────────────────────────
    print("[4/6] Görseller indiriliyor...")
    image_dir = f"{work_dir}/images"
    queries = [s.get("image_query", topic) for s in content.get("slides", [])]
    if not queries:
        queries = [topic] * 6
    try:
        image_paths = fetch_images(queries, image_dir)
        log["steps"]["images"] = f"✓ ({len(image_paths)} görsel)"
    except Exception as e:
        _fail("Görsel indirme", e, log)
        return log

    # ─── ADIM 5: Video Üret ─────────────────────────────────
    print("[5/6] Video oluşturuluyor...")
    video_path = f"{work_dir}/video.mp4"
    thumbnail_path = f"{work_dir}/thumbnail.jpg"
    try:
        build_video(
            image_paths=image_paths,
            audio_path=audio_path,
            subtitle_text=subtitle_text,
            subtitle_lang=subtitle_lang,
            output_path=video_path,
            slide_data=content.get("slides", [])
        )
        # Thumbnail
        create_thumbnail(content["title"], image_paths[0], thumbnail_path)
        log["steps"]["video"] = "✓"
    except Exception as e:
        _fail("Video üretimi", e, log)
        return log

    # ─── ADIM 6: YouTube'a Yükle ────────────────────────────
    print("[6/6] YouTube'a yükleniyor...")
    try:
        video_id = upload_video(
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=content["title"],
            description=content["description"],
            tags=content.get("tags", []),
            language=VIDEO_LANGUAGE
        )
        log["steps"]["upload"] = f"✓ ID: {video_id}"
        log["youtube_url"] = f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        _fail("YouTube yükleme", e, log)
        return log

    print(f"\n{'='*60}")
    print(f"  ✅ TAMAMLANDI!")
    print(f"  URL: {log.get('youtube_url', 'N/A')}")
    print(f"{'='*60}\n")

    # Log kaydet
    with open(f"{work_dir}/log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    return log


def _fail(step: str, error: Exception, log: dict):
    print(f"\n[✗] HATA - {step}: {error}")
    traceback.print_exc()
    log["steps"][step] = f"✗ {error}"


def run_scheduler():
    """Zamanlayıcı modunda çalışır - belirlenen günlerde otomatik yayınlar"""
    import schedule
    import time

    day_map = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday,
    }

    for day in SCHEDULE_DAYS:
        day_map[day.lower()].at(SCHEDULE_TIME).do(run_pipeline)
        print(f"[⏰] Zamanlandı: Her {day} saat {SCHEDULE_TIME}")

    print(f"\n[▶] Zamanlayıcı çalışıyor... (Ctrl+C ile durdur)\n")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Otomasyon Botu")
    parser.add_argument("topic", nargs="?", help="Video konusu (opsiyonel)")
    parser.add_argument("--schedule", action="store_true", help="Zamanlayıcı modunda çalıştır")
    args = parser.parse_args()

    if args.schedule:
        run_scheduler()
    else:
        run_pipeline(args.topic)
