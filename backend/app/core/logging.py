import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Set up application-wide logging once, at startup.

    Logs go to stdout rather than a file on purpose: containers and hosting platforms
    collect stdout automatically, so writing our own files would only hide them.
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
    # Replace any handlers already installed, so a reload doesn't stack duplicates and
    # print every line twice.
    root.handlers = [handler]

    # SQLAlchemy's echo already prints every statement when DEBUG is on; letting its
    # own logger through as well would duplicate all of it.
    logging.getLogger("sqlalchemy.engine").propagate = False
