"""
One-command check of the Facebook + Instagram connection.

Run this on the SAME computer that runs the dashboard (the OAuth login is stored
in config.json on that machine, not anywhere else).

  python verify_meta_live.py              # read-only health check (safe)
  python verify_meta_live.py --post       # also publish ONE small test post
  python verify_meta_live.py --post --yes # publish without the confirmation prompt

The test post goes live on your real Facebook Page and Instagram account, so it
is deliberately explicit. Delete it from the apps afterwards if you want.
"""
import argparse
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from app.config import config_manager          # noqa: E402
from app.modules import meta_auth              # noqa: E402
from app.modules.uploaders import MetaUploader  # noqa: E402

TEST_CAPTION = "ReelPilot connection test - please ignore. Verifying Facebook + Instagram publishing."


def show_health() -> dict:
    state = meta_auth.health()
    fb = state.get("facebook") or {}
    ig = state.get("instagram") or {}
    days = state.get("days_left")

    print("=" * 68)
    print(" FACEBOOK / INSTAGRAM CONNECTION HEALTH")
    print("=" * 68)
    print(f"  Status ............... {state.get('status')}")
    print(f"  Connected ............ {state.get('connected')}")
    print(f"  Facebook Page ........ {fb.get('name') or '-'}  (id: {fb.get('id') or '-'})")
    ig_name = ig.get("username") or "-"
    ig_display = f"@{ig_name}" if ig_name not in ("-", "Not Connected") else ig_name
    print(f"  Instagram ............ {ig_display}  (id: {ig.get('id') or '-'})")
    print(f"  Permission left ...... {'no fixed expiry' if days is None else str(days) + ' day(s)'}")
    print(f"  Token expires ........ {'never (Page token)' if not state.get('expires_at') else state.get('expires_at')}")
    print(f"  Reconnect needed ..... {state.get('needs_reauth')}")
    print(f"  Message .............. {state.get('message')}")
    print(f"  App ID / Secret ...... {'configured' if state.get('app_configured') else 'MISSING in .env'}")

    if state.get("needs_reauth"):
        print()
        print("  -> Open the dashboard (Start_Web_Dashboard.bat) and press")
        print("     Settings -> 'Connect with Facebook' once.")
        if config_manager.config.meta_last_error:
            print(f"     Last Meta error: {config_manager.config.meta_last_error}")
    print()
    return state


def make_test_image(path: str) -> str:
    from PIL import Image, ImageDraw, ImageFont

    def font(size: int):
        for name in (
            "arial.ttf",
            "Arial.ttf",
            "Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ):
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        try:
            return ImageFont.load_default(size=size)  # Pillow >= 10.1
        except TypeError:
            return ImageFont.load_default()

    img = Image.new("RGB", (1080, 1080), (11, 17, 32))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 1040, 1040], outline=(245, 158, 11), width=6)
    draw.text((110, 430), "ReelPilot", fill=(245, 158, 11), font=font(86))
    draw.text((110, 540), "connection test", fill=(255, 255, 255), font=font(64))
    draw.text((110, 640), datetime.now().strftime("%Y-%m-%d  %H:%M"), fill=(148, 163, 184), font=font(40))
    img.save(path, "PNG")
    return path


