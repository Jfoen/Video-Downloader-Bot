from yt_dlp import YoutubeDL

ydl_opts = {
    "format": "bv*+ba/b",
    "merge_output_format": "mp4",

    "outtmpl": "%(id)s.%(ext)s",

    "cookiefile": "/home/video_downloader_bot/videos/www.youtube.com_cookies.txt",

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
    info = ydl.extract_info(
        "https://www.youtube.com/watch?v=FX6v_54vwmQ",
        download=True
    )

print(info["title"])