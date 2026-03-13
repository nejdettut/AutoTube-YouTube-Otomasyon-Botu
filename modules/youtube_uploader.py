"""
Modül: YouTube Yükleyici
YouTube Data API v3 kullanarak video yükler ve meta bilgileri ayarlar.
"""

import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_CATEGORY_ID,
    YOUTUBE_PRIVACY, YOUTUBE_TAGS_TR, YOUTUBE_TAGS_EN, VIDEO_LANGUAGE
)


def upload_video(
    video_path: str,
    thumbnail_path: str,
    title: str,
    description: str,
    tags: list = None,
    language: str = None
) -> str:
    """
    Videoyu YouTube'a yükler.
    Döndürür: YouTube video ID'si
    """
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle

    lang = language or VIDEO_LANGUAGE
    extra_tags = YOUTUBE_TAGS_TR if lang == "tr" else YOUTUBE_TAGS_EN
    final_tags = (tags or []) + extra_tags

    # OAuth kimlik doğrulama
    youtube = _get_youtube_service()

    # Video yükleme isteği
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": final_tags[:30],  # YouTube max 30 tag
            "categoryId": YOUTUBE_CATEGORY_ID,
            "defaultLanguage": lang,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY,
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5  # 5MB chunk
    )

    print(f"[↑] Video yükleniyor: {title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"    Yükleme: {pct}%", end="\r")

    video_id = response["id"]
    print(f"\n[✓] Video yüklendi! ID: {video_id}")
    print(f"    URL: https://www.youtube.com/watch?v={video_id}")

    # Thumbnail yükle
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            print(f"[✓] Thumbnail yüklendi.")
        except Exception as e:
            print(f"[UYARI] Thumbnail yüklenemedi: {e}")

    return video_id


def _get_youtube_service():
    """OAuth2 ile YouTube servisini başlatır. Token'ı kaydeder."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube"]
    TOKEN_FILE = "config/token.pickle"
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


if __name__ == "__main__":
    print("YouTube uploader modülü hazır.")
    print("İlk çalıştırmada tarayıcı açılarak Google hesabı onayı istenecek.")
