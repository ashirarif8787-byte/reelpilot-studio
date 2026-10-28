import os
import json
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

# PERMANENT CREDENTIALS (NEVER EXPIRES)
PERMANENT_META_TOKEN = "EAAZATAUGR6T0BSZCvsRTCqnkWl4PI0cJI5YvHcAEtlEp96JB59RSTGdEqbND72SDY01BRLdO0dQxi0xjXbdAmCZAxZBuKOvVEKUW9I2tMFNyC8ZBdnd2F6ZC5caZAQ6ZBhuX1tZA7TVMZB85Ec7rk9q4duiUJygZAmdXxTU5kd2sJZBUCBO2mrzhWWlpg4huzuJL64d7ZCPF4lsE9"
PERMANENT_FB_PAGE_ID = "800869286434757"
PERMANENT_IG_ID = "17841423338066933"
PERMANENT_BRAND_NAME = "JANI's Perfume"
PERMANENT_APP_ID = "1780114720418109"
PERMANENT_APP_SECRET = "6af61d4174e0d667bbe5d022c6f32b3b"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")

@dataclass
class AppConfig:
    # AI Credentials (Gemini & OpenAI)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_engine: str = "auto"  # "auto", "gemini", "openai"
    brand_name: str = PERMANENT_BRAND_NAME
    
    # Social Media API Credentials (Permanent Defaults for JANI's Perfume)
    meta_access_token: str = PERMANENT_META_TOKEN
    instagram_account_id: str = PERMANENT_IG_ID
    facebook_page_id: str = PERMANENT_FB_PAGE_ID
    meta_app_id: str = PERMANENT_APP_ID
    meta_app_secret: str = PERMANENT_APP_SECRET
    
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    tiktok_access_token: str = ""
    tiktok_open_id: str = ""

    # Cloudflare R2 Storage (Free 10GB persistent hosting)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_domain: str = ""

    # Scheduling & Daily Limits
    posting_mode: str = "human_delay"  # "instant" or "human_delay"
    daily_limit_insta: int = 3
    daily_limit_tiktok: int = 3
    daily_limit_facebook: int = 3
    min_delay_minutes: int = 120  # 2 hours
    max_delay_minutes: int = 240  # 4 hours
    human_like_variance: bool = True
    scheduler_check_interval_seconds: int = 5

    # Media Processing
    image_duration_seconds: int = 8  # 7-10s short video / Reel
    video_width: int = 1080
    video_height: int = 1920
    fps: int = 30
    
    # Watch & Working Folders
    watch_folder_insta: str = os.path.join(PROJECT_ROOT, "watch_folders", "Ready_for_Insta")
    watch_folder_tiktok: str = os.path.join(PROJECT_ROOT, "watch_folders", "Ready_for_TikTok")
    watch_folder_facebook: str = os.path.join(PROJECT_ROOT, "watch_folders", "Ready_for_Facebook")
    processed_folder: str = os.path.join(PROJECT_ROOT, "processed_media")
    audio_library_folder: str = os.path.join(PROJECT_ROOT, "audio_library")

    # Storage Paths
    watch_folder_instagram: str = os.path.join(PROJECT_ROOT, "watch_folders", "Ready_for_Instagram")
    output_folder_tiktok: str = "output/tiktok"
    output_folder_meta: str = "output/meta"

    def ensure_directories(self):
        """Ensures all configured folders exist on disk (safe on serverless)."""
        if os.environ.get("VERCEL"):
            return
        for folder in [
            self.watch_folder_insta,
            self.watch_folder_tiktok,
            self.watch_folder_facebook,
            self.watch_folder_instagram,
            self.processed_folder,
            self.audio_library_folder,
            "assets/watermarks",
            "assets/fonts"
        ]:
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception:
                pass


class ConfigManager:
    """Thread-safe singleton config manager that persists changes to JSON."""
    def __init__(self, config_file: str = CONFIG_PATH):
        if os.environ.get("VERCEL"):
            self.config_file = "/tmp/reelpilot_config.json"
        else:
            self.config_file = config_file
        self.config = self.load()
        self.config.ensure_directories()

    def load(self) -> AppConfig:
        """Loads configuration from config.json or returns default."""
        data = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[ConfigManager] Error reading config: {e}. Falling back to defaults.")
        
        cfg = AppConfig(**{k: v for k, v in data.items() if hasattr(AppConfig, k)})
        
        # Ensure permanent token is preserved
        if not cfg.meta_access_token:
            cfg.meta_access_token = os.getenv("META_ACCESS_TOKEN", PERMANENT_META_TOKEN)
        if not cfg.facebook_page_id:
            cfg.facebook_page_id = os.getenv("FACEBOOK_PAGE_ID", PERMANENT_FB_PAGE_ID)
        if not cfg.instagram_account_id:
            cfg.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", PERMANENT_IG_ID)
        if not cfg.brand_name or cfg.brand_name == "My Brand":
            cfg.brand_name = os.getenv("BRAND_NAME", PERMANENT_BRAND_NAME)
        if not cfg.meta_app_id:
            cfg.meta_app_id = os.getenv("META_APP_ID", PERMANENT_APP_ID)
        if not cfg.meta_app_secret:
            cfg.meta_app_secret = os.getenv("META_APP_SECRET", PERMANENT_APP_SECRET)

        if not os.path.exists(self.config_file):
            self.save(cfg)
        return cfg

    def save(self, cfg: AppConfig = None):
        """Saves current configuration to config.json or /tmp on Vercel."""
        if cfg:
            self.config = cfg
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, indent=4)
        except Exception:
            pass

    def update(self, **kwargs):
        """Updates specific settings and persists to disk."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save()
        self.config.ensure_directories()


# Singleton instance
config_manager = ConfigManager()
