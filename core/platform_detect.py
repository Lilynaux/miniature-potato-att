import re


def extract_url(text: str) -> str:
    """Extract first HTTP/HTTPS URL from text (handles Douyin share messages)."""
    match = re.search(r'https?://[^\s　-〿＀-￯]+', text)
    if match:
        url = match.group(0).rstrip('。，、；：！？…》】）')
        return url
    return text.strip()


def detect_platform(url: str) -> str:
    """Detect media platform from URL."""
    lower = url.lower()
    if 'podcasts.apple.com' in lower:
        return 'apple_podcast'
    if 'feeds.' in lower or 'rss.' in lower or '/rss' in lower:
        return 'podcast_rss'
    if 'bilibili.com' in lower or 'b23.tv' in lower:
        return 'bilibili'
    if 'douyin.com' in lower:
        return 'douyin'
    if 'xiaohongshu.com' in lower or 'xhslink.com' in lower:
        return 'xiaohongshu'
    if 'youtube.com' in lower or 'youtu.be' in lower:
        return 'youtube'
    if 'mediasite' in lower:
        return 'mediasite'
    return 'unknown'
