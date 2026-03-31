"""
Niche database with RPM estimates, keywords, and content strategies.
Focus: maximum revenue per view.
"""

NICHES = {
    "ai_tools": {
        "name": "AI Tools & Technology",
        "rpm_estimate": {"en": 12.0, "es": 4.0},
        "keywords_en": [
            "best ai tools", "ai tools 2025", "chatgpt alternatives",
            "free ai tools", "ai for productivity", "ai automation",
            "best ai apps", "ai tools you need", "ai news today"
        ],
        "keywords_es": [
            "herramientas ia", "mejores ia 2025", "alternativas chatgpt",
            "ia gratis", "ia productividad", "automatizacion ia"
        ],
        "content_style": "demo_showcase",
        "shorts_hooks": [
            "This AI tool will blow your mind",
            "Stop what you're doing and try this AI",
            "Free AI tool nobody talks about",
            "This AI replaces {tool_name}"
        ],
        "target_duration": 480,
        "competition": "high",
        "growth_potential": "very_high"
    },
    "finance_investing": {
        "name": "Finance & Investing",
        "rpm_estimate": {"en": 15.0, "es": 5.0},
        "keywords_en": [
            "how to invest", "passive income ideas", "make money online",
            "stock market today", "crypto news", "financial freedom",
            "money tips", "investing for beginners", "side hustle ideas"
        ],
        "keywords_es": [
            "como invertir", "ingresos pasivos", "ganar dinero online",
            "invertir para principiantes", "libertad financiera",
            "ideas negocio"
        ],
        "content_style": "educational_listicle",
        "shorts_hooks": [
            "If you have ${amount}, do this NOW",
            "Rich people do this every morning",
            "This passive income idea prints money",
            "Nobody teaches you this about money"
        ],
        "target_duration": 600,
        "competition": "very_high",
        "growth_potential": "high"
    },
    "facts_curiosities": {
        "name": "Facts & Curiosities",
        "rpm_estimate": {"en": 4.0, "es": 2.5},
        "keywords_en": [
            "did you know", "amazing facts", "top 10", "unbelievable facts",
            "things you didn't know", "mind blowing facts", "fun facts",
            "interesting facts", "facts about"
        ],
        "keywords_es": [
            "sabias que", "datos curiosos", "top 10", "datos increibles",
            "cosas que no sabias", "curiosidades", "datos interesantes"
        ],
        "content_style": "rapid_facts",
        "shorts_hooks": [
            "I bet you didn't know this",
            "This fact will change how you see {topic}",
            "Scientists can't explain this",
            "99% of people don't know this"
        ],
        "target_duration": 480,
        "competition": "medium",
        "growth_potential": "very_high"
    },
    "scary_stories": {
        "name": "Scary Stories & Horror",
        "rpm_estimate": {"en": 6.0, "es": 3.0},
        "keywords_en": [
            "scary stories", "true horror stories", "creepypasta",
            "horror stories", "scary facts", "true scary stories",
            "nightmare stories", "reddit horror", "paranormal stories"
        ],
        "keywords_es": [
            "historias de terror", "creepypasta español", "historias miedo",
            "relatos terror", "leyendas urbanas", "historias paranormales"
        ],
        "content_style": "narration",
        "shorts_hooks": [
            "This real story will terrify you",
            "Don't watch this alone at night",
            "The scariest thing I've ever heard",
            "This happened to someone last week"
        ],
        "target_duration": 600,
        "competition": "medium",
        "growth_potential": "high"
    },
    "life_hacks": {
        "name": "Life Hacks & Tips",
        "rpm_estimate": {"en": 5.0, "es": 2.5},
        "keywords_en": [
            "life hacks", "tips and tricks", "things you're doing wrong",
            "genius ideas", "smart gadgets", "useful inventions",
            "home hacks", "cleaning hacks"
        ],
        "keywords_es": [
            "trucos caseros", "tips y trucos", "ideas geniales",
            "inventos utiles", "trucos limpieza", "hacks vida"
        ],
        "content_style": "rapid_facts",
        "shorts_hooks": [
            "You've been doing this WRONG your whole life",
            "Try this hack tonight",
            "I wish I knew this sooner",
            "This $1 trick saves hundreds"
        ],
        "target_duration": 480,
        "competition": "medium",
        "growth_potential": "high"
    },
    "psychology": {
        "name": "Psychology & Self-Improvement",
        "rpm_estimate": {"en": 8.0, "es": 3.5},
        "keywords_en": [
            "psychology facts", "dark psychology", "manipulation tactics",
            "body language", "how to read people", "stoicism",
            "self improvement", "habits of successful people"
        ],
        "keywords_es": [
            "psicologia oscura", "lenguaje corporal", "estoicismo",
            "como leer personas", "habitos exitosos", "superacion personal"
        ],
        "content_style": "educational_listicle",
        "shorts_hooks": [
            "If someone does this, RUN",
            "Psychologists say this trick works every time",
            "Dark psychology trick #47",
            "People who do this are secretly manipulating you"
        ],
        "target_duration": 540,
        "competition": "high",
        "growth_potential": "very_high"
    }
}

# RPM tiers for quick filtering
HIGH_RPM_NICHES = [k for k, v in NICHES.items() if v["rpm_estimate"]["en"] >= 8.0]
EASY_GROWTH_NICHES = [k for k, v in NICHES.items() if v["competition"] in ("low", "medium")]
BEST_FOR_SHORTS = ["facts_curiosities", "life_hacks", "psychology", "ai_tools"]
