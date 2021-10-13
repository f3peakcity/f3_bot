import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from googleapiclient import discovery
from googleapiclient.errors import HttpError

service = discovery.build('sheets', 'v4')
spreadsheet_id = '1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY'


def f3_sheets_handler(request):
    global service

    logger.info(f"{request.headers}")
    logger.info(f"{request.form}")
    logger.info(f"{request.data}")
    logger.info(f"{request.path}")
    logger.info(f"{request.url}")
    logger.info(f"{request.json}")

    done = False
    retry_count = 0
    body = request.get_json().get("body", {})
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
    return {"status": "ok", "retry_count": retry_count}
