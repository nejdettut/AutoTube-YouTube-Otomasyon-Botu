"""
Modül: Video Üretici
Görseller + ses + altyazı birleştirerek MP4 video oluşturur.
"""

import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, FONT_PATH


def build_video(
    image_paths: list,
    audio_path: str,
    subtitle_text: str,
    subtitle_lang: str,
    output_path: str,
    slide_data: list = None
) -> str:
    """
    Görseller + ses + altyazıdan tam video üretir.
    Döndürür: çıktı video dosyasının yolu
    """
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, TextClip, CompositeAudioClip
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Ses yükle
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Her slaytın süresi
    slide_duration = total_duration / max(len(image_paths), 1)

    # Görsel klipleri oluştur
    clips = []
    for i, img_path in enumerate(image_paths):
        duration = slide_duration
        if i == len(image_paths) - 1:
            duration = total_duration - (slide_duration * i)

        clip = (
            ImageClip(img_path)
            .set_duration(duration)
            .resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        )

        # Hafif zoom efekti (Ken Burns)
        clip = clip.resize(lambda t: 1 + 0.03 * (t / duration))

        # Slayt başlığı varsa üste ekle
        if slide_data and i < len(slide_data):
            title = slide_data[i].get("title", "")
            if title:
                txt = _make_title_clip(title, duration, VIDEO_WIDTH)
                if txt is not None:
                    clip = CompositeVideoClip([clip, txt])

        clips.append(clip)

    # Klipleri birleştir
    video = concatenate_videoclips(clips, method="compose")

    # Altyazı katmanı ekle
    video = _add_subtitle_overlay(video, subtitle_text, subtitle_lang, total_duration)

    # Sesi ekle
    video = video.set_audio(audio)

    # Render
    video.write_videofile(
        output_path,
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="fast",
        logger="bar"
    )

    print(f"[✓] Video tamamlandı: {output_path}")
    return output_path


def _make_title_clip(title: str, duration: float, width: int):
    """Slayt başlığını video üstüne ekler"""
    from moviepy.editor import TextClip, CompositeVideoClip

    try:
        txt = TextClip(
            title,
            fontsize=52,
            color="white",
            font="DejaVu-Sans-Bold",
            stroke_color="black",
            stroke_width=2,
            size=(width - 80, None),
            method="caption"
        ).set_position(("center", 40)).set_duration(duration)
        return txt
    except Exception:
        return None


def _add_subtitle_overlay(video, subtitle_text: str, lang: str, duration: float):
    """
    Altyazıyı video üzerine ekler.
    Cümleleri eşit süreye böler.
    """
    from moviepy.editor import TextClip, CompositeVideoClip

    if not subtitle_text:
        return video

    sentences = [s.strip() + "." for s in subtitle_text.split(".") if len(s.strip()) > 5]
    if not sentences:
        return video

    time_per = duration / len(sentences)
    subtitle_clips = []

    for i, sentence in enumerate(sentences):
        start = i * time_per
        end = min(start + time_per, duration)

        try:
            txt = (
                TextClip(
                    sentence,
                    fontsize=36,
                    color="yellow",
                    font="DejaVu-Sans",
                    stroke_color="black",
                    stroke_width=1.5,
                    size=(VIDEO_WIDTH - 100, None),
                    method="caption"
                )
                .set_position(("center", VIDEO_HEIGHT - 120))
                .set_start(start)
                .set_end(end)
            )
            subtitle_clips.append(txt)
        except Exception:
            pass

    if subtitle_clips:
        return CompositeVideoClip([video] + subtitle_clips)
    return video


def create_thumbnail(title: str, image_path: str, output_path: str) -> str:
    """
    Video için otomatik thumbnail oluşturur.
    """
    from PIL import Image, ImageDraw, ImageFilter
    import textwrap

    img = Image.open(image_path).resize((1280, 720))

    # Hafif blur + koyu overlay
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 140))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Başlık metni
    try:
        from PIL import ImageFont
        font_large = ImageFont.truetype(FONT_PATH, 72)
        font_small = ImageFont.truetype(FONT_PATH, 36)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = font_large

    # Metni ortala
    wrapped = textwrap.fill(title, width=22)
    lines = wrapped.split("\n")

    y_start = 720 // 2 - (len(lines) * 80) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        w = bbox[2] - bbox[0]
        x = (1280 - w) // 2
        # Gölge
        draw.text((x + 3, y_start + 3), line, font=font_large, fill=(0, 0, 0))
        draw.text((x, y_start), line, font=font_large, fill=(255, 220, 0))
        y_start += 90

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "JPEG", quality=95)
    print(f"[✓] Thumbnail oluşturuldu: {output_path}")
    return output_path


if __name__ == "__main__":
    print("Video builder modülü hazır.")
