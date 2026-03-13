"""
Modül: Görsel İndirici
Pexels API'den konuya uygun ücretsiz görseller indirir.
"""

import os
import sys
import requests
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import PEXELS_API_KEY, VIDEO_WIDTH, VIDEO_HEIGHT


def fetch_images(queries: list, output_dir: str) -> list:
    """
    Her sorgu için Pexels'tan bir görsel indirir.
    Döndürür: indirilen dosya yolları listesi
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []

    for i, query in enumerate(queries):
        path = os.path.join(output_dir, f"slide_{i:02d}.jpg")
        try:
            result = _download_pexels_image(query, path)
            image_paths.append(result)
            print(f"[✓] Görsel indirildi [{i+1}/{len(queries)}]: {query}")
        except Exception as e:
            print(f"[UYARI] Görsel indirilemedi '{query}': {e}. Varsayılan kullanılıyor.")
            fallback = _create_fallback_image(query, path)
            image_paths.append(fallback)

    return image_paths


def _download_pexels_image(query: str, output_path: str) -> str:
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": "landscape",
        "size": "large",
        "per_page": 10
    }

    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    data = response.json()

    photos = data.get("photos", [])
    if not photos:
        raise ValueError(f"Sonuç bulunamadı: {query}")

    photo = random.choice(photos[:5])
    img_url = photo["src"]["large2x"]

    img_response = requests.get(img_url, timeout=30)
    img_response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(img_response.content)

    return output_path


def _create_fallback_image(text: str, output_path: str) -> str:
    """Pexels başarısız olursa düz renkli görsel oluşturur"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color=(30, 30, 50))
        draw = ImageDraw.Draw(img)

        # Ortaya metin yaz
        font_size = 60
        try:
            from config.settings import FONT_PATH
            font = ImageFont.truetype(FONT_PATH, font_size)
        except Exception:
            font = ImageFont.load_default()

        draw.text(
            (VIDEO_WIDTH // 2, VIDEO_HEIGHT // 2),
            text[:50],
            font=font,
            fill=(220, 220, 255),
            anchor="mm"
        )
        img.save(output_path)
    except Exception:
        # En basit fallback: boş görsel
        with open(output_path, "wb") as f:
            f.write(b"")

    return output_path


if __name__ == "__main__":
    paths = fetch_images(
        ["artificial intelligence technology", "science education"],
        "output/test_images"
    )
    print("İndirilen görseller:", paths)
