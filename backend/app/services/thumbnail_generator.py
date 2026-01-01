"""Thumbnail generator using Unsplash API + PIL."""
import httpx
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from app.config import settings


class ThumbnailGenerator:
    """
    Generate episode artwork:
    1. Search Unsplash for relevant image
    2. Add dark overlay for text readability
    3. Overlay episode title + branding
    4. Export as 3000x3000 JPEG (Spotify spec)
    """

    def __init__(self):
        self.unsplash_key = settings.unsplash_access_key
        self.size = (3000, 3000)
        self.brand_color = (234, 88, 11)  # #ea580b as RGB
        self.fallback_bg = (30, 30, 30)   # Dark gray fallback

    async def search_image(self, query: str) -> str | None:
        """Search Unsplash for relevant background image."""
        if not self.unsplash_key:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={
                        "query": query,
                        "orientation": "squarish",
                        "per_page": 5,
                        "content_filter": "high"  # Safe images only
                    },
                    headers={"Authorization": f"Client-ID {self.unsplash_key}"},
                    timeout=10.0
                )
                resp.raise_for_status()
                data = resp.json()
                
                if data["results"]:
                    # Get the largest available size
                    return data["results"][0]["urls"]["regular"]
                    
            except Exception as e:
                print(f"Unsplash search failed: {e}")
        
        return None

    async def download_image(self, url: str) -> Image.Image | None:
        """Download image from URL."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=30.0)
                resp.raise_for_status()
                return Image.open(BytesIO(resp.content))
            except Exception as e:
                print(f"Image download failed: {e}")
                return None

    def create_fallback_background(self) -> Image.Image:
        """Create solid color fallback if Unsplash fails."""
        img = Image.new('RGB', self.size, self.fallback_bg)
        
        # Add subtle gradient
        draw = ImageDraw.Draw(img)
        for y in range(self.size[1]):
            # Darker at top, lighter at bottom
            shade = int(30 + (y / self.size[1]) * 20)
            draw.line([(0, y), (self.size[0], y)], fill=(shade, shade, shade))
        
        return img

    def crop_to_square(self, img: Image.Image) -> Image.Image:
        """Center crop image to square."""
        width, height = img.size
        
        if width == height:
            return img.resize(self.size, Image.LANCZOS)
        
        # Crop to square from center
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        
        cropped = img.crop((left, top, right, bottom))
        return cropped.resize(self.size, Image.LANCZOS)

    def add_overlay(self, img: Image.Image, opacity: int = 160) -> Image.Image:
        """Add dark overlay for text readability."""
        overlay = Image.new('RGBA', self.size, (0, 0, 0, opacity))
        
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        return Image.alpha_composite(img, overlay)

    def add_text(
        self,
        img: Image.Image,
        episode_title: str,
        episode_number: int | None = None
    ) -> Image.Image:
        """Add episode title and branding text."""
        draw = ImageDraw.Draw(img)
        
        # Load fonts (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("CircularStd-Bold.ttf", 180)
            subtitle_font = ImageFont.truetype("CircularStd-Medium.ttf", 80)
            number_font = ImageFont.truetype("CircularStd-Bold.ttf", 120)
        except OSError:
            # Fallback to default
            title_font = ImageFont.load_default()
            subtitle_font = title_font
            number_font = title_font

        # "ENERGY DEBATES" at top
        brand_text = "ENERGY DEBATES"
        draw.text(
            (self.size[0] // 2, 200),
            brand_text,
            fill=self.brand_color,
            font=subtitle_font,
            anchor="mm"
        )

        # Episode number badge (if provided)
        if episode_number:
            badge_text = f"EP {episode_number:02d}"
            draw.text(
                (self.size[0] // 2, 400),
                badge_text,
                fill=(255, 255, 255),
                font=number_font,
                anchor="mm"
            )

        # Episode title (centered, wrapped if needed)
        # Simple approach: truncate long titles
        if len(episode_title) > 40:
            episode_title = episode_title[:37] + "..."
        
        draw.text(
            (self.size[0] // 2, self.size[1] // 2),
            episode_title.upper(),
            fill=(255, 255, 255),
            font=title_font,
            anchor="mm"
        )

        # "askespresso.com" at bottom
        draw.text(
            (self.size[0] // 2, self.size[1] - 200),
            "askespresso.com",
            fill=(180, 180, 180),
            font=subtitle_font,
            anchor="mm"
        )

        return img

    async def generate(
        self,
        search_terms: list[str],
        episode_title: str,
        episode_number: int | None = None
    ) -> bytes:
        """
        Generate complete episode thumbnail.
        
        Args:
            search_terms: Keywords for Unsplash search
            episode_title: Title to display on thumbnail
            episode_number: Optional episode number for badge
            
        Returns:
            JPEG image as bytes
        """
        # Try to get background from Unsplash
        query = " ".join(search_terms[:3])
        image_url = await self.search_image(query)
        
        if image_url:
            bg = await self.download_image(image_url)
            if bg:
                bg = self.crop_to_square(bg)
            else:
                bg = self.create_fallback_background()
        else:
            bg = self.create_fallback_background()
        
        # Add dark overlay
        bg = self.add_overlay(bg)
        
        # Convert back to RGB for JPEG export
        if bg.mode == 'RGBA':
            bg = bg.convert('RGB')
        
        # Add text
        final = self.add_text(bg, episode_title, episode_number)
        
        # Export as JPEG
        output = BytesIO()
        final.save(output, format="JPEG", quality=95, optimize=True)
        output.seek(0)
        
        return output.getvalue()
