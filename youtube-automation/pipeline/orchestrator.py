"""
Orchestrator: the main pipeline that ties everything together.
Analyze -> Script -> Audio -> Video -> Upload -> Track.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import SCRIPTS_DIR, DATA_DIR
from config.niches import NICHES
from scraper.niche_analyzer import NicheAnalyzer
from scraper.trend_detector import TrendDetector
from generator.script_writer import ScriptWriter
from generator.tts_engine import TTSEngine
from generator.subtitle_generator import SubtitleGenerator
from generator.video_assembler import VideoAssembler
from generator.thumbnail_creator import ThumbnailCreator
from uploader.youtube_uploader import YouTubeUploader
from uploader.seo_optimizer import SEOOptimizer
from analytics.performance_tracker import PerformanceTracker


class Orchestrator:
    """Main pipeline orchestrator. Runs the full content creation cycle."""

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

    def analyze(self, language: str = "en") -> dict:
        """Analyze all niches and find the best opportunity."""
        print("\n=== ANALYZING NICHES ===")
        result = self.analyzer.find_best_opportunity(language)

        if "error" in result:
            print(f"[Pipeline] Analysis error: {result['error']}")
            return result

        best = result["best_niche"]
        print(f"\n[Pipeline] Best opportunity: {best['niche_name']}")
        print(f"  Score: {best['opportunity_score']}/100")
        print(f"  RPM: ${best['rpm_estimate']}")
        print(f"  Competition: {best['competition']['level']}")

        print("\n[Pipeline] All rankings:")
        for r in result["rankings"]:
            print(f"  {r['name']}: {r['score']}/100 (RPM: ${r['rpm']})")

        return result

    def compare(self, niche: str = "facts_curiosities") -> dict:
        """Compare EN vs ES for a niche."""
        print(f"\n=== COMPARING EN vs ES: {niche} ===")
        result = self.analyzer.compare_languages(niche)

        print(f"\nEnglish: Score={result['english']['opportunity_score']}, RPM=${result['english']['rpm']}")
        print(f"Spanish: Score={result['spanish']['opportunity_score']}, RPM=${result['spanish']['rpm']}")
        print(f"Recommendation: {result['recommendation'].upper()}")

        return result

    def produce(self, topic: Optional[str] = None, niche: str = "facts_curiosities",
                language: str = "en", is_short: bool = False,
                upload: bool = False) -> dict:
        """Full production pipeline: script -> audio -> video -> (optional) upload."""
        print(f"\n=== PRODUCING {'SHORT' if is_short else 'VIDEO'} ===")

        # Step 1: Get topic if not provided
        if not topic:
            print("[Pipeline] Finding best topic...")
            analysis = self.analyzer.analyze_niche(niche, language)
            topics = analysis.get("recommended_topics", [])
            if topics:
                topic = topics[0].split(": ", 1)[-1] if ": " in topics[0] else topics[0]
            else:
                niche_data = NICHES.get(niche, {})
                keywords = niche_data.get(f"keywords_{language}", niche_data.get("keywords_en", ["interesting facts"]))
                topic = keywords[0]
            print(f"[Pipeline] Selected topic: {topic}")

        # Step 2: Generate script
        print("[Pipeline] Writing script...")
        niche_data = NICHES.get(niche, {})

        if is_short:
            hooks = niche_data.get("shorts_hooks", [])
            hook = hooks[0] if hooks else None
            script = self.script_writer.write_short_script(topic, niche, language, hook)
        else:
            target_duration = niche_data.get("target_duration", 480)
            style = niche_data.get("content_style", "educational_listicle")
            script = self.script_writer.write_long_script(
                topic, niche, language, target_duration, style
            )

        if script.get("parse_error"):
            print("[Pipeline] Warning: Script parsing had issues, using raw output")

        # Save script
        script_id = hashlib.md5(f"{topic}{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        script_path = SCRIPTS_DIR / f"script_{script_id}.json"
        script_path.write_text(json.dumps(script, indent=2))
        print(f"[Pipeline] Script saved: {script_path}")

        # Step 3: Generate audio
        print("[Pipeline] Generating audio...")
        narration = self.script_writer.get_full_narration(script)
        audio_path = self.tts.generate_audio(narration, language, f"audio_{script_id}.mp3")

        if not audio_path:
            print("[Pipeline] Audio generation failed!")
            return {"error": "Audio generation failed", "script": script}

        # Step 4: Generate subtitles
        print("[Pipeline] Generating subtitles...")
        sub_path = self.subtitles.generate_srt(narration, f"subs_{script_id}.srt")

        # Step 5: Generate images/thumbnail
        print("[Pipeline] Creating visuals...")
        visual_prompts = self._extract_visual_prompts(script, topic)
        images = self.thumbnails.generate_content_images(visual_prompts, niche, count=5)
        thumbnail_path = self.thumbnails.create_thumbnail(
            script.get("title", topic), niche,
            output_filename=f"thumb_{script_id}.png"
        )

        # Step 6: Assemble video
        print("[Pipeline] Assembling video...")
        video_filename = f"{'short' if is_short else 'video'}_{script_id}.mp4"

        if is_short:
            video_path = self.assembler.assemble_short(audio_path, images, sub_path, video_filename)
        else:
            video_path = self.assembler.assemble_long_video(audio_path, images, sub_path, video_filename)

        if not video_path:
            print("[Pipeline] Video assembly failed!")
            return {"error": "Video assembly failed", "script": script, "audio": str(audio_path)}

        result = {
            "script": script,
            "audio": str(audio_path),
            "video": str(video_path),
            "thumbnail": str(thumbnail_path) if thumbnail_path else None,
            "subtitles": str(sub_path) if sub_path else None,
            "topic": topic,
            "niche": niche,
            "language": language,
            "is_short": is_short
        }

        # Step 7: Upload (optional)
        if upload:
            result["upload"] = self._upload(result)

        print(f"\n[Pipeline] Production complete!")
        print(f"  Video: {video_path}")
        print(f"  Title: {script.get('title', 'N/A')}")

        return result

    def run(self, niche: Optional[str] = None, language: str = "en",
            upload: bool = True) -> dict:
        """Full automated run: analyze -> produce -> upload."""
        print("\n========================================")
        print("  YOUTUBE AUTOMATION - FULL RUN")
        print("========================================\n")

        # Find best opportunity
        if not niche:
            analysis = self.analyze(language)
            if "error" in analysis:
                return analysis
            niche = analysis["best_niche"]["niche"]

        results = {"niche": niche, "language": language, "videos": []}

        # Produce long video
        print("\n--- Producing long video ---")
        long_result = self.produce(niche=niche, language=language,
                                    is_short=False, upload=upload)
        results["videos"].append(long_result)

        # Produce Shorts
        from config.settings import DAILY_SHORTS
        for i in range(DAILY_SHORTS):
            print(f"\n--- Producing Short {i+1}/{DAILY_SHORTS} ---")
            short_result = self.produce(niche=niche, language=language,
                                         is_short=True, upload=upload)
            results["videos"].append(short_result)

        print("\n========================================")
        print(f"  RUN COMPLETE: {len(results['videos'])} videos")
        print("========================================")

        return results

    def report(self) -> dict:
        """Generate and display performance report."""
        report = self.tracker.generate_report()

        print("\n=== PERFORMANCE REPORT ===")
        print(f"Total videos: {report['total_videos']}")
        print(f"Total views: {report['total_views']:,}")
        print(f"Avg views/video: {report['avg_views_per_video']:,}")
        print(f"Best niche: {report['best_niche']}")

        if report["recommendations"]:
            print("\nRecommendations:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

        return report

    def _upload(self, production: dict) -> dict:
        """Handle video upload and metadata."""
        script = production["script"]
        video_path = Path(production["video"])

        # Optimize SEO
        optimized = self.seo.optimize_metadata(
            script.get("title", ""),
            script.get("description", ""),
            script.get("tags", []),
            production["niche"],
            production["language"]
        )

        # Upload
        video_id = self.uploader.upload_video(
            video_path=video_path,
            title=optimized.get("title", script.get("title", "Video")),
            description=optimized.get("description", ""),
            tags=optimized.get("tags", []),
            is_short=production.get("is_short", False)
        )

        if video_id:
            # Set thumbnail
            if production.get("thumbnail"):
                self.uploader.set_thumbnail(video_id, Path(production["thumbnail"]))

            # Track
            self.tracker.record_upload(
                video_id=video_id,
                title=optimized.get("title", ""),
                niche=production["niche"],
                language=production["language"],
                is_short=production.get("is_short", False),
                metadata=optimized
            )

            return {"video_id": video_id, "url": f"https://youtube.com/watch?v={video_id}"}

        return {"error": "Upload failed"}

    def _extract_visual_prompts(self, script: dict, fallback_topic: str) -> list[str]:
        """Extract visual prompts from script for image generation."""
        prompts = []

        if script.get("sections"):
            for section in script["sections"]:
                visual = section.get("visual_notes", "")
                if visual:
                    prompts.append(visual)
                else:
                    prompts.append(section.get("title", fallback_topic))
        elif script.get("visual_notes"):
            prompts.append(script["visual_notes"])

        if not prompts:
            prompts = [fallback_topic] * 3

        return prompts[:8]
