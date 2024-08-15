import copy
import datetime
import json
import logging
import os
import time
import uuid
from flask import make_response

from google.cloud import tasks_v2
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

class SlackbotConfig:
    def __init__(self):
        self.gcp_project = 'f3-carpex'
        self.gcp_location = 'us-east1'
        self.gcp_queue_name = os.environ.get("BACKBLAST_QUEUE_NAME", "")
        self.handler_url = os.environ.get("BACKBLAST_HANDLER_URL")
        # This will be set on a per-deployment basis for now, but if we had a multi-workspace app woudl come from interaction payloads
        self.team_id = os.environ.get("SLACK_TEAM_ID")  

        # Default to empty, but expect a comma separated list of IDs
        self.paxmate_say_authorized_slack_ids = os.environ.get("PAXMATE_SAY_AUTHORIZED_SLACK_IDS", "").replace(" ", "").split(",")

slackbot_config = SlackbotConfig()

client = tasks_v2.CloudTasksClient()
parent = client.queue_path(slackbot_config.gcp_project, slackbot_config.gcp_location, slackbot_config.gcp_queue_name)

logging.basicConfig(level=logging.INFO)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)

@app.command("/paxmate")
def post_as_paxmate(ack, client, command, logger):
    ack()
    logger.info(json.dumps(command))
    user = command.get("user_id")
    channel = command.get("channel_id")
    text = command.get("text")
    if text is None or not text.startswith("say "):
        client.chat_postEphemeral(
            channel=channel,
            text="I don't understand that command. Try saying, /paxmate say I like Banjo.",
            user=user
        )
        logger.warning(f"unrecognized subcommand: {text}")
        return
    else:
        text = text[4:]

    if user not in slackbot_config.paxmate_say_authorized_slack_ids:
        client.chat_postEphemeral(
            channel=channel,
            # TODO(multi-tenant) look this up based on the list of slack ids
            text="Sorry, you don't have this power; please check with the Paxmate Admin.",
            user=user
        )
    else:
        client.chat_postMessage(
            channel=channel,
            text=text,
        )


@app.command("/backblast")
def open_backblast_form(ack, client, command, logger):
    ack()
    trigger_id = command.get("trigger_id")
    user = command.get("user_id")
    team = slackbot_config.team_id
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
                    # TODO(multi-tenant) Add customization of this header.
                    # There is a 25 character limit.
                    "text": "F3 PaxMate",
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
                "private_metadata": f'{{"initial_channel": "{channel}", "team": "{team}"}}',
                # body of the view
                "blocks": [
                    {
                        "type": "actions",
                        "block_id": "date-ao-q",
                        "elements": [
                            {
                                "type": "datepicker",
                                "initial_date": default_date,
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select date",
                                    "emoji": True
                                },
                                "action_id": "date-select"
                            },
                            {
                                "type": "channels_select",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select an AO by channel",
                                    "emoji": True
                                },
                                "action_id": "ao-select",
                                # do not set an initial_channel since too many people left it as default (1st f)
                                # "initial_channel": channel,
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
                        "block_id": "pax-select",
                        "dispatch_action": True,
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
                        "block_id": "summary",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "initial_value": """WARMUP:

THE THANG:

MARY:

ANNOUNCEMENTS / COT:
""",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Workout summary"
                            },
                            "action_id": "summary",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Workout Summary",
                            "emoji": True
                        },
                        "optional": True
                    },
                    {
                        "type": "input",
                        "block_id": "fng-select",
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
                        "block_id": "pax-no-slack",
                        "element": {
                            "type": "plain_text_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Pax Not Yet on Slack"
                            },
                            "action_id": "pax-no-slack",
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Additional Pax?",
                            "emoji": True
                        },
                        "optional": True
                    },
                    {
                        "type": "input",
                        "block_id": "visiting-pax",
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


@app.action("pax-select")
def handle_pax_select_interactive(ack, body, logger):
    ack()

    # Get the number of selected users
    actions = body.get("actions", [])
    selected_users_cnt = 0
    for action in actions:
        if action.get("action_id") == "pax-select":
            selected_users_cnt = len(action.get("selected_users", []))

    def _update_pax_number(blocks, new_num):
        for block in blocks:
            # descend into action blocks
            if block["type"] == "actions":
                _update_pax_number(block["elements"], new_num)
            elif block["type"] == "input":
                if block["element"]["action_id"] == "pax-select":
                    block["label"]["text"] = f"Pax ({new_num} selected)"
                    block["element"]["placeholder"]["text"] = f"{new_num} selected"

    # Build the view update:
    view = body.get("view", {})
    view = copy.deepcopy(view)
    view.pop("id")
    view.pop("team_id")
    view.pop("state")
    view.pop("hash")
    view.pop("previous_view_id")
    view.pop("root_view_id")
    view.pop("app_id")
    view.pop("app_installed_team_id")
    view.pop("bot_id")
    _update_pax_number(view["blocks"], selected_users_cnt)

    app.client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        view=view
    )


