from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Создаём кнопку
explain_button = InlineKeyboardButton(
    text="Объяснить",    # текст на кнопке
    callback_data="explain"  # callback data, которую можно ловить
)

download_audio_button = InlineKeyboardButton(
    text="Скачать аудио",    # текст на кнопке
    callback_data="download_audio"  # callback data, которую можно ловить
)

# Создаём клавиатуру и добавляем кнопку
inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Explain",
                callback_data="explain"
            ),
        ],
        [
            InlineKeyboardButton(
                text="аудио",
                callback_data="download_audio"
            ),
        ]
    ]
)