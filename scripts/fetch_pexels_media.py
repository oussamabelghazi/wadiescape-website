#!/usr/bin/env python3
"""
Download free-license Oman-themed photos and hero-quality videos from Pexels.

Uses only the Python standard library (no pip install needed).

Usage:
    PEXELS_API_KEY="your-key-here" python3 scripts/fetch_pexels_media.py

Output goes to <project-root>/images/<category-slug>/ for photos and
<project-root>/images/hero-videos/ for video candidates. This folder is
a raw pull from Pexels for review — the best picks get copied/optimized
into assets/images/ and wired into the site separately.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_KEY = os.environ.get("PEXELS_API_KEY")
if not API_KEY:
    sys.exit("Set the PEXELS_API_KEY environment variable before running this script.")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "images")

# Each category tries its primary "Oman ..." query first, then falls back to
# a broader term if Pexels doesn't have enough Oman-tagged results.
PHOTO_CATEGORIES = {
    "oman-desert": ["Oman desert", "desert dunes"],
    "oman-mosque": ["Oman mosque", "islamic mosque architecture"],
    "oman-wadi-canyon": ["Oman wadi canyon", "canyon river pool"],
    "oman-diving-underwater": ["Oman diving underwater", "scuba diving coral reef"],
    "oman-mountains-jabal-akhdar": ["Oman mountains Jabal Akhdar", "green mountain terraces"],
    "oman-traditional-souk": ["Oman traditional souk", "arab market souk"],
}
PHOTOS_PER_CATEGORY = 8

VIDEO_SEARCH_TERMS = ["Oman desert aerial", "desert dunes aerial drone", "coastline aerial drone"]
VIDEOS_TO_FETCH = 3

# Pexels sits behind Cloudflare, which blocks Python's default urllib User-Agent
# (error code 1010) — a browser-like UA is required on every request.
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
HEADERS = {"Authorization": API_KEY, "User-Agent": USER_AGENT}


def api_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_file(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def search_photos(query, per_page):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": per_page, "orientation": "landscape"}
    )
    return api_get(url)


def fetch_category_photos(slug, queries, count):
    out_dir = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)

    collected, seen_ids = [], set()
    for query in queries:
        if len(collected) >= count:
            break
        try:
            data = search_photos(query, per_page=count)
        except urllib.error.HTTPError as e:
            print(f"  ! search failed for '{query}': {e}")
            continue
        for photo in data.get("photos", []):
            if photo["id"] in seen_ids:
                continue
            seen_ids.add(photo["id"])
            collected.append(photo)
            if len(collected) >= count:
                break

    downloaded = []
    for i, photo in enumerate(collected[:count], start=1):
        src = photo["src"]["large2x"]  # ~1880px wide, high-res but web-reasonable
        photographer = (photo.get("photographer") or "unknown").replace(" ", "-")
        fname = f"{slug}-{i:02d}-{photographer}.jpg"
        dest = os.path.join(out_dir, fname)
        try:
            download_file(src, dest)
            downloaded.append(dest)
            print(f"  [{slug}] saved {fname}")
        except Exception as e:
            print(f"  ! failed to download photo {photo['id']}: {e}")
        time.sleep(0.3)
    return downloaded


def search_videos(query, per_page):
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": per_page, "orientation": "landscape"}
    )
    return api_get(url)


def fetch_hero_videos(queries, count):
    out_dir = os.path.join(OUTPUT_DIR, "hero-videos")
    os.makedirs(out_dir, exist_ok=True)

    collected, seen_ids = [], set()
    for query in queries:
        if len(collected) >= count:
            break
        try:
            data = search_videos(query, per_page=count)
        except urllib.error.HTTPError as e:
            print(f"  ! video search failed for '{query}': {e}")
            continue
        for video in data.get("videos", []):
            if video["id"] in seen_ids:
                continue
            seen_ids.add(video["id"])
            collected.append(video)
            if len(collected) >= count:
                break

    downloaded = []
    for i, video in enumerate(collected[:count], start=1):
        mp4_files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4"]
        mp4_files.sort(key=lambda f: abs((f.get("width") or 0) - 1920))
        if not mp4_files:
            continue
        best = mp4_files[0]
        fname = f"hero-video-{i:02d}-{video['id']}.mp4"
        dest = os.path.join(out_dir, fname)
        try:
            download_file(best["link"], dest)
            downloaded.append(dest)
            print(f"  [hero-videos] saved {fname} ({best.get('width')}x{best.get('height')})")
        except Exception as e:
            print(f"  ! failed to download video {video['id']}: {e}")
        time.sleep(0.3)
    return downloaded


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = {}

    print("=== Fetching photos ===")
    for slug, queries in PHOTO_CATEGORIES.items():
        print(f"\n-- {slug} --")
        summary[slug] = len(fetch_category_photos(slug, queries, PHOTOS_PER_CATEGORY))

    print("\n=== Fetching hero videos ===")
    summary["hero-videos"] = len(fetch_hero_videos(VIDEO_SEARCH_TERMS, VIDEOS_TO_FETCH))

    print("\n=== Summary ===")
    for slug, n in summary.items():
        print(f"{slug}: {n} files")


if __name__ == "__main__":
    main()
