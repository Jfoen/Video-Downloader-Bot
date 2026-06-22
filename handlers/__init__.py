from aiogram import Router
from aiogram.filters import CommandStart

from handlers.start import start
from handlers.check_link import check_msg, dp
from handlers.group_chat.check_link_public import group_check_msg

__all__ = ("register_user_command",)


def register_user_command(router: Router) -> None:
    router.message.register(start, CommandStart())
    router.message.register(group_check_msg)
    router.message.register(check_msg)

