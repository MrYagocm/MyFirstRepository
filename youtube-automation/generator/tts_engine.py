"""
TTS Engine: Text-to-speech using ElevenLabs (premium) with edge-tts fallback.
ElevenLabs produces much more natural voices = better viewer retention.
"""

import asyncio
import hashlib
from pathlib import Path
from typing import Optional

from config.settings import (
    AUDIO_DIR, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_EN,
    ELEVENLABS_VOICE_ID_ES, ELEVENLABS_MODEL, ELEVENLABS_STABILITY,
    ELEVENLABS_SIMILARITY
)


class TTSEngine:
    """Handles text-to-speech conversion with premium and fallback options."""

    def __init__(self):
        self.use_elevenlabs = bool(ELEVENLABS_API_KEY)

    def generate_audio(self, text: str, language: str = "en",
                        output_filename: Optional[str] = None) -> Optional[Path]:
        """Generate audio from text. Uses ElevenLabs if available, else edge-tts."""
        if not text.strip():
            return None

        if not output_filename:
            text_hash = hashlib.md5(text[:100].encode()).hexdigest()[:10]
            output_filename = f"audio_{language}_{text_hash}.mp3"

        output_path = AUDIO_DIR / output_filename

        if output_path.exists():
            return output_path

        if self.use_elevenlabs:
            result = self._generate_elevenlabs(text, language, output_path)
            if result:
                return result
            print("[TTS] ElevenLabs failed, falling back to edge-tts")

        return self._generate_edge_tts(text, language, output_path)

    def _generate_elevenlabs(self, text: str, language: str, output_path: Path) -> Optional[Path]:
        """Generate audio using ElevenLabs API."""
        try:
            from elevenlabs import ElevenLabs

            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

            voice_id = ELEVENLABS_VOICE_ID_EN if language == "en" else ELEVENLABS_VOICE_ID_ES

            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=ELEVENLABS_MODEL,
                voice_settings={
                    "stability": ELEVENLABS_STABILITY,
                    "similarity_boost": ELEVENLABS_SIMILARITY
                }
            )

            # Write audio bytes to file
            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            print(f"[TTS] ElevenLabs audio saved: {output_path}")
            return output_path

        except Exception as e:
            print(f"[TTS] ElevenLabs error: {e}")
            return None

    def _generate_edge_tts(self, text: str, language: str, output_path: Path) -> Optional[Path]:
        """Generate audio using edge-tts (free, Microsoft voices)."""
        try:
            import edge_tts

            voice_map = {
                "en": "en-US-ChristopherNeural",
                "es": "es-ES-AlvaroNeural"
            }
            voice = voice_map.get(language, voice_map["en"])

            async def _generate():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(str(output_path))

            asyncio.run(_generate())
            print(f"[TTS] Edge-TTS audio saved: {output_path}")
            return output_path

        except Exception as e:
            print(f"[TTS] Edge-TTS error: {e}")
            return None

    def generate_audio_chunks(self, sections: list[dict], language: str = "en") -> list[Path]:
        """Generate separate audio files for each script section."""
        audio_files = []

        for i, section in enumerate(sections):
            text = section.get("content", "")
            if not text:
                continue

            filename = f"section_{i:03d}_{language}.mp3"
            audio_path = self.generate_audio(text, language, filename)
            if audio_path:
                audio_files.append(audio_path)

        return audio_files

    def estimate_duration(self, text: str) -> float:
        """Estimate audio duration in seconds from text length."""
        word_count = len(text.split())
        return word_count / 2.5  # ~150 words per minute = 2.5 words per second
