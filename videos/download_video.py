import asyncio
from typing import Tuple, Any

from yt_video_downloader import download_yt_video_func
import subprocess
import requests


COOKIES_MAP = {
    "instagram": "/home/video_downloader_bot/videos/cookies_insta.txt",
    "reddit": r"/home/video_downloader_bot/videos/www.reddit.com_cookies.txt",
    "pornhub": r"/home/video_downloader_bot/videos/rt.pornhub.com_cookies.txt",
}


def fix_instagram_video_fast(input_path: str) -> str:
    output_path = str(Path(input_path).with_name(Path(input_path).stem + "_fixed.mp4"))

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "superfast",  # Очень быстрое кодирование
        "-crf", "26",  # Хороший баланс для инстаграма
        "-c:a", "copy",
        "-movflags", "+faststart",
        "-vf", "fps=fps=30",  # Принудительно 30 кадров если нужно
        "-y", output_path
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("FFmpeg output:", result.stdout)
        if result.stderr:
            print("FFmpeg warnings:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        raise

    return output_path


from pathlib import Path
from yt_dlp import YoutubeDL

def expand_reddit_url(url: str) -> str:
    r = requests.get(url, allow_redirects=True, timeout=10)
    return r.url

async def download_video(
    url: str,
    platform: str,
    output_dir: str = "downloads"
) -> tuple[str, str | None, Any | None, Any | None]:

    if platform == "youtube":
        video_path = await download_yt_video_func(url=url)
        return video_path
    else:
        ydl_opts = {
            "outtmpl": f"{output_dir}/%(uploader)s_%(id)s.%(ext)s",
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "quiet": True,
            "nonplaylist": True,
            "nocheckcertificate": True,
            "concurrent_fragment_downloads": 16,
            "no_warnings": True,
            "writethumbnail": True,
        }

    cookiefile = COOKIES_MAP.get(platform)
    if cookiefile:
        ydl_opts["cookiefile"] = cookiefile

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)


        if "entries" in info and len(info["entries"]) > 1:
            info = info["entries"][0]

        video_path = Path(
            info.get("filepath") or ydl.prepare_filename(info)
        ).resolve()

        # --- THUMBNAIL ---
        thumbnail_path = None

        if info.get("thumbnails"):
            # yt-dlp кладёт thumbnail рядом с видео
            thumb = info["thumbnails"][-1]
            if "filepath" in thumb:
                thumbnail_path = Path(thumb["filepath"]).resolve()
            else:
                # fallback: вычисляем имя
                thumbnail_path = video_path.with_suffix(".jpg")
                if not thumbnail_path.exists():
                    thumbnail_path = None
    title = info.get("title")
    description = info.get("description")

    if platform == "instagram":
        video_path = Path(fix_instagram_video_fast(str(video_path))).resolve()

    return str(video_path), str(thumbnail_path) if thumbnail_path else None, title if title else None, description if description else None


if __name__ == "__main__":
    twitter_url = "https://store.steampowered.com/app/3065800/Marathon/?snr=1_4_4__118"
    x = asyncio.run(download_video(twitter_url, platform='steam'))
    print(x)