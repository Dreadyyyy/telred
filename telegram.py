from typing import final, get_args
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from reddit import RedditInstance
from utils.enums import FeedType, TimeFilter
import utils.strings as strings


@final
class TelegramInstance:
    dp = Dispatcher()

    def __init__(self, reddit_instance: RedditInstance, bot_token: str) -> None:
        self.bot = Bot(token=bot_token)
        self.reddit_instance = reddit_instance
        self._wrapper()

    @staticmethod
    def process_args(cmnd: str) -> tuple[str, TimeFilter, FeedType]:
        """Raises ValueError if there are too few arguments or time filter is invalid"""
        vals = cmnd.split(" ")

        if len(vals) == 2:
            (feed, subreddit), time_filter = vals, "hour"
        elif len(vals) == 3:
            feed, subreddit, time_filter = vals
        else:
            raise ValueError("Command signature: command subreddit [time]")

        if time_filter not in get_args(TimeFilter):
            raise ValueError(
                "Time filter should be one of the following values: all, day, hour, month, week, year"
            )

        feed = feed.strip("/")

        return subreddit, time_filter, feed

    def _wrapper(self) -> None:

        @self.dp.message(Command("start"))
        async def _(message: Message) -> None:
            await message.answer(strings.start, parse_mode=ParseMode.MARKDOWN)

        @self.dp.message(Command(*get_args(FeedType)))
        async def _(message: Message) -> None:
            try:
                subreddit, time_filter, feed = self.process_args(message.text or "")
            except ValueError as e:
                await message.answer(str(e))
                return

            temp_message = await message.answer(f"Fetching top from r/{subreddit}")
            await (await self.reddit_instance.get_post(subreddit, time_filter, feed))(
                message
            )
            await self.bot.delete_message(message.chat.id, temp_message.message_id)

    async def start(self) -> None:
        await self.dp.start_polling(self.bot)
