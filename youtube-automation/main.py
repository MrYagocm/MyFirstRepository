"""
YouTube Automation System v2 - CLI Entry Point
Optimized for maximum revenue with minimum cost.

Usage:
    python main.py analyze [--lang en|es]
    python main.py compare [--niche betrayal_narratives]
    python main.py produce [--topic "..."] [--niche ...] [--short] [--no-upload]
    python main.py run [--channel betrayal_stories] [--no-upload]
    python main.py run-all [--no-upload]
    python main.py autopilot [--interval 24]
    python main.py report
    python main.py cost-estimate
"""

import click
import schedule
import time
from config.niches import NICHES, PRIMARY_CHANNELS
from config.settings import CHANNELS
from pipeline.orchestrator import Orchestrator


@click.group()
def cli():
    """YouTube Automation v2 - Data-driven money machine."""
    pass


@cli.command()
@click.option("--lang", default="en", help="Language: en or es")
def analyze(lang):
    """Analyze all niches and find the best opportunity."""
    orch = Orchestrator()
    orch.analyze(language=lang)


@cli.command()
@click.option("--niche", default="betrayal_narratives", help="Niche to compare")
def compare(niche):
    """Compare EN vs ES for a niche."""
    orch = Orchestrator()
    orch.compare(niche=niche)


@cli.command()
@click.option("--topic", default=None, help="Video topic (auto-detected if not provided)")
@click.option("--niche", default="betrayal_narratives", help="Niche")
@click.option("--lang", default="en", help="Language: en or es")
@click.option("--short", is_flag=True, help="Create a YouTube Short")
@click.option("--no-upload", is_flag=True, help="Don't upload, just produce locally")
def produce(topic, niche, lang, short, no_upload):
    """Produce a single video."""
    orch = Orchestrator()
    result = orch.produce(
        topic=topic, niche=niche, language=lang,
        is_short=short, upload=not no_upload
    )
    if result.get("error"):
        click.echo(f"\nError: {result['error']}")
    else:
        click.echo(f"\nVideo: {result.get('video', 'N/A')}")
        click.echo(f"Title: {result.get('script', {}).get('title', 'N/A')}")


@cli.command()
@click.option("--channel", default=None, help="Channel ID (from config)")
@click.option("--no-upload", is_flag=True, help="Don't upload")
def run(channel, no_upload):
    """Run production for a channel (weekly batch)."""
    orch = Orchestrator()
    if channel:
        orch.run_channel(channel, upload=not no_upload)
    else:
        # Default: run first primary channel
        first_channel = list(CHANNELS.keys())[0]
        orch.run_channel(first_channel, upload=not no_upload)


@cli.command("run-all")
@click.option("--no-upload", is_flag=True, help="Don't upload")
def run_all(no_upload):
    """Run production for ALL channels."""
    orch = Orchestrator()
    orch.run_all_channels(upload=not no_upload)


@cli.command()
@click.option("--interval", default=168, help="Hours between runs (default: 168 = weekly)")
@click.option("--lang", default="en", help="Language")
def autopilot(interval, lang):
    """Autopilot mode - weekly production and upload."""
    click.echo(f"\n=== AUTOPILOT MODE (every {interval}h) ===")
    click.echo("Press Ctrl+C to stop\n")

    orch = Orchestrator()

    def weekly_run():
        click.echo(f"\n--- Autopilot run: {time.strftime('%Y-%m-%d %H:%M')} ---")
        try:
            orch.run_all_channels(upload=True)
        except Exception as e:
            click.echo(f"Error: {e}")

    weekly_run()
    schedule.every(interval).hours.do(weekly_run)

    while True:
        schedule.run_pending()
        time.sleep(60)


@cli.command()
def report():
    """Show performance report with revenue estimates."""
    orch = Orchestrator()
    orch.report()


@cli.command("cost-estimate")
def cost_estimate():
    """Estimate monthly costs for current configuration."""
    from config.settings import TTS_PROVIDER, LLM_PROVIDER, IMAGE_PROVIDER

    click.echo("\n=== MONTHLY COST ESTIMATE ===\n")

    # Calculate based on 2 channels, 3 long + 7 shorts per week each
    videos_per_week = (3 + 7) * len(CHANNELS)  # per channel
    videos_per_month = videos_per_week * 4

    llm_cost = {"gemini": 0.0, "claude": 0.02, "openai": 0.02}
    tts_cost = {"google_cloud": 0.0, "edge": 0.0, "voxtral": 0.013, "elevenlabs": 0.13}
    img_cost = {"siliconflow": 0.015 * 5, "google_imagen": 0.01 * 5, "replicate": 0.04 * 5}

    script_total = llm_cost.get(LLM_PROVIDER, 0) * videos_per_month
    voice_total = tts_cost.get(TTS_PROVIDER, 0) * videos_per_month
    image_total = img_cost.get(IMAGE_PROVIDER, 0) * videos_per_month

    click.echo(f"Channels: {len(CHANNELS)}")
    click.echo(f"Videos/month: {videos_per_month}")
    click.echo(f"")
    click.echo(f"Scripts ({LLM_PROVIDER}): ${script_total:.2f}")
    click.echo(f"Voice ({TTS_PROVIDER}): ${voice_total:.2f}")
    click.echo(f"Images ({IMAGE_PROVIDER}): ${image_total:.2f}")
    click.echo(f"Hosting (GitHub Actions): $0.00")
    click.echo(f"{'─' * 30}")
    click.echo(f"TOTAL: ${script_total + voice_total + image_total:.2f}/month")

    # Revenue estimate
    click.echo(f"\n=== REVENUE ESTIMATE (Month 12) ===\n")
    for niche_key in PRIMARY_CHANNELS:
        niche = NICHES.get(niche_key, {})
        rpm = niche.get("rpm_real", {}).get("en", 5)
        click.echo(f"{niche.get('name', niche_key)}: RPM ${rpm}")

    click.echo(f"\nWith 1.2M views/month across {len(CHANNELS)} channels:")
    avg_rpm = sum(NICHES[n]["rpm_real"]["en"] for n in PRIMARY_CHANNELS) / len(PRIMARY_CHANNELS)
    click.echo(f"  AdSense: ${1200000 * avg_rpm / 1000:,.0f}/month")
    click.echo(f"  Affiliates (est): ${1200000 * avg_rpm / 1000 * 0.4:,.0f}/month")
    click.echo(f"  Total est: ${1200000 * avg_rpm / 1000 * 1.4:,.0f}/month")


if __name__ == "__main__":
    cli()
