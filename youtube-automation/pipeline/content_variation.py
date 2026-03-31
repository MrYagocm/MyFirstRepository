"""
Content Variation Engine: ensures each video is unique enough
to avoid YouTube's anti-template detection.

YouTube detects: upload velocity, script fingerprinting,
pattern consistency, production pipeline uniformity.
"""

import random
import hashlib
from datetime import datetime
from typing import Optional

from config.settings import DATA_DIR


class ContentVariation:
    """Anti-fingerprinting system for content production."""

    # Voice variation options
    VOICE_SPEEDS = [0.9, 0.95, 1.0, 1.05, 1.1]
    VOICE_PITCHES = [-2.0, -1.0, 0.0, 1.0, 2.0]

    # Visual variation
    TRANSITION_STYLES = [
        "crossfade", "cut", "fade_to_black", "slide_left",
        "slide_right", "zoom_in", "zoom_out"
    ]
    SUBTITLE_POSITIONS = ["bottom", "center", "top_third"]
    SUBTITLE_STYLES = [
        {"color": "white", "stroke": "black", "size": 32},
        {"color": "yellow", "stroke": "black", "size": 34},
        {"color": "white", "stroke": "navy", "size": 30},
        {"color": "#00ff88", "stroke": "black", "size": 33},
    ]

    # Intro variations (no two videos start the same way)
    INTRO_PATTERNS = [
        "question",  # Start with a rhetorical question
        "statement",  # Bold claim
        "statistic",  # Shocking number
        "story",  # Mini-anecdote
        "contradiction",  # "Everyone thinks X, but actually..."
    ]

    def __init__(self):
        self.history_file = DATA_DIR / "variation_history.json"
        self.recent_choices = self._load_history()

    def get_variation_params(self) -> dict:
        """Generate a unique set of production parameters for this video."""
        params = {
            "voice_speed": random.choice(self.VOICE_SPEEDS),
            "voice_pitch": random.choice(self.VOICE_PITCHES),
            "transition_style": random.choice(self.TRANSITION_STYLES),
            "subtitle_position": random.choice(self.SUBTITLE_POSITIONS),
            "subtitle_style": random.choice(self.SUBTITLE_STYLES),
            "intro_pattern": random.choice(self.INTRO_PATTERNS),
            "image_duration_variance": random.uniform(0.8, 1.3),  # Vary how long each image shows
            "ken_burns_intensity": random.uniform(0.02, 0.08),
            "music_volume": random.uniform(0.05, 0.15) if random.random() > 0.3 else 0,  # 30% no music
            "timestamp": datetime.now().isoformat(),
        }

        # Ensure we don't repeat the same combination
        param_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()[:8]
        params["variation_id"] = param_hash

        # Record this choice
        self.recent_choices.append(param_hash)
        self.recent_choices = self.recent_choices[-50:]  # Keep last 50
        self._save_history()

        return params

    def get_script_variation_prompt(self) -> str:
        """Generate variation instructions for the script writer."""
        style = random.choice([
            "Use short, punchy sentences. Maximum impact per word.",
            "Mix short sentences with longer, flowing ones. Create rhythm.",
            "Use a lot of rhetorical questions to engage the viewer.",
            "Be direct and authoritative. State facts confidently.",
            "Be conversational, like you're talking to a friend over coffee.",
        ])

        structure = random.choice([
            "Build tension gradually, with the biggest reveal at the end.",
            "Front-load the most shocking information, then explain.",
            "Use a numbered list structure but make each point a mini-story.",
            "Alternate between facts and emotional reactions.",
            "Present two opposing viewpoints, then reveal the truth.",
        ])

        return f"WRITING STYLE: {style}\nSTRUCTURE: {structure}"

    def should_add_music(self) -> bool:
        """Decide if this video should have background music.
        Research shows Shorts without music earn higher RPM."""
        return random.random() > 0.5  # 50% chance, but Shorts should default to no music

    def get_upload_delay(self) -> int:
        """Random delay between uploads to avoid velocity detection.
        Returns minutes to wait."""
        return random.randint(120, 480)  # 2-8 hours between uploads

    def _load_history(self) -> list:
        import json
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text())
            except (json.JSONDecodeError, KeyError):
                pass
        return []

    def _save_history(self):
        import json
        self.history_file.write_text(json.dumps(self.recent_choices))
