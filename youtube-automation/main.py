"""
YouTube Automation System - CLI Entry Point
Usage:
    python main.py analyze [--lang en|es]
    python main.py compare [--niche facts_curiosities]
    python main.py produce [--topic "..."] [--niche ...] [--short] [--no-upload]
    python main.py run [--niche ...] [--lang en|es]
    python main.py schedule [--interval 24]
    python main.py report
"""

import click
import schedule
import time
from pipeline.orchestrator import Orchestrator


@click.group()
def cli():
    """YouTube Automation System - Generate money while you sleep."""
    pass


@cli.command()
@click.option("--lang", default="en", help="Language: en or es")
def analyze(lang):
    """Analyze all niches and find the best opportunity."""
    orch = Orchestrator()
    orch.analyze(language=lang)


@cli.command()
@click.option("--niche", default="facts_curiosities", help="Niche to compare")
def compare(niche):
    """Compare EN vs ES for a niche."""
    orch = Orchestrator()
    orch.compare(niche=niche)


@cli.command()
@click.option("--topic", default=None, help="Video topic (auto-detected if not provided)")
@click.option("--niche", default="facts_curiosities", help="Niche")
@click.option("--lang", default="en", help="Language: en or es")
@click.option("--short", is_flag=True, help="Create a YouTube Short")
@click.option("--no-upload", is_flag=True, help="Don't upload, just produce locally")
def produce(topic, niche, lang, short, no_upload):
    """Produce a single video (script + audio + video)."""
    orch = Orchestrator()
    result = orch.produce(
        topic=topic,
        niche=niche,
        language=lang,
        is_short=short,
        upload=not no_upload
    )

    if result.get("error"):
        click.echo(f"\nError: {result['error']}")
    else:
        click.echo(f"\nVideo ready: {result.get('video', 'N/A')}")


@cli.command()
@click.option("--niche", default=None, help="Niche (auto-selected if not provided)")
@click.option("--lang", default="en", help="Language: en or es")
@click.option("--no-upload", is_flag=True, help="Don't upload")
def run(niche, lang, no_upload):
    """Full automated run: analyze -> produce all daily content -> upload."""
    orch = Orchestrator()
    orch.run(niche=niche, language=lang, upload=not no_upload)


@cli.command()
@click.option("--interval", default=24, help="Hours between runs")
@click.option("--lang", default="en", help="Language")
def autopilot(interval, lang):
    """Run on autopilot - produces and uploads daily."""
    click.echo(f"\n=== AUTOPILOT MODE (every {interval}h) ===")
    click.echo("Press Ctrl+C to stop\n")

    orch = Orchestrator()

    def daily_run():
        click.echo(f"\n--- Autopilot run at {time.strftime('%Y-%m-%d %H:%M')} ---")
        try:
            orch.run(language=lang, upload=True)
        except Exception as e:
            click.echo(f"Error in autopilot run: {e}")

    # Run immediately
    daily_run()

    # Schedule future runs
    schedule.every(interval).hours.do(daily_run)

    while True:
        schedule.run_pending()
        time.sleep(60)


@cli.command()
def report():
    """Show performance report."""
    orch = Orchestrator()
    orch.report()


if __name__ == "__main__":
    cli()
