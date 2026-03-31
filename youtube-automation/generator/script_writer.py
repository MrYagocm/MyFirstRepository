"""
Script writer: generates video scripts using Claude API.
Optimized for engagement, retention, and SEO.
"""

import json
from typing import Optional

import anthropic

from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS


class ScriptWriter:
    """Generates video scripts optimized for YouTube engagement."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def write_long_script(self, topic: str, niche: str, language: str = "en",
                           target_duration: int = 480, style: str = "educational_listicle",
                           viral_patterns: Optional[dict] = None) -> dict:
        """Generate a full video script for a long-form video."""
        lang_instruction = "Write in English." if language == "en" else "Write in Spanish (Castilian)."

        patterns_context = ""
        if viral_patterns:
            best_titles = viral_patterns.get("best_performing_titles", [])
            if best_titles:
                patterns_context = f"\nViral titles in this niche for reference (adapt, don't copy): {', '.join(best_titles[:3])}"

        words_needed = int(target_duration * 2.5)  # ~150 words per minute

        prompt = f"""You are a top YouTube scriptwriter. Create a complete video script.

TOPIC: {topic}
NICHE: {niche}
STYLE: {style}
TARGET LENGTH: ~{words_needed} words ({target_duration // 60} minutes)
{lang_instruction}
{patterns_context}

REQUIREMENTS:
1. HOOK (first 10 seconds): Start with a shocking fact, bold claim, or question that makes viewers NEED to keep watching. No introductions.
2. RETENTION: Every 60-90 seconds, add a "pattern interrupt" - a surprising fact, rhetorical question, or teaser about what's coming next.
3. STRUCTURE: Use clear sections. Each section builds curiosity for the next one.
4. CTA: Include a natural subscribe CTA in the middle (not beginning or end) when engagement is highest.
5. ENDING: End with a cliffhanger or open question that makes viewers want to comment.

OUTPUT FORMAT (JSON):
{{
    "title": "SEO-optimized title (50-60 chars, include power words)",
    "description": "YouTube description (first 150 chars are crucial - include main keyword)",
    "tags": ["tag1", "tag2", ...],
    "hook": "First 10 seconds of the script",
    "sections": [
        {{
            "title": "Section name",
            "content": "Full narration text",
            "visual_notes": "What to show on screen",
            "duration_estimate": 60
        }}
    ],
    "outro": "Closing narration",
    "total_word_count": 0
}}"""

        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_script_response(response.content[0].text)

    def write_short_script(self, topic: str, niche: str, language: str = "en",
                            hook_template: Optional[str] = None) -> dict:
        """Generate a YouTube Shorts script (< 60 seconds)."""
        lang_instruction = "Write in English." if language == "en" else "Write in Spanish (Castilian)."

        hook_context = ""
        if hook_template:
            hook_context = f"\nUse this hook style as inspiration: '{hook_template}'"

        prompt = f"""You are a viral Shorts scriptwriter. Create a YouTube Short script.

TOPIC: {topic}
NICHE: {niche}
MAX DURATION: 58 seconds (~145 words)
{lang_instruction}
{hook_context}

REQUIREMENTS:
1. HOOK (0-3 seconds): The most important part. Must stop the scroll IMMEDIATELY. Use shock, curiosity, or a bold claim.
2. BODY (3-45 seconds): Deliver value fast. No filler. Every sentence must earn the next second of watch time.
3. PAYOFF (45-58 seconds): Deliver on the hook's promise + leave them wanting more (follow for part 2).
4. NO INTRODUCTIONS. No "hey guys". Start with the hook immediately.
5. Keep sentences SHORT. One idea per sentence. Conversational tone.

OUTPUT FORMAT (JSON):
{{
    "title": "Short title with #Shorts hashtag",
    "description": "Brief description with hashtags",
    "tags": ["tag1", "tag2", ...],
    "hook": "First 3 seconds (CRITICAL - this determines if they watch)",
    "body": "Main content (one continuous narration)",
    "payoff": "Closing line (leave them wanting more)",
    "total_word_count": 0,
    "visual_notes": "What to show on screen throughout"
}}"""

        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_script_response(response.content[0].text)

    def rewrite_for_engagement(self, script: dict, performance_data: Optional[dict] = None) -> dict:
        """Rewrite a script based on performance data to improve engagement."""
        context = ""
        if performance_data:
            context = f"""
Previous video performance:
- Average view duration: {performance_data.get('avg_view_duration', 'unknown')}
- CTR: {performance_data.get('ctr', 'unknown')}%
- Drop-off points: {performance_data.get('drop_off_points', 'unknown')}
Improve the weak points based on this data."""

        prompt = f"""Rewrite this YouTube script to maximize engagement.
{context}

ORIGINAL SCRIPT:
{json.dumps(script, indent=2)}

Focus on:
1. Stronger hook (first 10 seconds determine everything)
2. Better retention (add more pattern interrupts)
3. More compelling title (higher CTR)
4. Tighter writing (remove any filler)

Return in the same JSON format."""

        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_script_response(response.content[0].text)

    def _parse_script_response(self, text: str) -> dict:
        """Parse Claude's response into a clean script dict."""
        # Try to extract JSON from the response
        try:
            # Find JSON block
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

        # Fallback: return raw text
        return {
            "title": "Generated Video",
            "description": "",
            "tags": [],
            "raw_script": text,
            "parse_error": True
        }

    def get_full_narration(self, script: dict) -> str:
        """Extract full narration text from a script for TTS."""
        parts = []

        if script.get("hook"):
            parts.append(script["hook"])

        if script.get("sections"):
            for section in script["sections"]:
                parts.append(section.get("content", ""))
        elif script.get("body"):
            parts.append(script["body"])

        if script.get("payoff"):
            parts.append(script["payoff"])
        elif script.get("outro"):
            parts.append(script["outro"])

        return " ".join(parts)
