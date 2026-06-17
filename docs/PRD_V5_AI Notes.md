# PRD-005 AI Notes Generator

Version

v0.5

⸻

Background

Current workflow:

Video URL
↓
Download Audio
↓
Whisper Transcription
↓
TXT Export

Current output is only a raw transcript.

Although transcription solves the problem of converting audio into text, users still need to manually:

* Read long transcripts
* Remove transcription errors
* Extract key ideas
* Structure information
* Create notes

This process is time-consuming.

The next step is to transform transcripts into structured knowledge.

⸻

Goal

Allow users to generate AI-structured notes from transcripts.

Workflow:

Video
↓
Audio
↓
Transcript
↓
AI Notes
↓
Markdown

Users can choose whether AI processing is required.

AI API calls should only occur after explicit user confirmation.

⸻

User Story

As a user,

I want to optionally generate structured Markdown notes from a transcript,

So that I can quickly extract knowledge from lectures, videos, podcasts and interviews.

⸻

Functional Requirements

FR-001 Optional AI Analysis

After transcription completes:

Display a new button:

Generate AI Notes

AI processing should NOT run automatically.

Reason:

* Reduce API cost
* Avoid unnecessary token usage
* Allow transcript review before analysis

Workflow:

Transcribe
↓
User clicks button
↓
Call LLM
↓
Generate Notes

⸻

FR-002 Model Provider Selection

Support:

* Gemini
* OpenAI GPT

Add dropdown:

AI Provider

Options:

* Gemini
* GPT

Default:

Gemini

Reason:

Current project already supports Gemini API.

⸻

FR-003 Prompt Template

Default Prompt:

根据音频转文字的文本，帮我整理为Markdown笔记。
要求：

1. 修正明显转录错误和错别字
2. 删除重复表达、口头语和无意义内容
3. 提炼核心观点和逻辑结构
4. 使用 Markdown 标题层级整理内容
5. 保留重要数据、结论和案例
6. 输出适合 Obsidian 长期保存的笔记格式
7. 如果内容涉及框架，请整理成结构化框架
8. 如果内容涉及时间节点，请整理为时间线
9. 如果内容涉及投资、金融、AI、销售等主题，请提炼关键结论

Prompt should be stored as:

DEFAULT_SUMMARIZATION_PROMPT

for future customization.

⸻

FR-004 AI Processing Pipeline

Input:

Transcript TXT

Process:

Transcript
↓
Prompt
↓
LLM API
↓
Markdown Notes

Output:

Markdown string

⸻

FR-005 Markdown Export

After generation:

Automatically save:

original.txt
original_notes.md

Example:

Sales_Training.txt
Sales_Training_notes.md

⸻

FR-006 Notes Preview Panel

Add new output area:

AI Notes

UI Layout:

Transcript

AI Notes

Saved File Path

Allow user to copy notes directly.

⸻

FR-007 Long Transcript Handling

Large transcripts may exceed model context limits.

Add automatic chunking.

Workflow:

Long Transcript
↓
Chunk
↓
Summarize Each Chunk
↓
Combine Summaries
↓
Generate Final Notes

Target:

Support transcripts up to:

* 2 hours lecture
* 100,000+ characters

without crashing.

⸻

FR-008 API Configuration

Support:

Gemini

GEMINI_API_KEY

OpenAI

OPENAI_API_KEY

Stored in:

.env

Example:

GEMINI_API_KEY=xxxx
OPENAI_API_KEY=xxxx

⸻

FR-009 Cost Protection

Before API call:

Estimate transcript length.

If transcript exceeds threshold:

Display warning:

Large transcript detected.
Estimated token usage:
XXXX
Continue?

User must confirm.

⸻

FR-010 Error Handling

API Failure

Failed to generate notes.

Rate Limit

API rate limit reached.

Missing API Key

API key not configured.

No application crash.

⸻

UI Changes

Add:

AI Provider Dropdown

Options:

* Gemini
* GPT

Default:

Gemini

⸻

Add:

Generate AI Notes Button

Only enabled after transcript exists.

⸻

Add:

AI Notes Output Box

Markdown display area.

⸻

Architecture

Video URL
↓
Download
↓
Whisper
↓
Transcript TXT
↓
[User Click]
↓
AI Notes Generator
↓
Markdown
↓
notes.md

⸻

Future Extensions

PRD-005 Obsidian Export

Automatically export:

Vault/

Transcript/

Notes/

Resources/

⸻

PRD-006 Prompt Library

Support templates:

* Lecture Notes
* Sales Notes
* Investment Research
* Podcast Summary
* Meeting Minutes
* Interview Notes

Users can select note style before generation.

⸻

Success Criteria

Input:

Video URL

Output:

Transcript TXT

User Clicks:

Generate AI Notes

Output:

Markdown Notes

Saved:

*_notes.md

Supports:

* Gemini
* GPT

Without modifying existing transcription workflow.
