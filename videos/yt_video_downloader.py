import asyncio
import re
from pathlib import Path
from typing import Optional, Tuple, Union

import aiohttp
from pytubefix import AsyncYouTube, YouTube
from pytubefix.exceptions import RegexMatchError
from yt_dlp import YoutubeDL

async def download_yt_video_func(
    url: str,
    dirname: str = "downloads"
) -> Tuple[str, Optional[str], str, Optional[str]]:

    Path(dirname).mkdir(parents=True, exist_ok=True)

    match = re.search(r"(?:youtu\.be/|[?&]v=|/shorts/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        raise ValueError("Не удалось извлечь video_id из ссылки")

    video_id = match.group(1)

    try:
        yt = YouTube(url, use_oauth=False, token_file="pytube_tokens/tokens.json")

        ys = yt.streams.get_highest_resolution(False)
        video_path = ys.download(
            output_path=dirname,
            filename=f"{video_id}.mp4"
        )

        # миниатюра
        thumb_path = None
        async with aiohttp.ClientSession() as session:
            for quality in ["maxresdefault", "hqdefault"]:
                t_url = f"https://i.ytimg.com/vi/{video_id}/{quality}.jpg"
                async with session.get(t_url) as resp:
                    if resp.status == 200:
                        thumb_path = Path(dirname) / f"{video_id}.jpg"
                        thumb_path.write_bytes(await resp.read())
                        break

        title = await yt.title()
        description = await yt.description() or None

        return str(video_path), str(thumb_path) if thumb_path else None, title, description

    except Exception as e:
        print(f"[PYTUBEFIX FAILED] → {e}")
        # продолжаем в fallback


    loop = asyncio.get_running_loop()

    def run_yt_dlp():
        # максимально стабильные настройки
        ydl_opts = {
            "format": "bv*+ba/b",
            "merge_output_format": "mp4",

            "outtmpl": "%(id)s.%(ext)s",

            "cookiefile": "/home/video_downloader_bot/videos/www.youtube.com_cookies.txt",

            "concurrent_fragment_downloads": 8,

            "external_downloader": "aria2c",
            "external_downloader_args": [
                "-x", "16",
                "-k", "1M"
            ],

            "throttled_rate": "100K",

            "js_runtimes": {
                "node": {
                    "path": "/usr/bin/node"
                }
            },

            "remote_components": ["ejs:github"],

            "extractor_args": {
                "youtube": {
                    "player_client": ["web"]
                }
            }
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if "entries" in info:
                info = info["entries"][0]

            video_path = ydl.prepare_filename(info)

            return (
                str(Path(video_path).resolve()),
                None,  # не заморачиваемся с thumbnail
                info.get("title"),
                info.get("description"),
            )

    return await loop.run_in_executor(None, run_yt_dlp)
if __name__ == '__main__':
    asyncio.run(
        download_yt_video_func('https://www.youtube.com/watch?v=G_pIEMIqBQI')
    )
