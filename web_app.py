"""
ReelPilot Studio v3.6 - Enterprise Social Media Automation & Multi-Media Hub
Features:
- Multi-Image Albums & Carousels (1 to 12 photos) with selectable Main Cover
- Native Photos & Pure Carousels (No forced video conversion for images)
- Interactive Visual Calendar & Scheduled Publishing Engine
- Worldwide Music Search & Audio Trimmer (iTunes 100M+ global song catalog)
- Cloudflare R2 Persistent Object Storage (Free 10GB S3-compatible) + Instant Fallback
- Dual-AI Vision (Google Gemini 1.5 Flash + OpenAI GPT-4o Vision)
- Dedicated separation for Instagram and Facebook Page
"""
import os
import sys
import time
import json
import threading
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, render_template_string, send_from_directory, session, redirect, url_for
from werkzeug.utils import secure_filename

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from app.config import config_manager
from app.database.db import DatabaseManager
from app.database.models import PostStatus, Platform, MediaType
try:
    from app.modules.watcher import FolderWatcherService
except Exception:
    FolderWatcherService = None

try:
    from app.modules.scheduler import SocialScheduler
except Exception:
    SocialScheduler = None
from app.modules.caption_generator import caption_generator, append_brand_footer
from app.modules.uploaders import MetaUploader, TikTokUploader
from app.modules.audio_fetcher import audio_service
from app.modules.storage_service import storage_service
from app.utils.logger import register_ui_log_listener, logger
from app.utils.helpers import format_delay_time
from studio_template import HTML_STUDIO_V36
from login_template import LOGIN_HTML

app = Flask(__name__)
app.config["SECRET_KEY"] = "reelpilot_v36_ultimate"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

LOG_BUFFER = []
MAX_LOGS = 150

def log_listener(msg: str):
    LOG_BUFFER.append(msg)
    if len(LOG_BUFFER) > MAX_LOGS:
        LOG_BUFFER.pop(0)

register_ui_log_listener(log_listener)

IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))

db = None
scheduler = None
watcher = None

def get_db():
    global db
    if db is None:
        try:
            db = DatabaseManager()
        except Exception as e:
            logger.warning(f"DB lazy init warning: {e}")
            db = None
    return db

if not IS_VERCEL:
    try:
        db = get_db()
        scheduler = SocialScheduler(db=db)
        watcher = FolderWatcherService(db=db)
        watcher.start()
        scheduler.start()
    except Exception as e:
        logger.warning(f"Background worker start skipped: {e}")

ACCOUNTS_FILE = "/tmp/connected_accounts.json" if IS_VERCEL else os.path.join(ROOT_DIR, "connected_accounts.json")

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    cfg = config_manager.config
    fb_connected = bool(cfg.meta_access_token and cfg.facebook_page_id)
    ig_connected = bool(cfg.meta_access_token and cfg.instagram_account_id)
    return {
        "instagram": {"connected": ig_connected, "username": "official_janisperfume" if ig_connected else "Not Connected", "id": cfg.instagram_account_id or "17841423338066933", "auth_type": "permanent_page_token"},
        "facebook": {"connected": fb_connected, "page_name": "JANI's Perfume" if fb_connected else "Not Connected", "page_id": cfg.facebook_page_id or "800869286434757", "auth_type": "permanent_page_token"},
        "tiktok": {"connected": False, "username": "", "display_name": ""}
    }

def save_accounts(data):
    try:
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

# --------------------------------------------------------------------
# ROUTES & ENDPOINTS
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# AUTHENTICATION & SECURITY (Ashir87 Owner Credentials)
# --------------------------------------------------------------------
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "Ashir87")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ashir88090@")

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "janis-perfumes-ashir87-secure-auth-vault-2026")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
)

@app.before_request
def require_authentication():
    allowed_prefixes = (
        "/login",
        "/logout",
        "/static",
        "/manifest.json",
        "/sw.js",
        "/api/cron/check-due",
        "/api/media",
        "/api/video"
    )
    req_path = request.path
    if any(req_path == p or req_path.startswith(p + "/") or req_path.startswith(p) for p in allowed_prefixes):
        return None

    if not session.get("authenticated"):
        if req_path.startswith("/api/"):
            return jsonify({"error": "Unauthorized. Please login.", "redirect": "/login"}), 401
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form or {}
        u = str(data.get("username", "")).strip()
        p = str(data.get("password", ""))

        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session.permanent = True
            session["authenticated"] = True
            session["username"] = ADMIN_USERNAME
            logger.info(f"✅ [Auth] Owner '{u}' authenticated successfully.")
            return jsonify({"success": True, "redirect": "/"})

        logger.warning(f"⚠️ [Auth] Failed login attempt for username '{u}'. Access denied.")
        return jsonify({"success": False, "error": "Invalid Username or Password! Access Denied."}), 401

    if session.get("authenticated"):
        return redirect("/")
    return render_template_string(LOGIN_HTML)

