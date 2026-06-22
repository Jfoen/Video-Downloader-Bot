from faster_whisper import WhisperModel
import os
from pathlib import Path
import asyncio

# Загружаем модель
# Загружаем модель
model = WhisperModel(
    "small",        # tiny/base/small/medium/large
    device="cpu",   # CPU
    compute_type="float32"  # безопасно для всех CPU
)

async def transcribe_video(video_path: str) -> str | None:
    video_file = Path(video_path)
    if not video_file.exists():
        raise FileNotFoundError(f"{video_path} не найден")

    loop = asyncio.get_running_loop()

    # транскрибируем в отдельном потоке, чтобы не блокировать event loop
    segments, info = await loop.run_in_executor(
        None,  # default ThreadPoolExecutor
        lambda: model.transcribe(
            str(video_file),
            language=None,
            task="transcribe"
        )
    )

    text = " ".join(segment.text for segment in segments).strip()

    # проверяем количество слов
    if len(text.split()) < 20:
        return None

    return text

