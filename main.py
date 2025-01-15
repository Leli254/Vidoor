import re
import os
import sys
import logging
from typing import Optional, Dict, Any, List, Tuple
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QWidget,
    QMessageBox, QProgressBar, QGroupBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QMovie, QPixmap, QIcon
import yt_dlp

# Determine the directory of the script
script_dir = os.path.dirname(__file__)


class MyLogger:
    """
    A simple logger class for custom logging.

    Args:
        name (str, optional): The name of the logger. Defaults to "MyLogger".
        level (int, optional): The logging level. Defaults to logging.INFO.

    """
    def __init__(self, name: str = "MyLogger", level: int = logging.INFO):
        """
        Initializes the logger with the given name and level.

        Args:
            name (str, optional):
                The name of the logger. Defaults to "MyLogger".
            level (int, optional): The logging level. Defaults to logging.INFO.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create console handler and set the level
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
            )
        ch.setFormatter(formatter)

        # Add the handler to the logger
        if not self.logger.handlers:  # Prevent duplicate handlers
            self.logger.addHandler(ch)

    def debug(self, msg: str) -> None:
        """
        Logs a debug message.

        Args:
            msg (str): The debug message.
        """
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        """
        Logs an info message.

        Args:
            msg (str): The info message.
        """
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        """
        Logs a warning message.

        Args:
            msg (str): The warning message.
        """
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        """
        Logs an error message.

        Args:
            msg (str): The error message.
        """
        self.logger.error(msg)


class ResolutionFetcherThread(QThread):
    """
    Fetches available video resolutions from a YouTube URL using yt_dlp.

    Emits:
        resolution_fetched:
            Signal emitted with a list of tuples containing
            resolution strings and their corresponding format IDs.
        error_signal: Signal emitted with an error message string.
    """
    resolution_fetched = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, url: str):
        """
        Initializes the thread with the given YouTube URL.

        Args:
            url (str): The URL of the YouTube video.
        """

        super().__init__()
        # Validate YouTube URL format
        if not re.match(r'https?://(www\.)?youtube\.com|youtu\.be', url):
            raise ValueError("Invalid YouTube URL")
        self.url = url
        self.allowed_resolutions = {
            '144p', '240p', '360p',
            '480p', '720p', '1080p',
            '1440p', '2160p'
            }

    def run(self):
        """
        Fetches video resolutions in a separate thread.
        """

        try:
            ydl_opts = {'logger': MyLogger(), 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                formats = info_dict.get('formats', [])
                resolutions = []

                for fmt in formats:
                    format_note = fmt.get('format_note')
                    ext = fmt.get('ext')
                    filesize = fmt.get(
                        'filesize', fmt.get('filesize_approx', 0)
                    ) or 0
                    if format_note in self.allowed_resolutions and ext:
                        size_mb = filesize / (1024 * 1024)
                        resolution = (
                            f"{format_note} ({ext.upper()}) ({size_mb:.2f} MB)"
                            if filesize > 0 else
                            f"{format_note} ({ext.upper()}) (Unknown size)"
                        )
                        resolutions.append((resolution, fmt['format_id']))

                # Sort by resolution
                resolutions.sort(key=lambda x: int(x[0].split('p')[0]))
                if resolutions:
                    self.resolution_fetched.emit(resolutions)
                else:
                    self.error_signal.emit(
                        "No resolutions available for this video."
                        )
        except yt_dlp.utils.DownloadError as e:
            error_message = (
                f"Failed to fetch video info. "
                f"Check the URL or your internet connection. Error: {str(e)}"
                )

            self.error_signal.emit(error_message)
            ydl_opts['logger'].error(error_message)

        except Exception as e:
            error_message = f"Failed to fetch resolutions: {str(e)}"
            self.error_signal.emit(error_message)
            ydl_opts['logger'].error(error_message)


class YouTubeDownloader(QMainWindow):
    """
    A Qt-based GUI application for downloading YouTube videos or audio.

    This class handles the video downloader UI, manages input from the user,
    and coordinates the download process using yt-dlp.
    """

    # Global variable for downloads folder
    DOWNLOADS_FOLDER: str = os.path.expanduser("~/Downloads")

    def __init__(self):
        """
        Initializes the main window of the YouTubeDownloader application.

        Sets up the layout, user interface elements, and connects signals.
        """
        super().__init__()
        self.setWindowTitle("Sonic Video Downloader")
        self.setGeometry(200, 200, 600, 600)
        # Set the window icon
        icon_path = os.path.join(script_dir, 'Assets', 'app_icon.ico')
        pixmap = QPixmap(icon_path).scaled(
            70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        self.setWindowIcon(QIcon(pixmap))

        # Set Downloads folder
        self.downloads_folder: str = os.path.expanduser("~/Downloads")

        # Central Widget
        self.central_widget: QWidget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout: QVBoxLayout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # App Icon
        self.icon_label: QLabel = QLabel()
        app_icon_pixmap = QPixmap(icon_path)
        self.icon_label.setPixmap(app_icon_pixmap)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.icon_label)

        # Header
        self.header_label: QLabel = QLabel(
            "<h1 style='color: #0078d7;'>Sonic Video Downloader</h1>"
            )
        self.header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        # Step 1: URL Input
        self.url_group: QGroupBox = QGroupBox("Step 1: Enter YouTube URL")
        self.url_layout: QVBoxLayout = QVBoxLayout()
        self.url_group.setLayout(self.url_layout)
        self.url_label: QLabel = QLabel("YouTube URL:")
        self.url_input: QLineEdit = QLineEdit()
        self.url_input.setPlaceholderText(
            "Enter the YouTube video or playlist URL here..."
            )
        self.url_layout.addWidget(self.url_label)
        self.url_layout.addWidget(self.url_input)
        self.layout.addWidget(self.url_group)

        # Step 2: Select Type and Resolution
        self.type_group: QGroupBox = QGroupBox(
            "Step 2: Select Download Type and Resolution"
            )
        self.type_layout: QVBoxLayout = QVBoxLayout()
        self.type_group.setLayout(self.type_layout)
        self.type_label: QLabel = QLabel("Select download type:")
        self.type_combo: QComboBox = QComboBox()
        self.type_combo.addItem("Select Type", None)
        self.type_combo.addItems(["Video", "Audio"])
        self.type_combo.setCurrentIndex(0)
        self.type_combo.setEnabled(True)
        self.type_combo.currentIndexChanged.connect(self.update_ui)
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_combo)

        # Loading animation setup
        gif_path: str = os.path.join(
            os.path.dirname(__file__), 'Assets', 'loading.gif'
            )
        self.loading_container: QHBoxLayout = QHBoxLayout()
        self.loading_label: QLabel = QLabel()
        self.loading_movie: QMovie = QMovie(gif_path)
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setFixedSize(50, 50)
        self.loading_label.setScaledContents(True)
        self.loading_label.setVisible(False)
        self.loading_container.addWidget(self.loading_label)
        self.loading_text: QLabel = QLabel("Fetching resolutions please wait")
        self.loading_text.setVisible(False)
        self.loading_container.addWidget(self.loading_text)
        self.type_layout.addLayout(self.loading_container)

        self.resolution_label: QLabel = QLabel("Select Video resolution ")
        self.resolution_combo: QComboBox = QComboBox()
        self.resolution_combo.setEnabled(False)
        self.type_layout.addWidget(self.resolution_label)
        self.type_layout.addWidget(self.resolution_combo)
        self.layout.addWidget(self.type_group)

        # Step 3: Download
        self.download_group: QGroupBox = QGroupBox("Step 3: Download")
        self.download_layout: QVBoxLayout = QVBoxLayout()
        self.download_group.setLayout(self.download_layout)

        # Load the download icon
        icon_path = os.path.join(script_dir, 'Assets', 'download.png')
        pixmap = QPixmap(icon_path)
        icon = QIcon(pixmap)  # Convert QPixmap to QIcon

        # Set up the download button with icon
        self.download_button: QPushButton = QPushButton("Download")
        self.download_button.setIcon(icon)
        self.download_button.setIconSize(pixmap.size())
        self.download_button.setLayoutDirection(Qt.LeftToRight)
        self.download_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 5px; /* Adjust padding as needed */
            }
        """)
        self.download_button.clicked.connect(self.download_video)
        self.progress_bar: QProgressBar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")
        self.download_layout.addWidget(self.download_button)
        self.download_layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.download_group)

        # Styling
        self.apply_styles()

    def apply_styles(self) -> None:
        """
        Applies custom styles to the UI elements of the application.

        This method uses Qt style sheets to define visual properties like
        background color, font size, colors, borders, and hover effects for
        various widgets including QMainWindow, QLabel, QGroupBox, QLineEdit,
        QPushButton, and QProgressBar.

        :return: None
        """
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

    def check_url_input(self) -> None:
        url: str = self.url_input.text().strip()
        if url:
            self.type_combo.setEnabled(True)
        else:
            self.type_combo.setEnabled(False)
            self.type_combo.setCurrentIndex(0)  # Reset to placeholder
            self.resolution_combo.clear()
            self.resolution_combo.setEnabled(False)

    def update_ui(self) -> None:
        """
        Adjusts UI elements based on the selected download type.
        """
        selected_type: str = self.type_combo.currentText()
        if not self.url_input.text().strip():
            QMessageBox.warning(
                self, "URL Required",
                "Please provide a YouTube URL before selecting download type."
                )
            self.type_combo.setCurrentIndex(0)
            return

        if selected_type == "Audio":
            self.progress_bar.setFormat("Ready to download audio.")
            self.resolution_combo.setEnabled(False)
            self.resolution_combo.clear()
            self.loading_label.setVisible(False)
            self.loading_text.setVisible(False)
        elif selected_type == "Video":
            self.progress_bar.setFormat("Ready to download video.")
            self.resolution_combo.setEnabled(False)  # Disable while fetching
            self.resolution_combo.clear()
            self.loading_label.setVisible(True)
            self.loading_text.setVisible(True)
            self.loading_movie.start()
            self.fetch_resolutions_in_background()
        else:  # Placeholder 'Select Type' is selected
            self.progress_bar.setFormat("Please select download type.")
            self.resolution_combo.setEnabled(False)
            self.resolution_combo.clear()
            self.loading_label.setVisible(False)
            self.loading_text.setVisible(False)

    def fetch_resolutions_in_background(self) -> None:
        """
        Starts a background thread to fetch available resolutions for a video.

        This method creates and starts a worker thread,
        that fetches the available
        resolutions for the provided URL.
        """
        url: str = self.url_input.text().strip()
        self.fetcher_thread: ResolutionFetcherThread = (
            ResolutionFetcherThread(url)
        )
        self.fetcher_thread.resolution_fetched.connect(
            self.on_resolutions_fetched
        )
        self.fetcher_thread.error_signal.connect(self.on_fetch_error)
        self.fetcher_thread.start()

    def on_resolutions_fetched(
            self, resolutions: List[Tuple[str, str]]
    ) -> None:
        """
        Handles the fetched resolutions and updates the resolution combo box.

        Displays available resolutions in the resolution combo box, or shows an
        information message if no resolutions are available.
        """
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        self.loading_text.setVisible(False)
        if resolutions:
            self.resolution_combo.clear()
            for res in resolutions:
                resolution_str, format_id = res
                self.resolution_combo.addItem(
                    f"{resolution_str} - {format_id}", format_id
                    )
            self.resolution_combo.setEnabled(True)
        else:
            QMessageBox.information(
                self,
                "Info", "No resolutions available for this video."
                )
            self.resolution_combo.setEnabled(False)

    def on_fetch_error(self, error_message: str) -> None:
        """
        Handle errors encountered while fetching video resolutions.

        This method is called when an error occurs during,
        the resolution fetching process.
        It stops the loading animation,
        hides the loading indicator, shows an error message
        to the user via a dialog,
        and disables the resolution selection dropdown.

        :param error_message: The error message string to display to the user.
        """
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        QMessageBox.critical(self, "Error", error_message)
        self.resolution_combo.setEnabled(False)

    def download_video(self) -> None:
        """
        Initiate the download process for a YouTube video or audio.

        This method collects the URL, download type,
        and resolution (if applicable)
        from the UI, sets up the download options,
        and attempts to download the content.
        It also manages the UI state during and after the download process.

        :raises Exception:
            Any exception that occurs during the download process is
            caught and displayed to the user.
        """
        url: str = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(
                self, "Error", "Please enter a valid YouTube URL."
                )
            return

        download_type: str = self.type_combo.currentText()
        resolution: Optional[str] = (
            self.resolution_combo.currentData()
            if download_type == "Video"
            else None
        )
        self.download_button.setEnabled(False)

        # Set initial message on the progress bar
        self.progress_bar.setFormat("Download initiated, please wait...")
        self.progress_bar.setValue(0)
        QApplication.processEvents()  # Ensure immediate UI update

        # Use QTimer for non-blocking delay
        # Use QTimer for non-blocking delay
        QTimer.singleShot(
            500,
            lambda: self._perform_download(
                url, ydl_opts
            )
        )
        QApplication.processEvents()  # Process UI events to update the display

        try:
            ydl_opts: Dict[str, Any] = self._setup_download_options(
                download_type, resolution
                )
            # Correct to:
            QTimer.singleShot(
                500, lambda: self._perform_download(url, ydl_opts)
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download: {e}")
        finally:
            self.download_button.setEnabled(True)

    def _setup_download_options(
            self, download_type: str, resolution: Optional[str]
    ) -> Dict[str, Any]:
        """Set up yt-dlp options based on download type (video or audio)."""
        ydl_opts: Dict[str, Any] = {
            'format': (
                f"{resolution}+bestaudio/best"
                if resolution else 'bestaudio/best'
            ),
            'outtmpl': (
                os.path.join(self.DOWNLOADS_FOLDER, '%(title)s.%(ext)s')
                ),
            'concurrent_fragments': 4,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'retries': 3,
            'verbose': True,
            'logger': MyLogger(),
        }

        if download_type == "Audio":
            ydl_opts.update(self._get_audio_postprocessors())
        else:
            ydl_opts.update(self._get_video_postprocessors())

        return ydl_opts

    def _get_audio_postprocessors(self) -> Dict[str, Any]:
        """Return postprocessor options for audio downloads."""
        return {
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                    },
                {'key': 'EmbedThumbnail'},
            ]
        }

    def _get_video_postprocessors(self) -> Dict[str, Any]:
        """Return postprocessor options for video downloads."""
        return {
            'postprocessors': [
                {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}
                ],
            'postprocessor_args': ['-c', 'copy'],
        }

    def _perform_download(self, url: str, ydl_opts: Dict[str, Any]) -> None:
        """Download the video/audio using yt-dlp."""
        def progress_hook(d: Dict[str, Any]) -> None:
            self._update_progress_bar(d)

        ydl_opts['progress_hooks'] = [progress_hook]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def _update_progress_bar(self, d: Dict[str, Any]) -> None:
        """Update the progress bar based on the download status."""
        if d['status'] == 'downloading':
            downloaded_bytes: int = d.get('downloaded_bytes', 0)
            total_bytes: int = d.get('total_bytes', 1)
            percent: float = downloaded_bytes / total_bytes * 100
            status: str = (
                "Downloading Audio"
                if d['info_dict'].get('is_audio')
                else "Downloading Video"
            )
            self.progress_bar.setFormat(f"{status} - {int(percent)}%")
            self.progress_bar.setValue(int(percent))

        elif d['status'] == 'finished':
            self.progress_bar.setFormat("Download Completed - 100%")
            self.progress_bar.setValue(100)

        elif d['status'] == 'post_processing':
            self.progress_bar.setFormat("Merging Audio and Video...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
