from pathlib import Path
import re
import subprocess
from datetime import datetime

from config import AUDIO_DIR


def _sanitize_stem(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = name.strip('. ')
    return name[:80] if name else ''


def download_audio(url: str, platform: str) -> Path:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fallback_stem = f"{platform.capitalize()}_{timestamp}"

    output_template = str(AUDIO_DIR / "%(title).80s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--cookies-from-browser", "chrome",
        "-x",
        "--audio-format", "mp3",
        "--restrict-filenames",
        "-o", output_template,
    ]

    if platform == 'bilibili':
        cmd += [
            "--add-header", "Referer:https://www.bilibili.com",
            "--add-header", "User-Agent:Mozilla/5.0",
        ]
    else:
        cmd += ["--add-header", "User-Agent:Mozilla/5.0"]

    cmd.append(url)

    before = set(AUDIO_DIR.glob("*.mp3"))
    subprocess.run(cmd, check=True)
    after = set(AUDIO_DIR.glob("*.mp3"))

    new_files = after - before
    if new_files:
        downloaded = max(new_files, key=lambda x: x.stat().st_mtime)
    else:
        files = sorted(AUDIO_DIR.glob("*.mp3"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not files:
            raise FileNotFoundError("No mp3 file found after download.")
        downloaded = files[0]

    stem = _sanitize_stem(downloaded.stem)
    bad_patterns = ('manifest', 'playbackticket', 'http', 'www.')
    if not stem or any(p in stem.lower() for p in bad_patterns) or len(stem) < 3:
        stem = fallback_stem

    final_path = downloaded.parent / f"{stem}.mp3"
    if final_path != downloaded:
        downloaded.rename(final_path)

    return final_path
