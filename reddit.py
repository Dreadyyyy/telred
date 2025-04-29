from typing import final

from asyncpraw import Reddit
from asyncpraw.exceptions import InvalidURL
from asyncprawcore import NotFound, Redirect

from utils.contents import Contents, get_contents
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

    async def post_from_url(self, url: str) -> Contents:
        try:
            submission = await (
                self.reddit or await self._instantiate_reddit()
            ).submission(url=url)
        except InvalidURL:
            raise ValueError("Invalid url")
        except NotFound:
            raise ValueError("Post not found")

        return get_contents(submission)

    async def post_from_feed(
        self, subreddit: str, time_filter: TimeFilter, feed_type: FeedType
    ) -> Contents:
        try:
            subreddit_instance = await (
                self.reddit or await self._instantiate_reddit()
            ).subreddit(subreddit, fetch=True)
        except (NotFound, Redirect):
            raise ValueError(f"Subreddit r/{subreddit} doesn't exist")

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
            raise ValueError("No posts during this time frame")

        return get_contents(top_post)
