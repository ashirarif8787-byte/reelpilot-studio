"""
Configuration manager for API keys, limits, folders, and delay settings.
Persists settings into config.json.
"""
import os
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any


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
    brand_name: str = "My Brand"
    
    # Social Media API Credentials
    meta_access_token: str = ""
    instagram_account_id: str = ""
    facebook_page_id: str = ""
    meta_app_id: str = ""
    meta_app_secret: str = ""
    
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

    def ensure_directories(self):
        """Ensures all configured folders exist on disk."""
        if os.environ.get("VERCEL"):
            return
        for folder in [
            self.watch_folder_insta,
            self.watch_folder_tiktok,
            self.watch_folder_facebook,
            self.processed_folder,
            self.audio_library_folder
        ]:
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception:
                pass


class ConfigManager:
    def __init__(self, config_file: str = CONFIG_PATH):
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
        
        if os.getenv("META_ACCESS_TOKEN"):
            cfg.meta_access_token = os.getenv("META_ACCESS_TOKEN")
        if os.getenv("FACEBOOK_PAGE_ID"):
            cfg.facebook_page_id = os.getenv("FACEBOOK_PAGE_ID")
        if os.getenv("INSTAGRAM_ACCOUNT_ID"):
            cfg.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        if os.getenv("BRAND_NAME"):
            cfg.brand_name = os.getenv("BRAND_NAME")

        if not os.path.exists(self.config_file) and not os.environ.get("VERCEL"):
            self.save(cfg)
        return cfg

    def save(self, cfg: AppConfig = None):
        """Saves current configuration to config.json."""
        if cfg:
            self.config = cfg
        if os.environ.get("VERCEL"):
            return
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
