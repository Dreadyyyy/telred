import aiofiles.os as os

from utils.download import download

from abc import ABC
from dataclasses import dataclass
from typing import final, override
from itertools import batched

from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

from asyncpraw.reddit import Submission


type ResponseType = Post | Error


@dataclass
class Post:
    submission: Submission


@dataclass
class Error:
    text: str


class Contents(ABC):
    submission: Submission

    def __init__(self, submission: Submission) -> None:
        self.submission = submission

    def get_text(self) -> str:
        return f"<b>{self.submission.title}</b>\n<tg-spoiler>{self.submission.selftext}</tg-spoiler>"

    async def send(self, message: Message) -> None:
        await message.answer(self.get_text(), parse_mode=ParseMode.HTML)


@final
class Plain(Contents):
    pass


@final
class Link(Contents):

    @override
    def get_text(self) -> str:
        return super().get_text() + f"\n{self.submission.url}"


class Media(Contents, ABC):
    has_spoiler: bool

    def __init__(self, submission: Submission) -> None:
        super().__init__(submission)
        self.has_spoiler = submission.over_18 or submission.spoiler


@final
class Image(Media):
    is_gif: bool

    def __init__(self, submission: Submission) -> None:
        super().__init__(submission)
        self.is_gif = submission.url.endswith(".gif")

    @override
    async def send(self, message: Message) -> None:
        send = message.answer_animation if self.is_gif else message.answer_photo
        await send(
            self.submission.url,
            caption=self.get_text(),
            parse_mode=ParseMode.HTML,
            has_spoiler=self.has_spoiler,
        )


@final
class Video(Media):

    @override
    async def send(self, message: Message) -> None:
        filepath: str | None = None

        try:
            filepath = await download(
                self.submission.media["reddit_video"]["fallback_url"]
            )
            video = FSInputFile(filepath)
        except ValueError:
            video = self.submission.media["reddit_video"]["fallback_url"]

        await message.answer_video(
            video,
            caption=self.get_text(),
            parse_mode=ParseMode.HTML,
            has_spoiler=self.has_spoiler,
        )

        if filepath is not None:
            await os.remove(filepath)


@final
class Gallery(Media):
    urls: list[str]

    def __init__(self, submission: Submission) -> None:
        super().__init__(submission)
        self.urls = [
            val["p"][-1]["u"] for val in list(submission.media_metadata.values())
        ]

    @override
    async def send(self, message: Message) -> None:
        text = self.get_text()

        groups = list(batched(self.urls, 10))
        for i, group in enumerate(groups):
            media_group = MediaGroupBuilder(caption=text + f"\n{i+1}/{len(groups)}")

            for image in group:
                media_group.add_photo(
                    image, parse_mode=ParseMode.HTML, has_spoiler=self.has_spoiler
                )

            await message.answer_media_group(
                media_group.build(),
                parse_mode=ParseMode.HTML,
                has_spoiler=self.has_spoiler,
            )


def get_contents(submission: Submission) -> Contents:
    if getattr(submission, "is_gallery", False):
        return Gallery(submission)
    elif getattr(submission, "post_hint", "") == "image":
        return Image(submission)
    elif (getattr(submission, "media", {}) or {}).get("reddit_video", False):
        return Video(submission)
    elif submission.id not in submission.url:
        return Link(submission)
    else:
        return Plain(submission)
