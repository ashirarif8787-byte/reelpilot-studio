"""
Database models and enum representations for Social Media Scheduler.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PostStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SCHEDULED = "SCHEDULED"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"


@dataclass
class PostRecord:
    id: Optional[int] = None
    file_path: str = ""
    file_hash: str = ""
    target_platform: str = Platform.INSTAGRAM.value
    media_type: str = MediaType.IMAGE.value
    processed_path: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    status: str = PostStatus.QUEUED.value
    scheduled_time: Optional[str] = None
    uploaded_at: Optional[str] = None
    remote_media_id: Optional[str] = None
    remote_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Backward compatibility alias
Post = PostRecord
