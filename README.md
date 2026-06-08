# AudioToText

A local Gradio tool for transcribing video audio from multiple platforms using faster-whisper.

Paste any supported video URL — the tool automatically detects the platform, downloads the audio, transcribes it, and saves a transcript to your Desktop.

## Supported Platforms

| Platform | Example URL |
| -------- | ----------- |
| Bilibili | `https://www.bilibili.com/video/...` or `https://b23.tv/...` |
| Douyin | `https://v.douyin.com/...` (share text also accepted) |
| YouTube | `https://www.youtube.com/watch?v=...` or `https://youtu.be/...` |
| Mediasite | `https://mediasite.*.ac.uk/...` |

Douyin share messages are supported — paste the full share text and the URL is extracted automatically:

```text
x.xx 复制打开抖音，看看【xxx的作品】 https://v.douyin.com/xxxxxx/
```

## Features

- Paste a video URL from any supported platform
- Auto-detects platform — no manual selection needed
- Download audio with yt-dlp
- Transcribe with faster-whisper (runs fully local)
- Upload local audio files directly
- Live status display: Detecting → Downloading → Transcribing → Saving
- Clean file naming: uses video title, falls back to `Platform_YYYYMMDD_HHMMSS`
- Saves transcripts to `~/Desktop/AudioTranscripts/`

## Installation

```bash
pip install -r requirements.txt
brew install ffmpeg
```

## Usage

```bash
python app.py
```

The Gradio interface opens in your browser automatically.

**Video URL tab** — paste any supported URL or Douyin share text, select the transcription language, and click Download + Transcribe.

**Upload Audio tab** — upload a local `.mp3`, `.wav`, `.m4a`, `.mp4`, or `.aac` file for direct transcription.

## Output

- Audio saved to `~/Desktop/AudioDownloads/`
- Transcripts saved to `~/Desktop/AudioTranscripts/`

## Notes

- Chrome cookies are used automatically for login-restricted videos (Bilibili, Douyin).
- Transcription runs on CPU by default; change `device` in `transcriber.py` for GPU.
- Unsupported URLs return a graceful error — the app does not crash.