@app.route("/logout", methods=["GET", "POST"])
def logout_route():
    session.clear()
    return redirect("/login")

@app.route("/manifest.json")
def pwa_manifest():
    return send_from_directory(os.path.join(ROOT_DIR, "static"), "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def pwa_sw():
    return send_from_directory(os.path.join(ROOT_DIR, "static"), "sw.js", mimetype="application/javascript")

@app.route("/static/<path:filename>")
def pwa_static(filename):
    return send_from_directory(os.path.join(ROOT_DIR, "static"), filename)


@app.route("/")
def index():
    return render_template_string(HTML_STUDIO_V36)

@app.route("/api/status")
def api_status():
    current_db = get_db()
    today_insta = current_db.count_uploads_today("instagram") if current_db else 0
    today_fb = current_db.count_uploads_today("facebook") if current_db else 0
    today_tiktok = current_db.count_uploads_today("tiktok") if current_db else 0
    all_queued = current_db.get_posts() if current_db else []
    active_in_queue = sum(1 for p in all_queued if p.status in [PostStatus.QUEUED.value, PostStatus.PROCESSING.value, PostStatus.SCHEDULED.value])

    return jsonify({
        "watcher_running": watcher.is_running if watcher else False,
        "scheduler_running": scheduler.is_running if scheduler else False,
        "active_queue_count": active_in_queue,
        "daily_counts": {
            "instagram": today_insta,
            "facebook": today_fb,
            "tiktok": today_tiktok
        },
        "daily_limits": {
            "instagram": config_manager.config.daily_limit_insta,
            "facebook": config_manager.config.daily_limit_facebook,
            "tiktok": config_manager.config.daily_limit_tiktok
        },
        "posting_mode": config_manager.config.posting_mode
    })

@app.route("/api/scheduler/mode", methods=["POST"])
def api_scheduler_mode():
    data = request.json or {}
    mode = data.get("mode", "human_delay")
    config_manager.update(posting_mode=mode)
    return jsonify({"success": True, "mode": mode})

def extract_cover_url(p):
    path = getattr(p, "processed_path", None) or getattr(p, "file_path", None) or ""
    if path.startswith("["):
        try:
            arr = json.loads(path)
            if isinstance(arr, list) and len(arr) > 0:
                path = arr[0]
        except Exception:
            pass
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    fname = os.path.basename(path)
    return f"/api/media/{fname}"

@app.route("/api/posts")
def api_posts():
    current_db = get_db()
    posts = current_db.get_posts(limit=100) if current_db else []
    result = []
    for p in posts:
        d = p.__dict__.copy()
        if p.status == PostStatus.SCHEDULED.value and p.scheduled_time:
            d["scheduled_countdown"] = format_delay_time(p.scheduled_time)
        elif p.uploaded_at:
            d["scheduled_countdown"] = f"Uploaded ({p.uploaded_at.split('T')[0]})"
        else:
            d["scheduled_countdown"] = "Ready"
        d["cover_url"] = extract_cover_url(p)
        result.append(d)
    return jsonify(result)

def format_post_datetime(iso_str: str) -> dict:
    if not iso_str:
        return {
            "exact_date": "Immediate",
            "exact_time": "Now",
            "waqt": "Foran",
            "countdown": "Ready"
        }
    try:
        from app.modules.scheduler import parse_scheduled_datetime
        dt = parse_scheduled_datetime(iso_str)
        if not dt:
            return {
                "exact_date": str(iso_str),
                "exact_time": "",
                "waqt": "",
                "countdown": "Scheduled"
            }
        local_dt = dt.astimezone()
        day_name = local_dt.strftime("%A")
        date_str = local_dt.strftime(f"{day_name}, %d %b %Y")
        time_str = local_dt.strftime("%I:%M %p")
        h = local_dt.hour
        if 5 <= h < 12:
            waqt = "Subah (Morning)"
        elif 12 <= h < 17:
            waqt = "Dopahar (Afternoon)"
        elif 17 <= h < 21:
            waqt = "Sham (Evening)"
        else:
            waqt = "Raat (Night)"
        return {
            "exact_date": date_str,
            "exact_time": time_str,
            "waqt": waqt,
            "countdown": format_delay_time(iso_str)
        }
    except Exception:
        return {
            "exact_date": str(iso_str),
            "exact_time": "",
            "waqt": "",
            "countdown": "Scheduled"
        }

@app.route("/api/calendar")
def api_calendar():
    current_db = get_db()
    try:
        from app.modules.scheduler import check_and_upload_due_posts
        check_and_upload_due_posts(db=current_db)
    except Exception as ce:
        logger.warning(f"Error checking due posts in calendar: {ce}")

    posts = current_db.get_posts(limit=150) if current_db else []
    seen_ids = set()
    calendar_events = []
    for p in posts:
        if p.scheduled_time or p.status in [PostStatus.SCHEDULED.value, PostStatus.QUEUED.value, PostStatus.UPLOADING.value, PostStatus.UPLOADED.value, PostStatus.FAILED.value]:
            d = p.__dict__.copy()
            d["dt_info"] = format_post_datetime(p.scheduled_time or p.created_at)
            d["scheduled_countdown"] = d["dt_info"]["countdown"]
            d["cover_url"] = extract_cover_url(p)
            calendar_events.append(d)
            seen_ids.add(p.id)

    # Seamlessly merge cloud queue for Vercel persistence across container recycles
    try:
        from app.modules.cloud_queue import cloud_queue
        cloud_posts = cloud_queue.get_all_posts()
        for cp in cloud_posts:
            cid = cp.get("id")
            if cid and cid not in seen_ids:
                m_urls = cp.get("media_urls", [])
                cover = m_urls[0] if m_urls else ""
                f_path = json.dumps(m_urls) if len(m_urls) > 1 else cover
                d = {
                    "id": cid,
                    "target_platform": cp.get("target_platform", "instagram"),
                    "caption": cp.get("caption", ""),
                    "hashtags": cp.get("hashtags", ""),
                    "media_type": cp.get("media_type", "image"),
                    "file_path": f_path,
                    "status": cp.get("status", "SCHEDULED"),
                    "scheduled_time": cp.get("scheduled_time"),
                    "created_at": cp.get("created_at"),
                    "error_message": cp.get("error_message"),
                    "remote_url": cp.get("remote_url"),
                    "cover_url": cover
                }
                d["dt_info"] = format_post_datetime(cp.get("scheduled_time") or cp.get("created_at"))
                d["scheduled_countdown"] = d["dt_info"]["countdown"]
                calendar_events.append(d)
                seen_ids.add(cid)
    except Exception as cqe:
        logger.warning(f"Error merging cloud queue posts into calendar: {cqe}")

    calendar_events.sort(key=lambda x: str(x.get("scheduled_time") or x.get("created_at") or ""), reverse=True)
    return jsonify({"success": True, "events": calendar_events})

@app.route("/api/audio/search")
def api_audio_search():
    query = request.args.get("q", "Trending Hits")
    limit = int(request.args.get("limit", 25))
    tracks = audio_service.search_worldwide_tracks(query=query, limit=limit)
    return jsonify({"success": True, "tracks": tracks})

@app.route("/api/audio/trim", methods=["POST"])
def api_audio_trim():
    data = request.json or {}
    preview_url = data.get("preview_url", "")
    start_sec = int(data.get("start_sec", 0))
    duration_sec = int(data.get("duration_sec", 30))
    if not preview_url:
        return jsonify({"success": False, "error": "No preview URL provided"}), 400
    trimmed_path = audio_service.download_and_trim_track(preview_url, start_sec=start_sec, duration_sec=duration_sec)
    if trimmed_path and os.path.exists(trimmed_path):
        return jsonify({"success": True, "audio_path": trimmed_path, "filename": os.path.basename(trimmed_path)})
    return jsonify({"success": False, "error": "Failed to download or trim audio"}), 500

@app.route("/api/ai/analyze-media", methods=["POST"])
def api_ai_analyze_media():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
    file = request.files["file"]
    filename = secure_filename(file.filename)
    if not filename:
        filename = f"analyze_{int(time.time())}.jpg"

    temp_dir = "/tmp/analysis" if IS_VERCEL else os.path.join(ROOT_DIR, "tmp_analysis")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)
    file.save(temp_path)

    try:
        caption, hashtags, vibe = caption_generator.generate(temp_path, platform="instagram")
        return jsonify({
            "success": True,
            "caption": caption,
            "hashtags": hashtags,
            "sound_vibe": vibe
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.route("/api/accounts/health")
def api_accounts_health():
    from app.config import PERMANENT_META_TOKEN
    cfg = config_manager.config

    candidate_tokens = []
    header_token = request.headers.get("X-Meta-Token", "").strip()
    if header_token:
        candidate_tokens.append(header_token)
    if cfg.meta_access_token and cfg.meta_access_token.strip():
        candidate_tokens.append(cfg.meta_access_token.strip())
    if PERMANENT_META_TOKEN and PERMANENT_META_TOKEN.strip():
        candidate_tokens.append(PERMANENT_META_TOKEN.strip())

    last_err_data = None
    for token in candidate_tokens:
        try:
            url = f"https://graph.facebook.com/v19.0/me?access_token={token}&fields=id,name"
            r = requests.get(url, timeout=6)
            data = r.json()
            if "error" not in data:
                user_name = data.get("name", "User")
                return jsonify({
                    "connected": True,
                    "status": "ACTIVE",
                    "user_name": user_name,
                    "message": f"Connected & Verified Live with Meta ({user_name})!",
                    "facebook": {
                        "connected": bool(cfg.facebook_page_id),
                        "name": cfg.brand_name or "JANI's Perfume",
                        "id": cfg.facebook_page_id or "800869286434757"
                    },
                    "instagram": {
                        "connected": bool(cfg.instagram_account_id),
                        "username": "official_janisperfume",
                        "id": cfg.instagram_account_id or "17841423338066933"
                    }
                })
            else:
                last_err_data = data["error"]
        except Exception as ex:
            logger.warning(f"Error verifying candidate token: {ex}")

    err_msg = last_err_data.get("message", "Token validation failed") if last_err_data else "No token configured"
    code = last_err_data.get("code") if last_err_data else 0
    subcode = last_err_data.get("error_subcode", 0) if last_err_data else 0
    is_expired = (code == 190 or subcode == 463)
    return jsonify({
        "connected": False,
        "status": "EXPIRED" if is_expired else "ERROR",
        "message": f"Meta Session Expired: {err_msg}" if is_expired else f"Meta Error: {err_msg}",
        "error_code": code,
        "subcode": subcode,
        "facebook": {"connected": False, "name": cfg.brand_name, "id": cfg.facebook_page_id},
        "instagram": {"connected": False, "username": "official_janisperfume", "id": cfg.instagram_account_id}
    })

@app.route("/api/ai/generate-luxury-copy", methods=["POST"])
def api_ai_generate_luxury_copy():
    data = request.json or {}
    product_name = data.get("product_name", "")
    volume_ml = data.get("volume_ml", "100ml")
    scent_notes = data.get("scent_notes", "")
    price_offer = data.get("price_offer", "")
    platform = data.get("platform", "instagram")

    try:
        cap, tags, vibe = caption_generator.generate_perfume_copy(
            product_name=product_name,
            volume_ml=volume_ml,
            scent_notes=scent_notes,
            price_offer=price_offer,
            platform=platform
        )
        return jsonify({
            "success": True,
            "caption": append_brand_footer(cap),
            "hashtags": tags,
            "sound_vibe": vibe
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/accounts")
def api_accounts():
    return jsonify(load_accounts())

@app.route("/api/accounts/connect-meta", methods=["POST"])
@app.route("/api/accounts/reconnect-meta", methods=["POST"])
def api_connect_meta():
    data = request.json or {}
    token = data.get("token", "").strip()
    if not token:
        return jsonify({"success": False, "error": "No token provided"}), 400

    try:
        uploader = MetaUploader(access_token=token)
        success, pages = uploader.get_user_pages()
        if not success or not pages:
            return jsonify({"success": False, "error": "Could not find any Facebook Pages associated with this token."}), 400

        matched_page = None
        for p in pages:
            if "jani" in p.get("name", "").lower():
                matched_page = p
                break
        if not matched_page:
            matched_page = pages[0]

        fb_page_id = matched_page["id"]
        page_token = matched_page.get("access_token", token)
        page_name = matched_page.get("name", "Facebook Page")

        ig_success, ig_data = uploader.get_instagram_account(fb_page_id)
        ig_id = ig_data.get("id", "") if ig_success else ""
        ig_username = ig_data.get("username", "official_janisperfume") if ig_success else ""

        config_manager.update(
            meta_access_token=page_token,
            facebook_page_id=fb_page_id,
            instagram_account_id=ig_id
        )

        acc = load_accounts()
        acc["facebook"] = {"connected": True, "page_name": page_name, "page_id": fb_page_id, "auth_type": "meta_graph_api"}
        acc["instagram"] = {"connected": bool(ig_id), "username": ig_username or "official_janisperfume", "id": ig_id, "auth_type": "meta_graph_api"}
        save_accounts(acc)

        return jsonify({
            "success": True,
            "message": f"Connected to Facebook Page '{page_name}' and Instagram '@{ig_username}'!"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/open-folder", methods=["POST"])
def api_open_folder():
    if IS_VERCEL:
        return jsonify({"success": False, "error": "Folder openers only available locally."})
    data = request.json or {}
    folder_type = data.get("folder", "insta")
    if folder_type == "insta":
        folder_path = config_manager.config.watch_folder_insta
    elif folder_type == "tiktok":
        folder_path = config_manager.config.watch_folder_tiktok
    else:
        folder_path = config_manager.config.watch_folder_facebook

    os.makedirs(folder_path, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(folder_path)
        return jsonify({"success": True, "path": folder_path})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/media/<path:filename>")
def api_media(filename):
    clean_name = os.path.basename(filename)
    # Security: block hidden files, system files, source code & database files
    blocked_exts = (".py", ".json", ".db", ".env", ".sqlite", ".bat", ".cmd", ".sh", ".exe")
    if clean_name.startswith(".") or any(clean_name.lower().endswith(ext) for ext in blocked_exts):
        return jsonify({"error": "Access denied"}), 403
    filename = clean_name
    search_dirs = [
        os.path.join(ROOT_DIR, "studio_uploads"),
        os.path.join(ROOT_DIR, "assets"),
        os.path.join(ROOT_DIR, "output"),
        os.path.join(ROOT_DIR, "watch_folders", "Ready_for_Instagram"),
        os.path.join(ROOT_DIR, "watch_folders", "Ready_for_Insta"),
        os.path.join(ROOT_DIR, "watch_folders", "Ready_for_Facebook"),
        os.path.join(ROOT_DIR, "watch_folders", "Ready_for_TikTok"),
        os.path.join(ROOT_DIR, "watch_folders_archive"),
        ROOT_DIR,
        config_manager.config.processed_folder,
        config_manager.config.watch_folder_insta,
        config_manager.config.watch_folder_facebook,
        config_manager.config.watch_folder_tiktok,
        config_manager.config.audio_library_folder,
        "/tmp/studio_uploads",
        "/tmp/processed_media",
        "/tmp/watch_folders/instagram",
        "/tmp/watch_folders/facebook",
        "/tmp/watch_folders/tiktok",
        "/tmp/audio_library"
    ]
    for d in search_dirs:
        if os.path.exists(d):
            full_path = os.path.join(d, filename)
            if os.path.exists(full_path):
                return send_from_directory(d, filename)
    return jsonify({"error": "File not found"}), 404

@app.route("/api/video/<path:filename>")
def api_video(filename):
    return api_media(filename)

@app.route("/api/posts/<int:post_id>/post-now", methods=["POST"])
def api_post_now(post_id):
    current_db = get_db()
    post = current_db.get_post(post_id) if current_db else None
    if not post:
        return jsonify({"success": False, "error": "Post not found"}), 404

    from app.modules.scheduler import execute_post_upload
    ok, rid, msg = execute_post_upload(post_id, db=current_db)
    if ok:
        return jsonify({"success": True, "message": f"Post #{post_id} published LIVE successfully!", "remote_id": rid})
    else:
        return jsonify({"success": False, "error": f"Upload failed: {msg}"}), 500

@app.route("/api/posts/<int:post_id>/delete", methods=["POST"])
def api_delete_post(post_id):
    current_db = get_db()
    if not current_db:
        return jsonify({"success": False}), 500
    post = current_db.get_post(post_id)
    if post:
        try:
            f_path = post.processed_path or post.file_path
            if f_path and not f_path.startswith("http") and not f_path.startswith("["):
                if os.path.exists(f_path):
                    os.remove(f_path)
            elif f_path and f_path.startswith("["):
                import json
                try:
                    for sub_f in json.loads(f_path):
                        if sub_f and not sub_f.startswith("http") and os.path.exists(sub_f):
                            os.remove(sub_f)
                except Exception:
                    pass
        except Exception as fe:
            logger.warning(f"Error cleaning local file for #{post_id}: {fe}")
    success = current_db.delete_post(post_id)
    try:
        from app.modules.cloud_queue import cloud_queue
        cloud_queue.delete_post(post_id)
    except Exception as cde:
        logger.warning(f"Cloud queue delete error: {cde}")
    return jsonify({"success": success})

@app.route("/api/posts/clear-failed", methods=["POST"])
def api_clear_failed():
    current_db = get_db()
    removed_db = 0
    if current_db:
        posts = current_db.get_posts(limit=200)
        for p in posts:
            if p.status == PostStatus.FAILED.value:
                current_db.delete_post(p.id)
                removed_db += 1
    from app.modules.cloud_queue import cloud_queue
    removed_cloud = cloud_queue.clear_failed()
    return jsonify({"success": True, "removed": max(removed_db, removed_cloud)})

@app.route("/api/cron/check-due", methods=["GET", "POST"])
def api_cron_check_due():
    current_db = get_db()
    from app.modules.cloud_queue import cloud_queue
    due_posts = cloud_queue.get_due_posts()
    logger.info(f"⏰ [Cron] Triggered! Found {len(due_posts)} due posts in cloud queue.")

    results = []
    from app.modules.scheduler import execute_post_upload

    for p in due_posts:
        pid = p.get("id")
        plat = p.get("target_platform", "instagram")
        try:
            cloud_queue.update_post_status(pid, "UPLOADING")
            success, remote_id, err = execute_post_upload(pid, db=current_db)
            results.append({
                "post_id": pid,
                "platform": plat,
                "success": success,
                "remote_id": remote_id,
                "error": err
            })
        except Exception as ex:
            logger.error(f"[Cron] Error publishing post #{pid}: {ex}")
            cloud_queue.update_post_status(pid, "FAILED", error_message=str(ex))
            results.append({"post_id": pid, "platform": plat, "success": False, "error": str(ex)})

    return jsonify({
        "success": True,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "processed_count": len(due_posts),
        "results": results
    })

@app.route("/api/calendar/restore", methods=["POST"])
def api_calendar_restore():
    """Restores cached posts from browser localStorage into current serverless container's SQLite."""
    data = request.json or {}
    cached_events = data.get("events", [])
    current_db = get_db()
    if not current_db or not cached_events:
        return jsonify({"success": False, "count": 0})

    restored_count = 0
    existing_posts = current_db.get_posts(limit=200)
    existing_ids = {p.id for p in existing_posts}

    for ev in cached_events:
        eid = ev.get("id")
        if eid and eid not in existing_ids:
            try:
                p_platform = ev.get("target_platform", "instagram")
                current_db.insert_post(
                    file_path=ev.get("file_path", ""),
                    file_hash=ev.get("file_hash", f"restored_{eid}_{p_platform}_{int(time.time()*1000)}"),
                    target_platform=p_platform,
                    media_type=ev.get("media_type", "image"),
                    status=ev.get("status", PostStatus.SCHEDULED.value)
                )
                current_db.update_post(
                    post_id=eid,
                    caption=ev.get("caption", ""),
                    hashtags=ev.get("hashtags", ""),
                    scheduled_time=ev.get("scheduled_time"),
                    status=ev.get("status", PostStatus.SCHEDULED.value),
                    remote_media_id=ev.get("remote_media_id"),
                    remote_url=ev.get("remote_url"),
                    error_message=ev.get("error_message")
                )
                restored_count += 1
            except Exception as ex:
                logger.warning(f"Error restoring post #{eid}: {ex}")

    return jsonify({"success": True, "restored_count": restored_count})

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        data = request.json or {}
        try:
            config_manager.update(**data)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    else:
        cfg = config_manager.config
        return jsonify({
            "brand_name": cfg.brand_name,
            "gemini_api_key": cfg.gemini_api_key,
            "gemini_model": cfg.gemini_model,
            "openai_api_key": cfg.openai_api_key,
            "openai_model": cfg.openai_model,
            "meta_access_token": cfg.meta_access_token,
            "r2_account_id": getattr(cfg, "r2_account_id", ""),
            "r2_bucket_name": getattr(cfg, "r2_bucket_name", ""),
            "r2_access_key_id": getattr(cfg, "r2_access_key_id", ""),
            "r2_secret_access_key": getattr(cfg, "r2_secret_access_key", ""),
            "r2_public_domain": getattr(cfg, "r2_public_domain", ""),
            "daily_limit_insta": cfg.daily_limit_insta,
            "daily_limit_facebook": cfg.daily_limit_facebook
        })

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """
    Handles Multi-Image Albums (1 to 12 pictures) or Single Video.
    Main Cover is placed at index 0. Pure images remain pure images.
    Supports Instant Live Post, Calendar Scheduled Post, and Auto-Pilot Queue.
    """
    try:
        uploaded_files = request.files.getlist("files") or request.files.getlist("file")
        if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ""):
            return jsonify({"success": False, "error": "No files selected"}), 400

        platform = request.form.get("platform", "instagram")
        caption = request.form.get("caption", "").strip()
        hashtags = request.form.get("hashtags", "").strip()
        schedule_mode = request.form.get("schedule_mode", "instant") # "instant", "calendar", "queue"
        scheduled_time = request.form.get("scheduled_time", "").strip()
        scheduled_time_utc = request.form.get("scheduled_time_utc", "").strip()
        main_index = int(request.form.get("main_index", 0))

        # Reorder so chosen cover is at index 0
        if 0 < main_index < len(uploaded_files):
            cover = uploaded_files.pop(main_index)
            uploaded_files.insert(0, cover)

        # Limit to 12 items
        uploaded_files = uploaded_files[:12]

        if platform == "all":
            platforms_to_save = ["instagram", "facebook"]
        else:
            platforms_to_save = [platform]

        # 1. Save uploaded files in a clean studio_uploads folder (NOT watch_folders to avoid watcher collision)
        upload_dir = "/tmp/studio_uploads" if IS_VERCEL else os.path.join(ROOT_DIR, "studio_uploads")
        os.makedirs(upload_dir, exist_ok=True)

        saved_file_paths = []
        for idx, file in enumerate(uploaded_files):
            fname = secure_filename(file.filename)
            if not fname:
                fname = f"media_{int(time.time())}_{idx}.jpg"
            allowed_exts = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".avi", ".webm"}
            f_ext = os.path.splitext(fname)[1].lower()
            if f_ext not in allowed_exts:
                return jsonify({"success": False, "error": f"Invalid file format '{f_ext}'. Allowed formats: JPG, PNG, WEBP, MP4, MOV, WEBM"}), 400
            unique_fname = f"{int(time.time())}_{idx}_{fname}"
            target_path = os.path.join(upload_dir, unique_fname)
            file.save(target_path)
            saved_file_paths.append(target_path)

        # 2. Upload media items to CDN ONCE (Shared by all selected platforms)
        p_paths = []
        for r_path in saved_file_paths:
            try:
                cdn_url = storage_service.upload_file(r_path)
                p_paths.append(cdn_url if cdn_url else r_path)
            except Exception as ue:
                logger.warning(f"CDN upload error for {r_path}: {ue}. Using local path.")
                p_paths.append(r_path)

        first_path = p_paths[0]
        is_image_ext = any(first_path.lower().endswith(x) for x in [".jpg", ".jpeg", ".png", ".webp"]) or ("iili.io" in first_path or "freeimage" in first_path or "uguu.se" in first_path)

        # 1. Multi-photo -> carousel
        # 2. Single image -> native image
        # 3. Video file -> video
        if len(p_paths) > 1:
            media_type = "carousel"
            stored_file_path = json.dumps(p_paths)
        elif is_image_ext:
            media_type = "image"
            stored_file_path = first_path
        else:
            media_type = "video"
            stored_file_path = first_path

        post_status = PostStatus.QUEUED.value
        post_sched_time = None

        if schedule_mode == "calendar" and (scheduled_time_utc or scheduled_time):
            post_status = PostStatus.SCHEDULED.value
            post_sched_time = scheduled_time_utc or scheduled_time
        elif schedule_mode == "instant":
            post_status = PostStatus.UPLOADING.value
        else:
            post_status = PostStatus.QUEUED.value

        final_caption = append_brand_footer(caption or f"🌸 Luxury Fragrance Experience from {config_manager.config.brand_name}!")
        final_hashtags = hashtags or "#JanisPerfume #Luxury #Fragrance #Trending"

        current_db = get_db()
        created_post_ids = []

        for p in platforms_to_save:
            if current_db:
                base_hash = current_db.calculate_file_hash(saved_file_paths[0])
                f_hash = f"{base_hash}_{p}_{int(time.time()*1000)}"
                post_id = current_db.insert_post(
                    file_path=stored_file_path,
                    file_hash=f_hash,
                    target_platform=p,
                    media_type=media_type
                )
                if post_id:
                    current_db.update_post(
                        post_id=post_id,
                        caption=final_caption,
                        hashtags=final_hashtags,
                        scheduled_time=post_sched_time,
                        status=post_status
                    )
                    created_post_ids.append(post_id)

        # Sync scheduled posts to persistent CloudQueue (guarantees persistence across Vercel cold restarts)
        try:
            from app.modules.cloud_queue import cloud_queue
            for idx, pid in enumerate(created_post_ids):
                plat = platforms_to_save[idx] if idx < len(platforms_to_save) else platforms_to_save[0]
                cloud_queue.add_scheduled_post({
                    "id": pid,
                    "target_platform": plat,
                    "caption": final_caption,
                    "hashtags": final_hashtags,
                    "scheduled_time": post_sched_time,
                    "media_type": media_type,
                    "media_urls": p_paths,
                    "status": post_status,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
        except Exception as cqe:
            logger.error(f"[api_upload] CloudQueue sync error: {cqe}")

        # Facebook Native Cloud Scheduling (Meta Page API schedules directly on Meta servers)
        if schedule_mode == "calendar" and post_sched_time and "facebook" in platforms_to_save:
            try:
                from app.modules.scheduler import parse_scheduled_datetime
                sched_dt = parse_scheduled_datetime(post_sched_time)
                if sched_dt:
                    diff_seconds = int(sched_dt.timestamp() - time.time())
                    if 600 <= diff_seconds <= 6480000:
                        fb_pid = None
                        for pid in created_post_ids:
                            p_rec = current_db.get_post(pid) if current_db else None
                            if p_rec and p_rec.target_platform == "facebook":
                                fb_pid = pid
                                break
                        if fb_pid:
                            from app.modules.uploaders.meta_uploader import MetaUploader
                            mu = MetaUploader()
                            fb_unix = int(sched_dt.timestamp())
                            if media_type == "carousel" or len(p_paths) > 1:
                                fb_ok, fb_id, fb_url, fb_err = mu.upload_facebook_carousel(
                                    photo_paths_or_urls=p_paths,
                                    caption=final_caption,
                                    hashtags=final_hashtags,
                                    scheduled_time=fb_unix
                                )
                            elif media_type == "image":
                                fb_ok, fb_id, fb_url, fb_err = mu.upload_facebook_photo(
                                    photo_path_or_url=p_paths[0],
                                    caption=final_caption,
                                    hashtags=final_hashtags,
                                    scheduled_time=fb_unix
                                )
                            if fb_ok:
                                logger.info(f"🚀 [Facebook Native] Post #{fb_pid} successfully scheduled on Meta servers! Remote ID: {fb_id}")
                                if current_db:
                                    current_db.update_post(fb_pid, status=PostStatus.SCHEDULED.value, remote_media_id=fb_id, remote_url=fb_url)
                                try:
                                    from app.modules.cloud_queue import cloud_queue
                                    cloud_queue.update_post_status(fb_pid, "SCHEDULED", remote_id=fb_id, remote_url=fb_url)
                                except Exception:
                                    pass
            except Exception as fb_sched_ex:
                logger.warning(f"Facebook native schedule warning: {fb_sched_ex}")

        # 3. Background execution for instant uploads or due posts (Non-blocking!)
        due_now_pids = []
        for pid in created_post_ids:
            if schedule_mode == "instant":
                due_now_pids.append(pid)
            elif schedule_mode == "calendar" and post_sched_time:
                from app.modules.scheduler import is_post_due
                if is_post_due(post_sched_time):
                    due_now_pids.append(pid)

        if due_now_pids:
            if IS_VERCEL:
                for pid in due_now_pids:
                    try:
                        from app.modules.scheduler import execute_post_upload
                        execute_post_upload(pid, db=current_db)
                    except Exception as ex:
                        logger.error(f"[api_upload] Vercel upload error for #{pid}: {ex}")
            else:
                def _bg_execute(pids, d):
                    for pid in pids:
                        try:
                            from app.modules.scheduler import execute_post_upload
                            execute_post_upload(pid, db=d)
                        except Exception as ex:
                            logger.error(f"[api_upload] BG upload error for #{pid}: {ex}")

                threading.Thread(target=_bg_execute, args=(list(due_now_pids), current_db), daemon=True).start()

        created_events = []
        if current_db:
            for pid in created_post_ids:
                p_rec = current_db.get_post(pid)
                if p_rec:
                    d = p_rec.__dict__.copy()
                    d["dt_info"] = format_post_datetime(p_rec.scheduled_time or p_rec.created_at)
                    d["scheduled_countdown"] = d["dt_info"]["countdown"]
                    created_events.append(d)

        msg = f"Post created for {platform.upper()} with {len(uploaded_files)} media item(s)!"
        if schedule_mode == "calendar":
            msg += f" Scheduled for {scheduled_time}."
        elif schedule_mode == "instant":
            msg += " Instant live upload initiated!"

        return jsonify({"success": True, "post_ids": created_post_ids, "events": created_events, "message": msg})
    except Exception as e:
        logger.error(f"[api_upload] Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("================================================================")
    print(" 🚀 ReelPilot Studio v3.6 (Multi-Media & Worldwide Music Hub)")
    print(" 🌐 Localhost Link: http://localhost:5000")
    print(" 🌐 Localhost IP:   http://127.0.0.1:5000")
    print("================================================================")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
