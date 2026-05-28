from pathlib import Path
import subprocess

from config import AUDIO_DIR


def download_audio(url: str) -> Path:
    output_template = str(AUDIO_DIR / "%(title).80s.%(ext)s")

    cmd = [
        "yt-dlp",

        "--cookies-from-browser", "chrome",

        "--add-header",
        "Referer:https://www.bilibili.com",

        "--add-header",
        "User-Agent:Mozilla/5.0",

        "-x",
        "--audio-format", "mp3",

        "-o", output_template,

        url,
    ]

    subprocess.run(cmd, check=True)

    files = sorted(
        AUDIO_DIR.glob("*.mp3"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    if not files:
        raise FileNotFoundError("No mp3 file found after download.")

    return files[0]