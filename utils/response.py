import logging
from typing import final

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.media_group import MediaGroupBuilder
from asyncpraw.reddit import Submission

from utils.download import download
from utils.enums import MediaType
from aiogram.types import InputFile, Message, FSInputFile


@final
class response:
    def __init__(
        self, post: Submission | None, error: str = "Error fetching post"
    ) -> None:
        if not post:
            self.media_type = MediaType.NONE
            self.text = error
        else:
            self.media_type = self._get_media_type(post)
            self.text = self._get_text(post)
            self.media = self._get_media(post)

    @staticmethod
    def _get_media_type(post: Submission) -> MediaType:
        if getattr(post, "is_gallery", False):
            return MediaType.GALLERY

        if getattr(post, "post_hint", "") == "image":
            return MediaType.GIF if "gif" in post.url else MediaType.IMAGE
        elif (getattr(post, "media", {}) or {}).get("reddit_video", None):
            return MediaType.VIDEO
        elif post.id not in post.url:
            return MediaType.LINK

        return MediaType.NONE

    def _get_text(self, post: Submission) -> str:
        text = f"<b>{post.title}</b>\n<tg-spoiler>{post.selftext}</tg-spoiler>"
        if self.media_type == MediaType.LINK:
            text += f"\n{post.url}"
        return text

    async def _get_media(self, post: Submission) -> list[InputFile | str] | None:
        match self.media_type:
            case MediaType.IMAGE | MediaType.GIF:
                return [post.url]
            case MediaType.VIDEO:
                return (
                    [post.media["reddit_video"]["fallback_url"]]
                    if not post.media["reddit_video"]["has_audio"]
                    else [
                        FSInputFile(
                            await download(post.media["reddit_video"]["fallback_url"])
                        )
                    ]
                )
            case MediaType.GALLERY:
                return [
                    val["p"][0]["u"].split("?")[0].replace("preview", "i")
                    for val in list(post.media_metadata.values())
                ]
            case MediaType.NONE | MediaType.LINK:
                return

    async def __call__(self, message: Message) -> Message | list[Message]:
        bot = message.bot or exit("Couldn't access bot instance")

        answer = None
        if self.media_type in (MediaType.NONE, MediaType.LINK) or not (
            media := await self.media
        ):
            answer = message.answer(
                self.text,
                parse_mode=ParseMode.HTML,
            )
        elif self.media_type == MediaType.GALLERY:
            media_group = MediaGroupBuilder(caption=self.text)
            for image in media:
                media_group.add_photo(image, parse_mode=ParseMode.HTML)
            answer = bot.send_media_group(message.chat.id, media_group.build())
        else:
            send = {
                MediaType.IMAGE: bot.send_photo,
                MediaType.GIF: bot.send_animation,
                MediaType.VIDEO: bot.send_video,
            }[self.media_type]

            answer = send(
                message.chat.id,
                media[0],
                caption=self.text,
                parse_mode=ParseMode.HTML,
            )

        try:
            return await answer
        except TelegramBadRequest as e:
            logging.error(
                f"The following error occured when sending media of type {self.media_type}: {e}"
            )
            return await message.answer(f"Couldn't send media")
