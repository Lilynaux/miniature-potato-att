from pathlib import Path
from faster_whisper import WhisperModel

from core.config import OUTPUT_DIR


model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_path: Path, language: str = "zh") -> str:
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


def save_transcript(audio_path: Path, text: str, fallback_name: str | None = None) -> Path:
    stem = audio_path.stem or fallback_name or "transcript"
    output_path = OUTPUT_DIR / f"{stem}.txt"
    output_path.write_text(text, encoding="utf-8")
    return output_path