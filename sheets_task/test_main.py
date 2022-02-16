import uuid
import datetime

import pytest
from unittest import mock

from sqlalchemy_cockroachdb import run_transaction

import model
from sheets_task import db

mock_uuid = uuid.UUID("a5b54c95d475477583e1c2a60cb6bdc7")


@pytest.fixture
@mock.patch("model.uuid.uuid4", return_value=mock_uuid)
def backblast(_):
    backblast = model.Backblast(
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
    rows = backblast.to_rows()
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
    try:
        Session = db.get_cockroach_sessionmaker()
        run_transaction(Session, lambda s: s.add(backblast))
    except Exception as e:
        print(e)

    spreadsheet_request_body = {
        "values": backblast.to_rows()
    }

    print(spreadsheet_request_body)
