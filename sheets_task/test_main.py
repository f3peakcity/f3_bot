import datetime

import pytest

import model

@pytest.fixture
def backblast():
    backblast = model.Backblast(
        store_date=datetime.datetime.now(),
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
        fngs_raw="what_a_guy",
        n_visiting_pax=5
    )
    return backblast


def test_row_conversion(backblast):
    assert backblast.to_rows() == [['2021-10-20',
                                    'Torpedo',
                                    '1st F',
                                    3,
                                    'Torpedo',
                                    'QWERTY123',
                                    0,
                                    '',
                                    'what_a_guy',
                                    5,
                                    'a5b54c95d475477583e1c2a60cb6bdc7',
                                    '2021-10-20T21:08:17.834782'],
                                   ['2021-10-20',
                                    'Torpedo',
                                    '1st F',
                                    3,
                                    'Parker',
                                    'ZXCV123',
                                    0,
                                    '',
                                    'what_a_guy',
                                    5,
                                    'a5b54c95d475477583e1c2a60cb6bdc7',
                                    '2021-10-20T21:08:17.834782'],
                                   ['2021-10-20',
                                    'Torpedo',
                                    '1st F',
                                    3,
                                    'Banjo',
                                    'ASDF456',
                                    0,
                                    '',
                                    'what_a_guy',
                                    5,
                                    'a5b54c95d475477583e1c2a60cb6bdc7',
                                    '2021-10-20T21:08:17.834782']]
