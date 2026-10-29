"""
Cloud-Persistent Scheduled Posts Queue.
Synchronizes scheduled social media posts to a private GitHub repository JSON store
(data/queue.json) so that Vercel Serverless containers, background cron triggers,
and local daemons share 100% persistent state across cold starts and laptop restarts.
"""
import os
import sys
import json
import base64
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.utils.logger import logger

GITHUB_REPO = "ashirarif8787-byte/reelpilot-studio"
GITHUB_PATH = "data/queue.json"
PERMANENT_GITHUB_TOKEN = "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"

class CloudQueueManager:
    def __init__(self):
        self.repo = GITHUB_REPO
        self.path = GITHUB_PATH
        self.token = os.environ.get("GITHUB_TOKEN", "").strip() or PERMANENT_GITHUB_TOKEN

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ReelPilot-Studio-Cloud-Queue"
        }

    def fetch_queue(self) -> Dict[str, Any]:
        """Fetches the queue JSON and its git blob SHA from GitHub."""
        try:
            url = f"https://api.github.com/repos/{self.repo}/contents/{self.path}"
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                sha = data.get("sha")
                content_b64 = data.get("content", "")
                decoded = base64.b64decode(content_b64).decode("utf-8")
                parsed = json.loads(decoded)
                return {"success": True, "sha": sha, "data": parsed}
            elif resp.status_code == 404:
                # File does not exist yet; initialize
                return {"success": True, "sha": None, "data": {"scheduled": [], "history": []}}
            else:
                logger.warning(f"[CloudQueue] GitHub fetch error HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"[CloudQueue] Error fetching queue from GitHub: {e}")

        # Local fallback if GitHub unreachable
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "queue.json")
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    return {"success": True, "sha": None, "data": json.load(f)}
            except Exception:
                pass
        return {"success": False, "sha": None, "data": {"scheduled": [], "history": []}}

    def save_queue(self, queue_data: Dict[str, Any], sha: Optional[str] = None) -> bool:
        """Saves updated queue JSON to GitHub with a commit."""
        try:
            json_str = json.dumps(queue_data, indent=2, ensure_ascii=False)
            content_b64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

            url = f"https://api.github.com/repos/{self.repo}/contents/{self.path}"
            payload = {
                "message": f"chore(queue): sync scheduled queue [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]",
                "content": content_b64,
                "branch": "main"
            }
            if sha:
                payload["sha"] = sha

            resp = requests.put(url, headers=self._get_headers(), json=payload, timeout=15)
            if resp.status_code in [200, 201]:
                logger.info(f"✅ [CloudQueue] Successfully synced cloud queue to GitHub (HTTP {resp.status_code})")
                return True
            elif resp.status_code == 409:
                # SHA mismatch / conflict; re-fetch latest SHA and retry once
                logger.warning("[CloudQueue] SHA conflict during save, re-fetching latest...")
                latest = self.fetch_queue()
                if latest.get("sha"):
                    payload["sha"] = latest["sha"]
                    r2 = requests.put(url, headers=self._get_headers(), json=payload, timeout=15)
                    return r2.status_code in [200, 201]
            logger.error(f"[CloudQueue] Failed to save queue to GitHub: {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.error(f"[CloudQueue] Exception saving queue: {e}")

        # Save to local file backup
        try:
            local_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
            os.makedirs(local_dir, exist_ok=True)
            local_file = os.path.join(local_dir, "queue.json")
            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(queue_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return False

    def add_scheduled_post(self, post_info: Dict[str, Any]) -> bool:
        """Adds a new scheduled post item to cloud queue."""
        q = self.fetch_queue()
        queue_data = q.get("data", {"scheduled": [], "history": []})
        scheduled = queue_data.get("scheduled", [])

        # Ensure unique post_id
        post_id = post_info.get("id")
        scheduled = [p for p in scheduled if p.get("id") != post_id]
        scheduled.append(post_info)
        queue_data["scheduled"] = scheduled

        return self.save_queue(queue_data, sha=q.get("sha"))

    def get_due_posts(self) -> List[Dict[str, Any]]:
        """Returns all posts that are SCHEDULED and whose scheduled_time <= now (UTC)."""
        q = self.fetch_queue()
        scheduled = q.get("data", {}).get("scheduled", [])
        now_dt = datetime.now(timezone.utc)

        due = []
        for p in scheduled:
            if p.get("status") not in ["SCHEDULED", "QUEUED"]:
                continue
            sched_str = p.get("scheduled_time")
            if not sched_str:
                due.append(p)
                continue
            try:
                # Handle ISO timestamps with or without timezone
                clean_str = sched_str.replace("Z", "+00:00")
                if "+" in clean_str or "-" in clean_str[10:]:
                    sched_dt = datetime.fromisoformat(clean_str)
                else:
                    sched_dt = datetime.fromisoformat(clean_str).replace(tzinfo=timezone.utc)

                if now_dt >= sched_dt:
                    due.append(p)
            except Exception as ex:
                logger.warning(f"[CloudQueue] Date parse fallback for {sched_str}: {ex}")
                due.append(p)
        return due

    def update_post_status(
        self,
        post_id: int,
        status: str,
        remote_id: Optional[str] = None,
        remote_url: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Updates a post's status and archives completed/failed ones to history."""
        q = self.fetch_queue()
        queue_data = q.get("data", {"scheduled": [], "history": []})
        scheduled = queue_data.get("scheduled", [])
        history = queue_data.get("history", [])

        updated = False
        remaining_scheduled = []

        for p in scheduled:
            if p.get("id") == post_id:
                p["status"] = status
                if remote_id: p["remote_media_id"] = remote_id
                if remote_url: p["remote_url"] = remote_url
                if error_message is not None: p["error_message"] = error_message
                p["updated_at"] = datetime.now(timezone.utc).isoformat()

                if status in ["UPLOADED", "FAILED"]:
                    history.append(p)
                else:
                    remaining_scheduled.append(p)
                updated = True
            else:
                remaining_scheduled.append(p)

        if updated:
            queue_data["scheduled"] = remaining_scheduled
            queue_data["history"] = history[-100:] # Keep last 100 history items
            return self.save_queue(queue_data, sha=q.get("sha"))
        return False

    def delete_post(self, post_id: int) -> bool:
        """Permanently removes a post from both scheduled queue and history."""
        q = self.fetch_queue()
        queue_data = q.get("data", {"scheduled": [], "history": []})
        scheduled = [p for p in queue_data.get("scheduled", []) if p.get("id") != post_id]
        history = [p for p in queue_data.get("history", []) if p.get("id") != post_id]

        queue_data["scheduled"] = scheduled
        queue_data["history"] = history
        return self.save_queue(queue_data, sha=q.get("sha"))

    def clear_failed(self) -> int:
        """Wipes all failed entries from queue and history."""
        q = self.fetch_queue()
        queue_data = q.get("data", {"scheduled": [], "history": []})
        orig_s_count = len(queue_data.get("scheduled", []))
        orig_h_count = len(queue_data.get("history", []))

        scheduled = [p for p in queue_data.get("scheduled", []) if p.get("status") != "FAILED"]
        history = [p for p in queue_data.get("history", []) if p.get("status") != "FAILED"]

        removed = (orig_s_count - len(scheduled)) + (orig_h_count - len(history))
        queue_data["scheduled"] = scheduled
        queue_data["history"] = history
        self.save_queue(queue_data, sha=q.get("sha"))
        return removed

    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Returns all scheduled and historic posts for calendar rendering."""
        q = self.fetch_queue()
        data = q.get("data", {})
        all_items = list(data.get("scheduled", [])) + list(data.get("history", []))
        return all_items

cloud_queue = CloudQueueManager()
