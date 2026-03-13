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
import random
import datetime
import traceback
import threading
import uuid

import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Modülleri import et
from config.settings import TOPIC_LIST, VIDEO_LANGUAGE
from modules.content_generator import generate_script, generate_srt
from modules.voice_synthesizer import text_to_speech, get_audio_duration
from modules.image_fetcher import fetch_images
from modules.video_builder import build_video, create_thumbnail
from modules.youtube_uploader import upload_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output", exist_ok=True)
app.mount("/output", StaticFiles(directory="output"), name="output")

JOBS = {}

class VideoRequest(BaseModel):
    topic: str

def run_pipeline(topic: str, job_id: str):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = f"output/{timestamp}"
    os.makedirs(work_dir, exist_ok=True)

    log = {"topic": topic, "timestamp": timestamp, "steps": {}}
    JOBS[job_id]["status"] = "running"
    JOBS[job_id]["log"] = log

    def update_step(step_name, status_msg):
        log["steps"][step_name] = status_msg
        JOBS[job_id]["log"] = log

    # ─── ADIM 1: İçerik Üret ────────────────────────────────
    update_step("content", "üretiliyor...")
    try:
        content = generate_script(topic)
        with open(f"{work_dir}/content.json", "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        update_step("content", "✓")
        JOBS[job_id]["content"] = content
    except Exception as e:
        _fail("content", e, log, job_id)
        return

    # ─── ADIM 2: Seslendirme ────────────────────────────────
    update_step("audio", "oluşturuluyor...")
    audio_path = f"{work_dir}/audio.mp3"
    try:
        text_to_speech(content["script"], audio_path, VIDEO_LANGUAGE)
        duration = get_audio_duration(audio_path)
        update_step("audio", f"✓ ({duration:.0f}s)")
    except Exception as e:
        _fail("audio", e, log, job_id)
        return

    # ─── ADIM 3: Altyazı ────────────────────────────────────
    update_step("subtitle", "oluşturuluyor...")
    subtitle_lang = "en" if VIDEO_LANGUAGE == "tr" else "tr"
    subtitle_text = content.get("subtitle_translation", "")
    srt_path = f"{work_dir}/subtitle_{subtitle_lang}.srt"
    try:
        srt_content = generate_srt(subtitle_text, subtitle_lang)
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        update_step("subtitle", f"✓ ({subtitle_lang.upper()})")
    except Exception as e:
        update_step("subtitle", f"✗ ({e})")
        subtitle_text = ""

    # ─── ADIM 4: Görseller ──────────────────────────────────
    update_step("images", "indiriliyor...")
    image_dir = f"{work_dir}/images"
    queries = [s.get("image_query", topic) for s in content.get("slides", [])]
    if not queries:
        queries = [topic] * 6
    try:
        image_paths = fetch_images(queries, image_dir)
        update_step("images", f"✓ ({len(image_paths)} görsel)")
    except Exception as e:
        _fail("images", e, log, job_id)
        return

    # ─── ADIM 5: Video Üret ─────────────────────────────────
    update_step("video", "oluşturuluyor...")
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
        create_thumbnail(content["title"], image_paths[0], thumbnail_path)
        update_step("video", "✓")
        JOBS[job_id]["video_url"] = f"/output/{timestamp}/video.mp4"
    except Exception as e:
        _fail("video", e, log, job_id)
        return

    # ─── ADIM 6: YouTube'a Yükle ────────────────────────────
    update_step("upload", "yükleniyor...")
    try:
        video_id = upload_video(
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=content["title"],
            description=content["description"],
            tags=content.get("tags", []),
            language=VIDEO_LANGUAGE
        )
        update_step("upload", f"✓ ID: {video_id}")
        JOBS[job_id]["youtube_url"] = f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        update_step("upload", f"✗ (YouTube atlandı: {e})")
        pass

    JOBS[job_id]["status"] = "completed"

def _fail(step: str, error: Exception, log: dict, job_id: str):
    traceback.print_exc()
    log["steps"][step] = f"✗ {error}"
    JOBS[job_id]["status"] = "error"
    JOBS[job_id]["error"] = str(error)

@app.post("/api/generate")
def generate_video_endpoint(req: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    topic = req.topic if req.topic else random.choice(TOPIC_LIST)
    JOBS[job_id] = {"status": "starting", "topic": topic, "log": {"steps": {}}}
    
    background_tasks.add_task(run_pipeline, topic, job_id)
    return {"job_id": job_id, "message": "Video üretimi başlatıldı."}

@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
