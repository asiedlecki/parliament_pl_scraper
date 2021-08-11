import src.scraper as sc
import src.dataproc as dp
from typing import NoReturn

class DailyPageChecker:
    def __init__(self, term):
        self.term = term
        self.uri = 'agent.xsp?symbol=posglos&NrKadencji={t}'.format(t=self.term)
        self.entry_page = sc.MainVotingPage(self.uri)
        self.days_from_page = self.get_days_from_page()
        self.days_from_db = self.get_days_from_db()
        self.missing_days = self.days_from_page - self.days_from_db

    def get_days_from_page(self):
        self.entry_page.get_dict_of_days()
        return set(self.entry_page.days_dict.keys())

    def get_days_from_db(self):
        client = dp.MyMongoClient()
        client.set_votes_collection()
        return set(
            client.db.coll.find({}, {'date': 1}).distinct('date')
        )

    def scrap_missing_dates(self) -> NoReturn:
        self.scraped_data = dp.batch_dump_parliament_votings(term=self.term, dates=self.missing_days)

    def insert_missing_dates_to_db(self) -> NoReturn:
        client = dp.MyMongoClient()
        client.set_votes_collection()
        return client.db.coll.insert_many(documents=self.scraped_data, ordered=False)