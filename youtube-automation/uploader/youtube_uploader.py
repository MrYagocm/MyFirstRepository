"""
YouTube uploader: handles OAuth authentication and video uploads
using YouTube Data API v3.
"""

import json
import pickle
import time
from pathlib import Path
from typing import Optional

from config.settings import (
    YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION, YOUTUBE_SCOPES, DATA_DIR
)


class YouTubeUploader:
    """Handles YouTube video uploads with OAuth2 authentication."""

    def __init__(self):
        self.credentials_path = DATA_DIR / "youtube_credentials.pickle"
        self.service = None

    def authenticate(self) -> bool:
        """Authenticate with YouTube API using OAuth2."""
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            credentials = None

            # Load saved credentials
            if self.credentials_path.exists():
                with open(self.credentials_path, "rb") as f:
                    credentials = pickle.load(f)

            # Refresh or create new credentials
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    if not Path(YOUTUBE_CLIENT_SECRETS_FILE).exists():
                        print("[Uploader] client_secrets.json not found!")
                        print("[Uploader] Download it from Google Cloud Console:")
                        print("  1. Go to console.cloud.google.com")
                        print("  2. Create project > Enable YouTube Data API v3")
                        print("  3. Create OAuth 2.0 credentials (Desktop app)")
                        print("  4. Download JSON and save as client_secrets.json")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_SCOPES
                    )
                    credentials = flow.run_local_server(port=8090)

                # Save credentials
                with open(self.credentials_path, "wb") as f:
                    pickle.dump(credentials, f)

            self.service = build(
                YOUTUBE_API_SERVICE_NAME,
                YOUTUBE_API_VERSION,
                credentials=credentials
            )

            print("[Uploader] YouTube API authenticated successfully")
            return True

        except Exception as e:
            print(f"[Uploader] Authentication error: {e}")
            return False

    def upload_video(self, video_path: Path, title: str, description: str,
                      tags: list[str], category_id: str = "22",
                      privacy: str = "public",
                      is_short: bool = False) -> Optional[str]:
        """Upload a video to YouTube. Returns video ID on success."""
        if not self.service:
            if not self.authenticate():
                return None

        try:
            from googleapiclient.http import MediaFileUpload

            # Add #Shorts tag if it's a Short
            if is_short and "#Shorts" not in title:
                title = f"{title} #Shorts"

            body = {
                "snippet": {
                    "title": title[:100],  # YouTube limit
                    "description": description[:5000],
                    "tags": tags[:500],  # YouTube limit
                    "categoryId": category_id,
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": privacy,
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(
                str(video_path),
                mimetype="video/mp4",
                resumable=True
            )

            request = self.service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            # Execute upload with retry
            response = None
            retries = 0
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        print(f"[Uploader] Upload progress: {int(status.progress() * 100)}%")
                except Exception as e:
                    retries += 1
                    if retries > 3:
                        raise
                    print(f"[Uploader] Retry {retries}/3: {e}")
                    time.sleep(5 * retries)

            video_id = response.get("id")
            print(f"[Uploader] Video uploaded: https://youtube.com/watch?v={video_id}")
            return video_id

        except Exception as e:
            print(f"[Uploader] Upload error: {e}")
            return None

    def set_thumbnail(self, video_id: str, thumbnail_path: Path) -> bool:
        """Set custom thumbnail for an uploaded video."""
        if not self.service:
            return False

        try:
            from googleapiclient.http import MediaFileUpload

            media = MediaFileUpload(str(thumbnail_path), mimetype="image/png")
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()

            print(f"[Uploader] Thumbnail set for video {video_id}")
            return True

        except Exception as e:
            print(f"[Uploader] Thumbnail error: {e}")
            return False

    def get_video_stats(self, video_id: str) -> Optional[dict]:
        """Get statistics for an uploaded video."""
        if not self.service:
            if not self.authenticate():
                return None

        try:
            response = self.service.videos().list(
                part="statistics,snippet",
                id=video_id
            ).execute()

            if response.get("items"):
                item = response["items"][0]
                stats = item.get("statistics", {})
                return {
                    "video_id": video_id,
                    "title": item["snippet"]["title"],
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "favorites": int(stats.get("favoriteCount", 0))
                }

        except Exception as e:
            print(f"[Uploader] Stats error: {e}")

        return None
