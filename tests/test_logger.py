"""Tests for MyLogger."""
import logging

import main


def test_my_logger_no_duplicate_handlers():
    """Re-instantiating with the same name must not stack StreamHandlers."""
    name = "VidoorDupLoggerTest"
    log = logging.getLogger(name)
    log.handlers.clear()

    main.MyLogger(name=name, level=logging.WARNING)
    main.MyLogger(name=name, level=logging.WARNING)

    assert len(log.handlers) == 1


def test_my_logger_emits(caplog):
    caplog.set_level(logging.INFO)
    logger = main.MyLogger(name="VidoorCaplogTest", level=logging.INFO)
    logger.info("hello")
    assert "hello" in caplog.text
