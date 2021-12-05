import datetime
import logging

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from sqlalchemy_cockroachdb import run_transaction

import db
import model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

service = discovery.build('sheets', 'v4')
spreadsheet_id = '1c1vvx07AXdnu6NSa4is4a0oyUiu8q3cgOecFbTNWlAY'


def f3_sheets_handler(request):
    global service

    done = False
    retry_count = 0
    body = request.get_json().get("body", {})

    backblast = model.Backblast(
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
        fngs_raw=body.get("fngs_raw"),
        n_visiting_pax=body.get("n_visiting_pax"),
        submitter_id=body.get("submitter_id"),
        submitter=body.get("submitter"),
        id=body.get("id")
    )

    try:
        session = db.get_session()
        session.add(backblast)
        session.commit()
    except Exception as e:
        logger.error(f"Error storing /backblast data to BigQuery: {e}")

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
        fngs_raw=body.get("fngs_raw"),
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

    spreadsheet_request_body = {
        "values": backblast.to_rows()
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
    return {"status": "ok", "retry_count": retry_count}
