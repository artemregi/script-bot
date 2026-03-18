import os
import uuid
import yt_dlp


TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp')


def download_audio(url: str) -> str:
    """
    Скачивает аудио из TikTok / Instagram / YouTube.
    Возвращает путь к .mp3 файлу.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_path


def cleanup(file_path: str) -> None:
    """Удаляет временный файл после обработки."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
