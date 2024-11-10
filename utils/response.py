from typing import final

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.media_group import MediaGroupBuilder
from asyncpraw.reddit import Submission

from utils.enums import MediaType
from aiogram.types import InputFile, Message


@final
class response:
    def __init__(
        self, post: Submission | None, error: str = "Error fetching post"
    ) -> None:
        if not post:
            self.text = error
        else:
            self.text = f"<b>{post.title}</b>\n<tg-spoiler>{post.selftext}</tg-spoiler>"
            self.media_type = self._get_media_type(post)
            self.media = self._get_media(post)

    @staticmethod
    def _get_media_type(post: Submission) -> MediaType | None:
        if getattr(post, "is_gallery", False):
            return MediaType.GALLERY

        if getattr(post, "post_hint", "") == "image":
            return MediaType.GIF if "gif" in post.url else MediaType.IMAGE
        elif getattr(post, "media", {}).get("reddit_video", None):
            return MediaType.VIDEO

    def _get_media(self, post: Submission) -> list[InputFile | str] | None:
        if not self.media_type:
            return

        match self.media_type:
            case MediaType.IMAGE | MediaType.GIF:
                return [post.url]
            case MediaType.VIDEO:
                return [post.media["reddit_video"]["fallback_url"]]
            case MediaType.GALLERY:
                return [
                    val["p"][0]["u"].split("?")[0].replace("preview", "i")
                    for val in list(post.media_metadata.values())
                ]

    async def __call__(self, message: Message) -> Message | list[Message]:
        bot = message.bot or exit("Couldn't access bot instance")

        if not self.media_type or not self.media:
            return await message.answer(
                self.text,
                parse_mode=ParseMode.HTML,
            )

        if self.media_type == MediaType.GALLERY:
            media_group = MediaGroupBuilder(caption=self.text)
            for image in self.media:
                media_group.add_photo(image, parse_mode=ParseMode.HTML)
            return await bot.send_media_group(message.chat.id, media_group.build())

        send = {
            MediaType.IMAGE: bot.send_photo,
            MediaType.GIF: bot.send_animation,
            MediaType.VIDEO: bot.send_video,
        }[self.media_type]

        try:
            return await send(
                message.chat.id,
                self.media[0],
                caption=self.text,
                parse_mode=ParseMode.HTML,
            )
        except TelegramBadRequest as e:
            return await message.answer(f"Couldn't send media: {e.message}")
