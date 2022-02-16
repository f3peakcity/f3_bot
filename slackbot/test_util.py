from sheets_task.util import build_message


def test_message_basic():
    backblast_data = {
        "date": "2021-10-20",
        "ao_id": "C8LR0QG5V",
        "ao": "1st F",
        "q_id": "QWERTY123",
        "q": "Torpedo",
        "pax_ids": ["ASDF456", "ZXCV123", "QWERTY123"],  # note duplication
        "pax": ["Banjo", "Parker", "Torpedo"],
        "summary": "ran, did merkins, and got swole",
        "fng_ids": [],
        "fngs": [],
        "pax_no_slack": "what_a_guy",
        "n_visiting_pax": 0
    }
    assert build_message(backblast_data, None) == """3 posted at <#C8LR0QG5V>.
ran, did merkins, and got swole
<@ASDF456>, <@ZXCV123> (<@QWERTY123> Q)
Pax not yet in slack: what_a_guy"""


def test_message_visitors():
    backblast_data = {
        "date": "2021-10-20",
        "ao_id": "C8LR0QG5V",
        "ao": "1st F",
        "q_id": "QWERTY123",
        "q": "Torpedo",
        "pax_ids": ["ASDF456", "ZXCV123", "QWERTY123"],  # note duplication
        "pax": ["Banjo", "Parker", "Torpedo"],
        "summary": "ran, did merkins, and got swole",
        "fng_ids": [],
        "fngs": [],
        "pax_no_slack": "what_a_guy",
        "n_visiting_pax": 5
    }
    assert build_message(backblast_data, None) == """8 posted at <#C8LR0QG5V>.
ran, did merkins, and got swole
<@ASDF456>, <@ZXCV123> (<@QWERTY123> Q)
Pax not yet in slack: what_a_guy
Joined by 5 from outside our region."""