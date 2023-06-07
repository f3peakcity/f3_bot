import pytest
from unittest.mock import MagicMock, patch

from slackbot.main import handle_backblast_submit, _parse_backblast_body

@pytest.fixture
def view_submission_no_ao():
    body = {
        "type": "view_submission",
        "team": {"id": "Tisateamid", "domain": "f3paxmatedev"},
        "user": {
            "id": "Uisauserid",
            "username": "jcampbelldev",
            "name": "jcampbelldev",
            "team_id": "Tisateamid",
        },
        "api_app_id": "Aappid9",
        "token": "imatoken",
        "trigger_id": "5378395399268.4742077510288.isnotevenarealtriggerid",
        "view": {
            "id": "Visaviewid",
            "team_id": "Tisateamid",
            "type": "modal",
            "blocks": [
                {
                    "type": "actions",
                    "block_id": "date-ao-q",
                    "elements": [
                        {
                            "type": "datepicker",
                            "action_id": "date-select",
                            "initial_date": "2023-06-05",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select date",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "channels_select",
                            "action_id": "ao-select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select an AO by channel",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "users_select",
                            "action_id": "q-select",
                            "initial_user": "Uisauserid",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select Q",
                                "emoji": True,
                            },
                        },
                    ],
                },
                {
                    "type": "input",
                    "block_id": "pax-select",
                    "label": {
                        "type": "plain_text",
                        "text": "Pax (1 selected)",
                        "emoji": True,
                    },
                    "optional": False,
                    "dispatch_action": True,
                    "element": {
                        "type": "multi_users_select",
                        "action_id": "pax-select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "1 selected",
                            "emoji": True,
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "summary",
                    "label": {"type": "plain_text", "text": "Summary", "emoji": True},
                    "optional": True,
                    "dispatch_action": False,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "summary",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Workout summary",
                            "emoji": True,
                        },
                        "multiline": True,
                        "dispatch_action_config": {
                            "trigger_actions_on": ["on_enter_pressed"]
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "fng-select",
                    "label": {"type": "plain_text", "text": "FNGs", "emoji": True},
                    "optional": True,
                    "dispatch_action": False,
                    "element": {
                        "type": "multi_users_select",
                        "action_id": "fng-select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "FNGs",
                            "emoji": True,
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "pax-no-slack",
                    "label": {
                        "type": "plain_text",
                        "text": "Additional Pax?",
                        "emoji": True,
                    },
                    "optional": True,
                    "dispatch_action": False,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "pax-no-slack",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Pax Not Yet on Slack",
                            "emoji": True,
                        },
                        "dispatch_action_config": {
                            "trigger_actions_on": ["on_enter_pressed"]
                        },
                    },
                },
                {
                    "type": "input",
                    "block_id": "visiting-pax",
                    "label": {
                        "type": "plain_text",
                        "text": "Visiting PAX",
                        "emoji": True,
                    },
                    "optional": True,
                    "dispatch_action": False,
                    "element": {
                        "type": "static_select",
                        "action_id": "visiting-pax",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "How many PAX from another region?",
                            "emoji": True,
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "0",
                                    "emoji": True,
                                },
                                "value": "0",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "1",
                                    "emoji": True,
                                },
                                "value": "1",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "2",
                                    "emoji": True,
                                },
                                "value": "2",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "3",
                                    "emoji": True,
                                },
                                "value": "3",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "4",
                                    "emoji": True,
                                },
                                "value": "4",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "5",
                                    "emoji": True,
                                },
                                "value": "5",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "6",
                                    "emoji": True,
                                },
                                "value": "6",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "7",
                                    "emoji": True,
                                },
                                "value": "7",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "8",
                                    "emoji": True,
                                },
                                "value": "8",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "9",
                                    "emoji": True,
                                },
                                "value": "9",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "10+",
                                    "emoji": True,
                                },
                                "value": "10+",
                            },
                        ],
                    },
                },
            ],
            "private_metadata": '{"initial_channel": "Cisachannelid", "team": "Tisateamid"}',
            "callback_id": "backblast_modal",
            "state": {
                "values": {
                    "date-ao-q": {
                        "date-select": {
                            "type": "datepicker",
                            "selected_date": "2023-06-05",
                        },
                        "ao-select": {
                            "type": "channels_select",
                            "selected_channel": None,
                        },
                        "q-select": {
                            "type": "users_select",
                            "selected_user": "Uisauserid",
                        },
                    },
                    "pax-select": {
                        "pax-select": {
                            "type": "multi_users_select",
                            "selected_users": ["Uisauserid"],
                        }
                    },
                    "summary": {
                        "summary": {"type": "plain_text_input", "value": "asdfsad"}
                    },
                    "fng-select": {
                        "fng-select": {
                            "type": "multi_users_select",
                            "selected_users": [],
                        }
                    },
                    "pax-no-slack": {
                        "pax-no-slack": {"type": "plain_text_input", "value": None}
                    },
                    "visiting-pax": {
                        "visiting-pax": {
                            "type": "static_select",
                            "selected_option": None,
                        }
                    },
                }
            },
            "hash": "1685991526.FGKdT3jB",
            "title": {"type": "plain_text", "text": "F3 PaxMate", "emoji": True},
            "clear_on_close": False,
            "notify_on_close": False,
            "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "previous_view_id": None,
            "root_view_id": "Visaviewid",
            "app_id": "Aappid9",
            "external_id": "",
            "app_installed_team_id": "Tisateamid",
            "bot_id": "Bisabotid",
        },
        "response_urls": [],
        "is_enterprise_install": False,
        "enterprise": None,
    }
    return body

@patch("slackbot.main.app")
@patch("slackbot.main.json")
def test_parse_backblast_body(mock_json, mock_app, view_submission_no_ao):
    mock_logger = MagicMock()
    body = _parse_backblast_body(view_submission_no_ao, mock_logger)
    assert body["date"] == "2023-06-05"
    assert mock_app.client.conversations_info.call_count == 1
    assert mock_json.dumps.call_count == 1
    assert mock_logger.error.call_args_list == []
    assert mock_logger.info.call_count == 0
    assert mock_logger.error.call_count == 0



def test_handle_backblast_submission(view_submission_no_ao):
    ack = MagicMock()
    body = view_submission_no_ao
    logger = MagicMock()
    with patch("slackbot.main.client") as mock_task_queue_client:
        handle_backblast_submit(ack, body, logger)
    assert ack.call_count == 1
    ack.assert_called_once_with(response_action="errors", errors={"pax-select": "Please select an AO above for your backblast."})

