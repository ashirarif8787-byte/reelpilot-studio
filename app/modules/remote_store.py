"""
Durable storage for the Facebook connection on serverless hosts.

Vercel's filesystem is ephemeral: config.json lives in /tmp and is wiped on the
next cold start. Without this module every redeploy or idle period would lose the
Meta login and force a reconnect, which is exactly the problem this whole feature
exists to remove.

When GITHUB_TOKEN is available (Vercel environment variable) the Meta connection
is mirrored into data/meta_state.json of this repository and restored at startup.
Locally nothing changes: config.json remains the source of truth.
"""
import base64
import json
import os
import threading
from typing import Any, Dict

import requests

from app.utils.logger import logger

STATE_REPO = os.environ.get("STATE_GITHUB_REPO", "ashirarif8787-byte/reelpilot-studio")
STATE_PATH = os.environ.get("STATE_GITHUB_PATH", "data/meta_state.json")
STATE_BRANCH = os.environ.get("STATE_GITHUB_BRANCH", "main")

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


def is_enabled() -> bool:
    """Serverless (persistent config needed) and a token to store it with."""
    return bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV")) and bool(_token())


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ReelPilot-MetaState",
    }


def snapshot(cfg: Any) -> Dict[str, Any]:
    return {name: getattr(cfg, name, None) for name in META_FIELDS}


def load_meta() -> Dict[str, Any]:
    """Fetch the stored connection, or an empty dict when there is none."""
    if not is_enabled():
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

    threading.Thread(target=_push, daemon=True).start()
    return True
