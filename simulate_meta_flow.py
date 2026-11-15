"""
End-to-end SIMULATION of the Facebook Login -> publish flow.

Every Meta Graph API response is faked in-process, so this proves the whole
chain without touching a real Facebook account and without any credentials:

    1. /auth/facebook            -> redirect to the Facebook login dialog
    2. /auth/facebook/callback   -> code -> short-lived token
    3. fb_exchange_token         -> long-lived user token (~60 days)  [the step that was missing]
    4. /me/accounts              -> Page token + Page ID + Instagram account ID, stored automatically
    5. /api/accounts/health      -> ACTIVE with days remaining
    6. publish                   -> Facebook photo + Instagram photo really go through the upload code
    7. Page token revoked        -> rebuilt from the stored login, upload retried and succeeds
    8. login also revoked        -> one clean "Reconnect" state, no silent failures

Run:  python simulate_meta_flow.py
"""
import json
import os
import sys
import time
import urllib.parse

os.environ["VERCEL"] = "1"                                  # config -> /tmp, never your real config.json
os.environ.setdefault("META_APP_ID", "100000000000000")      # dummy app, nothing is sent to Meta
os.environ.setdefault("META_APP_SECRET", "simulated_app_secret_for_tests")

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import requests as real_requests  # noqa: E402

CONFIG_FILE = "/tmp/reelpilot_config.json"
if os.path.exists(CONFIG_FILE):
    os.remove(CONFIG_FILE)

SCOPES = ["pages_show_list", "pages_manage_posts", "instagram_basic", "instagram_content_publish"]
RESULTS = []


def check(label, condition, detail=""):
    RESULTS.append(bool(condition))
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f"   [{detail}]" if detail and not condition else ""))
    return condition


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


