import datetime
import json
import logging
import os
import time

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from slack_bolt import App
from sqlalchemy_cockroachdb import run_transaction

import db
import model
import util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

service = discovery.build('sheets', 'v4')
spreadsheet_id = os.environ.get("SPREADSHEET_ID", '1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY')

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


def f3_sheets_handler(request):
    global service

    start = time.time()

    done = False
    retry_count = 0
    body = request.get_json().get("body", {})

    now = time.time()
    logger.info(f"Starting to send slack messages after {now - start} seconds.")
    try:
        post_messages(backblast_data=body)
    except Exception as e:
        logger.error(f"Error posting messages to slack: {e}")

    now = time.time()
    logger.info(f"Done sending slack messages after {now - start} seconds.")

    backblast_cockroach = model.Backblast(
        store_date=datetime.datetime.now(),
        date=body.get("date"),
        ao_id=body.get("ao_id"),
        ao=body.get("ao"),
        q_id=body.get("q_id"),
        q=body.get("q"),
        pax_ids=body.get("pax_ids"),
        pax=body.get("pax"),
        summary=body.get("summary"),
        fng_ids=body.get("fng_ids"),
        fngs=body.get("fngs"),
        pax_no_slack=body.get("pax_no_slack"),
        n_visiting_pax=body.get("n_visiting_pax"),
        submitter_id=body.get("submitter_id"),
        submitter=body.get("submitter"),
        id=body.get("id")
    )

    try:
        Session = db.get_cockroach_sessionmaker()
        run_transaction(Session, lambda s: s.add(backblast_cockroach))
    except Exception as e:
        logger.error(f"Error storing /backblast data to CockroachDb: {e}")

    now = time.time()
    logger.info(f"Done saving to cockroachdb after {now - start} seconds.")

    spreadsheet_request_body = {
        "values": backblast_cockroach.to_rows()
    }

    while not done and retry_count < 3:
        retry_count += 1
        try:
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range="__RAW",
                body=spreadsheet_request_body,
                valueInputOption="RAW"
            ).execute()
            done = True
        except (ConnectionError, HttpError):
            service = discovery.build('sheets', 'v4', credentials=None)

    now = time.time()
    logger.info(f"Done saving to sheets after {now - start} seconds.")

    return {"status": "ok", "retry_count": retry_count}


def post_messages(backblast_data):
    message_text = util.build_message(backblast_data, logger)
    if message_text is None:
        return

    # Post in the channel(s)
    first_f_channel = "C8LR0QG5V"
    backblast_bot_test_channel = "C02HZNS9GHY"
    ao_channel = backblast_data["ao_id"]
    if ao_channel is None or ao_channel == "":
        post_channels = {first_f_channel}
    else:
        try:
            channel = app.client.conversations_info(channel=ao_channel).get("channel", {})
            ao_name = channel.get("name", "")
            post_channels = {ao_channel}
            if ao_name.startswith("ao"):
                post_channels.add(first_f_channel)

            if not channel["is_member"]:
                app.client.conversations_join(channel=ao_channel)
        except Exception as e:
            post_channels = {ao_channel, first_f_channel}
            logger.error(f"Error getting channel info: {e}")

    logger.info(f"Posting to channels: {post_channels}")
    for post_channel in post_channels:
        try:
            app.client.chat_postMessage(
                channel=post_channel,
                text=message_text,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message_text
                        },
                        "accessory": {
                            "type": "overflow",
                            "action_id": "edit-backblast",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Edit Backblast -- NOT ACTIVE YET",
                                        "emoji": True
                                    },
                                    "value": json.dumps({"id": backblast_data["id"]})
                                }
                            ]
                        }
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Error posting message to channel: {e}")
