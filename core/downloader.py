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

    is_youtube = any(x in url for x in ('youtube.com', 'youtu.be'))

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'retries': 3,
        'http_headers': {
            'User-Agent': (
                'com.google.ios.youtube/19.29.1 '
                'CFNetwork/1408.0.4 Darwin/22.5.0'
                if is_youtube else
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 '
                'Mobile/15E148 Safari/604.1'
            )
        },
        **(
            {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'mweb'],
                        'player_skip': ['webpage'],
                    }
                }
            }
            if is_youtube else {}
        ),
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
