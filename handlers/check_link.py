import json
import random
from html import escape
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher, F

import keyboard_pack
from videos import download_video
from aiogram.types import FSInputFile
from pathlib import Path
import subprocess
from .links_models import Link, Video
from .user_await_mode import check_user_wait_mode, initialise_wait_mode, remove_from_wait_mode
from db_pckg import db_module
from yt_dlp.utils import DownloadError, ExtractorError, PostProcessingError
from keyboard_pack.explainer_keyboard_code import inline_kb
from aiogram.types import CallbackQuery
from explainer_pack.measure_length import is_video_shorter_than_3_minutes
from explainer_pack.trascriber import transcribe_video
from explainer_pack.langchain_endpoint import generate_summary
from moviepy import VideoFileClip
from enum import Enum

import asyncio
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

load_dotenv()

executor = ThreadPoolExecutor(max_workers=4)

async def download_video_async(url, platform):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        executor,
        download_video_sync,
        url,
        platform
    )


def download_video_sync(url, platform):
    return asyncio.run(download_video(url, platform))


dp = Dispatcher()


@dp.message(F.chat.type.in_(["group", "supergroup"]), F.text.contains("http"))
async def group_check_msg(message: Message):
    await process_link_logic(message)


async def process_link_logic(message: Message):
    user_message = normalize_url(message.text)

    sent_link = Link(raw=user_message)
    if not sent_link.is_url():
        return

    if not sent_link.social_in_link():
        return

    vide_netloc = sent_link.get_netloc()
    video_link = Video(user_message, social=vide_netloc)

    if not video_link.if_url_is_valid():
        await message.reply("Убедитесь в правильности ссылки")
        return

    user_id = str(message.from_user.id)



    if await check_user_wait_mode(user_id):
        await message.reply('⏳ Дождитесь окончания предыдущей загрузки')
        return


    await initialise_wait_mode(user_id)


    sent_message = await message.reply('Скачивание началось ⏳')

    db_module.add_social_link(network_name=sent_link.get_social_name())

    asyncio.create_task(
        process_video_download(
            message,
            user_message,
            video_link.social,
            sent_message,
            public_chat=True
        )
    )


@dp.message(F.chat.type == "private", F.text)
async def check_msg(message: Message, state: FSMContext) -> None:
    user_message = normalize_url(message.text)

    sent_link = Link(raw=user_message)
    if not sent_link.is_url():
        await message.answer('Убедитесь в правильности ссылки')
        return

    if not sent_link.social_in_link():
        return

    vide_netloc = sent_link.get_netloc()
    video_link = Video(user_message, social=vide_netloc)

    if not video_link.if_url_is_valid():
        await message.answer("Убедитесь в правильности ссылки")
        return

    # if "list=" in video_link.link_to_media:
    #     import re
    #     video_link = re.sub(r"[?&]list=[^&]+", "", video_link.link_to_media)
    user_id = str(message.from_user.id)

    if await check_user_wait_mode(user_id):
        await message.answer('⏳ Дождитесь окончания предыдущей загрузки')
        return

    await initialise_wait_mode(user_id)


    sent_message: Message = await message.answer('Скачивание началось ⏳')

    db_module.add_social_link(network_name=sent_link.get_social_name())
    asyncio.create_task(
        process_video_download(message, user_message, video_link.social, sent_message, public_chat=False)
    )


async def process_video_download(
        message: Message,
        url: str,
        platform: str,
        message_notifier: Message,
        public_chat: bool
):
    user_id = str(message.from_user.id)

    if "list=" in url:
        import re
        url = re.sub(r"[?&]list=[^&]+", "", url)

    try:
        video_path = await download_video.download_video(
            url,
            platform,
            "downloads"
        )
        if public_chat:
            caption = True
        else:
            caption = False
        await send_video(
            message=message,
            path_to_video=video_path[0],
            video_thumbnail=video_path[1],
            message_notifier=message_notifier,
            caption=caption,
            video_title=video_path[2],
            video_description=video_path[3]

        )

    except (DownloadError, ExtractorError, PostProcessingError) as ex:

        print("Ошибка при скачивании видео:", ex)

        await message.answer(f"❌ Ошибка при скачивании видео: {str(ex)}")


    finally:

        await remove_from_wait_mode(user_id)


async def process_video(callback: CallbackQuery, video_data: dict):
    try:
        await callback.answer("Щас объясню", cache_time=50)

        video_text = await transcribe_video(video_data['path_to_video'])

        if video_text and len(video_text.split()) > 20:
            video_content = {
                "video_text": video_text,
                "video_title": video_data['video_title'],
                "video_description": video_data['video_description'],
            }

            video_summary = await generate_summary(video_content)

            await callback.message.reply(video_summary)
        else:
            await callback.message.reply(
                "Мало слов. Я не буду ничего из этого тебе пересказывать"
            )

    except Exception as e:
        await callback.message.reply(f"Ошибка: {e}")


