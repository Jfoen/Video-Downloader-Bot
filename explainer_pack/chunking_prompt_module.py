import tiktoken


def split_into_chunks(text, max_tokens):
    """Функция для разбиения текста на части, не превышающие max_tokens с учетом токенов."""
    # Инициализируем токенизатор для модели GPT-4
    encoding = tiktoken.get_encoding("cl100k_base")  # Это токенизатор для GPT-4 и GPT-3.5
    tokens = encoding.encode(str(text))  # Преобразуем весь текст в токены

    chunks = []
    current_chunk = []
    current_length = 0

    for token in tokens:
        # Подсчитываем количество токенов в текущем чанке
        if current_length + 1 > max_tokens:  # Если добавление следующего токена превысит лимит
            chunks.append(encoding.decode(current_chunk))  # Преобразуем токены обратно в текст и добавляем в чанки
            current_chunk = [token]  # Новый чанк
            current_length = 1
        else:
            current_chunk.append(token)  # Добавляем токен в текущий чанк
            current_length += 1

    # Добавляем последний чанк, если он не пустой
    if current_chunk:
        chunks.append(encoding.decode(current_chunk))

    return chunks



# if __name__ == "__main__":
#     with open('../system_role_prompt', 'r') as f:
#         x = f.read()
#
#     print(split_into_chunks(x))