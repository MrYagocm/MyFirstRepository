"""
Video assembler: combines images, audio, and subtitles into
finished videos (both long-form and Shorts).
"""

import random
from pathlib import Path
from typing import Optional

from config.settings import (
    VIDEOS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    SHORTS_WIDTH, SHORTS_HEIGHT, SHORTS_FPS
)


class VideoAssembler:
    """Assembles final videos from components."""

    def __init__(self):
        pass

    def assemble_long_video(self, audio_path: Path, images: list[Path],
                             subtitle_path: Optional[Path] = None,
                             output_filename: str = "video.mp4") -> Optional[Path]:
        """Assemble a long-form video from audio + images + subtitles."""
        try:
            from moviepy.editor import (
                AudioFileClip, ImageClip, CompositeVideoClip,
                concatenate_videoclips
            )

            output_path = VIDEOS_DIR / output_filename

            # Load audio
            audio = AudioFileClip(str(audio_path))
            total_duration = audio.duration

            if not images:
                print("[Assembler] No images provided, creating text-based video")
                return None

            # Create image clips distributed across the video
            image_duration = total_duration / len(images)
            clips = []

            for img_path in images:
                clip = (
                    ImageClip(str(img_path))
                    .set_duration(image_duration)
                    .resize((VIDEO_WIDTH, VIDEO_HEIGHT))
                )
                # Add subtle zoom effect (Ken Burns)
                clip = self._add_ken_burns(clip)
                clips.append(clip)

            # Concatenate all image clips
            video = concatenate_videoclips(clips, method="compose")
            video = video.set_audio(audio)

            # Add subtitles if available
            if subtitle_path and subtitle_path.exists():
                video = self._burn_subtitles(video, subtitle_path)

            # Export
            video.write_videofile(
                str(output_path),
                fps=VIDEO_FPS,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=4
            )

            # Cleanup
            audio.close()
            video.close()

            print(f"[Assembler] Long video saved: {output_path}")
            return output_path

        except Exception as e:
            print(f"[Assembler] Error: {e}")
            return None

    def assemble_short(self, audio_path: Path, images: list[Path],
                        subtitle_path: Optional[Path] = None,
                        output_filename: str = "short.mp4") -> Optional[Path]:
        """Assemble a YouTube Short (vertical, < 60 seconds)."""
        try:
            from moviepy.editor import (
                AudioFileClip, ImageClip, CompositeVideoClip,
                concatenate_videoclips
            )

            output_path = VIDEOS_DIR / output_filename

            audio = AudioFileClip(str(audio_path))
            total_duration = min(audio.duration, 59)  # Max 59 seconds

            if not images:
                return None

            image_duration = total_duration / len(images)
            clips = []

            for img_path in images:
                clip = (
                    ImageClip(str(img_path))
                    .set_duration(image_duration)
                    .resize((SHORTS_WIDTH, SHORTS_HEIGHT))
                )
                clips.append(clip)

            video = concatenate_videoclips(clips, method="compose")
            video = video.set_duration(total_duration)
            video = video.set_audio(audio.subclip(0, total_duration))

            if subtitle_path and subtitle_path.exists():
                video = self._burn_subtitles(video, subtitle_path, is_short=True)

            video.write_videofile(
                str(output_path),
                fps=SHORTS_FPS,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=4
            )

            audio.close()
            video.close()

            print(f"[Assembler] Short saved: {output_path}")
            return output_path

        except Exception as e:
            print(f"[Assembler] Error assembling short: {e}")
            return None

    def _add_ken_burns(self, clip):
        """Add subtle zoom/pan effect to an image clip."""
        try:
            duration = clip.duration
            # Random zoom direction
            zoom_in = random.choice([True, False])

            if zoom_in:
                clip = clip.resize(lambda t: 1 + 0.05 * (t / duration))
            else:
                clip = clip.resize(lambda t: 1.05 - 0.05 * (t / duration))

            return clip
        except Exception:
            return clip

    def _burn_subtitles(self, video, subtitle_path: Path, is_short: bool = False):
        """Overlay subtitles on the video."""
        try:
            from moviepy.editor import TextClip, CompositeVideoClip

            srt_content = subtitle_path.read_text(encoding="utf-8")
            subtitle_clips = self._parse_srt(srt_content)

            txt_clips = []
            for sub in subtitle_clips:
                font_size = 40 if is_short else 32
                width = SHORTS_WIDTH - 100 if is_short else VIDEO_WIDTH - 200

                txt_clip = (
                    TextClip(
                        sub["text"],
                        fontsize=font_size,
                        color="white",
                        stroke_color="black",
                        stroke_width=2,
                        font="Arial-Bold",
                        size=(width, None),
                        method="caption"
                    )
                    .set_position(("center", "bottom"))
                    .set_start(sub["start"])
                    .set_duration(sub["end"] - sub["start"])
                    .margin(bottom=80, opacity=0)
                )
                txt_clips.append(txt_clip)

            return CompositeVideoClip([video] + txt_clips)

        except Exception as e:
            print(f"[Assembler] Subtitle overlay error: {e}")
            return video

    def _parse_srt(self, srt_content: str) -> list[dict]:
        """Parse SRT content into subtitle entries."""
        entries = []
        blocks = srt_content.strip().split("\n\n")

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                timing = lines[1]
                text = " ".join(lines[2:])

                try:
                    start_str, end_str = timing.split(" --> ")
                    start = self._srt_time_to_seconds(start_str.strip())
                    end = self._srt_time_to_seconds(end_str.strip())
                    entries.append({"start": start, "end": end, "text": text})
                except (ValueError, IndexError):
                    continue

        return entries

    def _srt_time_to_seconds(self, time_str: str) -> float:
        """Convert SRT timestamp to seconds."""
        time_str = time_str.replace(",", ".")
        parts = time_str.split(":")
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
