import json


async def check_user_wait_mode(user_id: str) -> bool:
    with open('await_users.json', 'r', encoding='utf-8') as f:
        await_users = json.load(f)

    return user_id in await_users


async def initialise_wait_mode(user_id: str):
    with open('await_users.json', 'r', encoding='utf-8') as f:
        await_users = json.load(f)

    await_users[user_id] = True

    with open("await_users.json", "w", encoding="utf-8") as f:
        json.dump(await_users, f, ensure_ascii=False, indent=4)


async def remove_from_wait_mode(user_id: str):
    with open('await_users.json', 'r', encoding='utf-8') as f:
        await_users = json.load(f)

    del await_users[user_id]

    with open("await_users.json", "w", encoding="utf-8") as f:
        json.dump(await_users, f, ensure_ascii=False, indent=4)