# AudioToText

A local Gradio tool for downloading Bilibili audio and transcribing it with faster-whisper.

## Features

- Paste Bilibili video URL
- Download audio with yt-dlp
- Transcribe with faster-whisper
- Upload local audio files
- Save transcripts to Desktop folders

## Installation

```bash
pip install -r requirements.txt
brew install ffmpeg
```

## Notes

For Bilibili login-restricted videos, Chrome cookies may be required:
`yt-dlp --cookies-from-browser chrome URL`
