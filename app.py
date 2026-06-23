from pathlib import Path
import subprocess
import gradio as gr

from core.downloader import download_audio
from core.platform_detect import detect_platform, extract_url
from core.transcriber import transcribe_audio, save_transcript
from core.ai_notes import generate_notes, save_notes, estimate_tokens


def handle_video_url(url: str, language: str):
    if not url or not url.strip():
        yield "Please paste a video URL.", "", "Idle."
        return

    try:
        yield "", "", "Detecting platform..."

        clean_url = extract_url(url.strip())
        platform = detect_platform(clean_url)

        if platform == 'unknown':
            yield "Unsupported platform. Supported: Bilibili, Douyin, Xiaohongshu, YouTube, Mediasite, Apple Podcasts, Podcast RSS.", "", "Failed."
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


def handle_generate_notes(transcript: str, provider: str, txt_path: str):
    if not transcript or not transcript.strip():
        yield "", "", "No transcript to process."
        return

    try:
        tokens = estimate_tokens(transcript)
        yield "", "", f"Generating AI notes ({provider}, ~{tokens} tokens)..."

        notes = generate_notes(transcript, provider)

        notes_path = ""
        if txt_path:
            notes_path = str(save_notes(txt_path, notes))

        yield notes, notes_path, "AI notes generated."

    except Exception as e:
        yield "", "", f"Failed to generate notes: {e}"


with gr.Blocks(title="Audio Transcriber") as demo:

    gr.Markdown("# Audio Transcriber")
    gr.Markdown("Video / podcast URL or local audio → download → transcribe → AI notes.")

    with gr.Row():
        language = gr.Dropdown(
            choices=["zh", "en"],
            value="zh",
            label="Transcription Language"
        )
        ai_provider = gr.Dropdown(
            choices=["Gemini", "GPT"],
            value="Gemini",
            label="AI Provider"
        )

    with gr.Tab("URL"):
        url_input = gr.Textbox(
            label="Paste URL",
            placeholder="Bilibili / Douyin / Xiaohongshu / YouTube / Mediasite / Apple Podcasts / Podcast RSS"
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
        lines=20
    )

    output_path = gr.Textbox(
        label="Saved TXT Path",
        lines=1
    )

    gr.Markdown("---")

    notes_btn = gr.Button(
        "Generate AI Notes",
        variant="secondary"
    )

    notes_output = gr.Textbox(
        label="AI Notes",
        lines=20
    )

    notes_path = gr.Textbox(
        label="Saved Notes Path",
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

    notes_event = notes_btn.click(
        fn=handle_generate_notes,
        inputs=[transcript_output, ai_provider, output_path],
        outputs=[notes_output, notes_path, status_display]
    )

    stop_btn = gr.Button("Stop", variant="stop")

    stop_btn.click(
        fn=None,
        inputs=None,
        outputs=None,
        cancels=[url_event, upload_event, notes_event]
    )


if __name__ == "__main__":
    demo.queue()

    demo.launch(
        server_name="127.0.0.1",
        inbrowser=True,
        share=True
    )
