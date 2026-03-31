"""
TTS Engine v2: Multi-provider with cost optimization.
Priority: Google Cloud TTS (FREE 1M chars/mo) > Edge TTS (free) > Voxtral > ElevenLabs
"""

import asyncio
import hashlib
from pathlib import Path
from typing import Optional

from config.settings import (
    AUDIO_DIR, TTS_PROVIDER,
    GOOGLE_CLOUD_PROJECT, GOOGLE_TTS_VOICE_EN, GOOGLE_TTS_VOICE_ES,
    EDGE_TTS_VOICE_EN, EDGE_TTS_VOICE_ES,
    ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_EN, ELEVENLABS_VOICE_ID_ES,
    ELEVENLABS_MODEL
)


class TTSEngine:
    """Multi-provider TTS with automatic fallback chain."""

    PROVIDERS = ["google_cloud", "edge", "voxtral", "elevenlabs"]

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or TTS_PROVIDER
        self.chars_used_google = 0  # Track free tier usage

    def generate_audio(self, text: str, language: str = "en",
                        output_filename: Optional[str] = None) -> Optional[Path]:
        """Generate audio with automatic provider fallback."""
        if not text.strip():
            return None

        if not output_filename:
            text_hash = hashlib.md5(text[:100].encode()).hexdigest()[:10]
            output_filename = f"audio_{language}_{text_hash}.mp3"

        output_path = AUDIO_DIR / output_filename
        if output_path.exists():
            return output_path

        # Try providers in priority order
        providers_to_try = [self.provider] + [p for p in self.PROVIDERS if p != self.provider]

        for provider in providers_to_try:
            result = self._generate_with_provider(provider, text, language, output_path)
            if result:
                return result
            print(f"[TTS] {provider} failed, trying next...")

        print("[TTS] All providers failed!")
        return None

    def _generate_with_provider(self, provider: str, text: str,
                                  language: str, output_path: Path) -> Optional[Path]:
        """Generate audio with a specific provider."""
        try:
            if provider == "google_cloud":
                return self._generate_google_cloud(text, language, output_path)
            elif provider == "edge":
                return self._generate_edge_tts(text, language, output_path)
            elif provider == "voxtral":
                return self._generate_voxtral(text, language, output_path)
            elif provider == "elevenlabs":
                return self._generate_elevenlabs(text, language, output_path)
        except Exception as e:
            print(f"[TTS] {provider} error: {e}")
        return None

    def _generate_google_cloud(self, text: str, language: str, output_path: Path) -> Optional[Path]:
        """Google Cloud TTS - FREE 1M characters/month."""
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()

        voice_name = GOOGLE_TTS_VOICE_EN if language == "en" else GOOGLE_TTS_VOICE_ES
        lang_code = "en-US" if language == "en" else "es-US"

        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )

        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        self.chars_used_google += len(text)
        print(f"[TTS] Google Cloud saved: {output_path} ({self.chars_used_google:,} chars used this session)")
        return output_path

    def _generate_edge_tts(self, text: str, language: str, output_path: Path) -> Optional[Path]:
        """Edge TTS - completely free, good quality."""
        import edge_tts

        voice = EDGE_TTS_VOICE_EN if language == "en" else EDGE_TTS_VOICE_ES

        async def _generate():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

        asyncio.run(_generate())
        print(f"[TTS] Edge-TTS saved: {output_path}")
        return output_path

    def _generate_voxtral(self, text: str, language: str, output_path: Path) -> Optional[Path]:
        """Voxtral TTS (Mistral) - $0.016/1K chars, 47% cheaper than ElevenLabs."""
        import requests

        api_key = os.environ.get("MISTRAL_API_KEY", "")
        if not api_key:
            return None

        response = requests.post(
            "https://api.mistral.ai/v1/audio/speech",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "voxtral-mini", "input": text},
            timeout=120
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"[TTS] Voxtral saved: {output_path}")
            return output_path
        return None

    def _generate_elevenlabs(self, text: str, language: str, output_path: Path) -> Optional[Path]:
        """ElevenLabs - premium quality, $0.13/video."""
        if not ELEVENLABS_API_KEY:
            return None

        from elevenlabs import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        voice_id = ELEVENLABS_VOICE_ID_EN if language == "en" else ELEVENLABS_VOICE_ID_ES

        audio = client.text_to_speech.convert(
            voice_id=voice_id, text=text, model_id=ELEVENLABS_MODEL,
            voice_settings={"stability": 0.5, "similarity_boost": 0.75}
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        print(f"[TTS] ElevenLabs saved: {output_path}")
        return output_path

    def estimate_duration(self, text: str) -> float:
        """Estimate audio duration in seconds."""
        return len(text.split()) / 2.5

    def get_free_tier_remaining(self) -> int:
        """Check remaining Google Cloud free tier chars."""
        return max(0, 1_000_000 - self.chars_used_google)
