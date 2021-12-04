import logging
import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

engine = None
Session = None

_cockroach_engine = None
_cockroach_session = None


def get_engine():
    global engine
    global Session
    if engine is None:
        engine = create_engine('bigquery://f3-carpex/backblast')
    return engine


def get_session():
    global engine
    global Session
    if engine is None:
        engine = get_engine()

    Session = sessionmaker(bind=engine)
    return Session()


def get_cockroach_engine():
    global _cockroach_engine
    if _cockroach_engine is None:
        connection_string = os.environ.get("CONNECTION_STRING")
        if not connection_string:
            logger.error("No connection string available; please set CONNECTION_STRING environment variable.")

        _cockroach_engine = create_engine(connection_string)
    return _cockroach_engine


def get_cockroach_sessionmaker():
    global _cockroach_session
    if _cockroach_session is None:
        engine = get_cockroach_engine()
        _cockroach_session = sessionmaker(engine)
    return _cockroach_session
