"""
Orchestrator v2: Intelligence-driven content pipeline.
Analyze -> Decide -> Produce -> Vary -> Upload -> Track -> Learn -> Repeat
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import SCRIPTS_DIR, DATA_DIR, CHANNELS, WEEKLY_LONG_VIDEOS, WEEKLY_SHORTS
from config.niches import NICHES, PRIMARY_CHANNELS
from scraper.niche_analyzer import NicheAnalyzer
from scraper.trend_detector import TrendDetector
from generator.script_writer import ScriptWriter
from generator.tts_engine import TTSEngine
from generator.subtitle_generator import SubtitleGenerator
from generator.video_assembler import VideoAssembler
from generator.thumbnail_creator import ThumbnailCreator
from generator.affiliate_engine import AffiliateEngine
from uploader.youtube_uploader import YouTubeUploader
from uploader.seo_optimizer import SEOOptimizer
from analytics.performance_tracker import PerformanceTracker
from pipeline.content_variation import ContentVariation
from pipeline.multi_platform import MultiPlatformRepurposer


class Orchestrator:
    """v2 Pipeline: data-driven, multi-channel, anti-detection."""

    def __init__(self):
        self.analyzer = NicheAnalyzer()
        self.trend_detector = TrendDetector()
        self.script_writer = ScriptWriter()
        self.tts = TTSEngine()
        self.subtitles = SubtitleGenerator()
        self.assembler = VideoAssembler()
        self.thumbnails = ThumbnailCreator()
        self.uploader = YouTubeUploader()
        self.seo = SEOOptimizer()
        self.tracker = PerformanceTracker()
        self.variation = ContentVariation()
        self.affiliates = AffiliateEngine()
        self.repurposer = MultiPlatformRepurposer()

    def analyze(self, language: str = "en") -> dict:
        """Analyze all niches and find best opportunity."""
        print("\n=== ANALYZING NICHES (Real RPM Data) ===")
        result = self.analyzer.find_best_opportunity(language)

        if "error" in result:
            print(f"[Pipeline] Analysis error: {result['error']}")
            return result

        best = result["best_niche"]
        print(f"\n Best opportunity: {best['niche_name']}")
        print(f"  Score: {best['opportunity_score']}/100")
        print(f"  RPM: ${best['rpm_estimate']}")

        return result

    def produce(self, topic: Optional[str] = None, niche: str = "betrayal_narratives",
                language: str = "en", is_short: bool = False,
                upload: bool = False, channel_id: Optional[str] = None) -> dict:
        """Full production pipeline with anti-fingerprinting."""
        vid_type = "SHORT" if is_short else "VIDEO"
        print(f"\n=== PRODUCING {vid_type} [{niche}] ===")

        # Get variation parameters (anti-detection)
        variation_params = self.variation.get_variation_params()
        print(f"  Variation ID: {variation_params['variation_id']}")

        # Step 1: Topic selection
        if not topic:
            topic = self._select_topic(niche, language)
        print(f"  Topic: {topic}")

        # Step 2: Script with variation
        print("  Writing script...")
        niche_data = NICHES.get(niche, {})

        if is_short:
            hooks = niche_data.get("shorts_hooks", [])
            hook = hooks[hash(topic) % len(hooks)] if hooks else None
            script = self.script_writer.write_short_script(topic, niche, language, hook)
        else:
            target_duration = niche_data.get("target_duration", 480)
            style = niche_data.get("content_style", "narration")
            script = self.script_writer.write_long_script(
                topic, niche, language, target_duration, style
            )

        # Step 3: Generate audio
        print("  Generating audio...")
        script_id = hashlib.md5(f"{topic}{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        narration = self.script_writer.get_full_narration(script)
        audio_path = self.tts.generate_audio(narration, language, f"audio_{script_id}.mp3")

        if not audio_path:
            return {"error": "Audio generation failed", "script": script}

        # Step 4: Subtitles
        print("  Generating subtitles...")
        sub_path = self.subtitles.generate_srt(narration, f"subs_{script_id}.srt")

        # Step 5: Visuals with variation
        print("  Creating visuals...")
        visual_prompts = self._extract_visual_prompts(script, topic)
        images = self.thumbnails.generate_content_images(visual_prompts, niche, count=5)
        thumbnail_path = self.thumbnails.create_thumbnail(
            script.get("title", topic), niche, output_filename=f"thumb_{script_id}.png"
        )

        # Step 6: Assemble video
        print("  Assembling video...")
        video_filename = f"{'short' if is_short else 'video'}_{script_id}.mp4"
        if is_short:
            video_path = self.assembler.assemble_short(audio_path, images, sub_path, video_filename)
        else:
            video_path = self.assembler.assemble_long_video(audio_path, images, sub_path, video_filename)

        if not video_path:
            return {"error": "Video assembly failed", "script": script}

        # Step 7: Save script
        script_path = SCRIPTS_DIR / f"script_{script_id}.json"
        script_path.write_text(json.dumps(script, indent=2))

        result = {
            "script": script, "audio": str(audio_path), "video": str(video_path),
            "thumbnail": str(thumbnail_path) if thumbnail_path else None,
            "subtitles": str(sub_path) if sub_path else None,
            "topic": topic, "niche": niche, "language": language,
            "is_short": is_short, "variation": variation_params,
        }

        # Step 8: Upload
        if upload:
            result["upload"] = self._upload(result, channel_id)

            # Step 9: Repurpose for other platforms
            if is_short and video_path:
                print("  Repurposing for TikTok/Instagram/Facebook...")
                result["repurposed"] = self.repurposer.repurpose_all_platforms(video_path)

        print(f"\n  Production complete: {script.get('title', 'N/A')}")
        return result

    def run_channel(self, channel_id: str, upload: bool = True) -> dict:
        """Run production for a specific channel."""
        channel = CHANNELS.get(channel_id)
        if not channel:
            return {"error": f"Channel '{channel_id}' not found"}

        niche = channel["niche"]
        language = channel["language"]
        schedule = channel["upload_schedule"]

        print(f"\n{'='*50}")
        print(f"  CHANNEL: {channel['name']}")
        print(f"  Niche: {niche} | Language: {language}")
        print(f"{'='*50}")

        results = {"channel": channel_id, "videos": []}

        # Produce long videos
        for i in range(schedule.get("long", 3)):
            print(f"\n--- Long video {i+1}/{schedule['long']} ---")
            result = self.produce(niche=niche, language=language,
                                   is_short=False, upload=upload, channel_id=channel_id)
            results["videos"].append(result)

            # Anti-detection delay between uploads
            if upload and i < schedule["long"] - 1:
                delay = self.variation.get_upload_delay()
                print(f"  Waiting {delay} min before next upload (anti-detection)")

        # Produce Shorts
        for i in range(schedule.get("shorts", 7)):
            print(f"\n--- Short {i+1}/{schedule['shorts']} ---")
            result = self.produce(niche=niche, language=language,
                                   is_short=True, upload=upload, channel_id=channel_id)
            results["videos"].append(result)

        return results

    def run_all_channels(self, upload: bool = True) -> dict:
        """Run production for ALL configured channels."""
        print("\n" + "=" * 60)
        print("  YOUTUBE AUTOMATION v2 - FULL RUN (ALL CHANNELS)")
        print("=" * 60)

        all_results = {}
        for channel_id in CHANNELS:
            all_results[channel_id] = self.run_channel(channel_id, upload)

        total_videos = sum(len(r["videos"]) for r in all_results.values())
        print(f"\n{'='*60}")
        print(f"  COMPLETE: {total_videos} videos across {len(CHANNELS)} channels")
        print(f"{'='*60}")

        return all_results

    def report(self) -> dict:
        """Performance report with revenue estimates."""
        report = self.tracker.generate_report()

        print("\n=== PERFORMANCE REPORT ===")
        print(f"Total videos: {report['total_videos']}")
        print(f"Total views: {report['total_views']:,}")

        # Add affiliate revenue estimate
        for niche, stats in report.get("niche_breakdown", {}).items():
            affiliate_est = self.affiliates.estimate_affiliate_revenue(
                niche, stats.get("total_views", 0)
            )
            print(f"\n{niche}:")
            print(f"  AdSense est: ${stats['total_views'] * NICHES.get(niche, {}).get('rpm_real', {}).get('en', 5) / 1000:.0f}")
            print(f"  Affiliate est: ${affiliate_est['estimated_monthly']:.0f}")

        return report

    def _select_topic(self, niche: str, language: str) -> str:
        """Intelligently select the best topic based on data."""
        analysis = self.analyzer.analyze_niche(niche, language)
        topics = analysis.get("recommended_topics", [])

        if topics:
            topic = topics[0].split(": ", 1)[-1] if ": " in topics[0] else topics[0]
            return topic

        niche_data = NICHES.get(niche, {})
        keywords = niche_data.get("keywords_en", ["interesting topic"])
        return keywords[hash(datetime.now().isoformat()) % len(keywords)]

    def _upload(self, production: dict, channel_id: Optional[str] = None) -> dict:
        """Upload with SEO optimization and affiliate links."""
        script = production["script"]
        video_path = Path(production["video"])
        niche = production["niche"]
        language = production["language"]

        # Optimize SEO
        optimized = self.seo.optimize_metadata(
            script.get("title", ""), script.get("description", ""),
            script.get("tags", []), niche, language
        )

        # Add affiliate links to description
        description = self.affiliates.generate_description(
            optimized.get("description", ""), niche, language
        )

        # Upload
        video_id = self.uploader.upload_video(
            video_path=video_path,
            title=optimized.get("title", script.get("title", "Video")),
            description=description,
            tags=optimized.get("tags", []),
            is_short=production.get("is_short", False)
        )

        if video_id:
            if production.get("thumbnail"):
                self.uploader.set_thumbnail(video_id, Path(production["thumbnail"]))

            self.tracker.record_upload(
                video_id=video_id,
                title=optimized.get("title", ""),
                niche=niche, language=language,
                is_short=production.get("is_short", False),
                metadata=optimized
            )
            return {"video_id": video_id, "url": f"https://youtube.com/watch?v={video_id}"}

        return {"error": "Upload failed"}

    def _extract_visual_prompts(self, script: dict, fallback: str) -> list[str]:
        """Extract visual prompts from script."""
        prompts = []
        if script.get("sections"):
            for section in script["sections"]:
                visual = section.get("visual_notes", section.get("title", fallback))
                prompts.append(visual)
        elif script.get("visual_notes"):
            prompts.append(script["visual_notes"])
        return prompts[:8] or [fallback] * 3
