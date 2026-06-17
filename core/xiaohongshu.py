from pathlib import Path
import subprocess
from datetime import datetime

from playwright.sync_api import sync_playwright

from core.config import AUDIO_DIR
from core.downloader import _sanitize_stem


def download_xiaohongshu_audio(url: str) -> Path:
    """Download Xiaohongshu video audio using a headless browser to bypass bot detection."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fallback_stem = f"Xiaohongshu_{timestamp}"

    video_url = None
    title = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            viewport={'width': 1280, 'height': 720},
            locale='zh-CN',
        )
        page = context.new_page()

        note_detail = {}

        def on_response(response):
            nonlocal note_detail
            try:
                resp_url = response.url
                if ('/api/sns/web/v1/feed' in resp_url
                        or '/api/sns/web/v2/note' in resp_url
                        or '/api/sns/web/v1/note' in resp_url) and response.status == 200:
                    data = response.json()
                    items = data.get('data', {}).get('items', [])
                    if items:
                        note_detail.update(items[0].get('note_card', {}))
                    elif data.get('data', {}).get('note_card'):
                        note_detail.update(data['data']['note_card'])
            except Exception:
                pass

        cdn_urls: list[str] = []

        def on_request(request):
            u = request.url
            if ('xhscdn.com' in u or 'xhscdn.net' in u) and request.resource_type in ('media', 'xhr', 'fetch', 'other'):
                if '.mp4' in u or '.m3u8' in u or 'video' in u or '/pre_post/' in u or '/spectrum/' in u:
                    cdn_urls.append(u)

        page.on('response', on_response)
        page.on('request', on_request)

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            try:
                page.wait_for_selector('video', timeout=10000)
                page.evaluate('document.querySelector("video")?.play()')
            except Exception:
                pass
            page.wait_for_timeout(5000)

            # Try to extract video source directly from the DOM
            if not cdn_urls:
                try:
                    src = page.evaluate('''() => {
                        const v = document.querySelector("video source");
                        if (v) return v.src;
                        const v2 = document.querySelector("video");
                        if (v2) return v2.src || v2.currentSrc;
                        return null;
                    }''')
                    if src:
                        cdn_urls.append(src)
                except Exception:
                    pass

            # Try to extract title from the page
            if not title:
                try:
                    title = page.evaluate('''() => {
                        const el = document.querySelector("#detail-title")
                            || document.querySelector(".note-content .title")
                            || document.querySelector("[class*='title']");
                        return el ? el.textContent.trim() : null;
                    }''')
                except Exception:
                    pass
        finally:
            browser.close()

    # Extract video URL from API response
    if note_detail:
        video_info = note_detail.get('video', {})
        media = video_info.get('media', {})
        stream = media.get('stream', {})
        # Try h264 streams first
        for quality in ('h264', 'h265', 'av1'):
            streams = stream.get(quality, [])
            if streams and streams[0].get('master_url'):
                video_url = streams[0]['master_url']
                break
            if streams and streams[0].get('backup_urls'):
                video_url = streams[0]['backup_urls'][0]
                break

        if not video_url:
            # Fallback: try consumer.origin_video_key
            origin_key = video_info.get('consumer', {}).get('origin_video_key', '')
            if origin_key:
                video_url = f'https://sns-video-bd.xhscdn.com/{origin_key}'

        if not title:
            title = note_detail.get('title', '') or note_detail.get('desc', '')

    if not video_url and cdn_urls:
        video_url = cdn_urls[0]

    if not video_url:
        raise RuntimeError(
            'Could not extract video URL from Xiaohongshu page. '
            'The note may be image-only, private, or deleted. '
            'Try logging in to Xiaohongshu in Chrome and restart the app.'
        )

    stem = _sanitize_stem(title) if title else ''
    if not stem or len(stem) < 3:
        stem = fallback_stem

    audio_path = AUDIO_DIR / f"{stem}.mp3"

    subprocess.run(
        [
            'ffmpeg', '-y',
            '-user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            '-headers', 'Referer: https://www.xiaohongshu.com/\r\n',
            '-i', video_url,
            '-vn', '-acodec', 'mp3', '-q:a', '2',
            str(audio_path),
        ],
        check=True,
        capture_output=True,
    )

    return audio_path
