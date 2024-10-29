from redvid import Downloader


def download(url: str) -> str:
    downloader = Downloader(
        url=url,
        path="/tmp",
        max_q=True,
    )
    downloader.overwrite = True
    video = downloader.download()

    return video if isinstance(video, str) else ""
