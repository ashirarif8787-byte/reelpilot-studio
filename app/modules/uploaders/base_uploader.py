"""
Base class and common exceptions for social media official API uploaders.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional


class TokenExpiredException(Exception):
    """Raised when an API access token has expired or is invalid."""
    pass


class DailyLimitExceededException(Exception):
    """Raised when the user has reached their configured daily quota."""
    pass


class BaseUploader(ABC):
    @abstractmethod
    def upload_reel(
        self,
        video_path: str,
        caption: str,
        hashtags: str
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Uploads a video/reel to the social platform.
        Returns:
            (success: bool, remote_media_id: Optional[str], remote_url: Optional[str], error_message: Optional[str])
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> Tuple[bool, str]:
        """
        Validates whether current API credentials are present and valid.
        Returns: (is_valid: bool, status_message: str)
        """
        pass
