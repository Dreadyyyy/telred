import re
import subprocess

from pathlib import Path
from tempfile import tempdir

from aiohttp import ClientSession

from aiofile import async_open


from aiofiles.tempfile import TemporaryDirectory


async def download(url: str) -> str:
    """
    Raises ValueError if video doesn't have audio
    """
    url, _ = url.split("?")

    id = url.split("/")[-2]

    async with TemporaryDirectory(dir=tempdir) as dir:
        await get_files(Path(dir), url)

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


async def get_files(tmpdir: Path, url: str) -> None:
    """
    Raises ValueError if video doesn't have audio
    """
    url = "/".join(url.split("/")[:-1])

    headers = {"User-Agent": "Mozilla/5.0"}
    async with ClientSession(headers=headers) as session:
        durl = url + "/DASHPlaylist.mpd"

        mpd = await (await session.get(durl)).text()
        r = r">DASH[^>]*<"
        qualities = re.findall(r, mpd)
        qualities = [q.strip("><") for q in qualities]
        audio = [l for l in qualities if "AUDIO" in l]
        video = [l for l in qualities if "AUDIO" not in l]

        if len(audio) == 0:
            raise ValueError("Video doesn't have audio")

        vurl = url + "/" + video[0]
        aurl = url + "/" + audio[0]

        response = await session.get(vurl)
        async with async_open(tmpdir / "v.mp4", "wb") as f:
            await f.write(await response.read())

        response = await session.get(aurl)
        async with async_open(tmpdir / "a.m4a", "wb") as f:
            await f.write(await response.read())
