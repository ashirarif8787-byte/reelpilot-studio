"""
Official TikTok Content Posting API Uploader.
Implements the official Direct Post API v2 workflow:
1. Video publish initialization (`/v2/post/publish/video/init/`)
2. Binary chunk upload (`PUT` to upload_url with byte-range)
3. Status verification (`/v2/post/publish/status/fetch/`)
4. Detects expired/revoked access tokens and raises TokenExpiredException.
"""
import os
import time
import requests
from typing import Tuple, Optional, Dict, Any
from app.config import config_manager
from app.modules.uploaders.base_uploader import BaseUploader, TokenExpiredException
from app.utils.logger import logger

TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"


class TikTokUploader(BaseUploader):
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or config_manager.config.tiktok_access_token

    def _refresh_config(self):
        self.access_token = config_manager.config.tiktok_access_token

    def validate_credentials(self) -> Tuple[bool, str]:
        self._refresh_config()
        if not self.access_token:
            return False, "Missing TikTok Access Token in Settings."

        url = f"{TIKTOK_API_BASE}/user/info/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"fields": "open_id,union_id,avatar_url,display_name"}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            data = resp.json()
            if data.get("error", {}).get("code") != "ok" and data.get("error", {}).get("code") != 0:
                err = data.get("error", {})
                if "token" in err.get("message", "").lower() or resp.status_code == 401:
                    return False, f"Token Expired: {err.get('message')}"
                return False, f"TikTok API error: {err.get('message')}"
            user_data = data.get("data", {}).get("user", {})
            return True, f"Connected to TikTok user: {user_data.get('display_name', 'Verified User')}"
        except Exception as e:
            return False, f"Connection error: {e}"

    def upload_reel(
        self,
        video_path: str,
        caption: str,
        hashtags: str
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Uploads a video to TikTok via the official Content Posting API.
        """
        self._refresh_config()
        if not self.access_token:
            msg = "TikTok Access Token is missing in Settings."
            logger.error(f"[TikTokUploader] {msg}")
            return False, None, None, msg

        if not os.path.exists(video_path):
            return False, None, None, f"Video file not found: {video_path}"

        # Only explicitly simulated if in pure demo mode
        if self.access_token == "TIKTOK_DEMO_TOKEN_ACTIVE":
            logger.info(f"[TikTokUploader] [DEMO MODE] Simulating TikTok Direct Post...")
            time.sleep(1.5)
            mock_id = f"739{int(time.time())}"
            mock_url = f"https://www.tiktok.com/@reel_master_pro/video/{mock_id}"
            logger.info(f"🚀 [TikTokUploader] [DEMO MODE] TikTok post published! URL: {mock_url}")
            return True, mock_id, mock_url, None

        file_size = os.path.getsize(video_path)
        full_title = f"{caption} {hashtags}".strip()[:150]  # TikTok title limit

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }

        try:
            # Step 1: Initialize Direct Post
            logger.info(f"[TikTokUploader] Initializing direct post for {os.path.basename(video_path)} ({file_size} bytes)...")
            init_url = f"{TIKTOK_API_BASE}/post/publish/video/init/"
            payload = {
                "post_info": {
                    "title": full_title,
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_stitch": False,
                    "disable_comment": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": file_size,
                    "chunk_size": file_size,
                    "total_chunk_count": 1
                }
            }

            resp = requests.post(init_url, headers=headers, json=payload, timeout=20)
            self._check_for_token_expiration(resp)
            data = resp.json()

            if data.get("error", {}).get("code") != "ok":
                err_msg = data.get("error", {}).get("message", resp.text)
                logger.error(f"[TikTokUploader] Init error: {err_msg}")
                return False, None, None, f"Init error: {err_msg}"

            publish_id = data.get("data", {}).get("publish_id")
            upload_url = data.get("data", {}).get("upload_url")

            if not upload_url:
                return False, None, None, "No upload_url received from TikTok API."

            logger.info(f"[TikTokUploader] Received publish_id: {publish_id}. Uploading binary...")

            # Step 2: Upload Video Chunk
            upload_headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
            }
            with open(video_path, "rb") as f:
                up_resp = requests.put(upload_url, headers=upload_headers, data=f, timeout=120)

            if up_resp.status_code not in [200, 201, 204]:
                logger.error(f"[TikTokUploader] Binary upload failed: HTTP {up_resp.status_code} - {up_resp.text}")
                return False, None, None, f"Binary upload failed: {up_resp.status_code}"

            logger.info("[TikTokUploader] Video uploaded. Checking publish status...")

            # Step 3: Check Publish Status
            if not self._poll_publish_status(publish_id):
                return False, None, None, "TikTok publish processing timed out or failed."

            remote_url = f"https://www.tiktok.com/@me"
            logger.info(f"🚀 [TikTokUploader] Successfully posted to TikTok! Publish ID: {publish_id}")
            return True, publish_id, remote_url, None

        except TokenExpiredException as te:
            logger.critical(f"[TikTokUploader] TOKEN EXPIRED! Pausing queue. Reason: {te}")
            raise
        except Exception as e:
            logger.error(f"[TikTokUploader] Unexpected error during TikTok upload: {e}")
            return False, None, None, str(e)

    def _poll_publish_status(self, publish_id: str, max_retries: int = 12, delay: int = 5) -> bool:
        """Polls TikTok publish status."""
        status_url = f"{TIKTOK_API_BASE}/post/publish/status/fetch/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {"publish_id": publish_id}

        for attempt in range(max_retries):
            try:
                resp = requests.post(status_url, headers=headers, json=payload, timeout=10)
                self._check_for_token_expiration(resp)
                data = resp.json()

                status = data.get("data", {}).get("status", "")
                logger.info(f"[TikTokUploader] Publish {publish_id} status: {status} (attempt {attempt+1}/{max_retries})")

                if status in ["PUBLISH_COMPLETE", "SUCCESS"]:
                    return True
                elif status in ["FAILED", "REJECTED"]:
                    err = data.get("data", {}).get("fail_reason", "Unknown failure")
                    logger.error(f"[TikTokUploader] Post failed: {err}")
                    return False
            except TokenExpiredException:
                raise
            except Exception as e:
                logger.warning(f"[TikTokUploader] Polling warning: {e}")

            time.sleep(delay)
        return False

    def _check_for_token_expiration(self, resp: requests.Response):
        if resp.status_code == 401:
            raise TokenExpiredException("TikTok token expired (HTTP 401 Unauthorized)")
        try:
            data = resp.json()
            err_code = data.get("error", {}).get("code", "")
            err_msg = data.get("error", {}).get("message", "")
            if "access_token" in err_code or "expired" in err_msg.lower() or "invalid_token" in err_code:
                raise TokenExpiredException(f"TikTok token invalid or expired: {err_msg} ({err_code})")
        except Exception:
            pass
