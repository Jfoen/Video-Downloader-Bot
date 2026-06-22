from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Создаём кнопку
download_audio_button = InlineKeyboardButton(
    text="Скачать аудио",    # текст на кнопке
    callback_data="download_audio"  # callback data, которую можно ловить
)

# Создаём клавиатуру и добавляем кнопку
audio_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Скачать аудио",
                callback_data="download"
            )
        ]
    ]
)