"""
Durable storage for the Facebook connection on serverless hosts.

Vercel's filesystem is ephemeral: config.json lives in /tmp and is wiped on the
next cold start. Without this module every redeploy or idle period would lose the
Meta login and force a reconnect, which is exactly the problem this whole feature
exists to remove.

Two backends, picked automatically at runtime:

1. Vercel Blob (preferred) - a private blob store attached to the project. The
   runtime receives BLOB_READ_WRITE_TOKEN plus BLOB_STORE_BASE_URL, so the JSON
   is written with one PUT and read with one authenticated GET. Nothing to
   configure by hand.
2. GitHub (fallback) - when GITHUB_TOKEN is present the connection is mirrored
   into data/meta_state.json of this repository.

Locally nothing changes: config.json remains the source of truth.
"""
import base64
import json
import os
import threading
import time
from typing import Any, Dict

import requests

from app.utils.logger import logger

STATE_REPO = os.environ.get("STATE_GITHUB_REPO", "ashirarif8787-byte/reelpilot-studio")
STATE_PATH = os.environ.get("STATE_GITHUB_PATH", "data/meta_state.json")
STATE_BRANCH = os.environ.get("STATE_GITHUB_BRANCH", "main")

BLOB_PATH = os.environ.get("STATE_BLOB_PATH", "reelpilot/meta_state.json")
BLOB_BASE_URL = os.environ.get("BLOB_STORE_BASE_URL", "").strip().rstrip("/")
BLOB_UPLOAD_URL = "https://blob.vercel-storage.com"

# Only the connection itself travels; brand and AI settings stay per deployment.
META_FIELDS = (
    "meta_access_token",
    "meta_user_token",
    "meta_user_token_expires_at",
    "meta_data_access_expires_at",
    "meta_page_token_expires_at",
    "meta_page_name",
    "meta_ig_username",
    "meta_connected_at",
    "meta_needs_reauth",
    "meta_last_error",
    "meta_pages",
    "facebook_page_id",
    "instagram_account_id",
)

_last_saved = {"hash": None}
_lock = threading.Lock()


def _token() -> str:
    return os.environ.get("GITHUB_TOKEN", "").strip()


def _blob_token() -> str:
    return os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()


def blob_ready() -> bool:
    return bool(_blob_token()) and bool(BLOB_BASE_URL)


def backend() -> str:
    """Which durable backend this deployment will use."""
    if blob_ready():
        return "blob"
    if _token():
        return "github"
    return "none"


def is_enabled() -> bool:
    """Serverless (persistent config needed) and a place to store it."""
    return bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV")) and backend() != "none"


def snapshot(cfg: Any) -> Dict[str, Any]:
    return {name: getattr(cfg, name, None) for name in META_FIELDS}


# --------------------------------------------------------------------------
# Vercel Blob
# --------------------------------------------------------------------------
def _blob_headers() -> Dict[str, str]:
    return {"authorization": f"Bearer {_blob_token()}"}


def _blob_put(blob: str) -> bool:
    if not blob_ready():
        return False
    headers = {
        "authorization": f"Bearer {_blob_token()}",
        "x-vercel-blob-access": "private",
        "x-add-random-suffix": "0",
        "x-allow-overwrite": "1",
        "x-content-type": "application/json",
        "x-cache-control-max-age": "60",
    }
    try:
        resp = requests.put(
            f"{BLOB_UPLOAD_URL}/{BLOB_PATH}",
            data=blob.encode("utf-8"),
            headers=headers,
            timeout=12,
        )
        if resp.status_code in (200, 201):
            logger.info("[MetaState] Facebook connection saved to Vercel Blob.")
            return True
        logger.warning(f"[MetaState] Blob save failed HTTP {resp.status_code}: {resp.text[:160]}")
    except Exception as exc:
        logger.warning(f"[MetaState] Blob save error: {exc}")
    return False


def _blob_load() -> Dict[str, Any]:
    if not blob_ready():
        return {}
    try:
        # Bypass the blob CDN cache: a stale read here would show the account as
        # disconnected right after it was connected.
        cb = f"{int(time.time() * 1000)}-{os.urandom(3).hex()}"
        resp = requests.get(f"{BLOB_BASE_URL}/{BLOB_PATH}?v={cb}", headers=_blob_headers(), timeout=8)
        if resp.status_code == 404:
            logger.info("[MetaState] No stored Facebook connection in Vercel Blob yet.")
            return {}
        if resp.status_code != 200:
            logger.warning(f"[MetaState] Blob load failed HTTP {resp.status_code}")
            return {}
        data = resp.json()
        if isinstance(data, dict):
            logger.info("[MetaState] Facebook connection restored from Vercel Blob.")
            return data
    except Exception as exc:
        logger.warning(f"[MetaState] Blob load error: {exc}")
    return {}


# --------------------------------------------------------------------------
# GitHub (fallback)
# --------------------------------------------------------------------------
def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ReelPilot-MetaState",
    }


def _github_load() -> Dict[str, Any]:
    if not _token():
        return {}
    try:
        url = f"https://api.github.com/repos/{STATE_REPO}/contents/{STATE_PATH}"
        resp = requests.get(url, headers=_headers(), params={"ref": STATE_BRANCH}, timeout=8)
        if resp.status_code == 404:
            logger.info("[MetaState] No stored Facebook connection yet.")
            return {}
        if resp.status_code != 200:
            logger.warning(f"[MetaState] Load failed HTTP {resp.status_code}")
            return {}
        payload = resp.json()
        decoded = base64.b64decode(payload.get("content", "")).decode("utf-8")
        data = json.loads(decoded)
        if isinstance(data, dict):
            logger.info("[MetaState] Facebook connection restored from durable storage.")
            return data
    except Exception as exc:
        logger.warning(f"[MetaState] Load error: {exc}")
    return {}


def _github_save(blob: str) -> None:
    try:
        url = f"https://api.github.com/repos/{STATE_REPO}/contents/{STATE_PATH}"
        current = requests.get(url, headers=_headers(), params={"ref": STATE_BRANCH}, timeout=8)
        sha = current.json().get("sha") if current.status_code == 200 else None
        body = {
            "message": "chore(meta): persist Facebook connection",
            "content": base64.b64encode(blob.encode("utf-8")).decode("utf-8"),
            "branch": STATE_BRANCH,
        }
        if sha:
            body["sha"] = sha
        resp = requests.put(url, headers=_headers(), json=body, timeout=12)
        if resp.status_code in (200, 201):
            logger.info("[MetaState] Facebook connection saved for future cold starts.")
        else:
            logger.warning(f"[MetaState] Save failed HTTP {resp.status_code}: {resp.text[:160]}")
    except Exception as exc:
        logger.warning(f"[MetaState] Save error: {exc}")


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def load_meta() -> Dict[str, Any]:
    """Fetch the stored connection, or an empty dict when there is none."""
    if not is_enabled():
        return {}
    data = _blob_load()
    if data:
        return data
    return _github_load()


def save_meta(cfg: Any) -> bool:
    """Persist the connection in the background; failures never break publishing."""
    if not is_enabled():
        return False
    data = snapshot(cfg)
    blob = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)

    with _lock:
        if _last_saved["hash"] == hash(blob):
            return True
        _last_saved["hash"] = hash(blob)

    def _push():
        if _blob_put(blob):
            return
        _github_save(blob)

    threading.Thread(target=_push, daemon=True).start()
    return True
