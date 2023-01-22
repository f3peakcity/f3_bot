import datetime
import json
import logging
import os
import time

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from slack_bolt import App
from sqlalchemy_cockroachdb import run_transaction

import sheets_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

service = discovery.build('sheets', 'v4', cache_discovery=False)

# TODO(multi-tenant) may want to bifurcate this data
# Spreadsheet to which to save data
spreadsheet_id = os.environ.get("SPREADSHEET_ID", '1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY')

# TODO(multi-tenant) this will need to change to an oauth flow
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


def f3_sheets_handler(request):
    global service

    start = time.time()
    body = request.get_json().get("body", {})

    backblast = sheets_task.model.Backblast(
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
        Session = sheets_task.db.get_cockroach_sessionmaker()
        backblast_cockroach = backblast.get_sqlalchemy_model()
        run_transaction(Session, lambda s: s.add(backblast_cockroach))
        now = time.time()
        logger.info(f"Done saving to cockroachdb after {now - start} seconds.")
    except Exception as e:
        logger.error(f"Error storing /backblast data to CockroachDb: {e}")


    spreadsheet_request_body = {"values": []}
    try:
        spreadsheet_request_body = {
            "values": backblast.get_rows_model()
        }
    except Exception as e:
        logger.error(f"Error building spreadsheet model: {e}")

    try_count = 0
    done = False
    while not done and try_count < 3:
        try_count += 1
        try:
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range="__RAW",
                body=spreadsheet_request_body,
                valueInputOption="RAW"
            ).execute()
            done = True
        except (ConnectionError, HttpError):
            service = discovery.build('sheets', 'v4', cache_discovery=False)

    now = time.time()
    logger.info(f"Done saving to sheets after {now - start} seconds (try count: {try_count}).")

    try:
        post_messages(backblast_data=body)
    except Exception as e:
        logger.error(f"Error posting messages to slack: {e}")

    now = time.time()
    logger.info(f"Done sending slack messages after {now - start} seconds.")

    return {"status": "ok", "try_count": try_count}


def post_messages(backblast_data):
    message_text = sheets_task.util.build_message(backblast_data, logger)
    if message_text is None:
        return

    message_text_blocks = sheets_task.util.get_message_blocks_from_message_text(message_text=message_text)

    # Post in the channel(s)
    # TODO(multi-tenant) we'll need to look these up or provide a way for folks to configure it
    first_f_channel = "C04H3NW8JQM"
    third_f_channel = "C04GS5M55F1"
    backblast_bot_test_channel = "C04H38NN2QG"
    ao_channel = backblast_data["ao_id"]
    if ao_channel is None or ao_channel == "":
        post_channels = {first_f_channel}
    else:
        try:
            channel = app.client.conversations_info(channel=ao_channel).get("channel", {})
            ao_name = channel.get("name", "")
            post_channels = {ao_channel}
            if ao_name.startswith("ao"):
                # TODO(multi-tenant) Remove the duplicate post to the AO channel if 1stf
                # need to talk this over with both SLTs
                post_channels.remove(ao_channel)
                post_channels.add(first_f_channel)

            if ao_name.startswith("3rdf"):
                post_channels.add(third_f_channel)

            # TODO we should auto-join the 1stf/3rdf channel as well
            # not just this AO channel.
            if not channel["is_member"]:
                app.client.conversations_join(channel=ao_channel)
        except Exception as e:
            post_channels = {ao_channel}
            logger.error(f"Error getting channel info: {e}")

    logger.info(f"Posting to channels: {post_channels}")
    for message_text in message_text_blocks:
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
