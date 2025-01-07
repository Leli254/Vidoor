import sys
import os
import signal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget,
    QMessageBox, QProgressBar, QGroupBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
import yt_dlp


class MyLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        print(msg)

    def warning(self, msg):
        print(f"WARNING: {msg}")

    def error(self, msg):
        print(f"ERROR: {msg}")


class ResolutionFetcherThread(QThread):
    resolution_fetched = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        # YouTube resolutions to filter
        self.allowed_resolutions = {
            '144p', '240p', '360p',
            '480p', '720p', '1080p',
            '1440p', '2160p'
            }

    def run(self):
        try:
            ydl_opts = {'logger': MyLogger()}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                formats = info_dict.get('formats', [])
                resolutions = []

                for fmt in formats:
                    format_note = fmt.get('format_note')
                    ext = fmt.get('ext')
                    filesize = fmt.get('filesize', 0) or 0  # Default to 0 if not available
                    if format_note in self.allowed_resolutions and ext:
                        size_mb = filesize / (1024 * 1024)
                        resolution = (
                            f"{format_note} ({ext.upper()}) "
                            f"({size_mb:.2f} MB)" if filesize > 0
                            else f"{format_note} ({ext.upper()}) (Unknown size)"
                        )
                        resolutions.append((resolution, fmt['format_id']))

                if resolutions:
                    self.resolution_fetched.emit(resolutions)
                else:
                    self.error_signal.emit("No resolutions available for this video.")
        except Exception as e:
            error_message = f"Failed to fetch resolutions: {str(e)}"
            print(f"Error: {error_message}")  # Log error
            self.error_signal.emit(error_message)


