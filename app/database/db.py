"""
SQLite Database manager for tracking uploaded files, preventing duplicates,
and maintaining upload logs and daily post counters.
"""
import os
import sqlite3
import hashlib
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from app.database.models import PostRecord, PostStatus, Platform


DEFAULT_DB_PATH = "/tmp/scheduler.db" if os.environ.get("VERCEL") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scheduler.db")


class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_dir()
        self.init_db()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes database schema if tables do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    target_platform TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    processed_path TEXT,
                    caption TEXT,
                    hashtags TEXT,
                    status TEXT NOT NULL DEFAULT 'QUEUED',
                    scheduled_time TEXT,
                    uploaded_at TEXT,
                    remote_media_id TEXT,
                    remote_url TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS upload_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    platform TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE SET NULL
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_file_hash ON posts(file_hash);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(target_platform);
            """)
            conn.commit()

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Computes SHA-256 hash of a file or URL string to detect duplicates."""
        hasher = hashlib.sha256()
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
        else:
            hasher.update(str(file_path).encode("utf-8"))
        return hasher.hexdigest()

    def is_duplicate(self, file_hash: str) -> bool:
        """Checks if a file with this hash was already processed or uploaded."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM posts WHERE file_hash = ?", (file_hash,))
            row = cursor.fetchone()
            return row is not None

    def insert_post(
        self,
        file_path: str,
        file_hash: str,
        target_platform: str,
        media_type: str,
        status: str = PostStatus.QUEUED.value
    ) -> Optional[int]:
        """Inserts a new post record. Returns record ID if inserted, None if duplicate."""
        now = datetime.now().isoformat()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO posts (file_path, file_hash, target_platform, media_type, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (file_path, file_hash, target_platform, media_type, status, now, now))
                conn.commit()
                post_id = cursor.lastrowid
                self.log_event(post_id, target_platform, status, f"Queued file: {os.path.basename(file_path)}")
                return post_id
        except sqlite3.IntegrityError:
            return None

    def update_post(self, post_id: int, **kwargs):
        """Updates fields of a post record dynamically."""
        if not kwargs:
            return
        kwargs["updated_at"] = datetime.now().isoformat()
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [post_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE posts SET {fields} WHERE id = ?", values)
            conn.commit()

    def get_post(self, post_id: int) -> Optional[PostRecord]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            if row:
                return PostRecord(**dict(row))
            return None

    def get_posts(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 100
    ) -> List[PostRecord]:
        query = "SELECT * FROM posts WHERE 1=1"
        params: List[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if platform:
            query += " AND target_platform = ?"
            params.append(platform)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [PostRecord(**dict(r)) for r in rows]

    def count_uploads_today(self, platform: str) -> int:
        """Counts successful uploads today for a platform to enforce daily limits."""
        today_prefix = date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM posts
                WHERE target_platform = ?
                  AND status = ?
                  AND uploaded_at LIKE ?
            """, (platform, PostStatus.UPLOADED.value, f"{today_prefix}%"))
            count = cursor.fetchone()[0]
            return count

    def log_event(self, post_id: Optional[int], platform: str, status: str, details: str):
        now = datetime.now().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO upload_logs (post_id, platform, status, details, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (post_id, platform, status, details, now))
            conn.commit()

    def delete_post(self, post_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            cursor.execute("DELETE FROM upload_logs WHERE post_id = ?", (post_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM upload_logs ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
