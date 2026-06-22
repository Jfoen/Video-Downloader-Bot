import subprocess
import json
from pathlib import Path


def get_video_duration_seconds(video_path: str) -> float:
    """
    Возвращает длительность видео в секундах.
    """
    video_path = str(Path(video_path))

    command = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        video_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe error: {result.stderr}")

    data = json.loads(result.stdout)
    duration = float(data["format"]["duration"])
    return duration


def is_video_shorter_than_3_minutes(video_path: str) -> bool:
    """
    Возвращает False, если видео длиннее 3 минут.
    """
    duration = get_video_duration_seconds(video_path)
    return duration <= 180