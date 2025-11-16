
# src/youtube_fetch.py
import os
import re
import requests
from datetime import timedelta
import isodate
import json
from time import time

CACHE_FILE = os.environ.get('YT_CACHE_FILE', 'data/yt_cache.json')
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

YT_API_KEY = os.environ.get('YT_API_KEY')  # set this in env or Streamlit secrets

VIDEO_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"
CATEGORIES_URL = "https://www.googleapis.com/youtube/v3/videoCategories"

def _load_cache():
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def extract_video_id(url_or_id: str) -> str or None:
    s = (url_or_id or "").strip()
    if not s:
        return None
    patterns = [
        r"v=([A-Za-z0-9_-]{11})",
        r"youtu\\.be/([A-Za-z0-9_-]{11})",
        r"youtube\\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\\.com/v/([A-Za-z0-9_-]{11})"
    ]
    for p in patterns:
        m = re.search(p, s)
        if m:
            return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    return None

def parse_iso_duration_to_minutes(iso_duration: str) -> float or None:
    try:
        dur = isodate.parse_duration(iso_duration)
        if isinstance(dur, timedelta):
            return dur.total_seconds() / 60.0
    except Exception:
        pass
    return None

def fetch_video_metadata(video_id: str, api_key: str or None = None, use_cache=True) -> dict or None:
    key = api_key or YT_API_KEY
    if not key:
        raise RuntimeError("YouTube API key not provided. Set YT_API_KEY environment variable or pass api_key.")
    cache = _load_cache() if use_cache else {}
    cache_key = f"video:{video_id}"
    if use_cache and cache_key in cache:
        meta = cache[cache_key]
        if time() - meta.get('_fetched_at', 0) < 86400:
            return meta['data']
    params = {
        "part": "snippet,contentDetails,statistics",
        "id": video_id,
        "key": key
    }
    r = requests.get(VIDEO_DETAILS_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    if not items:
        return None
    it = items[0]
    snippet = it.get("snippet", {})
    stats = it.get("statistics", {})
    content = it.get("contentDetails", {})

    duration_iso = content.get("duration")
    duration_minutes = parse_iso_duration_to_minutes(duration_iso) if duration_iso else None

    meta = {
        "video_id": video_id,
        "title": snippet.get("title"),
        "publishedAt": snippet.get("publishedAt"),
        "categoryId": snippet.get("categoryId"),
        "channelId": snippet.get("channelId"),
        "viewCount": int(stats.get("viewCount", 0)) if stats.get("viewCount") is not None else None,
        "likeCount": int(stats.get("likeCount", 0)) if stats.get("likeCount") is not None else None,
        "commentCount": int(stats.get("commentCount", 0)) if stats.get("commentCount") is not None else None,
        "duration_minutes": duration_minutes
    }
    if use_cache:
        cache[cache_key] = {'data': meta, '_fetched_at': time()}
        _save_cache(cache)
    return meta

def fetch_channel_subscribers(channel_id: str, api_key: str or None = None, use_cache=True) -> int or None:
    key = api_key or YT_API_KEY
    if not key:
        raise RuntimeError("YouTube API key not provided.")
    cache = _load_cache() if use_cache else {}
    cache_key = f"channel:{channel_id}"
    if use_cache and cache_key in cache:
        meta = cache[cache_key]
        if time() - meta.get('_fetched_at', 0) < 86400:
            return meta['data'].get('subscriberCount')
    params = {
        "part": "statistics",
        "id": channel_id,
        "key": key
    }
    r = requests.get(CHANNELS_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    if not items:
        return None
    stats = items[0].get("statistics", {})
    subs = int(stats.get("subscriberCount", 0)) if stats.get("subscriberCount") is not None else None
    if use_cache:
        cache[cache_key] = {'data': {'subscriberCount': subs}, '_fetched_at': time()}
        _save_cache(cache)
    return subs

def fetch_category_map(region_code='US', api_key: str or None = None, use_cache=True) -> dict:
    key = api_key or YT_API_KEY
    if not key:
        return {}
    cache = _load_cache() if use_cache else {}
    cache_key = f"categories:{region_code}"
    if use_cache and cache_key in cache and time() - cache[cache_key].get('_fetched_at', 0) < 86400:
        return cache[cache_key]['data']
    params = {"part": "snippet", "regionCode": region_code, "key": key}
    r = requests.get(CATEGORIES_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    items = data.get('items', [])
    mapping = {}
    for it in items:
        cid = it.get('id')
        title = it.get('snippet', {}).get('title')
        if cid and title:
            mapping[cid] = title
    if use_cache:
        cache[cache_key] = {'data': mapping, '_fetched_at': time()}
        _save_cache(cache)
    return mapping

def build_feature_row_from_video(video_meta: dict, retention_rate: float = 0.30, category_map=None) -> dict:
    v = video_meta or {}
    views = v.get("viewCount") or 0
    likes = v.get("likeCount") or 0
    comments = v.get("commentCount") or 0
    video_length_minutes = v.get("duration_minutes") or None

    if video_length_minutes:
        avg_watch_minutes = video_length_minutes * float(retention_rate)
        watch_time_minutes = views * avg_watch_minutes
    else:
        watch_time_minutes = views * 0.02

    cid = v.get('categoryId')
    category = (category_map.get(cid) if category_map and cid in category_map else f"cat_{cid}" ) if cid else "Unknown"
    device = "Mobile"
    country = "US"

    return {
        "video_id": v.get("video_id"),
        "views": views,
        "likes": likes,
        "comments": comments,
        "watch_time_minutes": watch_time_minutes,
        "video_length_minutes": video_length_minutes if video_length_minutes is not None else 0.0,
        "subscribers": None,
        "category": category,
        "device": device,
        "country": country,
        "publishedAt": v.get("publishedAt")
    }
