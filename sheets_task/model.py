import datetime
import uuid

from sqlalchemy import Column, INTEGER, String, ARRAY, DATE, DATETIME
from sqlalchemy.orm import declarative_base

import db

Base = declarative_base()


class Backblast(Base):
    __tablename__ = 'backblast'

    def __init__(self, store_date, date, q, q_id, ao, ao_id, summary, pax, pax_ids, fngs, fng_ids, fngs_raw):
        self.id = uuid.uuid4().hex
        self.store_date = store_date
        self.date = date
        self.q = q
        self.q_id = q_id
        self.ao = ao
        self.ao_id = ao_id
        self.summary = summary
        self.pax = pax
        self.pax_ids = pax_ids
        self.fngs = fngs
        self.fng_ids = fng_ids
        if self.pax is None:
            self.pax = []
        if self.pax_ids is None:
            self.pax_ids = []
        if self.fngs is None:
            self.fng_ids = []
        if self.fng_ids is None:
            self.fng_ids = []

        self.all_pax = [x for x in ({q_id} | set(pax) | set(fngs))]  # convert to list to support indexing
        self.n_pax = len(self.all_pax)
        self.n_fngs = len(self.fngs)
        self.fngs_raw = fngs_raw

    id = Column(String, primary_key=True)
    store_date = Column(DATETIME)
    date = Column(DATE)
    q = Column(String)
    q_id = Column(String)
    ao = Column(String)
    ao_id = Column(String)
    summary = Column(String)
    n_pax = Column(INTEGER)
    pax = Column(ARRAY(String))
    pax_ids = Column(ARRAY(String))
    n_fngs = Column(INTEGER)
    fngs = Column(ARRAY(String))
    fng_ids = Column(ARRAY(String))
    fngs_raw = Column(String)

    def to_rows(self):
        n_rows = max(1, self.n_pax)
        rows = []
        if isinstance(self.store_date, datetime.datetime):
            store_date = self.store_date.isoformat()
        elif isinstance(self.store_date, str):
            store_date = self.store_date
        else:
            store_date = "_unknown_"
        if isinstance(self.date, datetime.date):
            date = self.date.strftime("%Y-%m-%d")
        elif isinstance(self.date, str):
            date = self.date
        else:
            date = "_unknown_"
        for i in range(n_rows):
            row = [
                self.id,
                store_date,
                date,
                self.q,
                self.ao,
                self.n_pax,
                self.all_pax[i] if i < len(self.all_pax) else "",
                self.n_fngs,
                self.fngs[i] if i < len(self.fngs) else "",
                self.fngs_raw
            ]
            rows.append(row)
        return rows


def init_db():
    engine = db.get_engine()
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
