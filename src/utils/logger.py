"""Application rotating file logger and thread-safe UI status message queue."""

import logging
from logging.handlers import QueueHandler, RotatingFileHandler
from pathlib import Path
import queue
from src.utils.config import get_app_log_level

_LOG_QUEUE: queue.Queue[logging.LogRecord] = queue.Queue(maxsize=500)
_INITIALIZED = False


def get_log_dir() -> Path:
    """Return the user's application log directory (~/.smart_markdown_publisher)."""
    log_dir = Path.home() / ".smart_markdown_publisher"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_log_file_path() -> Path:
    """Return the full path to ~/.smart_markdown_publisher/app.log."""
    return get_log_dir() / "app.log"


def get_ui_log_queue() -> queue.Queue[logging.LogRecord]:
    """Return the thread-safe queue containing log records for UI status consumption."""
    return _LOG_QUEUE


class NonBlockingQueueHandler(QueueHandler):
    """Thread-safe QueueHandler that drops oldest record if the UI queue is full."""

    def enqueue(self, record: logging.LogRecord) -> None:
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            try:
                self.queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.queue.put_nowait(record)
            except queue.Full:
                pass


def get_logger(name: str = "smart_markdown_publisher") -> logging.Logger:
    """Configure and return a logger with rotating file output and UI queue handler."""
    global _INITIALIZED
    root_logger = logging.getLogger("smart_markdown_publisher")

    if not _INITIALIZED:
        level_name = get_app_log_level()
        level = getattr(logging, level_name, logging.INFO)
        root_logger.setLevel(level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        try:
            file_handler = RotatingFileHandler(
                get_log_file_path(),
                maxBytes=2 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except OSError:
            # Fallback if home directory is read-only
            pass

        queue_handler = NonBlockingQueueHandler(_LOG_QUEUE)
        queue_handler.setFormatter(formatter)
        root_logger.addHandler(queue_handler)

        _INITIALIZED = True

    if name == "smart_markdown_publisher" or name.startswith("smart_markdown_publisher."):
        return logging.getLogger(name)
    return logging.getLogger(f"smart_markdown_publisher.{name}")
