from pathlib import Path
from faster_whisper import WhisperModel

from config import OUTPUT_DIR


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


def save_transcript(audio_path: Path, text: str) -> Path:
    output_path = OUTPUT_DIR / f"{audio_path.stem}.txt"
    output_path.write_text(text, encoding="utf-8")
    return output_path