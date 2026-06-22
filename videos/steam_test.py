import re
import requests
from yt_dlp import YoutubeDL


def extract_steam_video(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    html = requests.get(url, headers=headers).text

    # ищем mp4 трейлеры
    mp4_urls = re.findall(r'https://cdn\.cloudflare\.steamstatic\.com/steam/apps/.*?\.mp4', html)

    # убираем дубликаты
    mp4_urls = list(set(mp4_urls))

    return mp4_urls


def download_video(video_url, output="downloads/%(title)s.%(ext)s"):
    ydl_opts = {
        "outtmpl": output,
        "quiet": False
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


if __name__ == "__main__":

    steam_url = "https://store.steampowered.com/app/3065800/Marathon/"

    videos = extract_steam_video(steam_url)

    print("Найденные видео:")
    for v in videos:
        print(v)

    if videos:
        download_video(videos[0])