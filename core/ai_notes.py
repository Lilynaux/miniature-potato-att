from pathlib import Path

from core.config import NOTES_DIR, GEMINI_API_KEY, OPENAI_API_KEY

DEFAULT_SUMMARIZATION_PROMPT = """根据音频转文字的文本，帮我整理为Markdown笔记。
要求：

1. 修正明显转录错误和错别字
2. 删除重复表达、口头语和无意义内容
3. 提炼核心观点和逻辑结构
4. 使用 Markdown 标题层级整理内容
5. 保留重要数据、结论和案例
6. 输出适合 Obsidian 长期保存的笔记格式
7. 如果内容涉及框架，请整理成结构化框架
8. 如果内容涉及时间节点，请整理为时间线
9. 如果内容涉及投资、金融、AI、销售等主题，请提炼关键结论"""

CHUNK_SIZE = 30000
COMBINE_PROMPT = "请将以下多段笔记合并为一篇完整、结构清晰的 Markdown 笔记，去除重复内容，保持逻辑连贯：\n\n"


def estimate_tokens(text: str) -> int:
    cn_chars = sum(1 for c in text if '一' <= c <= '鿿')
    other_chars = len(text) - cn_chars
    return cn_chars * 2 + other_chars // 3


def _chunk_text(text: str) -> list[str]:
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    lines = text.split('\n')
    current = []
    current_len = 0
    for line in lines:
        if current_len + len(line) > CHUNK_SIZE and current:
            chunks.append('\n'.join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line) + 1
    if current:
        chunks.append('\n'.join(current))
    return chunks


def _call_gemini(prompt: str, text: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("API key not configured. Set GEMINI_API_KEY in .env file.")
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{prompt}\n\n{text}",
    )
    return response.text


def _call_openai(prompt: str, text: str) -> str:
    if not OPENAI_API_KEY:
        raise ValueError("API key not configured. Set OPENAI_API_KEY in .env file.")
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content


PROVIDERS = {
    "Gemini": _call_gemini,
    "GPT": _call_openai,
}


def generate_notes(transcript: str, provider: str = "Gemini") -> str:
    call_fn = PROVIDERS.get(provider)
    if not call_fn:
        raise ValueError(f"Unknown provider: {provider}")

    chunks = _chunk_text(transcript)

    if len(chunks) == 1:
        return call_fn(DEFAULT_SUMMARIZATION_PROMPT, chunks[0])

    summaries = []
    for i, chunk in enumerate(chunks):
        chunk_prompt = f"{DEFAULT_SUMMARIZATION_PROMPT}\n\n（第 {i+1}/{len(chunks)} 部分）"
        summaries.append(call_fn(chunk_prompt, chunk))

    combined = "\n\n---\n\n".join(summaries)
    return call_fn(COMBINE_PROMPT, combined)


def save_notes(transcript_path: str, notes: str) -> Path:
    stem = Path(transcript_path).stem.removesuffix("_notes")
    output_path = NOTES_DIR / f"{stem}_notes.md"
    output_path.write_text(notes, encoding="utf-8")
    return output_path
