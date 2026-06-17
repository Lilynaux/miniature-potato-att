# PRD-003 Universal Video URL Support

## Overview

Current system only supports:

Video URL (Bilibili)
→ Download Audio
→ Whisper Transcription
→ TXT Export

The objective of this iteration is to transform the application from a Bilibili-only tool into a universal video-to-text transcription platform.

Supported platforms should include:

- Bilibili
- Douyin
- YouTube
- Mediasite

Future extensibility should be preserved for:

- TikTok
- Podcast RSS
- Spotify Podcasts

---

# Problem Statement

Current UI assumes all URLs are Bilibili URLs.

Limitations:

- Cannot process Douyin share links
- Cannot process YouTube videos
- Cannot process Mediasite lecture recordings
- Users must manually identify platform compatibility
- File naming is inconsistent

The application should automatically detect the source platform and route the download workflow accordingly.

---

# User Story

As a learner,

I want to paste a video URL from any supported platform,

So that the system automatically downloads audio, transcribes speech, and saves a transcript without additional configuration.

---

# Functional Requirements

## FR-001 Universal URL Input

Replace:

Paste Bilibili URL

With:

Paste Video URL

Supported examples:

<https://www.bilibili.com/video/>...

<https://v.douyin.com/>...

<https://www.youtube.com/watch?v=>...

<https://mediasite.bris.ac.uk/>...

The user should not need to specify the platform manually.

---

## FR-002 Platform Detection

Create:

detect_platform(url: str)

Return values:

- bilibili
- douyin
- youtube
- mediasite
- unknown

Detection rules:

Bilibili:

- bilibili.com
- b23.tv

Douyin:

- douyin.com
- v.douyin.com

YouTube:

- youtube.com
- youtu.be

Mediasite:

- mediasite

Unknown:

Fallback state

---

## FR-003 Douyin Share Text Support

Support direct copy-paste of Douyin share messages.

Example:

0.07 复制打开抖音，看看【黑盒调查局的作品】
<https://v.douyin.com/xxxxxx/>

The system should:

1. Extract the URL automatically
2. Ignore surrounding text
3. Continue processing normally

Implementation:

extract_url(text: str)

Regex-based URL extraction.

---

## FR-004 Universal Downloader

Refactor:

download_audio(url)

Into:

download_audio(url, platform)

Downloader should internally use yt-dlp.

The platform parameter should determine any platform-specific options if required.

Expected output:

audio_path

No UI changes required.

---

## FR-005 Processing Status

Add a status display component.

Possible states:

Detecting platform...

Downloading audio...

Transcribing audio...

Saving transcript...

Completed.

Failed.

Purpose:

Provide user feedback during long-running operations.

---

## FR-006 Clean File Naming

Current filenames may contain:

manifest(...)
playbackTicket(...)
long URLs

New filename priority:

1. Extract video title if available
2. Sanitize invalid filename characters
3. Fallback:

Platform_YYYYMMDD_HHMMSS

Examples:

Sales_Objection_Handling.mp3

Sales_Objection_Handling.txt

Douyin_20260608_213500.txt

---

## FR-007 Error Handling

Unsupported URL:

Return:

Unsupported platform

Download failure:

Return:

Failed to download audio

Transcription failure:

Return:

Failed to transcribe audio

Do not crash the application.

---

# UI Changes

Current:

Tab:

- Bilibili URL

Rename:

Tab:

- Video URL

Textbox:

Label:

Paste Video URL

Placeholder:

Bilibili / Douyin / YouTube / Mediasite

No additional tabs required.

---

# Technical Architecture

User Input
↓
extract_url()
↓
detect_platform()
↓
download_audio()
↓
transcribe_audio()
↓
save_transcript()
↓
Display Transcript

---

# Future Roadmap (Not in Scope)

## PRD-004 AI Notes Generator

Transcript
↓
LLM
↓
Markdown Notes

Outputs:

- Summary
- Key Ideas
- Action Items
- Obsidian Markdown

## PRD-005 Batch Processing

Folder
↓
Multiple Videos
↓
Multiple Transcripts

## PRD-006 Obsidian Integration

Automatic export to:

Vault/
├── Transcript
├── Notes
├── Videos

---

# Acceptance Criteria

Case 1

Input:

<https://www.bilibili.com/video/>...

Expected:

Transcript generated
TXT file saved

---

Case 2

Input:

<https://v.douyin.com/xxxxxx/>

Expected:

Transcript generated
TXT file saved

---

Case 3

Input:

Douyin share text + URL

Expected:

URL automatically extracted
Transcript generated

---

Case 4

Input:

Mediasite lecture URL

Expected:

Audio downloaded
Transcript generated
TXT file saved

---

Case 5

Input:

Unsupported URL

Expected:

Graceful error message
No application crash
