import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("HUMANIZER_MODEL", "llama-4-scout")

SYSTEM_PROMPT = """Ты — редактор, который делает текст живым и человечным.

Получишь сценарий для короткого видео. Твоя задача:

УБЕРИ:
- Канцелярские обороты и шаблонные фразы
- Признаки AI-текста: "безусловно", "несомненно", "в заключение"
- Слишком правильные, "книжные" предложения
- Избыточные прилагательные и наречия

ДОБАВЬ:
- Живые разговорные обороты
- Лёгкие паузы через многоточие или тире там, где говорят
- Естественные переходы между мыслями
- Ощущение, что человек рассказывает, а не читает

СОХРАНИ:
- Структуру и смысл сценария полностью
- Крюк в начале
- Призыв к действию в конце
- Примерно ту же длину

Верни ТОЛЬКО переработанный текст, без комментариев."""


def humanize(script: str) -> str:
    """
    Делает сгенерированный сценарий более живым и человечным.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": script},
        ],
        temperature=0.7,
        max_tokens=1200,
    )
    return response.choices[0].message.content.strip()
