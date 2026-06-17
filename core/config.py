import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DESKTOP_DIR = Path.home() / "Desktop"

AUDIO_DIR = DESKTOP_DIR / "AudioDownloads"
OUTPUT_DIR = DESKTOP_DIR / "AudioTranscripts"
NOTES_DIR = DESKTOP_DIR / "AudioTranscripts"

AUDIO_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
