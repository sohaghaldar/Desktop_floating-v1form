# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - GitHub Auto-Updater Engine
Checks repository releases/branches, validates syntax, atomically updates, and restarts.
Supports both release ZIP packages and standalone scripts.
"""

import os
import sys
import time
import json
import urllib.request
import threading
import subprocess
import py_compile
import zipfile
import io
import stat
import tkinter.messagebox as messagebox

from core.config import APP_VERSION, IS_WINDOWS, ROOT_DIR

class GitHubAutoUpdater:
    """Built-in GitHub Auto-Updater & Version Checker:
    - Checks GitHub Releases API or raw repository branch asynchronously.
    - Compares semantic versioning (Major.Minor.Patch).
    - Can download and atomically install the latest script + modular packages + locales.
    - Seamless restart on update completion!"""
    def __init__(self, app):
        self.app = app
        self.current_version = APP_VERSION
        self.latest_version = APP_VERSION
        self.update_available = False
        self.release_url = ""
        self.release_notes = ""
        self.download_url = ""
        self.is_checking = False
        self.last_check_time = 0.0

    def get_repo(self):
        return self.app.config.get("GITHUB_REPO", "sohaghaldar/desktop-pet-ecosystem")

    def check_for_updates_async(self, on_result=None, silent=True):
        if self.is_checking:
            return
        self.is_checking = True

        def _worker():
            repo = self.get_repo()
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            headers = {"User-Agent": f"DesktopPetEcosystem-{self.current_version}"}
            found_update = False
            remote_ver = self.current_version
            notes = ""
            rel_url = f"https://github.com/{repo}/releases"
            raw_url = f"https://raw.githubusercontent.com/{repo}/main/desktop_spider.py"

            try:
                req = urllib.request.Request(api_url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        tag = data.get("tag_name", "").lstrip("v").strip()
                        notes = data.get("body", "")
                        rel_url = data.get("html_url", rel_url)
                        if tag and self.is_newer(tag, self.current_version):
                            remote_ver = tag
                            found_update = True
                            for asset in data.get("assets", []):
                                aname = asset.get("name", "")
                                if aname.endswith(".zip"):
                                    raw_url = asset.get("browser_download_url")
                                    break
                                elif aname == "desktop_spider.py":
                                    raw_url = asset.get("browser_download_url")
            except Exception:
                try:
                    ver_url = f"https://raw.githubusercontent.com/{repo}/main/VERSION"
                    v_req = urllib.request.Request(ver_url, headers=headers)
                    with urllib.request.urlopen(v_req, timeout=4) as v_resp:
                        if v_resp.status == 200:
                            v_tag = v_resp.read().decode("utf-8").strip().lstrip("v")
                            if v_tag and self.is_newer(v_tag, self.current_version):
                                remote_ver = v_tag
                                found_update = True
                except Exception:
                    pass

            self.is_checking = False
            self.last_check_time = time.time()
            self.update_available = found_update
            self.latest_version = remote_ver
            self.release_url = rel_url
            self.release_notes = notes
            self.download_url = raw_url

            if on_result:
                self.app.root.after(0, lambda: on_result(found_update, remote_ver, notes))
            elif found_update and not silent:
                self.app.root.after(0, lambda: messagebox.showinfo(
                    "Update Available",
                    f"A new version v{remote_ver} is available!\n\nOpen Settings [Shift+P] to update.",
                    parent=getattr(self.app, "settings_window", None) or self.app.root
                ))

        threading.Thread(target=_worker, daemon=True).start()

    def is_newer(self, remote_ver, local_ver):
        def parse(v):
            cleaned = str(v).lower().lstrip("v").strip()
            parts = []
            for p in cleaned.split("."):
                digits = "".join(c for c in p if c.isdigit())
                parts.append(int(digits) if digits else 0)
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts)
        return parse(remote_ver) > parse(local_ver)

    def apply_update_async(self, on_progress=None, on_success=None, on_error=None):
        def _worker():
            try:
                target_file = os.path.join(ROOT_DIR, "desktop_spider.py")
                backup_file = target_file + ".bak"
                temp_file = target_file + ".download"

                if on_progress:
                    self.app.root.after(0, lambda: on_progress("Downloading update from GitHub..."))

                req = urllib.request.Request(self.download_url, headers={"User-Agent": "DesktopPetEcosystem"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    total_bytes = int(resp.headers.get("Content-Length", 0))
                    total_mb = total_bytes / (1024 * 1024) if total_bytes > 0 else 0
                    downloaded_bytes = 0
                    chunks = []
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        chunks.append(chunk)
                        downloaded_bytes += len(chunk)
                        if on_progress:
                            dl_mb = downloaded_bytes / (1024 * 1024)
                            if total_mb > 0:
                                pct = int((downloaded_bytes / total_bytes) * 100)
                                msg = f"Downloading: {dl_mb:.1f} MB / {total_mb:.1f} MB ({pct}%)"
                            else:
                                msg = f"Downloading: {dl_mb:.1f} MB..."
                            self.app.root.after(0, lambda m=msg: on_progress(m))
                    new_code = b"".join(chunks)

                # If the asset is a full release ZIP package, extract all files (core, creatures, locales, etc.)
                if zipfile.is_zipfile(io.BytesIO(new_code)):
                    root = os.path.abspath(ROOT_DIR)
                    with zipfile.ZipFile(io.BytesIO(new_code)) as zf:
                        for info in zf.infolist():
                            member_name = info.filename.replace("\\", "/")
                            if not member_name or member_name.startswith("/"):
                                raise ValueError("Update archive contains an invalid path")
                            target_path = os.path.abspath(os.path.join(root, *member_name.split("/")))
                            try:
                                inside_root = os.path.commonpath([root, target_path]) == root
                            except ValueError:
                                inside_root = False
                            if not inside_root:
                                raise ValueError("Update archive contains a path outside the application folder")
                            mode = info.external_attr >> 16
                            if stat.S_ISLNK(mode):
                                raise ValueError("Update archive may not contain symbolic links")
                        zf.extractall(root)
                else:
                    with open(temp_file, "wb") as f:
                        f.write(new_code)

                    py_compile.compile(temp_file, doraise=True)

                    if os.path.exists(target_file):
                        with open(target_file, "rb") as rf, open(backup_file, "wb") as wf:
                            wf.write(rf.read())
                    os.replace(temp_file, target_file)

                if on_success:
                    self.app.root.after(0, on_success)
            except Exception as e:
                if on_error:
                    self.app.root.after(0, lambda: on_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def restart_app(self):
        if getattr(sys, 'frozen', False):
            try:
                subprocess.Popen([sys.executable] + sys.argv[1:])
                self.app.quit_app()
                return
            except Exception as e:
                print("[!] Error restarting frozen app:", e)
        target_script = os.path.join(ROOT_DIR, "desktop_spider.py")
        if IS_WINDOWS:
            python_exe = "pythonw.exe"
            try:
                subprocess.Popen([python_exe, target_script] + sys.argv[1:])
                self.app.quit_app()
            except Exception:
                subprocess.Popen([sys.executable, target_script] + sys.argv[1:])
                self.app.quit_app()
        else:
            try:
                subprocess.Popen([sys.executable, target_script] + sys.argv[1:])
                self.app.quit_app()
            except Exception:
                os.execv(sys.executable, [sys.executable, target_script] + sys.argv[1:])
