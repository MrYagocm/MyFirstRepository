"""
Subtitle generator: creates SRT subtitles from script text.
Subtitles improve accessibility, SEO, and viewer retention.
"""

import re
from pathlib import Path
from typing import Optional

from config.settings import SUBTITLES_DIR


class SubtitleGenerator:
    """Generates SRT subtitle files from script text."""

    def __init__(self):
        self.words_per_second = 2.5  # Average speech rate

    def generate_srt(self, text: str, output_filename: Optional[str] = None,
                      start_offset: float = 0.0) -> Optional[Path]:
        """Generate an SRT subtitle file from text."""
        if not text.strip():
            return None

        if not output_filename:
            output_filename = "subtitles.srt"

        output_path = SUBTITLES_DIR / output_filename
        sentences = self._split_into_sentences(text)
        srt_entries = []
        current_time = start_offset

        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            # Split long sentences into chunks of ~8 words for readability
            chunks = self._split_into_chunks(sentence, max_words=8)

            for chunk in chunks:
                word_count = len(chunk.split())
                duration = word_count / self.words_per_second

                start = self._format_timestamp(current_time)
                end = self._format_timestamp(current_time + duration)

                srt_entries.append(f"{len(srt_entries) + 1}\n{start} --> {end}\n{chunk}\n")
                current_time += duration

        srt_content = "\n".join(srt_entries)
        output_path.write_text(srt_content, encoding="utf-8")
        return output_path

    def generate_from_sections(self, sections: list[dict],
                                output_filename: str = "subtitles.srt") -> Optional[Path]:
        """Generate SRT from script sections with proper timing."""
        all_text_parts = []
        for section in sections:
            content = section.get("content", "")
            if content:
                all_text_parts.append(content)

        full_text = " ".join(all_text_parts)
        return self.generate_srt(full_text, output_filename)

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_into_chunks(self, text: str, max_words: int = 8) -> list[str]:
        """Split text into display-friendly chunks."""
        words = text.split()
        chunks = []

        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i:i + max_words])
            chunks.append(chunk)

        return chunks

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds into SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
