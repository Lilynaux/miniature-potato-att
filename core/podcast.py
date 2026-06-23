from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
from urllib.error import URLError
from urllib.parse import parse_qs, quote, urlparse, urlunparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from core.config import AUDIO_DIR
from core.downloader import _sanitize_stem


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


@dataclass
class PodcastEpisode:
    podcast_name: str
    episode_title: str
    pub_date: str
    audio_url: str


class _ApplePodcastHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "meta":
            prop = attr.get("property") or attr.get("name")
            content = attr.get("content", "")
            if prop == "og:title" and content:
                self.title = content


def _normalize_url(url: str) -> str:
    url = url.strip()
    if url.startswith("//"):
        url = f"https:{url}"
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urlparse(url)
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc.encode("idna").decode("ascii"),
            quote(parsed.path, safe="/%:"),
            parsed.params,
            quote(parsed.query, safe="=&%:/?+"),
            quote(parsed.fragment, safe="=&%:/?+"),
        )
    )


def _fetch_text(url: str) -> str:
    request = Request(_normalize_url(url), headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _fetch_json(url: str) -> dict:
    return json.loads(_fetch_text(url))


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(element: ET.Element, name: str) -> str:
    for child in element:
        if _local_name(child.tag) == name and child.text:
            return child.text.strip()
    return ""


def _find_audio_enclosure(item: ET.Element) -> str:
    for child in item:
        if _local_name(child.tag) != "enclosure":
            continue
        media_type = child.attrib.get("type", "")
        enclosure_url = child.attrib.get("url", "")
        if enclosure_url and (media_type.startswith("audio/") or _looks_like_audio_url(enclosure_url)):
            return enclosure_url
    return ""


def _looks_like_audio_url(url: str) -> bool:
    lowered = url.lower().split("?", 1)[0]
    return lowered.endswith((".mp3", ".m4a", ".aac", ".wav", ".ogg"))


def _episode_matches(item: ET.Element, apple_episode_id: str, apple_title: str) -> bool:
    if not apple_episode_id and not apple_title:
        return False

    item_title = _child_text(item, "title")
    guid = _child_text(item, "guid")
    link = _child_text(item, "link")
    enclosure = _find_audio_enclosure(item)
    haystack = " ".join([guid, link, enclosure])

    if apple_episode_id and apple_episode_id in haystack:
        return True
    if apple_title and item_title:
        return _clean_title(apple_title) == _clean_title(item_title)
    return False


def _clean_title(title: str) -> str:
    return " ".join(title.lower().replace(" - apple podcasts", "").split())


def _parse_rss_feed(feed_xml: str, episode_id: str = "", episode_title: str = "") -> PodcastEpisode:
    root = ET.fromstring(feed_xml)
    channel = root.find("channel")
    if channel is None:
        channel = root

    podcast_name = _child_text(channel, "title") or "Podcast"
    items = [child for child in channel if _local_name(child.tag) == "item"]
    if not items:
        raise RuntimeError("RSS feed contains no podcast episodes.")

    selected = None
    for item in items:
        if _episode_matches(item, episode_id, episode_title):
            selected = item
            break
    if selected is None:
        selected = items[0]

    audio_url = _find_audio_enclosure(selected)
    if not audio_url:
        raise RuntimeError("Could not find an audio enclosure URL in the RSS episode.")

    return PodcastEpisode(
        podcast_name=podcast_name,
        episode_title=_child_text(selected, "title") or "Episode",
        pub_date=_child_text(selected, "pubDate"),
        audio_url=audio_url,
    )


def _extract_apple_ids(url: str) -> tuple[str, str, str]:
    parsed = urlparse(_normalize_url(url))
    path_parts = [part for part in parsed.path.split("/") if part]
    country = path_parts[0] if path_parts else "us"
    show_id = ""
    for part in path_parts:
        if part.startswith("id") and part[2:].isdigit():
            show_id = part[2:]
            break
    episode_id = parse_qs(parsed.query).get("i", [""])[0]
    return country, show_id, episode_id


def _resolve_apple_feed_url(url: str) -> tuple[str, str, str]:
    country, show_id, episode_id = _extract_apple_ids(url)
    if not show_id:
        raise RuntimeError("Could not find the Apple Podcasts show id in the URL.")

    lookup_url = f"https://itunes.apple.com/lookup?id={show_id}&country={country}"
    data = _fetch_json(lookup_url)
    results = data.get("results", [])
    feed_url = results[0].get("feedUrl", "") if results else ""
    if not feed_url:
        raise RuntimeError("Could not resolve RSS feed from Apple Podcasts.")

    try:
        page_title = _resolve_apple_episode_title(episode_id, country) if episode_id else ""
    except (URLError, TimeoutError, RuntimeError, json.JSONDecodeError):
        page_title = ""
    try:
        parser = _ApplePodcastHTMLParser()
        parser.feed(_fetch_text(url))
        page_title = page_title or parser.title
    except (URLError, TimeoutError, RuntimeError):
        pass

    return feed_url, episode_id, page_title


def _resolve_apple_episode_title(episode_id: str, country: str) -> str:
    lookup_url = f"https://itunes.apple.com/lookup?id={episode_id}&country={country}"
    data = _fetch_json(lookup_url)
    results = data.get("results", [])
    return results[0].get("trackName", "") if results else ""


def resolve_podcast_episode(url: str, platform: str) -> PodcastEpisode:
    if platform == "apple_podcast":
        feed_url, episode_id, episode_title = _resolve_apple_feed_url(url)
        return _parse_rss_feed(_fetch_text(feed_url), episode_id, episode_title)

    return _parse_rss_feed(_fetch_text(url))


def _podcast_stem(episode: PodcastEpisode) -> str:
    name = _sanitize_stem(episode.podcast_name)
    title = _sanitize_stem(episode.episode_title)
    stem = "_".join(part for part in (name, title) if part)
    if stem:
        return stem[:120]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"Podcast_{timestamp}"


def download_podcast_audio(url: str, platform: str) -> Path:
    episode = resolve_podcast_episode(url, platform)
    audio_path = AUDIO_DIR / f"{_podcast_stem(episode)}.mp3"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-user_agent", USER_AGENT,
            "-i", episode.audio_url,
            "-vn", "-acodec", "mp3", "-q:a", "2",
            str(audio_path),
        ],
        check=True,
        capture_output=True,
    )

    return audio_path
