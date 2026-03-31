"""
Trend detector: identifies rising topics and viral opportunities
using YouTube search suggestions and video velocity analysis.
"""

import json
import subprocess
import urllib.parse
from datetime import datetime
from typing import Optional

import requests

from config.settings import DATA_DIR
from .youtube_scraper import YouTubeScraper


class TrendDetector:
    """Detects trending topics and emerging content opportunities."""

    def __init__(self):
        self.scraper = YouTubeScraper()
        self.trends_file = DATA_DIR / "trends.json"

    def get_youtube_suggestions(self, seed_query: str) -> list[str]:
        """Get YouTube autocomplete suggestions for a query."""
        url = "https://suggestqueries-clients6.youtube.com/complete/search"
        params = {
            "client": "youtube",
            "q": seed_query,
            "ds": "yt"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                # Response is JSONP, extract JSON
                text = response.text
                start = text.index("(") + 1
                end = text.rindex(")")
                data = json.loads(text[start:end])
                if data and len(data) > 1:
                    return [item[0] for item in data[1] if isinstance(item, list)]
        except Exception:
            pass
        return []

    def detect_rising_topics(self, niche_keywords: list[str], language: str = "en") -> list[dict]:
        """Find topics that are gaining traction but not yet saturated."""
        rising = []

        for keyword in niche_keywords:
            suggestions = self.get_youtube_suggestions(keyword)

            for suggestion in suggestions:
                # Search for videos on this suggestion
                videos = self.scraper.search_videos(suggestion, max_results=10)

                if not videos:
                    continue

                # Calculate velocity metrics
                recent_videos = [
                    v for v in videos
                    if v.get("days_since_upload") is not None and v["days_since_upload"] <= 14
                ]

                if recent_videos:
                    avg_views_recent = sum(v.get("view_count", 0) for v in recent_videos) / len(recent_videos)
                    avg_views_all = sum(v.get("view_count", 0) for v in videos) / len(videos)

                    # Rising = recent videos getting more views than average
                    if avg_views_recent > avg_views_all * 0.7 and len(recent_videos) >= 2:
                        rising.append({
                            "topic": suggestion,
                            "source_keyword": keyword,
                            "recent_video_count": len(recent_videos),
                            "avg_views_recent": int(avg_views_recent),
                            "avg_views_all": int(avg_views_all),
                            "velocity_score": round(avg_views_recent / max(avg_views_all, 1), 2),
                            "competition_videos": len(videos),
                            "detected_at": datetime.now().isoformat()
                        })

        rising.sort(key=lambda x: x["velocity_score"], reverse=True)
        self._save_trends(rising)
        return rising[:20]

    def find_shorts_opportunities(self, niche_keywords: list[str]) -> list[dict]:
        """Find topics where Shorts are performing well."""
        opportunities = []

        for keyword in niche_keywords[:5]:  # Limit to avoid too many requests
            shorts = self.scraper.search_shorts(keyword, max_results=15)

            if not shorts:
                continue

            # Analyze Shorts performance
            views = [s.get("view_count", 0) for s in shorts]
            if not views:
                continue

            avg_views = sum(views) / len(views)
            max_views = max(views)

            # Good opportunity if Shorts in this niche get decent views
            if avg_views > 10000:
                best_short = max(shorts, key=lambda x: x.get("view_count", 0))
                opportunities.append({
                    "keyword": keyword,
                    "avg_views": int(avg_views),
                    "max_views": max_views,
                    "total_shorts_found": len(shorts),
                    "best_title": best_short.get("title", ""),
                    "opportunity_score": min(100, int(avg_views / 1000))
                })

        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return opportunities

    def get_content_calendar_suggestions(self, niche_key: str, language: str = "en",
                                          days: int = 7) -> list[dict]:
        """Generate content suggestions for the next N days."""
        from config.niches import NICHES

        niche = NICHES.get(niche_key)
        if not niche:
            return []

        keywords = niche.get(f"keywords_{language}", niche.get("keywords_en", []))

        # Get rising topics
        rising = self.detect_rising_topics(keywords[:3], language)

        # Get Shorts opportunities
        shorts_opps = self.find_shorts_opportunities(keywords[:3])

        calendar = []
        for day in range(days):
            day_plan = {
                "day": day + 1,
                "long_video": None,
                "shorts": []
            }

            # Assign a long video topic
            if rising and day < len(rising):
                day_plan["long_video"] = {
                    "topic": rising[day]["topic"],
                    "reason": f"Rising topic (velocity: {rising[day]['velocity_score']}x)"
                }
            elif keywords:
                day_plan["long_video"] = {
                    "topic": keywords[day % len(keywords)],
                    "reason": "Core niche keyword"
                }

            # Assign Shorts topics (2-3 per day)
            for i in range(3):
                idx = (day * 3 + i) % max(len(shorts_opps), 1)
                if shorts_opps:
                    day_plan["shorts"].append({
                        "topic": shorts_opps[idx]["keyword"],
                        "hook_style": niche.get("shorts_hooks", [""])[i % len(niche.get("shorts_hooks", [""]))]
                    })

            calendar.append(day_plan)

        return calendar

    def _save_trends(self, trends: list[dict]):
        """Save detected trends for tracking."""
        self.trends_file.write_text(json.dumps(trends, indent=2))
