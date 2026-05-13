import re
import os
import sys
import glob
import logging
import shutil
from typing import Optional, List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget,
    QMessageBox, QProgressBar, QGroupBox, QHBoxLayout,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie, QPixmap, QIcon
import yt_dlp

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

script_dir = os.path.dirname(__file__)

_YOUTUBE_URL_RE = re.compile(
    r'^https?://((www\.|m\.)?youtube\.com/|youtu\.be/)',
    re.IGNORECASE,
)


def _get_node_path() -> Optional[str]:
    """Resolve the Node.js executable, even when it is not on PATH."""
    node_path = shutil.which("node") or shutil.which("nodejs")
    if node_path:
        return node_path

    candidates: List[str] = []
    if sys.platform == "win32":
        pf = os.environ.get("ProgramFiles",      r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        appdata = os.environ.get("APPDATA", "")
        candidates = [
            os.path.join(pf,      "nodejs", "node.exe"),
            os.path.join(pf86,   "nodejs", "node.exe"),
            os.path.join(appdata, "nvm", "current", "node.exe"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/usr/local/bin/node",
            "/opt/homebrew/bin/node",
            "/usr/bin/node",
        ]
    else:
        candidates = ["/usr/bin/node",
                      "/usr/local/bin/node", "/usr/bin/nodejs"]

    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def _build_js_runtime_opt() -> dict:
    node = _get_node_path()
    return {"javascript_runtimes": [f"node:{node}"]} if node else {}


def _cleanup_part_files(folder: str) -> None:
    """Delete leftover .part / .ytdl / .temp files left by yt-dlp."""
    for pattern in ("*.part", "*.ytdl", "*.temp"):
        for f in glob.glob(os.path.join(folder, pattern)):
            try:
                os.remove(f)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

class MyLogger:
    def __init__(self, name: str = "MyLogger", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(ch)

    def debug(self, msg):   self.logger.debug(msg)
    def info(self, msg):    self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg):   self.logger.error(msg)


# ---------------------------------------------------------------------------
# Resolution fetcher thread
# ---------------------------------------------------------------------------

class ResolutionFetcherThread(QThread):
    resolution_fetched = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    ALLOWED = {'144p', '240p', '360p', '480p',
               '720p', '1080p', '1440p', '2160p'}

    def __init__(self, url: str):
        super().__init__()
        if not _YOUTUBE_URL_RE.match(url.strip()):
            raise ValueError("Invalid YouTube URL")
        self.url = url

    def run(self):
        try:
            opts = {'logger': MyLogger(), 'quiet': True, **
                    _build_js_runtime_opt()}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                result = []
                for fmt in info.get('formats', []):
                    note = fmt.get('format_note')
                    ext = fmt.get('ext')
                    if note not in self.ALLOWED or not ext:
                        continue
                    size = fmt.get('filesize', fmt.get(
                        'filesize_approx', 0)) or 0
                    size_str = f"{size / (1024*1024):.2f} MB" if size else "Unknown size"
                    result.append(
                        (f"{note} ({ext.upper()}) ({size_str})", fmt['format_id']))

                result.sort(key=lambda x: int(
                    re.search(r'(\d+)', x[0]).group(1)))
                self.resolution_fetched.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))


# ---------------------------------------------------------------------------
# Download thread  ← runs yt-dlp off the main thread so the UI stays alive
# ---------------------------------------------------------------------------

