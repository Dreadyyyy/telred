from pathlib import Path
from aiohttp import ClientSession
from aiofile import async_open
from tempfile import tempdir
from aiofiles.tempfile import TemporaryDirectory

import subprocess


async def download(url: str) -> str:
    url, _ = url.split("?")

    parts = url.split("/")
    parts.pop()

    id = parts[-1]

    vurl = url
    aurl = "/".join(parts) + "/DASH_AUDIO_128.mp4"

    async with TemporaryDirectory(dir=tempdir) as dir:
        await get_files(Path(dir), vurl, aurl)

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "panic",
            "-y",
            "-i",
            f"{dir}/v.mp4",
            "-i",
            f"{dir}/a.m4a",
            "-vcodec",
            "copy",
            "-acodec",
            "copy",
            f"{tempdir}/{id}.mp4",
        ]
        subprocess.run(cmd)

    return f"{tempdir}/{id}.mp4"


async def get_files(tmpdir: Path, vurl: str, aurl: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    async with ClientSession(headers=headers) as session:
        response = await session.get(vurl)
        async with async_open(tmpdir / "v.mp4", "wb") as f:
            await f.write(await response.read())

        response = await session.get(aurl)
        async with async_open(tmpdir / "a.m4a", "wb") as f:
            await f.write(await response.read())
