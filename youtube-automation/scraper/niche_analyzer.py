"""
Niche analyzer: finds the best content opportunities by analyzing
competition, demand, and RPM across niches and languages.
This is the BRAIN of the system - quality > quantity.
"""

import json
from datetime import datetime
from typing import Optional
from config.niches import NICHES
from config.settings import DATA_DIR, VIRAL_RATIO_THRESHOLD, MIN_CHANNEL_SIZE, MAX_CHANNEL_SIZE
from .youtube_scraper import YouTubeScraper


class NicheAnalyzer:
    """Analyzes niches to find the most profitable content opportunities."""

    def __init__(self):
        self.scraper = YouTubeScraper()
        self.analysis_file = DATA_DIR / "niche_analysis.json"

    def analyze_niche(self, niche_key: str, language: str = "en") -> dict:
        """Deep analysis of a specific niche."""
        niche = NICHES.get(niche_key)
        if not niche:
            return {"error": f"Niche '{niche_key}' not found"}

        keywords = niche.get(f"keywords_{language}", niche.get("keywords_en", []))
        print(f"[Analyzer] Analyzing niche: {niche['name']} ({language})")

        # Get trending videos in this niche
        videos = self.scraper.get_trending_in_niche(keywords, language=language,
                                                     max_per_keyword=10)

        if not videos:
            return {"niche": niche_key, "language": language, "error": "No videos found"}

        # Analyze competition
        competition = self._analyze_competition(videos)

        # Find content gaps
        content_gaps = self._find_content_gaps(videos, keywords)

        # Find viral patterns
        viral_patterns = self._find_viral_patterns(videos)

        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(
            niche, competition, content_gaps, viral_patterns, language
        )

        analysis = {
            "niche": niche_key,
            "niche_name": niche["name"],
            "language": language,
            "rpm_estimate": niche["rpm_estimate"].get(language, 3.0),
            "total_videos_analyzed": len(videos),
            "competition": competition,
            "content_gaps": content_gaps,
            "viral_patterns": viral_patterns,
            "opportunity_score": opportunity_score,
            "recommended_topics": self._get_recommended_topics(content_gaps, viral_patterns),
            "analyzed_at": datetime.now().isoformat()
        }

        self._save_analysis(analysis)
        return analysis

    def compare_languages(self, niche_key: str) -> dict:
        """Compare EN vs ES opportunity for a niche."""
        en_analysis = self.analyze_niche(niche_key, "en")
        es_analysis = self.analyze_niche(niche_key, "es")

        comparison = {
            "niche": niche_key,
            "english": {
                "opportunity_score": en_analysis.get("opportunity_score", 0),
                "rpm": en_analysis.get("rpm_estimate", 0),
                "competition_level": en_analysis.get("competition", {}).get("level", "unknown"),
                "content_gaps": len(en_analysis.get("content_gaps", []))
            },
            "spanish": {
                "opportunity_score": es_analysis.get("opportunity_score", 0),
                "rpm": es_analysis.get("rpm_estimate", 0),
                "competition_level": es_analysis.get("competition", {}).get("level", "unknown"),
                "content_gaps": len(es_analysis.get("content_gaps", []))
            },
            "recommendation": "en" if en_analysis.get("opportunity_score", 0) >= es_analysis.get("opportunity_score", 0) else "es"
        }

        return comparison

    def find_best_opportunity(self, language: str = "en") -> dict:
        """Analyze all niches and return the best opportunity right now."""
        results = []

        for niche_key in NICHES:
            analysis = self.analyze_niche(niche_key, language)
            if "error" not in analysis:
                results.append(analysis)

        if not results:
            return {"error": "No niches could be analyzed"}

        results.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)

        return {
            "best_niche": results[0],
            "rankings": [
                {
                    "niche": r["niche"],
                    "name": r["niche_name"],
                    "score": r["opportunity_score"],
                    "rpm": r["rpm_estimate"]
                }
                for r in results
            ]
        }

    def _analyze_competition(self, videos: list[dict]) -> dict:
        """Analyze competition level from video data."""
        if not videos:
            return {"level": "unknown", "avg_views": 0}

        view_counts = [v.get("view_count", 0) for v in videos]
        avg_views = sum(view_counts) / len(view_counts)

        # Count small channels (our competitors)
        small_channel_videos = [
            v for v in videos
            if MIN_CHANNEL_SIZE <= (v.get("view_count", 0) * 4) <= MAX_CHANNEL_SIZE
        ]

        # Videos from last 30 days
        recent_videos = [
            v for v in videos
            if v.get("days_since_upload") is not None and v["days_since_upload"] <= 30
        ]

        saturation = len(recent_videos) / max(len(videos), 1)

        if avg_views > 500000 and saturation > 0.5:
            level = "very_high"
        elif avg_views > 100000 and saturation > 0.3:
            level = "high"
        elif avg_views > 30000:
            level = "medium"
        else:
            level = "low"

        return {
            "level": level,
            "avg_views": int(avg_views),
            "median_views": int(sorted(view_counts)[len(view_counts)//2]) if view_counts else 0,
            "small_channel_presence": len(small_channel_videos) / max(len(videos), 1),
            "recent_saturation": saturation,
            "total_analyzed": len(videos)
        }

    def _find_content_gaps(self, videos: list[dict], keywords: list[str]) -> list[dict]:
        """Find underserved topics within the niche."""
        title_words = {}
        for video in videos:
            title = video.get("title", "").lower()
            for word in title.split():
                if len(word) > 3:
                    title_words[word] = title_words.get(word, 0) + 1

        # Keywords with low video presence = content gaps
        gaps = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            matching_videos = [
                v for v in videos
                if keyword_lower in v.get("title", "").lower()
            ]

            if len(matching_videos) < 3:
                avg_views = 0
                if matching_videos:
                    avg_views = sum(v.get("view_count", 0) for v in matching_videos) / len(matching_videos)

                gaps.append({
                    "keyword": keyword,
                    "existing_videos": len(matching_videos),
                    "avg_views_existing": int(avg_views),
                    "gap_score": max(0, 10 - len(matching_videos) * 2)
                })

        gaps.sort(key=lambda x: x["gap_score"], reverse=True)
        return gaps[:10]

    def _find_viral_patterns(self, videos: list[dict]) -> dict:
        """Identify patterns in viral/high-performing videos."""
        if not videos:
            return {"patterns": [], "avg_title_length": 0}

        # Find outlier videos (viral)
        avg_views = sum(v.get("view_count", 0) for v in videos) / len(videos)
        viral_videos = [v for v in videos if v.get("view_count", 0) > avg_views * 3]

        # Analyze title patterns
        title_patterns = {
            "numbers": 0, "questions": 0, "how_to": 0,
            "top_list": 0, "emotional": 0, "caps_words": 0
        }

        emotional_words = {"amazing", "insane", "shocking", "incredible", "terrifying",
                          "unbelievable", "mind", "blown", "crazy", "secret", "never"}

        for video in viral_videos or videos[:10]:
            title = video.get("title", "")
            if any(c.isdigit() for c in title):
                title_patterns["numbers"] += 1
            if "?" in title:
                title_patterns["questions"] += 1
            if title.lower().startswith(("how to", "como", "cómo")):
                title_patterns["how_to"] += 1
            if any(title.lower().startswith(p) for p in ("top ", "best ", "worst ", "los ", "las ")):
                title_patterns["top_list"] += 1
            if any(w in title.lower() for w in emotional_words):
                title_patterns["emotional"] += 1
            caps = sum(1 for w in title.split() if w.isupper() and len(w) > 1)
            if caps >= 2:
                title_patterns["caps_words"] += 1

        total = len(viral_videos) or len(videos[:10])
        dominant_patterns = sorted(
            title_patterns.items(), key=lambda x: x[1], reverse=True
        )[:3]

        title_lengths = [len(v.get("title", "")) for v in videos]
        avg_duration = sum(v.get("duration", 0) for v in videos) / len(videos)

        return {
            "viral_count": len(viral_videos),
            "patterns": [{"type": p[0], "frequency": p[1] / total} for p in dominant_patterns],
            "avg_title_length": int(sum(title_lengths) / len(title_lengths)),
            "avg_duration": int(avg_duration),
            "best_performing_titles": [
                v.get("title", "") for v in sorted(
                    videos, key=lambda x: x.get("view_count", 0), reverse=True
                )[:5]
            ]
        }

    def _calculate_opportunity_score(self, niche: dict, competition: dict,
                                      content_gaps: list, viral_patterns: dict,
                                      language: str) -> float:
        """Calculate 0-100 opportunity score."""
        score = 50.0  # Base

        # RPM factor (higher RPM = better)
        rpm = niche["rpm_estimate"].get(language, 3.0)
        score += min(20, rpm * 1.5)

        # Competition factor (lower = better)
        comp_map = {"low": 15, "medium": 5, "high": -5, "very_high": -15}
        score += comp_map.get(competition.get("level", "medium"), 0)

        # Content gaps (more gaps = more opportunity)
        score += min(15, len(content_gaps) * 2)

        # Small channel presence (if small channels succeed, we can too)
        small_presence = competition.get("small_channel_presence", 0)
        score += small_presence * 10

        # Growth potential
        growth_map = {"very_high": 10, "high": 5, "medium": 0, "low": -5}
        score += growth_map.get(niche.get("growth_potential", "medium"), 0)

        return round(max(0, min(100, score)), 1)

    def _get_recommended_topics(self, content_gaps: list, viral_patterns: dict) -> list[str]:
        """Generate specific topic recommendations."""
        topics = []

        # From content gaps
        for gap in content_gaps[:5]:
            topics.append(f"Content gap: {gap['keyword']} (only {gap['existing_videos']} videos)")

        # From viral patterns
        best_titles = viral_patterns.get("best_performing_titles", [])
        for title in best_titles[:3]:
            topics.append(f"Viral format: Similar to '{title}'")

        return topics

    def _save_analysis(self, analysis: dict):
        """Save analysis to file for historical tracking."""
        history = []
        if self.analysis_file.exists():
            try:
                history = json.loads(self.analysis_file.read_text())
            except json.JSONDecodeError:
                history = []

        history.append(analysis)
        # Keep last 100 analyses
        history = history[-100:]
        self.analysis_file.write_text(json.dumps(history, indent=2))