@app.action("edit-backblast")
def edit_backblast(ack, body, logger):
    ack()
    dump = json.dumps(body)
    user = body.get("user").get("id")
    channel = body.get("channel").get("id")
    logger.info(f"got data: {dump}")
    app.client.chat_postEphemeral(
        channel=channel,
        text=f"I can't edit messages yet, but this is in the works. I saw data: {dump}",
        user=user
    )


@app.view("backblast_modal")
def handle_backblast_submit(ack, body, logger) -> None:
    start = time.time()
    # Validate data. Currently, this is validating that an AO was selected.
    # We're doing it separately now because we don't want any latency to
    # delay the errors update, and in the normal parsing process we hit the slack api
    ao_id = None
    try:
        ao_id = body["view"]["state"]["values"]["date-ao-q"]["ao-select"]["selected_channel"]
    except KeyError:
        pass
    if ao_id is None or ao_id == "":
        # We cannot put the error message on the channel select because it is not an "input"
        # type object. This seems like a slack limitation (see: 
        # https://stackoverflow.com/questions/60220290/how-to-display-validation-errors-about-non-input-blocks-in-slack-modals)
        errors = {"pax-select": "Please select an AO above for your backblast."}
        ack(response_action="errors", errors=errors)
        return
    ack()
    backblast_data = _parse_backblast_body(body, logger)
    now = time.time()
    logger.info(f"starting to add to queue after {now - start}")
    _add_data_to_queue(backblast_data, logger)
    now = time.time()
    logger.info(f"done adding to queue after {now - start}")


def _parse_backblast_body(body, logger):
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
    pax_no_slack = ""
    n_visiting_pax = 0
    submitter_id = ""
    submitter = ""
    values = body.get("view", {}).get("state", {}).get("values", {})
    for val in values.values():
        try:
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
            if "pax-no-slack" in val:
                pax_no_slack = val["pax-no-slack"]["value"]
            if "visiting-pax" in val:
                visiting_pax = val["visiting-pax"]["selected_option"]
                if visiting_pax is None:
                    continue
                else:
                    visiting_pax_str = visiting_pax["value"]
                try:
                    n_visiting_pax = int(visiting_pax_str)
                except ValueError:
                    if len(visiting_pax_str) > 0:
                        n_visiting_pax = 10
                    else:
                        n_visiting_pax = 0
        except Exception as e:
            logger.error(f"Error parsing /backblast data: {e}")
    try:
        submitter_id = body.get("user", {}).get("id")
        if submitter_id is not None:
            submitter = _get_name_from_id(submitter_id)
    except Exception as e:
        logger.error(f"Error getting submitter from /backblast data: {e}")

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
        "pax_no_slack": pax_no_slack,
        "n_visiting_pax": n_visiting_pax,
        "submitter_id": submitter_id,
        "submitter": submitter,
        "team_id": slackbot_config.team_id,
        "id": uuid.uuid4().hex
    }
    logger.debug(f"Built backblast object: \n{json.dumps(backblast_data, indent=2)}")
    return backblast_data


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
                "url": slackbot_config.handler_url,
                "headers": {"Content-type": "application/json"},
                "body": converted_payload
            },
            "name": client.task_path(slackbot_config.gcp_project, slackbot_config.gcp_location, slackbot_config.gcp_queue_name, backblast_data.get("id", uuid.uuid4().hex))
        }
        response = client.create_task(request={"parent": parent, "task": task})
        logger.info(f"Created task {response.name}")
    except Exception as e:
        logger.error(f"Error creating task: {e}")


handler = SlackRequestHandler(app)

def slackbot(request):
    if request.method == "GET" and request.path.endswith("/healthz"):
        return make_response(f'{{"status": "alive", "path": "{request.path}"}}', 200)
    return handler.handle(request)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

