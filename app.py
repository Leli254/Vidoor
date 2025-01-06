import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget,
    QMessageBox, QFileDialog, QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt
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


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sonic Video Downloader")
        self.setGeometry(200, 200, 600, 500)

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
        self.url_input.setPlaceholderText("Enter the YouTube video URL here...")
        self.url_layout.addWidget(self.url_label)
        self.url_layout.addWidget(self.url_input)
        self.layout.addWidget(self.url_group)

        # Step 2: Select Type (Audio/Video)
        self.type_group = QGroupBox("Step 2: Select Download Type")
        self.type_layout = QVBoxLayout()
        self.type_group.setLayout(self.type_layout)
        self.type_label = QLabel("Select download type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Video", "Audio"])
        self.type_combo.currentIndexChanged.connect(self.update_ui)
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_combo)
        self.layout.addWidget(self.type_group)

        # Step 3: Fetch Resolutions
        self.resolution_group = QGroupBox("Step 3: Choose Resolution (Video Only)")
        self.resolution_layout = QVBoxLayout()
        self.resolution_group.setLayout(self.resolution_layout)
        self.fetch_button = QPushButton("Fetch Resolutions")
        self.fetch_button.clicked.connect(self.fetch_resolutions)
        self.resolution_label = QLabel("Available Resolutions:")
        self.resolutions_combo = QComboBox()
        self.resolution_layout.addWidget(self.fetch_button)
        self.resolution_layout.addWidget(self.resolution_label)
        self.resolution_layout.addWidget(self.resolutions_combo)
        self.layout.addWidget(self.resolution_group)

        # Step 4: Download
        self.download_group = QGroupBox("Step 4: Download")
        self.download_layout = QVBoxLayout()
        self.download_group.setLayout(self.download_layout)
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_video)
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")
        self.download_layout.addWidget(self.download_button)
        self.download_layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.download_group)

        # Styling
        self.apply_styles()
        self.update_ui()  # Set initial state of UI

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
            QComboBox {
                padding: 5px;
            }
            QProgressBar {
                text-align: center;
                background-color: #e0e0e0;
                color: #000000;
            }
        """)

    def update_ui(self):
        """Update the UI based on the selected type (Audio/Video)."""
        is_video = self.type_combo.currentText() == "Video"
        self.resolution_group.setVisible(is_video)
        self.fetch_button.setEnabled(is_video)
        self.resolutions_combo.setEnabled(is_video)

    def fetch_resolutions(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL.")
            return

        try:
            ydl_opts = {'logger': MyLogger()}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                self.resolutions_combo.clear()
                for fmt in formats:
                    if fmt.get('height') and fmt.get('ext'):
                        size_mb = (fmt.get('filesize', 0) or 0) / (1024 * 1024)
                        resolution = (
                            f"{fmt['height']}p, {fmt['ext'].upper()} "
                            f"({size_mb:.2f} MB)" if size_mb > 0
                            else f"{fmt['height']}p, {fmt['ext'].upper()} (Unknown size)"
                        )
                        self.resolutions_combo.addItem(resolution, fmt['format_id'])

            QMessageBox.information(self, "Success", "Resolutions fetched successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch resolutions: {e}")

    def download_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL.")
            return

        download_type = self.type_combo.currentText()
        selected_resolution = self.resolutions_combo.currentData()

        try:
            def progress_hook(d):
                if d['status'] == 'downloading':
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes', 1)
                    percent = downloaded_bytes / total_bytes * 100
                    self.progress_bar.setFormat(f"Downloading - {int(percent)}%")
                    self.progress_bar.setValue(int(percent))
                elif d['status'] == 'finished':
                    self.progress_bar.setValue(100)
                    self.progress_bar.setFormat("Completed - 100%")

            if download_type == "Video":
                if not selected_resolution:
                    QMessageBox.warning(self, "Error", "Please select a resolution.")
                    return
                ydl_opts = {
                    'format': f"{selected_resolution}+bestaudio/best",
                    'outtmpl': os.path.join(self.downloads_folder, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'progress_hooks': [progress_hook],
                    'logger': MyLogger()
                }
            else:  # Audio
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.downloads_folder, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'progress_hooks': [progress_hook],
                    'logger': MyLogger()
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            QMessageBox.information(self, "Success", "Download completed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
