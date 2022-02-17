import logging
import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

engine = None
Sesaion = None

_cockroach_engine = None
_cockroach_session = None


def get_cockroach_engine():
    global _cockroach_engine
    if _cockroach_engine is None:
        connection_string = os.environ.get("COCKROACH_CONNECTION_STRING")
        if not connection_string:
            logger.error("No connection string available; please set COCKROACH_CONNECTION_STRING environment variable.")
            exit()
        _cockroach_engine = create_engine(connection_string)
    return _cockroach_engine


def get_cockroach_sessionmaker():
    global _cockroach_session
    if _cockroach_session is None:
        engine = get_cockroach_engine()
        _cockroach_session = sessionmaker(engine)
    return _cockroach_session
