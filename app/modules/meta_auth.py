"""
Facebook Login (OAuth) + automatic Meta token lifecycle.

Why this module exists
----------------------
A Meta access token is never "permanent" for a human account. A long-lived Page
token carries no expiry date, but Meta silently invalidates it when the password
changes, the app is removed, the page role is taken away, or Meta flags the
session for security. Pasting a token by hand therefore always breaks eventually
(error code 190 / subcode 460 is exactly that case).

This module makes the app repair itself instead:
  1. "Connect with Facebook" (OAuth dialog)      -> short-lived user token
  2. short-lived -> long-lived user token (~60d) -> fb_exchange_token
  3. long-lived user token -> Page token + Page ID + Instagram account ID
  4. token rejected (190/463/467)                -> rebuild Page token from the
                                                    stored long-lived user token
  5. only when the user token itself is gone     -> one-click "Reconnect"

Nothing here needs the user to copy an access token by hand.
"""
import os
import time
import secrets
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

import requests

from app.config import config_manager
from app.utils.logger import logger

GRAPH_VERSION = "v19.0"
GRAPH = f"https://graph.facebook.com/{GRAPH_VERSION}"
OAUTH_DIALOG_URL = f"https://www.facebook.com/{GRAPH_VERSION}/dialog/oauth"

# Permissions needed to publish to a Page and to its linked Instagram account.
DEFAULT_SCOPES = [
    "pages_show_list",
    "pages_manage_posts",
    "pages_read_engagement",
    "instagram_basic",
    "instagram_content_publish",
]

PAGE_FIELDS = "id,name,access_token,instagram_business_account{id,username}"

# Meta auth failure codes: 190 = invalid token, 463/467 = expired/session invalid.
TOKEN_ERROR_CODES = {190, 463, 467}
# 458 app removed, 459 user checkpointed, 460 password changed, 464 unconfirmed user
TOKEN_ERROR_SUBCODES = {458, 459, 460, 463, 464, 467}


class MetaAuthError(Exception):
    """Raised when the Facebook login handshake or token exchange cannot complete."""


def format_meta_error(payload: Dict[str, Any], fallback: str = "Facebook rejected the request") -> str:
    """Meta error -> one readable line that keeps the code/subcode for debugging."""
    err = (payload or {}).get("error") or {}
    message = err.get("message") or (payload or {}).get("error_description") or fallback
    bits = []
    if err.get("code") is not None:
        bits.append(f"code {err.get('code')}")
    if err.get("error_subcode"):
        bits.append(f"subcode {err.get('error_subcode')}")
    if err.get("type"):
        bits.append(str(err.get("type")))
    return f"{message} ({', '.join(bits)})" if bits else str(message)


TOKEN_SUBCODE_HINTS = {
    458: "the app was removed from the account",
    459: "the account needs a Facebook security check",
    460: "the password changed or Facebook invalidated the session",
    463: "the token expired",
    464: "the Facebook account is unconfirmed",
    467: "the token is invalid",
}


# ---------------------------------------------------------------------------
# App credentials
# ---------------------------------------------------------------------------
def _cfg():
    return config_manager.config


def app_id() -> str:
    # .env wins, so a rotated/updated value is always the one used.
    return (os.getenv("META_APP_ID", "") or _cfg().meta_app_id or "").strip()


def app_secret() -> str:
    return (os.getenv("META_APP_SECRET", "") or _cfg().meta_app_secret or "").strip()


def is_configured() -> bool:
    """True when the Meta App ID + App Secret are available (needed for OAuth)."""
    return bool(app_id() and app_secret())


def app_access_token() -> str:
    return f"{app_id()}|{app_secret()}"


def resolve_redirect_uri(base_url: str = "") -> str:
    """
    The OAuth callback URL. Priority: META_REDIRECT_URI env -> the running host.
    The exact same string must be whitelisted in the Meta app dashboard.
    """
    configured = os.getenv("META_REDIRECT_URI", "").strip()
    if configured:
        return configured
    if not base_url:
        return ""
    # Keep localhost and 127.0.0.1 from fighting each other: Meta matches exactly.
    url = base_url.replace("127.0.0.1", "localhost").replace("0.0.0.0", "localhost")
    # Accept a bare origin too, so callers cannot print a half URL by mistake.
    if urllib.parse.urlparse(url).path in ("", "/"):
        url = url.rstrip("/") + "/auth/facebook/callback"
    return url


