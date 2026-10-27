"""
Official Meta Graph API Uploader for Instagram Reels & Facebook Pages.
Implements official container creation, resumable binary chunk upload,
status polling, and final publication, along with token-expiration detection.
"""
import os
import time
import requests
from typing import Tuple, Optional, Dict, Any
from app.config import config_manager
from app.modules.uploaders.base_uploader import BaseUploader, TokenExpiredException
from app.utils.logger import logger

GRAPH_API_VERSION = "v19.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
RUP_LOAD_BASE = f"https://rupload.facebook.com/ig-video-upload"


class MetaUploader(BaseUploader):
    def __init__(
        self,
        access_token: Optional[str] = None,
        instagram_account_id: Optional[str] = None,
        facebook_page_id: Optional[str] = None
    ):
        self.access_token = access_token or config_manager.config.meta_access_token
        self.ig_account_id = instagram_account_id or config_manager.config.instagram_account_id
        self.fb_page_id = facebook_page_id or config_manager.config.facebook_page_id

    def _refresh_config(self):
        self.access_token = config_manager.config.meta_access_token
        self.ig_account_id = config_manager.config.instagram_account_id
        self.fb_page_id = config_manager.config.facebook_page_id

    def validate_credentials(self) -> Tuple[bool, str]:
        self._refresh_config()
        if not self.access_token or not self.ig_account_id:
            return False, "Missing Meta Access Token or Instagram Account ID."

        url = f"{GRAPH_API_BASE}/me"
        params = {"access_token": self.access_token}
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if "error" in data:
                err = data["error"]
                if err.get("code") in [190, 463, 467]:
                    return False, f"Token Expired or Invalid: {err.get('message')}"
                return False, f"Meta API Error: {err.get('message')}"
            return True, f"Connected to Meta Graph API (User/Page ID: {data.get('id', 'Unknown')})"
        except Exception as e:
            return False, f"Connection failed: {e}"

    def upload_reel(
        self,
        video_path: str,
        caption: str,
        hashtags: str
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Uploads an Instagram Reel via official Meta Graph API:
        1. Initialize resumable upload session on Instagram Media Container
        2. Transfer video binary bytes
        3. Poll status until container is FINISHED
        4. Publish the container
        """
        self._refresh_config()
        if not self.access_token or not self.ig_account_id:
            msg = "Meta Access Token or Instagram Account ID is missing in Settings."
            logger.error(f"[MetaUploader] {msg}")
            return False, None, None, msg

        if not os.path.exists(video_path):
            return False, None, None, f"Video file not found: {video_path}"

        # Only explicitly simulated if in pure demo mode
        if self.access_token == "EAAB_DEMO_TOKEN_ACTIVE":
            logger.info(f"[MetaUploader] [DEMO MODE] Simulating Instagram Reel upload...")
            time.sleep(1.5)
            mock_id = f"180{int(time.time())}"
            mock_url = f"https://www.instagram.com/reel/{mock_id}/"
            logger.info(f"🚀 [MetaUploader] [DEMO MODE] Reel published! URL: {mock_url}")
            return True, mock_id, mock_url, None

        full_caption = f"{caption}\n\n{hashtags}".strip()
        file_size = os.path.getsize(video_path)

        try:
            # Step 1: Initialize Resumable Media Container
            logger.info(f"[MetaUploader] Initializing Instagram Reel container for {os.path.basename(video_path)} ({file_size} bytes)...")
            init_url = f"{GRAPH_API_BASE}/{self.ig_account_id}/media"
            init_payload = {
                "media_type": "REELS",
                "upload_type": "resumable",
                "caption": full_caption,
                "share_to_feed": "true",
                "access_token": self.access_token
            }

            resp = requests.post(init_url, data=init_payload, timeout=20)
            init_data = resp.json()
            self._check_for_token_expiration(init_data)

            if "id" not in init_data or "uri" not in init_data:
                err_msg = init_data.get("error", {}).get("message", resp.text)
                logger.error(f"[MetaUploader] Container creation failed: {err_msg}")
                return False, None, None, f"Container creation failed: {err_msg}"

            container_id = init_data["id"]
            upload_uri = init_data["uri"]
            logger.info(f"[MetaUploader] Created container ID: {container_id}. Uploading binary chunks...")

            # Step 2: Upload Video Binary Chunks
            headers = {
                "Authorization": f"OAuth {self.access_token}",
                "offset": "0",
                "file_size": str(file_size)
            }
            with open(video_path, "rb") as f:
                upload_resp = requests.post(upload_uri, headers=headers, data=f, timeout=120)

            upload_data = upload_resp.json()
            self._check_for_token_expiration(upload_data)

            if not upload_data.get("success", False) and "id" not in upload_data:
                logger.warning(f"[MetaUploader] Resumable upload response: {upload_resp.text}")

            # Step 3: Poll Container Processing Status
            logger.info(f"[MetaUploader] Waiting for Instagram to process Reel (Container {container_id})...")
            if not self._poll_container_status(container_id):
                return False, None, None, "Instagram video processing timed out or failed."

            # Step 4: Publish Media Container
            logger.info(f"[MetaUploader] Publishing Reel {container_id}...")
            publish_url = f"{GRAPH_API_BASE}/{self.ig_account_id}/media_publish"
            publish_payload = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            pub_resp = requests.post(publish_url, data=publish_payload, timeout=30)
            pub_data = pub_resp.json()
            self._check_for_token_expiration(pub_data)

            if "id" in pub_data:
                published_id = pub_data["id"]
                remote_url = f"https://www.instagram.com/p/{published_id}/"
                logger.info(f"🚀 [MetaUploader] Successfully published Instagram Reel! ID: {published_id}")
                return True, published_id, remote_url, None
            else:
                err = pub_data.get("error", {}).get("message", pub_resp.text)
                return False, None, None, f"Publish failed: {err}"

        except TokenExpiredException as te:
            logger.critical(f"[MetaUploader] TOKEN EXPIRED! Pausing queue. Reason: {te}")
            raise
        except Exception as e:
            logger.error(f"[MetaUploader] Unexpected error during upload: {e}")
            return False, None, None, str(e)

    def upload_facebook_video(
        self,
        video_path: str,
        caption: str,
        hashtags: str
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """Uploads a Reel / Video directly to a Facebook Page."""
        self._refresh_config()
        if not self.access_token or not self.fb_page_id:
            msg = "Meta Access Token or Facebook Page ID is missing in Settings."
            logger.error(f"[MetaUploader] {msg}")
            return False, None, None, msg

        if not os.path.exists(video_path):
            return False, None, None, f"Video file not found: {video_path}"

        # Only explicitly simulated if in pure demo mode
        if self.access_token == "EAAB_DEMO_TOKEN_ACTIVE":
            logger.info(f"[MetaUploader] [DEMO MODE] Simulating Facebook Page video upload...")
            time.sleep(1.5)
            mock_id = f"109{int(time.time())}"
            mock_url = f"https://www.facebook.com/watch/?v={mock_id}"
            logger.info(f"🚀 [MetaUploader] [DEMO MODE] Facebook video published! URL: {mock_url}")
            return True, mock_id, mock_url, None

        full_description = f"{caption}\n\n{hashtags}".strip()
        file_size = os.path.getsize(video_path)

        try:
            logger.info(f"[MetaUploader] Uploading Facebook Page video ({file_size} bytes)...")
            url = f"{GRAPH_API_BASE}/{self.fb_page_id}/videos"
            payload = {
                "description": full_description,
                "access_token": self.access_token
            }
            with open(video_path, "rb") as f:
                resp = requests.post(url, data=payload, files={"source": f}, timeout=180)
            data = resp.json()
            self._check_for_token_expiration(data)

            if "id" in data:
                fb_vid_id = data["id"]
                fb_url = f"https://www.facebook.com/watch/?v={fb_vid_id}"
                logger.info(f"🚀 [MetaUploader] Facebook Video Published! ID: {fb_vid_id}")
                return True, fb_vid_id, fb_url, None
            else:
                err = data.get("error", {}).get("message", resp.text)
                return False, None, None, f"Facebook publish error: {err}"
        except Exception as e:
            return False, None, None, str(e)

    def _poll_container_status(self, container_id: str, max_retries: int = 15, delay: int = 6) -> bool:
        """Polls container status until FINISHED, ERROR, or timeout."""
        status_url = f"{GRAPH_API_BASE}/{container_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token
        }

        for attempt in range(max_retries):
            try:
                resp = requests.get(status_url, params=params, timeout=10)
                data = resp.json()
                self._check_for_token_expiration(data)

                status_code = data.get("status_code", "").upper()
                logger.info(f"[MetaUploader] Container {container_id} status: {status_code} (attempt {attempt+1}/{max_retries})")

                if status_code == "FINISHED":
                    return True
                elif status_code in ["ERROR", "EXPIRED"]:
                    logger.error(f"[MetaUploader] Container status error: {data}")
                    return False
            except TokenExpiredException:
                raise
            except Exception as e:
                logger.warning(f"[MetaUploader] Polling request warning: {e}")

            time.sleep(delay)
        return False

    def _check_for_token_expiration(self, data: Dict[str, Any]):
        """Detects OAuth token expiration codes and raises TokenExpiredException."""
        if "error" in data:
            error = data["error"]
            code = error.get("code")
            subcode = error.get("error_subcode")
            message = error.get("message", "")
            if code in [190, 463, 467] or "access token" in message.lower() or "session has expired" in message.lower():
                raise TokenExpiredException(f"Meta Access Token expired or revoked: {message} (Code: {code}, Subcode: {subcode})")
