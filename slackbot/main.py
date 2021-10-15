import datetime
import json
import os
import logging
import uuid

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from google.cloud import tasks_v2

logging.basicConfig(level=logging.INFO)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


client = tasks_v2.CloudTasksClient()
project = 'f3-carpex'
queue = 'sheets-append'
location = 'us-east1'
url = 'https://us-east1-f3-carpex.cloudfunctions.net/f3-sheets-handler'
parent = client.queue_path(project, location, queue)


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
                                "optional": False
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
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error processing /backblast command: {e}")


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


def get_worked_phrase(summary):
    return "got pushed to their max"


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
    except Exception as e:
        logger.error(f"Error parsing /backblast data: {e}")
        return
    
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
        "fngs_raw": fngs_raw
    }

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

    try:
        all_pax = {q_id} | set(fng_ids) | set(pax_ids)
        all_pax_mention = ["<@" + pax + ">" for pax in all_pax]
        all_pax_str = ", ".join(all_pax_mention)
        n_pax = len(all_pax)

        worked_phrase = get_worked_phrase(summary)

        # Post in the channel(s)

        # 1st F ID: C8LR0QG5V
        backblast_bot_test_channel = "C02HZNS9GHY"
        # ao_id: in message
        message = f"{n_pax} {worked_phrase}"
        if ao_id is not None and ao_id != "":
            message += f" at <#{ao_id}>"
        message += "."
        if summary is not None and summary != "":
            message += f"\n{summary}"
        message += f"\n{all_pax_str}"
        app.client.chat_postMessage(
            channel=backblast_bot_test_channel,
            text=message
        )
    except Exception as e:
        logger.error(f"Error posting message to channel: {e}")


handler = SlackRequestHandler(app)


def slackbot(request):
    return handler.handle(request)


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

