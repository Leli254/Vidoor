import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget,
    QMessageBox, QFileDialog, QProgressBar, QGroupBox
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
        self.setWindowTitle("Sonic YouTube Downloader")
        self.setGeometry(200, 200, 600, 500)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Header
        self.header_label = QLabel("<h1 style='color: #0078d7;'>Sonic YouTube Downloader</h1>")
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

        # Step 2: Fetch Resolutions
        self.resolution_group = QGroupBox("Step 2: Choose Resolution")
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

        # Step 3: Download Video
        self.download_group = QGroupBox("Step 3: Download Video")
        self.download_layout = QVBoxLayout()
        self.download_group.setLayout(self.download_layout)
        self.download_button = QPushButton("Download Video")
        self.download_button.clicked.connect(self.download_video)
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.download_layout.addWidget(self.download_button)
        self.download_layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.download_group)

        # Styling
        self.apply_styles()

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
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #32CD32;  /* Lime Green */
                border-radius: 5px;
            }
        """)

    def fetch_resolutions(self):
        # Fetching resolutions logic as before
        pass

    def download_video(self):
        # Download video logic as before
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
