"""ResolutionFetcherThread with mocked yt-dlp."""
from unittest.mock import MagicMock, patch

import pytest
import yt_dlp.utils

import main


def test_resolution_fetcher_emits_sorted_and_sizes(qtbot):
    formats = [
        {
            "format_note": "720p",
            "ext": "mp4",
            "filesize": 10 * 1024 * 1024,
            "format_id": "22",
        },
        {
            "format_note": "360p",
            "ext": "webm",
            "filesize": 0,
            "format_id": "43",
        },
    ]
    info_dict = {"formats": formats}

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = info_dict
    context = MagicMock()
    context.__enter__.return_value = mock_ydl
    context.__exit__.return_value = False

    with patch.object(main.yt_dlp, "YoutubeDL", return_value=context):
        thread = main.ResolutionFetcherThread(
            "https://www.youtube.com/watch?v=1"
        )
        with qtbot.waitSignal(thread.resolution_fetched, timeout=3000) as blocker:
            thread.start()
        rows = blocker.args[0]

    assert len(rows) == 2
    assert rows[0][0].startswith("360p")
    assert rows[0][1] == "43"
    assert rows[1][0].startswith("720p")
    assert "10.00 MB" in rows[1][0]
    assert rows[1][1] == "22"


def test_resolution_fetcher_no_matching_formats(qtbot):
    info_dict = {
        "formats": [
            {"format_note": "storyboard", "ext": "mhtml", "format_id": "sb0"},
        ]
    }
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = info_dict
    context = MagicMock()
    context.__enter__.return_value = mock_ydl
    context.__exit__.return_value = False

    with patch.object(main.yt_dlp, "YoutubeDL", return_value=context):
        thread = main.ResolutionFetcherThread(
            "https://www.youtube.com/watch?v=1"
        )
        with qtbot.waitSignal(thread.error_signal, timeout=3000) as blocker:
            thread.start()
        msg = blocker.args[0]

    assert "No resolutions available" in msg


def test_resolution_fetcher_download_error(qtbot):
    mock_ydl = MagicMock()
    mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("boom")
    context = MagicMock()
    context.__enter__.return_value = mock_ydl
    context.__exit__.return_value = False

    with patch.object(main.yt_dlp, "YoutubeDL", return_value=context):
        thread = main.ResolutionFetcherThread(
            "https://www.youtube.com/watch?v=1"
        )
        with qtbot.waitSignal(thread.error_signal, timeout=3000) as blocker:
            thread.start()
        msg = blocker.args[0]

    assert "Failed to fetch video info" in msg
    assert "boom" in msg


def test_resolution_fetcher_youtubedl_constructor_error(qtbot):
    """Errors before extract_info must still emit error_signal (no NameError)."""

    def raise_ctor(*a, **k):
        raise RuntimeError("ctor fail")

    with patch.object(main.yt_dlp, "YoutubeDL", side_effect=raise_ctor):
        thread = main.ResolutionFetcherThread(
            "https://www.youtube.com/watch?v=1"
        )
        with qtbot.waitSignal(thread.error_signal, timeout=3000) as blocker:
            thread.start()
        msg = blocker.args[0]

    assert "ctor fail" in msg