@dp.callback_query(lambda c: c.data == "explain")
async def handle_explain_request(callback: CallbackQuery):
    with open('/home/video_downloader_bot/handlers/explained_videos.txt', 'r', encoding='utf-8') as file:
        all_videos = file.read()

    if str(callback.message.message_id) in all_videos:
        await callback.answer("Не успел, сладкий, кто-то уже нажал", show_alert=True)
        return

    with open('/home/video_downloader_bot/handlers/videos_to_explain.json', 'r', encoding='utf-8') as file:
        exp_dict = json.load(file)

    video_id = callback.message.message_id
    print(video_id)
    video_data = exp_dict[str(video_id - 2)]

    if not is_video_shorter_than_3_minutes(video_data['path_to_video']):
        await callback.answer("Видео слишком длинное", show_alert=True)
        return

    with open('/home/video_downloader_bot/handlers/explained_videos.txt', 'a', encoding='utf-8') as file:
        file.write(f"{callback.message.message_id}\n")

    # 👇 Запускаем фоновую задачу
    await asyncio.create_task(process_video(callback, video_data))


@dp.callback_query(lambda c: c.data == "download_audio")
async def handle_download_audio_request(callback: CallbackQuery):
    with open('/home/video_downloader_bot/handlers/download_audios.txt', 'r', encoding='utf-8') as file:
        all_videos = file.read()

    if str(callback.message.message_id) in all_videos:
        await callback.answer("Не успел, сладкий, кто-то уже нажал", show_alert=True)
        return

    with open('/home/video_downloader_bot/handlers/videos_to_explain.json', 'r', encoding='utf-8') as file:
        exp_dict = json.load(file)

    video_id = callback.message.message_id
    video_data = exp_dict[str(video_id - 2)]

    with open('/home/video_downloader_bot/handlers/download_audios.txt', 'a', encoding='utf-8') as file:
        file.write(f"{callback.message.message_id}\n")

    video = VideoFileClip(video_data['path_to_video'])
    audio = video.audio
    await callback.answer("Начинаем скачивание", show_alert=True)
    audio_path = f"{video_data['video_title']}.mp3"
    audio.write_audiofile(audio_path)

    audio_file = FSInputFile(audio_path)

    await callback.message.reply_audio(
        audio_file,
        caption=video_data['video_title']
    )
def normalize_url(url: str) -> str:
    url = url.strip()

    if url.startswith("//"):
        return "https:" + url

    if not url.startswith(("http://", "https://")):
        return "https://" + url

    return url

class Platform(str, Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    REDDIT = "reddit"


def detect_platform(text: str) -> Platform | None:
    if any(d in text for d in ["youtube.com", "youtu.be"]):
        return Platform.YOUTUBE

    if any(d in text for d in ["twitter.com", "x.com"]):
        return Platform.TWITTER

    if "reddit.com" in text:
        return Platform.REDDIT

    return None


async def send_video(
        callback: CallbackQuery,
        message: Message,
        path_to_video: str,
        video_thumbnail: str,
        message_notifier: Message,
        caption: bool,
        progress_msg: Message | None = None,
        video_title: str = None,
        video_description: str = None,

):
    if progress_msg:
        try:
            await progress_msg.delete()
        except Exception:
            pass

    title = escape(video_title)
    url = escape(message.text)

    thumb_path = Path(video_thumbnail) if video_thumbnail else None
    if thumb_path and thumb_path.suffix.lower() == ".webp":
        new_thumb = thumb_path.with_suffix(".jpg")
        subprocess.run([
            "ffmpeg", "-y", "-i", str(thumb_path), str(new_thumb)
        ])
        video_thumbnail = str(new_thumb)

    video = FSInputFile(path_to_video)
    thumbnail_file = FSInputFile(video_thumbnail) if video_thumbnail else None
    if not caption:
        with open('/home/video_downloader_bot/handlers/download_audios.txt', 'a', encoding='utf-8') as file:
            file.write(f"{callback.message.message_id}\n")

        await message.answer_video(
            video=video,
            thumbnail=thumbnail_file,
            reply_markup=inline_kb,
            supports_streaming=True,
            caption=f'<a href="{url}">{title}</a>\n',

            parse_mode="HTML"
        )
    else:
        if 'youtube.com' in message.text or 'youtu.be' in message.text or 'twitter.com' in message.text or 'x.com' in message.text or 'reddit.com' in message.text:
            await message.answer_video(
                video=video,
                caption=f'<a href="{url}">{title}</a>\n'
                        f'Видео отправил: @{message.from_user.username}',
                thumbnail=thumbnail_file,
                supports_streaming=True,
                reply_markup=inline_kb,
                parse_mode="HTML"
            )

            with open('/home/video_downloader_bot/handlers/videos_to_explain.json', 'r', encoding='utf-8') as file:
                exp_dict = json.load(file)

            match detect_platform(message.text):
                case Platform.YOUTUBE:
                    video_platform = "youtube"
                case Platform.TWITTER:
                    video_platform = "twitter"
                case Platform.REDDIT:
                    video_platform = "reddit"
            print(video_title)
            exp_dict[message.message_id] = {"path_to_video": path_to_video, "video_platform": video_platform, "video_title": video_title,
                                                          "video_description": video_description}

            with open('/home/video_downloader_bot/handlers/videos_to_explain.json', 'w', encoding='utf-8') as file:
                json.dump(exp_dict, file)

        else:
            await message.answer_video(
                video=video,
                caption=f'<a href="{url}">{title}</a>\n'
                        f'Видео отправил: @{message.from_user.username}',
                thumbnail=thumbnail_file,
                supports_streaming=True,
                parse_mode="HTML"
            )
            await message.delete()
    db_module.add_user_link(message.from_user.id)

    await message.delete()
    await message_notifier.delete()
