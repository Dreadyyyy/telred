from typing import final
from asyncpraw import Reddit
from asyncprawcore import logging

from utils.response import response
from utils.enums import TimeFilter


@final
class RedditInstance:
    reddit: Reddit | None = None

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

    async def _instantiate_reddit(self) -> Reddit:
        self.reddit = Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )
        return self.reddit

    async def get_top_post(self, subreddit: str, time_filter: TimeFilter) -> response:
        try:
            subreddit_instance = await (
                self.reddit or await self._instantiate_reddit()
            ).subreddit(subreddit, fetch=True)
        except Exception as e:
            logging.error(
                f"The following error occured when fetching instance of subreddit {subreddit}: {e}"
            )
            return response(None, "Error occured while fetching subreddit")

        top_post = await anext(subreddit_instance.top(time_filter=time_filter), None)

        if top_post is None:
            return response(None, "No posts during this time window")

        return response(top_post)
