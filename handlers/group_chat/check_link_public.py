import random

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher, F
from videos import download_video
from aiogram.types import FSInputFile
from pathlib import Path
import subprocess
from ..links_models import Link, Video
from ..user_await_mode import check_user_wait_mode, initialise_wait_mode, remove_from_wait_mode
from db_pckg import db_module

import asyncio
from concurrent.futures import ThreadPoolExecutor

dp = Dispatcher()
executor = ThreadPoolExecutor(max_workers=4)  # до 4 одновременных загрузок


def download_video_sync(url, platform):
    return asyncio.run(download_video(url, platform))


async def download_video_async(url, platform):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        executor,
        download_video_sync,
        url,
        platform
    )


def normalize_url(url: str) -> str:
    url = url.strip()

    if url.startswith("//"):
        return "https:" + url

    if not url.startswith(("http://", "https://")):
        return "https://" + url

    return url


async def process_video_download(
        message: Message,
        url: str,
        platform: str,
        message_notifier: Message
):
    user_id = str(message.from_user.id)

    try:
        video_path = await download_video.download_video(
            url,
            platform,
            "downloads"
        )

        await send_video(
            message=message,
            path_to_video=video_path[0],
            video_thumbnail=video_path[1],
            message_notifier=message_notifier
        )

    except Exception as ex:
        await message.answer("❌ Ошибка при скачивании видео\n", ex)

    finally:
        await remove_from_wait_mode(user_id)


async def process_link_logic(message: Message):
    user_message = normalize_url(message.text)

    sent_link = Link(raw=user_message)
    if not sent_link.is_url():
        return

    if not sent_link.social_in_link():
        await message.reply(
            "Поддерживаются: YouTube, X, Instagram, TikTok, Pinterest"
        )
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
            sent_message
        )
    )


@dp.message(F.chat.type.in_(["group", "supergroup"]), F.text.contains("http"))
async def group_check_msg(message: Message):
    await process_link_logic(message)


@dp.message()
async def send_video(
        message: Message,
        path_to_video: str,
        video_thumbnail: str,
        message_notifier: Message,
        progress_msg: Message | None = None,
        video_title: str = None,
        video_description: str = None,

):
    if progress_msg:
        try:
            await progress_msg.delete()
        except Exception:
            pass

    thumb_path = Path(video_thumbnail) if video_thumbnail else None
    if thumb_path and thumb_path.suffix.lower() == ".webp":
        new_thumb = thumb_path.with_suffix(".jpg")
        subprocess.run([
            "ffmpeg", "-y", "-i", str(thumb_path), str(new_thumb)
        ])
        video_thumbnail = str(new_thumb)

    video = FSInputFile(path_to_video)
    thumbnail_file = FSInputFile(video_thumbnail) if video_thumbnail else None

    await message.answer_video(
        video=video,
        has_spoiler=True,
        thumbnail=thumbnail_file,
        supports_streaming=True,
        caption=message.text
    )
    db_module.add_user_link(message.from_user.id)

    await message_notifier.delete()
