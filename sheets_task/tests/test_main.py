import uuid
import datetime

import pytest
from unittest import mock
import sqlalchemy

from sqlalchemy_cockroachdb import run_transaction

import sheets_task.model
import sheets_task.db

mock_uuid = uuid.UUID("a5b54c95d475477583e1c2a60cb6bdc7")


@pytest.fixture
@mock.patch("sheets_task.model.uuid.uuid4", return_value=mock_uuid)
def backblast(_):
    backblast = sheets_task.model.Backblast(
        store_date=datetime.datetime(2021, 10, 20, 11, 11, 11),
        date="2021-10-20",
        ao_id="C8LR0QG5V",
        ao="1st F",
        q_id="QWERTY123",
        q="Torpedo",
        pax_ids=["ASDF456", "ZXCV123", "QWERTY123"],  # note duplication
        pax=["Banjo", "Parker", "Torpedo"],
        summary="ran, did merkins, and got swole",
        fng_ids=[],
        fngs=[],
        pax_no_slack="what_a_guy",
        n_visiting_pax=5,
        submitter="ME",
        submitter_id="QWERTY123"
    )
    return backblast


def test_row_conversion(backblast):
    rows = backblast.get_rows_model()
    expected_rows = [['2021-10-20',
                      'Torpedo',
                      '1st F',
                      3,
                      'Torpedo',
                      'QWERTY123',
                      0,
                      '_',
                      'what_a_guy',
                      5,
                      'ME',
                      'QWERTY123',
                      'a5b54c95d475477583e1c2a60cb6bdc7',
                      '2021-10-20T11:11:11'],
                     ['2021-10-20',
                      'Torpedo',
                      '1st F',
                      3,
                      'Parker',
                      'ZXCV123',
                      0,
                      '_',
                      'what_a_guy',
                      5,
                      'ME',
                      'QWERTY123',
                      'a5b54c95d475477583e1c2a60cb6bdc7',
                      '2021-10-20T11:11:11'],
                     ['2021-10-20',
                      'Torpedo',
                      '1st F',
                      3,
                      'Banjo',
                      'ASDF456',
                      0,
                      '_',
                      'what_a_guy',
                      5,
                      'ME',
                      'QWERTY123',
                      'a5b54c95d475477583e1c2a60cb6bdc7',
                      '2021-10-20T11:11:11']]

    # order isn't important
    def normalize_rows(rows):
        normalized = [
            tuple(x) for x in rows
        ]
        return set(normalized)

    assert normalize_rows(rows) == normalize_rows(expected_rows)


def test_to_rows_following_saving(backblast):
    """This test is really just educational.
    
    After commiting a transaction, sqlalchemy orm (by default) "expires" the object that was bound
    to a session, forcing it to be re-loaded if any attribute is accessed later.

    However, if the session has since been closed, a DetachedInstanceError will be raised.

    This test shows why the current design pattern--the Backblast model providing an accessor for 
    the SqlAlchemy ORM model--was chosen.
    """
    
    try:
        Session = sheets_task.db.get_cockroach_sessionmaker()
        run_transaction(Session, lambda s: s.query(sheets_task.model.SqlAlchemyBackblast).filter_by(id=backblast.id).delete())
    except Exception as e:
        raise
    
    try:
        Session = sheets_task.db.get_cockroach_sessionmaker()
        backblast_cockroach = backblast.get_sqlalchemy_model()
        run_transaction(Session, lambda s: s.add(backblast_cockroach))
    except Exception as e:
        raise

    with pytest.raises(sqlalchemy.orm.exc.DetachedInstanceError) as e:
        print(backblast_cockroach.id)

    assert "is not bound to a Session" in str(e)

    try:
        Session = sheets_task.db.get_cockroach_sessionmaker()
        run_transaction(Session, lambda s: s.query(sheets_task.model.SqlAlchemyBackblast).filter_by(id=backblast.id).delete())
    except Exception as e:
        raise