class FakeMetaAPI:
    """A tiny stand-in for graph.facebook.com."""

    def __init__(self):
        self.short_token = "SIM_SHORT_USER_TOKEN"
        self.long_token = "SIM_LONG_LIVED_USER_TOKEN"
        self.page_token = "SIM_PAGE_TOKEN_1"
        self.revoked = set()          # tokens Meta has invalidated
        self.user_token_valid = True
        self.page_id = "800869286434757"
        self.page_name = "JANI's Perfume"
        self.ig_id = "17841423338066933"
        self.ig_username = "official_janisperfume"
        self.calls = []

    @staticmethod
    def error(code=190, subcode=460, message="Error validating access token: the session has been invalidated"):
        return {"error": {"message": message, "type": "OAuthException", "code": code, "error_subcode": subcode}}

    def _path(self, url):
        return urllib.parse.urlparse(url).path.replace("/v19.0/", "/").lstrip("/")

    def _page_token_ok(self, token):
        return str(token).startswith("SIM_PAGE_TOKEN") and token not in self.revoked

    def debug(self, token):
        now = int(time.time())
        if token == self.short_token:
            return {"data": {"is_valid": True, "type": "USER", "expires_at": now + 3600,
                             "data_access_expires_at": now + 86400, "scopes": SCOPES}}
        if token == self.long_token:
            if not self.user_token_valid:
                return {"data": {"is_valid": False, "type": "USER", "expires_at": 0,
                                 "data_access_expires_at": 0, "scopes": [], "error": self.error()["error"]}}
            return {"data": {"is_valid": True, "type": "USER", "expires_at": now + 5183944,
                             "data_access_expires_at": now + 5183944, "scopes": SCOPES}}
        if token.startswith("SIM_PAGE_TOKEN"):
            if not self._page_token_ok(token):
                return {"data": {"is_valid": False, "type": "PAGE", "expires_at": 0,
                                 "data_access_expires_at": 0, "scopes": [], "error": self.error()["error"]}}
            return {"data": {"is_valid": True, "type": "PAGE", "expires_at": 0,
                             "data_access_expires_at": now + 5183944, "scopes": SCOPES}}
        return {"data": {"is_valid": False, "type": "UNKNOWN", "expires_at": 0, "data_access_expires_at": 0,
                         "scopes": [], "error": {"message": "Invalid OAuth access token", "code": 190, "error_subcode": 460}}}

    def get(self, url, params=None, timeout=None, **kwargs):
        p = dict(params or {})
        path = self._path(url)
        self.calls.append(("GET", path, p))
        if path == "oauth/access_token":
            if p.get("grant_type") == "fb_exchange_token":
                if p.get("fb_exchange_token") in (self.short_token, self.long_token) and self.user_token_valid:
                    return FakeResponse({"access_token": self.long_token, "token_type": "bearer", "expires_in": 5183944})
                return FakeResponse(self.error())
            if p.get("code"):
                return FakeResponse({"access_token": self.short_token, "expires_in": 7200})
            return FakeResponse(self.error(100, 0, "Missing code"))
        if path == "debug_token":
            return FakeResponse(self.debug(p.get("input_token", "")))
        if path == "me/accounts":
            if not self.user_token_valid or p.get("access_token") != self.long_token:
                return FakeResponse(self.error())
            return FakeResponse({"data": [{
                "id": self.page_id,
                "name": self.page_name,
                "access_token": self.page_token,
                "instagram_business_account": {"id": self.ig_id, "username": self.ig_username},
            }]})
        if path == "me":
            if str(p.get("access_token", "")).startswith("SIM_PAGE_TOKEN") and not self._page_token_ok(p.get("access_token")):
                return FakeResponse(self.error())
            return FakeResponse({"id": self.page_id, "name": self.page_name})
        if path == self.page_id:
            return FakeResponse({"id": self.page_id,
                                 "instagram_business_account": {"id": self.ig_id, "username": self.ig_username}})
        if path.startswith("SIM_CONTAINER"):
            return FakeResponse({"status_code": "FINISHED"})
        return FakeResponse(self.error(100, 0, f"Unhandled GET {path}"))

    def post(self, url, params=None, data=None, files=None, headers=None, timeout=None, **kwargs):
        path = self._path(url)
        self.calls.append(("POST", path, {}))
        if "freeimage.host" in url:
            return FakeResponse({"image": {"url": "https://cdn.simulated.test/test_post.png"}})
        if path.endswith("/media_publish"):
            return FakeResponse({"id": "SIM_IG_MEDIA_1"})
        if path.endswith("/media"):
            return FakeResponse({"id": "SIM_CONTAINER_1"})
        if path.endswith("/photos"):
            if not self._page_token_ok((data or {}).get("access_token", "")):
                return FakeResponse(self.error())
            return FakeResponse({"id": "SIM_FB_PHOTO_1"})
        return FakeResponse(self.error(100, 0, f"Unhandled POST {path}"))


