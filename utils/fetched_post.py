from typing import Any
from collections.abc import Callable, Coroutine
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from utils.enums import MediaType


def error(error: str) -> Callable[[Message], Coroutine[Any, Any, None]]:

    async def answer(message: Message) -> None:
        await message.answer(f"Couldn't fetch post: {error}")

    return answer


def media(
    url: str, title: str, media_type: MediaType
) -> Callable[[Message], Coroutine[Any, Any, None]]:

    async def answer(message: Message) -> None:
        bot = message.bot or exit("Couldn't access bot instance")
        send = {
            MediaType.IMAGE: bot.send_photo,
            MediaType.GIF: bot.send_animation,
            MediaType.VIDEO: bot.send_video,
        }[media_type]

        try:
            await send(message.chat.id, url, caption=title)
        except TelegramBadRequest as e:
            await message.answer(f"Couldn't send media: {e.message}")

    return answer


def text(title: str, text: str) -> Callable[[Message], Coroutine[Any, Any, None]]:

    async def answer(message: Message) -> None:
        await message.answer(
            text=f"<b>{title}</b>\n<tg-spoiler>{text}</tg-spoiler>",
            parse_mode=ParseMode.HTML,
        )

    return answer
