"""
Cloudflare R2 and S3-Compatible Object Storage Service.
Provides permanent public HTTPS URLs for uploaded images and videos,
which are required by Instagram Graph API and multi-platform publishing.
Also includes seamless fallback to direct public hosting if R2 credentials are not set.
"""
import os
import time
import requests
from typing import Optional
from app.config import config_manager
from app.utils.logger import logger

class StorageService:
    def __init__(self):
        pass

    def upload_file(self, file_path: str, custom_key: Optional[str] = None) -> Optional[str]:
        """
        Uploads a file to Cloudflare R2 (or fallback storage) and returns its public HTTPS URL.
        """
        if not os.path.exists(file_path):
            logger.error(f"[Storage] File not found: {file_path}")
            return None

        cfg = config_manager.config
        account_id = getattr(cfg, "r2_account_id", "").strip()
        access_key = getattr(cfg, "r2_access_key_id", "").strip()
        secret_key = getattr(cfg, "r2_secret_access_key", "").strip()
        bucket_name = getattr(cfg, "r2_bucket_name", "").strip()
        public_domain = getattr(cfg, "r2_public_domain", "").strip()

        # 1. Cloudflare R2 / S3 Storage (Primary)
        if account_id and access_key and secret_key and bucket_name:
            try:
                import boto3
                from botocore.client import Config

                filename = os.path.basename(file_path)
                object_key = custom_key or f"uploads/{int(time.time())}_{filename}"

                s3 = boto3.client(
                    service_name="s3",
                    endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=Config(signature_version="s3v4"),
                    region_name="auto"
                )

                content_type = "image/jpeg"
                if filename.lower().endswith(".png"):
                    content_type = "image/png"
                elif filename.lower().endswith(".webp"):
                    content_type = "image/webp"
                elif filename.lower().endswith(".mp4"):
                    content_type = "video/mp4"

                with open(file_path, "rb") as f:
                    s3.upload_fileobj(f, bucket_name, object_key, ExtraArgs={"ContentType": content_type})

                if public_domain:
                    public_url = f"{public_domain.rstrip('/')}/{object_key}"
                else:
                    public_url = f"https://{bucket_name}.r2.dev/{object_key}"

                logger.info(f"🚀 [Storage] Uploaded to Cloudflare R2: {public_url}")
                return public_url
            except Exception as e:
                logger.warning(f"[Storage] Cloudflare R2 upload error: {e}. Trying fallback...")

        # 2. Instant Free Fallback Hosting (for Instagram Graph API public URL requirement)
        try:
            with open(file_path, "rb") as f:
                resp = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_url = data.get("data", {}).get("url", "")
                    if raw_url:
                        direct_url = raw_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
                        logger.info(f"🚀 [Storage] Public image URL generated via storage fallback: {direct_url}")
                        return direct_url
        except Exception as fe:
            logger.warning(f"[Storage] Fallback upload error: {fe}")

        return None

storage_service = StorageService()
