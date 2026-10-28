"""
Utility helper functions for media detection, ffprobe analysis, and formatting.
"""
import os
import json
import subprocess
from typing import Tuple, Optional
from datetime import datetime
from app.database.models import MediaType

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def detect_media_type(file_path: str) -> Optional[str]:
    """Returns 'image' or 'video' based on file extension, or None if unsupported."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return MediaType.IMAGE.value
    elif ext in VIDEO_EXTENSIONS:
        return MediaType.VIDEO.value
    return None


def run_ffprobe_json(file_path: str) -> dict:
    """Executes ffprobe to inspect streams and metadata of media file."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return json.loads(res.stdout)
    except Exception:
        return {}


def video_has_audio(file_path: str) -> bool:
    """Checks if a video file already has an active audio stream."""
    info = run_ffprobe_json(file_path)
    streams = info.get("streams", [])
    for stream in streams:
        if stream.get("codec_type") == "audio":
            return True
    return False


def get_media_duration(file_path: str) -> float:
    """Returns the duration of an audio or video file in seconds."""
    info = run_ffprobe_json(file_path)
    # Check format duration
    fmt = info.get("format", {})
    if "duration" in fmt:
        try:
            return float(fmt["duration"])
        except (ValueError, TypeError):
            pass
    # Check stream duration
    for s in info.get("streams", []):
        if "duration" in s:
            try:
                return float(s["duration"])
            except (ValueError, TypeError):
                pass
    return 0.0


def format_delay_time(dt_iso: Optional[str]) -> str:
    """Formats an ISO datetime into a friendly human-readable countdown string."""
    if not dt_iso:
        return "Not scheduled"
    try:
        raw_str = str(dt_iso).strip()
        from datetime import timezone
        if raw_str.endswith("Z"):
            target = datetime.fromisoformat(raw_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
        else:
            clean = raw_str.split(".")[0]
            if len(clean) == 16:
                clean += ":00"
            target = datetime.fromisoformat(clean)
            now = datetime.now()
        diff = target - now
        total_seconds = int(diff.total_seconds())
        if total_seconds <= 0:
            return "Ready now"
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"in {hours}h {minutes}m"
        return f"in {minutes}m {seconds}s"
    except Exception:
        return dt_iso
