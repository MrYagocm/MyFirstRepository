"""
Script writer v2: Multi-LLM with Gemini free tier as default.
Includes anti-fingerprinting variation to avoid YouTube detection.
"""

import json
import random
from typing import Optional

from config.settings import (
    LLM_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL,
    ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS
)


# Variation templates to avoid pattern detection
NARRATIVE_STYLES = [
    "conversational and casual, like telling a friend",
    "dramatic and suspenseful, building tension",
    "investigative journalism style, presenting facts",
    "storytelling with vivid imagery and metaphors",
    "direct and punchy, no fluff, rapid-fire delivery"
]

STRUCTURE_VARIATIONS = [
    "Start with the climax, then rewind to explain how we got there",
    "Build chronologically with rising tension",
    "Present the mystery first, then reveal clues one by one",
    "Use a contrast structure: what people think vs reality",
    "Start with a bold claim, then prove it step by step"
]


class ScriptWriter:
    """Multi-LLM script generator with anti-fingerprinting."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or LLM_PROVIDER

    def write_long_script(self, topic: str, niche: str, language: str = "en",
                           target_duration: int = 480, style: str = "educational_listicle",
                           viral_patterns: Optional[dict] = None) -> dict:
        """Generate a video script with built-in variation."""
        lang_instruction = "Write in English." if language == "en" else "Write in Spanish (Castilian)."

        # Anti-fingerprinting: randomize style and structure each time
        narrative_style = random.choice(NARRATIVE_STYLES)
        structure = random.choice(STRUCTURE_VARIATIONS)

        patterns_context = ""
        if viral_patterns:
            best_titles = viral_patterns.get("best_performing_titles", [])
            if best_titles:
                patterns_context = f"\nViral titles for reference (adapt, don't copy): {', '.join(best_titles[:3])}"

        words_needed = int(target_duration * 2.5)

        prompt = f"""You are a top YouTube scriptwriter. Create a complete video script.

TOPIC: {topic}
NICHE: {niche}
NARRATIVE STYLE: {narrative_style}
STRUCTURE: {structure}
TARGET LENGTH: ~{words_needed} words ({target_duration // 60} minutes)
{lang_instruction}
{patterns_context}

REQUIREMENTS:
1. HOOK (first 10 seconds): Start with something that makes viewers NEED to keep watching. No introductions, no "hey guys".
2. RETENTION: Every 60-90 seconds, add a pattern interrupt (surprising fact, question, teaser).
3. STRUCTURE: Use the structure style specified above. Make it feel UNIQUE, not templated.
4. CTA: Include a natural subscribe CTA in the MIDDLE (not beginning or end).
5. ENDING: End with something that makes viewers want to comment.
6. IMPORTANT: This must feel like a HUMAN wrote it. Vary sentence length. Use conversational language. Add personality.

OUTPUT FORMAT (JSON):
{{
    "title": "SEO-optimized title (50-60 chars, include power words)",
    "description": "First 150 chars are crucial for search. Include main keyword.",
    "tags": ["tag1", "tag2", ...],
    "hook": "First 10 seconds of the script",
    "sections": [
        {{
            "title": "Section name",
            "content": "Full narration text for this section",
            "visual_notes": "What to show on screen",
            "duration_estimate": 60
        }}
    ],
    "outro": "Closing narration",
    "total_word_count": 0
}}"""

        return self._call_llm(prompt)

    def write_short_script(self, topic: str, niche: str, language: str = "en",
                            hook_template: Optional[str] = None) -> dict:
        """Generate a YouTube Shorts script with variation."""
        lang_instruction = "Write in English." if language == "en" else "Write in Spanish (Castilian)."

        # Randomize tone for each Short
        tone = random.choice([
            "shocked and breathless", "calm and authoritative",
            "excited and energetic", "mysterious and intriguing",
            "matter-of-fact and confident"
        ])

        hook_context = f"\nHook inspiration: '{hook_template}'" if hook_template else ""

        prompt = f"""Create a YouTube Short script. MAX 58 seconds (~145 words).

TOPIC: {topic}
NICHE: {niche}
TONE: {tone}
{lang_instruction}
{hook_context}

REQUIREMENTS:
1. HOOK (0-3 sec): Stop the scroll. Shock, curiosity, or bold claim.
2. BODY (3-45 sec): Value fast. No filler. Every sentence earns the next second.
3. PAYOFF (45-58 sec): Deliver + leave wanting more.
4. NO introductions. Start with hook immediately.
5. Sound HUMAN. Vary rhythm. Short punchy sentences mixed with longer ones.

OUTPUT JSON:
{{
    "title": "Title with #Shorts",
    "description": "Brief + hashtags",
    "tags": ["tag1", ...],
    "hook": "First 3 seconds",
    "body": "Main content",
    "payoff": "Closing line",
    "total_word_count": 0,
    "visual_notes": "What to show"
}}"""

        return self._call_llm(prompt, max_tokens=2048)

    def _call_llm(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Call the configured LLM provider."""
        text = ""

        if self.provider == "gemini":
            text = self._call_gemini(prompt, max_tokens)
        elif self.provider == "claude":
            text = self._call_claude(prompt, max_tokens)
        else:
            text = self._call_gemini(prompt, max_tokens)  # Default fallback

        return self._parse_response(text)

    def _call_gemini(self, prompt: str, max_tokens: int) -> str:
        """Call Gemini API (FREE: 60 requests/minute)."""
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.9  # Higher temp = more variation
            )
        )
        return response.text

    def _call_claude(self, prompt: str, max_tokens: int) -> str:
        """Call Claude API (~$0.02/script)."""
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _parse_response(self, text: str) -> dict:
        """Parse LLM response into script dict."""
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        return {"title": "Generated Video", "raw_script": text, "parse_error": True}

    def get_full_narration(self, script: dict) -> str:
        """Extract full narration text for TTS."""
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
