from pathlib import Path
from aiohttp import ClientSession
from aiofile import async_open
from tempfile import tempdir
from aiofiles.tempfile import TemporaryDirectory

import os


async def download(url: str, has_audio: bool) -> str:
    url, _ = url.split("?")

    parts = url.split("/")
    parts.pop()

    id = parts[-1]

    vurl = url
    aurl = "/".join(parts) + "/DASH_AUDIO_128.mp4" if has_audio else None

    async with TemporaryDirectory(dir=tempdir) as dir:
        path = Path(dir)

        await get_files(path, vurl, aurl)

        os.system(
            "ffmpeg -hide_banner -loglevel panic"
            + f' -y -i "{dir}/v.mp4" -i "{dir}/a.m4a"'
            + f' -vcodec copy {"-acodec copy" if has_audio else ""} "{tempdir}/{id}.mp4"'
        )

    return f"{tempdir}/{id}.mp4"


async def get_files(tmpdir: Path, vurl: str, aurl: str | None):
    headers = {"User-Agent": "Mozilla/5.0"}
    async with ClientSession(headers=headers) as session:
        response = await session.get(vurl)
        async with async_open(tmpdir / "v.mp4", "wb") as f:
            await f.write(await response.read())

        if not aurl:
            return

        response = await session.get(aurl)
        async with async_open(tmpdir / "a.m4a", "wb") as f:
            await f.write(await response.read())