class DownloadThread(QThread):
    """
    Signals
    -------
    progress(int)           – 0-100
    status(str)             – speed / ETA line
    finished(bool, str)     – success flag + message
    """
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, url: str, ydl_opts: dict, save_folder: str):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        self.save_folder = save_folder

    def run(self):
        self.ydl_opts.setdefault('progress_hooks', [])
        self.ydl_opts['progress_hooks'].append(self._hook)

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
            _cleanup_part_files(self.save_folder)
            self.finished.emit(True, "Download complete!")
        except Exception as e:
            _cleanup_part_files(self.save_folder)
            self.finished.emit(False, str(e))

    def _hook(self, d: dict):
        status = d.get('status', '')

        if status == 'downloading':
            # _percent_str looks like "  12.3%" — strip whitespace and %
            raw = d.get('_percent_str', '').strip().replace('%', '')
            try:
                pct = int(float(raw))
            except ValueError:
                total = d.get('total_bytes') or d.get(
                    'total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                pct = int(downloaded / total * 100) if total else 0

            self.progress.emit(max(0, min(100, pct)))

            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str',   '').strip()
            parts = [p for p in (speed, f"ETA {eta}" if eta else "") if p]
            if parts:
                self.status.emit(' · '.join(parts))

        elif status == 'finished':
            self.progress.emit(100)
            self.status.emit("Processing…")

        elif status == 'error':
            self.status.emit("Error during download")


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class YouTubeDownloader(QMainWindow):
    DEFAULT_FOLDER: str = os.path.expanduser("~/Downloads")

    def __init__(self):
        super().__init__()
        self.save_folder = self.DEFAULT_FOLDER
        self._dl_thread: Optional[DownloadThread] = None

        self.setWindowTitle("Sonic Video Downloader")
        self.setGeometry(200, 200, 620, 720)

        icon_path = os.path.join(script_dir, 'Assets', 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout()
        central.setLayout(self.layout)

        # ── Step 1: URL ───────────────────────────────────────────────────
        url_group = QGroupBox("Step 1: Enter YouTube URL")
        url_layout = QVBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste your YouTube link here…")
        url_layout.addWidget(self.url_input)
        url_group.setLayout(url_layout)
        self.layout.addWidget(url_group)

        # ── Step 2: Type & Quality ────────────────────────────────────────
        type_group = QGroupBox("Step 2: Select Type and Quality")
        type_layout = QVBoxLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Select Type", "Video", "Audio"])
        self.type_combo.currentIndexChanged.connect(self.update_ui)

        self.resolution_combo = QComboBox()
        self.resolution_combo.setEnabled(False)

        loading_row = QHBoxLayout()
        self.loading_label = QLabel()
        gif_path = os.path.join(script_dir, 'Assets', 'loading.gif')
        self.loading_movie = QMovie(gif_path)
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setFixedSize(30, 30)
        self.loading_label.setScaledContents(True)
        self.loading_label.setVisible(False)
        self.loading_text = QLabel("Fetching available qualities…")
        self.loading_text.setVisible(False)
        loading_row.addWidget(self.loading_label)
        loading_row.addWidget(self.loading_text)
        loading_row.addStretch()

        type_layout.addWidget(QLabel("Download Format:"))
        type_layout.addWidget(self.type_combo)
        type_layout.addLayout(loading_row)
        type_layout.addWidget(QLabel("Quality / Resolution:"))
        type_layout.addWidget(self.resolution_combo)
        type_group.setLayout(type_layout)
        self.layout.addWidget(type_group)

        # ── Step 3: Save location ─────────────────────────────────────────
        folder_group = QGroupBox("Step 3: Save Location")
        folder_layout = QHBoxLayout()

        self.folder_display = QLineEdit(self.save_folder)
        self.folder_display.setReadOnly(True)
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self.choose_folder)

        folder_layout.addWidget(self.folder_display)
        folder_layout.addWidget(browse_btn)
        folder_group.setLayout(folder_layout)
        self.layout.addWidget(folder_group)

        # ── Step 4: Download ──────────────────────────────────────────────
        dl_group = QGroupBox("Step 4: Download")
        dl_layout = QVBoxLayout()

        self.download_button = QPushButton("▶  Start Download")
        self.download_button.clicked.connect(self.start_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #555; font-size: 12px;")

        dl_layout.addWidget(self.download_button)
        dl_layout.addWidget(self.progress_bar)
        dl_layout.addWidget(self.status_label)
        dl_group.setLayout(dl_layout)
        self.layout.addWidget(dl_group)

        # ── Footer ────────────────────────────────────────────────────────
        self.layout.addStretch()
        footer_icon = QLabel()
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            footer_icon.setPixmap(pix)
        footer_icon.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(footer_icon)

        footer_text = QLabel(
            "<h2 style='color:#0078d7;margin:0;'>Sonic Video Downloader</h2>")
        footer_text.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(footer_text)

        self.apply_styles()

    # ── Styles ────────────────────────────────────────────────────────────

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow  { background-color: #f9f9f9; }
            QGroupBox    { font-weight: bold; color: #0078d7;
                           border: 1px solid #dcdcdc; border-radius: 8px;
                           margin-top: 10px; padding: 15px; }
            QPushButton  { background-color: #0078d7; color: white;
                           border-radius: 6px; padding: 10px;
                           font-weight: bold; font-size: 13px; }
            QPushButton:hover    { background-color: #005a9e; }
            QPushButton:disabled { background-color: #cccccc; }
            QProgressBar { border: 1px solid #ccc; border-radius: 5px;
                           background: #eee; height: 22px; }
            QProgressBar::chunk { background-color: #0078d7; border-radius: 5px; }
        """)

    # ── Folder picker ─────────────────────────────────────────────────────

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Save Folder", self.save_folder,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if folder:
            self.save_folder = folder
            self.folder_display.setText(folder)

    # ── Type / resolution UI ──────────────────────────────────────────────

    def update_ui(self):
        selected = self.type_combo.currentText()
        url = self.url_input.text().strip()

        if not url and selected != "Select Type":
            QMessageBox.warning(self, "URL Missing",
                                "Please enter a valid YouTube URL first.")
            self.type_combo.setCurrentIndex(0)
            return

        if selected == "Video":
            self.resolution_combo.clear()
            self.loading_label.setVisible(True)
            self.loading_text.setVisible(True)
            self.loading_movie.start()
            self._fetch_resolutions()
        else:
            self.resolution_combo.setEnabled(False)
            self.resolution_combo.clear()
            self.loading_label.setVisible(False)
            self.loading_text.setVisible(False)

    def _fetch_resolutions(self):
        self.fetcher = ResolutionFetcherThread(self.url_input.text().strip())
        self.fetcher.resolution_fetched.connect(self._on_resolutions_ready)
        self.fetcher.error_signal.connect(self._on_fetch_error)
        self.fetcher.start()

    def _on_resolutions_ready(self, resolutions):
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        self.loading_text.setVisible(False)
        for text, fmt_id in resolutions:
            self.resolution_combo.addItem(text, fmt_id)
        self.resolution_combo.setEnabled(True)

    def _on_fetch_error(self, error):
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        self.loading_text.setVisible(False)
        QMessageBox.critical(
            self, "Error", f"Could not fetch metadata:\n{error}")

    # ── Download ──────────────────────────────────────────────────────────

    def start_download(self):
        url = self.url_input.text().strip()
        mode = self.type_combo.currentText()

        if not url:
            QMessageBox.warning(self, "No URL", "Please enter a YouTube URL.")
            return
        if mode == "Select Type":
            QMessageBox.warning(
                self, "No Type", "Please select Video or Audio.")
            return

        fmt_id = self.resolution_combo.currentData() if mode == "Video" else None

        ydl_opts = {
            'format':  f"{fmt_id}+bestaudio/best" if fmt_id else "bestaudio/best",
            'outtmpl': os.path.join(self.save_folder, '%(title)s.%(ext)s'),
            'logger':  MyLogger(),
            **_build_js_runtime_opt(),
        }

        if mode == "Audio":
            ydl_opts['postprocessors'] = [{
                'key':              'FFmpegExtractAudio',
                'preferredcodec':   'mp3',
                'preferredquality': '192',
            }]

        self.progress_bar.setValue(0)
        self.status_label.setText("Starting…")
        self.download_button.setEnabled(False)

        self._dl_thread = DownloadThread(url, ydl_opts, self.save_folder)
        self._dl_thread.progress.connect(self.progress_bar.setValue)
        self._dl_thread.status.connect(self.status_label.setText)
        self._dl_thread.finished.connect(self._on_download_finished)
        self._dl_thread.start()

    def _on_download_finished(self, success: bool, message: str):
        self.download_button.setEnabled(True)
        self.status_label.setText("")

        if success:
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Done", message)
            self.progress_bar.setValue(0)
        else:
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "Download Failed", message)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
