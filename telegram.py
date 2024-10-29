from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from reddit import RedditInstance


class TelegramInstance:
    dp = Dispatcher()

    def __init__(self, reddit_instance: RedditInstance, bot_token: str) -> None:
        self.bot = Bot(token=bot_token)
        self.reddit_instance = reddit_instance
        self.__wrapper()

    def __wrapper(self) -> None:

        @self.dp.message(Command("top"))
        async def top(message: Message) -> None:
            try:
                _, subreddit = (message.text or "").split(" ")
            except ValueError:
                await message.answer("Enter subreddit name after command")
                return

            temp_message = await message.answer(f"Fetching top from r/{subreddit}")
            await (await self.reddit_instance.get_top_post(subreddit))(message)
            await self.bot.delete_message(message.chat.id, temp_message.message_id)

        @self.dp.message(Command("controls"))
        async def controls(message: Message) -> None:
            builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="🎚️", callback_data="switch"))
            await message.answer("Switch", reply_markup=builder.as_markup())

    async def start(self) -> None:
        await self.dp.start_polling(self.bot)
