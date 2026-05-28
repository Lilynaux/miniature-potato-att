from pathlib import Path
import subprocess
import gradio as gr

from downloader import download_audio
from transcriber import transcribe_audio, save_transcript


def handle_bilibili_url(url: str, language: str):
    if not url or not url.strip():
        return "Please paste a Bilibili URL.", ""

    try:
        audio_path = download_audio(url.strip())

        text = transcribe_audio(
            audio_path=audio_path,
            language=language
        )

        output_path = save_transcript(audio_path, text)

        return text, str(output_path)

    except subprocess.CalledProcessError as e:
        return f"Download failed:\n{e}", ""

    except Exception as e:
        return f"Failed:\n{e}", ""


def handle_uploaded_audio(audio_file, language: str):
    if audio_file is None:
        return "Please upload an audio file.", ""

    try:
        audio_path = Path(audio_file)

        text = transcribe_audio(
            audio_path=audio_path,
            language=language
        )

        output_path = save_transcript(audio_path, text)

        return text, str(output_path)

    except Exception as e:
        return f"Failed:\n{e}", ""


with gr.Blocks(title="Audio Transcriber") as demo:

    gr.Markdown("# Audio Transcriber")
    gr.Markdown("Bilibili URL / local audio → download → transcribe → save txt.")

    language = gr.Dropdown(
        choices=["zh", "en"],
        value="zh",
        label="Transcription Language"
    )

    with gr.Tab("Bilibili URL"):
        url_input = gr.Textbox(
            label="Paste Bilibili URL",
            placeholder="https://www.bilibili.com/video/..."
        )

        url_btn = gr.Button(
            "Download + Transcribe",
            variant="primary"
        )

    with gr.Tab("Upload Audio"):
        audio_input = gr.File(
            label="Upload Audio File",
            file_types=[".mp3", ".wav", ".m4a", ".mp4", ".aac"],
            type="filepath"
        )

        upload_btn = gr.Button(
            "Transcribe Uploaded Audio",
            variant="primary"
        )

    transcript_output = gr.Textbox(
        label="Transcript",
        lines=25
    )

    output_path = gr.Textbox(
        label="Saved TXT Path",
        lines=1
    )

    url_event = url_btn.click(
        fn=handle_bilibili_url,
        inputs=[url_input, language],
        outputs=[transcript_output, output_path]
    )

    upload_event = upload_btn.click(
        fn=handle_uploaded_audio,
        inputs=[audio_input, language],
        outputs=[transcript_output, output_path]
    )

    stop_btn = gr.Button("Stop", variant="stop")

    stop_btn.click(
        fn=None,
        inputs=None,
        outputs=None,
        cancels=[url_event, upload_event]
    )


if __name__ == "__main__":
    demo.queue()

    demo.launch(
        server_name="127.0.0.1",
        inbrowser=True
    )