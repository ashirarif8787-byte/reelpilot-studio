import os
import json
from dataclasses import dataclass, asdict, field
from typing import Optional
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env once so credentials stay out of the source code.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except Exception:
    pass

# ---------------------------------------------------------------------------
# META / FACEBOOK CREDENTIALS
#
# A Meta access token is NOT permanent. Long-lived Page tokens have no expiry
# date, but Meta invalidates them on password change / app removal / security
# checks (error 190, subcode 460). The app therefore obtains its own token via
# "Connect with Facebook" (see app/modules/meta_auth.py) and repairs it
# automatically. Nothing below is required for that flow except the App ID and
# App Secret, which live in .env — never in this file.
# ---------------------------------------------------------------------------
PERMANENT_META_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
PERMANENT_FB_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
PERMANENT_IG_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
PERMANENT_BRAND_NAME = "JANI's Perfume"
PERMANENT_BRAND_WEBSITE = "janisperfumes.com"
PERMANENT_BRAND_WHATSAPP = "03134454899"
PERMANENT_BRAND_FOOTER = """🌐 𝐖𝐞𝐛𝐬𝐢𝐭𝐞 𝐂𝐡𝐞𝐜𝐤𝐨𝐮𝐭: janisperfumes.com
💬 𝐏𝐫𝐞𝐟𝐞𝐫 𝐖𝐡𝐚𝐭𝐬𝐀𝐩𝐩: 03134454899
📩 𝐒𝐞𝐧𝐝 𝐮𝐬 𝐚 𝐃𝐌 𝐭𝐨 𝐨𝐫𝐝𝐞𝐫 𝐝𝐢𝐫𝐞𝐜𝐭𝐥𝐲!"""
PERMANENT_APP_ID = os.getenv("META_APP_ID", "")
PERMANENT_APP_SECRET = os.getenv("META_APP_SECRET", "")

CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")

@dataclass
class AppConfig:
    # AI Credentials (Gemini & OpenAI)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-lite-latest"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_engine: str = "auto"  # "auto", "gemini", "openai"
    brand_name: str = PERMANENT_BRAND_NAME
    brand_website: str = PERMANENT_BRAND_WEBSITE
    brand_whatsapp: str = PERMANENT_BRAND_WHATSAPP
    brand_footer: str = PERMANENT_BRAND_FOOTER
    
    # Social Media API Credentials (Permanent Defaults for JANI's Perfume)
    meta_access_token: str = PERMANENT_META_TOKEN
    instagram_account_id: str = PERMANENT_IG_ID
    facebook_page_id: str = PERMANENT_FB_PAGE_ID
    meta_app_id: str = PERMANENT_APP_ID
    meta_app_secret: str = PERMANENT_APP_SECRET

    # Meta OAuth connection state — written automatically by "Connect with Facebook"
    meta_user_token: str = ""                 # long-lived Facebook login (~60 days)
    meta_user_token_expires_at: int = 0
    meta_data_access_expires_at: int = 0       # when the granted permissions lapse
    meta_page_token_expires_at: int = 0        # 0 = Page token has no fixed expiry
    meta_page_name: str = ""
    meta_ig_username: str = ""
    meta_connected_at: str = ""
    meta_needs_reauth: bool = False
    meta_last_error: str = ""
    # Every Facebook Page this login can publish to, each with its own Instagram account.
    # [{"page_id", "page_name", "page_token", "ig_id", "ig_username"}]
    meta_pages: list = field(default_factory=list)
    
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

        # Serverless hosts have an ephemeral filesystem: restore the Facebook
        # connection from durable storage so it survives cold starts.
        if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
            try:
                from app.modules import remote_store
                stored = remote_store.load_meta()
                for key, value in (stored or {}).items():
                    if hasattr(cfg, key) and value not in (None, ""):
                        setattr(cfg, key, value)
            except Exception as e:
                print(f"[ConfigManager] Remote state unavailable: {e}")
        
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

        # AI keys ship as environment variables on hosted deployments, so the
        # serverless filesystem never has to hold a secret.
        if not cfg.gemini_api_key:
            cfg.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        if not cfg.openai_api_key:
            cfg.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if os.getenv("GEMINI_MODEL"):
            cfg.gemini_model = os.getenv("GEMINI_MODEL")
        if os.getenv("OPENAI_MODEL"):
            cfg.openai_model = os.getenv("OPENAI_MODEL")

        # Older profiles only have the single Page fields: expose them as a list.
        if not cfg.meta_pages and cfg.facebook_page_id:
            cfg.meta_pages = [{
                "page_id": str(cfg.facebook_page_id),
                "page_name": cfg.meta_page_name or "",
                "page_token": cfg.meta_access_token or "",
                "ig_id": str(cfg.instagram_account_id or ""),
                "ig_username": cfg.meta_ig_username or "",
            }]

        if not os.path.exists(self.config_file):
            self.save(cfg)
        return cfg

    def save(self, cfg: AppConfig = None):
        """Saves current configuration to config.json or /tmp on Vercel."""
        if cfg:
            self.config = cfg
        try:
            data = asdict(self.config)
            # The App Secret belongs to .env only — never duplicate it into config.json.
            if "meta_app_secret" in data:
                data["meta_app_secret"] = ""
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
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
