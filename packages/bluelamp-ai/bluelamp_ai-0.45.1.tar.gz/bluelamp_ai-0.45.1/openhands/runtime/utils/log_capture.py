import io
import logging
from contextlib import asynccontextmanager
@asynccontextmanager
async def capture_logs(logger_name, level=logging.ERROR):
    logger = logging.getLogger(logger_name)
    original_handlers = logger.handlers[:]
    original_level = logger.level
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(level)
    logger.handlers = [handler]
    logger.setLevel(level)
    try:
        yield log_capture
    finally:
        logger.handlers = original_handlers
        logger.setLevel(original_level)