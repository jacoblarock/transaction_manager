import logging
import sys

_log = logging.getLogger("transaction_manager")
if not _log.handlers:
    _log.setLevel(logging.INFO)
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(pathname)s | %(lineno)d | %(funcName)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    _log.addHandler(_handler)
    _log.propagate = False

logger = _log
