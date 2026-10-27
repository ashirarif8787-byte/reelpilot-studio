"""
Desktop User Interface (Tkinter / CustomTkinter)
Provides an intuitive dashboard:
- Real-time queue view with status and scheduled countdown
- Settings configuration panel for API keys and anti-spam delays
- Live streaming activity log terminal
- Controls to start/stop folder watcher and pause/resume scheduler
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Optional

try:
    import customtkinter as ctk
    USE_CTK = True
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    USE_CTK = False

from app.config import config_manager
from app.database.db import DatabaseManager
from app.database.models import PostStatus
from app.modules.watcher import FolderWatcherService
from app.modules.scheduler import SocialScheduler
from app.modules.uploaders import MetaUploader, TikTokUploader
from app.utils.logger import register_ui_log_listener, logger
from app.utils.helpers import format_delay_time


class MainWindow:
    def __init__(self):
        if USE_CTK:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()

        self.root.title("Social Media Automation & Scheduler (Instagram & TikTok)")
        self.root.geometry("1100x780")
        self.root.minsize(950, 650)

        # Services
        self.db = DatabaseManager()
        self.scheduler = SocialScheduler(
            db=self.db,
            on_queue_update_callback=self._on_queue_updated,
            on_alert_callback=self._on_scheduler_alert
        )
        self.watcher = FolderWatcherService(
            db=self.db,
            on_new_file=lambda pid: self._on_queue_updated()
        )

        self._build_ui()

        # Connect logger to UI log box
        register_ui_log_listener(self._append_log)

        # Refresh queue timer (every 5 seconds)
        self._periodic_queue_refresh()

        # Auto-start watcher and scheduler
        self.watcher.start()
        self.scheduler.start()
        self._update_status_bar()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Top Header Bar
        self.header_frame = ctk.CTkFrame(self.root, corner_radius=0) if USE_CTK else tk.Frame(self.root, bg="#1e1e1e")
        self.header_frame.pack(fill="x", padx=0, pady=0)

        title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="📱 Social Media Automation & Scheduler",
            font=ctk.CTkFont(size=20, weight="bold")
        ) if USE_CTK else tk.Label(self.header_frame, text="Social Media Automation & Scheduler", font=("Arial", 16, "bold"), fg="white", bg="#1e1e1e")
        title_lbl.pack(side="left", padx=20, pady=12)

        # Status pills
        self.status_lbl = ctk.CTkLabel(
            self.header_frame,
            text="🟢 Watcher: ACTIVE | 🟢 Scheduler: RUNNING",
            font=ctk.CTkFont(size=12, weight="bold")
        ) if USE_CTK else tk.Label(self.header_frame, text="🟢 Watcher: ACTIVE | 🟢 Scheduler: RUNNING", fg="#00e676", bg="#1e1e1e")
        self.status_lbl.pack(side="right", padx=20, pady=12)

        # Tabview (Queue & Logs vs Settings)
        if USE_CTK:
            self.tabview = ctk.CTkTabview(self.root)
            self.tabview.pack(fill="both", expand=True, padx=15, pady=10)
            self.tab_queue = self.tabview.add("📊 Queue & Activity")
            self.tab_settings = self.tabview.add("⚙️ Settings & API Keys")
        else:
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
            self.tab_queue = ttk.Frame(self.notebook)
            self.tab_settings = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_queue, text="📊 Queue & Activity")
            self.notebook.add(self.tab_settings, text="⚙️ Settings & API Keys")

        self._build_queue_tab()
        self._build_settings_tab()

    def _build_queue_tab(self):
        # Action Toolbar
        action_bar = ctk.CTkFrame(self.tab_queue) if USE_CTK else tk.Frame(self.tab_queue)
        action_bar.pack(fill="x", padx=10, pady=(5, 10))

        if USE_CTK:
            btn_open_insta = ctk.CTkButton(action_bar, text="📂 Open Insta Folder", command=self._open_insta_folder, width=150)
            btn_open_insta.pack(side="left", padx=5)

            btn_open_tiktok = ctk.CTkButton(action_bar, text="📂 Open TikTok Folder", command=self._open_tiktok_folder, width=150)
            btn_open_tiktok.pack(side="left", padx=5)

            self.btn_pause = ctk.CTkButton(action_bar, text="⏸ Pause Queue", fg_color="#e65100", command=self._toggle_pause, width=130)
            self.btn_pause.pack(side="left", padx=5)

            btn_refresh = ctk.CTkButton(action_bar, text="🔄 Refresh", command=self._load_queue_table, width=100)
            btn_refresh.pack(side="right", padx=5)
        else:
            tk.Button(action_bar, text="Open Insta Folder", command=self._open_insta_folder).pack(side="left", padx=5)
            tk.Button(action_bar, text="Open TikTok Folder", command=self._open_tiktok_folder).pack(side="left", padx=5)
            self.btn_pause = tk.Button(action_bar, text="Pause Queue", command=self._toggle_pause)
            self.btn_pause.pack(side="left", padx=5)
            tk.Button(action_bar, text="Refresh", command=self._load_queue_table).pack(side="right", padx=5)

        # Queue Table
        table_frame = ctk.CTkFrame(self.tab_queue) if USE_CTK else tk.Frame(self.tab_queue)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "platform", "filename", "type", "scheduled_in", "status", "remote_url")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", height=10)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("platform", text="Platform")
        self.tree.heading("filename", text="Source File")
        self.tree.heading("type", text="Type")
        self.tree.heading("scheduled_in", text="Scheduled Post Time")
        self.tree.heading("status", text="Status")
        self.tree.heading("remote_url", text="Live Post URL")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("platform", width=90, anchor="center")
        self.tree.column("filename", width=220, anchor="w")
        self.tree.column("type", width=70, anchor="center")
        self.tree.column("scheduled_in", width=180, anchor="center")
        self.tree.column("status", width=110, anchor="center")
        self.tree.column("remote_url", width=260, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Log Terminal Section
        log_label = ctk.CTkLabel(self.tab_queue, text="📋 Activity Logs & Real-Time Output:", font=ctk.CTkFont(size=12, weight="bold")) if USE_CTK else tk.Label(self.tab_queue, text="Activity Logs:", font=("Arial", 10, "bold"))
        log_label.pack(anchor="w", padx=10, pady=(10, 2))

        self.log_text = tk.Text(self.tab_queue, height=8, bg="#121212", fg="#00e676", insertbackground="white", font=("Consolas", 9))
        self.log_text.pack(fill="x", padx=10, pady=(0, 10))

    def _build_settings_tab(self):
        # Settings Scrollable Area
        settings_canvas = ctk.CTkScrollableFrame(self.tab_settings) if USE_CTK else tk.Frame(self.tab_settings)
        settings_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        cfg = config_manager.config

        # Section 1: OpenAI
        self._create_section_label(settings_canvas, "🤖 OpenAI API (Viral Captions & Hashtags)")
        self.entry_openai_key = self._create_field(settings_canvas, "OpenAI API Key:", cfg.openai_api_key, show="*")
        self.entry_openai_model = self._create_field(settings_canvas, "Model:", cfg.openai_model)

        # Section 2: Meta Graph API
        self._create_section_label(settings_canvas, "📸 Meta Graph API (Instagram Reels & Facebook)")
        self.entry_meta_token = self._create_field(settings_canvas, "Meta Access Token:", cfg.meta_access_token, show="*")
        self.entry_ig_id = self._create_field(settings_canvas, "Instagram Account ID:", cfg.instagram_account_id)
        self.entry_fb_id = self._create_field(settings_canvas, "Facebook Page ID (Optional):", cfg.facebook_page_id)

        btn_test_meta = ctk.CTkButton(settings_canvas, text="🔍 Test Meta Credentials", command=self._test_meta_api, width=180) if USE_CTK else tk.Button(settings_canvas, text="Test Meta Credentials", command=self._test_meta_api)
        btn_test_meta.pack(anchor="w", padx=15, pady=(2, 10))

        # Section 3: TikTok Content Posting API
        self._create_section_label(settings_canvas, "🎵 TikTok Content Posting API")
        self.entry_tiktok_token = self._create_field(settings_canvas, "TikTok Access Token:", cfg.tiktok_access_token, show="*")
        self.entry_tiktok_key = self._create_field(settings_canvas, "Client Key (Optional):", cfg.tiktok_client_key)
        self.entry_tiktok_secret = self._create_field(settings_canvas, "Client Secret (Optional):", cfg.tiktok_client_secret, show="*")

        btn_test_tiktok = ctk.CTkButton(settings_canvas, text="🔍 Test TikTok Credentials", command=self._test_tiktok_api, width=180) if USE_CTK else tk.Button(settings_canvas, text="Test TikTok Credentials", command=self._test_tiktok_api)
        btn_test_tiktok.pack(anchor="w", padx=15, pady=(2, 10))

        # Section 4: Scheduling & Anti-Spam Delays
        self._create_section_label(settings_canvas, "⏱ Daily Limits & Human-like Delays")
        self.entry_limit_insta = self._create_field(settings_canvas, "Max Posts/Day (Instagram):", str(cfg.daily_limit_insta))
        self.entry_limit_tiktok = self._create_field(settings_canvas, "Max Posts/Day (TikTok):", str(cfg.daily_limit_tiktok))
        self.entry_min_delay = self._create_field(settings_canvas, "Min Delay Between Posts (Minutes):", str(cfg.min_delay_minutes))
        self.entry_max_delay = self._create_field(settings_canvas, "Max Delay Between Posts (Minutes):", str(cfg.max_delay_minutes))
        self.entry_duration = self._create_field(settings_canvas, "Reel Duration from Images (Seconds):", str(cfg.image_duration_seconds))

        # Save Button
        save_btn = ctk.CTkButton(
            settings_canvas,
            text="💾 Save All Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self._save_settings,
            height=40
        ) if USE_CTK else tk.Button(settings_canvas, text="Save All Settings", bg="#2e7d32", fg="white", font=("Arial", 11, "bold"), command=self._save_settings)
        save_btn.pack(fill="x", padx=15, pady=20)

    def _create_section_label(self, parent, text: str):
        if USE_CTK:
            lbl = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=14, weight="bold"))
            lbl.pack(anchor="w", padx=10, pady=(15, 5))
        else:
            lbl = tk.Label(parent, text=text, font=("Arial", 11, "bold"))
            lbl.pack(anchor="w", padx=10, pady=(15, 5))

    def _create_field(self, parent, label_text: str, default_value: str, show: Optional[str] = None):
        row = ctk.CTkFrame(parent, fg_color="transparent") if USE_CTK else tk.Frame(parent)
        row.pack(fill="x", padx=10, pady=3)

        lbl = ctk.CTkLabel(row, text=label_text, width=250, anchor="w") if USE_CTK else tk.Label(row, text=label_text, width=30, anchor="w")
        lbl.pack(side="left")

        entry = ctk.CTkEntry(row, show=show or "") if USE_CTK else tk.Entry(row, show=show or "")
        entry.insert(0, default_value or "")
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def _save_settings(self):
        try:
            config_manager.update(
                openai_api_key=self.entry_openai_key.get().strip(),
                openai_model=self.entry_openai_model.get().strip(),
                meta_access_token=self.entry_meta_token.get().strip(),
                instagram_account_id=self.entry_ig_id.get().strip(),
                facebook_page_id=self.entry_fb_id.get().strip(),
                tiktok_access_token=self.entry_tiktok_token.get().strip(),
                tiktok_client_key=self.entry_tiktok_key.get().strip(),
                tiktok_client_secret=self.entry_tiktok_secret.get().strip(),
                daily_limit_insta=int(self.entry_limit_insta.get().strip() or "3"),
                daily_limit_tiktok=int(self.entry_limit_tiktok.get().strip() or "3"),
                min_delay_minutes=int(self.entry_min_delay.get().strip() or "120"),
                max_delay_minutes=int(self.entry_max_delay.get().strip() or "240"),
                image_duration_seconds=int(self.entry_duration.get().strip() or "8")
            )
            messagebox.showinfo("Settings Saved", "All API credentials and delay limits have been successfully saved!")
            logger.info("[Settings] Updated configurations saved to config.json.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def _test_meta_api(self):
        uploader = MetaUploader(
            access_token=self.entry_meta_token.get().strip(),
            instagram_account_id=self.entry_ig_id.get().strip()
        )
        is_valid, msg = uploader.validate_credentials()
        if is_valid:
            messagebox.showinfo("Meta Graph API Success", msg)
        else:
            messagebox.showwarning("Meta Graph API Notice", msg)

    def _test_tiktok_api(self):
        uploader = TikTokUploader(access_token=self.entry_tiktok_token.get().strip())
        is_valid, msg = uploader.validate_credentials()
        if is_valid:
            messagebox.showinfo("TikTok API Success", msg)
        else:
            messagebox.showwarning("TikTok API Notice", msg)

    def _load_queue_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        posts = self.db.get_posts(limit=100)
        for p in posts:
            fname = os.path.basename(p.file_path)
            sch_text = format_delay_time(p.scheduled_time) if p.status == PostStatus.SCHEDULED.value else (p.uploaded_at or "-")
            url_text = p.remote_url or (p.error_message or "")

            self.tree.insert("", "end", values=(
                p.id,
                p.target_platform.upper(),
                fname,
                p.media_type.upper(),
                sch_text,
                p.status,
                url_text
            ))

    def _periodic_queue_refresh(self):
        self._load_queue_table()
        self._update_status_bar()
        self.root.after(5000, self._periodic_queue_refresh)

    def _on_queue_updated(self):
        self.root.after(0, self._load_queue_table)
        self.root.after(0, self._update_status_bar)

    def _on_scheduler_alert(self, title: str, message: str):
        self.root.after(0, lambda: messagebox.showwarning(title, message))
        self.root.after(0, self._update_status_bar)

    def _toggle_pause(self):
        if self.scheduler.is_paused:
            self.scheduler.resume()
            if USE_CTK:
                self.btn_pause.configure(text="⏸ Pause Queue", fg_color="#e65100")
            else:
                self.btn_pause.config(text="Pause Queue")
        else:
            self.scheduler.pause(reason="Manually paused by user")
            if USE_CTK:
                self.btn_pause.configure(text="▶ Resume Queue", fg_color="#2e7d32")
            else:
                self.btn_pause.config(text="Resume Queue")
        self._update_status_bar()

    def _update_status_bar(self):
        watcher_status = "🟢 ACTIVE" if self.watcher.is_running else "🔴 STOPPED"
        if self.scheduler.is_paused:
            sched_status = "🟠 PAUSED"
        elif self.scheduler.is_running:
            sched_status = "🟢 RUNNING"
        else:
            sched_status = "🔴 STOPPED"

        today_insta = self.db.count_uploads_today("instagram")
        today_tiktok = self.db.count_uploads_today("tiktok")
        text = f"Watcher: {watcher_status} | Scheduler: {sched_status} | Today: 📷 {today_insta}/{config_manager.config.daily_limit_insta} | 🎵 {today_tiktok}/{config_manager.config.daily_limit_tiktok}"

        if USE_CTK:
            self.status_lbl.configure(text=text)
        else:
            self.status_lbl.config(text=text)

    def _append_log(self, msg: str):
        def _do_append():
            if self.log_text:
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
        self.root.after(0, _do_append)

    def _open_insta_folder(self):
        folder = config_manager.config.watch_folder_insta
        os.makedirs(folder, exist_ok=True)
        os.startfile(folder)

    def _open_tiktok_folder(self):
        folder = config_manager.config.watch_folder_tiktok
        os.makedirs(folder, exist_ok=True)
        os.startfile(folder)

    def _on_close(self):
        try:
            self.watcher.stop()
            self.scheduler.stop()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()
