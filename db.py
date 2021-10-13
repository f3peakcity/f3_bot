from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

engine = None
Session = None


def get_engine():
    global engine
    global Session
    if engine is None:
        engine = create_engine('bigquery://f3-carpex/backblast')
        # engine = create_engine('bigquery://f3-carpex/backblast', credentials_path='../.secret/f3-carpex-c6ae222b8cfa.json')

    return engine


def get_session():
    global engine
    global Session
    if engine is None:
        engine = get_engine()

    Session = sessionmaker(bind=engine)
    return Session()
