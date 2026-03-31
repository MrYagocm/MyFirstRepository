"""
Multi-platform repurposer: adapts content for TikTok, Instagram Reels,
and Facebook Reels from YouTube videos.
Same content, 200% more reach, minimal extra cost.
"""

import subprocess
from pathlib import Path
from typing import Optional

from config.settings import VIDEOS_DIR, SHORTS_WIDTH, SHORTS_HEIGHT


class MultiPlatformRepurposer:
    """Adapts YouTube content for other platforms."""

    def __init__(self):
        self.output_dir = VIDEOS_DIR / "repurposed"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def repurpose_short(self, video_path: Path, platform: str = "tiktok") -> Optional[Path]:
        """Adapt a YouTube Short for another platform."""
        if not video_path.exists():
            return None

        output_name = f"{platform}_{video_path.stem}.mp4"
        output_path = self.output_dir / output_name

        if output_path.exists():
            return output_path

        try:
            if platform == "tiktok":
                return self._adapt_for_tiktok(video_path, output_path)
            elif platform == "instagram":
                return self._adapt_for_instagram(video_path, output_path)
            elif platform == "facebook":
                return self._adapt_for_facebook(video_path, output_path)
        except Exception as e:
            print(f"[Repurpose] Error for {platform}: {e}")

        return None

    def repurpose_long_to_clips(self, video_path: Path, clip_timestamps: list[tuple],
                                  max_clips: int = 5) -> list[Path]:
        """Extract short clips from long-form video for Shorts/Reels/TikTok."""
        clips = []

        for i, (start, end) in enumerate(clip_timestamps[:max_clips]):
            output_name = f"clip_{i}_{video_path.stem}.mp4"
            output_path = self.output_dir / output_name

            if output_path.exists():
                clips.append(output_path)
                continue

            try:
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(video_path),
                    "-ss", str(start),
                    "-to", str(end),
                    "-vf", f"scale={SHORTS_WIDTH}:{SHORTS_HEIGHT}:force_original_aspect_ratio=decrease,pad={SHORTS_WIDTH}:{SHORTS_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-preset", "fast",
                    str(output_path)
                ]
                subprocess.run(cmd, capture_output=True, timeout=120)
                if output_path.exists():
                    clips.append(output_path)
            except Exception as e:
                print(f"[Repurpose] Clip extraction error: {e}")

        return clips

    def _adapt_for_tiktok(self, video_path: Path, output_path: Path) -> Optional[Path]:
        """TikTok: vertical 9:16, max 3 min, fast-paced."""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-t", "180",  # Max 3 min for TikTok
            "-vf", f"scale={SHORTS_WIDTH}:{SHORTS_HEIGHT}:force_original_aspect_ratio=decrease,pad={SHORTS_WIDTH}:{SHORTS_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "128k",
            "-preset", "fast",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, timeout=120)
        return output_path if output_path.exists() else None

    def _adapt_for_instagram(self, video_path: Path, output_path: Path) -> Optional[Path]:
        """Instagram Reels: vertical 9:16, max 90 seconds."""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-t", "90",
            "-vf", f"scale={SHORTS_WIDTH}:{SHORTS_HEIGHT}:force_original_aspect_ratio=decrease,pad={SHORTS_WIDTH}:{SHORTS_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "128k",
            "-preset", "fast",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, timeout=120)
        return output_path if output_path.exists() else None

    def _adapt_for_facebook(self, video_path: Path, output_path: Path) -> Optional[Path]:
        """Facebook Reels: same as Instagram essentially."""
        return self._adapt_for_instagram(video_path, output_path)

    def repurpose_all_platforms(self, video_path: Path) -> dict:
        """Repurpose a Short for all platforms at once."""
        results = {}
        for platform in ["tiktok", "instagram", "facebook"]:
            result = self.repurpose_short(video_path, platform)
            results[platform] = str(result) if result else None
        return results
