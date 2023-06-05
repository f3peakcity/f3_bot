import pytest


@pytest.fixture
def view_submission():
    body = {
        "type": "view_submission",
        "team": {"id": "T04MU29F08G", "domain": "f3paxmatedev"},
        "user": {
            "id": "U04P1JJT2G6",
            "username": "james.p.campbell",
            "name": "james.p.campbell",
            "team_id": "T04MU29F08G",
        },
        "api_app_id": "A04RXQ9EGF9",
        "token": "9M9y7aCxfuIhC44h8iTLgwGM",
        "trigger_id": "5378395399268.4742077510288.ceb1415e92a3cbbf8059930fb65cb2ea",
        "view": {
            "id": "V05BRKL20GY",
            "team_id": "T04MU29F08G",
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
                            "initial_user": "U04P1JJT2G6",
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
                    "block_id": "0X+",
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
                    "block_id": "aoXn",
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
                    "block_id": "8Br",
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
                    "block_id": "HxZ",
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
                    "block_id": "AW0kl",
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
            "private_metadata": '{"initial_channel": "C04V4E61LN8", "team": "T04MU29F08G"}',
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
                            "selected_user": "U04P1JJT2G6",
                        },
                    },
                    "0X+": {
                        "pax-select": {
                            "type": "multi_users_select",
                            "selected_users": ["U04P1JJT2G6"],
                        }
                    },
                    "aoXn": {
                        "summary": {"type": "plain_text_input", "value": "asdfsad"}
                    },
                    "8Br": {
                        "fng-select": {
                            "type": "multi_users_select",
                            "selected_users": [],
                        }
                    },
                    "HxZ": {
                        "pax-no-slack": {"type": "plain_text_input", "value": None}
                    },
                    "AW0kl": {
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
            "root_view_id": "V05BRKL20GY",
            "app_id": "A04RXQ9EGF9",
            "external_id": "",
            "app_installed_team_id": "T04MU29F08G",
            "bot_id": "B04S5NJ83PY",
        },
        "response_urls": [],
        "is_enterprise_install": False,
        "enterprise": None,
    }
    return body
