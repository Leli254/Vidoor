import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget,
    QMessageBox, QFileDialog, QProgressBar, QGroupBox,
    QRadioButton, QButtonGroup
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
        self.setWindowTitle("Sonic YouTube Downloader")
        self.setGeometry(200, 200, 600, 600)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Header
        self.header_label = QLabel(
            "<h1 style='color: #0078d7;'>Sonic YouTube Downloader</h1>"
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

        # Step 2: Choose Download Type
        self.type_group = QGroupBox("Step 2: Choose Download Type")
        self.type_layout = QVBoxLayout()
        self.type_group.setLayout(self.type_layout)
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Audio")
        self.video_radio.setChecked(True)
        self.type_button_group = QButtonGroup()
        self.type_button_group.addButton(self.video_radio)
        self.type_button_group.addButton(self.audio_radio)
        self.type_layout.addWidget(self.video_radio)
        self.type_layout.addWidget(self.audio_radio)
        self.layout.addWidget(self.type_group)

        # Step 3: Fetch Resolutions (For Video)
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
        self.download_button.clicked.connect(self.start_download)
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")
        self.download_layout.addWidget(self.download_button)
        self.download_layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.download_group)

        # Styling
        self.apply_styles()

        # Connect radio button signals
        self.audio_radio.toggled.connect(self.update_ui_for_download_type)

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

    def update_ui_for_download_type(self):
        if self.audio_radio.isChecked():
            self.resolution_group.hide()
        else:
            self.resolution_group.show()

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

    def start_download(self):
        if self.audio_radio.isChecked():
            self.download_audio()
        else:
            self.download_video()

    def download_audio(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL.")
            return

        download_path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not download_path:
            QMessageBox.warning(self, "Error", "No download directory selected.")
            return

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'logger': MyLogger()
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            QMessageBox.information(self, "Success", "Audio downloaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download audio: {e}")

    def download_video(self):
        url = self.url_input.text().strip()
        selected_resolution = self.resolutions_combo.currentData()
        if not url or not selected_resolution:
            QMessageBox.warning(self, "Error", "Please enter a valid URL and select a resolution.")
            return

        download_path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not download_path:
            QMessageBox.warning(self, "Error", "No download directory selected.")
            return

        try:
            ydl_opts = {
                'format': f"{selected_resolution}+bestaudio/best",
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'logger': MyLogger()
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            QMessageBox.information(self, "Success", "Video downloaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download video: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
