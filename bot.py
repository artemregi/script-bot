import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from core.downloader import download_audio, cleanup
from core.transcriber import transcribe
from core.generator import generate_script, translate
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
        await status.edit_text("🌍 Перевожу на русский...")

        # Шаг 3: Нативный перевод
        translation = translate(transcript)
        await status.edit_text("✍️ Генерирую сценарий...")

        # Шаг 4: Генерация сценария
        script = generate_script(transcript)
        final_script = humanize(script)

        await status.delete()

        await message.answer(
            f"📝 *Версия 1 — Перевод оригинала:*\n\n{translation}",
            parse_mode="Markdown"
        )
        await message.answer(
            f"🎬 *Версия 2 — Готовый сценарий:*\n\n{final_script}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logging.error(f"Error processing {url}: {e}", exc_info=True)
        await status.edit_text(
            f"❌ Ошибка при обработке видео.\n\n"
            f"`{type(e).__name__}: {str(e)[:200]}`",
            parse_mode="Markdown"
        )
    finally:
        if audio_path:
            cleanup(audio_path)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
