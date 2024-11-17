from typing import final
from asyncpraw import Reddit
import logging as logg
from asyncprawcore import NotFound, Redirect

from utils.response import response
from utils.enums import FeedType, TimeFilter


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

    async def get_post(
        self, subreddit: str, time_filter: TimeFilter, feed_type: FeedType
    ) -> response:
        try:
            subreddit_instance = await (
                self.reddit or await self._instantiate_reddit()
            ).subreddit(subreddit, fetch=True)
        except (NotFound, Redirect):
            return response(None, f"Subreddit r/{subreddit} doesn't exist")

        feed = {
            "top": lambda: subreddit_instance.top(time_filter=time_filter),
            "hot": subreddit_instance.hot,
            "new": subreddit_instance.new,
            "controversial": lambda: subreddit_instance.controversial(
                time_filter=time_filter
            ),
            "rising": subreddit_instance.rising,
        }[feed_type]
        top_post = await anext(feed(), None)

        if top_post is None:
            return response(None, "No posts during this time window")

        return response(top_post)
