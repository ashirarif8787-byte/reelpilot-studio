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


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Facebook/Instagram connection and optionally publish a test post.")
    parser.add_argument("--post", action="store_true", help="publish one test post to the Facebook Page and Instagram")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt for --post")
    args = parser.parse_args()

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
