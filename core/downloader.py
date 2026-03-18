import os
import glob
import uuid
import yt_dlp


TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp')


def download_audio(url: str) -> str:
    """
    Скачивает аудио из TikTok / Instagram / YouTube.
    Возвращает путь к аудио файлу (m4a/webm/mp4 — без ffmpeg).
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    outtmpl = os.path.join(TEMP_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
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

    # Найти скачанный файл по file_id
    matches = glob.glob(os.path.join(TEMP_DIR, f"{file_id}.*"))
    if not matches:
        raise FileNotFoundError("Аудио файл не найден после загрузки")

    return matches[0]


def cleanup(file_path: str) -> None:
    """Удаляет временный файл после обработки."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
