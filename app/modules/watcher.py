"""
Module 1: Local Folder Watcher
Monitors local folders (e.g. Ready_for_Insta, Ready_for_TikTok) using watchdog.
Detects newly dropped images/videos, deduplicates via SQLite, and pushes to processing queue.
"""
import os
import time
import threading
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from app.config import config_manager
from app.database.db import DatabaseManager
from app.database.models import Platform, PostStatus
from app.utils.helpers import detect_media_type
from app.utils.logger import logger


class MediaDropHandler(FileSystemEventHandler):
    """Handles new file creation events in watched directories."""

    def __init__(self, platform: str, db: DatabaseManager, on_new_file_callback: Optional[Callable[[int], None]] = None):
        super().__init__()
        self.platform = platform
        self.db = db
        self.on_new_file_callback = on_new_file_callback
        self._processed_recent = set()

    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory:
            self._handle_file(event.src_path)

    def on_moved(self, event: FileMovedEvent):
        if not event.is_directory:
            self._handle_file(event.dest_path)

    def _wait_for_file_settled(self, file_path: str, timeout: int = 15) -> bool:
        """Ensures the file is fully copied and not locked by the operating system."""
        start_time = time.time()
        last_size = -1
        while time.time() - start_time < timeout:
            if not os.path.exists(file_path):
                return False
            try:
                current_size = os.path.getsize(file_path)
                if current_size > 0 and current_size == last_size:
                    # Try opening the file to verify read access
                    with open(file_path, "rb"):
                        return True
                last_size = current_size
            except (OSError, PermissionError):
                pass
            time.sleep(0.5)
        return False

    def _handle_file(self, file_path: str):
        # Ignore temporary files or non-media
        file_name = os.path.basename(file_path)
        if file_name.startswith((".", "~", "$")) or file_name.endswith((".tmp", ".crdownload", ".part")):
            return

        media_type = detect_media_type(file_path)
        if not media_type:
            logger.debug(f"[Watcher] Ignored unsupported file format: {file_name}")
            return

        # Ensure write is finished
        if not self._wait_for_file_settled(file_path):
            logger.warning(f"[Watcher] File did not settle or was removed: {file_path}")
            return

        # Calculate file hash
        try:
            file_hash = self.db.calculate_file_hash(file_path)
        except Exception as e:
            logger.error(f"[Watcher] Error calculating hash for {file_name}: {e}")
            return

        # Deduplication check
        if self.db.is_duplicate(file_hash):
            logger.info(f"[Watcher] Duplicate detected! Skipping already registered file: {file_name}")
            return

        # Insert into DB
        post_id = self.db.insert_post(
            file_path=os.path.abspath(file_path),
            file_hash=file_hash,
            target_platform=self.platform,
            media_type=media_type,
            status=PostStatus.QUEUED.value
        )

        if post_id:
            logger.info(f"✨ [Watcher] New {media_type.upper()} detected for {self.platform.upper()}: {file_name} (Post ID: {post_id})")
            if self.on_new_file_callback:
                try:
                    self.on_new_file_callback(post_id)
                except Exception as e:
                    logger.error(f"[Watcher] Callback error for post {post_id}: {e}")


class FolderWatcherService:
    """Manages the watchdog observer threads for all target platform folders."""

    def __init__(self, db: Optional[DatabaseManager] = None, on_new_file: Optional[Callable[[int], None]] = None):
        self.db = db or DatabaseManager()
        self.on_new_file = on_new_file
        self.observer: Optional[Observer] = None
        self._is_running = False

    def start(self):
        """Starts monitoring configured watch folders."""
        if self._is_running:
            logger.warning("[Watcher] Watcher is already running.")
            return

        config_manager.config.ensure_directories()
        self.observer = Observer()

        # Schedule watcher for Instagram
        insta_folder = config_manager.config.watch_folder_insta
        insta_handler = MediaDropHandler(
            platform=Platform.INSTAGRAM.value,
            db=self.db,
            on_new_file_callback=self.on_new_file
        )
        self.observer.schedule(insta_handler, insta_folder, recursive=False)
        logger.info(f"[Watcher] Monitoring Instagram folder: {insta_folder}")

        # Schedule watcher for TikTok
        tiktok_folder = config_manager.config.watch_folder_tiktok
        tiktok_handler = MediaDropHandler(
            platform=Platform.TIKTOK.value,
            db=self.db,
            on_new_file_callback=self.on_new_file
        )
        self.observer.schedule(tiktok_handler, tiktok_folder, recursive=False)
        logger.info(f"[Watcher] Monitoring TikTok folder: {tiktok_folder}")

        # Schedule watcher for Facebook
        fb_folder = config_manager.config.watch_folder_facebook
        fb_handler = MediaDropHandler(
            platform=Platform.FACEBOOK.value,
            db=self.db,
            on_new_file_callback=self.on_new_file
        )
        self.observer.schedule(fb_handler, fb_folder, recursive=False)
        logger.info(f"[Watcher] Monitoring Facebook folder: {fb_folder}")

        self.observer.start()
        self._is_running = True
        logger.info("[Watcher] Local Folder Watcher service started successfully.")

    def stop(self):
        """Stops the folder watcher cleanly."""
        if self.observer and self._is_running:
            self.observer.stop()
            self.observer.join(timeout=3)
            self._is_running = False
            logger.info("[Watcher] Folder Watcher service stopped.")

    @property
    def is_running(self) -> bool:
        return self._is_running


# Standalone CLI test for Module 1
if __name__ == "__main__":
    print("=== Testing Module 1: Local Folder Watcher ===")
    service = FolderWatcherService()
    service.start()
    print("Watcher running. Drop an image or video into watch_folders/Ready_for_Insta or Ready_for_TikTok.")
    print("Press Ctrl+C to terminate.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
        print("Watcher stopped.")
