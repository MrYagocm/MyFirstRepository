"""
Niche database with REAL RPM data from 2025-2026 research.
Sources: OutlierKit, MilX, Mediacube, Miraflow, VirvID AI, FluxNote
All RPM figures are verified from actual creator earnings data.
"""

NICHES = {
    # === TIER 1: Our primary channels ===
    "betrayal_narratives": {
        "name": "Betrayal & Revenge Narratives",
        "rpm_real": {"en": 12.82, "es": 4.0},
        "cpm_range": {"en": (20, 25), "es": (6, 10)},
        "shorts_rpm": {"en": 0.08, "es": 0.03},
        "keywords_en": [
            "betrayal story", "revenge story true", "cheating story",
            "relationship betrayal", "karma revenge", "caught cheating story",
            "betrayal revenge", "true betrayal stories", "cheater exposed",
            "ultimate revenge story", "narcissist exposed"
        ],
        "content_style": "narration",
        "shorts_hooks": [
            "She thought she could get away with it",
            "He found out the truth and this happened",
            "The most satisfying revenge I've ever seen",
            "Nobody expected what happened next",
            "This betrayal story will shock you"
        ],
        "target_duration": 600,  # 10 min = mid-roll eligible
        "competition": "medium",
        "growth_rate": "21x",
        "automation_score": 95,  # Excellent for AI
        "affiliate_fit": ["audible", "kindle_unlimited", "storytelling_apps"],
        "seasonal": False,  # Year-round stable
    },

    "english_learning": {
        "name": "English Learning Podcasts",
        "rpm_real": {"en": 11.88, "es": 3.5},
        "cpm_range": {"en": (18, 22), "es": (5, 8)},
        "shorts_rpm": {"en": 0.06, "es": 0.02},
        "keywords_en": [
            "learn english", "english podcast", "english lesson",
            "english for beginners", "english conversation practice",
            "improve english speaking", "english vocabulary",
            "english grammar lesson", "daily english", "english listening practice"
        ],
        "content_style": "structured_lesson",
        "shorts_hooks": [
            "Most people say this word WRONG",
            "English trick that native speakers use",
            "Stop saying {wrong_word}, say {right_word} instead",
            "This English rule changes everything",
            "3 words that make you sound fluent"
        ],
        "target_duration": 480,  # 8 min
        "competition": "low",  # Only ~10K channels
        "growth_rate": "21x",
        "automation_score": 95,
        "affiliate_fit": ["cambly", "italki", "preply", "grammarly", "language_apps"],
        "seasonal": False,
    },

    # === TIER 2: Future expansion ===
    "finance_us_hispanic": {
        "name": "Finance for US Hispanic Audience",
        "rpm_real": {"en": 15.0, "es": 12.0},  # ES targeting US = high CPM
        "cpm_range": {"en": (22, 40), "es": (8, 25)},
        "shorts_rpm": {"en": 0.25, "es": 0.15},
        "keywords_en": [
            "finanzas personales", "como invertir dinero",
            "credito en estados unidos", "taxes para hispanos",
            "como ahorrar dinero", "inversiones para principiantes",
            "ganar dinero extra", "mejorar credit score"
        ],
        "keywords_es": [
            "finanzas personales usa", "invertir en estados unidos",
            "tarjetas de credito usa", "como hacer taxes",
            "ahorrar dinero", "credit score hispanos"
        ],
        "content_style": "educational_listicle",
        "shorts_hooks": [
            "Si vives en USA y no haces esto, estas perdiendo dinero",
            "El truco del credit score que nadie te cuenta",
            "Esto me hubiera ahorrado $10,000 en taxes",
            "3 inversiones que todo hispano en USA deberia conocer"
        ],
        "target_duration": 600,
        "competition": "low",  # Very few target US Hispanic specifically
        "growth_rate": "high",
        "automation_score": 80,
        "affiliate_fit": ["nordvpn", "hostinger", "brokers", "credit_cards", "tax_software"],
        "seasonal": True,  # Q4 spike, Q2 tax season
        "seo_strategy": "spanish_content_english_metadata",  # Key: ES audio, EN SEO
    },

    "sleep_soundscapes": {
        "name": "Sleep & Healing Soundscapes",
        "rpm_real": {"en": 10.92, "es": 3.0},
        "cpm_range": {"en": (16, 20), "es": (4, 8)},
        "shorts_rpm": {"en": 0.04, "es": 0.01},
        "keywords_en": [
            "sleep music", "healing frequencies", "rain sounds sleep",
            "deep sleep music", "relaxation music", "meditation music",
            "white noise sleep", "ambient sounds", "sleep soundscape"
        ],
        "content_style": "ambient_audio",
        "shorts_hooks": [
            "Fall asleep in 3 minutes with this sound",
            "Your brain needs this frequency to heal",
            "The sound that cures insomnia"
        ],
        "target_duration": 3600,  # 1 hour+ = many mid-rolls
        "competition": "medium",
        "growth_rate": "moderate",
        "automation_score": 100,  # Easiest to automate
        "affiliate_fit": ["sleep_apps", "meditation_apps", "wellness"],
        "seasonal": False,
    },

    "psychology": {
        "name": "Psychology & Human Behavior",
        "rpm_real": {"en": 9.0, "es": 3.5},
        "cpm_range": {"en": (12, 18), "es": (5, 9)},
        "shorts_rpm": {"en": 0.07, "es": 0.03},
        "keywords_en": [
            "dark psychology", "manipulation tactics", "body language secrets",
            "how to read people", "stoicism", "psychology tricks",
            "narcissist signs", "emotional intelligence", "human behavior"
        ],
        "content_style": "educational_listicle",
        "shorts_hooks": [
            "If someone does this, RUN",
            "Psychologists say this trick works every time",
            "Signs you're dealing with a narcissist",
            "People who do this are secretly manipulating you"
        ],
        "target_duration": 540,
        "competition": "high",
        "growth_rate": "high",
        "automation_score": 85,
        "affiliate_fit": ["self_help_books", "therapy_apps", "courses"],
        "seasonal": False,
    },
}

# === Quick filters based on REAL data ===
HIGH_RPM_NICHES = [k for k, v in NICHES.items() if v["rpm_real"]["en"] >= 10.0]
BLUE_OCEAN_NICHES = [k for k, v in NICHES.items() if v["competition"] in ("low",)]
BEST_AUTOMATION = [k for k, v in NICHES.items() if v["automation_score"] >= 90]
BEST_FOR_SHORTS = [k for k, v in NICHES.items() if v["shorts_rpm"]["en"] >= 0.06]

# Primary channels to launch
PRIMARY_CHANNELS = ["betrayal_narratives", "english_learning"]
EXPANSION_CHANNELS = ["finance_us_hispanic", "sleep_soundscapes"]
