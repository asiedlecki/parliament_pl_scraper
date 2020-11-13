import src.scraper as sc
import src.dataproc as dp

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

