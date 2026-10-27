"""
Modular CLI Test Suite for Social Media Automation & Scheduler App.
Allows isolated, step-by-step testing of every individual module.
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from app.config import config_manager
from app.database.db import DatabaseManager
from app.database.models import PostStatus
from app.modules.watcher import FolderWatcherService
from app.modules.audio_fetcher import audio_service
from app.modules.media_processor import media_processor
from app.modules.caption_generator import caption_generator
from app.modules.uploaders import MetaUploader, TikTokUploader
from app.modules.scheduler import SocialScheduler


def test_database():
    print("\n[TEST 1] Testing Database & Duplicate Detection...")
    db = DatabaseManager()
    dummy_file = os.path.join(config_manager.config.watch_folder_insta, "db_test.txt")
    with open(dummy_file, "w") as f:
        f.write("test content for hashing")
    f_hash = db.calculate_file_hash(dummy_file)
    print(f"Calculated Hash: {f_hash}")
    
    post_id = db.insert_post(dummy_file, f_hash, "instagram", "image")
    print(f"Inserted Post ID: {post_id}")
    
    dup_check = db.is_duplicate(f_hash)
    print(f"Duplicate detected on re-check? {dup_check} (Expected: True)")
    assert dup_check is True, "Database deduplication failed!"
    print("Database test passed!\n")


def test_audio_fetcher():
    print("\n[TEST 2] Testing Viral Audio Integration...")
    tracks = audio_service.get_available_tracks()
    print(f"Available audio tracks in library: {len(tracks)}")
    for t in tracks:
        print(f" - {os.path.basename(t)}")
    random_track = audio_service.get_random_viral_track()
    print(f"Selected viral audio track: {random_track}")
    assert random_track is not None and os.path.exists(random_track), "Viral audio fetch failed!"
    print("Audio Fetcher test passed!\n")


def test_media_processor():
    print("\n[TEST 3] Testing Media Processor (Image -> 9:16 Reel with Viral Audio)...")
    test_img = os.path.join(config_manager.config.watch_folder_insta, "cli_test_image.png")
    img = Image.new("RGB", (720, 720), color=(255, 87, 34))
    draw = ImageDraw.Draw(img)
    draw.text((200, 350), "CLI Reel Automation Test", fill=(255, 255, 255))
    img.save(test_img)
    print(f"Generated test image: {test_img}")

    success, processed_path, err = media_processor.process_media(
        input_path=test_img,
        target_platform="instagram",
        duration=7
    )
    print(f"Media Processing Success: {success}")
    print(f"Processed Video Output: {processed_path}")
    if err:
        print(f"Error: {err}")
    assert success is True and os.path.exists(processed_path), "Media processing failed!"
    print(f"File size: {os.path.getsize(processed_path)} bytes")
    print("Media Processor test passed!\n")


def test_caption_generator():
    print("\n[TEST 4] Testing AI Caption & Hashtag Generation...")
    sample_file = "incredible_tokyo_night_street_walk.mp4"
    caption, tags = caption_generator.generate(sample_file, platform="instagram")
    print("\nGenerated Caption:")
    print("--------------------------------------------------")
    print(caption)
    print("--------------------------------------------------")
    print(f"Hashtags: {tags}")
    print("Caption Generator test passed!\n")


def test_uploaders():
    print("\n[TEST 5] Testing API Credentials Validation...")
    meta = MetaUploader()
    valid_meta, msg_meta = meta.validate_credentials()
    print(f"Meta Graph API Check: Valid={valid_meta} | Details: {msg_meta}")

    tiktok = TikTokUploader()
    valid_tt, msg_tt = tiktok.validate_credentials()
    print(f"TikTok API Check: Valid={valid_tt} | Details: {msg_tt}")
    print("Uploaders check completed!\n")


def test_folder_watcher():
    print("\n[TEST 6] Testing Local Folder Watcher (Interactive 10-Second Test)...")
    db = DatabaseManager()
    detected_posts = []

    def on_detect(pid):
        print(f"--> [EVENT] Detected and queued new post ID: {pid}")
        detected_posts.append(pid)

    watcher = FolderWatcherService(db=db, on_new_file=on_detect)
    watcher.start()

    # Drop a test file into Instagram folder
    drop_file = os.path.join(config_manager.config.watch_folder_insta, f"drop_test_{int(time.time())}.png")
    img = Image.new("RGB", (500, 500), color=(0, 200, 83))
    img.save(drop_file)
    print(f"Dropped test image: {os.path.basename(drop_file)}")

    print("Waiting 4 seconds for watchdog event...")
    time.sleep(4)
    watcher.stop()

    print(f"Posts detected by watcher: {detected_posts}")
    assert len(detected_posts) > 0, "Watcher failed to detect dropped file!"
    print("Folder Watcher test passed!\n")


if __name__ == "__main__":
    print("==================================================")
    print("  Social Media Automation & Scheduler App - CLI Tester")
    print("==================================================")
    
    test_database()
    test_audio_fetcher()
    test_media_processor()
    test_caption_generator()
    test_uploaders()
    test_folder_watcher()

    print("==================================================")
    print("  ALL INDEPENDENT MODULE TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")
