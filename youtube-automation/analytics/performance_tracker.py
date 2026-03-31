"""
Performance tracker: monitors video performance and feeds data
back into the system to improve future content.
The feedback loop is what makes this a money machine, not just a content generator.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import ANALYTICS_DB, DATA_DIR


class PerformanceTracker:
    """Tracks video performance and provides actionable insights."""

    def __init__(self):
        self.db_path = ANALYTICS_DB
        self.data = self._load_data()

    def _load_data(self) -> dict:
        if self.db_path.exists():
            try:
                return json.loads(self.db_path.read_text())
            except json.JSONDecodeError:
                pass
        return {"videos": [], "summary": {}, "insights": []}

    def _save_data(self):
        self.db_path.write_text(json.dumps(self.data, indent=2))

    def record_upload(self, video_id: str, title: str, niche: str,
                       language: str, is_short: bool, metadata: Optional[dict] = None) -> None:
        """Record a new video upload."""
        entry = {
            "video_id": video_id,
            "title": title,
            "niche": niche,
            "language": language,
            "is_short": is_short,
            "uploaded_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "performance": [],
            "status": "active"
        }

        self.data["videos"].append(entry)
        self._save_data()
        print(f"[Analytics] Recorded upload: {title}")

    def update_performance(self, video_id: str, stats: dict) -> None:
        """Update performance metrics for a video."""
        for video in self.data["videos"]:
            if video["video_id"] == video_id:
                video["performance"].append({
                    "timestamp": datetime.now().isoformat(),
                    "views": stats.get("views", 0),
                    "likes": stats.get("likes", 0),
                    "comments": stats.get("comments", 0),
                    "watch_time_hours": stats.get("watch_time_hours", 0),
                    "ctr": stats.get("ctr", 0),
                    "avg_view_duration": stats.get("avg_view_duration", 0)
                })
                self._save_data()
                return

    def get_best_performing(self, metric: str = "views", limit: int = 10) -> list[dict]:
        """Get best performing videos by a specific metric."""
        scored = []
        for video in self.data["videos"]:
            if video["performance"]:
                latest = video["performance"][-1]
                scored.append({
                    "video_id": video["video_id"],
                    "title": video["title"],
                    "niche": video["niche"],
                    "is_short": video["is_short"],
                    "value": latest.get(metric, 0)
                })

        scored.sort(key=lambda x: x["value"], reverse=True)
        return scored[:limit]

    def get_niche_performance(self) -> dict:
        """Aggregate performance by niche."""
        niche_stats = {}

        for video in self.data["videos"]:
            niche = video["niche"]
            if niche not in niche_stats:
                niche_stats[niche] = {
                    "total_videos": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "avg_views": 0,
                    "best_video": None,
                    "best_views": 0
                }

            niche_stats[niche]["total_videos"] += 1

            if video["performance"]:
                latest = video["performance"][-1]
                views = latest.get("views", 0)
                niche_stats[niche]["total_views"] += views
                niche_stats[niche]["total_likes"] += latest.get("likes", 0)

                if views > niche_stats[niche]["best_views"]:
                    niche_stats[niche]["best_views"] = views
                    niche_stats[niche]["best_video"] = video["title"]

        # Calculate averages
        for niche in niche_stats:
            total = niche_stats[niche]["total_videos"]
            if total > 0:
                niche_stats[niche]["avg_views"] = niche_stats[niche]["total_views"] // total

        return niche_stats

    def generate_report(self) -> dict:
        """Generate a comprehensive performance report."""
        total_videos = len(self.data["videos"])
        shorts = [v for v in self.data["videos"] if v.get("is_short")]
        longs = [v for v in self.data["videos"] if not v.get("is_short")]

        total_views = 0
        total_likes = 0
        for video in self.data["videos"]:
            if video["performance"]:
                latest = video["performance"][-1]
                total_views += latest.get("views", 0)
                total_likes += latest.get("likes", 0)

        niche_perf = self.get_niche_performance()
        best_niche = max(niche_perf.items(), key=lambda x: x[1]["avg_views"])[0] if niche_perf else "N/A"

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_videos": total_videos,
            "total_shorts": len(shorts),
            "total_long_videos": len(longs),
            "total_views": total_views,
            "total_likes": total_likes,
            "avg_views_per_video": total_views // max(total_videos, 1),
            "best_niche": best_niche,
            "niche_breakdown": niche_perf,
            "top_videos": self.get_best_performing("views", 5),
            "recommendations": self._generate_recommendations(niche_perf)
        }

        return report

    def _generate_recommendations(self, niche_perf: dict) -> list[str]:
        """Generate actionable recommendations based on data."""
        recs = []

        if not niche_perf:
            recs.append("Upload more videos to start getting performance data")
            return recs

        # Find best and worst niches
        sorted_niches = sorted(niche_perf.items(), key=lambda x: x[1]["avg_views"], reverse=True)

        if len(sorted_niches) >= 2:
            best = sorted_niches[0]
            worst = sorted_niches[-1]
            recs.append(f"Focus more on '{best[0]}' (avg {best[1]['avg_views']} views)")
            if worst[1]["avg_views"] < best[1]["avg_views"] * 0.3:
                recs.append(f"Consider dropping '{worst[0]}' (underperforming)")

        # Check Shorts vs Long performance
        shorts_views = []
        long_views = []
        for video in self.data["videos"]:
            if video["performance"]:
                views = video["performance"][-1].get("views", 0)
                if video.get("is_short"):
                    shorts_views.append(views)
                else:
                    long_views.append(views)

        if shorts_views and long_views:
            avg_shorts = sum(shorts_views) / len(shorts_views)
            avg_long = sum(long_views) / len(long_views)
            if avg_shorts > avg_long * 2:
                recs.append("Shorts are outperforming long videos - increase Shorts production")
            elif avg_long > avg_shorts * 5:
                recs.append("Long videos have better ROI - focus on quality long-form content")

        return recs

    def get_insights_for_niche(self, niche: str) -> dict:
        """Get specific insights for content creation in a niche."""
        niche_videos = [v for v in self.data["videos"] if v["niche"] == niche]

        if not niche_videos:
            return {"niche": niche, "message": "No data yet for this niche"}

        # Find patterns in successful videos
        successful = []
        for v in niche_videos:
            if v["performance"]:
                views = v["performance"][-1].get("views", 0)
                successful.append((v, views))

        successful.sort(key=lambda x: x[1], reverse=True)

        return {
            "niche": niche,
            "total_videos": len(niche_videos),
            "best_title": successful[0][0]["title"] if successful else "N/A",
            "best_views": successful[0][1] if successful else 0,
            "avg_views": sum(s[1] for s in successful) // max(len(successful), 1)
        }
