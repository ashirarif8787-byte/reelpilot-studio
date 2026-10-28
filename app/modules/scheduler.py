"""
Module 4: Scheduler & Human-like Delay Queue Engine
Uses Python's schedule library and background worker threads.
Enforces strict daily upload limits and calculates human-like randomized delays (2 to 4 hours)
to protect accounts from spam detection and algorithmic shadowbans.
"""
import os
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any

from app.config import config_manager
from app.database.db import DatabaseManager
from app.database.models import PostRecord, PostStatus, Platform
from app.modules.media_processor import media_processor
from app.modules.caption_generator import caption_generator
from app.modules.uploaders import MetaUploader, TikTokUploader, TokenExpiredException
from app.utils.logger import logger


class SocialScheduler:
    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
        on_queue_update_callback: Optional[Callable[[], None]] = None,
        on_alert_callback: Optional[Callable[[str, str], None]] = None
    ):
        self.db = db or DatabaseManager()
        self.on_queue_update = on_queue_update_callback
        self.on_alert = on_alert_callback

        self.meta_uploader = MetaUploader()
        self.tiktok_uploader = TikTokUploader()

        self._stop_event = threading.Event()
        self._is_paused = False
        self._worker_thread: Optional[threading.Thread] = None

    def start(self):
        """Starts background scheduler thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            logger.warning("[Scheduler] Worker thread is already active.")
            return

        self._stop_event.clear()
        self._is_paused = False
        self._worker_thread = threading.Thread(target=self._run_loop, daemon=True, name="SchedulerWorker")
        self._worker_thread.start()
        logger.info("[Scheduler] Automated scheduler loop started.")

    def stop(self):
        """Stops the scheduler cleanly."""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=3)
        logger.info("[Scheduler] Scheduler loop stopped.")

    def pause(self, reason: str = ""):
        """Pauses scheduled uploads (e.g. on token expiration)."""
        self._is_paused = True
        logger.warning(f"[Scheduler] Queue PAUSED. Reason: {reason}")
        if self.on_alert:
            self.on_alert("Scheduler Paused", reason)
        self._notify_update()

    def resume(self):
        """Resumes scheduled uploads."""
        self._is_paused = False
        logger.info("[Scheduler] Queue RESUMED by user.")
        self._notify_update()

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def is_running(self) -> bool:
        return self._worker_thread is not None and self._worker_thread.is_alive() and not self._stop_event.is_set()

    def _notify_update(self):
        if self.on_queue_update:
            try:
                self.on_queue_update()
            except Exception:
                pass

    def _run_loop(self):
        """Continuous scheduler tick loop."""
        while not self._stop_event.is_set():
            try:
                # 1. Process any newly discovered QUEUED posts
                self._process_unprocessed_queue()

                # 2. If not paused, check for posts ready to be uploaded
                if not self._is_paused:
                    self._check_and_upload_due_posts()

            except Exception as e:
                logger.error(f"[Scheduler] Exception in run loop: {e}")

            # Sleep short interval before next iteration
            interval = config_manager.config.scheduler_check_interval_seconds
            for _ in range(interval):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def _calculate_next_post_time(self, platform: str) -> datetime:
        """
        Calculates human-like randomized posting timestamp:
        - If daily limit is reached today, schedules for tomorrow morning + jitter.
        - Otherwise, calculates base randomized interval (e.g. 120-240 minutes) + random seconds.
        """
        now = datetime.now()
        if platform == Platform.INSTAGRAM.value:
            daily_limit = config_manager.config.daily_limit_insta
        elif platform == Platform.FACEBOOK.value:
            daily_limit = config_manager.config.daily_limit_facebook
        else:
            daily_limit = config_manager.config.daily_limit_tiktok
        today_uploads = self.db.count_uploads_today(platform)

        if today_uploads >= daily_limit:
            # Postpone to tomorrow around 9:30 AM + random jitter
            tomorrow = now.date() + timedelta(days=1)
            jitter_minutes = random.randint(0, 180)  # Between 9:00 AM and 12:00 PM
            scheduled_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0) + timedelta(minutes=jitter_minutes)
            logger.info(f"[Scheduler] Daily limit ({daily_limit}) reached today for {platform.upper()}. Postponed to {scheduled_dt.strftime('%Y-%m-%d %H:%M')}")
            return scheduled_dt

        if config_manager.config.posting_mode == "instant":
            logger.info(f"[Scheduler] Posting mode is INSTANT. Scheduling post for immediate upload.")
            return now

        # Check last scheduled post for this platform to chain human-like delay
        scheduled_posts = self.db.get_posts(status=PostStatus.SCHEDULED.value, platform=platform)
        latest_reference_time = now
        for p in scheduled_posts:
            if p.scheduled_time:
                try:
                    dt = datetime.fromisoformat(p.scheduled_time)
                    if dt > latest_reference_time:
                        latest_reference_time = dt
                except ValueError:
                    pass

        # Calculate random human-like delay between min_delay and max_delay minutes
        min_m = config_manager.config.min_delay_minutes
        max_m = config_manager.config.max_delay_minutes
        delay_minutes = random.randint(min_m, max_m)
        delay_seconds = random.randint(0, 59)
        next_time = latest_reference_time + timedelta(minutes=delay_minutes, seconds=delay_seconds)
        return next_time

    def _process_unprocessed_queue(self):
        """Pulls QUEUED posts, renders media (videos only), generates viral caption, and schedules them."""
        queued_posts = self.db.get_posts(status=PostStatus.QUEUED.value, limit=5)
        for post in queued_posts:
            if self._stop_event.is_set():
                break

            media_type = getattr(post, "media_type", "image") or "image"
            logger.info(f"[Scheduler] Processing post #{post.id} ({media_type})...")
            self.db.update_post(post.id, status=PostStatus.PROCESSING.value)
            self._notify_update()

            processed_path = post.file_path
            caption = post.caption or ""
            hashtags = post.hashtags or ""

            is_carousel = (media_type == "carousel") or (post.file_path and post.file_path.strip().startswith("["))
            if is_carousel:
                try:
                    photo_list = json.loads(post.file_path)
                    primary_file = photo_list[0] if photo_list else post.file_path
                except Exception:
                    primary_file = post.file_path
            else:
                primary_file = post.file_path

            # 1. Media Processing ONLY for Videos (Native images stay pure images/carousels)
            if media_type == MediaType.VIDEO.value or (primary_file and any(primary_file.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv"])):
                success, proc_res, err = media_processor.process_media(
                    input_path=primary_file,
                    target_platform=post.target_platform
                )
                if not success:
                    logger.error(f"[Scheduler] Video processing failed for post #{post.id}: {err}")
                    self.db.update_post(post.id, status=PostStatus.FAILED.value, error_message=err)
                    self.db.log_event(post.id, post.target_platform, PostStatus.FAILED.value, f"Media processing error: {err}")
                    self._notify_update()
                    continue
                processed_path = proc_res
            else:
                processed_path = post.file_path

            # 2. AI Vision Caption & Hashtag Generation (if not already provided)
            if (not caption or not hashtags) and primary_file and os.path.exists(primary_file):
                ai_caption, ai_hashtags, sound_vibe = caption_generator.generate(
                    file_path=primary_file,
                    platform=post.target_platform
                )
                if not caption:
                    caption = ai_caption
                if not hashtags:
                    hashtags = ai_hashtags

            # 3. Scheduling Time: Use user-chosen scheduled time, or calculate delay
            if post.scheduled_time and str(post.scheduled_time).strip():
                scheduled_iso = str(post.scheduled_time).strip()
            else:
                scheduled_dt = self._calculate_next_post_time(post.target_platform)
                scheduled_iso = scheduled_dt.isoformat()

            self.db.update_post(
                post.id,
                processed_path=processed_path,
                caption=caption,
                hashtags=hashtags,
                scheduled_time=scheduled_iso,
                status=PostStatus.SCHEDULED.value,
                error_message=None
            )
            self.db.log_event(
                post.id,
                post.target_platform,
                PostStatus.SCHEDULED.value,
                f"Scheduled for {scheduled_iso}"
            )
            logger.info(f"⏰ [Scheduler] Post #{post.id} scheduled for {scheduled_iso}")
            self._notify_update()

    def _check_and_upload_due_posts(self):
        """Finds SCHEDULED posts whose scheduled_time has arrived and uploads them."""
        now_iso = datetime.now().isoformat()
        scheduled_posts = self.db.get_posts(status=PostStatus.SCHEDULED.value)

        for post in scheduled_posts:
            if self._stop_event.is_set() or self._is_paused:
                break

            if not post.scheduled_time:
                continue

            try:
                sched_str = str(post.scheduled_time).replace("Z", "").split(".")[0]
                if len(sched_str) == 16:
                    sched_str += ":00"
                target_dt = datetime.fromisoformat(sched_str)
                if target_dt > datetime.now():
                    continue
            except Exception:
                if str(post.scheduled_time) > now_iso:
                    continue

            # Check daily upload limit
            if post.target_platform == Platform.INSTAGRAM.value:
                daily_limit = config_manager.config.daily_limit_insta
            elif post.target_platform == Platform.FACEBOOK.value:
                daily_limit = config_manager.config.daily_limit_facebook
            else:
                daily_limit = config_manager.config.daily_limit_tiktok
            today_count = self.db.count_uploads_today(post.target_platform)
            if today_count >= daily_limit:
                new_dt = self._calculate_next_post_time(post.target_platform)
                logger.info(f"[Scheduler] Post #{post.id} bumped to tomorrow due to daily limit.")
                self.db.update_post(post.id, scheduled_time=new_dt.isoformat())
                self._notify_update()
                continue

            # Perform the upload
            self._execute_upload(post)

    def _execute_upload(self, post: PostRecord):
        """Uploads a post to its target platform with official APIs (Native Carousel, Photo, or Video)."""
        logger.info(f"[Scheduler] Uploading post #{post.id} ({post.media_type}) to {post.target_platform.upper()}...")
        self.db.update_post(post.id, status=PostStatus.UPLOADING.value)
        self._notify_update()

        media_to_upload = post.processed_path or post.file_path
        caption = post.caption or ""
        hashtags = post.hashtags or ""

        # Parse multiple paths for carousel if applicable
        photo_paths = []
        if post.media_type == "carousel" or (post.file_path and post.file_path.strip().startswith("[")):
            try:
                photo_paths = json.loads(post.file_path)
            except Exception:
                photo_paths = [post.file_path]
        else:
            photo_paths = [media_to_upload]

        try:
            if post.target_platform == Platform.FACEBOOK.value:
                if post.media_type == "carousel" or len(photo_paths) > 1:
                    success, remote_id, remote_url, err = self.meta_uploader.upload_facebook_carousel(
                        photo_paths_or_urls=photo_paths,
                        caption=caption,
                        hashtags=hashtags
                    )
                elif post.media_type == "image":
                    success, remote_id, remote_url, err = self.meta_uploader.upload_facebook_photo(
                        photo_path_or_url=photo_paths[0],
                        caption=caption,
                        hashtags=hashtags
                    )
                else:
                    success, remote_id, remote_url, err = self.meta_uploader.upload_facebook_video(
                        video_path=media_to_upload,
                        caption=caption,
                        hashtags=hashtags
                    )
            elif post.target_platform == Platform.INSTAGRAM.value:
                if post.media_type == "carousel" or len(photo_paths) > 1:
                    success, remote_id, remote_url, err = self.meta_uploader.upload_instagram_carousel(
                        media_urls=photo_paths,
                        caption=caption,
                        hashtags=hashtags
                    )
                elif post.media_type == "image":
                    success, remote_id, remote_url, err = self.meta_uploader.upload_instagram_photo(
                        photo_url=photo_paths[0],
                        caption=caption,
                        hashtags=hashtags
                    )
                else:
                    success, remote_id, remote_url, err = self.meta_uploader.upload_reel(
                        video_path=media_to_upload,
                        caption=caption,
                        hashtags=hashtags
                    )
            elif post.target_platform == Platform.TIKTOK.value:
                success, remote_id, remote_url, err = self.tiktok_uploader.upload_reel(
                    video_path=media_to_upload,
                    caption=caption,
                    hashtags=hashtags
                )
            else:
                success, remote_id, remote_url, err = False, None, None, f"Unsupported platform: {post.target_platform}"

            if success:
                now_str = datetime.now().isoformat()
                self.db.update_post(
                    post.id,
                    status=PostStatus.UPLOADED.value,
                    uploaded_at=now_str,
                    remote_media_id=remote_id,
                    remote_url=remote_url,
                    error_message=None
                )
                self.db.log_event(
                    post.id,
                    post.target_platform,
                    PostStatus.UPLOADED.value,
                    f"Uploaded successfully. Remote ID: {remote_id} | URL: {remote_url}"
                )
                logger.info(f"🎉 [Scheduler] Post #{post.id} UPLOAD COMPLETED! Remote ID: {remote_id}")
            else:
                self.db.update_post(post.id, status=PostStatus.FAILED.value, error_message=err)
                self.db.log_event(post.id, post.target_platform, PostStatus.FAILED.value, f"Upload error: {err}")
                logger.error(f"[Scheduler] Upload failed for post #{post.id}: {err}")

        except TokenExpiredException as te:
            err_msg = str(te)
            self.db.update_post(post.id, status=PostStatus.PAUSED.value, error_message=err_msg)
            self.db.log_event(post.id, post.target_platform, PostStatus.PAUSED.value, f"Token expired: {err_msg}")
            self.pause(reason=f"Token Expired for {post.target_platform.upper()}: {err_msg}")

        except Exception as e:
            err_msg = f"Unexpected upload exception: {e}"
            self.db.update_post(post.id, status=PostStatus.FAILED.value, error_message=err_msg)
            self.db.log_event(post.id, post.target_platform, PostStatus.FAILED.value, err_msg)
            logger.error(f"[Scheduler] Post #{post.id} failed: {err_msg}")

        self._notify_update()
