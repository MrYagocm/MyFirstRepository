"""
Configuration settings for YouTube Automation System v2.
Optimized for MINIMUM cost, MAXIMUM revenue.
Stack: Gemini (free) + Google Cloud TTS (free) + FLUX (cheap) + MoneyPrinterTurbo
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
# Tier 1: FREE
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")

# Tier 2: CHEAP (optional upgrades)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")  # For FLUX images
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")  # Premium TTS

# Tier 3: Platform
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# === LLM Config (Script Generation) ===
# Priority: Gemini free > Claude > GPT-4o
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini, claude, openai
GEMINI_MODEL = "gemini-2.0-flash"  # Free tier: 60 req/min
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 4096

# === TTS Config (Voice) ===
# Priority: Google Cloud free > Edge TTS free > Voxtral cheap > ElevenLabs premium
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "google_cloud")  # google_cloud, edge, voxtral, elevenlabs
GOOGLE_TTS_VOICE_EN = "en-US-Neural2-D"  # Free: 1M chars/month
GOOGLE_TTS_VOICE_ES = "es-US-Neural2-A"  # US Hispanic targeting
EDGE_TTS_VOICE_EN = "en-US-ChristopherNeural"
EDGE_TTS_VOICE_ES = "es-ES-AlvaroNeural"
ELEVENLABS_VOICE_ID_EN = os.getenv("ELEVENLABS_VOICE_ID_EN", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_VOICE_ID_ES = os.getenv("ELEVENLABS_VOICE_ID_ES", "ThT5KcBeYPX3keUQqHPh")
ELEVENLABS_MODEL = "eleven_multilingual_v2"

# === Image Generation ===
# Priority: FLUX Kontext on SiliconFlow ($0.015/img) > Google Imagen 4 > Replicate
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "siliconflow")  # siliconflow, google_imagen, replicate
FLUX_MODEL = "black-forest-labs/FLUX.1-kontext-dev"
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720

# === Video Settings ===
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_BITRATE = "5000k"
SHORTS_WIDTH = 1080
SHORTS_HEIGHT = 1920
SHORTS_MAX_DURATION = 59
SHORTS_FPS = 30

# === YouTube Upload ===
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly"
]

# === Multi-Channel Config ===
CHANNELS = {
    "betrayal_stories": {
        "name": "Betrayal & Revenge Narratives",
        "niche": "betrayal_narratives",
        "language": "en",
        "credentials_file": "client_secrets_ch1.json",
        "upload_schedule": {"long": 3, "shorts": 7},  # per week
    },
    "english_learning": {
        "name": "English Learning Podcasts",
        "niche": "english_learning",
        "language": "en",
        "credentials_file": "client_secrets_ch2.json",
        "upload_schedule": {"long": 3, "shorts": 5},
    },
}

# === Scraper Settings ===
MAX_RESULTS_PER_SEARCH = 50
VIRAL_THRESHOLD_VIEWS = 100000
VIRAL_RATIO_THRESHOLD = 10
MIN_CHANNEL_SIZE = 1000
MAX_CHANNEL_SIZE = 500000

# === Content Strategy (v2: quality > quantity) ===
WEEKLY_LONG_VIDEOS = 3  # Per channel, NOT daily
WEEKLY_SHORTS = 7  # Per channel
LONG_VIDEO_DURATION_TARGET = (480, 720)  # 8-12 minutes (mid-roll eligible)
SHORTS_DURATION_TARGET = (30, 58)
SHORTS_USE_MUSIC = False  # No music = higher RPM on Shorts

# === Languages ===
SUPPORTED_LANGUAGES = ["en", "es"]
DEFAULT_LANGUAGE = "en"

# === Analytics ===
ANALYTICS_DB = DATA_DIR / "analytics.json"
PERFORMANCE_CHECK_INTERVAL = 86400

# === Affiliate Links ===
AFFILIATE_LINKS = {
    "betrayal_narratives": {
        "audible": os.getenv("AFFILIATE_AUDIBLE", ""),
        "kindle": os.getenv("AFFILIATE_KINDLE", ""),
    },
    "english_learning": {
        "cambly": os.getenv("AFFILIATE_CAMBLY", ""),
        "italki": os.getenv("AFFILIATE_ITALKI", ""),
        "preply": os.getenv("AFFILIATE_PREPLY", ""),
    },
    "finance_us_hispanic": {
        "nordvpn": os.getenv("AFFILIATE_NORDVPN", ""),
        "hostinger": os.getenv("AFFILIATE_HOSTINGER", ""),
    }
}
