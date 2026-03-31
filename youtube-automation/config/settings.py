"""
Configuration settings for YouTube Automation System.
Premium tier: ElevenLabs + Replicate/Flux for maximum quality.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === Base Paths ===
BASE_DIR = Path(__file__).parent.parent
STORAGE_DIR = BASE_DIR / "storage"
VIDEOS_DIR = STORAGE_DIR / "videos"
THUMBNAILS_DIR = STORAGE_DIR / "thumbnails"
AUDIO_DIR = STORAGE_DIR / "audio"
SCRIPTS_DIR = STORAGE_DIR / "scripts"
DATA_DIR = STORAGE_DIR / "data"
SUBTITLES_DIR = STORAGE_DIR / "subtitles"

# Create directories
for d in [VIDEOS_DIR, THUMBNAILS_DIR, AUDIO_DIR, SCRIPTS_DIR, DATA_DIR, SUBTITLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === API Keys ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# === Claude API ===
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 4096

# === ElevenLabs TTS (Premium) ===
ELEVENLABS_VOICE_ID_EN = os.getenv("ELEVENLABS_VOICE_ID_EN", "21m00Tcm4TlvDq8ikWAM")  # Rachel
ELEVENLABS_VOICE_ID_ES = os.getenv("ELEVENLABS_VOICE_ID_ES", "ThT5KcBeYPX3keUQqHPh")  # Spanish voice
ELEVENLABS_MODEL = "eleven_multilingual_v2"
ELEVENLABS_STABILITY = 0.5
ELEVENLABS_SIMILARITY = 0.75

# === Replicate / Flux (Image Generation) ===
REPLICATE_MODEL = "black-forest-labs/flux-schnell"
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720

# === Video Settings ===
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_BITRATE = "5000k"

# Shorts settings
SHORTS_WIDTH = 1080
SHORTS_HEIGHT = 1920
SHORTS_MAX_DURATION = 59  # seconds
SHORTS_FPS = 30

# === YouTube Upload ===
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
                  "https://www.googleapis.com/auth/youtube"]
UPLOAD_CHUNK_SIZE = -1  # Upload in single request

# === Scraper Settings ===
MAX_RESULTS_PER_SEARCH = 50
VIRAL_THRESHOLD_VIEWS = 100000
VIRAL_RATIO_THRESHOLD = 10  # views/subscriber ratio for viral detection
MIN_CHANNEL_SIZE = 1000
MAX_CHANNEL_SIZE = 500000  # Focus on small-medium channels (easier to compete)

# === Content Strategy ===
DAILY_SHORTS = 3
DAILY_LONG_VIDEOS = 1
LONG_VIDEO_DURATION_TARGET = (480, 600)  # 8-10 minutes (optimal for ads)
SHORTS_DURATION_TARGET = (30, 58)  # 30-58 seconds

# === Languages ===
SUPPORTED_LANGUAGES = ["en", "es"]
DEFAULT_LANGUAGE = "en"

# === Analytics ===
ANALYTICS_DB = DATA_DIR / "analytics.json"
PERFORMANCE_CHECK_INTERVAL = 86400  # 24 hours in seconds
