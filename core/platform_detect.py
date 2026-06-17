import re


def extract_url(text: str) -> str:
    """Extract first HTTP/HTTPS URL from text (handles Douyin share messages)."""
    match = re.search(r'https?://[^\s　-〿＀-￯]+', text)
    if match:
        url = match.group(0).rstrip('。，、；：！？…》】）')
        return url
    return text.strip()


def detect_platform(url: str) -> str:
    """Detect video platform from URL. Returns: bilibili | douyin | youtube | mediasite | unknown"""
    lower = url.lower()
    if 'bilibili.com' in lower or 'b23.tv' in lower:
        return 'bilibili'
    if 'douyin.com' in lower:
        return 'douyin'
    if 'youtube.com' in lower or 'youtu.be' in lower:
        return 'youtube'
    if 'mediasite' in lower:
        return 'mediasite'
    return 'unknown'
