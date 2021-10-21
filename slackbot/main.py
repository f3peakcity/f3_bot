import datetime
import json
import os
import logging
import uuid

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from google.cloud import tasks_v2

import util

client = tasks_v2.CloudTasksClient()
project = 'f3-carpex'
queue = 'sheets-append'
location = 'us-east1'
url = 'https://us-east1-f3-carpex.cloudfunctions.net/f3-sheets-handler'
parent = client.queue_path(project, location, queue)


logging.basicConfig(level=logging.INFO)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@app.command("/backblast")
def open_backblast_form(ack, client, command, logger):
    ack()
    trigger_id = command.get("trigger_id")
    user = command.get("user_id")
    channel = command.get("channel_id")
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "backblast_modal",
                "title": {
                    "type": "plain_text",
                    "text": "F3 Carpex PAX Assistant",
                    "emoji": True
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit",
                    "emoji": True
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel",
                    "emoji": True
                },
                # body of the view
                "blocks": [
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "datepicker",
                                "initial_date": default_date,
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a date",
                                    "emoji": True
                                },
                                "action_id": "date-select"
                            },
                            {
                                "type": "channels_select",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a AO by channel",
                                    "emoji": True
                                },
                                "action_id": "ao-select",
                                "initial_channel": channel,
                            },
                            {
                                "type": "users_select",
                                "initial_user": user,
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select Q",
                                    "emoji": True
                                },
                                "action_id": "q-select"
                            }
                        ]
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "multi_users_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select pax who posted",
                                "emoji": True
                            },
                            "action_id": "pax-select"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Pax",
                            "emoji": True
                        }
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Workout summary"
                            },
                            "action_id": "summary",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Summary",
                            "emoji": True
                        },
                        "optional": True
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "multi_users_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "FNGs",
                                "emoji": True
                            },
                            "action_id": "fng-select"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "FNGs",
                            "emoji": True
                        },
                        "optional": True
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "FNGs Not Yet on Slack"
                            },
                            "action_id": "fngs-raw",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Additional FNGs?",
                            "emoji": True
                        },
                        "optional": True
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "How many PAX from another region?"
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "0",
                                        "emoji": True
                                    },
                                    "value": "0"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "1",
                                        "emoji": True
                                    },
                                    "value": "1"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "2",
                                        "emoji": True
                                    },
                                    "value": "2"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "3",
                                        "emoji": True
                                    },
                                    "value": "3"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "4",
                                        "emoji": True
                                    },
                                    "value": "4"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "5",
                                        "emoji": True
                                    },
                                    "value": "5"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "6",
                                        "emoji": True
                                    },
                                    "value": "6"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "7",
                                        "emoji": True
                                    },
                                    "value": "7"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "8",
                                        "emoji": True
                                    },
                                    "value": "8"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "9",
                                        "emoji": True
                                    },
                                    "value": "9"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "10+",
                                        "emoji": True
                                    },
                                    "value": "10+"
                                }
                            ],
                            "action_id": "visiting-pax"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Visiting PAX",
                            "emoji": True
                        },
                        "optional": True
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error processing /backblast command: {e}")


@app.action("date-select")
def handle_date_interactive(ack, body, logger):
    ack()
    logger.debug(body)


@app.action("ao-select")
def handle_ao_interactive(ack, body, logger):
    ack()
    logger.debug(body)


@app.action("q-select")
def handle_q_select_interactive(ack, body, logger):
    ack()
    logger.debug(body)


@app.view("backblast_modal")
def handle_backblast_submit(ack, body, logger):
    ack()
    backblast_data = _parse_backblast_body(body, logger)

    _add_data_to_queue(backblast_data, logger)
    message = util.build_message(backblast_data, logger)
    if message is None:
        return

    # Post in the channel(s)
    first_f_channel = "C8LR0QG5V"
    backblast_bot_test_channel = "C02HZNS9GHY"
    ao_channel = backblast_data["ao_id"]

    for post_channel in [backblast_bot_test_channel]:  # [first_f_channel, ao_channel]:
        try:
            app.client.chat_postMessage(
                channel=post_channel,
                text=message
            )
        except Exception as e:
            logger.error(f"Error posting message to channel: {e}")


def _parse_backblast_body(body, logger):
    try:
        date = "1970-01-01"
        ao_id = ""
        ao = ""
        q_id = ""
        q = ""
        pax_ids = []
        pax = []
        summary = ""
        fng_ids = []
        fngs = []
        fngs_raw = ""
        n_visiting_pax = 0
        values = body.get("view", {}).get("state", {}).get("values")
        for val in values.values():
            if "date-select" in val:
                date = val["date-select"]["selected_date"]
            if "ao-select" in val:
                ao_id = val["ao-select"].get("selected_channel", "")
                try:
                    ao_obj = app.client.conversations_info(channel=ao_id)
                    ao = ao_obj.get("channel", {}).get("name", "")
                except Exception as e:
                    logger.error(f"Error getting channel info for channel {ao_id}")
                    ao = ""
            if "q-select" in val:
                q_id = val["q-select"]["selected_user"]
                q = _get_name_from_id(q_id)
            if "pax-select" in val:
                pax_ids = val["pax-select"]["selected_users"]
                pax = _get_names_from_id_list(pax_ids)
            if "summary" in val:
                summary = val["summary"]["value"]
            if "fng-select" in val:
                fng_ids = val["fng-select"]["selected_users"]
                fngs = _get_names_from_id_list(fng_ids)
            if "fngs-raw" in val:
                fngs_raw = val["fngs-raw"]["value"]
            if "visiting-pax" in val:
                visiting_pax_str = val["visiting-pax"]["value"]
                try:
                    n_visiting_pax = int(visiting_pax_str)
                except ValueError:
                    if len(visiting_pax_str) > 0:
                        n_visiting_pax = 10
                    else:
                        n_visiting_pax = 0
        backblast_data = {
            "date": date,
            "ao_id": ao_id,
            "ao": ao,
            "q_id": q_id,
            "q": q,
            "pax_ids": pax_ids,
            "pax": pax,
            "summary": summary,
            "fng_ids": fng_ids,
            "fngs": fngs,
            "fngs_raw": fngs_raw,
            "n_visiting_pax": n_visiting_pax
        }
        return backblast_data
    except Exception as e:
        logger.error(f"Error parsing /backblast data: {e}")
        return


def _get_name_from_id(id_):
    user = app.client.users_info(user=id_).get("user", {})
    display_name = user.get("profile", {}).get("display_name", None)
    real_name = user.get("profile", {}).get("real_name", None)
    name = user.get("name", None)
    return display_name or real_name or name or ""


def _get_names_from_id_list(id_list):
    names = []
    for id_ in id_list:
        names.append(_get_name_from_id(id_))
    return names


def _add_data_to_queue(backblast_data, logger):
    try:
        payload = {
            "body": backblast_data
        }
        payload = json.dumps(payload)
        converted_payload = payload.encode()
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {"Content-type": "application/json"},
                "body": converted_payload
            },
            "name": client.task_path(project, location, queue, uuid.uuid4().hex)
        }
        response = client.create_task(request={"parent": parent, "task": task})
        logger.info(f"Created task {response.name}")
    except Exception as e:
        logger.error(f"Error storing /backblast data to Sheets: {e}")


handler = SlackRequestHandler(app)


def slackbot(request):
    return handler.handle(request)


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

