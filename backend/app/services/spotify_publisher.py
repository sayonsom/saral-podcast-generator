"""Spotify for Podcasters integration.

NOTE: As of 2024, Spotify for Podcasters does not have a full public API
for uploading episodes. The recommended approach is:
1. Use RSS feed for automatic distribution
2. Use Spotify's web interface for direct uploads
3. Use third-party podcast hosts (Anchor, Buzzsprout, etc.) with Spotify integration

This service provides:
- OAuth flow for user authentication
- Metadata preparation in Spotify-compatible format
- RSS feed generation as alternative distribution method
- Manual upload helper (prepares files + metadata)
"""
import json
from dataclasses import dataclass
from datetime import datetime
import httpx

from app.config import settings


@dataclass
class SpotifyCredentials:
    access_token: str
    refresh_token: str
    expires_at: datetime


class SpotifyPublisher:
    """
    Spotify for Podcasters integration.
    
    Primary method: RSS feed distribution
    Alternative: Prepare files for manual upload
    """

    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.redirect_uri = settings.spotify_redirect_uri
        self.show_id = settings.spotify_show_id

    def get_auth_url(self, state: str = "") -> str:
        """Get OAuth authorization URL for Spotify."""
        scopes = [
            "user-read-private",
            "user-read-email",
        ]
        
        return (
            "https://accounts.spotify.com/authorize?"
            f"client_id={self.client_id}&"
            "response_type=code&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope={' '.join(scopes)}&"
            f"state={state}"
        )

    async def exchange_code(self, code: str) -> SpotifyCredentials:
        """Exchange authorization code for access tokens."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                auth=(self.client_id, self.client_secret),
            )
            resp.raise_for_status()
            data = resp.json()
            
            return SpotifyCredentials(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=datetime.utcnow() + timedelta(seconds=data["expires_in"])
            )

    async def refresh_token(self, refresh_token: str) -> SpotifyCredentials:
        """Refresh expired access token."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                auth=(self.client_id, self.client_secret),
            )
            resp.raise_for_status()
            data = resp.json()
            
            return SpotifyCredentials(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token", refresh_token),
                expires_at=datetime.utcnow() + timedelta(seconds=data["expires_in"])
            )

    def prepare_episode_metadata(
        self,
        title: str,
        description: str,
        keywords: list[str],
        chapters: list[dict],
        duration_seconds: int,
        explicit: bool = False
    ) -> dict:
        """
        Prepare episode metadata in Spotify-compatible format.
        
        Returns dict ready for RSS feed or manual upload.
        """
        return {
            "title": title,
            "description": description,
            "keywords": keywords,
            "duration": duration_seconds,
            "explicit": explicit,
            "chapters": [
                {
                    "title": ch["title"],
                    "start_time_ms": self._parse_timestamp(ch["start_time"]) * 1000
                }
                for ch in chapters
            ],
            "publication_date": datetime.utcnow().isoformat(),
            
            # Spotify-specific formatting
            "spotify_description": self._format_spotify_description(description, chapters),
        }

    def _parse_timestamp(self, timestamp: str) -> int:
        """Parse HH:MM:SS to seconds."""
        parts = timestamp.split(":")
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = map(int, parts)
            return m * 60 + s
        return int(parts[0])

    def _format_spotify_description(
        self,
        description: str,
        chapters: list[dict]
    ) -> str:
        """Format description with timestamps for Spotify."""
        lines = [description, "", "TIMESTAMPS:"]
        
        for ch in chapters:
            lines.append(f"{ch['start_time']} - {ch['title']}")
        
        lines.extend([
            "",
            "---",
            "Based on Dr. Cheyenne's analysis at askespresso.com",
            "",
            "Follow us on Spotify for new episodes!",
        ])
        
        return "\n".join(lines)

    def generate_rss_item(
        self,
        metadata: dict,
        audio_url: str,
        thumbnail_url: str,
        guid: str
    ) -> str:
        """
        Generate RSS feed item for episode.
        
        This can be added to your podcast RSS feed for automatic
        distribution to Spotify and other platforms.
        """
        # Escape XML special characters
        def escape(s):
            return (s
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
        
        duration_str = self._format_duration(metadata["duration"])
        
        return f"""
    <item>
        <title>{escape(metadata['title'])}</title>
        <description><![CDATA[{metadata['spotify_description']}]]></description>
        <enclosure url="{audio_url}" type="audio/mpeg" length="0"/>
        <guid isPermaLink="false">{guid}</guid>
        <pubDate>{metadata['publication_date']}</pubDate>
        <itunes:duration>{duration_str}</itunes:duration>
        <itunes:explicit>{'yes' if metadata['explicit'] else 'no'}</itunes:explicit>
        <itunes:image href="{thumbnail_url}"/>
        <itunes:keywords>{','.join(metadata['keywords'])}</itunes:keywords>
    </item>
"""

    def _format_duration(self, seconds: int) -> str:
        """Format duration as HH:MM:SS."""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    async def get_upload_instructions(
        self,
        audio_path: str,
        thumbnail_path: str,
        metadata: dict
    ) -> dict:
        """
        Generate instructions for manual Spotify upload.
        
        Since Spotify for Podcasters doesn't have a public upload API,
        this prepares everything needed for manual upload.
        """
        return {
            "method": "manual_upload",
            "platform_url": "https://podcasters.spotify.com/",
            "instructions": [
                "1. Log in to Spotify for Podcasters",
                "2. Click 'New Episode'",
                "3. Upload audio file",
                "4. Upload thumbnail image",
                "5. Copy the title and description below",
                "6. Add keywords as tags",
                "7. Set publish date and click Publish"
            ],
            "files": {
                "audio": audio_path,
                "thumbnail": thumbnail_path
            },
            "metadata": {
                "title": metadata["title"],
                "description": metadata["spotify_description"],
                "keywords": metadata["keywords"],
            }
        }


# Import fix for datetime.timedelta
from datetime import timedelta
