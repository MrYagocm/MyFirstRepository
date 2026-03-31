"""
Thumbnail creator: generates eye-catching thumbnails using
Replicate/Flux for AI images + Pillow for text overlay.
High CTR thumbnails = more views = more money.
"""

import hashlib
import io
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageFont

from config.settings import (
    THUMBNAILS_DIR, REPLICATE_API_TOKEN,
    THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, REPLICATE_MODEL
)


class ThumbnailCreator:
    """Creates YouTube thumbnails optimized for CTR."""

    def __init__(self):
        self.use_replicate = bool(REPLICATE_API_TOKEN)
        self.width = THUMBNAIL_WIDTH
        self.height = THUMBNAIL_HEIGHT

    def create_thumbnail(self, title: str, niche: str,
                          style: str = "bold_text",
                          output_filename: Optional[str] = None) -> Optional[Path]:
        """Create a thumbnail for a video."""
        if not output_filename:
            title_hash = hashlib.md5(title.encode()).hexdigest()[:10]
            output_filename = f"thumb_{title_hash}.png"

        output_path = THUMBNAILS_DIR / output_filename

        if output_path.exists():
            return output_path

        # Generate background image
        bg_image = None
        if self.use_replicate:
            bg_image = self._generate_flux_image(title, niche)

        if bg_image is None:
            bg_image = self._create_gradient_background(niche)

        # Add text overlay
        final = self._add_text_overlay(bg_image, title)

        # Save
        final.save(str(output_path), "PNG", quality=95)
        print(f"[Thumbnail] Saved: {output_path}")
        return output_path

    def create_shorts_thumbnail(self, title: str, niche: str,
                                 output_filename: Optional[str] = None) -> Optional[Path]:
        """Create a vertical thumbnail for Shorts."""
        if not output_filename:
            title_hash = hashlib.md5(title.encode()).hexdigest()[:10]
            output_filename = f"short_thumb_{title_hash}.png"

        output_path = THUMBNAILS_DIR / output_filename

        # Generate background
        bg_image = None
        if self.use_replicate:
            bg_image = self._generate_flux_image(title, niche, vertical=True)

        if bg_image is None:
            bg_image = self._create_gradient_background(niche, vertical=True)

        # Add text
        final = self._add_text_overlay(bg_image, title, is_short=True)
        final.save(str(output_path), "PNG", quality=95)
        return output_path

    def generate_content_images(self, prompts: list[str], niche: str,
                                 count: int = 5) -> list[Path]:
        """Generate images for use within video content."""
        images = []
        for i, prompt in enumerate(prompts[:count]):
            filename = f"content_{hashlib.md5(prompt.encode()).hexdigest()[:8]}_{i}.png"
            filepath = THUMBNAILS_DIR / filename

            if filepath.exists():
                images.append(filepath)
                continue

            img = None
            if self.use_replicate:
                img = self._generate_flux_image(prompt, niche)

            if img is None:
                img = self._create_gradient_background(niche)

            img = img.resize((1920, 1080), Image.LANCZOS)
            img.save(str(filepath), "PNG")
            images.append(filepath)

        return images

    def _generate_flux_image(self, prompt: str, niche: str,
                              vertical: bool = False) -> Optional[Image.Image]:
        """Generate an image using Replicate's Flux model."""
        try:
            import replicate

            style_prompts = {
                "ai_tools": "futuristic digital technology, neon blue and purple, clean design",
                "finance_investing": "luxury, gold accents, wealth, professional",
                "facts_curiosities": "colorful, dramatic lighting, cinematic",
                "scary_stories": "dark, moody, horror atmosphere, fog",
                "life_hacks": "bright, clean, organized, lifestyle",
                "psychology": "mysterious, brain imagery, dark background, dramatic"
            }

            style = style_prompts.get(niche, "cinematic, high quality, dramatic lighting")
            aspect = "9:16" if vertical else "16:9"

            full_prompt = f"{prompt}, {style}, YouTube thumbnail style, ultra detailed, 4K"

            output = replicate.run(
                REPLICATE_MODEL,
                input={
                    "prompt": full_prompt,
                    "aspect_ratio": aspect,
                    "num_outputs": 1
                }
            )

            if output and len(output) > 0:
                img_url = output[0]
                if hasattr(img_url, "url"):
                    img_url = img_url.url

                response = requests.get(str(img_url), timeout=30)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                    return img

        except Exception as e:
            print(f"[Thumbnail] Flux generation error: {e}")

        return None

    def _create_gradient_background(self, niche: str, vertical: bool = False) -> Image.Image:
        """Create a gradient background as fallback."""
        w = 1080 if vertical else self.width
        h = 1920 if vertical else self.height

        color_schemes = {
            "ai_tools": [(20, 30, 80), (100, 50, 200)],
            "finance_investing": [(10, 30, 10), (50, 150, 50)],
            "facts_curiosities": [(80, 20, 20), (200, 100, 50)],
            "scary_stories": [(10, 10, 10), (50, 20, 20)],
            "life_hacks": [(20, 80, 80), (50, 200, 200)],
            "psychology": [(30, 10, 50), (100, 30, 150)]
        }

        colors = color_schemes.get(niche, [(30, 30, 30), (100, 100, 100)])
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)

        for y in range(h):
            ratio = y / h
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        return img

    def _add_text_overlay(self, image: Image.Image, title: str,
                           is_short: bool = False) -> Image.Image:
        """Add bold text overlay to thumbnail image."""
        img = image.copy()
        if not is_short:
            img = img.resize((self.width, self.height), Image.LANCZOS)

        draw = ImageDraw.Draw(img)

        # Try to use a bold font
        font_size = 60 if is_short else 72
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

        # Shorten title for thumbnail
        display_title = title[:50].upper()
        if len(title) > 50:
            display_title = display_title[:47] + "..."

        # Calculate text position (centered)
        w, h = img.size
        bbox = draw.textbbox((0, 0), display_title, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (w - text_w) // 2
        y = (h - text_h) // 2

        # Draw text with outline
        outline_color = "black"
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                draw.text((x + dx, y + dy), display_title, font=font, fill=outline_color)

        draw.text((x, y), display_title, font=font, fill="white")

        return img