def new_state() -> str:
    return secrets.token_urlsafe(24)


def build_login_url(redirect_uri: str, state: str, scopes: Optional[List[str]] = None) -> str:
    """Facebook Login dialog URL the browser should be sent to."""
    if not is_configured():
        raise MetaAuthError(
            "Meta App ID / App Secret missing. Add META_APP_ID and META_APP_SECRET to .env."
        )
    params = {
        "client_id": app_id(),
        "redirect_uri": redirect_uri,
        "state": state,
        "response_type": "code",
        "scope": ",".join(scopes or DEFAULT_SCOPES),
    }
    return f"{OAUTH_DIALOG_URL}?{urllib.parse.urlencode(params)}"


# ---------------------------------------------------------------------------
# Low level Graph helpers
# ---------------------------------------------------------------------------
def _graph_get(path: str, params: Dict[str, Any], timeout: int = 15) -> requests.Response:
    url = f"{GRAPH}/{path.lstrip('/')}"
    try:
        return requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as exc:
        raise MetaAuthError(f"Network error while contacting Meta: {exc}")


def _json(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except ValueError:
        raise MetaAuthError(f"Meta returned an unreadable response (HTTP {resp.status_code}).")


def exchange_code(code: str, redirect_uri: str) -> str:
    """Step 1: authorization code -> short-lived user token."""
    if not is_configured():
        raise MetaAuthError("Meta App ID / App Secret missing in .env.")
    data = _json(_graph_get("oauth/access_token", {
        "client_id": app_id(),
        "client_secret": app_secret(),
        "redirect_uri": redirect_uri,
        "code": code,
    }))
    if "access_token" not in data:
        raise MetaAuthError(format_meta_error(data, "Facebook did not return a token."))
    return data["access_token"]


def extend_to_long_lived(user_token: str) -> Tuple[str, int]:
    """Step 2: short-lived user token -> long-lived user token (~60 days)."""
    if not is_configured():
        raise MetaAuthError("Meta App ID / App Secret missing in .env.")
    data = _json(_graph_get("oauth/access_token", {
        "grant_type": "fb_exchange_token",
        "client_id": app_id(),
        "client_secret": app_secret(),
        "fb_exchange_token": user_token,
    }))
    if "access_token" not in data:
        raise MetaAuthError(format_meta_error(data, "Could not extend the Facebook token."))
    return data["access_token"], int(data.get("expires_in") or 0)


def fetch_pages(user_token: str) -> List[Dict[str, Any]]:
    """Step 3a: every Page the user administers, with its own Page token."""
    params = {"access_token": user_token, "fields": PAGE_FIELDS, "limit": 100}
    pages: List[Dict[str, Any]] = []
    url: Optional[str] = f"{GRAPH}/me/accounts"
    for _ in range(5):  # follow paging, bounded
        if not url:
            break
        try:
            resp = requests.get(url, params=params, timeout=20)
        except requests.RequestException as exc:
            raise MetaAuthError(f"Network error while fetching Facebook Pages: {exc}")
        data = _json(resp)
        if "error" in data:
            raise MetaAuthError(format_meta_error(data, "Could not read Facebook Pages."))
        pages.extend(data.get("data") or [])
        url = (data.get("paging") or {}).get("next")
        params = {}  # the "next" URL already carries the query string
    return pages


def fetch_page_identity(token: str) -> Dict[str, Any]:
    """For a Page token: which Page does it belong to?"""
    data = _json(_graph_get("me", {"access_token": token, "fields": "id,name"}))
    if "error" in data:
        raise MetaAuthError(format_meta_error(data, "Could not identify the Facebook Page."))
    return data


def fetch_instagram(page_id: str, token: str) -> Dict[str, Any]:
    """Step 3b: the Instagram business account linked to a Page."""
    if not page_id:
        return {}
    data = _json(_graph_get(page_id, {
        "access_token": token,
        "fields": "instagram_business_account{id,username}",
    }))
    if "error" in data:
        logger.warning(f"[MetaAuth] Instagram lookup failed for Page {page_id}: {data['error'].get('message')}")
        return {}
    return data.get("instagram_business_account") or {}


def debug_token(token: str) -> Dict[str, Any]:
    """
    Meta's own verdict on a token: validity, type, real expiry timestamps.
    Falls back to a /me call when the app credentials are missing.
    """
    token = (token or "").strip()
    if not token:
        return {"is_valid": False, "error": {"message": "No token stored"}}
    if not is_configured():
        data = _json(_graph_get("me", {"access_token": token, "fields": "id,name"}))
        if "error" in data:
            return {"is_valid": False, "error": data["error"]}
        return {"is_valid": True, "type": "UNKNOWN", "expires_at": 0, "data_access_expires_at": 0}
    data = _json(_graph_get("debug_token", {
        "input_token": token,
        "access_token": app_access_token(),
    }))
    return data.get("data") or {"is_valid": False, "error": data.get("error", {})}


def token_info(token: str) -> Dict[str, Any]:
    raw = debug_token(token)
    err = raw.get("error") or {}
    return {
        "is_valid": bool(raw.get("is_valid")),
        "type": (raw.get("type") or "").upper(),
        "expires_at": int(raw.get("expires_at") or 0),
        "data_access_expires_at": int(raw.get("data_access_expires_at") or 0),
        "scopes": raw.get("scopes") or [],
        "error_code": err.get("code"),
        "error_subcode": err.get("error_subcode"),
        "error_message": err.get("message", ""),
    }


def is_token_error(payload: Dict[str, Any]) -> bool:
    """True when a Graph error means the token itself is dead (not a content error)."""
    err = (payload or {}).get("error") or {}
    code = err.get("code")
    subcode = err.get("error_subcode")
    message = (err.get("message") or "").lower()
    if code in TOKEN_ERROR_CODES:
        return True
    if subcode in TOKEN_ERROR_SUBCODES:
        return True
    return "access token" in message or "session has expired" in message


# ---------------------------------------------------------------------------
# Persist + connect
# ---------------------------------------------------------------------------
def _mark_needs_reauth(message: str) -> None:
    config_manager.update(
        meta_needs_reauth=True,
        meta_last_error=(message or "")[:500],
    )
    clear_health_cache()
    _persist_remote()
    logger.warning(f"[MetaAuth] Reconnect required: {message}")


def _pick_page(pages: List[Dict[str, Any]], preferred_id: str = "", brand_name: str = "") -> Optional[Dict[str, Any]]:
    if not pages:
        return None
    preferred_id = (preferred_id or "").strip()
    if preferred_id:
        for page in pages:
            if str(page.get("id")) == preferred_id:
                return page
    brand = (brand_name or "").split("'")[0].strip().lower()
    if brand:
        for page in pages:
            if brand in (page.get("name") or "").lower():
                return page
    # Prefer a Page that actually has an Instagram account linked.
    for page in pages:
        if page.get("instagram_business_account"):
            return page
    return pages[0]


def connect(user_token: str, preferred_page_id: str = "") -> Dict[str, Any]:
    """
    Turn any Facebook token into a ready-to-use Page + Instagram connection.

    Accepts either a user token (normal login flow: extended to long-lived first,
    then Pages are listed) or an already-pasted Page token.
    """
    user_token = (user_token or "").strip()
    if not user_token:
        raise MetaAuthError("Facebook did not return an access token.")

    info = token_info(user_token)
    if not info["is_valid"]:
        hint = TOKEN_SUBCODE_HINTS.get(info.get("error_subcode") or 0)
        raise MetaAuthError(
            format_meta_error({"error": {
                "message": info.get("error_message") or "Facebook rejected this token",
                "code": info.get("error_code"),
                "error_subcode": info.get("error_subcode"),
            }}, "Facebook rejected this token")
            + (f" — {hint}, press Connect again" if hint else "")
        )

    cfg = _cfg()
    long_lived_user_token = ""
    user_expires_at = info["expires_at"]
    data_access_expires_at = info["data_access_expires_at"]
    candidate_pages: List[Dict[str, Any]] = []

    if info["type"] == "PAGE":
        # A Page token pasted directly: it is already the publishing credential.
        page_token = user_token
        identity = fetch_page_identity(page_token)
        page_id = str(identity.get("id") or "")
        page_name = identity.get("name") or ""
        instagram = fetch_instagram(page_id, page_token)
    else:
        # 1) short-lived -> long-lived user token (this is the step that was missing)
        try:
            long_lived_user_token, expires_in = extend_to_long_lived(user_token)
            if expires_in:
                user_expires_at = int(time.time() + expires_in)
        except MetaAuthError as exc:
            logger.warning(f"[MetaAuth] Could not extend token, using it as-is: {exc}")
            long_lived_user_token = user_token

        extended = token_info(long_lived_user_token)
        if extended.get("expires_at"):
            user_expires_at = extended["expires_at"]
        if extended.get("data_access_expires_at"):
            data_access_expires_at = extended["data_access_expires_at"]

        # 2) long-lived user token -> Page token (has no expiry of its own)
        pages = fetch_pages(long_lived_user_token)
        candidate_pages = pages
        page = _pick_page(pages, preferred_page_id or cfg.facebook_page_id, cfg.brand_name)
        if not page:
            raise MetaAuthError(
                "No Facebook Page found for this login. Make sure your account is an admin of the Page."
            )
        page_token = page.get("access_token") or long_lived_user_token
        page_id = str(page.get("id") or "")
        page_name = page.get("name") or ""
        instagram = page.get("instagram_business_account") or fetch_instagram(page_id, page_token)

    page_info = token_info(page_token)
    if not page_info.get("is_valid"):
        raise MetaAuthError(
            format_meta_error({"error": {
                "message": page_info.get("error_message") or "The Facebook Page token could not be validated",
                "code": page_info.get("error_code"),
                "error_subcode": page_info.get("error_subcode"),
            }})
        )

    ig_id = str((instagram or {}).get("id") or "")
    ig_username = (instagram or {}).get("username") or ""

    # Every Page this login can publish to, each with the Instagram account that
    # is actually linked to it. A Page without Instagram stays publishable to Facebook.
    records: List[Dict[str, Any]] = []
    source_pages = candidate_pages or [{
        "id": page_id,
        "name": page_name,
        "access_token": page_token,
        "instagram_business_account": instagram,
    }]
    for candidate in source_pages:
        record_page_id = str(candidate.get("id") or "")
        if not record_page_id:
            continue
        record_token = candidate.get("access_token") or page_token
        record_ig = candidate.get("instagram_business_account") or {}
        if not record_ig and record_page_id != page_id:
            try:
                record_ig = fetch_instagram(record_page_id, record_token)
            except Exception as exc:
                logger.warning(f"[MetaAuth] Instagram lookup skipped for Page {record_page_id}: {exc}")
                record_ig = {}
        records.append({
            "page_id": record_page_id,
            "page_name": candidate.get("name") or "",
            "page_token": record_token,
            "ig_id": str((record_ig or {}).get("id") or ""),
            "ig_username": (record_ig or {}).get("username") or "",
        })

    config_manager.update(
        meta_access_token=page_token,
        meta_user_token=long_lived_user_token,
        meta_user_token_expires_at=user_expires_at or 0,
        meta_data_access_expires_at=(
            data_access_expires_at or page_info.get("data_access_expires_at") or 0
        ),
        meta_page_token_expires_at=page_info.get("expires_at") or 0,
        facebook_page_id=page_id,
        instagram_account_id=ig_id,
        meta_page_name=page_name,
        meta_ig_username=ig_username,
        meta_pages=records,
        meta_connected_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        meta_needs_reauth=False,
        meta_last_error="",
    )

    clear_health_cache()
    _persist_remote()
    logger.info(
        f"✅ [MetaAuth] Connected Page '{page_name}' ({page_id})"
        + (f" + Instagram @{ig_username}" if ig_username else "")
        + f". {len(records)} Page(s) available. Long-lived login stored for automatic recovery."
    )
    return {
        "page_id": page_id,
        "page_name": page_name,
        "instagram_id": ig_id,
        "instagram_username": ig_username,
        "user_token_expires_at": user_expires_at or 0,
        "data_access_expires_at": data_access_expires_at or 0,
        "page_token_expires_at": page_info.get("expires_at") or 0,
        "pages": records,
        "page_count": len(records),
    }


def _persist_remote() -> None:
    """Mirror the connection to durable storage on serverless hosts."""
    try:
        from app.modules.remote_store import save_meta
        save_meta(config_manager.config)
    except Exception as exc:
        logger.warning(f"[MetaAuth] Durable state unavailable: {exc}")


def pages_list() -> List[Dict[str, Any]]:
    """Connected Pages for the UI, with the active one flagged."""
    cfg = _cfg()
    active = str(cfg.facebook_page_id or "")
    out: List[Dict[str, Any]] = []
    for record in (cfg.meta_pages or []):
        page_id = str(record.get("page_id") or "")
        out.append({
            "page_id": page_id,
            "page_name": record.get("page_name") or "",
            "ig_id": record.get("ig_id") or "",
            "ig_username": record.get("ig_username") or "",
            "has_instagram": bool(record.get("ig_id")),
            "active": page_id == active,
        })
    return out


def activate_page(page_id: str) -> Dict[str, Any]:
    """Switch publishing to another connected Page (and its Instagram account)."""
    page_id = str(page_id or "").strip()
    cfg = _cfg()
    for record in (cfg.meta_pages or []):
        if str(record.get("page_id")) == page_id:
            config_manager.update(
                facebook_page_id=page_id,
                instagram_account_id=record.get("ig_id") or "",
                meta_page_name=record.get("page_name") or "",
                meta_ig_username=record.get("ig_username") or "",
                meta_access_token=record.get("page_token") or cfg.meta_access_token,
                meta_needs_reauth=False,
                meta_last_error="",
            )
            clear_health_cache()
            _persist_remote()
            logger.info(f"[MetaAuth] Active Page switched to '{record.get('page_name')}' ({page_id}).")
            return dict(record, active=True)
    raise MetaAuthError(
        f"Page {page_id} is not in the connected list. Connect with Facebook again or refresh the Pages."
    )


def refresh_pages() -> Dict[str, Any]:
    """Re-read every Page + Instagram account from Meta using the stored login."""
    cfg = _cfg()
    user_token = (cfg.meta_user_token or "").strip()
    if not user_token:
        raise MetaAuthError("No Facebook login stored. Press 'Connect with Facebook' once.")
    info = token_info(user_token)
    if not info["is_valid"]:
        raise MetaAuthError("The stored Facebook login is no longer valid. Press 'Reconnect'.")
    summary = connect(user_token, preferred_page_id=cfg.facebook_page_id)
    logger.info(f"[MetaAuth] Page list refreshed: {summary.get('page_count', 0)} Page(s).")
    return summary


def try_recover() -> bool:
    """
    Rebuild the Page token from the stored long-lived Facebook login.
    Returns True when a fresh, working Page token was written to config.
    """
    cfg = _cfg()
    user_token = (cfg.meta_user_token or "").strip()
    if not user_token:
        _mark_needs_reauth(
            "Facebook token was invalidated by Meta (password change, app removed or security check). "
            "Press 'Connect with Facebook' once — after that the app keeps it alive by itself."
        )
        return False

    info = token_info(user_token)
    if not info["is_valid"]:
        reason = info.get("error_message") or "Facebook invalidated the session"
        _mark_needs_reauth(
            f"Facebook login was invalidated ({reason}). Press 'Reconnect' once — "
            "after that the app keeps the connection alive by itself."
        )
        return False

    try:
        connect(user_token, preferred_page_id=cfg.facebook_page_id)
    except Exception as exc:
        _mark_needs_reauth(str(exc))
        return False

    logger.info("🔄 [MetaAuth] Page token rebuilt automatically — no manual token needed.")
    return True


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
def days_left(timestamp: int) -> Optional[int]:
    """Whole days until a unix timestamp; None when there is no fixed expiry."""
    try:
        timestamp = int(timestamp or 0)
    except (TypeError, ValueError):
        timestamp = 0
    if timestamp <= 0:
        return None
    return max(0, int((timestamp - time.time()) // 86400))


def _empty_health(message: str, needs_reauth: bool = True) -> Dict[str, Any]:
    cfg = _cfg()
    return {
        "connected": False,
        "status": "NOT_CONNECTED" if needs_reauth else "ERROR",
        "needs_reauth": needs_reauth,
        "message": message,
        "days_left": None,
        "expires_at": 0,
        "data_access_expires_at": 0,
        "facebook": {
            "connected": False,
            "name": cfg.meta_page_name or cfg.brand_name or "Not Connected",
            "id": cfg.facebook_page_id or "",
        },
        "instagram": {
            "connected": False,
            "username": cfg.meta_ig_username or "Not Connected",
            "id": cfg.instagram_account_id or "",
        },
        "app_configured": is_configured(),
        "pages": pages_list(),
        "active_page_id": cfg.facebook_page_id or "",
    }


# Short-lived cache so the 45s dashboard poll does not hit Meta every time.
_HEALTH_CACHE: Dict[str, Any] = {"at": 0.0, "data": None}
HEALTH_CACHE_SECONDS = 60


def clear_health_cache() -> None:
    _HEALTH_CACHE["at"] = 0.0
    _HEALTH_CACHE["data"] = None


def health(check_connection: bool = True) -> Dict[str, Any]:
    """
    Real connection state for the dashboard, including how many days remain and
    whether the user must press "Reconnect". Attempts a silent auto-recovery first.
    """
    if check_connection:
        cached = _HEALTH_CACHE["data"]
        if cached is not None and (time.time() - _HEALTH_CACHE["at"]) < HEALTH_CACHE_SECONDS:
            return dict(cached)

    result = _health_uncached(check_connection)
    if check_connection:
        _HEALTH_CACHE["at"] = time.time()
        _HEALTH_CACHE["data"] = dict(result)
    return result


def _health_uncached(check_connection: bool = True) -> Dict[str, Any]:
    cfg = _cfg()
    token = (cfg.meta_access_token or "").strip()

    if not token and not (cfg.meta_user_token or "").strip():
        return _empty_health("Facebook account is not connected yet. Press 'Connect with Facebook'.")

    if check_connection and token:
        info = token_info(token)
        if not info["is_valid"]:
            logger.info("[MetaAuth] Stored Page token is no longer valid — attempting automatic repair...")
            if try_recover():
                cfg = _cfg()
                token = (cfg.meta_access_token or "").strip()
                info = token_info(token) if token else {"is_valid": False}
            if not info.get("is_valid"):
                msg = (cfg.meta_last_error
                       or info.get("error_message")
                       or "Facebook token expired. Press 'Reconnect'.")
                out = _empty_health(msg)
                out["status"] = "EXPIRED"
                return out

        days = days_left(info.get("data_access_expires_at") or cfg.meta_data_access_expires_at)
        warning = ""
        if days is not None and days <= 7:
            warning = f" Facebook permission expires in {days} day(s) — reconnect soon."

        return {
            "connected": True,
            "status": "ACTIVE",
            "needs_reauth": False,
            "message": f"Connected & verified with Meta.{warning}",
            "days_left": days,
            "expires_at": info.get("expires_at") or 0,
            "data_access_expires_at": info.get("data_access_expires_at") or cfg.meta_data_access_expires_at or 0,
            "facebook": {
                "connected": bool(cfg.facebook_page_id),
                "name": cfg.meta_page_name or cfg.brand_name or "Facebook Page",
                "id": cfg.facebook_page_id or "",
            },
            "instagram": {
                "connected": bool(cfg.instagram_account_id),
                "username": cfg.meta_ig_username or "Instagram Account",
                "id": cfg.instagram_account_id or "",
            },
            "app_configured": is_configured(),
            "pages": pages_list(),
            "active_page_id": cfg.facebook_page_id or "",
        }

    # No verification requested: report what is stored.
    days = days_left(cfg.meta_data_access_expires_at)
    if not (cfg.meta_access_token or "").strip():
        return _empty_health("Facebook account is not connected yet. Press 'Connect with Facebook'.")
    return {
        "connected": True,
        "status": "ACTIVE",
        "needs_reauth": bool(cfg.meta_needs_reauth),
        "message": "Connection stored.",
        "days_left": days,
        "expires_at": cfg.meta_page_token_expires_at or 0,
        "data_access_expires_at": cfg.meta_data_access_expires_at or 0,
        "facebook": {
            "connected": bool(cfg.facebook_page_id),
            "name": cfg.meta_page_name or cfg.brand_name or "Facebook Page",
            "id": cfg.facebook_page_id or "",
        },
        "instagram": {
            "connected": bool(cfg.instagram_account_id),
            "username": cfg.meta_ig_username or "Instagram Account",
            "id": cfg.instagram_account_id or "",
        },
        "app_configured": is_configured(),
        "pages": pages_list(),
        "active_page_id": cfg.facebook_page_id or "",
    }