class YouTubeDownloader(QMainWindow):
    # Global variable for downloads folder
    DOWNLOADS_FOLDER = os.path.expanduser("~/Downloads")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sonic Video Downloader")
        self.setGeometry(200, 200, 600, 600)

        # Set Downloads folder
        self.downloads_folder = os.path.expanduser("~/Downloads")

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Header
        self.header_label = QLabel(
            "<h1 style='color: #0078d7;'>Sonic Video Downloader</h1>"
        )
        self.header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        # Step 1: URL Input
        self.url_group = QGroupBox("Step 1: Enter YouTube URL")
        self.url_layout = QVBoxLayout()
        self.url_group.setLayout(self.url_layout)
        self.url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter the YouTube video or playlist URL here...")
        self.url_layout.addWidget(self.url_label)
        self.url_layout.addWidget(self.url_input)

        self.layout.addWidget(self.url_group)

        # Step 2: Select Type and Resolution
        self.type_group = QGroupBox("Step 2: Select Download Type and Resolution")
        self.type_layout = QVBoxLayout()
        self.type_group.setLayout(self.type_layout)

        self.type_label = QLabel("Select download type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Video", "Audio"])
        self.type_combo.currentIndexChanged.connect(self.update_ui)
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_combo)

        # Loading animation setup
        self.loading_container = QHBoxLayout()

        self.loading_label = QLabel()
        self.loading_movie = QMovie("/home/leli/Projects/Youtube-Downloader/Sonic/Assets/loading.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setFixedSize(50, 50)
        self.loading_label.setScaledContents(True)
        self.loading_label.setVisible(False)
        self.loading_container.addWidget(self.loading_label)

        self.loading_text = QLabel("Fetching resolutions please wait")
        self.loading_text.setVisible(False)
        self.loading_container.addWidget(self.loading_text)

        self.type_layout.addLayout(self.loading_container)

        self.resolution_label = QLabel("Select Video resolution ")
        self.resolution_combo = QComboBox()
        self.resolution_combo.setEnabled(False)
        self.type_layout.addWidget(self.resolution_label)
        self.type_layout.addWidget(self.resolution_combo)

        self.layout.addWidget(self.type_group)

        # Step 3: Download
        self.download_group = QGroupBox("Step 3: Download")
        self.download_layout = QVBoxLayout()
        self.download_group.setLayout(self.download_layout)
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_video)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.confirm_cancel)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")

        self.download_layout.addWidget(self.download_button)
        self.download_layout.addWidget(self.progress_bar)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.cancel_button)
        self.download_layout.addLayout(self.button_layout)

        self.layout.addWidget(self.download_group)

        # Styling
        self.apply_styles()

        # State for tracking processes
        self.download_process = None
        self.cancel_requested = False

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f4f4;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #0078d7;
                border: 1px solid #0078d7;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QLineEdit {
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QProgressBar {
                text-align: center;
                background-color: #e0e0e0;
                color: #000000;
            }
        """)

    def update_ui(self):
        """
        Adjusts UI elements based on the selected download type.
        """
        if self.type_combo.currentText() == "Audio":
            self.progress_bar.setFormat("Ready to download audio.")
            self.resolution_combo.setEnabled(False)
            self.resolution_combo.clear()
            self.loading_label.setVisible(False)
            self.loading_text.setVisible(False)
        else:
            self.progress_bar.setFormat("Ready to download video.")
            self.resolution_combo.setEnabled(False)  # Disable while fetching
            self.resolution_combo.clear()
            self.loading_label.setVisible(True)
            self.loading_text.setVisible(True)
            self.loading_movie.start()
            self.fetch_resolutions_in_background()

    def fetch_resolutions_in_background(self):
        url = self.url_input.text().strip()
        self.fetcher_thread = ResolutionFetcherThread(url)
        self.fetcher_thread.resolution_fetched.connect(self.on_resolutions_fetched)
        self.fetcher_thread.error_signal.connect(self.on_fetch_error)
        self.fetcher_thread.start()

    def on_resolutions_fetched(self, resolutions):
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        self.loading_text.setVisible(False)
        if resolutions:
            self.resolution_combo.clear()
            for res in resolutions:
                resolution_str, format_id = res
                self.resolution_combo.addItem(f"{resolution_str} - {format_id}", format_id)
            self.resolution_combo.setEnabled(True)
        else:
            QMessageBox.information(self, "Info", "No resolutions available for this video.")
            self.resolution_combo.setEnabled(False)

    def on_fetch_error(self, error_message):
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        QMessageBox.critical(self, "Error", error_message)
        self.resolution_combo.setEnabled(False)

    def confirm_cancel(self):
        if QMessageBox.question(
                self, "Confirm Cancel", "Are you sure you want to cancel the download?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.cancel_download()

    def cancel_download(self):
        self.cancel_requested = True
        if self.download_process:
            os.killpg(os.getpgid(self.download_process.pid), signal.SIGTERM)
            self.download_process = None
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Canceled")
        self.cancel_button.setEnabled(False)
        self.download_button.setEnabled(True)

    def download_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL.")
            return

        download_type = self.type_combo.currentText()
        if download_type == "Video":
            # Use format_id instead of the full resolution string
            resolution = self.resolution_combo.currentData()
        else:
            resolution = None  # For audio, use default format

        self.cancel_button.setEnabled(True)
        self.download_button.setEnabled(False)
        self.cancel_requested = False

        try:
            def progress_hook(d):
                if self.cancel_requested:
                    raise KeyboardInterrupt

                if d['status'] == 'downloading':
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes', 1)
                    percent = downloaded_bytes / total_bytes * 100
                    self.progress_bar.setFormat(f"Downloading - {int(percent)}%")
                    self.progress_bar.setValue(int(percent))
                elif d['status'] == 'finished':
                    self.progress_bar.setValue(100)
                    self.progress_bar.setFormat("Completed - 100%")

            ydl_opts = {
                'format': f"{resolution}+bestaudio/best",
                'outtmpl': os.path.join(YouTubeDownloader.DOWNLOADS_FOLDER, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'concurrent_fragments': 4,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'retries': 3,
                'verbose': True,
                'logger': MyLogger(),
            }

            if download_type == "Audio":
                ydl_opts.update({
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192'
                        },
                        {'key': 'EmbedThumbnail'},
                    ]
                })
            else:
                ydl_opts.update({
                    'postprocessors': [
                        {
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4'
                        },
                    ],
                    'postprocessor_args': ['-c', 'copy'],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            QMessageBox.information(self, "Success", "Download completed successfully.")
        except KeyboardInterrupt:
            self.cancel_download()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download: {e}")
        finally:
            self.cancel_button.setEnabled(False)
            self.download_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())