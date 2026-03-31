"""
Affiliate Engine: automatically injects affiliate links and CTAs
into video descriptions based on niche.
Affiliate revenue should be 30-40% of total income.
"""

from typing import Optional
from config.settings import AFFILIATE_LINKS
from config.niches import NICHES


# Default affiliate templates by niche
AFFILIATE_TEMPLATES = {
    "betrayal_narratives": {
        "section": """
---
Resources mentioned in this video:
{links}

If you love stories like this, you'll love these:
""",
        "default_links": [
            ("Listen to more stories on Audible (free trial)", "{audible}"),
            ("Read the full story on Kindle Unlimited", "{kindle}"),
        ]
    },
    "english_learning": {
        "section": """
---
Improve your English faster:
{links}

Practice what you learned today!
""",
        "default_links": [
            ("Practice speaking with a tutor on Cambly", "{cambly}"),
            ("Book a lesson on italki", "{italki}"),
            ("Try Preply for personalized learning", "{preply}"),
        ]
    },
    "finance_us_hispanic": {
        "section": """
---
Herramientas mencionadas:
{links}

Protege tu informacion financiera online.
""",
        "default_links": [
            ("Protege tu privacidad con NordVPN (descuento especial)", "{nordvpn}"),
            ("Crea tu sitio web con Hostinger (40% descuento)", "{hostinger}"),
        ]
    },
    "sleep_soundscapes": {
        "section": """
---
Improve your sleep:
{links}
""",
        "default_links": [
            ("Try this sleep app (free trial)", "{sleep_app}"),
        ]
    },
    "psychology": {
        "section": """
---
Go deeper:
{links}
""",
        "default_links": [
            ("Read more on Audible (free trial)", "{audible}"),
            ("Explore courses on Skillshare", "{skillshare}"),
        ]
    },
}


class AffiliateEngine:
    """Manages affiliate links and revenue optimization."""

    def __init__(self):
        self.links = AFFILIATE_LINKS

    def generate_description(self, base_description: str, niche: str,
                               language: str = "en") -> str:
        """Add affiliate section to video description."""
        template = AFFILIATE_TEMPLATES.get(niche, {})
        if not template:
            return base_description

        niche_links = self.links.get(niche, {})
        link_lines = []

        for text, url_template in template.get("default_links", []):
            # Replace placeholders with actual affiliate links
            url = url_template
            for key, value in niche_links.items():
                url = url.replace(f"{{{key}}}", value)

            # Only include links that have actual URLs
            if url and not url.startswith("{"):
                link_lines.append(f"  {text}: {url}")
            elif not url.startswith("{"):
                link_lines.append(f"  {text}")

        if not link_lines:
            return base_description

        links_text = "\n".join(link_lines)
        affiliate_section = template["section"].format(links=links_text)

        # Add multi-platform CTA
        multi_platform_cta = self._get_multi_platform_cta(language)

        return f"{base_description}\n{affiliate_section}\n{multi_platform_cta}"

    def get_pinned_comment(self, niche: str, language: str = "en") -> Optional[str]:
        """Generate a pinned comment with affiliate link (higher visibility)."""
        niche_links = self.links.get(niche, {})
        if not niche_links:
            return None

        # Get the highest-value affiliate link for the pinned comment
        first_link_key = list(niche_links.keys())[0]
        first_link = niche_links[first_link_key]

        if not first_link:
            return None

        if language == "es":
            return f"El recurso que menciono en el video: {first_link}"
        return f"The resource I mentioned in the video: {first_link}"

    def _get_multi_platform_cta(self, language: str) -> str:
        """CTA for other platforms (TikTok, Instagram, etc.)."""
        if language == "es":
            return "Sigueme en TikTok e Instagram para mas contenido!"
        return "Follow me on TikTok and Instagram for more content!"

    def estimate_affiliate_revenue(self, niche: str, monthly_views: int) -> dict:
        """Estimate affiliate revenue based on niche and views."""
        # Average click-through rates from description links
        ctr = 0.02  # 2% of viewers click description links
        conversion_rate = 0.03  # 3% of clickers convert

        niche_data = NICHES.get(niche, {})
        affiliate_fit = niche_data.get("affiliate_fit", [])

        # Average commission by affiliate type
        avg_commissions = {
            "audible": 15.0, "kindle_unlimited": 5.0, "kindle": 5.0,
            "cambly": 20.0, "italki": 15.0, "preply": 15.0, "grammarly": 10.0,
            "nordvpn": 100.0, "hostinger": 50.0, "brokers": 200.0,
            "credit_cards": 50.0, "sleep_apps": 8.0, "meditation_apps": 10.0,
            "self_help_books": 5.0, "therapy_apps": 15.0, "courses": 25.0,
            "language_apps": 12.0, "storytelling_apps": 8.0, "tax_software": 30.0,
            "skillshare": 7.0, "sleep_app": 8.0, "wellness": 10.0,
        }

        clicks = monthly_views * ctr
        conversions = clicks * conversion_rate

        total_commission = 0
        breakdown = {}
        for affiliate in affiliate_fit:
            commission = avg_commissions.get(affiliate, 10.0)
            affiliate_conversions = conversions / len(affiliate_fit)
            revenue = affiliate_conversions * commission
            breakdown[affiliate] = round(revenue, 2)
            total_commission += revenue

        return {
            "estimated_monthly": round(total_commission, 2),
            "breakdown": breakdown,
            "assumptions": {
                "ctr": f"{ctr*100}%",
                "conversion_rate": f"{conversion_rate*100}%",
                "monthly_views": monthly_views
            }
        }
