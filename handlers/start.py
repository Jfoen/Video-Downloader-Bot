from aiogram import types
import aiogram.utils.markdown as fmt


async def start(message: types.Message) -> None:
    await message.answer(
        fmt.text(
            fmt.text(fmt.hbold("Скачай любое видео! Просто отправь ссылку на видео\n")),
            fmt.text("Поддерживаемые соц. сети:"),
            fmt.text("YouTube\nX(Twitter)\nInstagram\nTikTok\nPinterest"),
            sep="\n"
        ), parse_mode="HTML"
    )