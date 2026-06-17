from pathlib import Path
import subprocess
import gradio as gr

from core.downloader import download_audio
from core.platform_detect import detect_platform, extract_url
from core.transcriber import transcribe_audio, save_transcript


def handle_video_url(url: str, language: str):
    if not url or not url.strip():
        yield "Please paste a video URL.", "", "Idle."
        return

    try:
        yield "", "", "Detecting platform..."

        clean_url = extract_url(url.strip())
        platform = detect_platform(clean_url)

        if platform == 'unknown':
            yield "Unsupported platform. Supported: Bilibili, Douyin, Xiaohongshu, YouTube, Mediasite.", "", "Failed."
            return

        yield "", "", f"Downloading audio ({platform})..."
        audio_path = download_audio(clean_url, platform)

        yield "", "", "Transcribing audio..."
        text = transcribe_audio(audio_path=audio_path, language=language)

        yield "", "", "Saving transcript..."
        output_path = save_transcript(audio_path, text)

        yield text, str(output_path), "Completed."

    except subprocess.CalledProcessError as e:
        detail = e.stdout.strip() if e.stdout else "Check the URL or your network connection."
        yield f"Failed to download audio:\n\n{detail}", "", "Failed."

    except Exception as e:
        yield f"Failed to transcribe audio:\n{e}", "", "Failed."


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
    gr.Markdown("Video URL / local audio → download → transcribe → save txt.")

    language = gr.Dropdown(
        choices=["zh", "en"],
        value="zh",
        label="Transcription Language"
    )

    with gr.Tab("Video URL"):
        url_input = gr.Textbox(
            label="Paste Video URL",
            placeholder="Bilibili / Douyin / Xiaohongshu / YouTube / Mediasite"
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

    status_display = gr.Textbox(
        label="Status",
        lines=1,
        interactive=False
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
        fn=handle_video_url,
        inputs=[url_input, language],
        outputs=[transcript_output, output_path, status_display]
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
