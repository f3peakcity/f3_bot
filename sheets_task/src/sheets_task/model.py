import datetime
import uuid

from sqlalchemy import Column, INTEGER, String, ARRAY, Date, DateTime
from sqlalchemy.orm import declarative_base

import sheets_task.db

Base = declarative_base()


class Backblast():

    def __init__(self, store_date, date, q, q_id, ao, ao_id, summary, pax, pax_ids, fngs, fng_ids, pax_no_slack,
                 n_visiting_pax, submitter_id, submitter, team_id, id=None) -> None:
        if id is None:
            self.id = uuid.uuid4().hex
        else:
            self.id = id
        self.team_id = team_id
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
        self.pax_no_slack = pax_no_slack
        self.n_visiting_pax = n_visiting_pax
        self.submitter_id = submitter_id
        self.submitter = submitter

        if self.pax is None:
            self.pax = []
        if self.pax_ids is None:
            self.pax_ids = []
        if self.fngs is None:
            self.fng_ids = []
        if self.fng_ids is None:
            self.fng_ids = []


        # Create a set of tuples with (id, name) so we can keep a match between the two
        all_pax = set(
            zip(
                [self.q_id] + self.pax_ids + self.fng_ids,
                [self.q] + self.pax + self.fngs,
            )
        )
        self.all_pax = [x for x in all_pax]  # convert to list to support indexing
        self.n_pax = len(all_pax)
        self.n_fngs = len(self.fngs)
    
    def get_rows_model(self):
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

        if self.pax_no_slack is None or len(self.pax_no_slack) == 0:
            pax_no_slack_str = "_"
        else:
            pax_no_slack_str = self.pax_no_slack

        for i in range(n_rows):
            row = [
                date,
                self.q,
                self.ao,
                self.n_pax,
                self.all_pax[i][1] if i < len(self.all_pax) else "",  # name
                self.all_pax[i][0] if i < len(self.all_pax) else "",  # id
                self.n_fngs,
                self.fngs[i] if i < len(self.fngs) else "_",
                pax_no_slack_str,
                self.n_visiting_pax,
                self.submitter,
                self.submitter_id,
                self.id,
                store_date,
                self.q_id,
                self.team_id
            ]
            rows.append(row)
        return rows

    def get_sqlalchemy_model(self):
        sqlalchemy_backblast = SqlAlchemyBackblast()
        sqlalchemy_backblast.id = self.id
        sqlalchemy_backblast.store_date = self.store_date
        sqlalchemy_backblast.date = self.date
        sqlalchemy_backblast.q = self.q
        sqlalchemy_backblast.q_id = self.q_id
        sqlalchemy_backblast.ao = self.ao
        sqlalchemy_backblast.ao_id = self.ao_id
        sqlalchemy_backblast.summary = self.summary
        sqlalchemy_backblast.n_pax = self.n_pax
        sqlalchemy_backblast.pax = self.pax
        sqlalchemy_backblast.pax_ids = self.pax_ids
        sqlalchemy_backblast.n_fngs = self.n_fngs
        sqlalchemy_backblast.fngs = self.fngs
        sqlalchemy_backblast.fng_ids = self.fng_ids
        sqlalchemy_backblast.pax_no_slack = self.pax_no_slack
        sqlalchemy_backblast.n_visiting_pax = self.n_visiting_pax
        sqlalchemy_backblast.submitter_id = self.submitter_id
        sqlalchemy_backblast.submitter = self.submitter
        sqlalchemy_backblast.team_id = self.team_id

        return sqlalchemy_backblast


class SqlAlchemyBackblast(Base):
    __tablename__ = 'backblast'

    id = Column(String, primary_key=True)
    store_date = Column(DateTime)
    date = Column(Date)
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
    pax_no_slack = Column(String)
    n_visiting_pax = Column(INTEGER)
    submitter_id = Column(String)
    submitter = Column(String)
    team_id = Column(String)

    def get_backblast(self) -> Backblast:
        return Backblast(
            self.store_date, self.date, self.q, self.q_id, self.ao, self.ao_id, self.summary, self.pax, self.pax_ids, self.fngs, self.fng_ids, self.pax_no_slack, self.n_visiting_pax, self.submitter_id, self.submitter, self.team_id, self.id
        )


def init_cockroach_db():
    engine = sheets_task.db.get_cockroach_engine()
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_cockroach_db()
