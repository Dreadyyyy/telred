from typing import Any
from collections.abc import Callable, Coroutine
from aiogram.types import Message
from asyncprawcore import Redirect, NotFound
from asyncpraw import Reddit
from asyncpraw.reddit import Submission

from utils import fetched_post as fp
from utils.enums import MediaType


class RedditInstance:
    reddit: Reddit | None = None

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

    async def __instantiate_reddit(self) -> Reddit:
        self.reddit = Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )
        return self.reddit

    async def get_top_post(
        self, subreddit: str
    ) -> Callable[[Message], Coroutine[Any, Any, None]]:
        try:
            subreddit_instance = await (
                self.reddit or await self.__instantiate_reddit()
            ).subreddit(subreddit, fetch=True)
        except (Redirect, NotFound):
            return fp.error("Subreddit not found")

        if subreddit_instance.over18:
            return fp.error("Nsfw subreddit")

        top_post: Submission | None = None
        posts_seen = 0
        subreddit_instance.top(time_filter="hour")
        async for submission in subreddit_instance.top(time_filter="hour"):
            if not submission.over_18:
                top_post = submission
                break
            posts_seen += 1
            if posts_seen > 10:
                return fp.error("More than 10 nsfw post in hourly top")

        match getattr(top_post, "post_hint", None):
            case "image":
                media_type = (
                    MediaType.GIF if ".gif" in top_post.url else MediaType.IMAGE
                )
                return fp.media(
                    top_post.url,
                    top_post.title,
                    media_type,
                )
            case "hosted:video":
                return fp.media(
                    top_post.media["reddit_video"]["fallback_url"],
                    top_post.title,
                    MediaType.VIDEO,
                )
            case _:
                return fp.text(
                    top_post.title,
                    top_post.selftext,
                )
