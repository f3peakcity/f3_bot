import datetime
import os
import uuid
import logging

from googleapiclient.errors import HttpError
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from googleapiclient import discovery

import db
import model

logging.basicConfig(level=logging.INFO)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    # process_before_response=True,
)

service = discovery.build('sheets', 'v4')
spreadsheet_id = '1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY'


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
                                "action_id": "ao-select"
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
    global service
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
                ao_id = val["ao-select"]["selected_channel"]
                ao_obj = app.client.conversations_info(channel=ao_id)
                ao = ao_obj.get("channel", {}).get("name", "")
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

    backblast = model.Backblast(
        id=uuid.uuid4().hex,
        store_date=datetime.datetime.now(),
        date=date,
        ao_id=ao_id,
        ao=ao,
        q_id=q_id,
        q=q,
        pax_ids=pax_ids,
        pax=pax,
        summary=summary,
        fng_ids=fng_ids,
        fngs=fngs,
        fngs_raw=fngs_raw
    )

    try:
        session = db.get_session()

        session.add(backblast)
        session.commit()
    except Exception as e:
        logger.error(f"Error storing /backblast data to BigQuery: {e}")

    try:
        body = {
            "values": backblast.to_rows()
        }
        done = False
        retry_count = 0
        while not done and retry_count < 3:
            retry_count += 1
            try:
                service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range="__RAW",
                    body=body,
                    valueInputOption="RAW"
                ).execute()
                done = True
            except (ConnectionError, HttpError):
                service = discovery.build('sheets', 'v4', credentials=None)
    except Exception as e:
        logger.error(f"Error storing /backblast data to Sheets: {e}")


handler = SlackRequestHandler(app)
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))


# Cloud Function
def handle_request(request):
    return handler.handle(request)
