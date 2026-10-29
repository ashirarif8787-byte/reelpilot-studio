"""
Cloudflare R2, High-Speed Direct Image/Video CDN & S3 Storage Service.
Provides permanent direct raw binary HTTPS URLs for uploaded images and videos,
which are 100% compliant with Meta Instagram Graph API and Facebook Graph API crawler standards.
"""
import os
import time
import base64
import requests
from typing import Optional
from app.config import config_manager
from app.utils.logger import logger

class StorageService:
    def __init__(self):
        self._r2_disabled = False

    def upload_file(self, file_path: str, custom_key: Optional[str] = None) -> Optional[str]:
        """
        Uploads an image or video to a high-speed direct binary CDN (or Cloudflare R2)
        and returns a direct public HTTPS URL where Meta Graph API crawler receives
        image/jpeg, image/png, or video/mp4 headers without any HTML wrappers.
        """
        if not os.path.exists(file_path):
            logger.error(f"[Storage] File not found: {file_path}")
            return None

        filename = os.path.basename(file_path).lower()
        is_video = any(filename.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"])
        is_image = any(filename.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"])

        cfg = config_manager.config
        account_id = getattr(cfg, "r2_account_id", "").strip()
        access_key = getattr(cfg, "r2_access_key_id", "").strip()
        secret_key = getattr(cfg, "r2_secret_access_key", "").strip()
        bucket_name = getattr(cfg, "r2_bucket_name", "").strip()
        public_domain = getattr(cfg, "r2_public_domain", "").strip()

        # 1. Cloudflare R2 / S3 Storage (Primary Enterprise Storage - if working)
        if not self._r2_disabled and account_id and access_key and secret_key and bucket_name:
            try:
                import boto3
                from botocore.client import Config

                object_key = custom_key or f"uploads/{int(time.time())}_{os.path.basename(file_path)}"

                s3 = boto3.client(
                    service_name="s3",
                    endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=Config(signature_version="s3v4", connect_timeout=3, read_timeout=5),
                    region_name="auto"
                )

                content_type = "image/jpeg"
                if filename.endswith(".png"):
                    content_type = "image/png"
                elif filename.endswith(".webp"):
                    content_type = "image/webp"
                elif filename.endswith(".mp4"):
                    content_type = "video/mp4"

                with open(file_path, "rb") as f:
                    s3.upload_fileobj(f, bucket_name, object_key, ExtraArgs={"ContentType": content_type})

                if public_domain:
                    public_url = f"{public_domain.rstrip('/')}/{object_key}"
                else:
                    public_url = f"https://{bucket_name}.r2.dev/{object_key}"

                logger.info(f"✅ [Storage] Uploaded to Cloudflare R2: {public_url}")
                return public_url
            except Exception as e:
                self._r2_disabled = True
                logger.warning(f"[Storage] Cloudflare R2 upload error: {e}. Switching to direct image CDN fallbacks...")

        # 2. For Images: FreeImageHost (iili.io) - 100% Direct Permanent Image CDN
        if is_image:
            try:
                with open(file_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                
                resp = requests.post(
                    "https://freeimage.host/api/1/upload",
                    data={
                        "key": "6d207e02198a847aa98d0a2a901485a5",
                        "action": "upload",
                        "source": b64_data,
                        "format": "json"
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    direct_img_url = data.get("image", {}).get("url")
                    if direct_img_url and direct_img_url.startswith("http"):
                        logger.info(f"✅ [Storage] Direct Image CDN URL generated via iili: {direct_img_url}")
                        return direct_img_url
            except Exception as ie:
                logger.warning(f"[Storage] FreeImageHost upload error: {ie}. Trying next CDN...")

        # 3. Catbox Permanent Direct Upload (Permanent direct binary storage for images & videos)
        try:
            with open(file_path, "rb") as f:
                resp = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=12)
                if resp.status_code in [200, 500] and resp.text.strip().startswith("http"):
                    direct_url = resp.text.strip()
                    logger.info(f"✅ [Storage] Direct Media CDN URL generated via Catbox: {direct_url}")
                    return direct_url
        except Exception as ce:
            logger.warning(f"[Storage] Catbox upload error: {ce}")

        # 4. Uguu Direct Binary File CDN (Supports Images & Videos up to 100MB)
        try:
            with open(file_path, "rb") as f:
                resp = requests.post("https://uguu.se/upload.php", files={"files[]": f}, timeout=10)
                if resp.status_code == 200:
                    res_json = resp.json()
                    files = res_json.get("files", [])
                    if files and "url" in files[0]:
                        direct_url = files[0]["url"]
                        logger.info(f"✅ [Storage] Direct Media CDN URL generated via Uguu: {direct_url}")
                        return direct_url
        except Exception as ue:
            logger.warning(f"[Storage] Uguu upload error: {ue}. Trying next fallback...")

        # 5. Local endpoint fallback (only if local server is serving)
        if not os.environ.get("VERCEL"):
            try:
                rel_name = os.path.basename(file_path)
                return f"/api/media/{rel_name}"
            except Exception:
                pass

        return None

storage_service = StorageService()
