import unittest
import app
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout,
    QLineEdit, QComboBox,
)
from app import MyLogger, ResolutionFetcherThread, YouTubeDownloader


class TestMyLogger(unittest.TestCase):
    def setUp(self):
        self.logger = MyLogger()

    def test_debug(self):
        with patch('builtins.print') as mock_print:
            self.logger.debug("test message")
            mock_print.assert_not_called()

    def test_info(self):
        with patch('builtins.print') as mock_print:
            self.logger.info("info message")
            mock_print.assert_called_once_with("info message")

    def test_warning(self):
        with patch('builtins.print') as mock_print:
            self.logger.warning("warning message")
            mock_print.assert_called_once_with("WARNING: warning message")

    def test_error(self):
        with patch('builtins.print') as mock_print:
            self.logger.error("error message")
            mock_print.assert_called_once_with("ERROR: error message")


class TestResolutionFetcherThread(unittest.TestCase):
    @patch('yt_dlp.YoutubeDL')
    def test_run_with_resolutions(self, mock_ydl):
        mock_ydl_instance = mock_ydl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {
            'formats': [
                {'format_note': '720p', 'ext': 'mp4', 'format_id': 'format_id_1', 'filesize': 1024*1024},
                {'format_note': '1080p', 'ext': 'mp4', 'format_id': 'format_id_2', 'filesize': 2*1024*1024}
            ]
        }

        thread = ResolutionFetcherThread("test_url")
        thread.resolution_fetched = Mock()
        thread.error_signal = Mock()

        thread.run()

        thread.resolution_fetched.emit.assert_called_once()
        thread.error_signal.emit.assert_not_called()

    @patch('yt_dlp.YoutubeDL')
    def test_run_no_resolutions(self, mock_ydl):
        mock_ydl_instance = mock_ydl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {'formats': []}

        thread = ResolutionFetcherThread("test_url")
        thread.resolution_fetched = Mock()
        thread.error_signal = Mock()

        thread.run()

        thread.resolution_fetched.emit.assert_not_called()
        thread.error_signal.emit.assert_called_once_with("No resolutions available for this video.")

    @patch('yt_dlp.YoutubeDL')
    def test_run_with_exception(self, mock_ydl):
        mock_ydl_instance = mock_ydl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.side_effect = Exception("Test exception")

        thread = ResolutionFetcherThread("test_url")
        thread.resolution_fetched = Mock()
        thread.error_signal = Mock()

        thread.run()

        thread.resolution_fetched.emit.assert_not_called()
        thread.error_signal.emit.assert_called_once_with("Failed to fetch resolutions: Test exception")


class TestYouTubeDownloader(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])  # PyQt needs a QApplication instance
        self.downloader = YouTubeDownloader()

    def test_init(self):
        # Here you could check initial state, like if certain widgets exist, etc.
        self.assertIsInstance(self.downloader.layout, QVBoxLayout)
        self.assertIsInstance(self.downloader.url_input, QLineEdit)
        self.assertIsInstance(self.downloader.type_combo, QComboBox)

    def test_check_url_input(self):
        # Test when URL is provided
        self.downloader.url_input.setText("test_url")
        self.downloader.check_url_input()
        self.assertTrue(self.downloader.type_combo.isEnabled())

        # Test when URL is empty
        self.downloader.url_input.setText("")
        self.downloader.check_url_input()
        self.assertFalse(self.downloader.type_combo.isEnabled())

    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_update_ui_no_url(self, mock_warning):
        self.downloader.url_input.setText("")
        self.downloader.update_ui()
        mock_warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()