def publish_test_posts() -> int:
    uploader = MetaUploader()
    ok, message = uploader.validate_credentials()
    print(f"  Live credential check: {ok} -> {message}")
    if not ok:
        print("\n  Cannot publish: the connection is not live. Press 'Connect with Facebook' first.")
        return 1

    temp_dir = os.environ.get("TEMP") or "/tmp"
    image_path = make_test_image(os.path.join(temp_dir, "reelpilot_test_post.png"))
    print(f"  Test image: {image_path}")

    results = {}

    print("\n  [1/2] Facebook Page ...")
    fb_ok, fb_id, fb_url, fb_err = uploader.upload_facebook_photo(image_path, TEST_CAPTION, "")
    results["facebook"] = (fb_ok, fb_url, fb_err)
    print(f"        {'OK  ' + str(fb_url) if fb_ok else 'FAILED: ' + str(fb_err)}")

    print("\n  [2/2] Instagram ...")
    ig_ok, ig_id, ig_url, ig_err = uploader.upload_instagram_photo(image_path, TEST_CAPTION, "")
    results["instagram"] = (ig_ok, ig_url, ig_err)
    print(f"        {'OK  ' + str(ig_url) if ig_ok else 'FAILED: ' + str(ig_err)}")

    print("\n" + "-" * 68)
    both = all(v[0] for v in results.values())
    print(f"  RESULT: {'END-TO-END PUBLISHING WORKS on Facebook Page + Instagram' if both else 'PARTIAL / FAILED'}")
    for platform, (success, url, error) in results.items():
        print(f"    {platform:10s}: {'LIVE ' + str(url) if success else 'FAILED ' + str(error)}")
    print("-" * 68)
    return 0 if both else 1


def _when(timestamp: int) -> str:
    if not timestamp:
        return "never"
    return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")


KNOWN_ISSUES = [
    (("url blocked", "redirect_uri", "redirect uri"),
     "Redirect URI Meta mein registered nahi hai",
     ["Meta Dashboard -> Facebook Login -> Settings -> Valid OAuth Redirect URIs",
      "Bilkul wahi URL paste karein jo upar 'Redirect URI' line mein hai (http vs https, port, trailing slash sab match ho)",
      "Save karke 1-2 minute wait karein, phir Connect dobara dabayein"]),
    (("invalid scope", "invalid scopes"),
     "App ke paas ye permission add nahi hai",
     ["Meta Dashboard -> App Review -> Permissions and Features",
      "pages_show_list, pages_manage_posts, pages_read_engagement, instagram_basic, instagram_content_publish add/request karein"]),
    (("development mode", "not available for this app", "app not active", "app is in development"),
     "App Development mode mein hai",
     ["Meta Dashboard -> App Mode -> 'Live' karein, ya",
      "App Roles mein apna Facebook account Admin/Tester ke tor par add karein"]),
    (("session has been invalidated", "code 190", "subcode 460", "code 463", "code 467"),
     "Token Meta ne invalidate kar diya (password change / security / app removed)",
     ["Settings -> Connect with Facebook dobara dabayein",
      "Iske baad app khud token alive rakhta hai, manual token ki zaroorat nahi"]),
    (("does not have permission", "code 200", "code 10", "permission"),
     "Account ke paas Page/Instagram par required role nahi",
     ["Facebook Page -> Settings -> Page Roles: apna account Admin hona chahiye",
      "Instagram account Professional (Business/Creator) ho aur usi Page se linked ho"]),
    (("instagram",), "Instagram account Page se link nahi mila",
     ["Instagram app -> Settings -> Account type: Professional",
      "Instagram ko Facebook Page se link karein (Page Settings -> Linked accounts)"]),
    (("code 100", "invalid parameter"),
     "Meta ne request parameter reject kiya",
     ["Aam tor par redirect_uri mismatch ya purana token hota hai",
      "Connect dobara karein; phir bhi aaye to poora error message bhejein"]),
]


