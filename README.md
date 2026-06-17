# AudioToText

A local Gradio tool that downloads video audio from multiple platforms and transcribes it using faster-whisper.

Paste a video URL — the tool detects the platform, downloads audio, transcribes it, and saves the transcript to your Desktop. No cloud APIs, everything runs locally.

## Supported Platforms

| Platform | URL Patterns |
| -------- | ------------ |
| Bilibili | `bilibili.com/video/...` `b23.tv/...` |
| Douyin | `v.douyin.com/...` (share text supported) |
| Xiaohongshu | `xiaohongshu.com/explore/...` `xiaohongshu.com/discovery/...` `xhslink.com/...` |
| YouTube | `youtube.com/watch?v=...` `youtu.be/...` |
| Mediasite | `mediasite.*.ac.uk/...` |

Share text from Douyin and Xiaohongshu is supported — paste the full share message and the URL is extracted automatically.

## Project Structure

```text
├── app.py                  # Gradio web UI entry point
├── core/                   # Business logic package
│   ├── config.py           # Output directory configuration
│   ├── platform_detect.py  # URL extraction and platform detection
│   ├── downloader.py       # Audio download router (yt-dlp)
│   ├── douyin.py           # Douyin headless browser download
│   ├── xiaohongshu.py      # Xiaohongshu headless browser download
│   └── transcriber.py      # Whisper transcription and transcript saving
├── scripts/
│   └── StartTranscriber.command  # macOS double-click launcher
├── docs/                   # Product requirement documents
└── requirements.txt
```

## Installation

Requires Python 3.10+, ffmpeg, and the conda `Tools` environment (or any env with the dependencies below).

```bash
pip install -r requirements.txt
python -m playwright install chromium
brew install ffmpeg
```

## Usage

```bash
python app.py
```

The Gradio interface opens in your browser at `http://127.0.0.1:7860`.

On macOS, you can also double-click `scripts/StartTranscriber.command` to launch directly.

**Video URL tab** — paste a supported URL (or share text), select language, click Download + Transcribe.

**Upload Audio tab** — upload a local `.mp3` / `.wav` / `.m4a` / `.mp4` / `.aac` file for transcription.

## Output

| Type | Location |
| ---- | -------- |
| Audio | `~/Desktop/AudioDownloads/` |
| Transcripts | `~/Desktop/AudioTranscripts/` |

Files are named after the video title when available, otherwise `Platform_YYYYMMDD_HHMMSS`.

## Platform Notes

- **Douyin / Xiaohongshu** use headless Chromium (Playwright) to bypass bot detection. No login required for public content.
- **Bilibili / YouTube / Mediasite** use yt-dlp with Chrome cookies. Sign in to the site in Chrome first for login-restricted videos.
- Transcription runs on CPU (`int8`) by default. For GPU, change `device="cpu"` to `device="cuda"` in `core/transcriber.py`.
