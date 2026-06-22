from dataclasses import dataclass
from urllib.parse import urlparse
from enum import Enum

import re


class Platform(str, Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    X = "x"
    INSTAGRAM = "instagram"
    TIK_TOK = "tiktok"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    PORNHUB = "pornhub"
    XVIDEOS = "xvideos"
    RUTUBE = "rutube"
    KINOPOISK = "kinopoisk"

@dataclass
class Video:
    link_to_media: str
    social: Platform

    yt_video_link_pattern = re.compile(
        r"^https?://(?:www\.)?"
        r"(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)"
        r"([A-Za-z0-9_-]{11})"
        r"(?:[/?&].*)?$"
    )

    twitter_video_pattern = re.compile(
        r"^https://(x|twitter)\.com/[A-Za-z0-9_]+/status/\d+(\?.*)?$"
    )

    instagram_video_pattern = re.compile(
        r"^https://(www\.)?instagram\.com/"
        r"("
        r"(reel|p)/[A-Za-z0-9_-]+"
        r"|stories/[A-Za-z0-9_.]+/\d+"
        r")/?"
        r"(\?.*)?$"
    )

    tik_tok_video_pattern = re.compile(
        r"^https?://(www\.|m\.|vm\.)?tiktok\.com/"
        r"(@[A-Za-z0-9._-]+/video/)"  # username + /video/
        r"(\d+)"  # ID видео
        r"(\?.*)?$"  # GET параметры (опционально)
    )

    pinterest_video_pattern = re.compile(
        r"^https?://("
        r"(www\.)?pinterest\.com/pin/[\w-]+/"
        r"|pin\.it/[A-Za-z0-9]+"
        r")(\?.*)?$"
    )
    reddit_video_pattern = re.compile(
    r"^https?://"
    r"(?:www\.)?"
    r"(?:reddit\.com|v\.redd\.it)"
    r"/.+"
)

    pornhub_video_pattern = re.compile(
        r"^https?://"  # http или https
        r"(?:(?:[a-z]{2,3}\.)?pornhub\.com|phub\.com)/"  # любой поддомен + основной домен или короткий phub.com
        r"(?:view_video\.php\?viewkey=|ph)"  # стандартная страница видео или короткий вариант
        r"([A-Za-z0-9]+)"  # ID видео
        r"(?:[/?&].*)?$"  # optional GET параметры
    )

    xvideos_video_pattern = re.compile(
        r"^https?://"
        r"(?:www\.|[a-z0-9-]+\.)?"
        r"(?:xvideos\.com|xv-ru\.com)/"
        r"(?:video(\d+)|video\.([A-Za-z0-9]+))"
        r"(?:/[\w_-]+)?"
        r"(?:\?.*)?$"
    )

    rutube_video_pattern = re.compile(
        r"^https?://"
        r"(?:www\.)?"
        r"rutube\.ru/video/"
        r"([a-fA-F0-9]{32})"
        r"/?"
        r"(?:\?.*)?$"
    )

    kinopoisk_video_pattern = re.compile(
        r"^https?://"
        r"(?:www\.)?"
        r"kinopoisk\.ru/"
        r"film/"
        r"(\d+)"  # ID фильма
        r"(?:/video/)?"  # опционально /video/
        r"/?"
        r"(?:\?.*)?$"
    )

    def if_url_is_valid(self) -> bool:
        match self.social:
            case "youtube":
                return self.yt_video_link_pattern.fullmatch(self.link_to_media) is not None
            case "twitter":
                return self.twitter_video_pattern.fullmatch(self.link_to_media) is not None
            case "x":
                return self.twitter_video_pattern.fullmatch(self.link_to_media) is not None
            case "instagram":
                return self.instagram_video_pattern.fullmatch(self.link_to_media) is not None
            case "tiktok":
                return self.tik_tok_video_pattern.fullmatch(self.link_to_media) is not None
            case "pinterest":
                return self.pinterest_video_pattern.fullmatch(self.link_to_media) is not None
            case "reddit":
                return self.reddit_video_pattern.fullmatch(self.link_to_media) is not None
            case "pornhub":
                return self.pornhub_video_pattern.fullmatch(self.link_to_media) is not None
            case "xvideos":
                return self.xvideos_video_pattern.fullmatch(self.link_to_media) is not None
            case "rutube":
                return self.rutube_video_pattern.fullmatch(self.link_to_media) is not None
            case 'kinopoisk':
                return self.kinopoisk_video_pattern.fullmatch(self.link_to_media) is not None

@dataclass
class Link:
    raw: str

    socials = {
        # Pornhub
        'www.pornhub.com': 'pornhub',
        'pornhub.com': 'pornhub',
        'fr.pornhub.com': 'pornhub',
        'rt.pornhub.com': 'pornhub',
        'phub.com': 'pornhub',

        # Reddit
        'reddit.com': 'reddit',
        'www.reddit.com': 'reddit',
        'v.redd.it': 'reddit',

        # Kinopoisk
        'kinopoisk.ru': 'kinopoisk',
        
        # Rutube
        'rutube.ru': 'rutube',
        
        # YouTube
        'youtube.com': 'youtube',
        'www.youtube.com': 'youtube',
        'youtu.be': 'youtube',

        # X / Twitter
        'x.com': 'twitter',
        'twitter.com': 'twitter',

        # Instagram
        'www.instagram.com': 'instagram',
        'instagram.com': 'instagram',

        # TikTok
        'www.tiktok.com': 'tiktok',
        'm.tiktok.com': 'tiktok',
        'vm.tiktok.com': 'tiktok',

        # Pinterest
        'pinterest.com': 'pinterest',
        'www.pinterest.com': 'pinterest',
        'pin.it': 'pinterest',

        # XVideos
        'xvideos.com': 'xvideos',
        'www.xvideos.com': 'xvideos',
        'xv-ru.com': 'xvideos',
        'www.xv-ru.com': 'xvideos',
    }

    def is_url(self) -> bool:
        try:
            result = urlparse(self.raw)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def social_in_link(self):
        parsed = urlparse(self.raw)
        link_netloc = parsed.netloc
        return link_netloc in self.socials

    def get_social_name(self):
        parsed = urlparse(self.raw)
        link_netloc = parsed.netloc
        return self.socials[link_netloc]

    def get_netloc(self):
        parsed = urlparse(self.raw)
        link_netloc = parsed.netloc
        return self.socials[link_netloc]
