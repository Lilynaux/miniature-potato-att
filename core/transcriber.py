from pathlib import Path
import shutil
import subprocess
from datetime import datetime

from faster_whisper import WhisperModel

from core.config import AUDIO_DIR, OUTPUT_DIR


model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_path: Path, language: str = "zh") -> str:
    duration = _audio_duration_seconds(audio_path)
    if duration and duration > 30 * 60:
        return _transcribe_long_audio(audio_path, language)

    return _transcribe_single_file(audio_path, language)


def _transcribe_single_file(audio_path: Path, language: str = "zh") -> str:
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True
    )

    text = "\n".join(
        segment.text.strip()
        for segment in segments
        if segment.text.strip()
    )

    return text


def _audio_duration_seconds(audio_path: Path) -> float | None:
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def _transcribe_long_audio(audio_path: Path, language: str) -> str:
    chunks_dir = _split_audio(audio_path)
    try:
        chunks = sorted(chunks_dir.glob("chunk_*.mp3"))
        if not chunks:
            return _transcribe_single_file(audio_path, language)

        return "\n".join(
            text
            for text in (_transcribe_single_file(chunk, language) for chunk in chunks)
            if text
        )
    finally:
        shutil.rmtree(chunks_dir, ignore_errors=True)


def _split_audio(audio_path: Path, segment_seconds: int = 25 * 60) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chunks_dir = AUDIO_DIR / f"{audio_path.stem}_chunks_{timestamp}"
    chunks_dir.mkdir(exist_ok=True)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(audio_path),
            "-f", "segment",
            "-segment_time", str(segment_seconds),
            "-vn",
            "-acodec", "mp3",
            "-q:a", "2",
            str(chunks_dir / "chunk_%03d.mp3"),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return chunks_dir


def save_transcript(audio_path: Path, text: str, fallback_name: str | None = None) -> Path:
    stem = audio_path.stem or fallback_name or "transcript"
    output_path = OUTPUT_DIR / f"{stem}.txt"
    output_path.write_text(text, encoding="utf-8")
    return output_path
