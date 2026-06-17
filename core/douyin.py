from pathlib import Path
import subprocess
from datetime import datetime

from playwright.sync_api import sync_playwright

from config import AUDIO_DIR
from downloader import _sanitize_stem


def download_douyin_audio(url: str) -> Path:
    """Download Douyin audio using a headless browser to bypass bot detection."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fallback_stem = f"Douyin_{timestamp}"

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

        # Intercept responses from Douyin's detail API
        aweme_detail = {}

        def on_response(response):
            nonlocal aweme_detail
            if 'aweme/v1/web/aweme/detail' in response.url and response.status == 200:
                try:
                    data = response.json()
                    aweme_detail = data.get('aweme_detail') or {}
                except Exception:
                    pass

        # Also intercept CDN video requests as fallback
        cdn_urls: list[str] = []

        def on_request(request):
            u = request.url
            if ('douyinvod.com' in u or 'amemv.com' in u) and request.resource_type == 'media':
                cdn_urls.append(u)

        page.on('response', on_response)
        page.on('request', on_request)

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            # Give time for the API call and media to start loading
            try:
                page.wait_for_selector('video', timeout=10000)
                page.evaluate('document.querySelector("video")?.play()')
            except Exception:
                pass
            page.wait_for_timeout(4000)
        finally:
            browser.close()

    # Extract video URL from API response
    if aweme_detail:
        play_urls = (
            aweme_detail.get('video', {})
            .get('play_addr', {})
            .get('url_list', [])
        )
        if play_urls:
            video_url = play_urls[0]
        title = aweme_detail.get('desc', '')

    # Fallback to intercepted CDN URL
    if not video_url and cdn_urls:
        video_url = cdn_urls[0]

    if not video_url:
        raise RuntimeError(
            'Could not extract video URL from Douyin page. '
            'The page may have loaded with bot detection. '
            'Try logging in to Douyin in Chrome and restart the app.'
        )

    stem = _sanitize_stem(title) if title else ''
    if not stem or len(stem) < 3:
        stem = fallback_stem

    video_path = AUDIO_DIR / f"{stem}_tmp.mp4"
    audio_path = AUDIO_DIR / f"{stem}.mp3"

    # Download with ffmpeg (handles Douyin's CDN directly)
    subprocess.run(
        [
            'ffmpeg', '-y',
            '-user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            '-headers', 'Referer: https://www.douyin.com/\r\n',
            '-i', video_url,
            '-vn', '-acodec', 'mp3', '-q:a', '2',
            str(audio_path),
        ],
        check=True,
        capture_output=True,
    )

    return audio_path
