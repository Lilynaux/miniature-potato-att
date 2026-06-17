# PRD-004 Xiaohongshu (RED) Platform Support

Background

Current application supports:

* Bilibili
* Douyin
* YouTube
* Mediasite

When unsupported URLs are provided:

Unsupported platform.
Supported: Bilibili, Douyin, YouTube, Mediasite.

The application is increasingly used as a personal knowledge extraction tool.

A significant portion of learning content now originates from Xiaohongshu (RED), including:

* Sales training
* Career advice
* Finance content
* Industry analysis
* AI tutorials
* Personal growth content

Therefore Xiaohongshu should become a first-class supported platform.

⸻

Goal

Allow users to paste Xiaohongshu URLs directly.

The system should:

Xiaohongshu URL
↓
Download audio
↓
Transcribe
↓
Export transcript

without requiring any manual preprocessing.

⸻

User Story

As a user,

I want to paste a Xiaohongshu note URL,

So that the system automatically downloads audio and generates a transcript.

Example:

<https://www.xiaohongshu.com/explore/6a320b32000000001603cc14>

⸻

Functional Requirements

FR-001 Platform Detection

Update:

detect_platform(url)

Current:

bilibili
douyin
youtube
mediasite
unknown

New:

bilibili
douyin
youtube
mediasite
xiaohongshu
unknown

Detection rules:

if "xiaohongshu.com" in url:
    return "xiaohongshu"
if "xhslink.com" in url:
    return "xiaohongshu"

Support:

* <www.xiaohongshu.com>
* xhslink.com

⸻

FR-002 Xiaohongshu Share Text Parsing

Users frequently paste share text instead of raw URLs.

Example:

【标题】
<https://www.xiaohongshu.com/explore/xxxx>
复制本条信息，打开小红书查看

System should:

1. Extract URL automatically
2. Ignore surrounding text
3. Continue processing

Implementation:

extract_url(text)

Use regex URL extraction.

⸻

FR-003 Audio Download Support

Update:

download_audio(url, platform)

Add:

platform == "xiaohongshu"

Expected behavior:

Use existing yt-dlp workflow.

Target output:

.mp3

No additional user interaction required.

⸻

FR-004 Metadata Extraction

Attempt to retrieve:

* Note title
* Author name

Use metadata as filename.

Priority:

Title
↓
Platform + Timestamp

Example:

Sales_Closing_Techniques.mp3
Sales_Closing_Techniques.txt

Fallback:

Xiaohongshu_20260617_120000.mp3

⸻

FR-005 Error Handling

Possible scenarios:

Case A

Private note

Return:

This Xiaohongshu note is not publicly accessible.

⸻

Case B

Deleted note

Return:

Note unavailable.

⸻

Case C

Download failure

Return:

Failed to download audio.

Do not crash application.

⸻

FR-006 Transcript Workflow

No changes required.

Existing pipeline remains:

URL
↓
Download
↓
Whisper
↓
TXT

⸻

UI Changes

No new tabs.

Update placeholder:

Current:

Bilibili / Douyin / YouTube / Mediasite

New:

Bilibili / Douyin / Xiaohongshu / YouTube / Mediasite

⸻

Testing

Test Case 1

Input:

<https://www.xiaohongshu.com/explore/xxxxxxxx>

Expected:

* Platform detected
* Audio downloaded
* Transcript generated

⸻

Test Case 2

Input:

Share text + URL

Expected:

* URL extracted
* Transcript generated

⸻

Test Case 3

Input:

Deleted note

Expected:

* Graceful error message

⸻

Future Roadmap

PRD-004 AI Note Generator

Transcript
↓
LLM
↓
Markdown Note

Outputs:

* Summary
* Key Insights
* Frameworks
* Action Items

⸻

PRD-005 Obsidian Integration

Transcript
↓
AI Notes
↓
Auto-save into Vault

Folder structure:

Transcript/
Notes/
Resources/

⸻

Success Criteria

User can paste a Xiaohongshu URL and receive:

* Downloaded audio
* Generated transcript
* Saved TXT file

without any platform-specific configuration.
