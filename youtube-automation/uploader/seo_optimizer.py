"""
SEO Optimizer: maximizes discoverability through titles,
descriptions, tags, and metadata optimization.
"""

import json
from typing import Optional

import anthropic

from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL


class SEOOptimizer:
    """Optimizes video metadata for maximum YouTube discoverability."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def optimize_metadata(self, title: str, description: str, tags: list[str],
                           niche: str, language: str = "en") -> dict:
        """Optimize all video metadata for SEO."""
        prompt = f"""You are a YouTube SEO expert. Optimize this video's metadata for maximum discoverability and CTR.

CURRENT:
- Title: {title}
- Description: {description[:500]}
- Tags: {', '.join(tags[:10])}
- Niche: {niche}
- Language: {language}

OPTIMIZE for:
1. TITLE: Max 60 chars. Include primary keyword near the start. Use power words (shocking, secret, revealed, etc.). Numbers perform well.
2. DESCRIPTION: First 150 chars are critical (shown in search). Include main keyword in first sentence. Add 3-5 relevant hashtags. Include timestamps if applicable.
3. TAGS: Start with exact match keywords, then broad. Mix short-tail and long-tail. Include common misspellings. Max 30 tags.
4. HASHTAGS: 3-5 most relevant hashtags for the description.

Return JSON:
{{
    "title": "optimized title",
    "description": "full optimized description",
    "tags": ["tag1", "tag2", ...],
    "hashtags": ["#hash1", "#hash2", ...]
}}"""

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])

        except Exception as e:
            print(f"[SEO] Optimization error: {e}")

        return {"title": title, "description": description, "tags": tags, "hashtags": []}

    def generate_description(self, title: str, script_summary: str,
                              niche: str, language: str = "en") -> str:
        """Generate a full YouTube description optimized for SEO."""
        lang_text = "English" if language == "en" else "Spanish"

        prompt = f"""Write a YouTube video description in {lang_text}.

TITLE: {title}
CONTENT SUMMARY: {script_summary[:300]}
NICHE: {niche}

REQUIREMENTS:
1. First 150 characters: Hook + main keyword (this shows in search results)
2. Brief summary of what viewers will learn (2-3 lines)
3. Timestamps (estimate logical breaks)
4. Call to action (subscribe, like, comment)
5. 3-5 relevant hashtags at the end
6. Keep under 2000 characters total

Write the description directly, no JSON wrapper."""

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()

        except Exception as e:
            print(f"[SEO] Description error: {e}")
            return f"{title}\n\nDon't forget to subscribe!"

    def suggest_upload_time(self, language: str = "en", niche: str = "") -> dict:
        """Suggest optimal upload times based on niche and language."""
        # Based on general YouTube analytics data
        schedules = {
            "en": {
                "best_days": ["Tuesday", "Thursday", "Saturday"],
                "best_hours": ["14:00 EST", "17:00 EST"],
                "worst_day": "Monday",
                "reason": "US audience peaks mid-afternoon to evening"
            },
            "es": {
                "best_days": ["Wednesday", "Friday", "Sunday"],
                "best_hours": ["13:00 CET", "20:00 CET"],
                "worst_day": "Monday",
                "reason": "Spanish-speaking audience peaks afternoon and evening"
            }
        }

        return schedules.get(language, schedules["en"])

    def analyze_competition_titles(self, titles: list[str]) -> dict:
        """Analyze competitor titles to find patterns."""
        patterns = {
            "avg_length": sum(len(t) for t in titles) / max(len(titles), 1),
            "uses_numbers": sum(1 for t in titles if any(c.isdigit() for c in t)),
            "uses_caps": sum(1 for t in titles if sum(1 for w in t.split() if w.isupper()) >= 2),
            "uses_emoji": sum(1 for t in titles if any(ord(c) > 127 for c in t)),
            "total_analyzed": len(titles)
        }

        return patterns