def main():
    fake = FakeMetaAPI()
    real_requests.get, real_requests.post = fake.get, fake.post

    try:
        import web_app
        from app.config import config_manager
        from app.modules import meta_auth

        meta_auth.clear_health_cache()
        client = web_app.app.test_client()
        with client.session_transaction() as sess:
            sess["authenticated"] = True

        print("=" * 74)
        print(" SIMULATED FLOW — no real Meta calls, your Facebook account is untouched")
        print("=" * 74)

        # 1. OAuth start
        print("\n[1] Connect with Facebook -> login dialog")
        r = client.get("/auth/facebook")
        location = r.headers.get("Location", "")
        check("redirects to the Facebook login dialog", r.status_code == 302 and "dialog/oauth" in location)
        check("asks only for the publishing permissions",
              "pages_manage_posts" in location and "instagram_content_publish" in location)
        with client.session_transaction() as sess:
            state = sess.get("fb_oauth_state")
        check("CSRF state created", bool(state))

        # 2-4. Callback: code -> tokens -> page + instagram
        print("\n[2] Facebook returns -> app does the rest by itself")
        r = client.get(f"/auth/facebook/callback?code=SIM_CODE&state={state}")
        check("callback succeeds and returns to the dashboard", "meta_connected=1" in r.headers.get("Location", ""))

        cfg = config_manager.config
        check("Page token stored", cfg.meta_access_token == fake.page_token, cfg.meta_access_token)
        check("long-lived Facebook login stored for auto-repair", cfg.meta_user_token == fake.long_token)
        check("Page ID auto-detected", cfg.facebook_page_id == fake.page_id)
        check("Instagram account auto-detected", cfg.instagram_account_id == fake.ig_id)
        check("Page + Instagram names stored",
              (cfg.meta_page_name, cfg.meta_ig_username) == (fake.page_name, fake.ig_username))
        check("reconnect flag cleared", cfg.meta_needs_reauth is False)

        order = [(m, p) for m, p, _ in fake.calls]
        idx_exchange = next(i for i, (m, p, prm) in enumerate(fake.calls)
                            if p == "oauth/access_token" and prm.get("grant_type") == "fb_exchange_token")
        idx_pages = order.index(("GET", "me/accounts"))
        check("token extended to long-lived BEFORE listing Pages (the bug that was fixed)",
              idx_exchange < idx_pages)

        # 5. Health
        print("\n[3] Dashboard health")
        r = client.get("/api/accounts/health")
        health = r.get_json()
        check("status ACTIVE", health.get("status") == "ACTIVE", health.get("status"))
        check("shows the Page name", health["facebook"]["name"] == fake.page_name)
        check("shows the Instagram handle", health["instagram"]["username"] == fake.ig_username)
        check("shows days of permission left", isinstance(health.get("days_left"), int) and health["days_left"] > 0,
              str(health.get("days_left")))
        check("no reconnect needed", health.get("needs_reauth") is False)

        # 6. Publish a real test post through the real upload code
        print("\n[4] Publish one test post (Facebook photo + Instagram photo)")
        import verify_meta_live
        exit_code = verify_meta_live.publish_test_posts()
        check("both platforms published", exit_code == 0)
        check("Facebook upload used the Page token", any(m == "POST" and p.endswith("/photos") for m, p, _ in fake.calls))
        check("Instagram container + publish called",
              any(p.endswith("/media") for _, p, _ in fake.calls) and any(p.endswith("/media_publish") for _, p, _ in fake.calls))

        # 7. Meta revokes the Page token -> automatic repair + retry
        print("\n[5] Meta revokes the Page token mid-life (error 190 / subcode 460)")
        before = config_manager.config.meta_access_token
        fake.revoked.add(before)
        fake.page_token = "SIM_PAGE_TOKEN_2"
        meta_auth.clear_health_cache()
        from app.modules.uploaders import MetaUploader
        ok, media_id, url, err = MetaUploader().upload_facebook_photo(
            os.path.join(os.environ.get("TEMP") or "/tmp", "reelpilot_test_post.png"),
            "auto-repair check", "",
        )
        check("upload succeeded without asking the user anything", ok is True, err)
        check("Page token was rebuilt from the stored login", config_manager.config.meta_access_token == "SIM_PAGE_TOKEN_2",
              config_manager.config.meta_access_token)
        check("old token is gone", before != config_manager.config.meta_access_token)

        r = client.get("/api/accounts/health")
        check("health back to ACTIVE after repair", r.get_json().get("status") == "ACTIVE")

        # 8. Even the login is revoked -> one clean reconnect state
        print("\n[6] Facebook invalidates the stored login too (worst case)")
        fake.revoked.add(config_manager.config.meta_access_token)
        fake.user_token_valid = False
        meta_auth.clear_health_cache()
        health = client.get("/api/accounts/health").get_json()
        check("status EXPIRED", health.get("status") == "EXPIRED", health.get("status"))
        check("UI told to show Reconnect", health.get("needs_reauth") is True)
        check("clear reason given", bool(health.get("message")), health.get("message"))
        check("no crash, dashboard still serves", client.get("/").status_code == 200)
        print(f"\n      message shown: {health.get('message')}")

    finally:
        real_requests.get, real_requests.post = real_requests_get, real_requests_post

    passed, total = sum(RESULTS), len(RESULTS)
    print("\n" + "=" * 74)
    print(f" RESULT: {passed}/{total} checks passed" + ("  —  FLOW PROVEN END TO END" if passed == total else "  —  FAILURES ABOVE"))
    print("=" * 74)
    return 0 if passed == total else 1


real_requests_get, real_requests_post = real_requests.get, real_requests.post

if __name__ == "__main__":
    sys.exit(main())
