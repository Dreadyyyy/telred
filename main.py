import asyncio
import logging as logg

from reddit import RedditInstance
from telegram import TelegramInstance
from dotenv import dotenv_values as env

logg.basicConfig(
    handlers=[logg.FileHandler("info.log"), logg.StreamHandler()], level=logg.INFO
)
logg.basicConfig(
    handlers=[logg.FileHandler("error.log"), logg.StreamHandler()], level=logg.ERROR
)


async def main() -> None:
    reddit_instance = RedditInstance(
        env()["CLIENT_ID"] or exit("No client id for reddit bot set"),
        env()["CLIENT_SECRET"] or exit("No client secret for reddit bot set"),
        env()["USER_AGENT"] or exit("No user agent for reddit bot set"),
    )

    telegram_instance = TelegramInstance(
        reddit_instance, env()["BOT_TOKEN"] or exit("No api key for telegram bot set")
    )

    await telegram_instance.start()


if __name__ == "__main__":
    asyncio.run(main())
