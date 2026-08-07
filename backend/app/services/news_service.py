from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree

import httpx

NEWS_FEED_URL = "https://www.yna.co.kr/rss/economy.xml"
CACHE_TTL = timedelta(minutes=10)

_cache: dict[str, object] = {"items": None, "fetched_at": None}


def _parse_feed(xml_text: str, limit: int) -> list[dict]:
    root = ElementTree.fromstring(xml_text)
    items = []
    for item in root.findall("./channel/item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        published = (item.findtext("pubDate") or "").strip()
        if title and link:
            items.append({"title": title, "link": link, "published": published})
    return items


def get_news(limit: int = 5) -> list[dict]:
    now = datetime.now(timezone.utc)
    fetched_at = _cache["fetched_at"]
    is_fresh = fetched_at is not None and now - fetched_at < CACHE_TTL

    if is_fresh and _cache["items"] is not None:
        return _cache["items"][:limit]

    try:
        response = httpx.get(NEWS_FEED_URL, timeout=5.0, follow_redirects=True)
        response.raise_for_status()
        items = _parse_feed(response.text, limit=20)
        _cache["items"] = items
        _cache["fetched_at"] = now
    except (httpx.HTTPError, ElementTree.ParseError):
        items = _cache["items"] or []

    return items[:limit]