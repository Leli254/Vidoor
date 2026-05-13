"""YouTubeDownloader helpers and download flow (mocked network/Qt timers)."""
from unittest.mock import MagicMock, patch

import pytest

import main


@pytest.fixture
def downloader(qtbot, monkeypatch, tmp_path):
    monkeypatch.setattr(main.YouTubeDownloader, "DOWNLOADS_FOLDER", str(tmp_path))
    w = main.YouTubeDownloader()
    qtbot.addWidget(w)
    return w


def test_setup_download_options_video(downloader, tmp_path):
    opts = downloader._setup_download_options("Video", "137")
    assert opts["format"] == "137+bestaudio/best"
    assert str(tmp_path) in opts["outtmpl"]
    pp = opts["postprocessors"]
    assert any(p.get("key") == "FFmpegVideoConvertor" for p in pp)


def test_setup_download_options_audio(downloader, tmp_path):
    opts = downloader._setup_download_options("Audio", None)
    assert opts["format"] == "bestaudio/best"
    assert any(p.get("key") == "FFmpegExtractAudio" for p in opts["postprocessors"])


def test_setup_download_options_video_without_resolution_merged_best(downloader):
    """Video without a combo format_id should request merged best video+audio."""
    opts = downloader._setup_download_options("Video", None)
    assert opts["format"] == "bestvideo+bestaudio/best"


def test_update_progress_bar_downloading_video(downloader):
    downloader._update_progress_bar(
        {
            "status": "downloading",
            "downloaded_bytes": 50,
            "total_bytes": 100,
            "info_dict": {"is_audio": False},
        }
    )
    assert downloader.progress_bar.value() == 50
    assert "Video" in downloader.progress_bar.format()


def test_update_progress_bar_downloading_audio(downloader):
    downloader._update_progress_bar(
        {
            "status": "downloading",
            "downloaded_bytes": 25,
            "total_bytes": 100,
            "info_dict": {"is_audio": True},
        }
    )
    assert "Audio" in downloader.progress_bar.format()


def test_update_progress_bar_zero_total_bytes_no_division_error(downloader):
    downloader._update_progress_bar(
        {
            "status": "downloading",
            "downloaded_bytes": 0,
            "total_bytes": 0,
            "info_dict": {},
        }
    )
    assert downloader.progress_bar.value() == 0


def test_update_progress_bar_finished(downloader):
    downloader._update_progress_bar({"status": "finished", "info_dict": {}})
    assert downloader.progress_bar.value() == 100


def test_update_progress_bar_post_processing(downloader):
    downloader._update_progress_bar(
        {"status": "post_processing", "info_dict": {}}
    )
    assert "Merging" in downloader.progress_bar.format()


def test_download_video_empty_url_warns(qtbot, downloader):
    with patch.object(main.QMessageBox, "warning") as warn:
        with patch.object(main.QTimer, "singleShot") as single_shot:
            downloader.url_input.setText("   ")
            downloader.download_video()
    warn.assert_called_once()
    single_shot.assert_not_called()


def test_download_video_schedules_single_timer(qtbot, downloader):
    calls = []

    def capture(ms, callback):
        calls.append((ms, callback))

    mock_ydl = MagicMock()
    ctx = MagicMock()
    ctx.__enter__.return_value = mock_ydl
    ctx.__exit__.return_value = False

    with patch.object(main.QMessageBox, "critical"):
        with patch.object(main.QMessageBox, "warning"):
            with patch.object(main.QTimer, "singleShot", side_effect=capture):
                with patch.object(main.yt_dlp, "YoutubeDL", return_value=ctx):
                    downloader.url_input.setText(
                        "https://www.youtube.com/watch?v=1"
                    )
                    downloader.type_combo.setCurrentText("Audio")
                    downloader.download_video()
                    assert len(calls) == 1
                    assert calls[0][0] == 500
                    calls[0][1]()
    mock_ydl.download.assert_called_once()


def test_download_video_setup_failure_no_timer(qtbot, downloader):
    def boom(*a, **k):
        raise ValueError("bad options")

    with patch.object(main.QMessageBox, "critical"):
        with patch.object(main.QMessageBox, "warning"):
            with patch.object(main.QTimer, "singleShot") as single_shot:
                with patch.object(
                    downloader, "_setup_download_options", side_effect=boom
                ):
                    downloader.url_input.setText(
                        "https://www.youtube.com/watch?v=1"
                    )
                    downloader.download_video()
    single_shot.assert_not_called()
