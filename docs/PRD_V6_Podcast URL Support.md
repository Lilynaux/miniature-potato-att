PRD-006 Apple Podcasts & RSS Feed Support

Background

Current supported platforms:

* Bilibili
* Douyin
* Xiaohongshu
* YouTube
* Mediasite

The application is evolving into a universal knowledge extraction platform.

A growing amount of high-quality learning content comes from:

* Apple Podcasts
* Podcast RSS Feeds
* Long-form interviews
* Finance podcasts
* AI podcasts
* Business podcasts

Users want to transcribe podcast episodes and generate structured notes.

⸻

Goal

Allow users to paste either:

* Apple Podcasts episode URLs
* Podcast RSS feeds

The system should automatically extract the audio source and generate transcripts.

Workflow:

Apple Podcast URL / RSS Feed
↓
Resolve Episode
↓
Extract Audio Source
↓
Download Audio
↓
Whisper
↓
Transcript
↓
AI Notes (Optional)

⸻

User Story

As a user,

I want to paste an Apple Podcasts episode URL or a podcast RSS feed,

So that the system automatically downloads the episode audio and generates a transcript.

Examples:

Apple Podcast Episode:

<https://podcasts.apple.com/gb/podcast/铜镜/id1843128942?i=1000773573423>

Podcast RSS Feed:

<https://feeds.megaphone.fm/…>

⸻

Functional Requirements

FR-001 Platform Detection

Update:

detect_platform(url)

Current:

* bilibili
* douyin
* xiaohongshu
* youtube
* mediasite
* unknown

Add:

* apple_podcast
* podcast_rss

Detection rules:

if "podcasts.apple.com" in url:
    return "apple_podcast"
if "feeds." in url:
    return "podcast_rss"

⸻

FR-002 Podcast URL Support

Supported URL types:

Episode URL

<https://podcasts.apple.com/…>

Example:

<https://podcasts.apple.com/gb/podcast/铜镜/id1843128942?i=1000773573423>

Podcast Show URL

<https://podcasts.apple.com/…/idxxxx>

Mobile Share URL

podcasts.apple.com/…

⸻

FR-003 RSS Feed Support

Supported RSS examples:

<https://feeds.megaphone.fm/>...
<https://rss.art19.com/>...
<https://feeds.simplecast.com/>...

System should:

1. Parse RSS XML
2. Extract episodes
3. Extract audio enclosure URL
4. Download audio

⸻

FR-004 Apple Podcast Resolution

Apple Podcasts typically do not host audio directly.

System should:

1. Parse Apple Podcast page
2. Locate RSS feed
3. Locate episode
4. Extract audio URL

Workflow:

Apple Podcast URL
↓
RSS Feed
↓
Audio URL
↓
Download

⸻

FR-005 Audio Download

Reuse existing downloader pipeline.

Supported source formats:

* mp3
* m4a
* aac

Convert automatically to:

mp3

for Whisper compatibility.

Expected output:

audio_path

⸻

FR-006 Metadata Extraction

Extract:

* Podcast Name
* Episode Title
* Publication Date

Use metadata as filename.

Example:

铜镜_铜价周期解析.mp3
铜镜_铜价周期解析.txt
铜镜_铜价周期解析_notes.md

Fallback:

Podcast_20260623_143000

⸻

FR-007 Long Audio Handling

Podcast episodes often exceed:

* 30 minutes
* 60 minutes
* 120 minutes

Requirements:

* Stream download
* Chunked transcription
* Memory-safe processing

Target:

Support:

≤ 3 hours

without crashing.

⸻

FR-008 Transcript Generation

No changes required.

Pipeline:

Audio
↓
Whisper
↓
Transcript TXT

⸻

FR-009 AI Notes Integration

Compatible with PRD-004.

Workflow:

Transcript
↓
Generate AI Notes
↓
Markdown

Supported Providers:

* Gemini
* GPT

⸻

FR-010 Progress Display

Display:

Resolving podcast source...
Downloading episode...
Transcribing...
Generating notes...
Completed.

⸻

FR-011 Error Handling

Episode unavailable:

Podcast episode unavailable.

RSS unavailable:

Unable to resolve RSS feed.

Audio download failed:

Failed to download audio.

Unsupported podcast source:

Unsupported podcast source.

No application crash.

⸻

UI Changes

Current:

Paste Video URL

Update:

Paste Video / Podcast URL

Placeholder:

Bilibili / Douyin / Xiaohongshu / YouTube / Mediasite / Apple Podcasts / RSS Feed

⸻

Success Criteria

Input:

Apple Podcast Episode URL

Example:

<https://podcasts.apple.com/gb/podcast/铜镜/id1843128942?i=1000773573423>

Output:

* Audio downloaded
* Transcript generated
* TXT exported

Input:

RSS Feed URL

Example:

<https://feeds.megaphone.fm/…>

Output:

* Feed resolved
* Episode audio downloaded
* Transcript generated

Optional:

* AI Notes generated
* Markdown exported

Without additional user configuration.
