import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from core.downloader import download_audio, cleanup
from core.transcriber import transcribe
from core.generator import generate_script
from core.humanizer import humanize

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

WELCOME_TEXT = """👋 Привет! Я помогу создать сценарий для твоего видео.

Просто скинь мне ссылку на видео:
• TikTok
• YouTube / YouTube Shorts
• Instagram Reels

И я сделаю готовый русскоязычный сценарий."""

URL_PREFIXES = (
    "https://", "http://",
    "www.tiktok.com", "vm.tiktok.com",
    "youtube.com", "youtu.be",
    "instagram.com", "www.instagram.com",
)


def is_video_url(text: str) -> bool:
    return any(text.strip().startswith(p) for p in URL_PREFIXES)


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT)


@dp.message(F.text)
async def handle_url(message: Message) -> None:
    url = message.text.strip()

    if not is_video_url(url):
        await message.answer("Скинь ссылку на видео — TikTok, YouTube или Instagram.")
        return

    status = await message.answer("⏳ Скачиваю видео...")

    audio_path = None
    try:
        # Шаг 1: Скачать аудио
        audio_path = download_audio(url)
        await status.edit_text("🎙 Транскрибирую аудио...")

        # Шаг 2: Транскрипция
        transcript = transcribe(audio_path)
        await status.edit_text("✍️ Пишу сценарий...")

        # Шаг 3: Генерация сценария
        script = generate_script(transcript)
        await status.edit_text("✨ Делаю текст живым...")

        # Шаг 4: Humanizer
        final_script = humanize(script)

        await status.edit_text("✅ Готово!")
        await message.answer(final_script)

    except Exception as e:
        logging.error(f"Error processing {url}: {e}")
        await status.edit_text(
            "❌ Не удалось обработать видео.\n\n"
            "Убедись, что ссылка рабочая и видео публичное."
        )
    finally:
        if audio_path:
            cleanup(audio_path)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
