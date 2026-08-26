import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Set up logging once, at startup.

    stdout rather than a file: containers and hosting platforms collect stdout
    automatically, so our own files would only hide the logs.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())
    # Replace rather than append, so a reload doesn't print every line twice.
    root.handlers = [handler]

    # echo already prints every statement when DEBUG is on.
    logging.getLogger("sqlalchemy.engine").propagate = False
