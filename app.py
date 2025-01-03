import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget,
    QMessageBox, QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt
import yt_dlp


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader with yt-dlp")
        self.setGeometry(200, 200, 600, 400)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # URL Input
        self.url_label = QLabel("YouTube URL:")
        self.layout.addWidget(self.url_label)
        self.url_input = QLineEdit()
        self.layout.addWidget(self.url_input)

        # Fetch Resolutions Button
        self.fetch_button = QPushButton("Fetch Resolutions")
        self.fetch_button.clicked.connect(self.fetch_resolutions)
        self.layout.addWidget(self.fetch_button)

        # Resolutions Dropdown
        self.resolution_label = QLabel("Available Resolutions:")
        self.layout.addWidget(self.resolution_label)
        self.resolutions_combo = QComboBox()
        self.layout.addWidget(self.resolutions_combo)

        # Download Button
        self.download_button = QPushButton("Download Video")
        self.download_button.clicked.connect(self.download_video)
        self.layout.addWidget(self.download_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

    def fetch_resolutions(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL.")
            return

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'outtmpl': '%(title)s-%(id)s.%(ext)s',
                'logger': MyLogger(),
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                self.resolutions_combo.clear()
                for fmt in formats:
                    if fmt.get('height') and fmt.get('ext') == 'mp4':
                        size_mb = (fmt.get('filesize', 0) or 0) / (1024 * 1024)
                        resolution = f"{fmt['height']}p ({size_mb:.2f} MB)" if size_mb > 0 else f"{fmt['height']}p (Unknown size)"
                        self.resolutions_combo.addItem(resolution, fmt['format_id'])

            QMessageBox.information(self, "Success", "Resolutions fetched successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch resolutions: {e}")

    def download_video(self):
        url = self.url_input.text().strip()  # Get URL from input field
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL.")
            return

        # Get selected resolution from combo box
        selected_resolution = self.resolutions_combo.currentData()
        if not selected_resolution:
            QMessageBox.warning(self, "Error", "Please select a resolution.")
            return

        # Prompt user to select download folder
        download_path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not download_path:
            QMessageBox.warning(self, "Error", "No download directory selected.")
            return

        try:
            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
                    self.progress_bar.setValue(int(percent))  # Update progress bar
                elif d['status'] == 'finished':
                    self.progress_bar.setValue(100)  # Set progress bar to 100% once done

            # yt-dlp options for downloading the video with audio and video combined
            ydl_opts = {
                'format': 'bestaudio+bestaudio',  # Download the best available audio and video and combine them
                'concurrent_fragment_downloads': 4,  # Optional: download segments concurrently
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),  # Output template
                'progress_hooks': [progress_hook],  # Hook to update progress
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])  # Start downloading the video

            QMessageBox.information(self, "Success", "Download completed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download video: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
