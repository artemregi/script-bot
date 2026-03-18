import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("TRANSCRIPTION_MODEL", "whisper-large-v3-turbo")


def transcribe(file_path: str) -> str:
    """
    Транскрибирует аудио файл через Groq Whisper.
    Возвращает текст транскрипции.
    """
    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=MODEL,
            file=audio_file,
            response_format="text",
        )
    return response.strip()
