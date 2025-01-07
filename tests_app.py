import app
import unittest


class TestApp(unittest.TestCase):
    def test_appExists(self):
        app=
        self.assertIsNone(app)

    def test_appHasMethods(self):
        self.assertTrue(hasattr(app, 'YouTubeDownloader'))
        self.assertTrue(hasattr(app.YouTubeDownloader, 'fetch_resolutions'))
        self.assertTrue(hasattr(app.YouTubeDownloader, 'download_video'))
        self.assertTrue(hasattr(app.YouTubeDownloader, 'fetch_resolutions'))
        self.assertTrue(hasattr(app.YouTubeDownloader, 'init'))
        self.assertTrue(hasattr(app.YouTubeDownloader, 'info'))
        self.assertTrue(hasattr(app.YouTubeDownloader, 'warning'))
        self.assertTrue(hasattr(app.YouTubeDownloader, 'error'))

    def test_appMethodsAreFunctions(self):
        self.assertTrue(callable(app.YouTubeDownloader.fetch_resolutions))
        self.assertTrue(callable(app.YouTubeDownloader.download_video))
        self.assertTrue(callable(app.YouTubeDownloader.fetch_resolutions))
        self.assertTrue(callable(app.YouTubeDownloader.init))
        self.assertTrue(callable(app.YouTubeDownloader.info))
        self.assertTrue(callable(app.YouTubeDownloader.warning))
        self.assertTrue(callable(app.YouTubeDownloader.error))

    def test_fetch_resolutions(self):
        pass

    def test_download_video(self):
        pass

    def test_init(self):
        pass

    def test_info(self):
        pass

    def test_warning(self):
        pass

    def test_error(self):
        pass


if __name__ == "__main__":
    unittest.main()