def diagnose() -> int:
    """Print exactly what the app will send to Meta and decode the last error."""
    from app.modules.meta_auth import (
        DEFAULT_SCOPES, TOKEN_SUBCODE_HINTS, app_id, app_secret,
        resolve_redirect_uri, token_info,
    )

    cfg = config_manager.config
    aid, secret = app_id(), app_secret()
    masked_id = (aid[:4] + "*" * 6 + aid[-2:]) if len(aid) > 8 else ("set" if aid else "MISSING")
    redirect_uri = resolve_redirect_uri("http://localhost:5000")

    print("=" * 68)
    print(" FACEBOOK LOGIN DIAGNOSTICS")
    print("=" * 68)
    print(f"  App ID ............... {masked_id}")
    print(f"  App Secret ........... {'set' if secret else 'MISSING  <- .env mein META_APP_SECRET daalein'}")
    print(f"  Redirect URI ......... {redirect_uri}")
    print("     ^ Meta Dashboard -> Facebook Login -> Settings -> Valid OAuth Redirect URIs")
    print("       mein bilkul yehi URL hona chahiye (http/https, port, slash sab match)")
    print(f"  Required permissions . {', '.join(DEFAULT_SCOPES)}")

    token = (cfg.meta_access_token or "").strip()
    info = {}
    if not token:
        print("  Stored token ......... none (abhi connect nahi hua)")
    else:
        info = token_info(token)
        print(f"  Token type ........... {info.get('type') or '-'}")
        print(f"  Token valid .......... {info.get('is_valid')}")
        print(f"  Time expiry .......... {'never (Page token)' if not info.get('expires_at') else _when(info.get('expires_at'))}")
        data_access = info.get("data_access_expires_at") or 0
        expiry_text = f"{_when(data_access)} ({meta_auth.days_left(data_access)} day(s))" if data_access else "no fixed expiry"
        print(f"  Permission expiry .... {expiry_text}")
        missing = [s for s in DEFAULT_SCOPES if s not in (info.get("scopes") or [])]
        print(f"  Missing permissions .. {', '.join(missing) if missing else 'none'}")
        if not info.get("is_valid"):
            hint = TOKEN_SUBCODE_HINTS.get(info.get("error_subcode") or 0, "")
            print(f"  Meta says ............ {info.get('error_message')} "
                  f"(code {info.get('error_code')}, subcode {info.get('error_subcode')})")
            if hint:
                print(f"                         -> {hint}")

    print(f"  Facebook Page ID ..... {cfg.facebook_page_id or '-'}")
    print(f"  Instagram ID ......... {cfg.instagram_account_id or '-'}")
    print(f"  Reconnect needed ..... {cfg.meta_needs_reauth}")
    print(f"  Last Meta error ...... {cfg.meta_last_error or 'none recorded'}")

    haystack = " ".join(str(x or "").lower() for x in (
        cfg.meta_last_error,
        info.get("error_message"),
        f"code {info.get('error_code')}" if info.get("error_code") else "",
        f"subcode {info.get('error_subcode')}" if info.get("error_subcode") else "",
    ))
    matches = [(title, fixes) for needles, title, fixes in KNOWN_ISSUES
               if any(n in haystack for n in needles)]

    if matches:
        print("\n  LIKELY CAUSE + FIX")
        for index, (title, fixes) in enumerate(matches, 1):
            print(f"\n  {index}. {title}")
            for step in fixes:
                print(f"     - {step}")
    else:
        print("\n  (Koi recorded Meta error nahi — Connect dabayein, phir ye command dobara chalayein)")

    print("\n  CHECKLIST (in order)")
    for line in (
        "1. Browser mein facebook.com par logged-in ho (sahi account)",
        "2. App Live mode mein ho, ya aap Admin/Tester ho",
        f"3. Ye URI Meta mein whitelisted ho: {redirect_uri}",
        "4. Page par aapka account Admin ho, Instagram Page se linked + Professional ho",
        "5. Settings -> Connect with Facebook dabayein",
        "6. Phir: python verify_meta_live.py --diagnose",
    ):
        print(f"     {line}")
    print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Facebook/Instagram connection and optionally publish a test post.")
    parser.add_argument("--post", action="store_true", help="publish one test post to the Facebook Page and Instagram")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt for --post")
    parser.add_argument("--diagnose", action="store_true", help="show app/token/redirect-URI diagnostics and decode the last Meta error")
    args = parser.parse_args()

    if args.diagnose:
        return diagnose()

    state = show_health()

    if not args.post:
        print("  (read-only check - run with --post to publish one test post)")
        return 0 if state.get("connected") else 1

    if not state.get("connected"):
        print("  Connection is not live, nothing was published.")
        return 1

    if not args.yes:
        print("  WARNING: this publishes a real post to your Facebook Page and Instagram.")
        if input("  Type 'yes' to continue: ").strip().lower() != "yes":
            print("  Cancelled - nothing published.")
            return 1

    return publish_test_posts()


if __name__ == "__main__":
    sys.exit(main())
