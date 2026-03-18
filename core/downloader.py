import os
import glob
import uuid
import base64
import tempfile
import yt_dlp


TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp')
INSTAGRAM_COOKIES = os.environ.get('INSTAGRAM_COOKIES', '')
YOUTUBE_COOKIES = os.environ.get('YOUTUBE_COOKIES', '')


def _write_cookies_file(content: str):
    if not content.strip():
        return None
    # Support base64-encoded cookies (Railway env var friendly)
    try:
        decoded = base64.b64decode(content.strip()).decode('utf-8')
        content = decoded
    except Exception:
        pass  # Not base64, use as plain text
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    f.write(content)
    f.close()
    return f.name


def download_audio(url: str) -> str:
    """
    Скачивает аудио из TikTok / Instagram / YouTube.
    Возвращает путь к аудио файлу (без ffmpeg).
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    outtmpl = os.path.join(TEMP_DIR, f"{file_id}.%(ext)s")

    is_youtube = any(x in url for x in ('youtube.com', 'youtu.be'))
    is_instagram = 'instagram.com' in url

    cookies_file = None
    if is_instagram:
        cookies_file = _write_cookies_file(INSTAGRAM_COOKIES)
    elif is_youtube:
        cookies_file = _write_cookies_file(YOUTUBE_COOKIES)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'retries': 5,
        'socket_timeout': 30,
        **(
            {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_music', 'android', 'ios'],
                        'player_skip': ['webpage', 'configs'],
                    }
                }
            }
            if is_youtube else {}
        ),
        **(
            {'cookiefile': cookies_file}
            if cookies_file else {}
        ),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    finally:
        if cookies_file and os.path.exists(cookies_file):
            os.remove(cookies_file)

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
