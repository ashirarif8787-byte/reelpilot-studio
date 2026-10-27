# Social Media Automation & Scheduler Desktop App
### Automated Cross-Platform Publishing for Instagram Reels & TikTok

A modular, desktop automation application engineered in Python with Tkinter/CustomTkinter, Watchdog, SQLite, FFmpeg, and official social media publishing APIs (Meta Graph API & TikTok Content Posting API).

---

## 🌟 Key Features

1. **Local Folder Watcher (`watchdog`)**:
   - Monitors `watch_folders/Ready_for_Insta` and `watch_folders/Ready_for_TikTok`.
   - Real-time detection of dropped images (`.jpg`, `.png`, `.webp`) and videos (`.mp4`, `.mov`).
   - SHA-256 hash calculation and SQLite deduplication to prevent duplicate uploads forever.

2. **Viral Audio Integration & FFmpeg Media Engine**:
   - Automatically converts static pictures into 7-10 second vertical 9:16 Reels/TikToks (1080x1920).
   - Cinematic background-blur effect with foreground centering (eliminates black bars and distortion).
   - Fetches trending audio tracks and maintains a local viral audio library with offline fallback beats.
   - Detects silent videos and overlays trending audio tracks automatically.

3. **AI Caption & Hashtag Generation (OpenAI)**:
   - Integrates OpenAI (`gpt-4o-mini` / `gpt-4o`) to craft high-retention hooks, engaging captions, clear Call-To-Actions (CTA), and 5-8 trending hashtags.
   - Includes heuristic viral fallback templates if API keys are unconfigured.

4. **Human-like Scheduler & Anti-Spam Delays**:
   - Enforces daily upload limits (e.g., max 3 posts/day per platform).
   - Implements randomized delays (e.g., 2 to 4 hours between posts) with timing jitter to protect accounts from algorithmic spam detection and shadowbans.
   - If daily limit is reached, automatically postpones remaining posts to tomorrow morning.

5. **Official API Uploaders**:
   - **Instagram & Facebook**: Official Meta Graph API v19+ (Resumable video containers, status polling, and publishing).
   - **TikTok**: Official TikTok Content Posting API v2 (Direct Post init, chunk upload, and status verification).
   - Automatic token expiration handling: immediately pauses the queue and triggers a UI alert.

---

## 📂 Project Structure

```text
Track media/
├── app/
│   ├── config.py                   # Centralized settings & config.json manager
│   ├── database/
│   │   ├── db.py                   # SQLite database manager & duplicate tracking
│   │   └── models.py               # Post models & statuses
│   ├── modules/
│   │   ├── watcher.py              # Module 1: Watchdog local folder monitor
│   │   ├── audio_fetcher.py        # Module 2a: Trending audio fetcher & sound library
│   │   ├── media_processor.py      # Module 2b: FFmpeg video & audio merger
│   │   ├── caption_generator.py    # Module 3: OpenAI viral caption generator
│   │   ├── scheduler.py            # Module 4: Scheduler queue & human-like delays
│   │   └── uploaders/              # Module 5: Official APIs
│   │       ├── base_uploader.py    # Base class & TokenExpiredException
│   │       ├── meta_uploader.py    # Meta Graph API (Instagram & Facebook)
│   │       └── tiktok_uploader.py  # TikTok Content Posting API
│   ├── ui/
│   │   └── main_window.py          # Desktop GUI (CustomTkinter / Tkinter)
│   └── utils/
│       ├── helpers.py              # Media analysis & formatting helpers
│       └── logger.py               # Custom logging with live UI listener
├── watch_folders/
│   ├── Ready_for_Insta/            # Drop Instagram images/videos here
│   └── Ready_for_TikTok/           # Drop TikTok images/videos here
├── audio_library/                  # Trending/viral audio tracks
├── processed_media/                # Rendered 1080x1920 vertical videos
├── requirements.txt
├── config.json
├── run.py                          # GUI application launcher
└── cli_test.py                     # Independent test suite for each module
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **FFmpeg**: Must be installed and available in system PATH. (Run `ffmpeg -version` to verify).

### 2. Installation
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run the Desktop Application
```powershell
python run.py
```

### 4. Run Modular Independent Tests
To test every module individually without opening the GUI:
```powershell
python cli_test.py
```
Or test any single script directly:
```powershell
# Test Folder Watcher
python -m app.modules.watcher

# Test Viral Audio Fetcher
python -m app.modules.audio_fetcher

# Test Media Processing (FFmpeg image to 9:16 reel)
python -m app.modules.media_processor

# Test AI Caption Generation
python -m app.modules.caption_generator
```

---

## ⚙️ Official API Setup Guide

### Meta Graph API (Instagram Reels):
1. Create a Meta Developer App at [developers.facebook.com](https://developers.facebook.com).
2. Connect an **Instagram Professional/Creator Account** linked to a **Facebook Page**.
3. Generate a Long-Lived Access Token with permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
4. Enter your **Meta Access Token** and **Instagram Account ID** in the GUI Settings panel.

### TikTok Content Posting API:
1. Register at [developers.tiktok.com](https://developers.tiktok.com).
2. Create an app and request access to the **Content Posting API** scope: `video.publish`, `video.upload`.
3. Complete OAuth authorization to receive your user `access_token`.
4. Enter the token in the GUI Settings panel.
