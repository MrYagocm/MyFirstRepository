"""
YouTube scraper using yt-dlp to extract video data, channel stats,
and identify trending content without API quotas.
"""

import json
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from config.settings import DATA_DIR, MAX_RESULTS_PER_SEARCH


class YouTubeScraper:
    """Scrapes YouTube for video/channel data using yt-dlp."""

    def __init__(self):
        self.cache_file = DATA_DIR / "scraper_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            return json.loads(self.cache_file.read_text())
        return {"videos": {}, "channels": {}, "last_updated": None}

    def _save_cache(self):
        self.cache["last_updated"] = datetime.now().isoformat()
        self.cache_file.write_text(json.dumps(self.cache, indent=2))

    def search_videos(self, query: str, max_results: int = MAX_RESULTS_PER_SEARCH,
                      sort_by: str = "relevance") -> list[dict]:
        """Search YouTube and return video metadata."""
        sort_map = {
            "relevance": "",
            "date": "date",
            "views": "view_count",
            "rating": "rating"
        }

        cmd = [
            "yt-dlp",
            f"ytsearch{max_results}:{query}",
            "--dump-json",
            "--no-download",
            "--flat-playlist",
            "--no-warnings",
            "--quiet"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            videos = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        data = json.loads(line)
                        video = self._parse_video_data(data)
                        if video:
                            videos.append(video)
                    except json.JSONDecodeError:
                        continue

            if sort_by == "views":
                videos.sort(key=lambda x: x.get("view_count", 0), reverse=True)

            return videos
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"[Scraper] Error: {e}")
            return []

    def get_video_details(self, video_id: str) -> Optional[dict]:
        """Get full details for a specific video."""
        if video_id in self.cache["videos"]:
            cached = self.cache["videos"][video_id]
            cached_time = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(hours=24):
                return cached

        cmd = [
            "yt-dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "--dump-json",
            "--no-download",
            "--no-warnings",
            "--quiet"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.stdout.strip():
                data = json.loads(result.stdout.strip())
                video = self._parse_video_data(data, full=True)
                if video:
                    video["cached_at"] = datetime.now().isoformat()
                    self.cache["videos"][video_id] = video
                    self._save_cache()
                    return video
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        return None

    def get_channel_videos(self, channel_url: str, max_videos: int = 30) -> list[dict]:
        """Get recent videos from a channel."""
        cmd = [
            "yt-dlp",
            f"{channel_url}/videos",
            "--dump-json",
            "--no-download",
            "--flat-playlist",
            f"--playlist-end={max_videos}",
            "--no-warnings",
            "--quiet"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            videos = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        data = json.loads(line)
                        video = self._parse_video_data(data)
                        if video:
                            videos.append(video)
                    except json.JSONDecodeError:
                        continue
            return videos
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def search_shorts(self, query: str, max_results: int = 20) -> list[dict]:
        """Search specifically for YouTube Shorts."""
        videos = self.search_videos(f"{query} #shorts", max_results=max_results * 2)
        return [v for v in videos if v.get("duration", 999) <= 60][:max_results]

    def get_trending_in_niche(self, niche_keywords: list[str], language: str = "en",
                               max_per_keyword: int = 10) -> list[dict]:
        """Get trending videos across multiple keywords in a niche."""
        all_videos = []
        seen_ids = set()

        for keyword in niche_keywords:
            search_query = keyword
            if language == "es":
                search_query = f"{keyword} español"

            videos = self.search_videos(search_query, max_results=max_per_keyword,
                                        sort_by="views")
            for video in videos:
                vid = video.get("id", "")
                if vid and vid not in seen_ids:
                    seen_ids.add(vid)
                    video["search_keyword"] = keyword
                    all_videos.append(video)

        all_videos.sort(key=lambda x: x.get("view_count", 0), reverse=True)
        return all_videos

    def _parse_video_data(self, data: dict, full: bool = False) -> Optional[dict]:
        """Parse yt-dlp JSON into clean video data."""
        try:
            video = {
                "id": data.get("id", ""),
                "title": data.get("title", ""),
                "channel": data.get("channel", data.get("uploader", "")),
                "channel_id": data.get("channel_id", ""),
                "channel_url": data.get("channel_url", ""),
                "view_count": data.get("view_count", 0),
                "like_count": data.get("like_count", 0),
                "duration": data.get("duration", 0),
                "upload_date": data.get("upload_date", ""),
                "description": data.get("description", "")[:500] if full else "",
                "tags": data.get("tags", [])[:20] if full else [],
                "categories": data.get("categories", []),
                "thumbnail": data.get("thumbnail", ""),
            }

            # Calculate engagement metrics
            views = video["view_count"] or 1
            video["like_ratio"] = (video["like_count"] or 0) / views
            video["is_short"] = (video["duration"] or 0) <= 60

            # Estimate upload age in days
            if video["upload_date"]:
                try:
                    upload = datetime.strptime(video["upload_date"], "%Y%m%d")
                    video["days_since_upload"] = (datetime.now() - upload).days
                    if video["days_since_upload"] > 0:
                        video["views_per_day"] = views / video["days_since_upload"]
                    else:
                        video["views_per_day"] = views
                except ValueError:
                    video["days_since_upload"] = None
                    video["views_per_day"] = None

            return video
        except Exception:
            return None

    def estimate_channel_size(self, channel_videos: list[dict]) -> dict:
        """Estimate channel metrics from video data."""
        if not channel_videos:
            return {"estimated_subscribers": 0, "avg_views": 0, "consistency": 0}

        views = [v.get("view_count", 0) for v in channel_videos]
        avg_views = sum(views) / len(views)

        # Rough subscriber estimate: avg views * 3-5x
        est_subs = int(avg_views * 4)

        # Consistency: how regular are uploads
        dates = []
        for v in channel_videos:
            if v.get("upload_date"):
                try:
                    dates.append(datetime.strptime(v["upload_date"], "%Y%m%d"))
                except ValueError:
                    continue

        consistency = 0
        if len(dates) >= 2:
            dates.sort()
            gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            avg_gap = sum(gaps) / len(gaps)
            consistency = max(0, min(100, int(100 - avg_gap * 5)))  # Higher = more consistent

        return {
            "estimated_subscribers": est_subs,
            "avg_views": int(avg_views),
            "median_views": int(sorted(views)[len(views)//2]),
            "max_views": max(views),
            "total_videos_analyzed": len(channel_videos),
            "consistency_score": consistency
        }
