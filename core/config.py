from pathlib import Path

DESKTOP_DIR = Path.home() / "Desktop"

AUDIO_DIR = DESKTOP_DIR / "AudioDownloads"
OUTPUT_DIR = DESKTOP_DIR / "AudioTranscripts"

AUDIO_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)