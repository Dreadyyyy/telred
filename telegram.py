from typing import final
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from reddit import RedditInstance
from utils.enums import TimeFilter


@final
class TelegramInstance:
    dp = Dispatcher()

    def __init__(self, reddit_instance: RedditInstance, bot_token: str) -> None:
        self.bot = Bot(token=bot_token)
        self.reddit_instance = reddit_instance
        self._wrapper()

    @staticmethod
    def process_args(cmnd: str) -> tuple[str, TimeFilter]:
        """Raises ValueError if there is too few arguments or time filter is invalid"""
        vals = cmnd.split(" ")

        if len(vals) == 2:
            (_, subreddit), time_filter = vals, TimeFilter.HOUR
        elif len(vals) == 3:
            _, subreddit, time_filter = vals
            try:
                time_filter = TimeFilter[time_filter.upper()]
            except KeyError:
                raise ValueError(
                    "Time filter should be one of the following values: all, day, hour, month, week, year"
                )
        else:
            raise ValueError("Command signature: command subreddit [time]")

        return subreddit, time_filter

    def _wrapper(self) -> None:

        @self.dp.message(Command("top"))
        async def top(message: Message) -> None:
            try:
                subreddit, time_filter = self.process_args(message.text or "")
            except ValueError as e:
                await message.answer(str(e))
                return

            temp_message = await message.answer(f"Fetching top from r/{subreddit}")
            await (await self.reddit_instance.get_top_post(subreddit, time_filter))(
                message
            )
            await self.bot.delete_message(message.chat.id, temp_message.message_id)

    async def start(self) -> None:
        await self.dp.start_polling(self.bot)
