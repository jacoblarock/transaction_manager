import logging

from utils.logs import logger


def test_logger_has_correct_level():
    assert logger.level == logging.INFO


def test_logger_has_stream_handler():
    handlers = logger.handlers
    stream_handlers = [h for h in handlers if isinstance(h, logging.StreamHandler)]
    assert len(stream_handlers) >= 1


def test_logger_does_not_propagate():
    assert logger.propagate is False


def test_logger_name():
    assert logger.name == "transaction_manager"


def test_logger_handler_formatter():
    handler = logger.handlers[0]
    assert isinstance(handler.formatter, logging.Formatter)
    assert "%(funcName)s" in handler.formatter._fmt
    assert "%(message)s" in handler.formatter._fmt
