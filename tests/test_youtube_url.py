"""YouTube URL validation used by ResolutionFetcherThread."""
import pytest

import main


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=1",
        "https://m.youtube.com/watch?v=1",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://YOUTU.BE/dQw4w9WgXcQ",
        "  https://www.youtube.com/watch?v=1  ",
    ],
)
def test_youtube_url_accepted(url):
    main.ResolutionFetcherThread(url.strip())


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "ftp://youtube.com/watch?v=1",
        "https://vimeo.com/123",
        "https://youtube.com.evil.com/",
    ],
)
def test_youtube_url_rejected(url):
    with pytest.raises(ValueError, match="Invalid YouTube URL"):
        main.ResolutionFetcherThread(url)
